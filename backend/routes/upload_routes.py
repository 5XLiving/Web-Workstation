from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")

@upload_bp.route("/image", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"ok": False, "error": "No selected file"}), 400
    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.root_path, "..", "backend", "public", "images")
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    # Return a URL that xyz_modular can use
    url = f"/public/images/{filename}"
    return jsonify({"ok": True, "url": url}), 200
