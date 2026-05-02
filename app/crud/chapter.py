"""Chapter CRUD."""
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Chapter, KnowledgePoint
from app.schemas.chapter import ChapterCreate, ChapterUpdate


def list_chapters(db: Session, language: Optional[str] = None) -> List[Chapter]:
    stmt = select(Chapter).order_by(Chapter.language, Chapter.order_index)
    if language:
        stmt = stmt.where(Chapter.language == language)
    return list(db.execute(stmt).scalars().all())


def list_chapters_with_kps(
    db: Session, language: Optional[str] = None
) -> List[Chapter]:
    stmt = (
        select(Chapter)
        .options(selectinload(Chapter.knowledge_points))
        .order_by(Chapter.language, Chapter.order_index)
    )
    if language:
        stmt = stmt.where(Chapter.language == language)
    return list(db.execute(stmt).scalars().all())


def get_chapter(db: Session, chapter_id: int) -> Optional[Chapter]:
    return db.get(Chapter, chapter_id)


def get_chapter_by_code(db: Session, code: str) -> Optional[Chapter]:
    stmt = select(Chapter).where(Chapter.code == code)
    return db.execute(stmt).scalar_one_or_none()


def max_order_index_for_language(db: Session, language: str) -> int:
    stmt = select(func.coalesce(func.max(Chapter.order_index), 0)).where(
        Chapter.language == language
    )
    return int(db.execute(stmt).scalar_one() or 0)


def create_chapter(db: Session, **kwargs) -> Chapter:
    """Generic create — used by seed_service. For API use create_from_schema."""
    obj = Chapter(**kwargs)
    db.add(obj)
    db.flush()
    return obj


def create_from_schema(db: Session, data: ChapterCreate) -> Chapter:
    obj = Chapter(
        code=data.code,
        title=data.title,
        language=data.language,
        order_index=data.order_index,
        description=data.description,
    )
    db.add(obj)
    db.flush()
    return obj


def update_chapter(db: Session, obj: Chapter, data: ChapterUpdate) -> Chapter:
    payload = data.model_dump(exclude_unset=True)
    for k, v in payload.items():
        setattr(obj, k, v)
    db.flush()
    return obj


def delete_chapter(db: Session, obj: Chapter) -> None:
    """Cascades to knowledge_points + exercises via FK ondelete=CASCADE."""
    db.delete(obj)
    db.flush()


def count_kps_in_chapter(db: Session, chapter_id: int) -> int:
    stmt = select(func.count(KnowledgePoint.id)).where(
        KnowledgePoint.chapter_id == chapter_id
    )
    return int(db.execute(stmt).scalar_one() or 0)
