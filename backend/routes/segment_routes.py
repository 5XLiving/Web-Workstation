
import os
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from backend.services import segment_service, image_service

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.get("/__segment_ping")
async def __segment_ping():
    return {"ok": True, "route": "segment_routes"}


@router.post("/")
async def segment_endpoint(image: UploadFile = File(...)):
    try:
        image_bytes = await image.read()
        image_id = image_service.generate_image_id()

        original_name = image.filename or "upload.png"
        ext = os.path.splitext(original_name)[-1].lower() or ".png"
        filename = f"{image_id}{ext}"
        upload_path = os.path.join(UPLOAD_DIR, filename)

        with open(upload_path, "wb") as f:
            f.write(image_bytes)

        try:
            result = segment_service.segment_main_object(upload_path)
        except ModuleNotFoundError as e:
            return JSONResponse(
                {"ok": False, "error": f"Missing dependency: {e.name}"},
                status_code=500,
            )
        except Exception as e:
            return JSONResponse(
                {"ok": False, "error": f"Segmentation failed: {str(e)}"},
                status_code=500,
            )

        result["ok"] = True
        result["image_id"] = image_id
        return JSONResponse(result)

    except Exception as e:
        import traceback
        import sys
        tb_str = traceback.format_exc()
        print(f"[SEGMENT] exception: {e}", file=sys.stderr)
        print(tb_str, file=sys.stderr)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
