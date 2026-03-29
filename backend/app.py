
# --- Startup Imports and Path Setup ---
import sys
from pathlib import Path
import json
import os
import re
from datetime import datetime, timezone
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# --- App Creation ---
app = Flask(__name__, static_folder="static")

# --- Blueprint Registration ---
from xyz_routes import xyz_bp
app.register_blueprint(xyz_bp)

# --- Core Routes ---
@app.route("/")
def root():
    return jsonify({"ok": True, "message": "Workstation backend root"}), 200

@app.route("/health")
def health():
    return jsonify({"ok": True, "message": "Workstation backend healthy"}), 200

@app.route("/3d_model_maker")
def serve_3d_model_maker():
    return send_from_directory("../", "3d_model_maker.html")

@app.route("/xyz_spatial")
def serve_xyz_spatial():
    return send_from_directory("archive", "3d_model_maker_plugin_host.html")

@app.route("/static/images/<path:filename>")
def serve_static_images(filename):
    return send_from_directory("static/images", filename)

CORS(app)

# --- (Keep all other business logic, routes, and helpers as is, attached to this app object) ---

# ...existing business logic, API routes, and helpers...

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
# Add repo root to sys.path for xyz_routes import
REPO_ROOT = BASE_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from xyz_routes import xyz_bp

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent

# Simple .env loader
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

SHARED_WORKER_URL = os.environ.get("FIVEXLIVING_SHARED_WORKER_URL", "").strip()
SHARED_WORKER_TIMEOUT_SECONDS = int(
    os.environ.get("FIVEXLIVING_SHARED_WORKER_TIMEOUT_SECONDS", "45")
)
FALLBACK_MINI_AI_URL = os.environ.get("FIVEXLIVING_FALLBACK_MINI_AI_URL", "").strip()
FALLBACK_MINI_AI_TIMEOUT_SECONDS = int(
    os.environ.get("FIVEXLIVING_FALLBACK_MINI_AI_TIMEOUT_SECONDS", "20")
)

app = Flask(__name__, static_folder="static")
app.register_blueprint(xyz_bp)

@app.post("/api/core_ctr/action")
def api_core_ctr_action():
    payload = request.get_json(silent=True) or {}
    # Placeholder: Accepts any action and returns a mock response
    return jsonify({
        "ok": True,
        "action": payload.get("action", "unknown"),
        "result": {"summary": "CoreCtr action accepted (mock)."},
        "payload": payload
    }), 200

@app.post("/api/modular/pointer_commit")
def api_modular_pointer_commit():
    payload = request.get_json(silent=True) or {}
    # Placeholder: Accepts any pointer commit and returns a mock response
    return jsonify({
        "ok": True,
        "result": {"summary": "Pointer commit accepted (mock)."},
        "payload": payload
    }), 200
@app.route("/3d_model_maker")
def serve_3d_model_maker():
    return send_from_directory("../", "3d_model_maker.html")

@app.route("/xyz_spatial")
def serve_xyz_spatial():
    return send_from_directory("archive", "3d_model_maker_plugin_host.html")

@app.route("/static/images/<path:filename>")
def serve_static_images(filename):
    return send_from_directory("static/images", filename)
CORS(app)

EXPORT_TYPE_DIRECTORIES = {
    "preview-image": ("previews", ".png"),
    "report-pdf": ("reports", ".pdf"),
    "build-package": ("packages", ".json"),
    "3d-placeholder": ("3d", ".glb"),
}

ASSET_TYPES = (
    "mesh",
    "texture",
    "image",
    "material-preset",
    "prefab-template",
    "document",
    "print-file",
)

ASSET_VISIBILITY_TYPES = (
    "free-demo",
    "project-only",
    "private",
    "licensed-premium",
)

ASSET_STORAGE_TYPES = (
    "local",
    "cloud",
    "private-controlled",
)

ASSET_SOURCE_TYPES = (
    "upload",
    "internal-demo",
    "generated",
    "imported",
    "licensed",
)

ASSET_OWNER_TYPES = (
    "company",
    "project",
    "client",
    "vendor",
    "user",
)

ASSET_STATUS_TYPES = (
    "draft",
    "active",
    "archived",
    "blocked",
)

ASSET_LICENSE_TYPES = (
    "internal",
    "owned",
    "third-party",
    "cc0",
    "custom",
    "unknown",
)

CODEBOOK_TYPES = (
    "master",
    "client-safe",
)

CODEBOOK_STATUS_TYPES = (
    "draft",
    "active",
    "archived",
)

CODEBOOK_SOURCE_KINDS = (
    "mock",
    "derived",
)

UNITY_BUILD_TYPES = (
    "create_terrain",
    "place_bases",
    "spawn_pawsona",
    "prepare_test_scene",
)

