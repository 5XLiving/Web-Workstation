from PIL import Image
import numpy as np


ASSET_TEMPLATES = {
    "humanoid": {
        "template": "humanoid_mech_v2",
        "build_mode": "socket_skeleton",
        "needs_skeleton": True
    },
    "animal": {
        "template": "animal_quad_v1",
        "build_mode": "socket_skeleton",
        "needs_skeleton": True
    },
    "vehicle": {
        "template": "vehicle_car_v1",
        "build_mode": "modular_vehicle",
        "needs_skeleton": False
    },
    "bike": {
        "template": "bike_v1",
        "build_mode": "modular_vehicle",
        "needs_skeleton": False
    },
    "building": {
        "template": "building_v1",
        "build_mode": "architectural_blocks",
        "needs_skeleton": False
    },
    "terrain": {
        "template": "terrain_tile_v1",
        "build_mode": "terrain_grid",
        "needs_skeleton": False
    },
    "tree": {
        "template": "tree_v1",
        "build_mode": "organic_branching",
        "needs_skeleton": False
    },
    "road": {
        "template": "road_v1",
        "build_mode": "path_mesh",
        "needs_skeleton": False
    },
    "prop": {
        "template": "generic_prop_v1",
        "build_mode": "primitive_composition",
        "needs_skeleton": False
    }
}


def _subject_bounds(mask):
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None

    return {
        "min_x": int(xs.min()),
        "max_x": int(xs.max()),
        "min_y": int(ys.min()),
        "max_y": int(ys.max()),
        "width": int(max(xs.max() - xs.min(), 1)),
        "height": int(max(ys.max() - ys.min(), 1)),
        "area": int(mask.sum())
    }


def _row_density(mask):
    return mask.sum(axis=1)


def _col_density(mask):
    return mask.sum(axis=0)


def detect_asset_type(image_path: str):
    img = Image.open(image_path).convert("RGBA")
    arr = np.array(img)

    alpha = arr[:, :, 3]
    mask = alpha > 20

    bounds = _subject_bounds(mask)

    if not bounds:
        return {
            "ok": False,
            "asset_type": "unknown",
            "template": None,
            "build_mode": "none",
            "confidence": 0.0,
            "reason": "No visible subject detected."
        }

    h, w = mask.shape
    subject_w = bounds["width"]
    subject_h = bounds["height"]
    aspect = subject_w / max(subject_h, 1)
    fill_ratio = bounds["area"] / max(subject_w * subject_h, 1)

    rows = _row_density(mask)
    cols = _col_density(mask)

    upper = mask[bounds["min_y"]: bounds["min_y"] + subject_h // 3, :]
    middle = mask[bounds["min_y"] + subject_h // 3: bounds["min_y"] + 2 * subject_h // 3, :]
    lower = mask[bounds["min_y"] + 2 * subject_h // 3: bounds["max_y"] + 1, :]

    upper_density = upper.sum() / max(upper.size, 1)
    middle_density = middle.sum() / max(middle.size, 1)
    lower_density = lower.sum() / max(lower.size, 1)

    # Universal first-pass classification
    asset_type = "prop"
    confidence = 0.45
    reason = "Default balanced object."

    if aspect < 0.8 and middle_density > upper_density * 0.8:
        asset_type = "humanoid"
        confidence = 0.72
        reason = "Tall vertical body-like silhouette."

    elif aspect < 1.05 and lower_density > middle_density * 1.15:
        asset_type = "animal"
        confidence = 0.58
        reason = "Compact body with heavier lower mass."

    elif aspect >= 1.45 and fill_ratio > 0.22:
        asset_type = "vehicle"
        confidence = 0.68
        reason = "Wide horizontal solid object."

    elif aspect >= 1.25 and fill_ratio < 0.22:
        asset_type = "bike"
        confidence = 0.56
        reason = "Wide but sparse structure."

    elif aspect > 1.8 and fill_ratio < 0.18:
        asset_type = "road"
        confidence = 0.55
        reason = "Long flat path-like shape."

    elif aspect > 1.3 and fill_ratio > 0.55:
        asset_type = "terrain"
        confidence = 0.6
        reason = "Large filled area, likely terrain/tile."

    elif aspect < 0.75 and upper_density > middle_density * 1.1:
        asset_type = "tree"
        confidence = 0.55
        reason = "Tall organic top-heavy shape."

    elif 0.75 <= aspect <= 1.25 and fill_ratio > 0.5:
        asset_type = "building"
        confidence = 0.52
        reason = "Blocky filled structure."

    config = ASSET_TEMPLATES[asset_type]

    return {
        "ok": True,
        "asset_type": asset_type,
        "template": config["template"],
        "build_mode": config["build_mode"],
        "needs_skeleton": config["needs_skeleton"],
        "confidence": confidence,
        "reason": reason,
        "metrics": {
            "aspect": round(aspect, 3),
            "fill_ratio": round(fill_ratio, 3),
            "upper_density": round(float(upper_density), 3),
            "middle_density": round(float(middle_density), 3),
            "lower_density": round(float(lower_density), 3),
            "subject_width": subject_w,
            "subject_height": subject_h
        }
    }