import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class TripoSRError(RuntimeError):
    pass


def _resolve_python_bin() -> str:
    return os.getenv("TRIPOSR_PYTHON_BIN") or sys.executable


def _resolve_repo_dir(repo_dir: Optional[str] = None) -> Path:
    value = repo_dir or os.getenv("TRIPOSR_REPO_DIR")
    if not value:
        raise TripoSRError(
            "TRIPOSR_REPO_DIR is not set. Point it to your cloned TripoSR repo."
        )

    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise TripoSRError(f"TripoSR repo not found: {path}")

    run_py = path / "run.py"
    if not run_py.exists():
        raise TripoSRError(f"TripoSR run.py not found: {run_py}")

    return path


def _find_best_output_file(output_dir: Path) -> Optional[Path]:
    preferred_exts = [".glb", ".gltf", ".obj"]
    candidates = [p for p in output_dir.rglob("*") if p.is_file()]

    for ext in preferred_exts:
        matches = [p for p in candidates if p.suffix.lower() == ext]
        if matches:
            return max(matches, key=lambda p: p.stat().st_mtime)

    return None


def _copy_or_convert_primary_mesh(found: Path, output_dir: Path) -> Path:
    target = output_dir / found.name
    if found.resolve() != target.resolve():
        shutil.copy2(found, target)
    return target


def run_triposr(
    image_path: str,
    output_dir: str,
    *,
    repo_dir: Optional[str] = None,
    bake_texture: bool = False,
    texture_resolution: Optional[int] = None,
    timeout_seconds: int = 1800,
) -> dict:
    image = Path(image_path).expanduser().resolve()
    if not image.exists():
        raise TripoSRError(f"Input image not found: {image}")

    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    repo = _resolve_repo_dir(repo_dir)
    python_bin = _resolve_python_bin()

    cmd = [
        python_bin,
        str(repo / "run.py"),
        str(image),
        "--output-dir",
        str(out_dir),
    ]

    if bake_texture:
        cmd.append("--bake-texture")
    if texture_resolution and texture_resolution > 0:
        cmd.extend(["--texture-resolution", str(int(texture_resolution))])

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
        raise TripoSRError(
            "TripoSR inference failed.\n"
            f"Command: {' '.join(cmd)}\n"
            f"Exit code: {proc.returncode}\n"
            f"STDOUT:\n{stdout}\n"
            f"STDERR:\n{stderr}"
        )

    mesh = _find_best_output_file(out_dir)
    if not mesh:
        raise TripoSRError(
            "TripoSR finished but no output mesh/model file was found.\n"
            f"Output dir: {out_dir}\n"
            f"STDOUT:\n{stdout}\n"
            f"STDERR:\n{stderr}"
        )

    mesh = _copy_or_convert_primary_mesh(mesh, out_dir)

    return {
        "ok": True,
        "engine": "triposr",
        "output_path": str(mesh),
        "output_name": mesh.name,
        "output_dir": str(out_dir),
        "stdout": stdout,
        "stderr": stderr,
    }
