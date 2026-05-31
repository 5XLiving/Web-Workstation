from pathlib import Path
from typing import Any, Dict, List

from PIL import Image
import numpy as np


def _rgba_to_float_color(rgb):
    return [
        round(float(rgb[0]) / 255.0, 3),
        round(float(rgb[1]) / 255.0, 3),
        round(float(rgb[2]) / 255.0, 3),
        1,
    ]


def _safe_bounds(mask):
    ys, xs = np.where(mask)

    if len(xs) < 20:
        return None

    return {
        "x_min": int(xs.min()),
        "x_max": int(xs.max()),
        "y_min": int(ys.min()),
        "y_max": int(ys.max()),
        "width": int(xs.max() - xs.min() + 1),
        "height": int(ys.max() - ys.min() + 1),
    }


def _dominant_color(arr, mask):
    pixels = arr[:, :, :3][mask]

    if len(pixels) == 0:
        return [0.55, 0.55, 0.55, 1]

    rgb = np.median(pixels, axis=0)
    return _rgba_to_float_color(rgb)


def _make_part(name, shape, position, scale, color):
    return {
        "name": name,
        "shape": shape,
        "position": [round(float(v), 3) for v in position],
        "scale": [round(float(v), 3) for v in scale],
        "color": color,
    }


def build_custom_asset_plan(
    image_path: str,
    asset_id: str = "custom_1",
    label: str = "custom_asset",
    style: str = "lowpoly_custom",
) -> Dict[str, Any]:

    img = Image.open(image_path).convert("RGBA")
    arr = np.array(img)

    alpha = arr[:, :, 3]
    rgb = arr[:, :, :3]
    brightness = rgb.mean(axis=2)

    mask = (alpha > 20) & (brightness > 8)
    bounds = _safe_bounds(mask)

    if not bounds:
        return {
            "id": asset_id,
            "asset_type": "custom",
            "custom_label": label,
            "style": style,
            "parts": [
                _make_part(
                    f"{asset_id}_fallback_body",
                    "box",
                    [0, 0.5, 0],
                    [1, 1, 1],
                    [0.55, 0.55, 0.55, 1],
                )
            ],
            "details": [],
            "analysis": {
                "ok": False,
                "reason": "not enough visible pixels",
            },
        }

    w = bounds["width"]
    h = bounds["height"]
    ratio = h / max(w, 1)
    color = _dominant_color(arr, mask)

    parts: List[Dict[str, Any]] = []
    details: List[Dict[str, Any]] = []

    width_scale = max(0.7, min(2.2, 1.4 / max(ratio, 0.5)))

    if ratio >= 1.15:
        parts.append(_make_part(
            f"{asset_id}_core_body",
            "tapered_box",
            [0, 1.45, 0],
            [0.9 * width_scale, 1.55, 0.45 * width_scale],
            color,
        ))

        parts.append(_make_part(
            f"{asset_id}_upper_head_or_cap",
            "box",
            [0, 2.65, 0],
            [0.55 * width_scale, 0.45, 0.45 * width_scale],
            color,
        ))

        parts.append(_make_part(
            f"{asset_id}_left_side_part",
            "capsule",
            [-0.62 * width_scale, 1.45, 0],
            [0.25, 1.2, 0.25],
            color,
        ))

        parts.append(_make_part(
            f"{asset_id}_right_side_part",
            "capsule",
            [0.62 * width_scale, 1.45, 0],
            [0.25, 1.2, 0.25],
            color,
        ))

        parts.append(_make_part(
            f"{asset_id}_left_lower_support",
            "capsule",
            [-0.28 * width_scale, 0.45, 0],
            [0.28, 0.95, 0.28],
            color,
        ))

        parts.append(_make_part(
            f"{asset_id}_right_lower_support",
            "capsule",
            [0.28 * width_scale, 0.45, 0],
            [0.28, 0.95, 0.28],
            color,
        ))

    elif ratio <= 0.55:
        parts.append(_make_part(
            f"{asset_id}_wide_body",
            "box",
            [0, 0.75, 0],
            [2.4, 0.75, 0.9],
            color,
        ))

        parts.append(_make_part(
            f"{asset_id}_front_module",
            "tapered_box",
            [0.9, 0.8, 0],
            [0.8, 0.65, 0.8],
            color,
        ))

        parts.append(_make_part(
            f"{asset_id}_rear_module",
            "box",
            [-0.9, 0.8, 0],
            [0.75, 0.65, 0.75],
            color,
        ))

        details.append(_make_part(
            f"{asset_id}_left_wheel_or_side_detail",
            "cylinder",
            [-0.75, 0.35, 0.55],
            [0.35, 0.22, 0.35],
            [0.08, 0.08, 0.08, 1],
        ))

        details.append(_make_part(
            f"{asset_id}_right_wheel_or_side_detail",
            "cylinder",
            [0.75, 0.35, 0.55],
            [0.35, 0.22, 0.35],
            [0.08, 0.08, 0.08, 1],
        ))

    else:
        parts.append(_make_part(
            f"{asset_id}_main_mass",
            "tapered_box",
            [0, 0.85, 0],
            [1.4, 1.1, 1.0],
            color,
        ))

        parts.append(_make_part(
            f"{asset_id}_top_detail",
            "box",
            [0, 1.55, 0],
            [0.8, 0.45, 0.7],
            color,
        ))

        details.append(_make_part(
            f"{asset_id}_base_plate",
            "flat_plate",
            [0, 0.08, 0],
            [1.6, 1.0, 1.1],
            color,
        ))

    return {
        "id": asset_id,
        "asset_type": "custom",
        "custom_label": label,
        "style": style,
        "parts": parts,
        "details": details,
        "analysis": {
            "ok": True,
            "image_width": int(img.width),
            "image_height": int(img.height),
            "object_width": int(w),
            "object_height": int(h),
            "ratio": round(float(ratio), 3),
            "dominant_color": color,
            "strategy": "custom silhouette primitive decomposition",
        },
    }