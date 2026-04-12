

import os
import base64
import uuid
from PIL import Image
from io import BytesIO

import os
import json
from fastapi import UploadFile

def load_image(path: str) -> Image.Image:
	return Image.open(path)
def save_uploaded_cutout(uploaded_file: UploadFile, image_id: str) -> str:
	"""
	Save uploaded cutout image to backend/storage/uploads/ with a unique name.
	Returns the absolute file path.
	"""
	uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../storage/uploads'))
	os.makedirs(uploads_dir, exist_ok=True)
	filename = f"cutout_{image_id}.png"
	file_path = os.path.join(uploads_dir, filename)
	with open(file_path, "wb") as f:
		content = uploaded_file.file.read()
		f.write(content)
	return file_path

def create_output_folder(job_id: str) -> str:
	outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../storage/outputs'))
	job_dir = os.path.join(outputs_dir, job_id)
	os.makedirs(job_dir, exist_ok=True)
	return job_dir

def write_json_metadata(path: str, data: dict):
	with open(path, 'w', encoding='utf-8') as f:
		json.dump(data, f, indent=2)

def normalize_path(path: str) -> str:
	return os.path.normpath(os.path.abspath(path))

def save_png(img: Image.Image, path: str):
	img.save(path, format='PNG')

def image_to_base64(img: Image.Image) -> str:
	buffered = BytesIO()
	img.save(buffered, format="PNG")
	return base64.b64encode(buffered.getvalue()).decode('utf-8')

def generate_image_id() -> str:
	return uuid.uuid4().hex
