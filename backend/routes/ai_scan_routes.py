from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid

from backend.services.ai_scan_service import scan_image_to_build_form

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = PROJECT_ROOT / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/build-form")
async def build_form(image: UploadFile = File(...)):
    try:
        job_id = uuid.uuid4().hex
        suffix = Path(image.filename or "upload.png").suffix or ".png"
        img_path = UPLOAD_DIR / f"{job_id}{suffix}"

        img_path.write_bytes(await image.read())

        result = scan_image_to_build_form(str(img_path))
        result["job_id"] = job_id
        result["source_image"] = str(img_path)

        return {
            "ok": True,
            "job_id": job_id,
            "build_form": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))