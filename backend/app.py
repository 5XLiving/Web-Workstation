from pathlib import Path
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from routes.core_ctr_routes import core_ctr_bp

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

@app.get("/__which_app")
def which_app():
    return jsonify({"ok": True, "marker": "backend-app-clean"})


from routes.upload_routes import upload_bp
app.register_blueprint(core_ctr_bp)
app.register_blueprint(upload_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)