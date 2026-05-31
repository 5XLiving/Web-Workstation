from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple
import math
import uuid


Vec3 = Tuple[float, float, float]
Vec2 = Tuple[float, float]


@dataclass
class CageAnchor:
    name: str
    zone: str
    position: Vec3
    normal: Vec3
    socket_type: str = "surface"


@dataclass
class CageUVZone:
    name: str
    zone: str
    uv_min: Vec2
    uv_max: Vec2
    projection: str = "front"


@dataclass
class CageZone:
    name: str
    category: str
    center: Vec3
    scale: Vec3
    rotation: Vec3
    shape: str = "ellipsoid"
    material_slot: str = "cage_body"
    surface_offset: float = 0.02
    anchors: Optional[List[CageAnchor]] = None
    uv_zones: Optional[List[CageUVZone]] = None
    diamond_grid: Optional[Dict[str, Any]] = None


@dataclass
class UniversalCage:
    cage_id: str
    cage_type: str
    asset_type: str
    movement_type: str
    symmetry: bool
    zones: List[CageZone]
    global_anchors: List[CageAnchor]
    metadata: Dict[str, Any]


def _vec3(value: Any, default: Vec3 = (0.0, 0.0, 0.0)) -> Vec3:
    if isinstance(value, (list, tuple)) and len(value) >= 3:
        return (float(value[0]), float(value[1]), float(value[2]))
    return default


def _scale(value: Any, default: Vec3 = (1.0, 1.0, 1.0)) -> Vec3:
    return _vec3(value, default)


def _normalise(v: Vec3) -> Vec3:
    x, y, z = v
    length = math.sqrt(x * x + y * y + z * z)
    if length <= 0:
        return (0.0, 1.0, 0.0)
    return (x / length, y / length, z / length)


def _anchor(
    name: str,
    zone: str,
    center: Vec3,
    offset: Vec3,
    socket_type: str = "surface",
) -> CageAnchor:
    return CageAnchor(
        name=name,
        zone=zone,
        position=(center[0] + offset[0], center[1] + offset[1], center[2] + offset[2]),
        normal=_normalise(offset),
        socket_type=socket_type,
    )


def _default_uv(name: str, zone: str, index: int, total: int) -> List[CageUVZone]:
    total = max(total, 1)
    width = 1.0 / total
    u0 = index * width
    u1 = min(1.0, u0 + width)

    return [
        CageUVZone(
            name=f"{name}_front_uv",
            zone=zone,
            uv_min=(u0, 0.50),
            uv_max=(u1, 1.00),
            projection="front",
        ),
        CageUVZone(
            name=f"{name}_back_uv",
            zone=zone,
            uv_min=(u0, 0.00),
            uv_max=(u1, 0.50),
            projection="back",
        ),
    ]


def _zone_from_part(part: Dict[str, Any], index: int, total: int) -> CageZone:
    name = str(part.get("name") or f"zone_{index}")
    category = str(part.get("category") or part.get("type") or "body")
    center = _vec3(part.get("position") or part.get("center"))
    scale = _scale(part.get("scale"), (1.0, 1.0, 1.0))
    rotation = _vec3(part.get("rotation"), (0.0, 0.0, 0.0))
    shape = str(part.get("shape") or "ellipsoid")

    sx, sy, sz = scale

    anchors = [
        _anchor(f"{name}_top", name, center, (0.0, sy * 0.5, 0.0)),
        _anchor(f"{name}_bottom", name, center, (0.0, -sy * 0.5, 0.0)),
        _anchor(f"{name}_front", name, center, (0.0, 0.0, sz * 0.5)),
        _anchor(f"{name}_back", name, center, (0.0, 0.0, -sz * 0.5)),
        _anchor(f"{name}_left", name, center, (-sx * 0.5, 0.0, 0.0)),
        _anchor(f"{name}_right", name, center, (sx * 0.5, 0.0, 0.0)),
    ]

    return CageZone(
        name=name,
        category=category,
        center=center,
        scale=scale,
        rotation=rotation,
        shape=shape,
        material_slot=str(part.get("material") or "cage_body"),
        surface_offset=float(part.get("surface_offset", 0.02)),
        anchors=anchors,
        uv_zones=_default_uv(name, name, index, total),
    )


