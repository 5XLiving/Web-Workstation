import json
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRESET_DIR = PROJECT_ROOT / "backend" / "assets" / "presets"


PRESET_MAP = {
    "transportation": "transport_ground.json",
    "vehicle": "transport_ground.json",
    "terrain": "terrain_basic.json",
    "scenery": "terrain_basic.json",
    "building": "building_basic.json",
    "tree": "tree_basic.json",
    "plant": "tree_basic.json",
    "rock": "rock_basic.json",
    "fixture": "prop_basic.json",
    "prop": "prop_basic.json",
    "custom": "custom_fallback.json",
}


def load_preset_by_name(filename: str) -> Dict[str, Any]:
    path = PRESET_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Preset not found: {path}")

    return json.loads(path.read_text(encoding="utf-8"))


def load_preset_for_asset(asset_type: str) -> Dict[str, Any]:
    key = (asset_type or "custom").lower().strip()
    filename = PRESET_MAP.get(key, "custom_fallback.json")
    return load_preset_by_name(filename)
