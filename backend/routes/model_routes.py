from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from backend.services import triposr_service, image_service
import traceback

router = APIRouter()


@router.post("/generate-3d")
async def generate_3d_endpoint(
    image_id: str = Form(...),
    cutout_png: UploadFile = File(...),
):
    try:
        cutout_path = image_service.save_uploaded_cutout(cutout_png, image_id)
        result = triposr_service.generate_3d_from_cutout(image_id, cutout_path)

        if not isinstance(result, dict):
            return JSONResponse(
                {
                    "ok": False,
                    "error": "3D service returned invalid response format.",
                    "message": "Failed to process 3D generation request.",
                },
                status_code=500,
            )

        result.setdefault("ok", True)
        result.setdefault("image_id", image_id)
        return JSONResponse(result)

    except Exception as e:
        tb = traceback.format_exc()
        return JSONResponse(
            {
                "ok": False,
                "error": str(e),
                "trace": tb,
                "message": "Failed to process 3D generation request.",
            },
            status_code=500,
        )
