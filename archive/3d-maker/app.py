from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                r"http://localhost(:\\d+)?",
                r"http://127\.0\.0\.1(:\\d+)?",
            ]
        },
        r"/public/*": {
            "origins": [
                r"http://localhost(:\\d+)?",
                r"http://127\.0\.0\.1(:\\d+)?",
            ]
        },
        r"/health": {
            "origins": "*"
        },
        r"/run-job": {
            "origins": [
                r"http://localhost(:\\d+)?",
                r"http://127\.0\.0\.1(:\\d+)?",
            ]
        },
    },
)

# simple in-memory state for now
DEV_STATE = {
    "workerStatus": "connected",
    "runnerStatus": "connected",
    "security": "nominal",
    "lastCommand": "",
    "lastError": "",
    "jobQueue": [],
}


def absolute_public_url(path_fragment: str) -> str:
    base = request.host_url
    return urljoin(base, f"public/{path_fragment}")


@app.get("/health")
def health() -> tuple:
    return jsonify({"ok": True}), 200


@app.get("/api/dev/status")
def api_dev_status() -> tuple:
    return jsonify(
        {
            "ok": True,
            "workerStatus": DEV_STATE["workerStatus"],
            "runnerStatus": DEV_STATE["runnerStatus"],
            "security": DEV_STATE["security"],
            "lastCommand": DEV_STATE["lastCommand"],
            "lastError": DEV_STATE["lastError"],
            "jobQueue": DEV_STATE["jobQueue"],
        }
    ), 200


@app.post("/api/dev/chat")
def api_dev_chat() -> tuple:
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"ok": False, "reply": "Empty command."}), 400

    DEV_STATE["lastCommand"] = message
    DEV_STATE["lastError"] = ""

    lower = message.lower()

    if lower == "status":
        return jsonify(
            {
                "ok": True,
                "reply": "Worker online. Runner connected. Security nominal."
            }
        ), 200

    if lower == "hello" or lower == "ai":
        return jsonify(
            {
                "ok": True,
                "reply": "Hello. Dev Room worker is responding."
            }
        ), 200

    if "terrain" in lower:
        job = {
            "id": f"job_{len(DEV_STATE['jobQueue']) + 1:03d}",
            "command": message,
            "status": "accepted",
        }
        DEV_STATE["jobQueue"].append(job)
        return jsonify(
            {
                "ok": True,
                "reply": "Terrain job accepted. Unity not connected yet.",
                "job": job,
            }
        ), 200

    return jsonify(
        {
            "ok": True,
            "reply": f"Command received: {message}"
        }
    ), 200


@app.post("/run-job")
def run_job() -> tuple:
    payload = request.get_json(silent=True) or {}
    command = str(payload.get("command", "")).strip()
    project = str(payload.get("project", "web-workstation")).strip()

    if not command:
        return jsonify({"ok": False, "error": "Missing command"}), 400

    DEV_STATE["lastCommand"] = command
    DEV_STATE["lastError"] = ""

    lower = command.lower()

    if "terrain" in lower:
        job = {
            "id": f"job_{len(DEV_STATE['jobQueue']) + 1:03d}",
            "project": project,
            "command": command,
            "status": "accepted",
        }
        DEV_STATE["jobQueue"].append(job)

        return jsonify(
            {
                "ok": True,
                "message": "Terrain job accepted. Unity not connected yet.",
                "job": job,
            }
        ), 200

    return jsonify(
        {
            "ok": False,
            "error": "Unsupported command",
        }
    ), 400


@app.post("/api/ai-image")
def api_ai_image() -> tuple:
    payload = request.get_json(silent=True) or {}

    _prompt = str(payload.get("prompt", "")).strip()
    _style = str(payload.get("style", "")).strip()
    _aspect = str(payload.get("aspect", "")).strip()

    response = {
        "imageUrl": absolute_public_url("images/sample.png"),
        "note": "placeholder",
    }
    return jsonify(response), 200


@app.post("/api/mesh")
def api_mesh() -> tuple:
    payload = request.get_json(silent=True) or {}

    _image_url = str(payload.get("imageUrl", "")).strip()
    _species = str(payload.get("species", "")).strip()
    _params = payload.get("params", {})

    response = {
        "glbUrl": absolute_public_url("models/sample.glb"),
        "stats": {
            "triangles": 12345,
            "width": 0.8,
            "height": 1.2,
        },
        "note": "placeholder",
    }
    return jsonify(response), 200


@app.get("/public/<path:filename>")
def serve_public(filename: str):
    return send_from_directory(PUBLIC_DIR, filename, as_attachment=False)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)