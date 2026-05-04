"""Learning content + mastery management.

Generates per-KP markdown teaching material via LLM, persists it, and
exposes mastery-state transitions.
"""
from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.crud import knowledge_point as crud_kp
from app.llm import build_llm_client
from app.llm.prompts import build_learning_messages
from app.models import KnowledgePoint
from app.schemas.common import Mastery
from app.services.generation_service import (
    GenerationError,
    _resolve_llm_config,
)

logger = get_logger(__name__)


_FENCE_OUTER = re.compile(
    r"^\s*```(?:markdown|md)?\s*\n(.*)\n```\s*$", re.DOTALL | re.IGNORECASE
)


def _strip_outer_markdown_fence(text: str) -> str:
    """If the model wrapped the whole answer in ```markdown ... ```, unwrap it."""
    if not text:
        return text
    m = _FENCE_OUTER.match(text)
    if m:
        return m.group(1).strip()
    return text.strip()


def generate_content_for_kp(
    db: Session,
    *,
    kp_id: int,
    llm_config_id: Optional[int] = None,
    overwrite: bool = True,
) -> Tuple[KnowledgePoint, int]:
    """
    Generate learning content for a KP via LLM and persist it.
    Returns (kp, latency_ms).
    """
    kp = crud_kp.get_kp(db, kp_id)
    if kp is None:
        raise GenerationError(f"Knowledge point not found: id={kp_id}")

    if kp.content and not overwrite:
        raise GenerationError(
            "学习内容已存在；如需重新生成请勾选覆盖。"
        )

    cfg = _resolve_llm_config(db, llm_config_id)
    chapter_title = kp.chapter.title if kp.chapter else ""
    language = kp.language or "python"

    messages = build_learning_messages(
        kp=kp, chapter_title=chapter_title, language=language,
    )
    client = build_llm_client(cfg)

    t0 = time.perf_counter()
    try:
        resp = client.chat(messages, max_tokens=4096)
    except NotImplementedError as e:
        raise GenerationError(f"Provider not implemented: {e}")
    except Exception as e:
        raise GenerationError(f"LLM call failed: {type(e).__name__}: {e}")

    latency_ms = int((time.perf_counter() - t0) * 1000)
    content = _strip_outer_markdown_fence(resp.content or "")
    if not content.strip():
        raise GenerationError("LLM 返回为空，请稍后重试。")

    kp.content = content
    # Auto-promote mastery to "learning" when content is generated for the first time
    if kp.mastery == Mastery.not_started.value:
        kp.mastery = Mastery.learning.value
        kp.mastery_updated_at = datetime.utcnow()
    db.commit()
    db.refresh(kp)
    logger.info(
        "Generated learning content for KP #%d (%s, %d chars, %dms)",
        kp.id, kp.code, len(content), latency_ms,
    )
    return kp, latency_ms


def update_content(db: Session, *, kp_id: int, content: str) -> KnowledgePoint:
    """Manually overwrite a KP's learning content (e.g. user edited it)."""
    kp = crud_kp.get_kp(db, kp_id)
    if kp is None:
        raise GenerationError(f"Knowledge point not found: id={kp_id}")
    kp.content = content
    db.commit()
    db.refresh(kp)
    return kp


def set_mastery(
    db: Session,
    *,
    kp_id: int,
    mastery: Mastery,
    note: Optional[str] = None,
) -> KnowledgePoint:
    """Set mastery state for a KP. Optional note overrides existing mastery_note."""
    kp = crud_kp.get_kp(db, kp_id)
    if kp is None:
        raise GenerationError(f"Knowledge point not found: id={kp_id}")
    kp.mastery = mastery.value
    kp.mastery_updated_at = datetime.utcnow()
    if note is not None:
        kp.mastery_note = note
    db.commit()
    db.refresh(kp)
    return kp
