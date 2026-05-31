from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import uuid
import traceback

from backend.services.final_mesh_service import build_final_mesh_from_image

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMP_DIR = PROJECT_ROOT / "storage" / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/generate")
async def generate_final_mesh(image: UploadFile = File(...)):
    try:
        safe_name = image.filename or "upload.png"
        temp_path = TEMP_DIR / f"{uuid.uuid4().hex}_{safe_name}"

        with open(temp_path, "wb") as f:
            f.write(await image.read())

        return build_final_mesh_from_image(str(temp_path))

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }