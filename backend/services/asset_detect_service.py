from PIL import Image
import numpy as np


def detect_asset_from_image(image_path: str) -> dict:
    return {
        "ok": True,
        "asset_type": "humanoid_mech",
        "parts": ["head", "torso", "chest", "arms", "legs", "armor", "cape", "core"],
        "confidence": 0.95,
        "reason": "Forced humanoid_mech for current mech workflow."
    }

    ys, xs = np.where(alpha)
    w = xs.max() - xs.min() + 1
    h = ys.max() - ys.min() + 1
    ratio = h / max(w, 1)

    if ratio > 1.2:
        asset_type = "humanoid_mech"
        parts = ["head", "chest", "arms", "legs", "armor"]
    elif ratio < 0.75:
        asset_type = "vehicle"
        parts = ["body", "wheels", "cabin"]
    else:
        asset_type = "world_prop"
        parts = ["main_body"]

    return {
        "ok": True,
        "asset_type": asset_type,
        "parts": parts,
        "confidence": 0.65,
        "reason": f"Detected by silhouette ratio {ratio:.2f}"
    }
