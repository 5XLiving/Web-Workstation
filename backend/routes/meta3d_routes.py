from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import traceback
import uuid
from pathlib import Path

from backend.services.ai_shape_planner import create_shape_plan
from backend.services.universal_shape_builder import build_universal_model

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
    try:
        print("[META3D] generate_3d called")

        job_id = uuid.uuid4().hex
        job_dir = OUTPUT_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        cutout_path = job_dir / "cutout.png"

        with open(cutout_path, "wb") as f:
            f.write(await cutout_png.read())

        if cutout_mirror:
            mirror_path = job_dir / "cutout_mirror.png"
            with open(mirror_path, "wb") as f:
                f.write(await cutout_mirror.read())

        print("[META3D] files saved")
        print("[META3D] cutout_path =", cutout_path)

        plan = create_shape_plan(str(cutout_path))

        result = build_universal_model(
            plan=plan,
            output_dir=str(job_dir),
        )

        print("[META3D] result =", result)

        if not result:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": "Generator returned empty result",
                },
            )

        if isinstance(result, dict):
            model_glb = result.get("model_glb")
            style = result.get("style", "")
            source_image = result.get("source_image", "")
        else:
            model_glb = str(result)
            style = ""
            source_image = ""

        if not model_glb:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": "model_glb missing from result",
                    "result": result,
                },
            )

        filename = Path(model_glb).name

        return {
            "ok": True,
            "job_id": job_id,
            "model_url": public_output_url(job_id, filename),
            "style": style,
            "source_image": source_image,
        }

    except Exception as e:
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": str(e),
                "traceback": traceback.format_exc(),
            },
        )