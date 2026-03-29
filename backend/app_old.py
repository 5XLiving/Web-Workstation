# Backup of previous backend/app.py
# Do not use directly for startup. Reference only.

from __future__ import annotations
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

# ...existing code... (routes, logic, etc.)
