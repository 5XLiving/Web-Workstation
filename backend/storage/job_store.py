import threading
import json
import os

STORE_PATH = os.path.join(os.path.dirname(__file__), "jobs.json")
_store_lock = threading.RLock()
_jobs = {}

def _load():
    global _jobs
    if os.path.exists(STORE_PATH):
        try:
            with open(STORE_PATH, "r", encoding="utf-8") as f:
                _jobs = json.load(f)
            if not isinstance(_jobs, dict):
                _jobs = {}
        except Exception:
            _jobs = {}
    else:
        _jobs = {}

_load()

def save():
    with _store_lock:
        with open(STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(_jobs, f, indent=2)

def create_job(job):
    with _store_lock:
        _jobs[job["job_id"]] = job
        save()
        return job

def get_job(job_id):
    with _store_lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None

def update_job(job_id, updates):
    with _store_lock:
        if job_id in _jobs:
            _jobs[job_id].update(updates)
            save()
            return dict(_jobs[job_id])
        return None

def list_jobs():
    with _store_lock:
        return [dict(job) for job in _jobs.values()]