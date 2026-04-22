import os
import sys
from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import JSONResponse
from backend.services import segment_service, image_service

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()


@router.post("/")
async def segment_endpoint(request: Request, image: UploadFile = File(...)):
    try:
        print("[SEGMENT] route entered", file=sys.stderr)
        print(f"[SEGMENT] content-type: {request.headers.get('content-type')}", file=sys.stderr)
        try:
            form = await request.form()
            print(f"[SEGMENT] request.form keys: {list(form.keys())}", file=sys.stderr)
        except Exception as e:
            print(f"[SEGMENT] request.form() error: {e}", file=sys.stderr)
        print(f"[SEGMENT] image.filename: {getattr(image, 'filename', None)}", file=sys.stderr)
        print(f"[SEGMENT] image.content_type: {getattr(image, 'content_type', None)}", file=sys.stderr)
        print("[SEGMENT] before reading file", file=sys.stderr)
        image_bytes = await image.read()
        print(f"[SEGMENT] after reading file, bytes: {len(image_bytes)}", file=sys.stderr)
        image_id = image_service.generate_image_id()
        original_name = image.filename or "upload.png"
        ext = os.path.splitext(original_name)[-1].lower() or ".png"
        filename = f"{image_id}{ext}"
        upload_path = os.path.join(UPLOAD_DIR, filename)
        with open(upload_path, "wb") as f:
            f.write(image_bytes)
        print(f"[SEGMENT] before segment service call", file=sys.stderr)
        try:
            result = segment_service.segment_main_object(upload_path)
            print("[SEGMENT] after segment service call", file=sys.stderr)
        except ModuleNotFoundError as e:
            print(f"[SEGMENT] ModuleNotFoundError: {e}", file=sys.stderr)
            return JSONResponse(
                {"ok": False, "error": f"Missing dependency: {e.name}"},
                status_code=500,
            )
        except Exception as e:
            print(f"[SEGMENT] Exception in segment_main_object: {e}", file=sys.stderr)
            return JSONResponse(
                {"ok": False, "error": f"Segmentation failed: {str(e)}"},
                status_code=500,
            )
        print(f"[SEGMENT] before response return, result keys: {list(result.keys())}", file=sys.stderr)
        result["ok"] = True
        result["image_id"] = image_id
        return JSONResponse(result)
    except Exception as e:
        print(f"[SEGMENT] exception: {e}", file=sys.stderr)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
