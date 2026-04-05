from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def _allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS



def _upload_dir() -> Path:
    configured = current_app.config.get("UPLOAD_IMAGE_DIR")
    if configured:
        return Path(configured).resolve()
    # default: backend/static/images relative to app root
    return (Path(current_app.root_path).resolve() / "static" / "images").resolve()



def _url_prefix() -> str:
    return current_app.config.get("UPLOAD_IMAGE_URL_PREFIX", "/static/images")


@upload_bp.route("/image", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file part"}), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"ok": False, "error": "No selected file"}), 400

    if not _allowed_file(file.filename):
        return jsonify(
            {
                "ok": False,
                "error": "Unsupported file type. Allowed: png, jpg, jpeg, webp, gif",
            }
        ), 400

    original_name = secure_filename(file.filename)
    ext = original_name.rsplit(".", 1)[1].lower()
    stem = original_name.rsplit(".", 1)[0] or "upload"
    safe_name = f"{stem}_{uuid4().hex[:12]}.{ext}"

    upload_folder = _upload_dir()
    upload_folder.mkdir(parents=True, exist_ok=True)

    file_path = upload_folder / safe_name
    file.save(str(file_path))

    url = f"{_url_prefix().rstrip('/')}/{safe_name}"

    return jsonify(
        {
            "ok": True,
            "filename": safe_name,
            "url": url,
        }
    ), 200
