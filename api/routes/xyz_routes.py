"""
xyz_routes.py

API routes for XYZ modular system.
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from api.services.xyz_blueprint_generator import generate_blueprint_from_profile
from api.services.xyz_construct_service import construct_from_blueprint
from api.services.xyz_preview_service import prepare_preview


router = APIRouter()

@router.post("/blueprint/generate")
async def generate_blueprint(request: Request):
    """
    Generate a blueprint from profile/mask, bounds, and preset.
    Expects JSON: { profile, bounds, preset }
    """
    data = await request.json()
    profile = data.get("profile", {})
    bounds = data.get("bounds", {})
    preset = data.get("preset", "generic_object")
    blueprint = generate_blueprint_from_profile(profile, bounds, preset)
    return JSONResponse(blueprint)

@router.post("/construct/from-blueprint")
async def construct_from_blueprint_route(request: Request):
    """
    Construct chamber steps from blueprint.
    Expects JSON: { blueprint }
    """
    data = await request.json()
    blueprint = data.get("blueprint")
    result = construct_from_blueprint(blueprint)
    return JSONResponse(result)

@router.post("/preview/render")
async def preview_render(request: Request):
    """
    Render a preview for .ply/mesh/point cloud/splat.
    Expects JSON: { preview_data, preview_type }
    """
    try:
        data = await request.json()
        preview_data = data.get("preview_data")
        preview_type = data.get("preview_type", "ply")
        result = prepare_preview(preview_data, preview_type)
        return JSONResponse(result)
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))
