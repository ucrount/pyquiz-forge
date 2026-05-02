"""Quality scoring schemas."""
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ScoreRequest(BaseModel):
    llm_config_id: Optional[int] = Field(
        default=None,
        description="If omitted, uses the currently active LLM config.",
    )


class BatchScoreRequest(BaseModel):
    ids: List[int] = Field(min_length=1)
    llm_config_id: Optional[int] = None


class ScoreDimensions(BaseModel):
    """Per-dimension breakdown (1-10 scale, decimals OK)."""
    clarity: float = Field(ge=0, le=10, default=0)
    correctness: float = Field(ge=0, le=10, default=0)
    difficulty_match: float = Field(ge=0, le=10, default=0)
    educational_value: float = Field(ge=0, le=10, default=0)


class ScoreResult(BaseModel):
    """Returned to API caller and stored in DB."""
    model_config = ConfigDict(from_attributes=True)

    overall: float = Field(ge=0, le=10)
    dimensions: ScoreDimensions
    comment: str = ""


class BatchScoreResult(BaseModel):
    succeeded: List[Dict] = []  # {id, score: ScoreResult}
    failed: List[Dict] = []     # {id, error}
