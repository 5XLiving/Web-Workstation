from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.diamond_cage_glb_service import build_diamond_cage_glb


router = APIRouter(
    prefix="/api/diamond-cage-glb",
    tags=["diamond-cage-glb"],
)


class DiamondCageGlbRequest(BaseModel):
    bake_job_id: str
    output_name: str = "diamond_cage_textured.glb"


@router.post("/build")
async def build_glb(req: DiamondCageGlbRequest):
    try:
        return build_diamond_cage_glb(
            bake_job_id=req.bake_job_id,
            output_name=req.output_name,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "ok": False,
                "msg": "diamond_cage_glb_failed",
                "error": str(e),
            },
        )