import random
from typing import Any, Dict, Optional


SUPPORTED_ASSETS = {
    "tree", "rock", "bridge", "hill", "building", "house", "tower",
    "table", "chair", "crate", "barrel", "fence", "lamp", "sign",
    "terrain", "fixture", "prop",
}


def _make_tree_plan(asset_id: str, style: str, scale: float):
    return {
        "id": asset_id,
        "style": style,
        "parts": [
            {
                "name": f"{asset_id}_trunk",
                "shape": "cylinder",
                "position": [0, 1.0 * scale, 0],
                "scale": [0.22 * scale, 2.0 * scale, 0.22 * scale],
                "color": [0.42, 0.24, 0.12, 1],
            },

            {
                "name": f"{asset_id}_leaf_bottom",
                "shape": "tapered_box",
                "position": [0, 2.2 * scale, 0],
                "scale": [1.8 * scale, 1.0 * scale, 1.8 * scale],
                "taper_top": 0.15,
                "color": [0.12, 0.48, 0.18, 1],
            },

            {
                "name": f"{asset_id}_leaf_mid",
                "shape": "tapered_box",
                "position": [0, 3.0 * scale, 0],
                "scale": [1.4 * scale, 0.9 * scale, 1.4 * scale],
                "taper_top": 0.12,
                "color": [0.10, 0.52, 0.20, 1],
            },

            {
                "name": f"{asset_id}_leaf_top",
                "shape": "tapered_box",
                "position": [0, 3.7 * scale, 0],
                "scale": [0.9 * scale, 0.8 * scale, 0.9 * scale],
                "taper_top": 0.08,
                "color": [0.08, 0.45, 0.18, 1],
            },
        ],
        "details": [],
    }


def _make_rock_plan(asset_id: str, style: str, scale: float) -> Dict[str, Any]:
    return {
        "id": asset_id,
        "style": style,
        "parts": [
            {
                "name": f"{asset_id}_body",
                "shape": "tapered_box",
                "position": [0, 0.35 * scale, 0],
                "scale": [1.3 * scale, 0.7 * scale, 1.0 * scale],
                "taper_top": 0.75,
                "color": [0.45, 0.45, 0.43, 1],
            }
        ],
        "details": [],
    }


def _make_crate_plan(asset_id: str, style: str, scale: float) -> Dict[str, Any]:
    return {
        "id": asset_id,
        "style": style,
        "parts": [
            {
                "name": f"{asset_id}_box",
                "shape": "box",
                "position": [0, 0.5 * scale, 0],
                "scale": [1.0 * scale, 1.0 * scale, 1.0 * scale],
                "color": [0.55, 0.32, 0.14, 1],
            }
        ],
        "details": [
            {
                "name": f"{asset_id}_band_x",
                "shape": "flat_plate",
                "position": [0, 0.5 * scale, 0.52 * scale],
                "scale": [1.05 * scale, 1.0 * scale, 0.12 * scale],
                "color": [0.25, 0.16, 0.09, 1],
            }
        ],
    }


def _make_default_plan(asset_id: str, asset_type: str, style: str, scale: float) -> Dict[str, Any]:
    return {
        "id": asset_id,
        "style": style,
        "parts": [
            {
                "name": f"{asset_id}_body",
                "shape": "box",
                "position": [0, 0.5 * scale, 0],
                "scale": [1.0 * scale, 1.0 * scale, 1.0 * scale],
                "color": [0.6, 0.6, 0.6, 1],
            }
        ],
        "details": [],
        "asset_type": asset_type,
    }


def make_asset_plan(asset_id: str, asset_type: str, style: str, scale: float) -> Dict[str, Any]:
    if asset_type == "tree":
        return _make_tree_plan(asset_id, style, scale)
    if asset_type in {"rock", "hill"}:
        return _make_rock_plan(asset_id, style, scale)
    if asset_type in {"crate", "barrel"}:
        return _make_crate_plan(asset_id, style, scale)

    return _make_default_plan(asset_id, asset_type, style, scale)


def build_universal_asset(
    asset_type: str = "prop",
    style: str = "lowpoly",
    count: int = 1,
    seed: Optional[int] = None,
    options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    options = options or {}
    rng = random.Random(seed)

    asset_type = (asset_type or "prop").lower().strip()
    style = (style or "lowpoly").lower().strip()

    if asset_type not in SUPPORTED_ASSETS:
        asset_type = "prop"

    assets = []

    for i in range(count):
        scale = float(options.get("scale", rng.uniform(0.8, 1.4)))
        asset_id = f"{asset_type}_{i + 1}"
        plan = make_asset_plan(asset_id, asset_type, style, scale)

        assets.append({
            "id": asset_id,
            "asset_type": asset_type,
            "style": style,
            "transform": {
                "position": {
                    "x": round(rng.uniform(-5, 5), 3),
                    "y": 0,
                    "z": round(rng.uniform(-5, 5), 3),
                },
                "rotation": {
                    "x": 0,
                    "y": round(rng.uniform(0, 360), 3),
                    "z": 0,
                },
                "scale": {
                    "x": round(scale, 3),
                    "y": round(scale, 3),
                    "z": round(scale, 3),
                },
            },
            "build_profile": {
                "primitive_mode": "procedural_lowpoly",
                "mesh_skin": "pending_visual_detail",
                "collider": "auto",
            },
            "plan": plan,
            "options": options,
            "status": "generated",
        })

    return {
        "ok": True,
        "type": "universal_asset",
        "asset_type": asset_type,
        "style": style,
        "count": count,
        "seed": seed,
        "assets": assets,
    }