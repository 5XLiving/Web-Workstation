from pathlib import Path
from flask import Flask, jsonify, send_from_directory
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
    return send_from_directory("../", "3d_model_maker.html")

@app.route("/static/images/<path:filename>")
def serve_static_images(filename):
    return send_from_directory("static/images", filename)

@app.get("/__which_app")
def which_app():
    return jsonify({"ok": True, "marker": "backend-app-clean"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)