CODEBOOK_REGISTRY = [
    {
        "codebookId": "cb-vrws-master-001",
        "company": "5xLiving",
        "project": "VR Workstation",
        "codebookScopeKey": "5xLiving::VR Workstation",
        "codebookType": "master",
        "displayName": "VR Workstation Master Codebook",
        "versionId": "v2026.03.13-001",
        "status": "active",
        "sourceKind": "mock",
        "visibility": "project-only",
        "ownerType": "company",
        "storageType": "local",
        "storagePath": "/5xLiving/VR Workstation/codebook/master.codebook.md",
        "derivedFromCodebookId": None,
        "roomLoadRules": {
            "dev-room": "master",
            "client-room": "filtered-master",
            "review-room": "master",
            "settings-room": "master",
        },
        "content": {
            "summary": "Internal source of truth for VR Workstation orchestration and room loading.",
            "sections": [
                {
                    "key": "identity",
                    "title": "Project Identity",
                    "body": "VR Workstation is the internal control hub for 5xLiving project orchestration.",
                },
                {
                    "key": "routing",
                    "title": "Room Routing",
                    "body": "Dev Room, Review Room, and Settings Room read the project master codebook.",
                },
            ],
        },
        "createdAt": "2026-03-13T12:00:00Z",
        "updatedAt": "2026-03-13T12:00:00Z",
    },
    {
        "codebookId": "cb-petpaws-master-001",
        "company": "5xLiving",
        "project": "PetPaws",
        "codebookScopeKey": "5xLiving::PetPaws",
        "codebookType": "master",
        "displayName": "PetPaws Master Codebook",
        "versionId": "v2026.03.13-001",
        "status": "active",
        "sourceKind": "mock",
        "visibility": "private",
        "ownerType": "project",
        "storageType": "local",
        "storagePath": "/5xLiving/PetPaws/codebook/master.codebook.md",
        "derivedFromCodebookId": None,
        "roomLoadRules": {
            "dev-room": "master",
            "client-room": "client-safe",
            "review-room": "master",
            "settings-room": "master",
        },
        "content": {
            "summary": "Internal master codebook for PetPaws prototype pipeline and approval-gated flow.",
            "sections": [
                {
                    "key": "workflow",
                    "title": "Workstation Relation",
                    "body": "PetPaws uses the internal workstation flow: preview, review, approve, and later Unity push.",
                }
            ],
        },
        "createdAt": "2026-03-13T12:05:00Z",
        "updatedAt": "2026-03-13T12:05:00Z",
    },
    {
        "codebookId": "cb-petpaws-client-001",
        "company": "5xLiving",
        "project": "PetPaws",
        "codebookScopeKey": "5xLiving::PetPaws",
        "codebookType": "client-safe",
        "displayName": "PetPaws Client-Safe Codebook",
        "versionId": "v2026.03.13-001",
        "status": "active",
        "sourceKind": "derived",
        "visibility": "project-only",
        "ownerType": "project",
        "storageType": "local",
        "storagePath": "/5xLiving/PetPaws/codebook/client-safe.codebook.md",
        "derivedFromCodebookId": "cb-petpaws-master-001",
        "roomLoadRules": {
            "dev-room": "master",
            "client-room": "client-safe",
            "review-room": "master",
            "settings-room": "master",
        },
        "content": {
            "summary": "Client-safe derived codebook with internal-only controls removed.",
            "sections": [
                {
                    "key": "safe-overview",
                    "title": "Project Overview",
                    "body": "PetPaws is a cute but deep MMO, city, warfare, and racing project under 5xLiving.",
                }
            ],
        },
        "createdAt": "2026-03-13T12:06:00Z",
        "updatedAt": "2026-03-13T12:06:00Z",
    },
    {
        "codebookId": "cb-astro-master-001",
        "company": "5xLiving",
        "project": "Astro Sanctuary",
        "codebookScopeKey": "5xLiving::Astro Sanctuary",
        "codebookType": "master",
        "displayName": "Astro Sanctuary Master Codebook",
        "versionId": "v2026.03.13-001",
        "status": "active",
        "sourceKind": "mock",
        "visibility": "private",
        "ownerType": "company",
        "storageType": "cloud",
        "storagePath": "/5xLiving/Astro Sanctuary/codebook/master.codebook.md",
        "derivedFromCodebookId": None,
        "roomLoadRules": {
            "dev-room": "master",
            "client-room": "filtered-master",
            "review-room": "master",
            "settings-room": "master",
        },
        "content": {
            "summary": "Internal master codebook for Astro Sanctuary planning and room behavior.",
            "sections": [
                {
                    "key": "identity",
                    "title": "Project Identity",
                    "body": "Astro Sanctuary is managed as a 5xLiving project with project-level codebook ownership.",
                }
            ],
        },
        "createdAt": "2026-03-13T12:10:00Z",
        "updatedAt": "2026-03-13T12:10:00Z",
    },
]

