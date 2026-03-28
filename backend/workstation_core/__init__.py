from __future__ import annotations

from flask import Flask, jsonify
from flask_cors import CORS

from .config import CoreConfig
from .routes.admin import admin_bp
from .routes.client import client_bp
from .store import ScopeStore


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(CoreConfig)

    if test_config:
        app.config.update(test_config)

    allowed_origins = app.config.get("ALLOWED_ORIGINS", [])

    CORS(
        app,
        resources={
            r"/api/*": {"origins": allowed_origins},
            r"/generate-model": {"origins": allowed_origins},
            r"/admin/*": {"origins": allowed_origins},
            r"/health": {"origins": "*"},
        },
    )

    app.extensions["workstation_core_store"] = ScopeStore()

    @app.get("/health")
    def health() -> tuple:
        return (
            jsonify(
                {
                    "ok": True,
                    "status": "healthy",
                    "service": "WorkStation Core",
                    "mode": "mock",
                }
            ),
            200,
        )

    app.register_blueprint(client_bp)
    app.register_blueprint(admin_bp)
    return app