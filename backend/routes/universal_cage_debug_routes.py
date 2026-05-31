from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid
import traceback

from backend.services.universal_cage_detect_display_service import build_debug_cage_from_image
from backend.services.universal_multiview_service import create_multiview_from_image

router = APIRouter(prefix="/api/universal-cage", tags=["universal-cage"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = PROJECT_ROOT / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/debug-detect")
async def debug_detect_cage(image: UploadFile = File(...)):
    try:
        job_id = uuid.uuid4().hex
        job_dir = UPLOAD_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        image_path = job_dir / image.filename

        with image_path.open("wb") as f:
            shutil.copyfileobj(image.file, f)

        multiview = create_multiview_from_image(
            image_path=str(image_path),
            job_dir=str(job_dir),
            detect={},
        )

        result = build_debug_cage_from_image(
            image_path=multiview["views"]["front"]["path"],
            job_dir=str(job_dir),
        )

        result["job_id"] = job_id
        result["uploaded_filename"] = image.filename
        result["multiview"] = multiview

        return result

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "ok": False,
                "error": str(e),
                "stage": "universal_cage_debug_detect",
            },
        )