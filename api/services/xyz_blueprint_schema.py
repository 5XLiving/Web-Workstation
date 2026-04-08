"""
xyz_blueprint_schema.py

Defines the blueprint schema, presets, validation, and helper builders
for XYZ modular construction.
"""

import enum
from typing import List, Dict, Any, Optional


class Preset(enum.Enum):
    GENERIC_OBJECT = "generic_object"
    HUMANOID = "humanoid"
    ARMORED_MASCOT_BIPED = "armored_mascot_biped"


PRESET_DEFINITIONS = {
    Preset.GENERIC_OBJECT.value: {
        "description": "Generic object with basic part structure.",
        "anchors": ["center"],
        "parts": ["block"],
        "rules": {},
    },
    Preset.HUMANOID.value: {
        "description": "Humanoid with head, torso, limbs.",
        "anchors": [
            "head",
            "torso",
            "pelvis",
            "left_shoulder",
            "right_shoulder",
            "left_hip",
            "right_hip",
        ],
        "parts": [
            "head",
            "torso",
            "pelvis",
            "left_upper_arm",
            "right_upper_arm",
            "left_lower_arm",
            "right_lower_arm",
            "left_upper_leg",
            "right_upper_leg",
            "left_lower_leg",
            "right_lower_leg",
        ],
        "rules": {"limb_scale": 1.0},
    },
    Preset.ARMORED_MASCOT_BIPED.value: {
        "description": "Armored mascot with exaggerated limbs and accessories.",
        "anchors": [
            "head",
            "torso",
            "pelvis",
            "left_shoulder",
            "right_shoulder",
            "left_hip",
            "right_hip",
            "accessory",
        ],
        "parts": [
            "head",
            "torso",
            "pelvis",
            "left_upper_arm",
            "right_upper_arm",
            "left_lower_arm",
            "right_lower_arm",
            "left_upper_leg",
            "right_upper_leg",
            "left_lower_leg",
            "right_lower_leg",
            "accessory",
        ],
        "rules": {"limb_scale": 1.3, "accessory_scale": 1.5},
    },
}


