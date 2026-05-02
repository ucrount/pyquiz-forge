"""LLMConfig schemas."""
from typing import Any, Dict, Optional
import json

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import Provider


def mask_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


class LLMConfigBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    provider: Provider
    api_key: str = Field(min_length=1)
    api_base: str = ""
    model: str = Field(min_length=1, max_length=100)
    temperature: float = Field(ge=0.0, le=2.0, default=0.7)
    max_tokens: int = Field(ge=1, le=32000, default=2048)
    extra: Dict[str, Any] = Field(default_factory=dict)


class LLMConfigCreate(LLMConfigBase):
    pass


class LLMConfigUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[Provider] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=32000)
    extra: Optional[Dict[str, Any]] = None


class LLMConfigRead(BaseModel):
    """Public read model — api_key is masked."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    provider: str
    api_key: str  # masked
    api_base: str
    model: str
    temperature: float
    max_tokens: int
    extra: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool

    @field_validator("api_key", mode="before")
    @classmethod
    def _mask(cls, v):
        return mask_key(v) if isinstance(v, str) else v

    @field_validator("extra", mode="before")
    @classmethod
    def _parse_extra(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v) if v else {}
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                return {}
        return v or {}


class LLMTestResult(BaseModel):
    ok: bool
    message: str
    latency_ms: int = 0
