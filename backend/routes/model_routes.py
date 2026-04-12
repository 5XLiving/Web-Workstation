
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from backend.services import triposr_service, image_service
import traceback

router = APIRouter()

@router.post("/generate-3d")
async def generate_3d_endpoint(
	image_id: str = Form(...),
	cutout_png: UploadFile = File(...)
):
	try:
		# Save uploaded cutout image
		cutout_path = image_service.save_uploaded_cutout(cutout_png, image_id)
		# Call TripoSR placeholder service
		result = triposr_service.generate_3d_from_cutout(image_id, cutout_path)
		return JSONResponse(result)
	except Exception as e:
		tb = traceback.format_exc()
		return JSONResponse({
			"ok": False,
			"error": str(e),
			"trace": tb,
			"message": "Failed to process 3D generation request."
		}, status_code=500)
