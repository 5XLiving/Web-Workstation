
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.routes.segment_routes import router as segment_router
from backend.routes.model_routes import router as model_router


import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = FastAPI(title="XYZ Modular Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"ok": True, "message": "Workstation backend root"}

@app.get("/health")
def health():
    return {"ok": True, "message": "Workstation backend healthy"}

app.include_router(segment_router, prefix="/api/segment", tags=["segment"])
app.include_router(model_router, prefix="/api/model", tags=["model"])

# Serve outputs as static files
# Serve outputs as static files

outputs_dir = os.path.join(BASE_DIR, "storage", "outputs")
if not os.path.exists(outputs_dir):
    os.makedirs(outputs_dir, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=outputs_dir), name="outputs")

# Serve the frontend HTML at the required route
@app.get("/xyz_modular_mask_frontend.html")
def serve_xyz_modular_mask_frontend():
    frontend_path = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend', 'xyz_frontend_mask_shell.html'))
    if not os.path.exists(frontend_path):
        # Try absolute path from workspace root as fallback
        fallback_path = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'frontend', 'xyz_frontend_mask_shell.html'))
        if os.path.exists(fallback_path):
            frontend_path = fallback_path
    return FileResponse(frontend_path, media_type='text/html')




@app.get("/__which_app")
def which_app():
    return jsonify({"ok": True, "marker": "backend-app-clean"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
