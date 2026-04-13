```python id="9jq6cg"
import os
import uuid
import shutil
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def _outputs_root() -> str:
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "storage", "outputs")
    )
    os.makedirs(root, exist_ok=True)
    return root


def _job_dir(job_id: str) -> str:
    path = os.path.join(_outputs_root(), job_id)
    os.makedirs(path, exist_ok=True)
    return path


def _public_output_url(job_id: str, filename: str) -> str:
    return f"/outputs/{job_id}/{filename}"


def generate_3d_from_cutout(image_id: str, cutout_path: str) -> dict:
    if not cutout_path or not os.path.exists(cutout_path):
        return {
            "ok": False,
            "image_id": image_id,
            "status": "failed",
            "message": "Cutout PNG not found.",
        }

    job_id = uuid.uuid4().hex
    job_dir = _job_dir(job_id)

    logger.info("[3DGen] Created job folder: %s", job_dir)

    cutout_filename = f"cutout_{image_id}.png"
    job_cutout_path = os.path.join(job_dir, cutout_filename)
    shutil.copy2(cutout_path, job_cutout_path)
    logger.info("[3DGen] Saved cutout to: %s", job_cutout_path)

    model_path = None

    debug_use_fake_glb = os.getenv("DEBUG_USE_FAKE_GLB", "0").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    if debug_use_fake_glb:
        test_glb = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "storage",
                "test_assets",
                "sample.glb",
            )
        )
        logger.info("[3DGen] DEBUG_USE_FAKE_GLB enabled. sample path: %s", test_glb)

        if os.path.exists(test_glb):
            model_path = os.path.join(job_dir, "model.glb")
            shutil.copy2(test_glb, model_path)
            logger.info("[3DGen] Copied test GLB to: %s", model_path)
        else:
            logger.warning("[3DGen] sample.glb not found at: %s", test_glb)

    # Real generator hook goes here later.
    # Example:
    # model_path = run_real_3d_generation(job_cutout_path, job_dir)

    if model_path and Path(model_path).exists():
        model_name = Path(model_path).name
        model_url = _public_output_url(job_id, model_name)
        cutout_url = _public_output_url(job_id, cutout_filename)

        logger.info("[3DGen] Model available at: %s", model_url)

        return {
            "ok": True,
            "job_id": job_id,
            "image_id": image_id,
            "status": "completed",
            "model_url": model_url,
            "preview_url": model_url,
            "cutout_url": cutout_url,
        }

    logger.warning("[3DGen] Model generation not integrated yet for job %s.", job_id)

    return {
        "ok": False,
        "job_id": job_id,
        "image_id": image_id,
        "status": "not_implemented",
        "message": "Real image-to-3D generation is not integrated yet.",
        "cutout_url": _public_output_url(job_id, cutout_filename),
    }
```
