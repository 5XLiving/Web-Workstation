from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.multiview_storage_service import (
    save_multiview_images,
    load_multiview_manifest,
)


router = APIRouter(
    prefix="/api/multiview",
    tags=["multiview-storage"],
)


class MultiviewSaveRequest(BaseModel):
    job_id: Optional[str] = None
    views: Dict[str, Any]


@router.post("/save")
async def save_multiview(req: MultiviewSaveRequest):
    try:
        result = save_multiview_images(
            views=req.views,
            job_id=req.job_id,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "ok": False,
                "msg": "multiview_save_failed",
                "error": str(e),
            },
        )


@router.get("/{job_id}")
async def get_multiview(job_id: str):
    try:
        manifest = load_multiview_manifest(job_id)

        return {
            "ok": True,
            "job_id": job_id,
            "manifest": manifest,
        }

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail={
                "ok": False,
                "msg": "multiview_manifest_not_found",
                "error": str(e),
            },
        )