def _human_base_parts() -> List[Dict[str, Any]]:
    return [
        {"name": "head", "category": "body", "position": [0, 2.45, 0], "scale": [0.46, 0.56, 0.42]},
        {"name": "neck", "category": "body", "position": [0, 2.10, 0], "scale": [0.24, 0.24, 0.24]},
        {"name": "chest", "category": "body", "position": [0, 1.62, 0], "scale": [0.95, 0.82, 0.42]},
        {"name": "belly", "category": "body", "position": [0, 1.12, 0], "scale": [0.78, 0.55, 0.38]},
        {"name": "pelvis", "category": "body", "position": [0, 0.72, 0], "scale": [0.82, 0.42, 0.42]},
        {"name": "left_upper_arm", "category": "limb", "position": [-0.72, 1.55, 0], "scale": [0.25, 0.72, 0.25]},
        {"name": "right_upper_arm", "category": "limb", "position": [0.72, 1.55, 0], "scale": [0.25, 0.72, 0.25]},
        {"name": "left_forearm", "category": "limb", "position": [-0.88, 0.96, 0], "scale": [0.22, 0.66, 0.22]},
        {"name": "right_forearm", "category": "limb", "position": [0.88, 0.96, 0], "scale": [0.22, 0.66, 0.22]},
        {"name": "left_hand", "category": "limb", "position": [-0.92, 0.50, 0], "scale": [0.22, 0.24, 0.12]},
        {"name": "right_hand", "category": "limb", "position": [0.92, 0.50, 0], "scale": [0.22, 0.24, 0.12]},
        {"name": "left_thigh", "category": "limb", "position": [-0.28, 0.12, 0], "scale": [0.30, 0.78, 0.30]},
        {"name": "right_thigh", "category": "limb", "position": [0.28, 0.12, 0], "scale": [0.30, 0.78, 0.30]},
        {"name": "left_shin", "category": "limb", "position": [-0.28, -0.62, 0], "scale": [0.24, 0.72, 0.24]},
        {"name": "right_shin", "category": "limb", "position": [0.28, -0.62, 0], "scale": [0.24, 0.72, 0.24]},
        {"name": "left_foot", "category": "limb", "position": [-0.28, -1.10, 0.10], "scale": [0.26, 0.16, 0.46]},
        {"name": "right_foot", "category": "limb", "position": [0.28, -1.10, 0.10], "scale": [0.26, 0.16, 0.46]},
    ]


def _vehicle_base_parts() -> List[Dict[str, Any]]:
    return [
        {"name": "main_body", "category": "vehicle", "position": [0, 0.8, 0], "scale": [2.8, 0.7, 1.4], "shape": "box"},
        {"name": "cabin", "category": "vehicle", "position": [0.35, 1.35, 0], "scale": [1.1, 0.8, 1.1], "shape": "box"},
        {"name": "front", "category": "vehicle", "position": [1.55, 0.75, 0], "scale": [0.55, 0.55, 1.2], "shape": "box"},
        {"name": "rear", "category": "vehicle", "position": [-1.55, 0.75, 0], "scale": [0.55, 0.55, 1.2], "shape": "box"},
    ]


def _prop_base_parts() -> List[Dict[str, Any]]:
    return [
        {"name": "core", "category": "prop", "position": [0, 0.6, 0], "scale": [1.0, 1.0, 1.0], "shape": "box"},
        {"name": "top", "category": "prop", "position": [0, 1.2, 0], "scale": [0.8, 0.35, 0.8], "shape": "box"},
        {"name": "base", "category": "prop", "position": [0, 0.05, 0], "scale": [1.1, 0.18, 1.1], "shape": "box"},
    ]


def _pick_default_parts(asset_type: str, cage_type: str) -> List[Dict[str, Any]]:
    key = f"{asset_type} {cage_type}".lower()

    if any(x in key for x in ["human", "humanoid", "mech", "monster", "animal"]):
        return _human_base_parts()

    if any(x in key for x in ["vehicle", "car", "transport"]):
        return _vehicle_base_parts()

    return _prop_base_parts()