ASSET_REGISTRY = [
    {
        "assetId": "asset-vrws-mesh-001",
        "displayName": "Workstation Shell Mesh",
        "company": "5xLiving",
        "project": "VR Workstation",
        "module": "workstation-shell",
        "projectScopeKey": "5xLiving::VR Workstation::workstation-shell",
        "assetType": "mesh",
        "visibility": "project-only",
        "storageType": "local",
        "sourceType": "generated",
        "ownerType": "company",
        "filePath": "/5xLiving/VR Workstation/assets/meshes/workstation-shell.glb",
        "previewPath": "/5xLiving/VR Workstation/output/previews/workstation-shell.png",
        "tags": ["workstation", "shell", "internal"],
        "reusable": True,
        "status": "active",
        "createdAt": "2026-03-13T08:10:00Z",
        "updatedAt": "2026-03-13T08:10:00Z",
        "licenseInfo": {
            "type": "internal",
            "redistributable": False,
            "notes": "Internal 5xLiving use only.",
        },
    },
    {
        "assetId": "asset-petpaws-doc-001",
        "displayName": "Pawsona Prototype Brief",
        "company": "5xLiving",
        "project": "PetPaws",
        "module": "review-room",
        "projectScopeKey": "5xLiving::PetPaws::review-room",
        "assetType": "document",
        "visibility": "private",
        "storageType": "local",
        "sourceType": "upload",
        "ownerType": "project",
        "filePath": "/5xLiving/PetPaws/data/design/pawsona-prototype-brief.pdf",
        "previewPath": "/5xLiving/PetPaws/output/previews/pawsona-prototype-brief.png",
        "tags": ["petpaws", "prototype", "brief"],
        "reusable": False,
        "status": "draft",
        "createdAt": "2026-03-13T09:00:00Z",
        "updatedAt": "2026-03-13T09:00:00Z",
        "licenseInfo": {
            "type": "internal",
            "redistributable": False,
            "notes": "Internal project brief for prototype planning.",
        },
    },
    {
        "assetId": "asset-astro-texture-003",
        "displayName": "Nebula Surface 03",
        "company": "5xLiving",
        "project": "Astro Sanctuary",
        "module": "environment",
        "projectScopeKey": "5xLiving::Astro Sanctuary::environment",
        "assetType": "texture",
        "visibility": "licensed-premium",
        "storageType": "cloud",
        "sourceType": "licensed",
        "ownerType": "vendor",
        "filePath": "/5xLiving/Astro Sanctuary/assets/textures/nebula-surface-03.png",
        "previewPath": "/5xLiving/Astro Sanctuary/output/previews/nebula-surface-03.png",
        "tags": ["astro", "texture", "premium"],
        "reusable": False,
        "status": "active",
        "createdAt": "2026-03-12T18:45:00Z",
        "updatedAt": "2026-03-12T18:45:00Z",
        "licenseInfo": {
            "type": "third-party",
            "redistributable": False,
            "notes": "Licensed premium texture for internal prototype use.",
        },
    },
]


def _parse_response_body(response):
    raw_text = response.text
    try:
        return raw_text, response.json()
    except ValueError:
        return raw_text, {"raw": raw_text}


def _post_json(url, payload, timeout_seconds):
    try:
        response = requests.post(url, json=payload, timeout=timeout_seconds)
    except requests.Timeout as exc:
        return {
            "ok": False,
            "status": 504,
            "body": {"error": "timeout", "details": str(exc)},
            "url": url,
            "failureKind": "timeout",
        }
    except requests.RequestException as exc:
        return {
            "ok": False,
            "status": 502,
            "body": {"error": "upstream unavailable", "details": str(exc)},
            "url": url,
            "failureKind": "upstream-unavailable",
        }

    _, body = _parse_response_body(response)
    return {
        "ok": response.ok,
        "status": response.status_code,
        "body": body,
        "url": url,
        "failureKind": None,
    }


def _should_use_fallback(primary_result):
    if primary_result["status"] == 429:
        return True

    if primary_result["failureKind"] in {"timeout", "upstream-unavailable"}:
        return True

    if primary_result["status"] in {502, 503, 504}:
        return True

    body_text = json.dumps(primary_result.get("body") or {}, ensure_ascii=False).lower()
    fallback_markers = (
        "insufficient_quota",
        "timeout",
        "upstream unavailable",
    )
    return any(marker in body_text for marker in fallback_markers)


def _success_response(mode, message, worker_payload, upstream_result):
    return jsonify(
        {
            "ok": True,
            "company": worker_payload["company"],
            "project": worker_payload["project"],
            "module": worker_payload["module"],
            "message": message,
            "mode": mode,
            "workerUrl": upstream_result["url"],
            "upstream": upstream_result["body"],
        }
    ), 200


