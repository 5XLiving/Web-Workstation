from pathlib import Path
from flask import Blueprint, Flask, jsonify, make_response, request, send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route("/.well-known/appspecific/com.chrome.devtools.json")
def chrome_devtools_json():
    return jsonify({}), 200

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

@app.route("/favicon.ico")
def favicon():
    favicon_path = (BASE_DIR / "static" / "assets" / "images" / "favicon.ico").resolve()
    return send_from_directory(favicon_path.parent, favicon_path.name)

@app.get("/__which_app")
def which_app():
    return jsonify({"ok": True, "marker": "backend-app-clean"})
