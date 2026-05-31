from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.diamond_texture_bake_service import bake_diamond_texture_atlas


router = APIRouter(
    prefix="/api/diamond-texture",
    tags=["diamond-texture"],
)


class DiamondBakeRequest(BaseModel):
    multiview_job_id: str
    atlas_size: int = 2048
    grid_rows: int = 8
    grid_cols: int = 8


@router.post("/bake")
async def bake_texture(req: DiamondBakeRequest):
    try:
        return bake_diamond_texture_atlas(
            multiview_job_id=req.multiview_job_id,
            atlas_size=req.atlas_size,
            grid_rows=req.grid_rows,
            grid_cols=req.grid_cols,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "ok": False,
                "msg": "diamond_texture_bake_failed",
                "error": str(e),
            },
        )