def validate_blueprint(blueprint: Dict[str, Any]) -> bool:
    for key in ["preset", "anchors", "parts", "build_order"]:
        if key not in blueprint:
            raise ValueError(f"Missing required blueprint key: {key}")

    preset = blueprint["preset"]
    if preset not in PRESET_DEFINITIONS:
        raise ValueError(f"Unknown preset: {preset}")

    preset_def = PRESET_DEFINITIONS[preset]

    anchors = blueprint["anchors"]
    if not isinstance(anchors, list) or not anchors:
        raise ValueError("Anchors must be a non-empty list.")

    anchor_names: List[str] = []
    for a in anchors:
        if not isinstance(a, dict):
            raise ValueError("Each anchor must be an object.")
        if "name" not in a or "position" not in a:
            raise ValueError("Each anchor must have 'name' and 'position'.")
        if not isinstance(a["name"], str):
            raise ValueError("Anchor 'name' must be a string.")

        pos = a["position"]
        if not (
            isinstance(pos, list)
            and len(pos) == 3
            and all(isinstance(x, (int, float)) for x in pos)
        ):
            raise ValueError(
                f"Anchor '{a['name']}' position must be a list of 3 numbers."
            )

        if a["name"] in anchor_names:
            raise ValueError(f"Duplicate anchor name: {a['name']}")
        anchor_names.append(a["name"])

    parts = blueprint["parts"]
    if not isinstance(parts, list) or not parts:
        raise ValueError("Parts must be a non-empty list.")

    part_names: List[str] = []
    for p in parts:
        if not isinstance(p, dict):
            raise ValueError("Each part must be an object.")

        for field in ["name", "anchor", "primitive_type", "size"]:
            if field not in p:
                raise ValueError(f"Part missing required field: {field}")

        if not isinstance(p["name"], str):
            raise ValueError("Part 'name' must be a string.")
        if p["name"] in part_names:
            raise ValueError(f"Duplicate part name: {p['name']}")

        if not isinstance(p["anchor"], str):
            raise ValueError("Part 'anchor' must be a string.")
        if p["anchor"] not in anchor_names:
            raise ValueError(
                f"Part '{p['name']}' references missing anchor '{p['anchor']}'."
            )

        if not isinstance(p["primitive_type"], str):
            raise ValueError(
                f"Part '{p['name']}' primitive_type must be a string."
            )

        if "category" in p and not isinstance(p["category"], str):
            raise ValueError(
                f"Part '{p['name']}' category must be a string if present."
            )

        size = p["size"]
        if not (
            isinstance(size, list)
            and len(size) == 3
            and all(isinstance(x, (int, float)) for x in size)
        ):
            raise ValueError(
                f"Part '{p['name']}' size must be a list of 3 numbers."
            )

        if "rotation" in p:
            rot = p["rotation"]
            if not (
                isinstance(rot, list)
                and len(rot) == 3
                and all(isinstance(x, (int, float)) for x in rot)
            ):
                raise ValueError(
                    f"Part '{p['name']}' rotation must be a list of 3 numbers if present."
                )

        if "offset" in p:
            off = p["offset"]
            if not (
                isinstance(off, list)
                and len(off) == 3
                and all(isinstance(x, (int, float)) for x in off)
            ):
                raise ValueError(
                    f"Part '{p['name']}' offset must be a list of 3 numbers if present."
                )

        if "shell_thickness" in p and not isinstance(
            p["shell_thickness"], (int, float)
        ):
            raise ValueError(
                f"Part '{p['name']}' shell_thickness must be numeric if present."
            )

        part_names.append(p["name"])

    build_order = blueprint["build_order"]
    if not isinstance(build_order, list) or not build_order:
        raise ValueError("build_order must be a non-empty list.")

    seen_build = set()
    for part_name in build_order:
        if part_name not in part_names:
            raise ValueError(f"build_order references missing part: {part_name}")
        if part_name in seen_build:
            raise ValueError(f"Duplicate entry in build_order: {part_name}")
        seen_build.add(part_name)

    if set(build_order) != set(part_names):
        missing = set(part_names) - set(build_order)
        extra = set(build_order) - set(part_names)
        if missing:
            raise ValueError(f"build_order is missing parts: {sorted(missing)}")
        if extra:
            raise ValueError(f"build_order has unknown parts: {sorted(extra)}")

    missing_required_anchors = set(preset_def["anchors"]) - set(anchor_names)
    if missing_required_anchors:
        raise ValueError(
            f"Preset '{preset}' missing required anchors: {sorted(missing_required_anchors)}"
        )

    missing_required_parts = set(preset_def["parts"]) - set(part_names)
    if missing_required_parts:
        raise ValueError(
            f"Preset '{preset}' missing required parts: {sorted(missing_required_parts)}"
        )

    return True


def make_anchor(name: str, position: List[float]) -> Dict[str, Any]:
    return {
        "name": name,
        "position": position,
    }


def make_part(
    name: str,
    anchor: str,
    primitive_type: str,
    size: List[float],
    category: str = "generic",
    rotation: Optional[List[float]] = None,
    offset: Optional[List[float]] = None,
    shell_thickness: float = 0.0,
) -> Dict[str, Any]:
    return {
        "name": name,
        "anchor": anchor,
        "primitive_type": primitive_type,
        "size": size,
        "category": category,
        "rotation": rotation if rotation is not None else [0.0, 0.0, 0.0],
        "offset": offset if offset is not None else [0.0, 0.0, 0.0],
        "shell_thickness": shell_thickness,
    }


def make_blueprint(
    preset: str,
    anchors: List[Dict[str, Any]],
    parts: List[Dict[str, Any]],
    build_order: List[str],
) -> Dict[str, Any]:
    blueprint = {
        "preset": preset,
        "anchors": anchors,
        "parts": parts,
        "build_order": build_order,
    }
    validate_blueprint(blueprint)
    return blueprint
