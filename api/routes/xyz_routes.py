"""
xyz_routes.py

API routes for XYZ modular system.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from api.services.xyz_blueprint_generator import generate_blueprint_from_profile
from api.services.xyz_construct_service import construct_from_blueprint
from api.services.xyz_preview_service import prepare_preview

router = APIRouter()


@router.get("/health")
async def health():
    """
    Health check for XYZ API.
    """
    return JSONResponse({"ok": True, "message": "XYZ API healthy"})


@router.post("/blueprint/generate")
async def generate_blueprint(request: Request):
    """
    Generate a blueprint from profile/mask, bounds, and preset.
    Expects JSON: { profile, bounds, preset }
    """
    try:
        data = await request.json()
        profile = data.get("profile", {})
        bounds = data.get("bounds", {})
        preset = data.get("preset", "generic_object")

        blueprint = generate_blueprint_from_profile(profile, bounds, preset)
        return JSONResponse(blueprint)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blueprint generation failed: {str(e)}")


@router.post("/construct/from-blueprint")
async def construct_from_blueprint_route(request: Request):
    """
    Construct chamber steps from blueprint.
    Expects JSON: { blueprint }
    """
    try:
        data = await request.json()
        blueprint = data.get("blueprint")

        if blueprint is None:
            raise HTTPException(status_code=400, detail="blueprint must be provided.")

        result = construct_from_blueprint(blueprint)
        return JSONResponse(result)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Construct failed: {str(e)}")


@router.post("/preview/render")
async def preview_render(request: Request):
    """
    Render a preview for .ply / mesh / point cloud / splat.
    Expects JSON: { preview_data, preview_type }
    """
    try:
        data = await request.json()
        preview_data = data.get("preview_data")
        preview_type = data.get("preview_type", "mesh")

        result = prepare_preview(preview_data, preview_type)
        return JSONResponse(result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview render failed: {str(e)}")