def _error_response(error_message, status_code, worker_payload, upstream_result):
    return jsonify(
        {
            "ok": False,
            "error": error_message,
            "status": status_code,
            "workerUrl": upstream_result["url"],
            "payload": worker_payload,
            "upstream": upstream_result["body"],
        }
    ), status_code


def _slugify_scope_part(value):
    text = re.sub(r"[^a-z0-9]+", "-", str(value).strip().lower())
    return text.strip("-") or "unknown"


def _utc_timestamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _derive_project_scope_key(company, project, module):
    return f"{str(company).strip()}::{str(project).strip()}::{str(module).strip()}"


def _derive_codebook_scope_key(company, project):
    return f"{str(company).strip()}::{str(project).strip()}"


def _normalize_tags(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return []


def _validate_license_info(value):
    license_info = value if isinstance(value, dict) else {}
    license_type = str(license_info.get("type", "")).strip()
    notes = str(license_info.get("notes", "")).strip()
    redistributable = license_info.get("redistributable")

    if license_type not in ASSET_LICENSE_TYPES:
        supported_types = ", ".join(ASSET_LICENSE_TYPES)
        return False, f"licenseInfo.type must be one of: {supported_types}"

    if not isinstance(redistributable, bool):
        return False, "licenseInfo.redistributable must be a boolean"

    if not notes:
        return False, "licenseInfo.notes is required"

    return True, ""


def _validate_asset_payload(payload):
    required_fields = (
        "assetId",
        "displayName",
        "company",
        "project",
        "module",
        "assetType",
        "visibility",
        "storageType",
        "sourceType",
        "ownerType",
        "filePath",
        "previewPath",
        "reusable",
        "status",
        "createdAt",
        "updatedAt",
        "licenseInfo",
    )

    missing_fields = [
        field
        for field in required_fields
        if payload.get(field) is None or (isinstance(payload.get(field), str) and not str(payload.get(field, "")).strip())
    ]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    if str(payload.get("assetType", "")).strip() not in ASSET_TYPES:
        return False, f"assetType must be one of: {', '.join(ASSET_TYPES)}"

    if str(payload.get("visibility", "")).strip() not in ASSET_VISIBILITY_TYPES:
        return False, f"visibility must be one of: {', '.join(ASSET_VISIBILITY_TYPES)}"

    if str(payload.get("storageType", "")).strip() not in ASSET_STORAGE_TYPES:
        return False, f"storageType must be one of: {', '.join(ASSET_STORAGE_TYPES)}"

    if str(payload.get("sourceType", "")).strip() not in ASSET_SOURCE_TYPES:
        return False, f"sourceType must be one of: {', '.join(ASSET_SOURCE_TYPES)}"

    if str(payload.get("ownerType", "")).strip() not in ASSET_OWNER_TYPES:
        return False, f"ownerType must be one of: {', '.join(ASSET_OWNER_TYPES)}"

    if str(payload.get("status", "")).strip() not in ASSET_STATUS_TYPES:
        return False, f"status must be one of: {', '.join(ASSET_STATUS_TYPES)}"

    if not isinstance(payload.get("reusable"), bool):
        return False, "reusable must be a boolean"

    is_valid_license, license_message = _validate_license_info(payload.get("licenseInfo"))
    if not is_valid_license:
        return False, license_message

    return True, ""


def _serialize_asset_record(asset):
    record = dict(asset)
    record["tags"] = _normalize_tags(record.get("tags", []))
    record["projectScopeKey"] = _derive_project_scope_key(
        record.get("company", ""),
        record.get("project", ""),
        record.get("module", ""),
    )
    return record


def _asset_type_metadata():
    return {
        "assetTypes": list(ASSET_TYPES),
        "visibilityTypes": list(ASSET_VISIBILITY_TYPES),
        "storageTypes": list(ASSET_STORAGE_TYPES),
        "sourceTypes": list(ASSET_SOURCE_TYPES),
        "ownerTypes": list(ASSET_OWNER_TYPES),
        "statusTypes": list(ASSET_STATUS_TYPES),
        "licenseTypes": list(ASSET_LICENSE_TYPES),
    }


def _validate_codebook_payload(payload):
    required_fields = (
        "codebookId",
        "company",
        "project",
        "codebookType",
        "displayName",
        "versionId",
        "status",
        "sourceKind",
        "visibility",
        "ownerType",
        "storageType",
        "storagePath",
        "roomLoadRules",
        "content",
        "createdAt",
        "updatedAt",
    )

    missing_fields = [
        field
        for field in required_fields
        if payload.get(field) is None or (isinstance(payload.get(field), str) and not str(payload.get(field, "")).strip())
    ]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    codebook_type = str(payload.get("codebookType", "")).strip()
    if codebook_type not in CODEBOOK_TYPES:
        return False, f"codebookType must be one of: {', '.join(CODEBOOK_TYPES)}"

    if str(payload.get("status", "")).strip() not in CODEBOOK_STATUS_TYPES:
        return False, f"status must be one of: {', '.join(CODEBOOK_STATUS_TYPES)}"

    if str(payload.get("sourceKind", "")).strip() not in CODEBOOK_SOURCE_KINDS:
        return False, f"sourceKind must be one of: {', '.join(CODEBOOK_SOURCE_KINDS)}"

    if str(payload.get("visibility", "")).strip() not in ASSET_VISIBILITY_TYPES:
        return False, f"visibility must be one of: {', '.join(ASSET_VISIBILITY_TYPES)}"

    if str(payload.get("ownerType", "")).strip() not in ASSET_OWNER_TYPES:
        return False, f"ownerType must be one of: {', '.join(ASSET_OWNER_TYPES)}"

    if str(payload.get("storageType", "")).strip() not in ASSET_STORAGE_TYPES:
        return False, f"storageType must be one of: {', '.join(ASSET_STORAGE_TYPES)}"

    room_load_rules = payload.get("roomLoadRules")
    if not isinstance(room_load_rules, dict):
        return False, "roomLoadRules must be an object"

    required_room_rules = ("dev-room", "client-room", "review-room", "settings-room")
    missing_room_rules = [room for room in required_room_rules if not str(room_load_rules.get(room, "")).strip()]
    if missing_room_rules:
        return False, f"roomLoadRules missing entries for: {', '.join(missing_room_rules)}"

    content = payload.get("content")
    if not isinstance(content, dict):
        return False, "content must be an object"

    if not str(content.get("summary", "")).strip():
        return False, "content.summary is required"

    sections = content.get("sections")
    if not isinstance(sections, list):
        return False, "content.sections must be an array"

    for section in sections:
        if not isinstance(section, dict):
            return False, "Each content section must be an object"
        if not str(section.get("key", "")).strip() or not str(section.get("title", "")).strip() or not str(section.get("body", "")).strip():
            return False, "Each content section requires key, title, and body"

    derived_from_codebook_id = payload.get("derivedFromCodebookId")
    if codebook_type == "client-safe" and not str(derived_from_codebook_id or "").strip():
        return False, "client-safe codebooks require derivedFromCodebookId"

    return True, ""


def _serialize_codebook_record(codebook):
    record = dict(codebook)
    record["codebookScopeKey"] = _derive_codebook_scope_key(
        record.get("company", ""),
        record.get("project", ""),
    )
    return record


def _room_target_codebook_type(room):
    normalized_room = str(room or "").strip().lower()
    if normalized_room == "client-room":
        return "client-safe"
    return "master"


def _resolve_current_codebook(company, project, room):
    scope_key = _derive_codebook_scope_key(company, project)
    records = [
        _serialize_codebook_record(codebook)
        for codebook in CODEBOOK_REGISTRY
        if _serialize_codebook_record(codebook)["codebookScopeKey"] == scope_key
    ]
    if not records:
        return None

    requested_type = _room_target_codebook_type(room)
    preferred = next(
        (record for record in records if record["codebookType"] == requested_type and record["status"] == "active"),
        None,
    )
    if preferred:
        return preferred

    master = next(
        (record for record in records if record["codebookType"] == "master" and record["status"] == "active"),
        None,
    )
    if master and requested_type == "client-safe":
        fallback = dict(master)
        fallback["sourceKind"] = "derived"
        fallback["message"] = "Client-safe codebook unavailable; using filtered-master fallback."
        return fallback

    return master


def _validate_unity_push_request(payload):
    required_fields = (
        "company",
        "project",
        "module",
        "buildType",
        "sceneTemplate",
        "versionId",
        "approvedBy",
        "timestamp",
        "payload",
    )

    missing_fields = [
        field
        for field in required_fields
        if payload.get(field) is None
        or (isinstance(payload.get(field), str) and not str(payload.get(field, "")).strip())
    ]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    build_type = str(payload.get("buildType", "")).strip()
    if build_type not in UNITY_BUILD_TYPES:
        return False, f"buildType must be one of: {', '.join(UNITY_BUILD_TYPES)}"

    if not isinstance(payload.get("payload"), dict):
        return False, "payload must be an object"

    return True, ""


def _build_unity_push_result(payload):
    company = str(payload.get("company", "")).strip()
    project = str(payload.get("project", "")).strip()
    module = str(payload.get("module", "")).strip()
    build_type = str(payload.get("buildType", "")).strip()
    scene_template = str(payload.get("sceneTemplate", "")).strip()
    version_id = str(payload.get("versionId", "")).strip()
    timestamp = str(payload.get("timestamp", "")).strip()
    project_scope_key = _derive_project_scope_key(company, project, module)

    job_id = (
        f"job-{_slugify_scope_part(timestamp)}-"
        f"{_slugify_scope_part(company)}-"
        f"{_slugify_scope_part(project)}-"
        f"{_slugify_scope_part(build_type)}"
    )
    output_path = (
        f"/{company}/{project}/output/packages/"
        f"unity-{_slugify_scope_part(version_id)}-{_slugify_scope_part(build_type)}.json"
    )
    logs_path = f"/{company}/{project}/logs/{job_id}.log"
    unity_target = (
        f"mock-unity-target::{project_scope_key}::"
        f"{scene_template or 'default-scene-template'}"
    )

    return {
        "ok": True,
        "jobId": job_id,
        "versionId": version_id,
        "buildType": build_type,
        "sceneTemplate": scene_template,
        "unityTarget": unity_target,
        "outputPath": output_path,
        "logsPath": logs_path,
        "jobState": "queued",
        "message": "Mock Unity bridge package queued.",
    }


def _validate_export_request(payload):
    required_fields = (
        "company",
        "project",
        "module",
        "exportType",
        "versionId",
        "requestedBy",
        "timestamp",
    )

    missing_fields = [
        field for field in required_fields if not str(payload.get(field, "")).strip()
    ]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    if not str(payload.get("assetId", "")).strip() and not str(
        payload.get("outputId", "")
    ).strip():
        return False, "At least one of assetId or outputId is required"

    export_type = str(payload.get("exportType", "")).strip()
    if export_type not in EXPORT_TYPE_DIRECTORIES:
        supported_types = ", ".join(EXPORT_TYPE_DIRECTORIES.keys())
        return False, f"Unsupported exportType. Supported values: {supported_types}"

    return True, ""


def _build_export_result(payload):
    company = str(payload["company"]).strip()
    project = str(payload["project"]).strip()
    export_type = str(payload["exportType"]).strip()
    version_id = str(payload["versionId"]).strip()
    timestamp = str(payload["timestamp"]).strip()
    scope_token = payload.get("outputId") or payload.get("assetId") or "item"

    company_slug = _slugify_scope_part(company)
    project_slug = _slugify_scope_part(project)
    export_slug = _slugify_scope_part(export_type)
    version_slug = _slugify_scope_part(version_id)
    time_slug = _slugify_scope_part(timestamp)
    scope_slug = _slugify_scope_part(scope_token)

    job_id = (
        f"job-{time_slug}-{company_slug}-{project_slug}-{export_slug}-{scope_slug}"
    )
    output_folder, file_extension = EXPORT_TYPE_DIRECTORIES[export_type]
    output_path = (
        f"/{company}/{project}/output/{output_folder}/"
        f"{version_slug}-{scope_slug}{file_extension}"
    )
    logs_path = f"/{company}/{project}/logs/{job_id}.log"

    return {
        "ok": True,
        "jobId": job_id,
        "versionId": version_id,
        "exportType": export_type,
        "outputPath": output_path,
        "logsPath": logs_path,
        "message": f"Mock {export_type} export prepared.",
    }

@app.get("/api/dev/status")
def api_dev_status():
    return jsonify(
        {
            "ok": True,
            "worker": "shared-5xliving-worker",
            "configured": bool(SHARED_WORKER_URL),
            "workerUrl": SHARED_WORKER_URL,
        }
    ), 200


@app.post("/api/dev/command")
def api_dev_command():
    payload = request.get_json(silent=True) or {}

    company = str(payload.get("company", "")).strip()
    project = str(payload.get("project", "")).strip()
    module = str(payload.get("module", "")).strip()
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"ok": False, "error": "Missing message"}), 400

    if not SHARED_WORKER_URL:
        return jsonify(
            {
                "ok": False,
                "error": "Shared worker URL is not configured",
                "envVar": "FIVEXLIVING_SHARED_WORKER_URL",
            }
        ), 503

    worker_url = SHARED_WORKER_URL.rstrip("/") + "/api/chat"

    worker_payload = {
        "prompt": message,
        "company": company or "5xLiving",
        "project": project or "VR Workstation",
        "module": module or "devroom",
    }

    primary_result = _post_json(
        worker_url,
        worker_payload,
        SHARED_WORKER_TIMEOUT_SECONDS,
    )

    if primary_result["ok"]:
        return _success_response(
            "primary-shared-worker",
            message,
            worker_payload,
            primary_result,
        )

    if not _should_use_fallback(primary_result):
        return _error_response(
            "Shared worker returned error",
            primary_result["status"],
            worker_payload,
            primary_result,
        )

    if not FALLBACK_MINI_AI_URL:
        return jsonify(
            {
                "ok": False,
                "error": "Fallback mini AI URL is not configured",
                "status": 503,
                "envVar": "FIVEXLIVING_FALLBACK_MINI_AI_URL",
                "payload": worker_payload,
                "upstream": primary_result["body"],
            }
        ), 503

    fallback_result = _post_json(
        FALLBACK_MINI_AI_URL,
        worker_payload,
        FALLBACK_MINI_AI_TIMEOUT_SECONDS,
    )

    if fallback_result["ok"]:
        return _success_response(
            "fallback-mini-ai",
            message,
            worker_payload,
            fallback_result,
        )

    return _error_response(
        "Fallback mini AI returned error",
        fallback_result["status"],
        worker_payload,
        fallback_result,
    )


