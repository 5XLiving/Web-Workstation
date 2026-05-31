from backend.config import load_env
load_env()

import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routes.segment_routes import router as segment_router
from backend.routes.model_routes import router as model_router
from backend.routes.meta3d_routes import router as meta3d_router
from backend.routes import ai_scan_routes
from backend.routes import build_form_3d_routes
from backend.routes import world_fixture_routes
from backend.routes.universal_asset_routes import router as universal_asset_router
from backend.routes.auto_asset_routes import router as auto_asset_router
from backend.routes.humanoid_mesh_routes import router as humanoid_mesh_router
from backend.routes.final_mesh_routes import router as final_mesh_router
from backend.routes import universal_cage_routes
from backend.routes.universal_cage_debug_routes import router as universal_cage_debug_router
from backend.routes.universal_multiview_routes import router as universal_multiview_router
from backend.routes.universal_cage_diamond_grid_routes import router as universal_cage_diamond_grid_router
from backend.routes.multiview_storage_routes import router as multiview_storage_router
from backend.routes.diamond_texture_bake_routes import router as diamond_texture_bake_router
from backend.routes.diamond_cage_glb_routes import router as diamond_cage_glb_router


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "5000"))

FRONTEND_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "frontend"))
OUTPUTS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "storage", "outputs"))
UPLOADS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "storage", "uploads"))
STATIC_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "static"))
FRONTEND_ASSETS_DIR = os.path.join(FRONTEND_DIR, "assets")

os.makedirs(FRONTEND_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(FRONTEND_ASSETS_DIR, exist_ok=True)


app = FastAPI(
    title="5xLiving 3D Workstation Backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "ok": True,
        "message": "5xLiving 3D Workstation backend root",
        "engine": os.getenv("IMAGE3D_ENGINE", "meta3d"),
    }


@app.get("/health")
def health():
    return {
        "ok": True,
        "message": "5xLiving 3D Workstation backend healthy",
        "engine": os.getenv("IMAGE3D_ENGINE", "meta3d"),
    }


app.include_router(segment_router, prefix="/api/segment", tags=["segment"])
app.include_router(model_router, prefix="/api/model", tags=["model"])
app.include_router(meta3d_router, prefix="/api/meta3d", tags=["meta3d"])
app.include_router(humanoid_mesh_router)
app.include_router(auto_asset_router)
app.include_router(universal_cage_debug_router)
app.include_router(universal_multiview_router)
app.include_router(universal_cage_diamond_grid_router)
app.include_router(multiview_storage_router)
app.include_router(diamond_texture_bake_router)
app.include_router(diamond_cage_glb_router)


app.include_router(
    universal_cage_routes.router,
    prefix="/api/universal-cage",
    tags=["universal-cage"],
)

app.include_router(
    final_mesh_router,
    prefix="/api/final-mesh",
    tags=["final-mesh"],
)

app.include_router(
    ai_scan_routes.router,
    prefix="/api/scan",
    tags=["ai-scan"],
)

app.include_router(
    build_form_3d_routes.router,
    prefix="/api/build-form",
    tags=["build-form-3d"],
)

app.include_router(
    universal_asset_router,
    prefix="/api/universal-asset",
    tags=["universal-asset"],
)

app.include_router(
    world_fixture_routes.router,
    prefix="/api/world-fixture",
    tags=["world-fixture"],
)


app.mount(
    "/outputs",
    StaticFiles(directory=OUTPUTS_DIR),
    name="outputs",
)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOADS_DIR),
    name="uploads",
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)

app.mount(
    "/assets",
    StaticFiles(directory=FRONTEND_ASSETS_DIR),
    name="frontend_assets",
)


def _serve_frontend_file(filename: str):
    if not filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    normalized = os.path.normpath(filename)

    if normalized.startswith("..") or os.path.isabs(normalized):
        raise HTTPException(status_code=400, detail="Invalid filename")

    frontend_path = os.path.abspath(os.path.join(FRONTEND_DIR, normalized))

    if not frontend_path.startswith(FRONTEND_DIR):
        raise HTTPException(status_code=400, detail="Invalid frontend path")

    if os.path.exists(frontend_path):
        return FileResponse(frontend_path, media_type="text/html")

    print(f"[DEBUG] Frontend file not found: {frontend_path}")

    raise HTTPException(
        status_code=404,
        detail=f"Frontend HTML not found: {filename}",
    )


@app.get("/5xLiving_3D_Workstation.html")
def serve_5xliving_3d_workstation():
    return _serve_frontend_file("5xLiving_3D_Workstation.html")


@app.get("/xyz_modular_mask_frontend.html")
def serve_xyz_modular_mask_frontend():
    return _serve_frontend_file("xyz_modular_mask_frontend.html")


@app.get("/mask_frontend_backup.html")
def serve_mask_frontend_backup():
    return _serve_frontend_file("mask_frontend_backup.html")


@app.get("/mask_frontend_v2_backup.html")
def serve_mask_frontend_v2_backup():
    return _serve_frontend_file("mask_frontend_v2_backup.html")


@app.get("/procedural_mech_live.html")
def serve_procedural_mech_live():
    return _serve_frontend_file("procedural_mech_live.html")


@app.get("/xyz_frontend_mask_shell.html")
def serve_xyz_frontend_mask_shell():
    return _serve_frontend_file("xyz_frontend_mask_shell.html")


@app.get("/xyz_troubleshoot_logbook.html")
def serve_xyz_troubleshoot_logbook():
    return _serve_frontend_file("xyz_troubleshoot_logbook.html")


@app.get("/ai_modular_builder_test.html")
def serve_ai_modular_builder_test():
    return _serve_frontend_file("ai_modular_builder_test.html")


@app.get("/v2/universal_trade_builder_test.html")
def serve_universal_trade_builder_test():
    return _serve_frontend_file("v2/universal_trade_builder_test.html")


@app.get("/__which_app")
def which_app():
    return {
        "ok": True,
        "marker": "5xliving-3d-workstation-backend",
        "base_dir": BASE_DIR,
        "project_root": PROJECT_ROOT,
        "frontend_dir": FRONTEND_DIR,
        "outputs_dir": OUTPUTS_DIR,
        "uploads_dir": UPLOADS_DIR,
        "static_dir": STATIC_DIR,
        "host": APP_HOST,
        "port": APP_PORT,
        "engine": os.getenv("IMAGE3D_ENGINE", "meta3d"),
        "debug_fake_glb": os.getenv("DEBUG_USE_FAKE_GLB", "0"),
        "meta3d_repo": os.getenv("META3D_REPO", ""),
        "meta3d_python": os.getenv("META3D_PYTHON", ""),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=False,
    )