from __future__ import annotations

import json
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any

STORE_PATH = Path(__file__).resolve().with_name("jobs.json")
_store_lock = threading.RLock()
_jobs: dict[str, dict[str, Any]] = {}


def _load() -> None:
    global _jobs
    with _store_lock:
        if not STORE_PATH.exists():
            _jobs = {}
            return

        try:
            data = json.loads(STORE_PATH.read_text(encoding="utf-8"))
            _jobs = data if isinstance(data, dict) else {}
        except Exception:
            _jobs = {}


def save() -> None:
    with _store_lock:
        STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

        temp_path = STORE_PATH.with_suffix(".tmp")
        temp_path.write_text(
            json.dumps(_jobs, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temp_path.replace(STORE_PATH)


def create_job(job: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(job, dict):
        raise ValueError("job must be a dict")

    job_id = job.get("job_id")
    if not isinstance(job_id, str) or not job_id.strip():
        raise ValueError("job_id is required")

    with _store_lock:
        _jobs[job_id] = deepcopy(job)
        save()
        return deepcopy(_jobs[job_id])


def get_job(job_id: str) -> dict[str, Any] | None:
    if not isinstance(job_id, str) or not job_id.strip():
        return None

    with _store_lock:
        job = _jobs.get(job_id)
        return deepcopy(job) if job else None


def update_job(job_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(job_id, str) or not job_id.strip():
        return None
    if not isinstance(updates, dict):
        raise ValueError("updates must be a dict")

    with _store_lock:
        if job_id not in _jobs:
            return None

        _jobs[job_id].update(deepcopy(updates))
        save()
        return deepcopy(_jobs[job_id])


def delete_job(job_id: str) -> bool:
    if not isinstance(job_id, str) or not job_id.strip():
        return False

    with _store_lock:
        if job_id not in _jobs:
            return False
        del _jobs[job_id]
        save()
        return True


def list_jobs() -> list[dict[str, Any]]:
    with _store_lock:
        return [deepcopy(job) for job in _jobs.values()]


_load()