@app.get("/api/export/types")
def api_export_types():
    return jsonify(
        {
            "ok": True,
            "types": list(EXPORT_TYPE_DIRECTORIES.keys()),
        }
    ), 200


@app.post("/api/export/request")
def api_export_request():
    payload = request.get_json(silent=True) or {}
    is_valid, validation_message = _validate_export_request(payload)

    if not is_valid:
        export_type = str(payload.get("exportType", "")).strip()
        version_id = str(payload.get("versionId", "")).strip()
        company = str(payload.get("company", "")).strip()
        project = str(payload.get("project", "")).strip()
        job_id = (
            f"job-{_slugify_scope_part(payload.get('timestamp', 'pending'))}-"
            f"{_slugify_scope_part(company)}-"
            f"{_slugify_scope_part(project)}-"
            f"{_slugify_scope_part(export_type or 'unknown')}"
        )
        logs_path = f"/{company or 'company'}/{project or 'project'}/logs/{job_id}.log"
        return jsonify(
            {
                "ok": False,
                "jobId": job_id,
                "versionId": version_id,
                "exportType": export_type,
                "outputPath": "",
                "logsPath": logs_path,
                "message": validation_message,
            }
        ), 400

    return jsonify(_build_export_result(payload)), 200


@app.get("/api/assets/types")
def api_asset_types():
    return jsonify({"ok": True, **_asset_type_metadata()}), 200


