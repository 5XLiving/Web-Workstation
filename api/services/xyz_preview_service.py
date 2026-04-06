"""
xyz_preview_service.py

Handles preview-only logic for .ply, mesh, point cloud, or splat files.
No chamber logic here.
"""
from typing import Any, Dict



def prepare_preview(preview_data: Any, preview_type: str = "ply") -> Dict[str, Any]:
    """
    Prepares preview output for the frontend viewer.
    preview_data: raw data (e.g., file path, bytes, or object)
    preview_type: 'ply', 'mesh', 'point_cloud', 'splat', etc.
    Returns dict with preview info.
    Raises ValueError if invalid.
    """
    if preview_data is None:
        raise ValueError("preview_data must be provided.")
    if not isinstance(preview_type, str):
        raise ValueError("preview_type must be a string.")
    return {
        "type": preview_type,
        "data": preview_data
    }
