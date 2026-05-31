from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

from backend.services.universal_cage_builder_service import build_universal_cage
from backend.services.universal_cage_diamond_grid_service import add_diamond_grid_to_cage


router = APIRouter(
    prefix="/api/universal-cage-diamond",
    tags=["universal-cage-diamond"],
)


class DiamondCageRequest(BaseModel):
    asset_type: str = "prop"
    cage_type: str = "universal_prop"
    source_template: Optional[Dict[str, Any]] = None
    detect: Optional[Dict[str, Any]] = None
    rows: int = 8
    cols: int = 8


@router.post("/build")
async def build_diamond_cage(req: DiamondCageRequest):
    try:
        cage = build_universal_cage(
            asset_type=req.asset_type,
            cage_type=req.cage_type,
            source_template=req.source_template or {},
            detect=req.detect or {},
        )

        diamond_cage = add_diamond_grid_to_cage(
            cage,
            rows=req.rows,
            cols=req.cols,
        )

        return {
            "ok": True,
            "mode": "universal_diamond_cage",
            "cage": diamond_cage,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "ok": False,
                "msg": "diamond_cage_build_failed",
                "error": str(e),
            },
        )