@app.get("/api/assets")
def api_assets():
    company = str(request.args.get("company", "")).strip()
    project = str(request.args.get("project", "")).strip()
    module = str(request.args.get("module", "")).strip()
    derived_scope_key = ""

    if company and project and module:
        derived_scope_key = _derive_project_scope_key(company, project, module)

    assets = [_serialize_asset_record(asset) for asset in ASSET_REGISTRY]

    if derived_scope_key:
        assets = [asset for asset in assets if asset["projectScopeKey"] == derived_scope_key]
    else:
        if company:
            assets = [asset for asset in assets if asset["company"] == company]
        if project:
            assets = [asset for asset in assets if asset["project"] == project]
        if module:
            assets = [asset for asset in assets if asset["module"] == module]

    return jsonify(
        {
            "ok": True,
            "count": len(assets),
            "items": assets,
        }
    ), 200


@app.post("/api/assets/register")
def api_asset_register():
    payload = request.get_json(silent=True) or {}
    is_valid, validation_message = _validate_asset_payload(payload)

    if not is_valid:
        return jsonify({"ok": False, "message": validation_message}), 400

    asset_record = _serialize_asset_record(payload)
    asset_record["createdAt"] = str(payload.get("createdAt", "")).strip() or _utc_timestamp()
    asset_record["updatedAt"] = str(payload.get("updatedAt", "")).strip() or asset_record["createdAt"]

    existing_index = next(
        (index for index, asset in enumerate(ASSET_REGISTRY) if asset["assetId"] == asset_record["assetId"]),
        None,
    )

    if existing_index is None:
        ASSET_REGISTRY.append(asset_record)
    else:
        asset_record["createdAt"] = ASSET_REGISTRY[existing_index].get("createdAt", asset_record["createdAt"])
        asset_record["updatedAt"] = _utc_timestamp()
        ASSET_REGISTRY[existing_index] = asset_record

    return jsonify(
        {
            "ok": True,
            "item": asset_record,
            "message": "Asset registered in mock registry.",
        }
    ), 200


