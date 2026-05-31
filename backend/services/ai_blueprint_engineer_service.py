from typing import Any, Dict, Optional
import math


try:
    from backend.services.procedural_blueprint_service import create_base_blueprint
except Exception:
    create_base_blueprint = None


def _asset_type_from_any(
    asset_type: Optional[str] = None,
    detect: Optional[Dict[str, Any]] = None,
) -> str:
    if asset_type:
        return str(asset_type)

    if isinstance(detect, dict):
        return str(
            detect.get("asset_type")
            or detect.get("type")
            or detect.get("category")
            or "mech"
        )

    return "mech"


def _safe_base_blueprint(asset_type: str) -> Dict[str, Any]:
    if create_base_blueprint:
        try:
            bp = create_base_blueprint(asset_type)
            if isinstance(bp, dict):
                bp.setdefault("parts", {})
                return bp
        except Exception:
            pass

    return {
        "asset_type": asset_type,
        "style": "dynamic_scan_shell",
        "parts": {},
        "meta": {},
    }


def _read_cage_scale(cage: Optional[Dict[str, Any]]) -> Dict[str, float]:
    """
    Cage is hidden metadata only.
    This reads rough proportions if your cage service provides them.
    """
    scale = {
        "height": 3.0,
        "width": 1.45,
        "depth": 0.9,
        "bulk": 1.0,
    }

    if not isinstance(cage, dict):
        return scale

    for key in ["height", "width", "depth", "bulk"]:
        try:
            if key in cage:
                scale[key] = float(cage[key])
        except Exception:
            pass

    bounds = cage.get("bounds") or cage.get("volume_bounds")
    if isinstance(bounds, dict):
        try:
            scale["height"] = float(bounds.get("height", scale["height"]))
            scale["width"] = float(bounds.get("width", scale["width"]))
            scale["depth"] = float(bounds.get("depth", scale["depth"]))
        except Exception:
            pass

    return scale


def _part(shape, scale, position, material="armor", **extra):
    data = {
        "shape": shape,
        "scale": scale,
        "position": position,
        "material": material,
    }
    data.update(extra)
    return data


def _limb(a, b, radius, material="armor"):
    return {
        "shape": "capsule",
        "from": a,
        "to": b,
        "radius": radius,
        "material": material,
    }


def _launcher(pos, height=0.42, radius=0.055):
    return {
        "shape": "launcher",
        "position": pos,
        "height": height,
        "radius": radius,
        "material": "weapon",
    }


def _finger_set(pos, side):
    return {
        "shape": "finger_set",
        "position": pos,
        "side": side,
        "count": 3,
        "length": 0.18,
        "spread": 0.055,
        "material": "joint",
    }


