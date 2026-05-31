from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from backend.services.procedural_builder_service import build_procedural_model_from_form

router = APIRouter()


class BuildFormRequest(BaseModel):
    build_form: Dict[str, Any]


@router.post("/generate-3d")
async def generate_3d_from_build_form(payload: BuildFormRequest):
    try:
        result = build_procedural_model_from_form(payload.build_form)

        return {
            "ok": True,
            "job_id": result["job_id"],
            "model_url": result["model_url"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))