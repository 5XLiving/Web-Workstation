import json
from pathlib import Path
from PIL import Image
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = PROJECT_ROOT / "backend" / "data" / "skeleton_templates"


def _hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def detect_main_colors(img, max_colors=5):
    img = img.convert("RGB").resize((64, 64))
    arr = np.array(img).reshape((-1, 3))

    buckets = {}
    for p in arr:
        key = tuple((p // 32) * 32)
        buckets[key] = buckets.get(key, 0) + 1

    ranked = sorted(buckets.items(), key=lambda x: x[1], reverse=True)
    colors = [_hex(c) for c, _ in ranked[:max_colors]]

    while len(colors) < 5:
        colors.append("#666666")

    return colors


def load_skeleton_template(name="humanoid_mech_v2"):
    path = TEMPLATE_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Skeleton template not found: {path}")
    return json.loads(path.read_text())


def fit_image_to_skeleton(image_path: str, skeleton_name="humanoid_mech_v2"):
    img = Image.open(image_path).convert("RGBA")
    arr = np.array(img)
    alpha = arr[:, :, 3]
    mask = alpha > 20

    ys, xs = np.where(mask)
    if len(xs) == 0:
        raise ValueError("No visible subject detected.")

    min_x, max_x = xs.min(), xs.max()
    min_y, max_y = ys.min(), ys.max()

    subject_w = max(max_x - min_x, 1)
    subject_h = max(max_y - min_y, 1)

    colors = detect_main_colors(img)
    primary = colors[0]
    secondary = colors[1]
    accent = colors[2] if colors[2] != primary else "#ff7a00"

    template = load_skeleton_template(skeleton_name)
    sockets = template["sockets"]
    joint_rules = template.get("joint_rules", {})

    aspect = subject_w / subject_h
    bulky = aspect > 0.55

    scale_x = 1.25 if bulky else 1.0
    scale_z = 0.85 if bulky else 0.65

    armor_density = 4 if bulky else 2
    booster_count = 4 if bulky else 2
    spike_count = 6 if bulky else 2

    build_form = {
        "model_type": "humanoid_mech",
        "skeleton": skeleton_name,
        "style": "socket_fitted_from_image",
        "scan_result": {
            "confidence": 0.76,
            "subject_width_px": int(subject_w),
            "subject_height_px": int(subject_h),
            "bulky": bulky,
            "main_colors": colors
        },
        "sockets": sockets,
        "joint_rules": joint_rules,
        "parts": []
    }

    def add_part(
        part_id,
        socket,
        primitive,
        size,
        color,
        material,
        count=1,
        spread_axis="x",
        spacing=0.35,
        rotation=None
    ):
        build_form["parts"].append({
            "part_id": part_id,
            "socket": socket,
            "exists": True,
            "count": count,
            "primitive": primitive,
            "size": size,
            "color": color,
            "material": material,
            "spread_axis": spread_axis,
            "spacing": spacing,
            "rotation": rotation or {"x": 0, "y": 0, "z": 0}
        })

    # Head / torso
    add_part("head", "head", "sphere",
             {"width": 0.52 * scale_x, "height": 0.52, "depth": 0.52 * scale_z},
             secondary, "helmet")

    add_part("neck_joint", "neck_joint", "joint",
             {"width": 0.22, "height": 0.22, "depth": 0.22},
             primary, "neck_joint")

    add_part("chest_core", "chest", "rounded_box",
             {"width": 1.38 * scale_x, "height": 1.05, "depth": 0.75 * scale_z},
             primary, "torso_metal")

    add_part("waist_joint", "waist_joint", "joint",
             {"width": 0.28, "height": 0.28, "depth": 0.28},
             secondary, "waist_joint")

    add_part("hips", "hips", "rounded_box",
             {"width": 0.9 * scale_x, "height": 0.38, "depth": 0.55 * scale_z},
             primary, "hip_metal")

    # Arms
    add_part("left_shoulder_joint", "left_shoulder_joint", "joint",
             {"width": 0.34, "height": 0.34, "depth": 0.34},
             secondary, "shoulder_joint")

    add_part("right_shoulder_joint", "right_shoulder_joint", "joint",
             {"width": 0.34, "height": 0.34, "depth": 0.34},
             secondary, "shoulder_joint")

    add_part("left_upper_arm", "left_upper_arm", "capsule",
             {"width": 0.28, "height": 0.62, "depth": 0.28},
             primary, "upper_arm_metal")

    add_part("right_upper_arm", "right_upper_arm", "capsule",
             {"width": 0.28, "height": 0.62, "depth": 0.28},
             primary, "upper_arm_metal")

    add_part("left_elbow_joint", "left_elbow_joint", "joint",
             {"width": 0.28, "height": 0.28, "depth": 0.28},
             secondary, "elbow_joint")

    add_part("right_elbow_joint", "right_elbow_joint", "joint",
             {"width": 0.28, "height": 0.28, "depth": 0.28},
             secondary, "elbow_joint")

    add_part("left_forearm", "left_forearm", "capsule",
             {"width": 0.34, "height": 0.68, "depth": 0.34},
             primary, "forearm_metal")

    add_part("right_forearm", "right_forearm", "capsule",
             {"width": 0.34, "height": 0.68, "depth": 0.34},
             primary, "forearm_metal")

    add_part("left_wrist_joint", "left_wrist_joint", "joint",
             {"width": 0.22, "height": 0.22, "depth": 0.22},
             secondary, "wrist_joint")

    add_part("right_wrist_joint", "right_wrist_joint", "joint",
             {"width": 0.22, "height": 0.22, "depth": 0.22},
             secondary, "wrist_joint")

    add_part("left_palm", "left_palm", "rounded_box",
             {"width": 0.34, "height": 0.14, "depth": 0.24},
             secondary, "palm_metal")

    add_part("right_palm", "right_palm", "rounded_box",
             {"width": 0.34, "height": 0.14, "depth": 0.24},
             secondary, "palm_metal")

    # Fingers
    for side in ["left", "right"]:
        for finger in ["thumb", "finger_1", "finger_2", "finger_3"]:
            add_part(f"{side}_{finger}", f"{side}_{finger}", "capsule",
                     {"width": 0.08, "height": 0.2, "depth": 0.08},
                     secondary, "finger_metal")

    # Legs
    add_part("left_hip_joint", "left_hip_joint", "joint",
             {"width": 0.32, "height": 0.32, "depth": 0.32},
             secondary, "hip_joint")

    add_part("right_hip_joint", "right_hip_joint", "joint",
             {"width": 0.32, "height": 0.32, "depth": 0.32},
             secondary, "hip_joint")

    add_part("left_thigh", "left_thigh", "capsule",
             {"width": 0.38, "height": 0.72, "depth": 0.38},
             primary, "thigh_metal")

    add_part("right_thigh", "right_thigh", "capsule",
             {"width": 0.38, "height": 0.72, "depth": 0.38},
             primary, "thigh_metal")

    add_part("left_knee_joint", "left_knee_joint", "joint",
             {"width": 0.32, "height": 0.32, "depth": 0.32},
             secondary, "knee_joint")

    add_part("right_knee_joint", "right_knee_joint", "joint",
             {"width": 0.32, "height": 0.32, "depth": 0.32},
             secondary, "knee_joint")

    add_part("left_shin", "left_shin", "capsule",
             {"width": 0.4, "height": 0.78, "depth": 0.4},
             primary, "shin_metal")

    add_part("right_shin", "right_shin", "capsule",
             {"width": 0.4, "height": 0.78, "depth": 0.4},
             primary, "shin_metal")

    add_part("left_ankle_joint", "left_ankle_joint", "joint",
             {"width": 0.24, "height": 0.24, "depth": 0.24},
             secondary, "ankle_joint")

    add_part("right_ankle_joint", "right_ankle_joint", "joint",
             {"width": 0.24, "height": 0.24, "depth": 0.24},
             secondary, "ankle_joint")

    add_part("left_foot", "left_foot", "wedge_foot",
             {"width": 0.62, "height": 0.18, "depth": 0.78},
             secondary, "foot_metal")

    add_part("right_foot", "right_foot", "wedge_foot",
             {"width": 0.62, "height": 0.18, "depth": 0.78},
             secondary, "foot_metal")

    add_part("left_toe", "left_toe", "rounded_box",
             {"width": 0.34, "height": 0.08, "depth": 0.16},
             accent, "toe_plate")

    add_part("right_toe", "right_toe", "rounded_box",
             {"width": 0.34, "height": 0.08, "depth": 0.16},
             accent, "toe_plate")

    # Armor / boosters / spikes
    add_part("armor_chest_plates", "chest_front", "rounded_box",
             {"width": 0.32, "height": 0.12, "depth": 0.08},
             secondary, "armor_plate", count=armor_density, spread_axis="x", spacing=0.36)

    add_part("back_boosters", "back", "cylinder",
             {"width": 0.24, "height": 0.85, "depth": 0.24},
             accent, "booster_glow", count=booster_count, spread_axis="x", spacing=0.42)

    add_part("top_spikes", "head_top", "cone",
             {"width": 0.14, "height": 0.36, "depth": 0.14},
             secondary, "spike_metal", count=spike_count, spread_axis="x", spacing=0.28)

    return build_form