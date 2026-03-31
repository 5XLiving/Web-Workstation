from flask import Blueprint, request
from services.core_ctr_service import (
    create_job_service,
    preview_job_service,
    approve_job_service,
    push_job_service,
    get_job_service,
    health_service,
)

core_ctr_bp = Blueprint("core_ctr", __name__, url_prefix="/api/core-ctr/v1")

@core_ctr_bp.route("/jobs/create", methods=["POST"])
def create_job():
    return create_job_service(request)

@core_ctr_bp.route("/jobs/preview", methods=["POST"])
def preview_job():
    return preview_job_service(request)

@core_ctr_bp.route("/jobs/approve", methods=["POST"])
def approve_job():
    return approve_job_service(request)

@core_ctr_bp.route("/jobs/push", methods=["POST"])
def push_job():
    return push_job_service(request)

@core_ctr_bp.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    return get_job_service(job_id)

@core_ctr_bp.route("/health", methods=["GET"])
def health():
    return health_service()