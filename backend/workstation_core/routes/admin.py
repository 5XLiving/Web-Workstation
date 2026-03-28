from __future__ import annotations

from flask import Blueprint, current_app, jsonify

admin_bp = Blueprint("workstation_core_admin", __name__)


@admin_bp.get("/admin/ping")
def admin_ping() -> tuple:
    store = current_app.extensions["workstation_core_store"]
    summary = store.summary()
    return (
        jsonify(
            {
                "ok": True,
                "status": "online",
                "service": "WorkStation Core",
                "admin": True,
                "mode": "mock",
                **summary,
            }
        ),
        200,
    )