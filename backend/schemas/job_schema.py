import datetime

REQUIRED_FIELDS = [
    "company", "project", "module", "action", "input_data", "requested_by"
]
ALLOWED_STATUS = [
    "draft", "approved", "queued", "running", "completed", "failed", "archived"
]
ALLOWED_ACTIONS = [
    "create", "preview", "approve", "push"
]

DEFAULTS = {
    "company": "5xLiving",
    "project": "Workstation",
    "module": "3DModelMaker"
}


def validate_job_payload(payload):
    errors = []

    if not isinstance(payload, dict):
        return ["Payload must be an object"]

    for field in REQUIRED_FIELDS:
        if field not in payload:
            errors.append(f"Missing required field: {field}")

    if payload.get("company") != DEFAULTS["company"]:
        errors.append("Invalid company")

    if payload.get("project") != DEFAULTS["project"]:
        errors.append("Invalid project")

    if payload.get("module") != DEFAULTS["module"]:
        errors.append("Invalid module")

    if payload.get("action") not in ALLOWED_ACTIONS:
        errors.append("Invalid action")

    status = payload.get("status", "draft")
    if status not in ALLOWED_STATUS:
        errors.append("Invalid status")

    if "input_data" in payload and not isinstance(payload.get("input_data"), dict):
        errors.append("input_data must be an object")

    if "requested_by" in payload and not str(payload.get("requested_by", "")).strip():
        errors.append("requested_by cannot be empty")

    return errors

def generate_job_id():
    return f"job_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"


def generate_version_id():
    return f"v{datetime.datetime.utcnow().strftime('%Y.%m.%d.%H%M%S')}"


def current_timestamp():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
