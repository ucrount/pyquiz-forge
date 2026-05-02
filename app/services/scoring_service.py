"""Scoring service: ask an LLM to rate an existing exercise."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.crud import exercise as crud_exercise
from app.crud import llm_config as crud_llm
from app.llm import build_llm_client
from app.llm.prompts import build_score_messages
from app.models import Exercise, LLMConfig
from app.schemas.scoring import ScoreDimensions, ScoreResult
from app.services.generation_service import GenerationError, parse_llm_json

logger = get_logger(__name__)


# Mirror the LLMConfig resolution in generation_service to keep behavior
# consistent — caller may pass an explicit id, otherwise use active config.
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
            "No active LLM config. Activate one first or pass llm_config_id."
        )
    return cfg


def _coerce_score(v: Any, default: float = 0.0) -> float:
    """Coerce LLM-returned values to a float in [0, 10]. Tolerant of strings."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return default
    if f < 0:
        return 0.0
    if f > 10:
        return 10.0
    return f


def _build_score_result(parsed: Dict[str, Any]) -> ScoreResult:
    raw_scores = parsed.get("scores") or {}
    if not isinstance(raw_scores, dict):
        raw_scores = {}
    dims = ScoreDimensions(
        clarity=_coerce_score(raw_scores.get("clarity")),
        correctness=_coerce_score(raw_scores.get("correctness")),
        difficulty_match=_coerce_score(raw_scores.get("difficulty_match")),
        educational_value=_coerce_score(raw_scores.get("educational_value")),
    )
    overall_raw = parsed.get("overall")
    if overall_raw is None:
        # Fall back to mean of dimensions if model omitted overall.
        overall_raw = (
            dims.clarity + dims.correctness
            + dims.difficulty_match + dims.educational_value
        ) / 4
    overall = _coerce_score(overall_raw)
    return ScoreResult(
        overall=overall,
        dimensions=dims,
        comment=str(parsed.get("comment") or "")[:2000],
    )


def score_one(
    db: Session,
    *,
    exercise_id: int,
    llm_config_id: Optional[int] = None,
) -> tuple[Exercise, ScoreResult]:
    """Score one exercise and persist the result. Returns (exercise, score)."""
    ex = crud_exercise.get_exercise(db, exercise_id)
    if ex is None:
        raise GenerationError(f"Exercise not found: id={exercise_id}")

    cfg = _resolve_llm_config(db, llm_config_id)

    # Reconstruct test_cases from JSON string for prompt context
    try:
        test_cases = json.loads(ex.test_cases) if ex.test_cases else []
    except json.JSONDecodeError:
        test_cases = []

    chapter_title = ex.knowledge_point.chapter.title if ex.knowledge_point and ex.knowledge_point.chapter else ""
    kp_title = ex.knowledge_point.title if ex.knowledge_point else ""

    messages = build_score_messages(
        title=ex.title,
        chapter_title=chapter_title,
        kp_title=kp_title,
        difficulty=ex.difficulty,
        question_type=ex.question_type,
        description=ex.description,
        standard_answer=ex.standard_answer,
        reference_code=ex.reference_code,
        test_cases=test_cases,
        explanation=ex.explanation,
        common_mistakes=ex.common_mistakes,
    )

    client = build_llm_client(cfg)
    try:
        response = client.chat(messages)
    except NotImplementedError as e:
        raise GenerationError(f"Provider not implemented: {e}")
    except Exception as e:
        raise GenerationError(f"LLM call failed: {type(e).__name__}: {e}")

    parsed = parse_llm_json(response.content)
    if parsed is None:
        raise GenerationError(
            "Failed to parse LLM scoring response as JSON. "
            "Try lowering temperature or switching model."
        )

    result = _build_score_result(parsed)

    # Persist
    ex.score_overall = result.overall
    ex.score_detail = json.dumps(
        result.dimensions.model_dump(), ensure_ascii=False
    )
    ex.score_comment = result.comment
    ex.scored_at = datetime.utcnow()
    ex.score_llm_config_id = cfg.id
    db.flush()
    db.commit()
    db.refresh(ex)
    return ex, result
