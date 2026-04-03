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

# --- Legacy Core CTR compatibility stub ---
# Keeps old HTML pages working until CORE_CTR_BASE calls are fully removed.
core_ctr_stub = Blueprint("core_ctr_stub", __name__, url_prefix="/api/core-ctr/v1")

@core_ctr_stub.route("/health")
def ctr_health():
    return jsonify({"ok": True, "status": "stub", "message": "Core CTR retired — stub active"}), 200

@core_ctr_stub.route("/jobs/create", methods=["POST"])
def ctr_jobs_create():
    return jsonify({"ok": False, "error": "Core CTR create is retired. Use Dev Room."}), 410

@core_ctr_stub.route("/jobs/preview", methods=["POST"])
def ctr_jobs_preview():
    return jsonify({"ok": False, "error": "Core CTR preview is retired. Use XYZ Modular."}), 410

@core_ctr_stub.route("/jobs/<job_id>")
def ctr_jobs_get(job_id):
    return jsonify({"ok": False, "error": f"Core CTR job lookup retired. job_id={job_id}"}), 410

app.register_blueprint(core_ctr_stub)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)