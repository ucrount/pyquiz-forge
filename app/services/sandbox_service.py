"""Code sandbox service — runs user code via the Piston public API.

Each test case runs as a separate Piston request (sequential). Results are
normalized into a uniform shape regardless of language or runtime errors.
No code is executed inside our container — Piston handles isolation.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


# Map our language slugs to Piston (language, version) tuples.
# Versions chosen as recent stable runtimes that emkc.org supports.
_PISTON_LANGS: Dict[str, tuple[str, str]] = {
    "python": ("python", "3.10.0"),
    "javascript": ("javascript", "18.15.0"),
    "java": ("java", "15.0.2"),
    "go": ("go", "1.16.2"),
}


class SandboxError(Exception):
    """Raised when sandbox infrastructure fails (not when user code fails)."""


def _piston_payload(language: str, source: str, stdin: str = "") -> dict:
    lang_id, version = _PISTON_LANGS.get(language, (language, "*"))
    return {
        "language": lang_id,
        "version": version,
        "files": [{"content": source}],
        "stdin": stdin or "",
        "compile_timeout": settings.piston_compile_timeout_ms,
        "run_timeout": settings.piston_run_timeout_ms,
    }


def _classify(piston_response: dict, expected: str) -> tuple[str, str]:
    """
    Inspect a Piston response and return (status, actual_output).
    status ∈ pass | wrong_answer | runtime_error | compile_error | timeout
    """
    compile_data = piston_response.get("compile") or {}
    run_data = piston_response.get("run") or {}

    # Compile error (Java/Go)
    if compile_data.get("code") not in (None, 0):
        stderr = compile_data.get("stderr") or compile_data.get("output") or ""
        return "compile_error", stderr.strip()

    # Timeout — Piston signals via signal "SIGKILL" or signal:"SIGTERM"
    if run_data.get("signal") in ("SIGKILL", "SIGTERM", "SIGXCPU"):
        return "timeout", run_data.get("stderr", "").strip() or "Time limit exceeded"

    stdout = (run_data.get("stdout") or "").rstrip("\n")
    stderr = (run_data.get("stderr") or "").rstrip("\n")
    exit_code = run_data.get("code")

    # Non-zero exit = runtime error
    if exit_code not in (None, 0):
        return "runtime_error", (stderr or stdout).strip()

    # Compare stdout to expected
    actual = stdout.strip()
    if actual == (expected or "").strip():
        return "pass", actual
    return "wrong_answer", actual


def run_one(
    language: str,
    source: str,
    stdin: str = "",
    expected: str = "",
) -> Dict[str, Any]:
    """
    Run code once with given stdin. Returns:
      {
        status: pass | wrong_answer | runtime_error | compile_error | timeout,
        actual: stdout (or stderr summary on errors),
        stderr: full stderr,
        runtime_ms: int,
        ...
      }
    Raises SandboxError on infrastructure failures (network / 5xx / etc).
    """
    if language not in _PISTON_LANGS:
        raise SandboxError(f"Unsupported language for sandbox: {language}")

    payload = _piston_payload(language, source, stdin)
    t0 = time.perf_counter()
    try:
        with httpx.Client(timeout=30.0) as c:
            r = c.post(f"{settings.piston_api_base}/execute", json=payload)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPStatusError as e:
        msg = f"Piston HTTP {e.response.status_code}: {e.response.text[:200]}"
        logger.error(msg)
        raise SandboxError(msg)
    except httpx.RequestError as e:
        msg = f"Piston unreachable: {type(e).__name__}: {e}"
        logger.error(msg)
        raise SandboxError(msg)
    except Exception as e:
        raise SandboxError(f"Piston error: {type(e).__name__}: {e}")

    elapsed = int((time.perf_counter() - t0) * 1000)
    status, actual = _classify(data, expected)
    run_data = data.get("run") or {}
    return {
        "status": status,
        "actual": actual,
        "stdout": run_data.get("stdout", ""),
        "stderr": run_data.get("stderr", ""),
        "exit_code": run_data.get("code"),
        "signal": run_data.get("signal"),
        "runtime_ms": elapsed,
    }


def judge(
    language: str,
    source: str,
    test_cases: List[dict],
) -> Dict[str, Any]:
    """
    Run code against all test cases. Returns aggregate result + per-case detail.

    Stops at first compile_error (subsequent cases would all fail the same way).
    """
    results: List[Dict[str, Any]] = []
    passed = 0
    early_stop = False

    for idx, tc in enumerate(test_cases):
        stdin = str(tc.get("input") or "")
        expected = str(tc.get("expected_output") or "")
        try:
            r = run_one(language, source, stdin, expected)
        except SandboxError as e:
            r = {
                "status": "infra_error",
                "actual": "",
                "stdout": "",
                "stderr": str(e),
                "exit_code": None,
                "signal": None,
                "runtime_ms": 0,
            }
        r["test_index"] = idx
        r["input"] = stdin
        r["expected"] = expected
        results.append(r)
        if r["status"] == "pass":
            passed += 1
        elif r["status"] == "compile_error":
            # Compile is global — no point running remaining cases
            early_stop = True
            break

    total = len(test_cases)
    return {
        "language": language,
        "passed": passed,
        "total": total,
        "all_passed": passed == total and total > 0,
        "early_stop": early_stop,
        "results": results,
    }


def list_supported_languages() -> List[str]:
    return sorted(_PISTON_LANGS.keys())
