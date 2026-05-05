"""Sandbox API schemas."""
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class TestCaseInput(BaseModel):
    input: str = ""
    expected_output: str = ""


class RunRequest(BaseModel):
    language: str
    source: str
    test_cases: List[TestCaseInput] = Field(default_factory=list)


class JudgeRequest(BaseModel):
    """Submit user code against the test_cases stored on an exercise."""
    source: str
    language: Optional[str] = None  # if omitted, use the exercise's language


class TestResult(BaseModel):
    test_index: int
    input: str
    expected: str
    actual: str
    status: str  # pass | wrong_answer | runtime_error | compile_error | timeout | infra_error
    stdout: str = ""
    stderr: str = ""
    exit_code: Optional[int] = None
    signal: Optional[str] = None
    runtime_ms: int = 0


class JudgeResult(BaseModel):
    language: str
    passed: int
    total: int
    all_passed: bool
    early_stop: bool = False
    results: List[TestResult] = Field(default_factory=list)


class SupportedLangs(BaseModel):
    languages: List[str]
