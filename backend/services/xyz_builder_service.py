from typing import Any

from schemas.xyz_build_schema import (
    normalize_xyz_build_package,
    validate_xyz_build_package,
)
from services.xyz_path_service import generate_xyz_path_steps, summarize_xyz_path
from services.xyz_geometry_preview import (
    build_xyz_geometry_state,
    build_xyz_preview_payload,
)


def build_xyz_session(job: dict[str, Any]) -> dict[str, Any]:
    """
    Main Phase 1 XYZ builder.
    Converts a Core CTR job into a coordinate-based construction session.
    """

    job_id = job.get("job_id", "unknown-job")
    module = job.get("module")
    company = job.get("company", "5xLiving")
    project = job.get("project", "Workstation")

    input_data = job.get("input_data", {}) or {}
    build_package = normalize_xyz_build_package(input_data)
    validation_errors = validate_xyz_build_package(build_package)

    logs_path = f"/{company}/{project}/logs/{job_id}.log"
    output_path = f"/{company}/{project}/output/{job_id}.json"

    if validation_errors:
        return {
            "ok": False,
            "job_id": job_id,
            "module": module,
            "summary": "XYZ build package validation failed.",
            "errors": validation_errors,
            "preview": None,
            "logs_path": logs_path,
            "output_path": None,
        }

    steps = generate_xyz_path_steps(build_package)
    path_summary = summarize_xyz_path(steps)
    geometry_state = build_xyz_geometry_state(build_package, steps)
    preview = build_xyz_preview_payload(build_package, steps)

    return {
        "ok": True,
        "job_id": job_id,
        "module": module,
        "summary": f"XYZ construction session prepared for template '{build_package['template']}'.",
        "build_package": build_package,
        "path_summary": path_summary,
        "steps": steps,
        "geometry_state": geometry_state,
        "preview": preview,
        "logs_path": logs_path,
        "output_path": output_path,
    }
