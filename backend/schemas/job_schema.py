from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

REQUIRED_FIELDS = [
    "company",
    "project",
    "module",
    "action",
    "input_data",
    "requested_by",
]

ALLOWED_STATUS = {
    "draft",
    "approved",
    "queued",
    "running",
    "completed",
    "failed",
    "archived",
}

ALLOWED_ACTIONS = {
    "create",
    "preview",
    "approve",
    "push",
}

ALLOWED_COMPANIES = {
    "5xLiving",
}

ALLOWED_PROJECTS = {
    "Workstation",
    "XYZ",
    "3DModelMaker",
}

ALLOWED_MODULES = {
    "3DModelMaker",
    "XYZ Modular",
    "Dev Room",
    "Admin Shell",
}

DEFAULTS = {
    "company": "5xLiving",
    "project": "Workstation",
    "module": "3DModelMaker",
    "status": "draft",
}


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def validate_job_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(payload, dict):
        return ["Payload must be an object"]

    for field in REQUIRED_FIELDS:
        if field not in payload:
            errors.append(f"Missing required field: {field}")

    company = payload.get("company")
    if not _is_non_empty_string(company):
        errors.append("company must be a non-empty string")
    elif company not in ALLOWED_COMPANIES:
        errors.append(f"Invalid company: {company}")

    project = payload.get("project")
    if not _is_non_empty_string(project):
        errors.append("project must be a non-empty string")
    elif project not in ALLOWED_PROJECTS:
        errors.append(f"Invalid project: {project}")

    module = payload.get("module")
    if not _is_non_empty_string(module):
        errors.append("module must be a non-empty string")
    elif module not in ALLOWED_MODULES:
        errors.append(f"Invalid module: {module}")

    action = payload.get("action")
    if not _is_non_empty_string(action):
        errors.append("action must be a non-empty string")
    elif action not in ALLOWED_ACTIONS:
        errors.append(f"Invalid action: {action}")

    status = payload.get("status", DEFAULTS["status"])
    if not _is_non_empty_string(status):
        errors.append("status must be a non-empty string")
    elif status not in ALLOWED_STATUS:
        errors.append(f"Invalid status: {status}")

    if "input_data" in payload and not isinstance(payload.get("input_data"), dict):
        errors.append("input_data must be an object")

    requested_by = payload.get("requested_by")
    if not _is_non_empty_string(requested_by):
        errors.append("requested_by cannot be empty")

    return errors


def generate_job_id() -> str:
    return f"job_{_utc_now().strftime('%Y%m%d%H%M%S%f')}"


def generate_version_id() -> str:
    return f"v{_utc_now().strftime('%Y.%m.%d.%H%M%S')}"


def current_timestamp() -> str:
    return _utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")
