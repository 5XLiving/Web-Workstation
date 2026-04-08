"""
xyz_blueprint_generator.py

Rule-based blueprint generator for XYZ modular system.
Generates a blueprint from mask/profile, image bounds, and selected preset.
Outputs strict blueprint JSON only.
"""

from typing import Dict, Any, List
from .xyz_blueprint_schema import (
    PRESET_DEFINITIONS, make_anchor, make_part, make_blueprint
)


def _num(value: Any, name: str, default: float) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = float(default)
    if v <= 0:
        raise ValueError(f"{name} must be > 0")
    return v


def _part_spec(part_name: str, width: float, height: float, preset_def: Dict[str, Any]) -> Dict[str, Any]:
    limb_scale = float(preset_def["rules"].get("limb_scale", 1.0))
    accessory_scale = float(preset_def["rules"].get("accessory_scale", 1.0))

    specs = {
        "head": {"size": [width * 0.18, height * 0.18, width * 0.18], "category": "core", "anchor": "head"},
        "torso": {"size": [width * 0.22, height * 0.28, width * 0.14], "category": "core", "anchor": "torso"},
        "pelvis": {"size": [width * 0.18, height * 0.14, width * 0.12], "category": "core", "anchor": "pelvis"},
        "left_upper_arm": {"size": [width * 0.09, height * 0.16, width * 0.09], "category": "limb", "anchor": "left_shoulder"},
        "right_upper_arm": {"size": [width * 0.09, height * 0.16, width * 0.09], "category": "limb", "anchor": "right_shoulder"},
        "left_lower_arm": {"size": [width * 0.08, height * 0.15, width * 0.08], "category": "limb", "anchor": "left_shoulder"},
        "right_lower_arm": {"size": [width * 0.08, height * 0.15, width * 0.08], "category": "limb", "anchor": "right_shoulder"},
        "left_upper_leg": {"size": [width * 0.10, height * 0.18, width * 0.10], "category": "limb", "anchor": "left_hip"},
        "right_upper_leg": {"size": [width * 0.10, height * 0.18, width * 0.10], "category": "limb", "anchor": "right_hip"},
        "left_lower_leg": {"size": [width * 0.09, height * 0.17, width * 0.09], "category": "limb", "anchor": "left_hip"},
        "right_lower_leg": {"size": [width * 0.09, height * 0.17, width * 0.09], "category": "limb", "anchor": "right_hip"},
        "accessory": {"size": [width * 0.12, height * 0.12, width * 0.12], "category": "accessory", "anchor": "accessory"},
        "block": {"size": [width * 0.24, height * 0.24, width * 0.24], "category": "generic", "anchor": "center"},
    }

    spec = specs.get(part_name, {"size": [width * 0.1, height * 0.1, width * 0.1], "category": "core", "anchor": preset_def["anchors"][0]})

    if spec["category"] == "limb":
        spec["size"] = [s * limb_scale for s in spec["size"]]
    elif spec["category"] == "accessory":
        spec["size"] = [s * accessory_scale for s in spec["size"]]

    return spec


def generate_blueprint_from_profile(profile: Dict[str, Any], bounds: Dict[str, Any], preset: str) -> Dict[str, Any]:
    if preset not in PRESET_DEFINITIONS:
        raise ValueError(f"Unknown preset: {preset}")

    preset_def = PRESET_DEFINITIONS[preset]

    width = _num(bounds.get("width", 256), "width", 256)
    height = _num(bounds.get("height", 256), "height", 256)

    cx, cy = width / 2.0, height / 2.0

    anchors: List[Dict[str, Any]] = []
    parts: List[Dict[str, Any]] = []
    build_order: List[str] = []

    for anchor_name in preset_def["anchors"]:
        pos = [cx, cy, 0.0]

        if anchor_name == "head":
            pos = [cx, cy - height * 0.30, 0.0]
        elif anchor_name == "torso":
            pos = [cx, cy, 0.0]
        elif anchor_name == "pelvis":
            pos = [cx, cy + height * 0.20, 0.0]
        elif anchor_name == "left_shoulder":
            pos = [cx - width * 0.20, cy - height * 0.10, 0.0]
        elif anchor_name == "right_shoulder":
            pos = [cx + width * 0.20, cy - height * 0.10, 0.0]
        elif anchor_name == "left_hip":
            pos = [cx - width * 0.15, cy + height * 0.15, 0.0]
        elif anchor_name == "right_hip":
            pos = [cx + width * 0.15, cy + height * 0.15, 0.0]
        elif anchor_name == "accessory":
            pos = [cx, cy - height * 0.40, 0.0]
        elif anchor_name == "center":
            pos = [cx, cy, 0.0]

        anchors.append(make_anchor(anchor_name, pos))

    for part_name in preset_def["parts"]:
        spec = _part_spec(part_name, width, height, preset_def)

        parts.append(
            make_part(
                name=part_name,
                anchor=spec["anchor"],
                primitive_type="block",
                size=spec["size"],
                category=spec["category"],
                rotation=[0.0, 0.0, 0.0],
                offset=[0.0, 0.0, 0.0],
                shell_thickness=0.0,
            )
        )
        build_order.append(part_name)

    return make_blueprint(preset, anchors, parts, build_order)
