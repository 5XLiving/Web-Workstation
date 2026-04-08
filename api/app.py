from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.xyz_routes import router as xyz_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API is running"}

app.include_router(xyz_router, prefix="/api/xyz/v1", tags=["xyz"])

print("[DEBUG] Route registration complete.")
