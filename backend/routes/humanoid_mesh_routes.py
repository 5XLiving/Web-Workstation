from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import shutil
import traceback

from backend.services.humanoid_mesh_skin_service import build_humanoid_mesh_skin

router = APIRouter(prefix="/api/humanoid-mesh", tags=["humanoid-mesh"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_DIR = PROJECT_ROOT / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/generate")
async def generate_humanoid_mesh(image: UploadFile = File(...)):
    try:
        job_id = uuid.uuid4().hex
        job_dir = UPLOAD_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        image_path = job_dir / image.filename

        with image_path.open("wb") as f:
            shutil.copyfileobj(image.file, f)

        result = build_humanoid_mesh_skin(str(image_path))

        return {
            "ok": True,
            "message": "Humanoid mesh skin generated",
            "result": result,
            "render3DPreview": {
                "modelUrl": result.get("model_url")
            }
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Humanoid mesh generation failed: {str(e)}"
        )
