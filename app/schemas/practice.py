"""Practice mode schemas."""
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import Difficulty, ExerciseStatus, Mastery, QuestionType
from app.schemas.exercise import ExerciseRead


class PracticeSessionRequest(BaseModel):
    """Filters for picking N random exercises to practice on."""
    language: Optional[str] = None
    chapter_id: Optional[int] = None
    knowledge_point_id: Optional[int] = None
    difficulties: Optional[List[Difficulty]] = None
    question_types: Optional[List[QuestionType]] = None
    min_score: Optional[float] = Field(default=None, ge=0, le=10)
    status: Optional[ExerciseStatus] = ExerciseStatus.published
    # Optional: only pick exercises whose KP has these mastery states
    # (e.g. ["unknown", "learning"] for "review the rough spots")
    kp_mastery: Optional[List[Mastery]] = None
    size: int = Field(default=10, ge=1, le=50)
    random_order: bool = True


class PracticeSessionResponse(BaseModel):
    questions: List[ExerciseRead]
    total_available: int  # how many matched the filters in total


class PracticeStats(BaseModel):
    """Frontend submits final stats for logging (optional)."""
    total: int
    correct: int
    skipped: int
    duration_ms: int
    by_type: dict = Field(default_factory=dict)