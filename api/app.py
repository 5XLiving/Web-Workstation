from fastapi import FastAPI
from api.routes.xyz_routes import router as xyz_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API is running"}

# Mount xyz_router with prefix
app.include_router(xyz_router, prefix="/api/xyz/v1")
print("[DEBUG] Route registration complete.\n")
