from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json
import uuid
import math

try:
    import trimesh
except Exception:
    trimesh = None


def _box_mesh(center, scale):
    if trimesh is None:
        return None

    mesh = trimesh.creation.box(extents=scale)
    mesh.apply_translation(center)
    return mesh


def _sphere_mesh(center, scale):
    if trimesh is None:
        return None

    mesh = trimesh.creation.uv_sphere(radius=0.5, count=[24, 12])
    mesh.apply_scale(scale)
    mesh.apply_translation(center)
    return mesh


def _zone_mesh(zone: Dict[str, Any]):
    shape = str(zone.get("shape", "ellipsoid")).lower()
    center = zone.get("center", [0, 0, 0])
    scale = zone.get("scale", [1, 1, 1])

    if shape in ["box", "cube", "shell_plate"]:
        return _box_mesh(center, scale)

    return _sphere_mesh(center, scale)


def _mount_mesh(mount: Dict[str, Any]):
    if trimesh is None:
        return None

    position = mount.get("position", [0, 0, 0])
    scale = mount.get("scale", [1, 1, 1])
    shape = str(mount.get("shape", "shell_plate")).lower()

    plate_scale = [
        max(0.04, float(scale[0]) * 0.55),
        max(0.025, float(scale[1]) * 0.18),
        max(0.04, float(scale[2]) * 0.08),
    ]

    if "face" in shape:
        plate_scale = [
            max(0.08, float(scale[0]) * 0.55),
            max(0.08, float(scale[1]) * 0.55),
            max(0.025, float(scale[2]) * 0.08),
        ]

    mesh = trimesh.creation.box(extents=plate_scale)
    mesh.apply_translation(position)
    return mesh


def build_universal_layered_scene_package(
    cage: Dict[str, Any],
    texture_result: Optional[Dict[str, Any]] = None,
    shell_mount_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "ok": True,
        "version": "universal_layered_scene_v1",
        "scene_id": f"scene_{uuid.uuid4().hex[:12]}",
        "layers": {
            "skeleton": {
                "enabled": cage.get("movement_type") == "rigged",
                "rule": "movement frame only",
            },
            "cage": {
                "enabled": True,
                "cage_id": cage.get("cage_id"),
                "cage_type": cage.get("cage_type"),
                "zones": cage.get("zones", []),
                "rule": "body volume and surface control",
            },
            "cage_texture": {
                "enabled": bool(texture_result),
                "texture_path": texture_result.get("cage_texture_path") if texture_result else None,
                "uv_map_path": texture_result.get("uv_map_path") if texture_result else None,
                "rule": "replica texture belongs to cage",
            },
            "shell_mounts": {
                "enabled": bool(shell_mount_result),
                "mounts": shell_mount_result.get("mounts", []) if shell_mount_result else [],
                "rule": "shell mounts above cage and does not merge into cage",
            },
        },
        "export_rule": "final output combines layers but preserves cage/texture/shell separation",
    }


def export_universal_layered_glb(
    cage: Dict[str, Any],
    job_dir: str,
    texture_result: Optional[Dict[str, Any]] = None,
    shell_mount_result: Optional[Dict[str, Any]] = None,
    filename: str = "universal_layered_model.glb",
) -> Dict[str, Any]:
    job_path = Path(job_dir)
    out_dir = job_path / "layered_glb"
    out_dir.mkdir(parents=True, exist_ok=True)

    scene_package = build_universal_layered_scene_package(
        cage=cage,
        texture_result=texture_result,
        shell_mount_result=shell_mount_result,
    )

    scene_json_path = out_dir / "universal_layered_scene.json"
    scene_json_path.write_text(json.dumps(scene_package, indent=2), encoding="utf-8")

    glb_path = out_dir / filename

    if trimesh is None:
        fallback_path = out_dir / "README_NO_TRIMESH.txt"
        fallback_path.write_text(
            "trimesh is not installed, so GLB was not exported. "
            "Scene package JSON was generated successfully.",
            encoding="utf-8",
        )
        return {
            "ok": False,
            "message": "trimesh not installed; scene package generated only",
            "scene_json_path": str(scene_json_path),
            "glb_path": None,
        }

    scene = trimesh.Scene()

    for zone in cage.get("zones", []):
        mesh = _zone_mesh(zone)
        if mesh is not None:
            scene.add_geometry(mesh, node_name=f"cage_{zone.get('name')}")

    if shell_mount_result:
        for mount in shell_mount_result.get("mounts", []):
            mesh = _mount_mesh(mount)
            if mesh is not None:
                scene.add_geometry(mesh, node_name=f"shell_{mount.get('name')}")

    scene.export(str(glb_path))

    return {
        "ok": True,
        "message": "Universal layered GLB exported",
        "scene_json_path": str(scene_json_path),
        "glb_path": str(glb_path),
        "texture_path": texture_result.get("cage_texture_path") if texture_result else None,
        "rule": "GLB preview exported; source layers remain separate in JSON",
    }