def _apply_detected_cage_scaling(
    parts: List[Dict[str, Any]],
    detect: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    if not detect:
        return parts

    scale_multiplier = float(detect.get("scale_multiplier", 1.0))
    width_multiplier = float(detect.get("width_multiplier", 1.0))
    height_multiplier = float(detect.get("height_multiplier", 1.0))
    depth_multiplier = float(detect.get("depth_multiplier", 1.0))

    scaled_parts: List[Dict[str, Any]] = []

    for part in parts:
        p = dict(part)
        scale = list(p.get("scale", [1.0, 1.0, 1.0]))

        scale[0] = float(scale[0]) * scale_multiplier * width_multiplier
        scale[1] = float(scale[1]) * scale_multiplier * height_multiplier
        scale[2] = float(scale[2]) * scale_multiplier * depth_multiplier

        p["scale"] = scale
        scaled_parts.append(p)

    return scaled_parts


def build_universal_cage(
    asset_type: str = "humanoid",
    cage_type: str = "universal_humanoid",
    source_template: Optional[Dict[str, Any]] = None,
    detect: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_template = source_template or {}
    detect = detect or {}

    parts = (
        source_template.get("cage_parts")
        or source_template.get("body_parts")
        or source_template.get("parts")
        or _pick_default_parts(asset_type, cage_type)
    )

    parts = _apply_detected_cage_scaling(parts, detect)

    zones = [_zone_from_part(part, i, len(parts)) for i, part in enumerate(parts)]

    global_anchors: List[CageAnchor] = []
    for zone in zones:
        if zone.anchors:
            global_anchors.extend(zone.anchors)

    movement_type = str(
        source_template.get("movement_type")
        or detect.get("movement_type")
        or ("rigged" if "human" in cage_type or "humanoid" in cage_type else "static")
    )

    cage = UniversalCage(
        cage_id=f"cage_{uuid.uuid4().hex[:12]}",
        cage_type=cage_type,
        asset_type=asset_type,
        movement_type=movement_type,
        symmetry=bool(source_template.get("symmetry", True)),
        zones=zones,
        global_anchors=global_anchors,
        metadata={
            "version": "universal_cage_v1",
            "purpose": "control cage for texture projection and shell mounting",
            "rule": "skeleton moves, cage shapes, texture wraps, shell mounts",
            "source_detect": detect,
            "zone_count": len(zones),
            "anchor_count": len(global_anchors),
        },
    )

    return _to_dict(cage)


def _to_dict(cage: UniversalCage) -> Dict[str, Any]:
    data = asdict(cage)

    for zone in data["zones"]:
        zone["center"] = list(zone["center"])
        zone["scale"] = list(zone["scale"])
        zone["rotation"] = list(zone["rotation"])

        for anchor in zone.get("anchors") or []:
            anchor["position"] = list(anchor["position"])
            anchor["normal"] = list(anchor["normal"])

        for uv in zone.get("uv_zones") or []:
            uv["uv_min"] = list(uv["uv_min"])
            uv["uv_max"] = list(uv["uv_max"])

    for anchor in data["global_anchors"]:
        anchor["position"] = list(anchor["position"])
        anchor["normal"] = list(anchor["normal"])

    return data


def get_cage_zone(cage: Dict[str, Any], zone_name: str) -> Optional[Dict[str, Any]]:
    for zone in cage.get("zones", []):
        if zone.get("name") == zone_name:
            return zone
    return None


def get_zone_anchor(
    cage: Dict[str, Any],
    zone_name: str,
    anchor_name: str,
) -> Optional[Dict[str, Any]]:
    zone = get_cage_zone(cage, zone_name)
    if not zone:
        return None

    for anchor in zone.get("anchors", []):
        if anchor.get("name") == anchor_name:
            return anchor

    return None


def list_mount_zones(cage: Dict[str, Any]) -> List[str]:
    return [zone.get("name") for zone in cage.get("zones", []) if zone.get("name")]


def build_shell_mount_instruction(
    cage: Dict[str, Any],
    shell_name: str,
    mount_zone: str,
    surface_offset: float = 0.04,
    follow_cage: bool = True,
) -> Dict[str, Any]:
    zone = get_cage_zone(cage, mount_zone)
    if not zone:
        raise ValueError(f"Mount zone not found: {mount_zone}")

    return {
        "name": shell_name,
        "type": "shell_mount_instruction",
        "mount_zone": mount_zone,
        "zone_center": zone["center"],
        "zone_scale": zone["scale"],
        "surface_offset": surface_offset,
        "follow_cage": follow_cage,
        "rule": "shell mounts on cage surface, does not replace cage",
    }