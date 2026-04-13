from backend.config import load_env
load_env()

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routes.segment_routes import router as segment_router
from backend.routes.model_routes import router as model_router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="XYZ Modular Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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


outputs_dir = os.path.join(BASE_DIR, "storage", "outputs")
os.makedirs(outputs_dir, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=outputs_dir), name="outputs")


@app.get("/xyz_modular_mask_frontend.html")
def serve_xyz_modular_mask_frontend():
    candidate_paths = [
        os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "xyz_frontend_mask_shell.html")),
        os.path.abspath(os.path.join(BASE_DIR, "..", "..", "frontend", "xyz_frontend_mask_shell.html")),
    ]

    for frontend_path in candidate_paths:
        if os.path.exists(frontend_path):
            return FileResponse(frontend_path, media_type="text/html")

    raise HTTPException(status_code=404, detail="Frontend HTML not found")


@app.get("/__which_app")
def which_app():
    return {"ok": True, "marker": "backend-app-clean"}


if __name__ == "__main__":
    uvicorn.run("backend.app:app", host="0.0.0.0", port=5000, reload=True)
