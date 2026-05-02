"""Chapter CRUD."""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Chapter


def list_chapters(db: Session) -> List[Chapter]:
    stmt = select(Chapter).order_by(Chapter.order_index)
    return list(db.execute(stmt).scalars().all())


def list_chapters_with_kps(db: Session) -> List[Chapter]:
    stmt = (
        select(Chapter)
        .options(selectinload(Chapter.knowledge_points))
        .order_by(Chapter.order_index)
    )
    return list(db.execute(stmt).scalars().all())


def get_chapter(db: Session, chapter_id: int) -> Optional[Chapter]:
    return db.get(Chapter, chapter_id)


def get_chapter_by_code(db: Session, code: str) -> Optional[Chapter]:
    stmt = select(Chapter).where(Chapter.code == code)
    return db.execute(stmt).scalar_one_or_none()


def create_chapter(db: Session, **kwargs) -> Chapter:
    obj = Chapter(**kwargs)
    db.add(obj)
    db.flush()
    return obj
