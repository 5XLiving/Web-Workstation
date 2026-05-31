from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
from pathlib import Path

from backend.services.universal_asset_builder_service import (
    build_universal_asset_from_image
)

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "storage" / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def public_output_url(job_id: str, filename: str):
    return f"/outputs/{job_id}/{filename}"


@router.post("/api/auto-asset/generate-from-image")
async def generate_from_image(
    image: UploadFile = File(...)
):
    try:
        job_id = uuid.uuid4().hex

        job_dir = OUTPUT_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        image_path = job_dir / image.filename

        with open(image_path, "wb") as f:
            f.write(await image.read())

        result = build_universal_asset_from_image(str(image_path))

        return {
            "ok": True,
            "job_id": job_id,
            "result": result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )