"""Practice mode endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import exercise as crud_exercise
from app.crud import knowledge_point as crud_kp
from app.schemas.exercise import ExerciseRead
from app.schemas.practice import PracticeSessionRequest, PracticeSessionResponse

router = APIRouter(prefix="/practice", tags=["practice"])


@router.post("/session", response_model=PracticeSessionResponse)
def create_practice_session(
    req: PracticeSessionRequest,
    db: Session = Depends(get_db),
):
    """
    Pick up to `size` random exercises matching the filters.
    Returns full exercise objects so the frontend can render and grade.

    `kp_mastery` (optional): only include exercises whose KP has one of the
    given mastery states. Useful for "review the rough spots" sessions.
    """
    kp_ids_filter = None
    if req.kp_mastery:
        mastery_values = [m.value for m in req.kp_mastery]
        kps = crud_kp.list_kps(
            db, language=req.language, mastery=mastery_values,
        )
        # -1 ensures the IN clause produces an empty result if no KP matches
        kp_ids_filter = [kp.id for kp in kps] or [-1]

    items, total = crud_exercise.list_exercises(
        db,
        chapter_id=req.chapter_id,
        knowledge_point_id=req.knowledge_point_id,
        knowledge_point_ids=kp_ids_filter,
        language=req.language,
        difficulties=[d.value for d in req.difficulties] if req.difficulties else None,
        question_types=[q.value for q in req.question_types] if req.question_types else None,
        min_score=req.min_score,
        status=req.status.value if req.status else None,
        page=1,
        size=req.size,
        random_order=req.random_order,
    )
    return PracticeSessionResponse(
        questions=[ExerciseRead.model_validate(i) for i in items],
        total_available=total,
    )
