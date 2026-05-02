"""Scoring endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.exercise import ExerciseRead
from app.schemas.scoring import (
    BatchScoreRequest,
    BatchScoreResult,
    ScoreRequest,
    ScoreResult,
)
from app.services import scoring_service
from app.services.generation_service import GenerationError

router = APIRouter(tags=["scoring"])


@router.post("/exercises/{exercise_id}/score", response_model=ExerciseRead)
def score_exercise(
    exercise_id: int,
    req: ScoreRequest,
    db: Session = Depends(get_db),
):
    """Score a single exercise. Returns the updated exercise with score fields."""
    try:
        ex, _ = scoring_service.score_one(
            db,
            exercise_id=exercise_id,
            llm_config_id=req.llm_config_id,
        )
    except GenerationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ex


@router.post("/exercises/score/batch", response_model=BatchScoreResult)
def score_batch(req: BatchScoreRequest, db: Session = Depends(get_db)):
    """Score multiple exercises in one shot. Continues past individual failures."""
    succeeded: List[dict] = []
    failed: List[dict] = []
    for eid in req.ids:
        try:
            _, result = scoring_service.score_one(
                db,
                exercise_id=eid,
                llm_config_id=req.llm_config_id,
            )
            succeeded.append({"id": eid, "score": result.model_dump()})
        except GenerationError as e:
            failed.append({"id": eid, "error": str(e)})
    return BatchScoreResult(succeeded=succeeded, failed=failed)
