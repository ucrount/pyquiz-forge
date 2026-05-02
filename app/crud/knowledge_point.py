"""KnowledgePoint CRUD."""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import KnowledgePoint


def list_kps(
    db: Session,
    chapter_id: Optional[int] = None,
    language: Optional[str] = None,
) -> List[KnowledgePoint]:
    stmt = select(KnowledgePoint).order_by(
        KnowledgePoint.language, KnowledgePoint.order_index
    )
    if chapter_id is not None:
        stmt = stmt.where(KnowledgePoint.chapter_id == chapter_id)
    if language:
        stmt = stmt.where(KnowledgePoint.language == language)
    return list(db.execute(stmt).scalars().all())


def get_kp(db: Session, kp_id: int) -> Optional[KnowledgePoint]:
    return db.get(KnowledgePoint, kp_id)


def get_kp_by_code(db: Session, code: str) -> Optional[KnowledgePoint]:
    stmt = select(KnowledgePoint).where(KnowledgePoint.code == code)
    return db.execute(stmt).scalar_one_or_none()


def create_kp(db: Session, **kwargs) -> KnowledgePoint:
    obj = KnowledgePoint(**kwargs)
    db.add(obj)
    db.flush()
    return obj
