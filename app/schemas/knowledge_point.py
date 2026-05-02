"""KnowledgePoint schemas."""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
import json


class KnowledgePointBase(BaseModel):
    code: str
    title: str
    order_index: int = 0
    description: str = ""
    language: str = "python"


class KnowledgePointCreate(BaseModel):
    chapter_id: int
    code: str = Field(min_length=1, max_length=20)
    title: str = Field(min_length=1, max_length=200)
    language: str = Field(min_length=1, max_length=20, default="python")
    order_index: int = 0
    keywords: List[str] = []
    description: str = ""


class KnowledgePointUpdate(BaseModel):
    chapter_id: Optional[int] = None
    code: Optional[str] = Field(default=None, min_length=1, max_length=20)
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    language: Optional[str] = Field(default=None, min_length=1, max_length=20)
    order_index: Optional[int] = None
    keywords: Optional[List[str]] = None
    description: Optional[str] = None


class KnowledgePointRead(KnowledgePointBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chapter_id: int
    keywords: List[str] = []

    @field_validator("keywords", mode="before")
    @classmethod
    def _parse_keywords(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v) if v else []
                return parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                return []
        return v or []
