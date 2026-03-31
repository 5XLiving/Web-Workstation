from typing import Any

from schemas.xyz_build_schema import (
    normalize_xyz_build_package,
    validate_xyz_build_package,
)
from services.xyz_path_service import generate_xyz_path_steps, summarize_xyz_path
from services.xyz_geometry_service import build_xyz_geometry_state, build_xyz_preview_payload


def build_xyz_session(job: dict[str, Any]) -> dict[str, Any]:
    """
    Main Phase 1 XYZ builder.
    Converts a Core CTR job into a coordinate-based construction session.
    """

    input_data = job.get("input_data", {}) or {}
    build_package = normalize_xyz_build_package(input_data)
    validation_errors = validate_xyz_build_package(build_package)

    if validation_errors:
        return {
            "ok": False,
            "job_id": job.get("job_id"),
            "module": job.get("module"),
            "summary": "XYZ build package validation failed.",
            "errors": validation_errors,
            "preview": None,
            "logs_path": f"/{job.get('company', '5xLiving')}/{job.get('project', 'Workstation')}/logs/{job.get('job_id', 'unknown-job')}.log",
            "output_path": None,
        }

    steps = generate_xyz_path_steps(build_package)
    path_summary = summarize_xyz_path(steps)
    geometry_state = build_xyz_geometry_state(build_package, steps)
    preview = build_xyz_preview_payload(build_package, steps)

    return {
        "ok": True,
        "job_id": job.get("job_id"),
        "module": job.get("module"),
        "summary": f"XYZ construction session prepared for template '{build_package['template']}'.",
        "build_package": build_package,
        "path_summary": path_summary,
        "steps": steps,
        "geometry_state": geometry_state,
        "preview": preview,
        "logs_path": f"/{job.get('company', '5xLiving')}/{job.get('project', 'Workstation')}/logs/{job.get('job_id', 'unknown-job')}.log",
        "output_path": f"/{job.get('company', '5xLiving')}/{job.get('project', 'Workstation')}/output/{job.get('job_id', 'unknown-job')}.json",
    }