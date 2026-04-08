""" xyz_preview_service.py 

Handles preview-only logic for .ply, mesh, point cloud, or splat files. No chamber logic here. """

from typing import Any, Dict

ALLOWED_PREVIEW_TYPES = {"mesh", "ply", "point_cloud", "splat"}

def prepare_preview(preview_data: Any, preview_type: str = "mesh") -> Dict[str, Any]:
    if preview_data is None:
        raise ValueError("preview_data must be provided.")

    if not isinstance(preview_type, str):
        raise ValueError("preview_type must be a string.")

    preview_type = preview_type.strip().lower()
    if preview_type not in ALLOWED_PREVIEW_TYPES:
        raise ValueError(f"Unsupported preview_type: {preview_type}")

    return {
        "preview_type": preview_type,
        "type": preview_type,
        "data": preview_data
    }
