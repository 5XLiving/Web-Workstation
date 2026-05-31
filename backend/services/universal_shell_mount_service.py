from __future__ import annotations

from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import uuid


def _find_zone(cage: Dict[str, Any], zone_name: str) -> Optional[Dict[str, Any]]:
    for zone in cage.get("zones", []):
        if zone.get("name") == zone_name:
            return zone
    return None


def _find_anchor(zone: Dict[str, Any], anchor_name: Optional[str]) -> Optional[Dict[str, Any]]:
    anchors = zone.get("anchors") or []
    if not anchors:
        return None

    if anchor_name:
        for a in anchors:
            if a.get("name") == anchor_name:
                return a

    for a in anchors:
        if str(a.get("name", "")).endswith("_front"):
            return a

    return anchors[0]


def build_shell_mount(
    cage: Dict[str, Any],
    shell_part: Dict[str, Any],
) -> Dict[str, Any]:
    name = str(shell_part.get("name") or f"shell_{uuid.uuid4().hex[:8]}")
    mount_zone = str(shell_part.get("mount_zone") or shell_part.get("zone") or "chest")

    zone = _find_zone(cage, mount_zone)
    if not zone:
        raise ValueError(f"Shell mount zone not found: {mount_zone}")

    anchor = _find_anchor(zone, shell_part.get("anchor"))

    zone_center = zone.get("center", [0, 0, 0])
    zone_scale = zone.get("scale", [1, 1, 1])

    anchor_position = anchor.get("position") if anchor else zone_center
    anchor_normal = anchor.get("normal") if anchor else [0, 0, 1]

    surface_offset = float(shell_part.get("surface_offset", 0.04))
    offset = shell_part.get("offset", [0, 0, 0])

    final_position = [
        float(anchor_position[0]) + float(anchor_normal[0]) * surface_offset + float(offset[0]),
        float(anchor_position[1]) + float(anchor_normal[1]) * surface_offset + float(offset[1]),
        float(anchor_position[2]) + float(anchor_normal[2]) * surface_offset + float(offset[2]),
    ]

    return {
        "id": f"mount_{uuid.uuid4().hex[:12]}",
        "name": name,
        "type": "shell_mount",
        "mount_zone": mount_zone,
        "anchor": anchor,
        "position": final_position,
        "normal": anchor_normal,
        "rotation": shell_part.get("rotation", zone.get("rotation", [0, 0, 0])),
        "scale": shell_part.get("scale", zone_scale),
        "shape": shell_part.get("shape", "shell_plate"),
        "material": shell_part.get("material", "shell_default"),
        "surface_offset": surface_offset,
        "follow_cage": bool(shell_part.get("follow_cage", True)),
        "visible": bool(shell_part.get("visible", True)),
        "metadata": {
            "rule": "shell mounts on cage surface, does not replace cage",
            "source_shell_part": shell_part,
        },
    }


def build_shell_mounts(
    cage: Dict[str, Any],
    shell_parts: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    shell_parts = shell_parts or _default_humanoid_shell_parts(cage)

    mounts = []
    errors = []

    for part in shell_parts:
        try:
            mounts.append(build_shell_mount(cage, part))
        except Exception as e:
            errors.append({
                "part": part,
                "error": str(e),
            })

    return {
        "ok": len(errors) == 0,
        "version": "universal_shell_mount_v1",
        "cage_id": cage.get("cage_id"),
        "mount_count": len(mounts),
        "error_count": len(errors),
        "mounts": mounts,
        "errors": errors,
        "rule": "mounted shell layer only; cage and cage texture remain untouched",
    }


def _default_humanoid_shell_parts(cage: Dict[str, Any]) -> List[Dict[str, Any]]:
    zone_names = {z.get("name") for z in cage.get("zones", [])}

    parts = []

    if "chest" in zone_names:
        parts.append({
            "name": "chest_shell",
            "mount_zone": "chest",
            "anchor": "chest_front",
            "shape": "curved_plate",
            "surface_offset": 0.045,
            "material": "shell_default",
        })

    if "pelvis" in zone_names:
        parts.append({
            "name": "pelvis_shell",
            "mount_zone": "pelvis",
            "anchor": "pelvis_front",
            "shape": "curved_plate",
            "surface_offset": 0.04,
            "material": "shell_default",
        })

    if "head" in zone_names:
        parts.append({
            "name": "head_shell",
            "mount_zone": "head",
            "anchor": "head_front",
            "shape": "face_shell",
            "surface_offset": 0.035,
            "material": "cage_texture",
        })

    return parts


def save_shell_mounts(shell_mount_result: Dict[str, Any], job_dir: str) -> Dict[str, Any]:
    out_dir = Path(job_dir) / "shell_mounts"
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / "shell_mounts.json"
    path.write_text(json.dumps(shell_mount_result, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "shell_mounts_path": str(path),
        "shell_mounts": shell_mount_result,
    }