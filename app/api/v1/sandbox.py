"""Sandbox endpoints: run arbitrary code, judge against an exercise."""
import json
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import exercise as crud_exercise
from app.schemas.sandbox import (
    JudgeRequest,
    JudgeResult,
    RunRequest,
    SupportedLangs,
)
from app.services import sandbox_service

router = APIRouter(prefix="/sandbox", tags=["sandbox"])


@router.get("/languages", response_model=SupportedLangs)
def list_supported():
    return SupportedLangs(languages=sandbox_service.list_supported_languages())


@router.post("/run", response_model=JudgeResult)
def run_against_test_cases(req: RunRequest):
    """
    Run code against an inline list of test cases. Used by interactive
    code-running where the test cases are not yet persisted as an exercise.
    """
    cases = [{"input": t.input, "expected_output": t.expected_output} for t in req.test_cases]
    try:
        result = sandbox_service.judge(req.language, req.source, cases)
    except sandbox_service.SandboxError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return result


@router.post("/judge/{exercise_id}", response_model=JudgeResult)
def judge_exercise(
    exercise_id: int,
    req: JudgeRequest,
    db: Session = Depends(get_db),
):
    """
    Run user-submitted code against the test_cases stored on this exercise.
    Used by the practice flow.
    """
    ex = crud_exercise.get_exercise(db, exercise_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    try:
        cases: List[dict] = json.loads(ex.test_cases) if ex.test_cases else []
    except json.JSONDecodeError:
        cases = []
    if not isinstance(cases, list) or not cases:
        raise HTTPException(
            status_code=400,
            detail="该题目没有测试用例，无法自动评判。",
        )

    language = req.language or ex.language or "python"
    if language not in sandbox_service.list_supported_languages():
        raise HTTPException(
            status_code=400,
            detail=f"沙箱暂不支持 {language}",
        )

    try:
        result = sandbox_service.judge(language, req.source, cases)
    except sandbox_service.SandboxError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return result
