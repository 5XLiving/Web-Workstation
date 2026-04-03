from pathlib import Path
from flask import Blueprint, Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route("/")
def root():
    return jsonify({"ok": True, "message": "Workstation backend root"}), 200

@app.route("/health")
def health():
    return jsonify({"ok": True, "message": "Workstation backend healthy"}), 200

@app.route("/3d_model_maker")
def serve_3d_model_maker():
    html_path = (BASE_DIR.parent / "3d_model_maker.html").resolve()
    return send_from_directory(html_path.parent, html_path.name)


# Serve xyz_modular.html from the root directory
@app.route("/xyz_modular")
def serve_xyz_modular():
    html_path = (BASE_DIR.parent / "xyz_modular.html").resolve()
    return send_from_directory(html_path.parent, html_path.name)

@app.route("/static/images/<path:filename>")
def serve_static_images(filename):
    return send_from_directory("static/images", filename)

@app.route("/public/images/<path:filename>")
def serve_public_images(filename):
    return send_from_directory("public/images", filename)

@app.get("/__which_app")
def which_app():
    return jsonify({"ok": True, "marker": "backend-app-clean"})


from routes.upload_routes import upload_bp
app.register_blueprint(upload_bp)

# --- XYZ Builder API ---
from services.modular_service import handle_modular_job
from schemas.job_schema import validate_job_payload, generate_job_id, current_timestamp
from storage.job_store import create_job, get_job as store_get_job

xyz_bp = Blueprint("xyz", __name__, url_prefix="/api/xyz/v1")

@xyz_bp.route("/health")
def xyz_health():
    return jsonify({"ok": True, "status": "active", "message": "XYZ builder healthy"}), 200

@xyz_bp.route("/jobs/create", methods=["POST"])
def xyz_jobs_create():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"ok": False, "error": "Missing JSON body"}), 400
    errors = validate_job_payload(payload)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 400
    job_id = generate_job_id()
    job = {**payload, "job_id": job_id, "status": "queued", "created_at": current_timestamp()}
    create_job(job)
    result = handle_modular_job(job)
    return jsonify({"ok": True, "job_id": job_id, **result}), 200

@xyz_bp.route("/jobs/preview", methods=["POST"])
def xyz_jobs_preview():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"ok": False, "error": "Missing JSON body"}), 400
    errors = validate_job_payload(payload)
    if errors:
        return jsonify({"ok": False, "errors": errors}), 400
    job_id = generate_job_id()
    job = {**payload, "job_id": job_id, "status": "preview", "created_at": current_timestamp()}
    result = handle_modular_job(job)
    return jsonify({"ok": True, "job_id": job_id, **result}), 200

@xyz_bp.route("/jobs/<job_id>")
def xyz_jobs_get(job_id):
    job = store_get_job(job_id)
    if not job:
        return jsonify({"ok": False, "error": f"Job not found: {job_id}"}), 404
    return jsonify({"ok": True, **job}), 200

app.register_blueprint(xyz_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)