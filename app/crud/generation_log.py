"""GenerationLog CRUD."""
from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import GenerationLog


def create_log(db: Session, **kwargs) -> GenerationLog:
    obj = GenerationLog(**kwargs)
    db.add(obj)
    db.flush()
    return obj


def get_log(db: Session, log_id: int) -> Optional[GenerationLog]:
    return db.get(GenerationLog, log_id)


def list_logs(
    db: Session, page: int = 1, size: int = 20
) -> Tuple[List[GenerationLog], int]:
    total = db.execute(select(func.count(GenerationLog.id))).scalar_one()
    stmt = (
        select(GenerationLog)
        .order_by(GenerationLog.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    items = list(db.execute(stmt).scalars().all())
    return items, total
