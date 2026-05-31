from __future__ import annotations

import base64
import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS_DIR = PROJECT_ROOT / "storage" / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


REQUIRED_VIEWS = ["front", "side", "back", "top", "bottom"]


def _public_url(job_id: str, filename: str) -> str:
    return f"/outputs/{job_id}/{filename}"


def _clean_base64(value: str) -> str:
    if not value:
        return ""

    value = str(value)

    if "," in value and value.startswith("data:"):
        return value.split(",", 1)[1]

    return value


def _save_base64_png(
    image_base64: str,
    path: Path,
) -> None:
    raw = base64.b64decode(_clean_base64(image_base64))
    path.write_bytes(raw)


def save_multiview_images(
    views: Dict[str, Any],
    job_id: Optional[str] = None,
) -> Dict[str, Any]:
    if not views:
        raise ValueError("Missing views")

    job_id = job_id or f"mv_{uuid.uuid4().hex[:16]}"
    job_dir = OUTPUTS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    saved: Dict[str, Any] = {}

    for view in REQUIRED_VIEWS:
        view_obj = views.get(view) or {}
        image_base64 = view_obj.get("image_base64")

        if not image_base64:
            saved[view] = {
                "ok": False,
                "filename": None,
                "url": None,
                "error": f"missing_{view}_image_base64",
            }
            continue

        filename = f"{view}.png"
        file_path = job_dir / filename

        _save_base64_png(image_base64, file_path)

        saved[view] = {
            "ok": True,
            "filename": filename,
            "path": str(file_path),
            "url": _public_url(job_id, filename),
        }

    manifest = {
        "ok": True,
        "job_id": job_id,
        "type": "multiview_storage",
        "views": saved,
        "required_views": REQUIRED_VIEWS,
        "rule": "Saved AI multiview images for reuse by cage, shell and texture bake pipeline.",
    }

    manifest_path = job_dir / "multiview.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    return {
        "ok": True,
        "job_id": job_id,
        "output_dir": str(job_dir),
        "manifest_url": _public_url(job_id, "multiview.json"),
        "manifest_path": str(manifest_path),
        "views": saved,
    }


def load_multiview_manifest(job_id: str) -> Dict[str, Any]:
    manifest_path = OUTPUTS_DIR / job_id / "multiview.json"

    if not manifest_path.exists():
        raise FileNotFoundError(f"Multiview manifest not found: {job_id}")

    return json.loads(manifest_path.read_text(encoding="utf-8"))