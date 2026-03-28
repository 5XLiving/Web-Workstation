"""
Job queue system for async task processing
Simulates background processing with progress updates
"""
import uuid
import time
import threading
from typing import Dict, Optional, Any
from datetime import datetime

# Job store: {jobId: job_data}
_jobs: Dict[str, Dict] = {}

# Lock for thread-safe operations
_jobs_lock = threading.Lock()


class JobStatus:
    """Job status constants"""
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


def create_job(job_type: str, params: Dict) -> str:
    """
    Create a new job and return its ID
    
    Args:
        job_type: "image", "mesh_v1", "mesh_v2"
        params: Job parameters to store
    
    Returns:
        jobId (UUID string)
    """
    job_id = str(uuid.uuid4())
    
    with _jobs_lock:
        _jobs[job_id] = {
            "jobId": job_id,
            "type": job_type,
            "status": JobStatus.QUEUED,
            "progress": 0,
            "params": params,
            "result": {},
            "error": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    
    # Start background processing
    thread = threading.Thread(target=_process_job, args=(job_id,), daemon=True)
    thread.start()
    
    return job_id


def get_job(job_id: str) -> Optional[Dict]:
    """
    Get job status and result
    
    Returns:
        Job dict or None if not found
    """
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job:
            # Return a copy to avoid external modifications
            return job.copy()
        return None


def _update_job(job_id: str, updates: Dict):
    """Internal: Update job data (thread-safe)"""
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id].update(updates)
            _jobs[job_id]["updated_at"] = datetime.utcnow().isoformat()


def _process_job(job_id: str):
    """
    Background job processor (simulates AI processing)
    Runs in separate thread
    """
    job = get_job(job_id)
    if not job:
        return
    
    job_type = job["type"]
    
    try:
        # Simulate processing stages
        _update_job(job_id, {"status": JobStatus.RUNNING, "progress": 10})
        time.sleep(0.5)
        
        _update_job(job_id, {"progress": 30})
        time.sleep(0.5)
        
        _update_job(job_id, {"progress": 60})
        time.sleep(0.5)
        
        _update_job(job_id, {"progress": 90})
        time.sleep(0.3)
        
        # Generate result based on job type
        result = _generate_result(job_type, job["params"])
        
        _update_job(job_id, {
            "status": JobStatus.DONE,
            "progress": 100,
            "result": result
        })
        
    except Exception as e:
        _update_job(job_id, {
            "status": JobStatus.ERROR,
            "error": str(e)
        })


def _generate_result(job_type: str, params: Dict) -> Dict:
    """
    Generate placeholder results for MVP
    In production, this would call real AI services
    """
    if job_type == "image":
        # Image generation result
        return {
            "imageUrl": "/static/placeholder_image.png",
            "width": 512,
            "height": 512,
            "prompt": params.get("prompt", ""),
            "style": params.get("style", "realistic")
        }
    
    elif job_type == "mesh_v1":
        # Mesh V1 generation result
        return {
            "meshUrl": "/static/placeholder_mesh.glb",
            "format": "glb",
            "triangles": 512,
            "vertices": 280,
            "species": params.get("species", "dog"),
            "tier": "v1"
        }
    
    elif job_type == "mesh_v2":
        # Mesh V2 refinement result
        return {
            "meshUrl": "/static/placeholder_mesh.glb",
            "format": "glb",
            "triangles": 4096,
            "vertices": 2100,
            "smoothness": params.get("refine", {}).get("smoothness", 0.5),
            "tier": "v2"
        }
    
    else:
        raise ValueError(f"Unknown job type: {job_type}")


def cleanup_old_jobs(max_age_hours: int = 24):
    """
    Remove jobs older than max_age_hours
    Call periodically to prevent memory bloat
    """
    now = datetime.utcnow()
    
    with _jobs_lock:
        old_jobs = []
        for job_id, job in _jobs.items():
            try:
                created = datetime.fromisoformat(job["created_at"])
                age_hours = (now - created).total_seconds() / 3600
                if age_hours > max_age_hours:
                    old_jobs.append(job_id)
            except (ValueError, KeyError):
                # Invalid date or missing created_at
                old_jobs.append(job_id)
        
        for job_id in old_jobs:
            del _jobs[job_id]
    
    return len(old_jobs)


def get_all_jobs() -> list:
    """Get all jobs (for debugging/admin)"""
    with _jobs_lock:
        return list(_jobs.values())


def cancel_job(job_id: str) -> bool:
    """
    Cancel a running job
    Returns True if job was cancelled, False if not found or already done
    """
    job = get_job(job_id)
    if not job:
        return False
    
    if job["status"] in [JobStatus.QUEUED, JobStatus.RUNNING]:
        _update_job(job_id, {
            "status": JobStatus.ERROR,
            "error": "Job cancelled by user"
        })
        return True
    
    return False
