"""Exercise schemas."""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import Difficulty, ExerciseStatus, QuestionType


class TestCase(BaseModel):
    input: str = ""
    expected_output: str = ""


class ExerciseBase(BaseModel):
    title: str
    knowledge_point_id: int
    language: str = "python"
    difficulty: Difficulty
    question_type: QuestionType
    description: str = ""
    example_input: str = ""
    example_output: str = ""
    hint: str = ""
    standard_answer: str = ""
    reference_code: str = ""
    test_cases: List[TestCase] = Field(default_factory=list)
    explanation: str = ""
    common_mistakes: str = ""
    extra: Dict[str, Any] = Field(default_factory=dict)


class ExerciseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    example_input: Optional[str] = None
    example_output: Optional[str] = None
    hint: Optional[str] = None
    standard_answer: Optional[str] = None
    reference_code: Optional[str] = None
    test_cases: Optional[List[TestCase]] = None
    explanation: Optional[str] = None
    common_mistakes: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None
    status: Optional[ExerciseStatus] = None


class ExerciseRead(ExerciseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    llm_config_id: Optional[int] = None
    generation_log_id: Optional[int] = None
    status: ExerciseStatus = ExerciseStatus.published

    # Scoring fields (None until POST /score is called)
    score_overall: Optional[float] = None
    score_detail: Dict[str, Any] = Field(default_factory=dict)
    score_comment: str = ""
    scored_at: Optional[datetime] = None
    score_llm_config_id: Optional[int] = None

    @field_validator("test_cases", mode="before")
    @classmethod
    def _parse_test_cases(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v) if v else []
                return parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                return []
        return v or []

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

    @field_validator("score_detail", mode="before")
    @classmethod
    def _parse_score_detail(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v) if v else {}
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                return {}
        return v or {}


class ExerciseListItem(BaseModel):
    """Compact item for list endpoint."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    knowledge_point_id: int
    language: str = "python"
    difficulty: Difficulty
    question_type: QuestionType
    status: ExerciseStatus
    score_overall: Optional[float] = None


class BulkDeleteRequest(BaseModel):
    ids: List[int] = Field(min_length=1)