def _mech_humanoid_parts(scale_info: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    h = max(scale_info.get("height", 3.0), 2.2)
    w = max(scale_info.get("width", 1.45), 1.0)
    d = max(scale_info.get("depth", 0.9), 0.55)
    bulk = max(scale_info.get("bulk", 1.0), 0.7)

    # Normalized humanoid/mech points.
    y0 = -0.48
    head_y = y0 + h * 0.98
    chest_y = y0 + h * 0.75
    waist_y = y0 + h * 0.55
    hip_y = y0 + h * 0.44
    knee_y = y0 + h * 0.22

    shoulder_x = w * 0.36
    elbow_x = w * 0.61
    hand_x = w * 0.66
    knee_x = w * 0.23
    foot_x = w * 0.27

    parts = {
        "core_chest": _part(
            "tapered_box",
            [w * 0.46, h * 0.22, d * 0.42],
            [0, chest_y, 0.06],
            "body",
            taper=0.78,
        ),
        "front_chest_armor": _part(
            "armor_wedge",
            [w * 0.54, h * 0.14, d * 0.22],
            [0, chest_y + h * 0.03, d * 0.21],
            "armor",
            taper=0.68,
        ),
        "waist_core": _part(
            "tapered_box",
            [w * 0.32, h * 0.12, d * 0.32],
            [0, waist_y, 0.03],
            "body",
            taper=0.75,
        ),
        "hip_plate": _part(
            "armor_box",
            [w * 0.42, h * 0.07, d * 0.34],
            [0, hip_y, 0.04],
            "armor",
        ),
        "head": _part(
            "helmet_sphere",
            [w * 0.18, h * 0.08, d * 0.20],
            [0, head_y, 0.05],
            "armor",
        ),
        "helmet_front": _part(
            "tapered_box",
            [w * 0.22, h * 0.055, d * 0.08],
            [0, head_y - h * 0.005, d * 0.22],
            "armor",
            taper=0.5,
        ),
        "core_glow": _part(
            "glow_orb",
            [w * 0.085, h * 0.045, d * 0.04],
            [0, chest_y + h * 0.015, d * 0.31],
            "energy",
        ),

        # Shoulders are not oversized by default.
        "left_shoulder": _part(
            "shoulder_pad",
            [w * 0.22, h * 0.075, d * 0.32],
            [-shoulder_x, chest_y + h * 0.07, 0.02],
            "armor",
        ),
        "right_shoulder": _part(
            "shoulder_pad",
            [w * 0.22, h * 0.075, d * 0.32],
            [shoulder_x, chest_y + h * 0.07, 0.02],
            "armor",
        ),

        # Arms deliberately bend outward, not inward.
        "left_upper_arm": _limb(
            [-shoulder_x, chest_y + h * 0.04, 0.0],
            [-elbow_x, chest_y - h * 0.15, 0.05],
            0.075 * bulk,
        ),
        "right_upper_arm": _limb(
            [shoulder_x, chest_y + h * 0.04, 0.0],
            [elbow_x, chest_y - h * 0.15, 0.05],
            0.075 * bulk,
        ),
        "left_lower_arm": _limb(
            [-elbow_x, chest_y - h * 0.15, 0.05],
            [-hand_x, waist_y - h * 0.08, 0.10],
            0.065 * bulk,
        ),
        "right_lower_arm": _limb(
            [elbow_x, chest_y - h * 0.15, 0.05],
            [hand_x, waist_y - h * 0.08, 0.10],
            0.065 * bulk,
        ),
        "left_hand": _part(
            "joint_ball",
            [w * 0.07, h * 0.035, d * 0.06],
            [-hand_x, waist_y - h * 0.08, 0.11],
            "joint",
        ),
        "right_hand": _part(
            "joint_ball",
            [w * 0.07, h * 0.035, d * 0.06],
            [hand_x, waist_y - h * 0.08, 0.11],
            "joint",
        ),
        "left_fingers": _finger_set([-hand_x, waist_y - h * 0.08, 0.11], -1),
        "right_fingers": _finger_set([hand_x, waist_y - h * 0.08, 0.11], 1),

        # Legs also angle outward slightly.
        "left_upper_leg": _limb(
            [-w * 0.16, hip_y, 0.0],
            [-knee_x, knee_y, 0.04],
            0.085 * bulk,
        ),
        "right_upper_leg": _limb(
            [w * 0.16, hip_y, 0.0],
            [knee_x, knee_y, 0.04],
            0.085 * bulk,
        ),
        "left_lower_leg": _limb(
            [-knee_x, knee_y, 0.04],
            [-foot_x, y0, 0.16],
            0.08 * bulk,
        ),
        "right_lower_leg": _limb(
            [knee_x, knee_y, 0.04],
            [foot_x, y0, 0.16],
            0.08 * bulk,
        ),
        "left_foot": _part(
            "armor_box",
            [w * 0.20, h * 0.045, d * 0.42],
            [-foot_x, y0 - h * 0.015, 0.22],
            "joint",
        ),
        "right_foot": _part(
            "armor_box",
            [w * 0.20, h * 0.045, d * 0.42],
            [foot_x, y0 - h * 0.015, 0.22],
            "joint",
        ),

        # Four missing back launchers.
        "back_launcher_01": _launcher([-w * 0.31, head_y - h * 0.07, -d * 0.26]),
        "back_launcher_02": _launcher([-w * 0.12, head_y - h * 0.03, -d * 0.29]),
        "back_launcher_03": _launcher([w * 0.12, head_y - h * 0.03, -d * 0.29]),
        "back_launcher_04": _launcher([w * 0.31, head_y - h * 0.07, -d * 0.26]),

        # Weapon sockets.
        "left_weapon_socket": _part(
            "glow_orb",
            [0.04, 0.04, 0.04],
            [-hand_x - 0.06, waist_y - h * 0.08, 0.12],
            "energy",
        ),
        "right_weapon_socket": _part(
            "glow_orb",
            [0.04, 0.04, 0.04],
            [hand_x + 0.06, waist_y - h * 0.08, 0.12],
            "energy",
        ),
    }

    return parts


def _vehicle_parts(scale_info: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    w = max(scale_info.get("width", 2.4), 1.8)
    d = max(scale_info.get("depth", 1.2), 0.8)

    return {
        "main_chassis": _part("tapered_box", [w, 0.45, d], [0, 0.55, 0], "body", taper=0.82),
        "front_cabin": _part("tapered_box", [w * 0.42, 0.55, d * 0.72], [w * 0.12, 1.02, 0], "armor", taper=0.68),
        "rear_engine": _part("armor_box", [w * 0.35, 0.36, d * 0.85], [-w * 0.32, 0.82, 0], "armor"),
        "left_front_wheel": _part("cylinder", [0.28, 0.28, 0.28], [w * 0.33, 0.25, d * 0.52], "joint", axis=[0, 0, 1], radius=0.18, height=0.18),
        "right_front_wheel": _part("cylinder", [0.28, 0.28, 0.28], [w * 0.33, 0.25, -d * 0.52], "joint", axis=[0, 0, 1], radius=0.18, height=0.18),
        "left_rear_wheel": _part("cylinder", [0.28, 0.28, 0.28], [-w * 0.33, 0.25, d * 0.52], "joint", axis=[0, 0, 1], radius=0.18, height=0.18),
        "right_rear_wheel": _part("cylinder", [0.28, 0.28, 0.28], [-w * 0.33, 0.25, -d * 0.52], "joint", axis=[0, 0, 1], radius=0.18, height=0.18),
    }


def _generic_object_parts(scale_info: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    w = max(scale_info.get("width", 1.4), 0.8)
    h = max(scale_info.get("height", 1.6), 0.8)
    d = max(scale_info.get("depth", 1.0), 0.6)

    return {
        "main_volume": _part("tapered_box", [w, h * 0.7, d], [0, h * 0.35, 0], "body", taper=0.78),
        "front_detail": _part("armor_wedge", [w * 0.55, h * 0.22, d * 0.18], [0, h * 0.48, d * 0.46], "armor", taper=0.58),
        "top_detail": _part("helmet_sphere", [w * 0.22, h * 0.12, d * 0.22], [0, h * 0.8, 0], "armor"),
    }


def generate_blueprint_from_image(
    image_path: str,
    detect: Optional[Dict[str, Any]] = None,
    asset_type: Optional[str] = None,
    cage: Optional[Dict[str, Any]] = None,
    multiview: Optional[Any] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    CPU procedural blueprint engineer.

    It does NOT create final mesh.
    It creates a rich structured blueprint for mech_shell_builder_service.

    Compatible with old call:
        generate_blueprint_from_image(image_path, detect)

    Compatible with new call:
        generate_blueprint_from_image(image_path=image_path, asset_type=..., cage=..., multiview=...)
    """

    # Some callers pass asset_type as second positional argument.
    if isinstance(detect, str) and asset_type is None:
        asset_type = detect
        detect = None

    asset_type = _asset_type_from_any(asset_type=asset_type, detect=detect)
    scale_info = _read_cage_scale(cage)

    blueprint = _safe_base_blueprint(asset_type)
    blueprint["asset_type"] = asset_type
    blueprint["source_image"] = image_path
    blueprint["style"] = "dynamic_scan_shell"
    blueprint["engine"] = "cpu_blueprint_engineer_v2"

    lower = asset_type.lower()

    if any(k in lower for k in ["mech", "human", "humanoid", "character", "creature", "monster", "pet"]):
        parts = _mech_humanoid_parts(scale_info)
        skeleton_type = "humanoid_mech"
    elif any(k in lower for k in ["vehicle", "car", "transport", "tank", "truck"]):
        parts = _vehicle_parts(scale_info)
        skeleton_type = "vehicle"
    else:
        parts = _generic_object_parts(scale_info)
        skeleton_type = "generic_volume"

    # Merge with existing base parts if available, but dynamic scan parts override.
    base_parts = blueprint.get("parts", {})
    if not isinstance(base_parts, dict):
        base_parts = {}

    base_parts.update(parts)
    blueprint["parts"] = base_parts

    blueprint["meta"] = {
        "skeleton_type": skeleton_type,
        "cage_is_hidden_metadata": True,
        "uses_presets": "skeleton_only",
        "dynamic_parts": True,
        "add_launchers": True,
        "add_fingers": True,
        "add_sockets": True,
        "can_hold_weapon_later": True,
        "notes": [
            "Blueprint is generated from image/cage metadata.",
            "Shell builder turns these parts into final mesh.",
            "No fixed armor preset is required.",
        ],
    }

    return blueprint