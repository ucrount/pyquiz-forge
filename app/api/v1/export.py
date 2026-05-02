"""Export endpoints: JSON and Markdown."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import exercise as crud_exercise
from app.schemas.common import Difficulty, ExerciseStatus, QuestionType
from app.services import export_service

router = APIRouter(prefix="/export", tags=["export"])


def _get_exercises(
    db: Session,
    knowledge_point_id: Optional[int],
    difficulty: Optional[Difficulty],
    question_type: Optional[QuestionType],
    status: Optional[ExerciseStatus],
):
    return crud_exercise.list_exercises_for_export(
        db,
        knowledge_point_id=knowledge_point_id,
        difficulty=difficulty.value if difficulty else None,
        question_type=question_type.value if question_type else None,
        status=status.value if status else None,
    )


@router.get("/json")
def export_json(
    knowledge_point_id: Optional[int] = None,
    difficulty: Optional[Difficulty] = None,
    question_type: Optional[QuestionType] = None,
    status: Optional[ExerciseStatus] = None,
    db: Session = Depends(get_db),
):
    exercises = _get_exercises(db, knowledge_point_id, difficulty, question_type, status)
    body = export_service.export_json(db, exercises)
    fname = f"pyquiz-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    return Response(
        content=body,
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@router.get("/markdown")
def export_markdown(
    knowledge_point_id: Optional[int] = None,
    difficulty: Optional[Difficulty] = None,
    question_type: Optional[QuestionType] = None,
    status: Optional[ExerciseStatus] = None,
    db: Session = Depends(get_db),
):
    exercises = _get_exercises(db, knowledge_point_id, difficulty, question_type, status)
    body = export_service.export_markdown(db, exercises)
    fname = f"pyquiz-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.md"
    return Response(
        content=body,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )
