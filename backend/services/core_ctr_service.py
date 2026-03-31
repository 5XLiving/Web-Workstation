from flask import jsonify
from schemas.job_schema import (
    validate_job_payload,
    generate_job_id,
    generate_version_id,
    current_timestamp,
)
from storage.job_store import create_job, get_job, update_job
from services.modular_service import handle_modular_job

SAFE_ERROR = lambda msg, stage: {
    "ok": False,
    "job": None,
    "result": None,
    "error": {
        "message": msg,
        "stage": stage,
        "logs_path": None,
    },
}


def _get_json_object(request):
    try:
        payload = request.get_json(force=True) or {}
    except Exception:
        return None, (jsonify(SAFE_ERROR("Invalid JSON payload", "parse")), 400)

    if not isinstance(payload, dict):
        return None, (jsonify(SAFE_ERROR("JSON body must be an object", "parse")), 400)

    return payload, None


def create_job_service(request):
    payload, error = _get_json_object(request)
    if error:
        return error

    errors = validate_job_payload(payload)
    if errors:
        return jsonify(SAFE_ERROR(", ".join(errors), "validation")), 400

    job = dict(payload)
    job["job_id"] = generate_job_id()
    job["version_id"] = generate_version_id()
    job["timestamp"] = current_timestamp()
    job["status"] = "draft"

    create_job(job)
    return jsonify({"ok": True, "job": job, "result": None, "error": None})


def preview_job_service(request):
    payload, error = _get_json_object(request)
    if error:
        return error

    errors = validate_job_payload(payload)
    if errors:
        return jsonify(SAFE_ERROR(", ".join(errors), "validation")), 400

    job = dict(payload)
    job["job_id"] = generate_job_id()
    job["version_id"] = generate_version_id()
    job["timestamp"] = current_timestamp()
    job["status"] = "draft"

    create_job(job)
    result = handle_modular_job(job)

    update_fields = {"last_result": result}
    if result.get("ok"):
        update_fields["status"] = "completed"
    else:
        update_fields["status"] = "failed"

    update_job(job["job_id"], update_fields)
    job = get_job(job["job_id"])

    return jsonify({"ok": bool(result.get("ok")), "job": job, "result": result, "error": None if result.get("ok") else {
        "message": result.get("summary", "XYZ preview failed."),
        "stage": "preview",
        "logs_path": result.get("logs_path"),
    }}), (200 if result.get("ok") else 400)


def approve_job_service(request):
    payload, error = _get_json_object(request)
    if error:
        return error

    job_id = payload.get("job_id")
    if not job_id:
        return jsonify(SAFE_ERROR("Missing job_id", "approve")), 400

    job = get_job(job_id)
    if not job:
        return jsonify(SAFE_ERROR("Job not found", "approve")), 404

    if job.get("status") not in {"draft", "completed"}:
        return jsonify(SAFE_ERROR("Only draft or preview-completed jobs can be approved", "approve")), 400

    update_job(job_id, {"status": "approved"})
    job = get_job(job_id)
    return jsonify({"ok": True, "job": job, "result": None, "error": None})


def push_job_service(request):
    payload, error = _get_json_object(request)
    if error:
        return error

    job_id = payload.get("job_id")
    if not job_id:
        return jsonify(SAFE_ERROR("Missing job_id", "push")), 400

    job = get_job(job_id)
    if not job:
        return jsonify(SAFE_ERROR("Job not found", "push")), 404

    if job.get("status") != "approved":
        return jsonify(SAFE_ERROR("Only approved jobs can be pushed", "push")), 400

    update_job(job_id, {"status": "queued"})
    update_job(job_id, {"status": "running"})
    job = get_job(job_id)

    result = handle_modular_job(job)

    update_job(job_id, {
        "status": "completed" if result.get("ok") else "failed",
        "last_result": result,
    })
    job = get_job(job_id)

    return jsonify({
        "ok": bool(result.get("ok")),
        "job": job,
        "result": result,
        "error": None if result.get("ok") else {
            "message": result.get("summary", "XYZ push failed."),
            "stage": "push",
            "logs_path": result.get("logs_path"),
        },
    }), (200 if result.get("ok") else 400)


def get_job_service(job_id):
    job = get_job(job_id)
    if not job:
        return jsonify(SAFE_ERROR("Job not found", "get_job")), 404

    result = job.get("last_result")
    return jsonify({"ok": True, "job": job, "result": result, "error": None})


def health_service():
    return jsonify({"ok": True, "service": "Core CTR", "status": "healthy"})