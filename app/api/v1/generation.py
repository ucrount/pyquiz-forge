"""Generation endpoints: single, batch, regenerate."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import exercise as crud_exercise
from app.crud import generation_log as crud_log
from app.schemas.exercise import ExerciseRead
from app.schemas.generation import (
    BatchGenerateRequest,
    BatchGenerateResult,
    GenerateRequest,
    GenerationLogDetail,
    GenerationLogRead,
    RegenerateRequest,
)
from app.services import generation_service
from app.services.generation_service import GenerationError

router = APIRouter(tags=["generation"])


@router.post("/exercises/generate", response_model=ExerciseRead, status_code=201)
def generate_one(req: GenerateRequest, db: Session = Depends(get_db)):
    try:
        ex = generation_service.generate_one(
            db,
            knowledge_point_id=req.knowledge_point_id,
            difficulty=req.difficulty,
            question_type=req.question_type,
            llm_config_id=req.llm_config_id,
        )
    except GenerationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ex


@router.post(
    "/exercises/generate/batch",
    response_model=BatchGenerateResult,
    status_code=201,
)
def generate_batch(req: BatchGenerateRequest, db: Session = Depends(get_db)):
    succeeded: List = []
    failed: List[dict] = []
    for item in req.items:
        for _ in range(item.count):
            try:
                ex = generation_service.generate_one(
                    db,
                    knowledge_point_id=req.knowledge_point_id,
                    difficulty=item.difficulty,
                    question_type=item.question_type,
                    llm_config_id=req.llm_config_id,
                )
                succeeded.append(ex)
            except GenerationError as e:
                failed.append(
                    {
                        "difficulty": item.difficulty.value,
                        "question_type": item.question_type.value,
                        "error": str(e),
                    }
                )
    return BatchGenerateResult(
        succeeded=[ExerciseRead.model_validate(s) for s in succeeded],
        failed=failed,
    )


@router.post(
    "/exercises/{exercise_id}/regenerate",
    response_model=ExerciseRead,
    status_code=201,
)
def regenerate(
    exercise_id: int,
    req: RegenerateRequest,
    db: Session = Depends(get_db),
):
    ex = crud_exercise.get_exercise(db, exercise_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    try:
        new_ex = generation_service.regenerate(
            db,
            exercise=ex,
            mode=req.mode,
            llm_config_id=req.llm_config_id,
        )
    except GenerationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return new_ex


@router.get("/generation-logs", response_model=List[GenerationLogRead])
def list_generation_logs(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    items, _total = crud_log.list_logs(db, page=page, size=size)
    return items


@router.get("/generation-logs/{log_id}", response_model=GenerationLogDetail)
def get_generation_log(log_id: int, db: Session = Depends(get_db)):
    log = crud_log.get_log(db, log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
