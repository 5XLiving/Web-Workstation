from PIL import Image
import numpy as np


def scan_terrain_from_image(image_path: str):
    img = Image.open(image_path).convert("RGBA")
    arr = np.array(img)

    alpha = arr[:, :, 3]
    mask = alpha > 20

    ys, xs = np.where(mask)

    if len(xs) == 0:
        return {
            "asset_type": "terrain",
            "shape": "square",
            "height_mode": "flat",
            "confidence": 0.0,
            "reason": "No visible subject detected."
        }

    min_x, max_x = xs.min(), xs.max()
    min_y, max_y = ys.min(), ys.max()

    subject_w = max(max_x - min_x, 1)
    subject_h = max(max_y - min_y, 1)
    aspect = subject_w / subject_h

    area = mask.sum()
    bbox_area = subject_w * subject_h
    fill_ratio = area / max(bbox_area, 1)

    shape = "square"
    confidence = 0.55

    if 0.75 <= aspect <= 1.25 and fill_ratio > 0.65:
        shape = "round"
        confidence = 0.62

    if fill_ratio < 0.55:
        shape = "irregular"
        confidence = 0.68

    # Basic color/texture roughness estimate
    rgb = arr[:, :, :3][mask]
    color_std = float(np.std(rgb)) if len(rgb) > 0 else 0.0

    height_mode = "flat"
    if color_std > 42:
        height_mode = "random_multi_point"

    return {
        "asset_type": "terrain",
        "shape": shape,
        "height_mode": height_mode,
        "confidence": confidence,
        "reason": "Detected terrain shape and height mode from silhouette and color variation.",
        "metrics": {
            "aspect": round(float(aspect), 3),
            "fill_ratio": round(float(fill_ratio), 3),
            "color_std": round(color_std, 3),
            "subject_width": int(subject_w),
            "subject_height": int(subject_h)
        }
    }


def build_terrain_form_from_image(image_path: str):
    scan = scan_terrain_from_image(image_path)

    return {
        "asset_type": "terrain",
        "shape": scan["shape"],
        "height_mode": scan["height_mode"],
        "width": 4.0,
        "depth": 4.0,
        "height": 0.18,
        "segments": 24,
        "scan_result": scan
    }
