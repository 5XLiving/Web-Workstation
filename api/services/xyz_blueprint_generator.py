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

# --- Main Generator ---

def generate_blueprint_from_profile(profile: Dict[str, Any], bounds: Dict[str, Any], preset: str) -> Dict[str, Any]:
    """
    Generates a blueprint based on profile/mask, image bounds, and preset.
    profile: dict with region info (e.g., mask, bounding boxes)
    bounds: dict with image bounds (e.g., width, height)
    preset: string, one of the supported presets
    Returns: blueprint dict
    """
    if preset not in PRESET_DEFINITIONS:
        raise ValueError(f"Unknown preset: {preset}")
    preset_def = PRESET_DEFINITIONS[preset]
    anchors = []
    parts = []
    build_order = []

    width = bounds.get("width", 256)
    height = bounds.get("height", 256)
    cx, cy = width / 2, height / 2

    # Improved anchor placement with symmetry
    anchor_positions = {}
    for anchor_name in preset_def["anchors"]:
        pos = [cx, cy, 0.0]
        if "head" in anchor_name:
            pos[1] = cy - height * 0.3
        elif "pelvis" in anchor_name:
            pos[1] = cy + height * 0.2
        elif "torso" in anchor_name:
            pos[1] = cy
        elif "shoulder" in anchor_name:
            pos[1] = cy - height * 0.1
            pos[0] += -width * 0.2 if "left" in anchor_name else width * 0.2
        elif "hip" in anchor_name:
            pos[1] = cy + height * 0.15
            pos[0] += -width * 0.15 if "left" in anchor_name else width * 0.15
        elif "accessory" in anchor_name:
            pos[1] = cy - height * 0.4
        anchor_positions[anchor_name] = pos
        anchors.append(make_anchor(anchor_name, pos))

    # Explicit part-to-anchor mapping and richer part fields

    for part_name in preset_def["parts"]:
        # Explicit mapping for left/right limbs
        if part_name.startswith("left_upper_arm"):
            anchor = "left_shoulder"
            category = "limb"
        elif part_name.startswith("right_upper_arm"):
            anchor = "right_shoulder"
            category = "limb"
        elif part_name.startswith("left_lower_arm"):
            anchor = "left_shoulder"
            category = "limb"
        elif part_name.startswith("right_lower_arm"):
            anchor = "right_shoulder"
            category = "limb"
        elif part_name.startswith("left_upper_leg"):
            anchor = "left_hip"
            category = "limb"
        elif part_name.startswith("right_upper_leg"):
            anchor = "right_hip"
            category = "limb"
        elif part_name.startswith("left_lower_leg"):
            anchor = "left_hip"
            category = "limb"
        elif part_name.startswith("right_lower_leg"):
            anchor = "right_hip"
            category = "limb"
        elif part_name == "accessory":
            anchor = "accessory"
            category = "accessory"
        elif part_name in anchor_positions:
            anchor = part_name
            category = "core"
        else:
            anchor = preset_def["anchors"][0]
            category = "core"

        primitive_type = "block"
        size = [width * 0.1, height * 0.1, width * 0.1]
        if category == "limb":
            scale = preset_def["rules"].get("limb_scale", 1.0)
            size = [s * scale for s in size]
        if category == "accessory":
            scale = preset_def["rules"].get("accessory_scale", 1.0)
            size = [s * scale for s in size]
        rotation = [0.0, 0.0, 0.0]
        offset = [0.0, 0.0, 0.0]
        shell_thickness = 0.0
        parts.append(make_part(
            name=part_name,
            anchor=anchor,
            primitive_type=primitive_type,
            size=size,
            category=category,
            rotation=rotation,
            offset=offset,
            shell_thickness=shell_thickness
        ))
        build_order.append(part_name)

    blueprint = make_blueprint(preset, anchors, parts, build_order)
    return blueprint
