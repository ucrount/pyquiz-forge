"""Generation service: prompt -> LLM -> parse -> persist."""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.crud import exercise as crud_exercise
from app.crud import generation_log as crud_log
from app.crud import knowledge_point as crud_kp
from app.crud import llm_config as crud_llm
from app.llm import build_llm_client
from app.llm.base import LLMResponse
from app.llm.prompts import build_messages
from app.models import Exercise, GenerationLog, KnowledgePoint, LLMConfig
from app.schemas.common import Difficulty, QuestionType

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# JSON parsing helpers
# ---------------------------------------------------------------------------

_CODE_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)
_OUTER_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def _strip_fences(text: str) -> str:
    return _CODE_FENCE.sub("", text or "").strip()


def parse_llm_json(text: str) -> Optional[Dict[str, Any]]:
    """Try several strategies to extract a JSON object from an LLM response."""
    if not text:
        return None
    cleaned = _strip_fences(text)
    # Strategy 1: direct json.loads
    try:
        v = json.loads(cleaned)
        if isinstance(v, dict):
            return v
    except json.JSONDecodeError:
        pass
    # Strategy 2: extract outermost {...}
    m = _OUTER_OBJECT.search(cleaned)
    if m:
        try:
            v = json.loads(m.group(0))
            if isinstance(v, dict):
                return v
        except json.JSONDecodeError:
            pass
    return None


def _coerce_test_cases(raw: Any) -> list:
    if not isinstance(raw, list):
        return []
    out = []
    for item in raw:
        if isinstance(item, dict):
            out.append(
                {
                    "input": str(item.get("input", "")),
                    "expected_output": str(item.get("expected_output", "")),
                }
            )
    return out


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class GenerationError(Exception):
    """Raised when generation fails for a recoverable reason."""


# ---------------------------------------------------------------------------
# Core generation
# ---------------------------------------------------------------------------


def _resolve_llm_config(
    db: Session, llm_config_id: Optional[int]
) -> LLMConfig:
    if llm_config_id is not None:
        cfg = crud_llm.get_config(db, llm_config_id)
        if cfg is None:
            raise GenerationError(f"LLM config not found: id={llm_config_id}")
        return cfg
    cfg = crud_llm.get_active_config(db)
    if cfg is None:
        raise GenerationError(
            "No active LLM config. Please create one and call POST /llm-configs/{id}/activate."
        )
    return cfg


def _resolve_kp(db: Session, kp_id: int) -> KnowledgePoint:
    kp = crud_kp.get_kp(db, kp_id)
    if kp is None:
        raise GenerationError(f"Knowledge point not found: id={kp_id}")
    return kp


def _persist_log(
    db: Session,
    *,
    config_id: Optional[int],
    kp_id: Optional[int],
    difficulty: str,
    question_type: str,
    prompt: str,
    response: Optional[LLMResponse],
    parsed_ok: bool,
    error_message: str = "",
) -> GenerationLog:
    return crud_log.create_log(
        db,
        llm_config_id=config_id,
        knowledge_point_id=kp_id,
        difficulty=difficulty,
        question_type=question_type,
        prompt=prompt,
        raw_response=response.content if response else "",
        parsed_ok=parsed_ok,
        error_message=error_message,
        latency_ms=response.latency_ms if response else 0,
        prompt_tokens=response.prompt_tokens if response else 0,
        completion_tokens=response.completion_tokens if response else 0,
    )


