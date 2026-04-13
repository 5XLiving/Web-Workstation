import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class InstantMeshError(RuntimeError):
    pass


def _resolve_python_bin() -> str:
    return os.getenv("INSTANTMESH_PYTHON_BIN") or sys.executable


def _resolve_repo_dir(repo_dir: Optional[str] = None) -> Path:
    value = repo_dir or os.getenv("INSTANTMESH_REPO_DIR")
    if not value:
        raise InstantMeshError(
            "INSTANTMESH_REPO_DIR is not set. Point it to your cloned InstantMesh repo."
        )

    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise InstantMeshError(f"InstantMesh repo not found: {path}")

    run_py = path / "run.py"
    if not run_py.exists():
        raise InstantMeshError(f"InstantMesh run.py not found: {run_py}")

    return path


def _resolve_config_path(repo: Path, config_path: Optional[str] = None) -> Path:
    raw = config_path or os.getenv("INSTANTMESH_CONFIG") or "configs/instant-mesh-large.yaml"
    path = Path(raw)

    if not path.is_absolute():
        path = (repo / path).resolve()

    if not path.exists():
        raise InstantMeshError(f"InstantMesh config not found: {path}")

    return path


def _find_best_output_file(output_dir: Path) -> Optional[Path]:
    preferred_exts = [".obj", ".glb", ".gltf", ".ply", ".stl"]
    candidates = [p for p in output_dir.rglob("*") if p.is_file()]

    for ext in preferred_exts:
        matches = [p for p in candidates if p.suffix.lower() == ext]
        if matches:
            return max(matches, key=lambda p: p.stat().st_mtime)

    return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None


def _copy_primary_output(found: Path, output_dir: Path) -> Path:
    target = output_dir / found.name
    if found.resolve() != target.resolve():
        shutil.copy2(found, target)
    return target


def run_instantmesh(
    image_path: str,
    output_dir: str,
    *,
    repo_dir: Optional[str] = None,
    config_path: Optional[str] = None,
    no_rembg: bool = True,
    export_texmap: bool = False,
    save_video: bool = False,
    timeout_seconds: int = 3600,
) -> dict:
    image = Path(image_path).expanduser().resolve()
    if not image.exists():
        raise InstantMeshError(f"Input image not found: {image}")

    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    repo = _resolve_repo_dir(repo_dir)
    config = _resolve_config_path(repo, config_path)
    python_bin = _resolve_python_bin()

    cmd = [
        python_bin,
        str(repo / "run.py"),
        str(config),
        str(image),
        "--output_path",
        str(out_dir),
    ]

    if no_rembg:
        cmd.append("--no_rembg")
    if export_texmap:
        cmd.append("--export_texmap")
    if save_video:
        cmd.append("--save_video")

    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")

    proc = subprocess.run(
        cmd,
        cwd=str(repo),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    if proc.returncode != 0:
        raise InstantMeshError(
            "InstantMesh inference failed.\n"
            f"Command: {' '.join(cmd)}\n"
            f"Exit code: {proc.returncode}\n"
            f"STDOUT:\n{stdout}\n"
            f"STDERR:\n{stderr}"
        )

    mesh = _find_best_output_file(out_dir)
    if not mesh:
        raise InstantMeshError(
            "InstantMesh finished but no output mesh/model file was found.\n"
            f"Output dir: {out_dir}\n"
            f"STDOUT:\n{stdout}\n"
            f"STDERR:\n{stderr}"
        )

    mesh = _copy_primary_output(mesh, out_dir)

    return {
        "ok": True,
        "engine": "instantmesh",
        "output_path": str(mesh),
        "output_name": mesh.name,
        "output_dir": str(out_dir),
        "stdout": stdout,
        "stderr": stderr,
    }
