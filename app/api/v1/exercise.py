"""Exercise CRUD endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import exercise as crud_exercise
from app.schemas.common import Difficulty, ExerciseStatus, PageResult, QuestionType
from app.schemas.exercise import (
    BulkDeleteRequest,
    ExerciseListItem,
    ExerciseRead,
    ExerciseUpdate,
)

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=PageResult[ExerciseListItem])
def list_exercises(
    knowledge_point_id: Optional[int] = None,
    language: Optional[str] = None,
    difficulty: Optional[Difficulty] = None,
    question_type: Optional[QuestionType] = None,
    status: Optional[ExerciseStatus] = None,
    min_score: Optional[float] = Query(None, ge=0, le=10),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    items, total = crud_exercise.list_exercises(
        db,
        knowledge_point_id=knowledge_point_id,
        language=language,
        difficulty=difficulty.value if difficulty else None,
        question_type=question_type.value if question_type else None,
        status=status.value if status else None,
        min_score=min_score,
        page=page,
        size=size,
    )
    return PageResult(
        items=[ExerciseListItem.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{exercise_id}", response_model=ExerciseRead)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    ex = crud_exercise.get_exercise(db, exercise_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return ex


@router.patch("/{exercise_id}", response_model=ExerciseRead)
def update_exercise(
    exercise_id: int, data: ExerciseUpdate, db: Session = Depends(get_db)
):
    ex = crud_exercise.get_exercise(db, exercise_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    ex = crud_exercise.update_exercise(db, ex, data)
    db.commit()
    db.refresh(ex)
    return ex


@router.delete("/{exercise_id}", status_code=204)
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    ex = crud_exercise.get_exercise(db, exercise_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    crud_exercise.delete_exercise(db, ex)
    db.commit()
    return None


@router.post("/bulk-delete")
def bulk_delete_exercises(req: BulkDeleteRequest, db: Session = Depends(get_db)):
    n = crud_exercise.bulk_delete_exercises(db, req.ids)
    db.commit()
    return {"deleted": n}
