"""Seed service: load learning_path.json into DB on startup (idempotent)."""
from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import get_logger
from app.crud import chapter as crud_chapter
from app.crud import knowledge_point as crud_kp
from app.crud import llm_config as crud_llm
from app.models import LLMConfig
from app.schemas.llm_config import LLMConfigCreate

logger = get_logger(__name__)

LEARNING_PATH_FILE = Path(__file__).resolve().parent.parent / "data" / "learning_path.json"


def seed_learning_path(db: Session) -> None:
    """Idempotent: upserts chapters and knowledge points by code."""
    if not LEARNING_PATH_FILE.exists():
        logger.warning("learning_path.json not found at %s", LEARNING_PATH_FILE)
        return

    data = json.loads(LEARNING_PATH_FILE.read_text(encoding="utf-8"))

    chapters = data.get("chapters", [])
    chap_count = 0
    kp_count = 0
    for ch_idx, ch in enumerate(chapters):
        existing = crud_chapter.get_chapter_by_code(db, ch["code"])
        if existing is None:
            chapter = crud_chapter.create_chapter(
                db,
                code=ch["code"],
                title=ch["title"],
                order_index=ch.get("order_index", ch_idx),
                description=ch.get("description", ""),
            )
            chap_count += 1
        else:
            chapter = existing
            # Update title/order/desc if changed
            chapter.title = ch["title"]
            chapter.order_index = ch.get("order_index", chapter.order_index)
            chapter.description = ch.get("description", chapter.description)

        for kp_idx, kp in enumerate(ch.get("knowledge_points", [])):
            existing_kp = crud_kp.get_kp_by_code(db, kp["code"])
            keywords_json = json.dumps(kp.get("keywords", []), ensure_ascii=False)
            if existing_kp is None:
                crud_kp.create_kp(
                    db,
                    chapter_id=chapter.id,
                    code=kp["code"],
                    title=kp["title"],
                    order_index=kp.get("order_index", kp_idx),
                    keywords=keywords_json,
                    description=kp.get("description", ""),
                )
                kp_count += 1
            else:
                existing_kp.chapter_id = chapter.id
                existing_kp.title = kp["title"]
                existing_kp.order_index = kp.get("order_index", existing_kp.order_index)
                existing_kp.keywords = keywords_json
                existing_kp.description = kp.get("description", existing_kp.description)

    db.commit()
    logger.info(
        "Learning path seeded: +%d chapters, +%d knowledge points (existing rows updated).",
        chap_count,
        kp_count,
    )


def seed_default_llm_config(db: Session) -> None:
    """If no LLM config exists, seed one from environment defaults."""
    existing = crud_llm.list_configs(db)
    if existing:
        return

    if not settings.default_llm_api_key or settings.default_llm_api_key == "sk-your-api-key-here":
        logger.info(
            "No LLM config in DB and DEFAULT_LLM_API_KEY not set — skipping seed. "
            "Create one via POST /api/v1/llm-configs."
        )
        return

    from app.schemas.common import Provider
    try:
        provider = Provider(settings.default_llm_provider.lower())
    except ValueError:
        logger.warning(
            "Invalid DEFAULT_LLM_PROVIDER=%s, skipping LLM seed.",
            settings.default_llm_provider,
        )
        return

    data = LLMConfigCreate(
        name=f"{provider.value}-default",
        provider=provider,
        api_key=settings.default_llm_api_key,
        api_base=settings.default_llm_api_base,
        model=settings.default_llm_model,
        temperature=settings.default_llm_temperature,
        max_tokens=settings.default_llm_max_tokens,
        extra={},
    )
    cfg = crud_llm.create_config(db, data)
    crud_llm.activate_config(db, cfg.id)
    db.commit()
    logger.info("Default LLM config '%s' seeded and activated.", cfg.name)


def run_all_seeds(db: Session) -> None:
    seed_learning_path(db)
    seed_default_llm_config(db)
