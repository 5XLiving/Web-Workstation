import os
import re
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class TripoSRError(RuntimeError):
    pass


def _resolve_python_bin() -> str:
    value = (os.getenv("TRIPOSR_PYTHON_BIN") or "").strip()
    if value and re.match(r"^[A-Za-z]:\\", value):
        return sys.executable
    return value or sys.executable


def _looks_like_windows_path(value: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:\\", value.strip()))


def _default_repo_dir() -> Path:
    # backend/services/triposr_runner.py -> project root -> TripoSR
    return Path(__file__).resolve().parents[2] / "TripoSR"


def _resolve_repo_dir(repo_dir: Optional[str] = None) -> Path:
    raw_value = (repo_dir or os.getenv("TRIPOSR_REPO_DIR") or "").strip()
    fallback = _default_repo_dir()

    # On Linux server, ignore stale Windows paths and fall back to local repo
    if raw_value and _looks_like_windows_path(raw_value):
        if fallback.exists():
            path = fallback
        else:
            raise TripoSRError(
                f"TRIPOSR_REPO_DIR is a Windows path on Linux: {raw_value}\n"
                f"Fallback repo also not found: {fallback}"
            )
    elif raw_value:
        path = Path(raw_value).expanduser().resolve()
    else:
        path = fallback.resolve()

    if not path.exists():
        raise TripoSRError(
            f"TripoSR repo not found: {path}\n"
            f"repo_dir arg: {repo_dir}\n"
            f"TRIPOSR_REPO_DIR env: {os.getenv('TRIPOSR_REPO_DIR')}\n"
            f"default fallback: {fallback}"
        )

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
            f"Repo: {repo}\n"
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