"""Title-similarity-based deduplication for generated exercises.

Strategy:
1. Before calling LLM: fetch existing titles in the same KP and inject them
   into the prompt as a "please avoid these" block. This prevents most
   duplicates at the source.
2. After parsing the LLM response: compute fuzzy similarity of the new
   title against the same existing titles. If above threshold, signal
   the caller (which will retry once before giving up).

Uses stdlib `difflib.SequenceMatcher` — good enough for short titles,
no extra deps.
"""
from __future__ import annotations

import difflib
from typing import Optional

from sqlalchemy.orm import Session

from app.crud import exercise as crud_exercise


def get_existing_titles(db: Session, kp_id: int, limit: int = 20) -> list[str]:
    """Return up to `limit` most-recent exercise titles for a knowledge point."""
    items, _total = crud_exercise.list_exercises(
        db, knowledge_point_id=kp_id, page=1, size=limit
    )
    return [ex.title for ex in items if ex.title]


def title_similarity(a: str, b: str) -> float:
    """Return Jaccard-style fuzzy similarity in [0, 1]. Case-insensitive."""
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_too_similar(
    new_title: str,
    existing: list[str],
    threshold: float = 0.7,
) -> Optional[str]:
    """If new_title is too similar to any in `existing`, return the matching one."""
    if not new_title or not existing:
        return None
    for old in existing:
        if title_similarity(new_title, old) >= threshold:
            return old
    return None
