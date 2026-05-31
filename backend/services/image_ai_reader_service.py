from PIL import Image
import numpy as np


def read_image_features(image_path: str) -> dict:
    img = Image.open(image_path).convert("RGBA")
    arr = np.array(img)

    alpha = arr[:, :, 3]
    mask = alpha > 20

    ys, xs = np.where(mask)

    if len(xs) == 0 or len(ys) == 0:
        return {
            "object_type": "generic_prop",
            "reason": "empty_alpha"
        }

    width = int(xs.max() - xs.min() + 1)
    height = int(ys.max() - ys.min() + 1)

    aspect = width / max(height, 1)
    fill_ratio = float(mask.sum()) / float(mask.shape[0] * mask.shape[1])

    # Basic color read
    rgb = arr[:, :, :3]
    visible_rgb = rgb[mask]
    avg_color = visible_rgb.mean(axis=0).astype(int).tolist()

    # Simple AI-like rule detection
    if aspect > 1.7:
        obj = "transport_ground"
        subtype = "vehicle"
    elif aspect < 0.55:
        obj = "building_tower"
        subtype = "tower"
    elif fill_ratio < 0.22 and height > width:
        obj = "tree"
        subtype = "tree"
    elif fill_ratio > 0.45 and aspect > 0.7 and aspect < 1.3:
        obj = "building"
        subtype = "block_building"
    else:
        obj = "generic_prop"
        subtype = "prop"

    return {
        "object_type": obj,
        "subtype": subtype,
        "width": width,
        "height": height,
        "aspect_ratio": aspect,
        "fill_ratio": fill_ratio,
        "avg_color": avg_color,
    }