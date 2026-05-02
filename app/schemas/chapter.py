"""Chapter schemas."""
from typing import List

from pydantic import BaseModel, ConfigDict


class ChapterBase(BaseModel):
    code: str
    title: str
    order_index: int = 0
    description: str = ""
    language: str = "python"


class ChapterRead(ChapterBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ChapterWithKnowledgePoints(ChapterRead):
    knowledge_points: List["KnowledgePointRead"] = []  # noqa: F821


# Late import to avoid circular ref
from app.schemas.knowledge_point import KnowledgePointRead  # noqa: E402

ChapterWithKnowledgePoints.model_rebuild()
