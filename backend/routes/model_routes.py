from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import uuid
from pathlib import Path
import traceback

from backend.services.modular_pet_service import generate_modular_pet

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "storage" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def public_output_url(job_id: str, filename: str) -> str:
    return f"/outputs/{job_id}/{filename}"


@router.post("/generate-3d")
async def generate_3d(
    image_id: str = Form(None),
    cutout_png: UploadFile = File(...),
    cutout_mirror: UploadFile = File(None),
):
    job_id = uuid.uuid4().hex
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    cutout_path = job_dir / "cutout.png"

    try:
        with open(cutout_path, "wb") as f:
            f.write(await cutout_png.read())

        result = generate_modular_pet(
            image_path=str(cutout_path),
            output_dir=str(job_dir),
        )

        return {
            "ok": True,
            "engine": "modular_pet_glb_cpu",
            "job_id": job_id,
            "image_id": image_id,
            "model_url": public_output_url(job_id, "model.glb"),
            "cutout_url": public_output_url(job_id, "cutout.png"),
            "files": result,
        }

    except Exception as e:
        error_path = job_dir / "error.txt"
        error_path.write_text(traceback.format_exc(), encoding="utf-8")
        raise HTTPException(status_code=500, detail=str(e))
