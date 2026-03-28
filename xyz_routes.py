from flask import Blueprint, request, jsonify
from devroom.xyz_service import XYZSpatialService
from pathlib import Path

xyz_bp = Blueprint("xyz_bp", __name__, url_prefix="/admin/devroom/xyz")

# Initialize the service (adjust base_dir as needed)
xyz_service = XYZSpatialService(base_dir=Path("."))

@xyz_bp.route("/plans", methods=["POST"])
def create_plan():
    payload = request.get_json(force=True)
    actor = payload.get("actor", "api_user")
    result = xyz_service.create_plan(payload, actor=actor)
    return jsonify(result)

@xyz_bp.route("/generation-package", methods=["POST"])
def create_generation_package():
    payload = request.get_json(force=True)
    actor = payload.get("actor", "api_user")
    result = xyz_service.create_generation_package(payload, actor=actor)
    return jsonify(result)

@xyz_bp.route("/plans", methods=["GET"])
def list_plans():
    workspace_id = request.args.get("workspaceId")
    limit = int(request.args.get("limit", 100))
    result = xyz_service.list_plans(limit=limit, workspace_id=workspace_id)
    return jsonify(result)

@xyz_bp.route("/plans/<plan_id>", methods=["GET"])
def get_plan(plan_id):
    result = xyz_service.get_plan(plan_id)
    return jsonify(result)

@xyz_bp.route("/previews", methods=["GET"])
def list_previews():
    workspace_id = request.args.get("workspaceId")
    plan_id = request.args.get("planId")
    limit = int(request.args.get("limit", 100))
    result = xyz_service.list_previews(limit=limit, workspace_id=workspace_id, plan_id=plan_id)
    return jsonify(result)

@xyz_bp.route("/previews/<preview_id>", methods=["GET"])
def get_preview(preview_id):
    result = xyz_service.get_preview(preview_id)
    return jsonify(result)

@xyz_bp.route("/jobs", methods=["GET"])
def list_jobs():
    workspace_id = request.args.get("workspaceId")
    plan_id = request.args.get("planId")
    limit = int(request.args.get("limit", 100))
    result = xyz_service.list_jobs(limit=limit, workspace_id=workspace_id, plan_id=plan_id)
    return jsonify(result)

@xyz_bp.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    result = xyz_service.get_job(job_id)
    return jsonify(result)

@xyz_bp.route("/jobs/<job_id>/status", methods=["POST"])
def update_job_status(job_id):
    payload = request.get_json(force=True)
    actor = payload.get("actor", "api_user")
    # For now, just return the job info (stub for real status update logic)
    result = xyz_service.get_job(job_id)
    result["updatedBy"] = actor
    result["message"] = f"Status update endpoint called for job {job_id} by {actor}."
    return jsonify(result)

@xyz_bp.route("/history", methods=["GET"])
def get_history():
    workspace_id = request.args.get("workspaceId")
    limit = int(request.args.get("limit", 100))
    result = xyz_service.history(limit=limit, workspace_id=workspace_id)
    return jsonify(result)
