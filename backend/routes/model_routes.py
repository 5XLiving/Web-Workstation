from backend.config import load_env
load_env()

import os
import uuid
import traceback
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse

from backend.services import triposr_service, image_service

router = APIRouter()


def _pick_upload(*uploads):
    for upload in uploads:
        if upload is not None and getattr(upload, "filename", None):
            return upload
    return None


def _to_public_output_url(request: Request, value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    value = str(value).strip()
    if not value:
        return None

    if value.startswith("http://") or value.startswith("https://"):
        return value

    base_url = str(request.base_url).rstrip("/")

    if value.startswith("/outputs/"):
        return f"{base_url}{value}"

    if value.startswith("outputs/"):
        return f"{base_url}/{value}"

    outputs_dir = Path(__file__).resolve().parents[1] / "storage" / "outputs"

    try:
        p = Path(value)
        if p.is_absolute():
            rel = p.resolve().relative_to(outputs_dir.resolve())
            return f"{base_url}/outputs/{str(rel).replace('\\', '/')}"
    except Exception:
        pass

    if any(value.lower().endswith(ext) for ext in [".glb", ".gltf", ".obj", ".ply"]):
        return f"{base_url}/outputs/{Path(value).name}"

    return None


def _normalize_generation_result(request: Request, image_id: str, result):
    if not isinstance(result, dict):
        return {
            "ok": False,
            "image_id": image_id,
            "error": "3D service returned invalid response format.",
            "message": "Failed to process 3D generation request.",
        }

    payload = dict(result)
    payload.setdefault("ok", True)
    payload.setdefault("image_id", image_id)

    # Keep existing direct URLs if service already returns them
    model_url = (
        payload.get("model_url")
        or payload.get("glb_url")
        or payload.get("obj_url")
        or payload.get("preview_url")
    )

    # If service returns file paths instead of URLs, convert them
    if not model_url:
        path_candidates = [
            payload.get("model_path"),
            payload.get("glb_path"),
            payload.get("obj_path"),
            payload.get("preview_path"),
            payload.get("output_path"),
            payload.get("file_path"),
            payload.get("mesh_path"),
        ]
        for candidate in path_candidates:
            public_url = _to_public_output_url(request, candidate)
            if public_url:
                model_url = public_url
                break

    if model_url:
        ext = Path(model_url.split("?")[0]).suffix.lower()
        if ext == ".glb":
            payload["glb_url"] = model_url
        elif ext == ".obj":
            payload["obj_url"] = model_url
        else:
            payload["model_url"] = model_url

        payload.setdefault("model_url", model_url)
        payload["status"] = payload.get("status") or "completed"

    return payload


@router.post("/generate-3d")
async def generate_3d_endpoint(
    request: Request,
    image_id: Optional[str] = Form(None),
    cutout_png: Optional[UploadFile] = File(None),

    # Accept the fields your frontend actually sends
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    cutout: Optional[UploadFile] = File(None),
    image_file: Optional[UploadFile] = File(None),
):
    try:
        upload = _pick_upload(cutout_png, file, image, cutout, image_file)

        if upload is None:
            return JSONResponse(
                {
                    "ok": False,
                    "error": "No cutout PNG uploaded.",
                    "message": "Expected one of: cutout_png, file, image, cutout, image_file",
                },
                status_code=422,
            )

        if not image_id:
            image_id = uuid.uuid4().hex

        cutout_path = image_service.save_uploaded_cutout(upload, image_id)
        result = triposr_service.generate_3d_from_cutout(image_id, cutout_path)

        payload = _normalize_generation_result(request, image_id, result)

        if not payload.get("ok", False):
            return JSONResponse(payload, status_code=500)

        return JSONResponse(payload)

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


@router.get("/job-result/{job_id}")
async def job_result_endpoint(request: Request, job_id: str):
    """
    Optional support for queued workflows.
    This works only if triposr_service has get_job_result(job_id).
    """
    try:
        if not hasattr(triposr_service, "get_job_result"):
            return JSONResponse(
                {
                    "ok": False,
                    "job_id": job_id,
                    "error": "triposr_service.get_job_result() not implemented.",
                    "message": "Queued job lookup is not available in the current backend.",
                },
                status_code=404,
            )

        result = triposr_service.get_job_result(job_id)

        if not result:
            return JSONResponse(
                {
                    "ok": False,
                    "job_id": job_id,
                    "error": "Job not found.",
                },
                status_code=404,
            )

        image_id = result.get("image_id") or job_id
        payload = _normalize_generation_result(request, image_id, result)
        payload["job_id"] = result.get("job_id", job_id)

        return JSONResponse(payload)

    except Exception as e:
        tb = traceback.format_exc()
        return JSONResponse(
            {
                "ok": False,
                "job_id": job_id,
                "error": str(e),
                "trace": tb,
                "message": "Failed to fetch 3D job result.",
            },
            status_code=500,
        )
