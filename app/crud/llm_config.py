"""LLMConfig CRUD."""
import json
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import LLMConfig
from app.schemas.llm_config import LLMConfigCreate, LLMConfigUpdate


def list_configs(db: Session) -> List[LLMConfig]:
    stmt = select(LLMConfig).order_by(LLMConfig.id)
    return list(db.execute(stmt).scalars().all())


def get_config(db: Session, config_id: int) -> Optional[LLMConfig]:
    return db.get(LLMConfig, config_id)


def get_config_by_name(db: Session, name: str) -> Optional[LLMConfig]:
    stmt = select(LLMConfig).where(LLMConfig.name == name)
    return db.execute(stmt).scalar_one_or_none()


def get_active_config(db: Session) -> Optional[LLMConfig]:
    stmt = select(LLMConfig).where(LLMConfig.is_active.is_(True)).limit(1)
    return db.execute(stmt).scalar_one_or_none()


def create_config(db: Session, data: LLMConfigCreate) -> LLMConfig:
    obj = LLMConfig(
        name=data.name,
        provider=data.provider.value,
        api_key=data.api_key,
        api_base=data.api_base,
        model=data.model,
        temperature=data.temperature,
        max_tokens=data.max_tokens,
        extra=json.dumps(data.extra, ensure_ascii=False),
        is_active=False,
    )
    db.add(obj)
    db.flush()
    return obj


def update_config(db: Session, obj: LLMConfig, data: LLMConfigUpdate) -> LLMConfig:
    payload = data.model_dump(exclude_unset=True)
    if "provider" in payload and payload["provider"] is not None:
        payload["provider"] = payload["provider"].value
    if "extra" in payload and payload["extra"] is not None:
        payload["extra"] = json.dumps(payload["extra"], ensure_ascii=False)
    for k, v in payload.items():
        setattr(obj, k, v)
    db.flush()
    return obj


def delete_config(db: Session, obj: LLMConfig) -> None:
    db.delete(obj)
    db.flush()


def activate_config(db: Session, config_id: int) -> Optional[LLMConfig]:
    """Set the given config to active and deactivate all others. Atomic-ish."""
    target = db.get(LLMConfig, config_id)
    if target is None:
        return None
    db.execute(update(LLMConfig).values(is_active=False))
    target.is_active = True
    db.flush()
    return target
