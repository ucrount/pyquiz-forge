"""In-memory job tracker for long-running batch operations.

Used primarily for batch exercise generation: the API kicks off a background
task that calls `update_job` as it progresses, and the frontend polls
`get_job` to render a progress bar.

State lives in-process; if the server restarts, jobs are lost. That's
acceptable for transient generation jobs — finished exercises are still
in the DB.
"""
from __future__ import annotations

import time
import uuid
from threading import Lock
from typing import Any, Dict, List, Optional

from app.core.logger import get_logger

logger = get_logger(__name__)

_jobs: Dict[str, Dict[str, Any]] = {}
_lock = Lock()

# How long to retain finished jobs before letting them be GC'd
_RETENTION_SECONDS = 3600  # 1 hour


def _now() -> float:
    return time.time()


def _gc_old_jobs() -> None:
    """Drop jobs that finished more than _RETENTION_SECONDS ago."""
    now = _now()
    with _lock:
        stale = [
            jid
            for jid, job in _jobs.items()
            if job.get("finished_at")
            and (now - job["finished_at"]) > _RETENTION_SECONDS
        ]
        for jid in stale:
            _jobs.pop(jid, None)


def create_job(*, total: int, kind: str = "generation") -> str:
    """Create a new job and return its id."""
    _gc_old_jobs()
    job_id = uuid.uuid4().hex
    with _lock:
        _jobs[job_id] = {
            "id": job_id,
            "kind": kind,
            "status": "running",  # running | done | failed
            "total": total,
            "completed": 0,
            "current": "",
            "succeeded": [],  # exercise ids
            "failed": [],  # {error, params}
            "events": [],  # streaming log: [{ts, kind, label, exercise_id?, error?, latency_ms?}]
            "created_at": _now(),
            "finished_at": None,
        }
    logger.info("Job %s created (%s, total=%d)", job_id, kind, total)
    return job_id


def append_event(
    job_id: str,
    *,
    kind: str,
    label: str = "",
    exercise_id: Optional[int] = None,
    error: str = "",
    latency_ms: int = 0,
) -> None:
    """
    Push one streaming event to the job. kinds:
      - 'start':    a new item began
      - 'success':  item completed successfully
      - 'fail':     item failed (error filled)

    Frontend tails this list while the job runs, like a console log.
    Capped at 500 entries to keep memory bounded.
    """
    event = {
        "ts": _now(),
        "kind": kind,
        "label": label,
        "exercise_id": exercise_id,
        "error": error,
        "latency_ms": latency_ms,
    }
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return
        events = job.setdefault("events", [])
        events.append(event)
        if len(events) > 500:
            del events[: len(events) - 500]


def update_job(job_id: str, **patch: Any) -> None:
    """Patch arbitrary fields on a job. Use with care."""
    with _lock:
        job = _jobs.get(job_id)
        if job is not None:
            job.update(patch)


def progress_job(
    job_id: str,
    *,
    current_label: str = "",
    succeeded_id: Optional[int] = None,
    failed: Optional[Dict[str, Any]] = None,
) -> None:
    """Increment completion counter and optionally record success/failure."""
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return
        job["completed"] = job.get("completed", 0) + 1
        if current_label:
            job["current"] = current_label
        if succeeded_id is not None:
            job["succeeded"].append(succeeded_id)
        if failed:
            job["failed"].append(failed)


def finish_job(job_id: str, *, status: str = "done") -> None:
    with _lock:
        job = _jobs.get(job_id)
        if job is not None:
            job["status"] = status
            job["finished_at"] = _now()
            job["current"] = ""


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Return a snapshot copy of the job state."""
    with _lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        # Return a shallow copy so caller can't mutate
        return dict(job)


def list_jobs(limit: int = 20) -> List[Dict[str, Any]]:
    """List recent jobs (most recent first)."""
    with _lock:
        items = sorted(_jobs.values(), key=lambda j: j["created_at"], reverse=True)
        return [dict(j) for j in items[:limit]]
