from __future__ import annotations

from pathlib import Path
import shutil
import uuid
import traceback
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.services.universal_cage_builder_service import build_universal_cage
from backend.services.universal_cage_texture_service import build_universal_cage_texture
from backend.services.universal_shell_mount_service import build_shell_mounts, save_shell_mounts
from backend.services.universal_layered_glb_service import export_universal_layered_glb


router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS_DIR = PROJECT_ROOT / "storage" / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def _public_output_url(path: str) -> str:
    p = Path(path)
    try:
        rel = p.relative_to(OUTPUTS_DIR)
        return "/outputs/" + str(rel).replace("\\", "/")
    except Exception:
        return str(path)


def _save_upload(upload: UploadFile, folder: Path, filename: str) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    dst = folder / filename

    with dst.open("wb") as f:
        shutil.copyfileobj(upload.file, f)

    return dst


@router.post("/generate")
async def generate_universal_cage_model(
    front_image: UploadFile = File(...),
    back_image: Optional[UploadFile] = File(None),
    left_image: Optional[UploadFile] = File(None),
    right_image: Optional[UploadFile] = File(None),
    asset_type: str = Form("humanoid"),
    cage_type: str = Form("universal_humanoid"),
):
    try:
        job_id = uuid.uuid4().hex
        job_dir = OUTPUTS_DIR / job_id
        input_dir = job_dir / "input"
        job_dir.mkdir(parents=True, exist_ok=True)
        input_dir.mkdir(parents=True, exist_ok=True)

        front_path = _save_upload(front_image, input_dir, "front.png")

        back_path = None
        left_path = None
        right_path = None

        if back_image is not None:
            back_path = _save_upload(back_image, input_dir, "back.png")

        if left_image is not None:
            left_path = _save_upload(left_image, input_dir, "left.png")

        if right_image is not None:
            right_path = _save_upload(right_image, input_dir, "right.png")

        cage = build_universal_cage(
            asset_type=asset_type,
            cage_type=cage_type,
            source_template=None,
            detect={
                "source": "universal_cage_route",
                "has_front": True,
                "has_back": back_path is not None,
                "has_left": left_path is not None,
                "has_right": right_path is not None,
            },
        )

        texture_result = build_universal_cage_texture(
            cage=cage,
            job_dir=str(job_dir),
            front_image_path=str(front_path),
            back_image_path=str(back_path) if back_path else None,
            left_image_path=str(left_path) if left_path else None,
            right_image_path=str(right_path) if right_path else None,
            make_debug=True,
        )

        shell_mount_result = build_shell_mounts(cage=cage)
        shell_save = save_shell_mounts(shell_mount_result, str(job_dir))

        glb_result = export_universal_layered_glb(
            cage=cage,
            job_dir=str(job_dir),
            texture_result=texture_result,
            shell_mount_result=shell_mount_result,
            filename="universal_layered_model.glb",
        )

        glb_path = glb_result.get("glb_path")
        scene_json_path = glb_result.get("scene_json_path")

        return {
            "ok": True,
            "message": "Universal cage layered model generated",
            "job_id": job_id,
            "asset_type": asset_type,
            "cage_type": cage_type,

            "model_url": _public_output_url(glb_path) if glb_path else None,
            "glb_url": _public_output_url(glb_path) if glb_path else None,
            "final_model_url": _public_output_url(glb_path) if glb_path else None,

            "scene_json_url": _public_output_url(scene_json_path) if scene_json_path else None,
            "cage_texture_url": _public_output_url(texture_result.get("cage_texture_path")),
            "debug_texture_url": _public_output_url(texture_result.get("debug_texture_path")),
            "uv_map_url": _public_output_url(texture_result.get("uv_map_path")),
            "shell_mounts_url": _public_output_url(shell_save.get("shell_mounts_path")),

            "cage": cage,
            "texture_result": texture_result,
            "shell_mount_result": shell_mount_result,
            "glb_result": glb_result,

            "rule": "skeleton moves, cage shapes, texture wraps, shell mounts",
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "ok": False,
                "error": str(e),
                "trace": traceback.format_exc(),
            },
        )