@app.get("/api/codebooks")
def api_codebooks():
    company = str(request.args.get("company", "")).strip()
    project = str(request.args.get("project", "")).strip()
    codebook_type = str(request.args.get("codebookType", "")).strip()

    codebooks = [_serialize_codebook_record(codebook) for codebook in CODEBOOK_REGISTRY]

    if company:
        codebooks = [codebook for codebook in codebooks if codebook["company"] == company]
    if project:
        codebooks = [codebook for codebook in codebooks if codebook["project"] == project]
    if codebook_type:
        codebooks = [codebook for codebook in codebooks if codebook["codebookType"] == codebook_type]

    return jsonify(
        {
            "ok": True,
            "count": len(codebooks),
            "items": codebooks,
        }
    ), 200


@app.get("/api/codebooks/current")
def api_codebooks_current():
    company = str(request.args.get("company", "")).strip()
    project = str(request.args.get("project", "")).strip()
    room = str(request.args.get("room", "dev-room")).strip() or "dev-room"

    if not company or not project:
        return jsonify(
            {
                "ok": False,
                "message": "company and project are required",
            }
        ), 400

    current = _resolve_current_codebook(company, project, room)
    if current is None:
        return jsonify(
            {
                "ok": False,
                "message": "No codebook found for the requested scope",
            }
        ), 404

    response = {
        "ok": True,
        "room": room,
        "item": current,
    }
    if current.get("message"):
        response["message"] = current["message"]

    return jsonify(response), 200


