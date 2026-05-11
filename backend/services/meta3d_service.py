import os
import shutil
import subprocess
from pathlib import Path


def generate_meta3d_model(image_path: str, output_dir: str, job_id: str):
    image_path = Path(image_path)
    output_dir = Path(output_dir)

    if not image_path.exists():
        raise FileNotFoundError(f"Input image not found: {image_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    final_glb = output_dir / "model.glb"
    raw_dir = output_dir / "meta3d_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    meta_repo = os.getenv("META3D_REPO", "").strip()
    meta_python = os.getenv("META3D_PYTHON", "python").strip()

    if not meta_repo:
        raise RuntimeError("META3D_REPO is not set")

    meta_repo = Path(meta_repo)

    if not meta_repo.exists():
        raise RuntimeError(f"META3D_REPO not found: {meta_repo}")

    # IMPORTANT:
    # Adjust this command to match your installed Meta 3D repo script.
    # Keep output as GLB inside raw_dir.
    cmd = [
        meta_python,
        "run.py",
        "--input",
        str(image_path),
        "--output",
        str(raw_dir),
    ]

    result = subprocess.run(
        cmd,
        cwd=str(meta_repo),
        capture_output=True,
        text=True,
        timeout=1800,
    )

    log_path = output_dir / "meta3d_log.txt"
    log_path.write_text(
        "COMMAND:\n"
        + " ".join(cmd)
        + "\n\nSTDOUT:\n"
        + result.stdout
        + "\n\nSTDERR:\n"
        + result.stderr,
        encoding="utf-8",
    )

    if result.returncode != 0:
        raise RuntimeError(f"Meta 3D failed. See log: {log_path}")

    glb_files = list(raw_dir.rglob("*.glb"))

    if not glb_files:
        raise RuntimeError(f"No .glb produced by Meta 3D. See log: {log_path}")

    shutil.copyfile(glb_files[0], final_glb)

    return {
        "engine": "meta_3d",
        "job_id": job_id,
        "input": str(image_path),
        "model": str(final_glb),
        "raw_output": str(raw_dir),
        "log": str(log_path),
    }