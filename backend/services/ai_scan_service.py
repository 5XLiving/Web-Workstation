import json
from pathlib import Path
from PIL import Image
import numpy as np

SCHEMA_PATH = Path("backend/schemas/ai_3d_build_form.json")


def detect_main_colors(img, max_colors=5):

    img = img.convert("RGB")
    img = img.resize((64, 64))

    arr = np.array(img).reshape((-1, 3))

    colors = {}

    for pixel in arr:

        key = tuple((pixel // 32) * 32)

        if key not in colors:
            colors[key] = 0

        colors[key] += 1

    sorted_colors = sorted(
        colors.items(),
        key=lambda x: x[1],
        reverse=True
    )

    result = []

    for c, _ in sorted_colors[:max_colors]:
        result.append('#%02x%02x%02x' % c)

    return result


def scan_image_to_build_form(image_path: str):

    form = json.loads(SCHEMA_PATH.read_text())

    img = Image.open(image_path).convert("RGBA")

    arr = np.array(img)

    alpha = arr[:, :, 3]

    mask = alpha > 20

    h, w = mask.shape

    colors = detect_main_colors(img)

    primary = colors[0] if len(colors) > 0 else "#666666"
    secondary = colors[1] if len(colors) > 1 else primary
    accent = colors[2] if len(colors) > 2 else "#ff7a00"

    ys, xs = np.where(mask)

    if len(xs) == 0:
        raise ValueError("No visible subject detected.")

    min_x = xs.min()
    max_x = xs.max()

    min_y = ys.min()
    max_y = ys.max()

    subject_w = max_x - min_x
    subject_h = max_y - min_y

    aspect_ratio = subject_w / subject_h

    row_density = []

    for y in range(h):
        row_density.append(mask[y].sum())

    row_density = np.array(row_density)

    chest_y = min_y + int(subject_h * 0.32)
    waist_y = min_y + int(subject_h * 0.52)
    leg_y = min_y + int(subject_h * 0.78)

    chest_y = min(chest_y, h - 1)
    waist_y = min(waist_y, h - 1)
    leg_y = min(leg_y, h - 1)

    shoulder_width = row_density[chest_y] / max(subject_w, 1)
    waist_width = row_density[waist_y] / max(subject_w, 1)
    leg_width = row_density[leg_y] / max(subject_w, 1)

    bulky = shoulder_width > 0.55

    torso_width = 1.9 if bulky else 1.3
    torso_depth = 1.1 if bulky else 0.7

    arm_size = 0.42 if bulky else 0.28
    leg_size = 0.52 if bulky else 0.36

    booster_count = 6 if bulky else 2
    spike_count = 8 if bulky else 2

    head_size = 0.62 if bulky else 0.45

    shoulder_offset = torso_width * 0.72
    hip_offset = torso_width * 0.25

    form["parts"] = [

        {
            "part_id": "torso",
            "exists": True,
            "count": 1,
            "primitive": "box",
            "position": {
                "x": 0,
                "y": 1.5,
                "z": 0
            },
            "size": {
                "width": torso_width,
                "height": 1.6,
                "depth": torso_depth
            },
            "material": "torso_metal",
            "color": primary
        },

        {
            "part_id": "head",
            "exists": True,
            "count": 1,
            "primitive": "sphere",
            "position": {
                "x": 0,
                "y": 2.7,
                "z": 0
            },
            "size": {
                "width": head_size,
                "height": head_size,
                "depth": head_size
            },
            "material": "helmet",
            "color": secondary
        },

        {
            "part_id": "left_arm",
            "exists": True,
            "count": 1,
            "primitive": "cylinder",
            "position": {
                "x": -shoulder_offset,
                "y": 1.45,
                "z": 0
            },
            "size": {
                "width": arm_size,
                "height": 1.35,
                "depth": arm_size
            },
            "material": "arm_metal",
            "color": primary
        },

        {
            "part_id": "right_arm",
            "exists": True,
            "count": 1,
            "primitive": "cylinder",
            "position": {
                "x": shoulder_offset,
                "y": 1.45,
                "z": 0
            },
            "size": {
                "width": arm_size,
                "height": 1.35,
                "depth": arm_size
            },
            "material": "arm_metal",
            "color": primary
        },

        {
            "part_id": "left_leg",
            "exists": True,
            "count": 1,
            "primitive": "cylinder",
            "position": {
                "x": -hip_offset,
                "y": -0.1,
                "z": 0
            },
            "size": {
                "width": leg_size,
                "height": 1.7,
                "depth": leg_size
            },
            "material": "leg_metal",
            "color": primary
        },

        {
            "part_id": "right_leg",
            "exists": True,
            "count": 1,
            "primitive": "cylinder",
            "position": {
                "x": hip_offset,
                "y": -0.1,
                "z": 0
            },
            "size": {
                "width": leg_size,
                "height": 1.7,
                "depth": leg_size
            },
            "material": "leg_metal",
            "color": primary
        },

        {
            "part_id": "boosters",
            "exists": True,
            "count": booster_count,
            "primitive": "cylinder",
            "spread_axis": "x",
            "spacing": 0.45,
            "position": {
                "x": 0,
                "y": 2.0,
                "z": -0.7
            },
            "size": {
                "width": 0.25,
                "height": 0.95,
                "depth": 0.25
            },
            "material": "booster",
            "color": accent
        },

        {
            "part_id": "spikes",
            "exists": True,
            "count": spike_count,
            "primitive": "cone",
            "spread_axis": "x",
            "spacing": 0.38,
            "position": {
                "x": 0,
                "y": 3.0,
                "z": 0
            },
            "size": {
                "width": 0.16,
                "height": 0.4,
                "depth": 0.16
            },
            "material": "gold_spike",
            "color": secondary
        }
    ]

    return form