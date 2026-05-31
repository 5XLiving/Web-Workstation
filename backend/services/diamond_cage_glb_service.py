from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import trimesh


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS_DIR = PROJECT_ROOT / "storage" / "outputs"


def _public_url(job_id: str, filename: str) -> str:
    return f"/outputs/{job_id}/{filename}"


def _load_texture_map(bake_job_id: str) -> Dict[str, Any]:
    p = OUTPUTS_DIR / bake_job_id / "diamond_texture_map.json"
    if not p.exists():
        raise FileNotFoundError(f"Missing diamond_texture_map.json for {bake_job_id}")
    return json.loads(p.read_text(encoding="utf-8"))


def _make_uv_sphere_mesh(
    radius_x: float = 1.0,
    radius_y: float = 1.4,
    radius_z: float = 0.65,
    rows: int = 16,
    cols: int = 32,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    vertices: List[List[float]] = []
    uvs: List[List[float]] = []
    faces: List[List[int]] = []

    for r in range(rows + 1):
        v = r / rows
        theta = math.pi * v

        for c in range(cols):
            u = c / cols
            phi = 2 * math.pi * u

            x = radius_x * math.sin(theta) * math.cos(phi)
            y = radius_y * math.cos(theta)
            z = radius_z * math.sin(theta) * math.sin(phi)

            vertices.append([x, y, z])
            uvs.append([u, 1.0 - v])

    for r in range(rows):
        for c in range(cols):
            a = r * cols + c
            b = r * cols + ((c + 1) % cols)
            d = (r + 1) * cols + c
            e = (r + 1) * cols + ((c + 1) % cols)

            faces.append([a, d, b])
            faces.append([b, d, e])

    return (
        np.asarray(vertices, dtype=np.float64),
        np.asarray(faces, dtype=np.int64),
        np.asarray(uvs, dtype=np.float64),
    )


def build_diamond_cage_glb(
    bake_job_id: str,
    output_name: str = "diamond_cage_textured.glb",
) -> Dict[str, Any]:
    bake_dir = OUTPUTS_DIR / bake_job_id
    if not bake_dir.exists():
        raise FileNotFoundError(f"Bake job not found: {bake_job_id}")

    texture_path = bake_dir / "diamond_texture_atlas.png"
    if not texture_path.exists():
        raise FileNotFoundError(f"Missing diamond_texture_atlas.png for {bake_job_id}")

    texture_map = _load_texture_map(bake_job_id)

    vertices, faces, uvs = _make_uv_sphere_mesh()

    mesh = trimesh.Trimesh(
        vertices=vertices,
        faces=faces,
        process=False,
    )

    material = trimesh.visual.material.PBRMaterial(
        baseColorTexture=str(texture_path),
        metallicFactor=0.0,
        roughnessFactor=0.75,
    )

    mesh.visual = trimesh.visual.TextureVisuals(
        uv=uvs,
        image=str(texture_path),
        material=material,
    )

    glb_path = bake_dir / output_name
    mesh.export(glb_path)

    preview_json = {
        "ok": True,
        "type": "diamond_cage_glb",
        "bake_job_id": bake_job_id,
        "source_multiview_job_id": texture_map.get("source_multiview_job_id"),
        "glb_url": _public_url(bake_job_id, output_name),
        "texture_atlas_url": _public_url(bake_job_id, "diamond_texture_atlas.png"),
        "map_url": _public_url(bake_job_id, "diamond_texture_map.json"),
        "rule": "First proof GLB: universal ellipsoid cage using baked diamond atlas.",
    }

    info_path = bake_dir / "diamond_cage_glb.json"
    info_path.write_text(json.dumps(preview_json, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "mode": "diamond_cage_glb",
        "bake_job_id": bake_job_id,
        "glb_url": _public_url(bake_job_id, output_name),
        "glb_path": str(glb_path),
        "texture_atlas_url": _public_url(bake_job_id, "diamond_texture_atlas.png"),
        "info_url": _public_url(bake_job_id, "diamond_cage_glb.json"),
    }