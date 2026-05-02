"""KnowledgePoint schemas."""
from typing import List

from pydantic import BaseModel, ConfigDict, field_validator
import json


class KnowledgePointBase(BaseModel):
    code: str
    title: str
    order_index: int = 0
    description: str = ""
    language: str = "python"


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
