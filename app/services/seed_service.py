"""Seed service: load learning_path_*.json files into DB on startup (idempotent).

Each language has its own file `learning_path_<lang>.json` with a top-level
`language` field. Codes inside each file are global identifiers and should
already be language-prefixed (e.g. `py-ch01`, `java-ch01`). This module
upserts chapters + knowledge points by code.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import get_logger
from app.crud import chapter as crud_chapter
from app.crud import knowledge_point as crud_kp
from app.crud import llm_config as crud_llm
from app.schemas.llm_config import LLMConfigCreate

logger = get_logger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _seed_one_language_file(db: Session, path: Path) -> tuple[int, int]:
    """Seed a single language file. Returns (chap_added, kp_added)."""
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    language = (data.get("language") or "").strip()
    if not language:
        logger.warning(
            "Skipping %s — no top-level 'language' field.", path.name
        )
        return 0, 0

    chapters = data.get("chapters", [])
    chap_count = 0
    kp_count = 0

    for ch_idx, ch in enumerate(chapters):
        code = ch["code"]
        existing = crud_chapter.get_chapter_by_code(db, code)
        if existing is None:
            chapter = crud_chapter.create_chapter(
                db,
                language=language,
                code=code,
                title=ch["title"],
                order_index=ch.get("order_index", ch_idx),
                description=ch.get("description", ""),
            )
            chap_count += 1
        else:
            chapter = existing
            chapter.language = language
            chapter.title = ch["title"]
            chapter.order_index = ch.get("order_index", chapter.order_index)
            chapter.description = ch.get("description", chapter.description)

        for kp_idx, kp in enumerate(ch.get("knowledge_points", [])):
            kp_code = kp["code"]
            existing_kp = crud_kp.get_kp_by_code(db, kp_code)
            keywords_json = json.dumps(kp.get("keywords", []), ensure_ascii=False)
            if existing_kp is None:
                crud_kp.create_kp(
                    db,
                    chapter_id=chapter.id,
                    language=language,
                    code=kp_code,
                    title=kp["title"],
                    order_index=kp.get("order_index", kp_idx),
                    keywords=keywords_json,
                    description=kp.get("description", ""),
                )
                kp_count += 1
            else:
                existing_kp.chapter_id = chapter.id
                existing_kp.language = language
                existing_kp.title = kp["title"]
                existing_kp.order_index = kp.get("order_index", existing_kp.order_index)
                existing_kp.keywords = keywords_json
                existing_kp.description = kp.get("description", existing_kp.description)

    return chap_count, kp_count


def seed_learning_path(db: Session) -> None:
    """Idempotent: walk app/data/learning_path_*.json and upsert each."""
    files = sorted(DATA_DIR.glob("learning_path_*.json"))
    if not files:
        logger.warning(
            "No learning_path_*.json files found in %s — skipping seed.",
            DATA_DIR,
        )
        return

    total_ch, total_kp = 0, 0
    for f in files:
        try:
            ch, kp = _seed_one_language_file(db, f)
        except Exception as e:
            logger.error("Failed to seed %s: %s", f.name, e)
            continue
        if ch or kp:
            logger.info(
                "Seeded %s: +%d chapters, +%d knowledge points",
                f.name, ch, kp,
            )
        total_ch += ch
        total_kp += kp

    db.commit()
    logger.info(
        "Learning path seeded across %d files: +%d chapters, +%d knowledge points total.",
        len(files), total_ch, total_kp,
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