@app.post("/api/codebooks/register")
def api_codebooks_register():
    payload = request.get_json(silent=True) or {}
    is_valid, validation_message = _validate_codebook_payload(payload)

    if not is_valid:
        return jsonify({"ok": False, "message": validation_message}), 400

    codebook_record = _serialize_codebook_record(payload)
    codebook_record["createdAt"] = str(payload.get("createdAt", "")).strip() or _utc_timestamp()
    codebook_record["updatedAt"] = str(payload.get("updatedAt", "")).strip() or codebook_record["createdAt"]

    if codebook_record["codebookType"] == "master":
        duplicate_master = next(
            (
                existing
                for existing in CODEBOOK_REGISTRY
                if existing["company"] == codebook_record["company"]
                and existing["project"] == codebook_record["project"]
                and existing["codebookType"] == "master"
                and existing["codebookId"] != codebook_record["codebookId"]
            ),
            None,
        )
        if duplicate_master is not None:
            return jsonify(
                {
                    "ok": False,
                    "message": "Only one master codebook is allowed per project",
                }
            ), 400

    if codebook_record["codebookType"] == "client-safe":
        duplicate_client_safe = next(
            (
                existing
                for existing in CODEBOOK_REGISTRY
                if existing["company"] == codebook_record["company"]
                and existing["project"] == codebook_record["project"]
                and existing["codebookType"] == "client-safe"
                and existing["codebookId"] != codebook_record["codebookId"]
            ),
            None,
        )
        if duplicate_client_safe is not None:
            return jsonify(
                {
                    "ok": False,
                    "message": "Only one client-safe codebook is allowed per project",
                }
            ), 400

    existing_index = next(
        (index for index, codebook in enumerate(CODEBOOK_REGISTRY) if codebook["codebookId"] == codebook_record["codebookId"]),
        None,
    )

    if existing_index is None:
        CODEBOOK_REGISTRY.append(codebook_record)
    else:
        codebook_record["createdAt"] = CODEBOOK_REGISTRY[existing_index].get("createdAt", codebook_record["createdAt"])
        codebook_record["updatedAt"] = _utc_timestamp()
        CODEBOOK_REGISTRY[existing_index] = codebook_record

    return jsonify(
        {
            "ok": True,
            "item": codebook_record,
            "message": "Codebook registered in mock registry.",
        }
    ), 200


@app.post("/api/unity/push")
def api_unity_push():
    payload = request.get_json(silent=True) or {}
    is_valid, validation_message = _validate_unity_push_request(payload)

    if not is_valid:
        company = str(payload.get("company", "")).strip()
        project = str(payload.get("project", "")).strip()
        build_type = str(payload.get("buildType", "")).strip()
        version_id = str(payload.get("versionId", "")).strip()
        job_id = (
            f"job-{_slugify_scope_part(payload.get('timestamp', 'pending'))}-"
            f"{_slugify_scope_part(company)}-"
            f"{_slugify_scope_part(project)}-"
            f"{_slugify_scope_part(build_type or 'unknown')}"
        )
        return jsonify(
            {
                "ok": False,
                "jobId": job_id,
                "versionId": version_id,
                "buildType": build_type,
                "sceneTemplate": str(payload.get("sceneTemplate", "")).strip(),
                "unityTarget": "",
                "outputPath": "",
                "logsPath": f"/{company or 'company'}/{project or 'project'}/logs/{job_id}.log",
                "jobState": "queued",
                "message": validation_message,
            }
        ), 400

    return jsonify(_build_unity_push_result(payload)), 200


@app.post("/run-job")
def run_job():
    payload = request.get_json(silent=True) or {}
    command = str(payload.get("command", "")).strip()

    if not command:
        return jsonify({"ok": False, "error": "Missing command"}), 400

    return jsonify(
        {
            "ok": True,
            "message": "run-job placeholder only",
            "command": command,
        }
    ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
