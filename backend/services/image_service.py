import os
import json
import base64
import uuid
from io import BytesIO

from fastapi import UploadFile
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "storage", "uploads"))
OUTPUTS_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "storage", "outputs"))

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)


def load_image(path: str) -> Image.Image:
    return Image.open(path)


def save_uploaded_cutout(uploaded_file: UploadFile, image_id: str) -> str:
    filename = f"cutout_{image_id}.png"
    file_path = os.path.join(UPLOADS_DIR, filename)

    uploaded_file.file.seek(0)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.file.read())

    return file_path


def create_output_folder(job_id: str) -> str:
    job_dir = os.path.join(OUTPUTS_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    return job_dir


def write_json_metadata(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def normalize_path(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


def save_png(img: Image.Image, path: str):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    img.save(path, format="PNG")


def image_to_base64(img: Image.Image) -> str:
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def generate_image_id() -> str:
    return uuid.uuid4().hex
