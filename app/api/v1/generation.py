"""Generation endpoints: single, batch (async), regenerate, jobs."""
from concurrent.futures import ThreadPoolExecutor, as_completed
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

# How many exercises to generate concurrently in a batch job.
# Higher = faster wall clock, but more concurrent calls to the LLM provider.
# 3 is a safe default for typical rate limits.
_BATCH_CONCURRENCY = 3


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


def _generate_one_in_thread(
    job_id: str,
    knowledge_point_id: int,
    item: dict,
    seq_label: str,
    llm_config_id: int | None,
) -> None:
    """
    One unit of work for ThreadPoolExecutor: generates a single exercise,
    updates the job state with start/success/fail events. Each thread gets
    its own DB session — never share a Session across threads.
    """
    import time as _time

    db = SessionLocal()
    job_service.update_job(job_id, current=seq_label)
    job_service.append_event(job_id, kind="start", label=seq_label)
    t0 = _time.perf_counter()
    try:
        ex = generation_service.generate_one(
            db,
            knowledge_point_id=knowledge_point_id,
            difficulty=item["difficulty"],
            question_type=item["question_type"],
            llm_config_id=llm_config_id,
        )
        latency_ms = int((_time.perf_counter() - t0) * 1000)
        job_service.progress_job(
            job_id,
            current_label=seq_label,
            succeeded_id=ex.id,
        )
        job_service.append_event(
            job_id,
            kind="success",
            label=seq_label,
            exercise_id=ex.id,
            latency_ms=latency_ms,
        )
    except GenerationError as e:
        latency_ms = int((_time.perf_counter() - t0) * 1000)
        job_service.progress_job(
            job_id,
            current_label=seq_label,
            failed={
                "difficulty": item["difficulty"],
                "question_type": item["question_type"],
                "error": str(e),
            },
        )
        job_service.append_event(
            job_id,
            kind="fail",
            label=seq_label,
            error=str(e),
            latency_ms=latency_ms,
        )
    except Exception as e:  # 兜底
        latency_ms = int((_time.perf_counter() - t0) * 1000)
        err = f"unexpected: {type(e).__name__}: {e}"
        job_service.progress_job(
            job_id,
            current_label=seq_label,
            failed={
                "difficulty": item["difficulty"],
                "question_type": item["question_type"],
                "error": err,
            },
        )
        job_service.append_event(
            job_id,
            kind="fail",
            label=seq_label,
            error=err,
            latency_ms=latency_ms,
        )
    finally:
        db.close()


def _run_batch_job(
    job_id: str,
    knowledge_point_id: int,
    items: list,
    llm_config_id: int | None,
) -> None:
    """
    Background entry point. Expands items×count into individual unit tasks,
    runs them concurrently with a small worker pool.
    """
    units: list[tuple[dict, str]] = []
    for item in items:
        for n in range(item["count"]):
            label = f"{item['difficulty']} / {item['question_type']} ({n + 1}/{item['count']})"
            units.append((item, label))

    try:
        with ThreadPoolExecutor(max_workers=_BATCH_CONCURRENCY) as pool:
            futures = [
                pool.submit(
                    _generate_one_in_thread,
                    job_id,
                    knowledge_point_id,
                    item,
                    label,
                    llm_config_id,
                )
                for item, label in units
            ]
            # Drain all so exceptions inside threads don't get silently dropped
            for f in as_completed(futures):
                try:
                    f.result()
                except Exception:
                    # Already recorded as a fail event by _generate_one_in_thread,
                    # this is just belt-and-suspenders.
                    pass
    finally:
        job_service.finish_job(job_id, status="done")


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
