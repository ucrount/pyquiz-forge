"""Generation endpoints: single, batch (async), regenerate, jobs."""
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.database import SessionLocal
from app.crud import exercise as crud_exercise
from app.crud import generation_log as crud_log
from app.schemas.exercise import ExerciseRead
from app.schemas.generation import (
    BatchGenerateRequest,
    BatchJobCreated,
    GenerateRequest,
    GenerationLogDetail,
    GenerationLogRead,
    JobProgress,
    RegenerateRequest,
)
from app.services import generation_service, job_service
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


def _run_batch_job(
    job_id: str,
    knowledge_point_id: int,
    items: list,
    llm_config_id: int | None,
) -> None:
    """Background task: iterate items, generate one by one, update job state."""
    db = SessionLocal()
    try:
        for item in items:
            for n in range(item["count"]):
                label = f"{item['difficulty']}/{item['question_type']} ({n + 1}/{item['count']})"
                job_service.update_job(job_id, current=label)
                try:
                    ex = generation_service.generate_one(
                        db,
                        knowledge_point_id=knowledge_point_id,
                        difficulty=item["difficulty"],
                        question_type=item["question_type"],
                        llm_config_id=llm_config_id,
                    )
                    job_service.progress_job(
                        job_id,
                        current_label=label,
                        succeeded_id=ex.id,
                    )
                except GenerationError as e:
                    job_service.progress_job(
                        job_id,
                        current_label=label,
                        failed={
                            "difficulty": item["difficulty"],
                            "question_type": item["question_type"],
                            "error": str(e),
                        },
                    )
                except Exception as e:  # 兜底，防止后台任务死掉
                    job_service.progress_job(
                        job_id,
                        current_label=label,
                        failed={
                            "difficulty": item["difficulty"],
                            "question_type": item["question_type"],
                            "error": f"unexpected: {type(e).__name__}: {e}",
                        },
                    )
        job_service.finish_job(job_id, status="done")
    finally:
        db.close()


@router.post(
    "/exercises/generate/batch",
    response_model=BatchJobCreated,
    status_code=202,
)
def generate_batch(
    req: BatchGenerateRequest,
    background_tasks: BackgroundTasks,
):
    """
    Kick off a background batch generation job.
    Returns immediately with `job_id`; client polls /generation-jobs/{id}.
    """
    total = sum(item.count for item in req.items)
    if total == 0:
        raise HTTPException(status_code=400, detail="items has zero total count")

    job_id = job_service.create_job(total=total, kind="batch_generation")

    # Convert pydantic items to plain dicts so the BG task is decoupled
    items_payload = [
        {
            "difficulty": item.difficulty.value,
            "question_type": item.question_type.value,
            "count": item.count,
        }
        for item in req.items
    ]
    background_tasks.add_task(
        _run_batch_job,
        job_id,
        req.knowledge_point_id,
        items_payload,
        req.llm_config_id,
    )
    return BatchJobCreated(job_id=job_id, total=total)


@router.get("/generation-jobs/{job_id}", response_model=JobProgress)
def get_generation_job(job_id: str):
    job = job_service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobProgress(**job)


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
