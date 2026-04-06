

# ...existing imports...
from pathlib import Path
from flask import Blueprint, Flask, jsonify, make_response, request, send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__, static_folder="static")
CORS(app)

# Silence Chrome DevTools workspace probe (must be after app = Flask(...))
@app.route("/.well-known/appspecific/com.chrome.devtools.json")
def chrome_devtools_json():
    return jsonify({}), 200



from pathlib import Path
from flask import Blueprint, Flask, jsonify, make_response, request, send_from_directory
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
    resp = make_response(send_from_directory(html_path.parent, html_path.name))
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

@app.route("/static/images/<path:filename>")
def serve_static_images(filename):
    return send_from_directory("static/images", filename)

@app.route("/public/images/<path:filename>")
def serve_public_images(filename):
    return send_from_directory("public/images", filename)


# Serve favicon.ico from static/assets/images
@app.route('/favicon.ico')
def favicon():
    favicon_path = (BASE_DIR / 'static' / 'assets' / 'images' / 'favicon.ico').resolve()
    return send_from_directory(favicon_path.parent, favicon_path.name)

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


# ── Preset classes ────────────────────────────────────────────
from services.preset_classes import list_presets, DEFAULT_PRESET

# --- Preview service ---
from services.preview_service import generate_preview

@xyz_bp.route("/presets")
def xyz_presets():
    return jsonify({"ok": True, "default": DEFAULT_PRESET, "presets": list_presets()}), 200


# Honest preview endpoint (Phase 1)
@xyz_bp.route("/preview", methods=["POST"])
def xyz_preview():
    """Accept masked image + preset class, return honest preview (pointcloud/depth/mesh)."""
    if "image" not in request.files:
        return jsonify({"ok": False, "error": "No image file provided"}), 400

    image_file = request.files["image"]
    image_bytes = image_file.read()
    if not image_bytes:
        return jsonify({"ok": False, "error": "Empty image file"}), 400

    mask_bytes = None
    if "mask" in request.files:
        mb = request.files["mask"].read()
        if mb:
            mask_bytes = mb

    preset_class = request.form.get("preset_class", DEFAULT_PRESET)

    try:
        result = generate_preview(
            image_bytes=image_bytes,
            mask_bytes=mask_bytes,
            preset=preset_class,
        )
        # Ensure standardized schema
        return jsonify({"ok": True, **result}), 200
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": f"Preview failed: {exc}"}), 500


# ── Image-to-3D inference endpoint ───────────────────────────
from services.inference_service import run_inference

@xyz_bp.route("/infer", methods=["POST"])
def xyz_infer():
    """Accept masked image + preset class, return structure + point cloud + steps."""
    if "image" not in request.files:
        return jsonify({"ok": False, "error": "No image file provided"}), 400

    image_file = request.files["image"]
    image_bytes = image_file.read()
    if not image_bytes:
        return jsonify({"ok": False, "error": "Empty image file"}), 400

    mask_bytes = None
    if "mask" in request.files:
        mb = request.files["mask"].read()
        if mb:
            mask_bytes = mb

    preset_class = request.form.get("preset_class", DEFAULT_PRESET)

    # Optional user dimension overrides
    user_dims = {}
    for key in ("width", "height", "depth"):
        raw = request.form.get(key)
        if raw is not None:
            try:
                user_dims[key] = float(raw)
            except (ValueError, TypeError):
                pass

    try:
        result = run_inference(
            image_bytes=image_bytes,
            mask_bytes=mask_bytes,
            preset_class=preset_class,
            user_dimensions=user_dims if user_dims else None,
        )
        return jsonify(result), 200
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": f"Inference failed: {exc}"}), 500


app.register_blueprint(xyz_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)