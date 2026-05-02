"""Generation request/response schemas."""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Difficulty, QuestionType
from app.schemas.exercise import ExerciseRead


class GenerateRequest(BaseModel):
    knowledge_point_id: int
    difficulty: Difficulty
    question_type: QuestionType
    llm_config_id: Optional[int] = Field(
        default=None,
        description="If omitted, uses the currently active LLM config.",
    )


class BatchItem(BaseModel):
    difficulty: Difficulty
    question_type: QuestionType
    count: int = Field(ge=1, le=10, default=1)


class BatchGenerateRequest(BaseModel):
    knowledge_point_id: int
    items: List[BatchItem] = Field(min_length=1)
    llm_config_id: Optional[int] = None


class BatchGenerateResult(BaseModel):
    succeeded: List[ExerciseRead] = []
    failed: List[dict] = []  # {difficulty, question_type, error}


class RegenerateRequest(BaseModel):
    mode: str = Field(default="new", pattern="^(new|overwrite)$")
    llm_config_id: Optional[int] = None


class GenerationLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    llm_config_id: Optional[int]
    knowledge_point_id: Optional[int]
    difficulty: str
    question_type: str
    parsed_ok: bool
    error_message: str
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int


class GenerationLogDetail(GenerationLogRead):
    prompt: str
    raw_response: str
