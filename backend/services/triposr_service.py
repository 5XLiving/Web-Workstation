import os
import uuid
import shutil
import logging
from pathlib import Path

from backend.services.triposr_runner import run_triposr, TripoSRError
from backend.services.instantmesh_service import run_instantmesh, InstantMeshError

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


def _copy_into_job_dir(src_path: str, job_dir: str, preferred_name: str | None = None) -> str:
    src = Path(src_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"Output file not found: {src}")

    filename = preferred_name or src.name
    dst = Path(job_dir) / filename

    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)

    return str(dst)


def _run_real_generator(job_cutout_path: str, job_dir: str) -> tuple[str, str]:
    engine = os.getenv("IMAGE3D_ENGINE", "triposr").strip().lower()

    if engine == "triposr":
        result = run_triposr(
            image_path=job_cutout_path,
            output_dir=job_dir,
            repo_dir=None,
            bake_texture=os.getenv("TRIPOSR_BAKE_TEXTURE", "0").strip().lower() in {"1", "true", "yes", "on"},
            texture_resolution=int(os.getenv("TRIPOSR_TEXTURE_RESOLUTION", "0") or 0) or None,
            timeout_seconds=int(os.getenv("TRIPOSR_TIMEOUT_SECONDS", "1800")),
        )
        return result["output_path"], "triposr"

    if engine == "instantmesh":
        result = run_instantmesh(
            image_path=job_cutout_path,
            output_dir=job_dir,
            repo_dir=os.getenv("INSTANTMESH_REPO_DIR"),
            config_path=os.getenv("INSTANTMESH_CONFIG"),
            no_rembg=os.getenv("INSTANTMESH_NO_REMBG", "1").strip().lower() in {"1", "true", "yes", "on"},
            export_texmap=os.getenv("INSTANTMESH_EXPORT_TEXMAP", "0").strip().lower() in {"1", "true", "yes", "on"},
            save_video=os.getenv("INSTANTMESH_SAVE_VIDEO", "0").strip().lower() in {"1", "true", "yes", "on"},
            timeout_seconds=int(os.getenv("INSTANTMESH_TIMEOUT_SECONDS", "3600")),
        )
        return result["output_path"], "instantmesh"

    raise RuntimeError(
        f"Unsupported IMAGE3D_ENGINE='{engine}'. Use 'triposr' or 'instantmesh'."
    )


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

    debug_use_fake_glb = os.getenv("DEBUG_USE_FAKE_GLB", "0").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    try:
        model_path = None
        engine_used = "debug_fake_glb" if debug_use_fake_glb else os.getenv("IMAGE3D_ENGINE", "triposr").strip().lower()

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

            if not os.path.exists(test_glb):
                raise FileNotFoundError(f"sample.glb not found at: {test_glb}")

            model_path = _copy_into_job_dir(test_glb, job_dir, "model.glb")
            logger.info("[3DGen] Copied test GLB to: %s", model_path)
        else:
            model_path, engine_used = _run_real_generator(job_cutout_path, job_dir)
            model_path = _copy_into_job_dir(model_path, job_dir)

        if model_path and Path(model_path).exists():
            model_name = Path(model_path).name
            model_url = _public_output_url(job_id, model_name)
            cutout_url = _public_output_url(job_id, cutout_filename)

            logger.info("[3DGen] Model available at: %s", model_url)

            return {
                "ok": True,
                "job_id": job_id,
                "image_id": image_id,
                "engine": engine_used,
                "status": "completed",
                "model_url": model_url,
                "preview_url": model_url,
                "cutout_url": cutout_url,
            }

        raise RuntimeError("Model generator finished but no output model file was found.")

    except (TripoSRError, InstantMeshError, FileNotFoundError, RuntimeError) as e:
        logger.exception("[3DGen] Generation failed for job %s", job_id)
        return {
            "ok": False,
            "job_id": job_id,
            "image_id": image_id,
            "engine": os.getenv("IMAGE3D_ENGINE", "triposr").strip().lower(),
            "status": "failed",
            "message": str(e),
            "cutout_url": _public_output_url(job_id, cutout_filename),
        }

    except Exception as e:
        logger.exception("[3DGen] Unexpected generation error for job %s", job_id)
        return {
            "ok": False,
            "job_id": job_id,
            "image_id": image_id,
            "engine": os.getenv("IMAGE3D_ENGINE", "triposr").strip().lower(),
            "status": "failed",
            "message": f"Unexpected error: {e}",
            "cutout_url": _public_output_url(job_id, cutout_filename),
        }
