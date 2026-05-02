"""LLM config endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import llm_config as crud_llm
from app.schemas.llm_config import (
    LLMConfigCreate,
    LLMConfigRead,
    LLMConfigUpdate,
    LLMTestResult,
)
from app.services.generation_service import test_llm_config

router = APIRouter(prefix="/llm-configs", tags=["llm-configs"])


@router.get("", response_model=List[LLMConfigRead])
def list_configs(db: Session = Depends(get_db)):
    return crud_llm.list_configs(db)


@router.get("/{config_id}", response_model=LLMConfigRead)
def get_config(config_id: int, db: Session = Depends(get_db)):
    cfg = crud_llm.get_config(db, config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="LLM config not found")
    return cfg


@router.post("", response_model=LLMConfigRead, status_code=201)
def create_config(data: LLMConfigCreate, db: Session = Depends(get_db)):
    if crud_llm.get_config_by_name(db, data.name):
        raise HTTPException(status_code=400, detail="name already exists")
    cfg = crud_llm.create_config(db, data)
    db.commit()
    db.refresh(cfg)
    return cfg


@router.put("/{config_id}", response_model=LLMConfigRead)
def update_config(
    config_id: int, data: LLMConfigUpdate, db: Session = Depends(get_db)
):
    cfg = crud_llm.get_config(db, config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="LLM config not found")
    if data.name and data.name != cfg.name:
        if crud_llm.get_config_by_name(db, data.name):
            raise HTTPException(status_code=400, detail="name already exists")
    cfg = crud_llm.update_config(db, cfg, data)
    db.commit()
    db.refresh(cfg)
    return cfg


@router.delete("/{config_id}", status_code=204)
def delete_config(config_id: int, db: Session = Depends(get_db)):
    cfg = crud_llm.get_config(db, config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="LLM config not found")
    crud_llm.delete_config(db, cfg)
    db.commit()
    return None


@router.post("/{config_id}/activate", response_model=LLMConfigRead)
def activate_config(config_id: int, db: Session = Depends(get_db)):
    cfg = crud_llm.activate_config(db, config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="LLM config not found")
    db.commit()
    db.refresh(cfg)
    return cfg


@router.post("/{config_id}/test", response_model=LLMTestResult)
def test_config(config_id: int, db: Session = Depends(get_db)):
    cfg = crud_llm.get_config(db, config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="LLM config not found")
    ok, message, latency_ms = test_llm_config(cfg)
    return LLMTestResult(ok=ok, message=message, latency_ms=latency_ms)
