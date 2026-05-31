from pathlib import Path
import uuid
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form

from backend.services.asset_router_service import route_asset_from_image
from backend.services.universal_model_builder_service import build_universal_model

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "storage" / "outputs"
UPLOAD_DIR = PROJECT_ROOT / "storage" / "uploads"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def attach_glb_models(result):
    assets = result.get("assets", [])

    for asset in assets:
        plan = asset.get("plan")
        if not plan:
            continue

        job_id = uuid.uuid4().hex
        job_dir = OUTPUT_DIR / job_id

        model_result = build_universal_model(plan=plan, output_dir=str(job_dir))

        asset["job_id"] = job_id
        asset["model_glb"] = model_result.get("model_glb")
        asset["model_url"] = f"/outputs/{job_id}/model.glb"
        asset["model_result"] = model_result

    if assets:
        result["job_id"] = assets[0].get("job_id")
        result["model_url"] = assets[0].get("model_url")
        result["model_glb"] = assets[0].get("model_glb")

    return result


@router.post("/generate")
async def generate_universal_asset(
    image: UploadFile = File(...),
    style: str = Form(default="lowpoly"),
    count: int = Form(default=1),
    asset_type: Optional[str] = Form(default=None),
):
    try:
        upload_id = uuid.uuid4().hex
        upload_dir = UPLOAD_DIR / upload_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        image_path = upload_dir / (image.filename or "upload.png")

        with open(image_path, "wb") as f:
            f.write(await image.read())

        result = route_asset_from_image(
            image_path=str(image_path),
            style=style,
            count=count,
            manual_type=asset_type,
        )

        return attach_glb_models(result)

    except Exception as e:
        return {
            "ok": False,
            "error": "Universal asset route error",
            "message": str(e),
        }