"""Chapter schemas."""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChapterBase(BaseModel):
    code: str
    title: str
    order_index: int = 0
    description: str = ""
    language: str = "python"


class ChapterCreate(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    title: str = Field(min_length=1, max_length=100)
    language: str = Field(min_length=1, max_length=20, default="python")
    order_index: int = 0
    description: str = ""


class ChapterUpdate(BaseModel):
    code: Optional[str] = Field(default=None, min_length=1, max_length=20)
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    language: Optional[str] = Field(default=None, min_length=1, max_length=20)
    order_index: Optional[int] = None
    description: Optional[str] = None


class ChapterRead(ChapterBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ChapterWithKnowledgePoints(ChapterRead):
    knowledge_points: List["KnowledgePointRead"] = []  # noqa: F821


# Late import to avoid circular ref
from app.schemas.knowledge_point import KnowledgePointRead  # noqa: E402

ChapterWithKnowledgePoints.model_rebuild()
