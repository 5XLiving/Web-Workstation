from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from backend.services.world_fixture_builder_service import build_world_fixture


router = APIRouter()


class WorldFixtureRequest(BaseModel):
    fixture_type: str = Field(..., description="tree, rock, bridge, table, chair, building, hill, etc")
    style: str = Field(default="lowpoly", description="lowpoly, stylized, simple")
    count: int = Field(default=1, ge=1, le=50)
    seed: Optional[int] = None
    options: Dict[str, Any] = Field(default_factory=dict)


@router.post("/generate")
async def generate_world_fixture(req: WorldFixtureRequest):
    try:
        result = build_world_fixture(
            fixture_type=req.fixture_type,
            style=req.style,
            count=req.count,
            seed=req.seed,
            options=req.options,
        )

        return {
            "ok": True,
            "type": "world_fixture",
            "fixture_type": req.fixture_type,
            "style": req.style,
            "count": req.count,
            "result": result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "ok": False,
                "error": str(e),
            },
        )
