"""KnowledgePoint CRUD."""
import json
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Exercise, KnowledgePoint
from app.schemas.knowledge_point import KnowledgePointCreate, KnowledgePointUpdate


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


def max_order_index_in_chapter(db: Session, chapter_id: int) -> int:
    stmt = select(func.coalesce(func.max(KnowledgePoint.order_index), 0)).where(
        KnowledgePoint.chapter_id == chapter_id
    )
    return int(db.execute(stmt).scalar_one() or 0)


def create_kp(db: Session, **kwargs) -> KnowledgePoint:
    """Generic create — used by seed_service."""
    obj = KnowledgePoint(**kwargs)
    db.add(obj)
    db.flush()
    return obj


def create_from_schema(db: Session, data: KnowledgePointCreate) -> KnowledgePoint:
    obj = KnowledgePoint(
        chapter_id=data.chapter_id,
        code=data.code,
        title=data.title,
        language=data.language,
        order_index=data.order_index,
        keywords=json.dumps(data.keywords or [], ensure_ascii=False),
        description=data.description,
    )
    db.add(obj)
    db.flush()
    return obj


def update_kp(
    db: Session, obj: KnowledgePoint, data: KnowledgePointUpdate
) -> KnowledgePoint:
    payload = data.model_dump(exclude_unset=True)
    if "keywords" in payload and payload["keywords"] is not None:
        payload["keywords"] = json.dumps(payload["keywords"], ensure_ascii=False)
    for k, v in payload.items():
        setattr(obj, k, v)
    db.flush()
    return obj


def delete_kp(db: Session, obj: KnowledgePoint) -> None:
    """Cascades to exercises via FK ondelete=CASCADE."""
    db.delete(obj)
    db.flush()


def count_exercises_for_kp(db: Session, kp_id: int) -> int:
    stmt = select(func.count(Exercise.id)).where(Exercise.knowledge_point_id == kp_id)
    return int(db.execute(stmt).scalar_one() or 0)
