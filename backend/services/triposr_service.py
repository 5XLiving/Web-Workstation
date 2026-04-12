

import os
import uuid
import shutil
import json
from datetime import datetime
from . import image_service

from pathlib import Path
import logging

def generate_3d_from_cutout(image_id: str, cutout_path: str) -> dict:
	job_id = uuid.uuid4().hex
	outputs_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../storage/outputs'))
	job_dir = os.path.join(outputs_root, job_id)
	os.makedirs(job_dir, exist_ok=True)

	# Logging: job folder creation
	logging.info(f"[3DGen] Created job folder: {job_dir}")

	# Copy cutout to job folder
	cutout_filename = f"cutout_{image_id}.png"
	job_cutout_path = os.path.join(job_dir, cutout_filename)
	shutil.copy2(cutout_path, job_cutout_path)
	logging.info(f"[3DGen] Saved cutout to: {job_cutout_path}")


	# --- REAL 3D GENERATION STEP ---
	# To enable the old test GLB fallback, set this debug flag to True:
	DEBUG_USE_FAKE_GLB = False  # Set True ONLY for local debug
	model_path = None
	if DEBUG_USE_FAKE_GLB:
		test_glb = os.path.abspath(os.path.join(os.path.dirname(__file__), '../storage/test_assets/sample.glb'))
		logging.info(f"[3DGen] test_glb resolved path: {test_glb}")
		if os.path.exists(test_glb):
			model_path = os.path.join(job_dir, "model.glb")
			shutil.copy2(test_glb, model_path)
			logging.info(f"[3DGen] Copied test GLB to: {model_path}")

	# --- REAL GENERATOR CALL GOES HERE ---
	# Example:
	# model_path = run_real_3d_generation(job_cutout_path, job_dir)
	# (job_cutout_path: PNG input, job_dir: output folder)

	if model_path and Path(model_path).exists():
		model_url = f"http://127.0.0.1:5000/outputs/{job_id}/{Path(model_path).name}"
		logging.info(f"[3DGen] Model available at: {model_url}")
		return {
			"ok": True,
			"job_id": job_id,
			"image_id": image_id,
			"status": "completed",
			"model_url": model_url,
			"preview_url": model_url,
		}

	# If not available, return clear not_implemented state
	logging.warning(f"[3DGen] Model generation not integrated yet for job {job_id}.")
	return {
		"ok": False,
		"job_id": job_id,
		"image_id": image_id,
		"status": "not_implemented",
		"message": "Real image-to-3D generation is not integrated yet."
	}
