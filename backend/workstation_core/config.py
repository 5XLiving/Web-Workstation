from __future__ import annotations

import os


class CoreConfig:
    JSON_SORT_KEYS = False
    TESTING = False
    DEFAULT_COMPANY = os.environ.get("WORKSTATION_CORE_DEFAULT_COMPANY", "5xLiving")
    DEFAULT_PROJECT = os.environ.get("WORKSTATION_CORE_DEFAULT_PROJECT", "VR Workstation")
    DEFAULT_WORKSPACE = os.environ.get("WORKSTATION_CORE_DEFAULT_WORKSPACE", "local-workspace")
    DEFAULT_PRODUCT = os.environ.get("WORKSTATION_CORE_DEFAULT_PRODUCT", "3d-model-maker")
    ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.environ.get(
            "WORKSTATION_CORE_ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5500,http://127.0.0.1:5500",
        ).split(",")
        if origin.strip()
    ]