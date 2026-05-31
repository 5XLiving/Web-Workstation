from pathlib import Path
from typing import Any, Dict, Optional
import shutil

import trimesh
import numpy as np
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "storage" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _avg_rgba(path):
    img = Image.open(path).convert("RGBA").resize((96, 96))
    arr = np.array(img)

    alpha = arr[:, :, 3] > 20
    if not alpha.any():
        return [120, 180, 255, 255]

    rgb = arr[:, :, :3][alpha].mean(axis=0).astype(int)
    return [int(rgb[0]), int(rgb[1]), int(rgb[2]), 255]


def _resolve_job_dir(
    job_dir: Optional[str] = None,
    job_id: Optional[str] = None,
) -> Path:
    if job_dir:
        return Path(job_dir)

    if job_id:
        return OUTPUT_DIR / str(job_id)

    return OUTPUT_DIR / "texture_preview"


def _extract_front_texture(
    views: Optional[Any] = None,
    image_path: Optional[str] = None,
) -> Optional[Path]:
    if isinstance(views, dict):
        for key in ["front", "image", "source", "front_path"]:
            value = views.get(key)
            if value and Path(str(value)).exists():
                return Path(str(value))

    if image_path and Path(str(image_path)).exists():
        return Path(str(image_path))

    return None


def make_material_from_texture(name: str, texture_path: str):
    color = _avg_rgba(texture_path)

    try:
        tex = Image.open(texture_path).convert("RGBA")
        return trimesh.visual.material.PBRMaterial(
            name=name,
            baseColorFactor=color,
            baseColorTexture=tex,
            metallicFactor=0.16,
            roughnessFactor=0.48,
        )
    except Exception:
        return trimesh.visual.material.SimpleMaterial(
            name=name,
            diffuse=color,
            ambient=color,
            specular=[70, 70, 70, 255],
        )


def make_material_from_color(name: str, color):
    return trimesh.visual.material.SimpleMaterial(
        name=name,
        diffuse=color,
        ambient=color,
        specular=[70, 70, 70, 255],
    )


def _apply_material(scene: trimesh.Scene, mat):
    for geom in scene.geometry.values():
        try:
            geom.visual.material = mat
        except Exception:
            pass
    return scene


def bake_multiview_to_scene(
    scene: trimesh.Scene,
    views: Optional[Any] = None,
    job_dir: Optional[str] = None,
    image_path: Optional[str] = None,
    asset_type: Optional[str] = None,
    job_id: Optional[str] = None,
    multiview: Optional[Any] = None,
    **kwargs,
):
    """
    Backward compatible:
        bake_multiview_to_scene(scene, views, job_dir)

    New compatible:
        bake_multiview_to_scene(scene=scene, multiview=..., image_path=..., asset_type=..., job_id=...)

    Returns dict with scene included, so final_mesh_service does not lose geometry.
    """

    if multiview is not None and views is None:
        views = multiview

    base_job_dir = _resolve_job_dir(job_dir=job_dir, job_id=job_id)
    texture_dir = base_job_dir / "textures"
    texture_dir.mkdir(parents=True, exist_ok=True)

    src = _extract_front_texture(views=views, image_path=image_path)

    if src is None:
        mat = make_material_from_color(
            "fallback_average_material",
            [90, 100, 120, 255],
        )
        _apply_material(scene, mat)

        return {
            "ok": True,
            "scene": scene,
            "baked_texture": None,
            "material": "fallback_average_material",
            "note": "No valid texture source found. Applied fallback material.",
        }

    baked_front = texture_dir / "baked_front.png"

    try:
        shutil.copy(src, baked_front)
    except Exception:
        Image.open(src).convert("RGBA").save(baked_front)

    mat = make_material_from_texture(
        "baked_multiview_material",
        str(baked_front),
    )

    _apply_material(scene, mat)

    return {
        "ok": True,
        "scene": scene,
        "baked_texture": str(baked_front),
        "material": "baked_multiview_material",
        "asset_type": asset_type,
    }