def generate_one(
    db: Session,
    *,
    knowledge_point_id: int,
    difficulty: Difficulty,
    question_type: QuestionType,
    llm_config_id: Optional[int] = None,
    avoid_duplicates: bool = True,
    _dedup_retry_left: int = 1,
) -> Exercise:
    """
    Generate a single exercise. Persists both the generation_log and (on success)
    the exercise. Raises GenerationError on failure (log is still saved).

    When avoid_duplicates=True (default):
      - Existing titles for the same KP are injected into the prompt as
        "please avoid these"
      - After parsing, the new title is compared against existing ones; if too
        similar (>= 0.7 ratio), we retry up to `_dedup_retry_left` times
        before giving up
    """
    from app.services import dedup_service  # local import to avoid cycle

    cfg = _resolve_llm_config(db, llm_config_id)
    kp = _resolve_kp(db, knowledge_point_id)
    chapter_title = kp.chapter.title if kp.chapter else ""
    language = kp.language or "python"

    existing_titles = (
        dedup_service.get_existing_titles(db, kp.id) if avoid_duplicates else []
    )

    messages = build_messages(
        kp=kp,
        chapter_title=chapter_title,
        difficulty=difficulty,
        question_type=question_type,
        language=language,
        existing_titles=existing_titles,
    )
    prompt_text = json.dumps(messages, ensure_ascii=False)

    client = build_llm_client(cfg)
    response: Optional[LLMResponse] = None
    error_message = ""
    parsed: Optional[Dict[str, Any]] = None

    try:
        response = client.chat(messages)
        parsed = parse_llm_json(response.content)
        if parsed is None:
            error_message = "Failed to parse LLM response as JSON."
    except NotImplementedError as e:
        error_message = f"Provider not implemented: {e}"
    except Exception as e:
        error_message = f"LLM call failed: {type(e).__name__}: {e}"

    log = _persist_log(
        db,
        config_id=cfg.id,
        kp_id=kp.id,
        difficulty=difficulty.value,
        question_type=question_type.value,
        prompt=prompt_text,
        response=response,
        parsed_ok=parsed is not None,
        error_message=error_message,
    )
    db.commit()

    if parsed is None:
        raise GenerationError(error_message or "Empty response from LLM.")

    new_title = str(parsed.get("title") or "(untitled)")[:200]

    # Dedup check after parse — retry once if too similar
    if avoid_duplicates and existing_titles:
        hit = dedup_service.find_too_similar(new_title, existing_titles)
        if hit is not None:
            logger.warning(
                "Generated title %r too similar to existing %r", new_title, hit
            )
            if _dedup_retry_left > 0:
                logger.info("Retrying generation to avoid duplicate ...")
                return generate_one(
                    db,
                    knowledge_point_id=knowledge_point_id,
                    difficulty=difficulty,
                    question_type=question_type,
                    llm_config_id=llm_config_id,
                    avoid_duplicates=True,
                    _dedup_retry_left=_dedup_retry_left - 1,
                )
            raise GenerationError(
                f"生成的题目「{new_title}」与已有题目「{hit}」相似度过高，"
                "请稍后再试或更换难度/题型。"
            )

    # Build exercise from parsed fields (be lenient — fall back to "" / [] / {})
    exercise = crud_exercise.create_exercise(
        db,
        title=new_title,
        knowledge_point_id=kp.id,
        language=language,
        difficulty=difficulty.value,
        question_type=question_type.value,
        description=str(parsed.get("description") or ""),
        example_input=str(parsed.get("example_input") or ""),
        example_output=str(parsed.get("example_output") or ""),
        hint=str(parsed.get("hint") or ""),
        standard_answer=str(parsed.get("standard_answer") or ""),
        reference_code=str(parsed.get("reference_code") or ""),
        test_cases=_coerce_test_cases(parsed.get("test_cases")),
        explanation=str(parsed.get("explanation") or ""),
        common_mistakes=str(parsed.get("common_mistakes") or ""),
        extra=parsed.get("extra") if isinstance(parsed.get("extra"), dict) else {},
        llm_config_id=cfg.id,
        generation_log_id=log.id,
        status="published",
    )
    db.commit()
    db.refresh(exercise)
    return exercise


def regenerate(
    db: Session,
    *,
    exercise: Exercise,
    mode: str = "new",
    llm_config_id: Optional[int] = None,
) -> Exercise:
    """Re-generate using the same parameters. mode: 'new' (default) or 'overwrite'."""
    new_ex = generate_one(
        db,
        knowledge_point_id=exercise.knowledge_point_id,
        difficulty=Difficulty(exercise.difficulty),
        question_type=QuestionType(exercise.question_type),
        llm_config_id=llm_config_id,
    )
    if mode == "overwrite":
        # Delete the original exercise to keep only the latest version.
        crud_exercise.delete_exercise(db, exercise)
        db.commit()
    return new_ex


def test_llm_config(cfg: LLMConfig) -> Tuple[bool, str, int]:
    """Lightweight ping — returns (ok, message, latency_ms)."""
    try:
        client = build_llm_client(cfg)
        resp = client.ping()
        return True, "OK", resp.latency_ms
    except NotImplementedError as e:
        return False, f"Not implemented: {e}", 0
    except Exception as e:
        return False, f"{type(e).__name__}: {e}", 0
