"""
Image-to-3D inference service.

Accepts a masked RGBA image + preset class, runs the server-side
pipeline (depth estimation, structure prediction, mesh generation),
and returns geometry data the frontend can render.

Pipeline stages:
  1. Preprocess masked RGBA input
  2. Compute depth / pointmap
  3. Run sparse structure inference with preset priors
  4. Decode pose / scale / translation
  5. Optionally run layout post-optimization
  6. Return structured result to frontend
"""

import base64
import io
import logging
import math
import time
from typing import Any

import numpy as np
from PIL import Image

from services.preset_classes import get_preset, DEFAULT_PRESET

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. Preprocess
# ---------------------------------------------------------------------------

def _load_rgba(image_bytes: bytes) -> Image.Image:
    """Load image bytes into a PIL RGBA image."""
    img = Image.open(io.BytesIO(image_bytes))
    return img.convert("RGBA")


def _apply_mask(image: Image.Image, mask_bytes: bytes | None) -> Image.Image:
    """Apply an external mask to the image alpha channel if provided."""
    if mask_bytes is None:
        return image
    mask = Image.open(io.BytesIO(mask_bytes)).convert("L")
    mask = mask.resize(image.size, Image.LANCZOS)
    r, g, b, a = image.split()
    # Combine existing alpha with mask (intersection)
    combined = Image.fromarray(np.minimum(np.array(a), np.array(mask)))
    return Image.merge("RGBA", (r, g, b, combined))


def _crop_to_subject(image: Image.Image) -> tuple[Image.Image, dict]:
    """Crop to the bounding box of non-transparent pixels. Returns image + bbox."""
    arr = np.array(image)
    alpha = arr[:, :, 3]
    rows = np.any(alpha > 10, axis=1)
    cols = np.any(alpha > 10, axis=0)
    if not rows.any() or not cols.any():
        return image, {"minX": 0, "minY": 0, "maxX": 1, "maxY": 1}
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    h, w = arr.shape[:2]
    bbox = {
        "minX": float(cmin / w),
        "minY": float(rmin / h),
        "maxX": float((cmax + 1) / w),
        "maxY": float((rmax + 1) / h),
    }
    cropped = image.crop((int(cmin), int(rmin), int(cmax + 1), int(rmax + 1)))
    return cropped, bbox


# ---------------------------------------------------------------------------
# 2. Depth estimation (placeholder — swap in real model later)
# ---------------------------------------------------------------------------

def _estimate_depth(image: Image.Image) -> np.ndarray:
    """
    Estimate a depth map from the RGBA image.

    Currently returns a heuristic depth based on luminance + alpha.
    Replace this with Depth Anything V2, MiDaS, or ZoeDepth when available.
    """
    arr = np.array(image).astype(np.float32)
    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3] / 255.0

    # Luminance-based depth heuristic (brighter = closer for most subjects)
    lum = (0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]) / 255.0
    depth = (1.0 - lum * 0.4) * alpha

    # Normalize to 0-1
    dmin, dmax = depth.min(), depth.max()
    if dmax - dmin > 1e-6:
        depth = (depth - dmin) / (dmax - dmin)

    return depth


# ---------------------------------------------------------------------------
# 3. Sparse structure inference
# ---------------------------------------------------------------------------

def _analyze_structure(image: Image.Image, depth: np.ndarray, preset: dict) -> dict:
    """
    Predict 3D structure stats from the image, depth, and preset priors.

    Returns dimensions, symmetry score, confidence, fill density, etc.
    """
    arr = np.array(image)
    alpha = arr[:, :, 3]
    h, w = alpha.shape

    # Subject pixel mask
    subject = alpha > 10
    subject_count = int(subject.sum())
    total_pixels = h * w
    fill_ratio = subject_count / max(1, total_pixels)

    # Aspect ratio
    aspect = w / max(1, h)

    # Symmetry: compare left half to flipped right half
    mid = w // 2
    left_half = subject[:, :mid]
    right_half = np.fliplr(subject[:, mid:mid + left_half.shape[1]])
    min_cols = min(left_half.shape[1], right_half.shape[1])
    if min_cols > 0:
        match_pixels = int((left_half[:, :min_cols] == right_half[:, :min_cols]).sum())
        symmetry_score = match_pixels / max(1, left_half[:, :min_cols].size)
    else:
        symmetry_score = 0.5

    # Depth statistics within subject
    depth_in_subject = depth[subject]
    if len(depth_in_subject) > 0:
        depth_mean = float(np.mean(depth_in_subject))
        depth_std = float(np.std(depth_in_subject))
        depth_range = float(np.max(depth_in_subject) - np.min(depth_in_subject))
    else:
        depth_mean = 0.5
        depth_std = 0.1
        depth_range = 0.5

    # Use preset priors to scale dimensions
    target_h = preset["default_height"]
    target_w = round(target_h * aspect, 4)
    target_d = round(target_h * preset["depth_ratio"], 4)

    # Confidence: higher fill + symmetry match + depth range → higher confidence
    confidence = min(1.0, 0.3 + fill_ratio * 0.3 + symmetry_score * 0.2 + depth_range * 0.2)

    return {
        "width": target_w,
        "height": target_h,
        "depth": target_d,
        "aspect": round(aspect, 4),
        "fill_ratio": round(fill_ratio, 4),
        "symmetry_score": round(symmetry_score, 4),
        "symmetry_type": preset["symmetry"],
        "topology_hint": preset["topology_hint"],
        "depth_mean": round(depth_mean, 4),
        "depth_std": round(depth_std, 4),
        "depth_range": round(depth_range, 4),
        "confidence": round(confidence, 4),
        "thickness_multiplier": preset["thickness_multiplier"],
        "subject_pixels": subject_count,
        "image_width": w,
        "image_height": h,
    }


# ---------------------------------------------------------------------------
# 4. Pose / scale / translation decode
# ---------------------------------------------------------------------------

def _decode_pose(stats: dict, preset: dict) -> dict:
    """
    Decode canonical pose, scale, and translation from structure stats.
    """
    return {
        "scale": [stats["width"], stats["height"], stats["depth"]],
        "translation": [0.0, stats["height"] / 2 + 0.15, 0.0],
        "rotation": [0.0, 0.0, 0.0],
        "up_axis": "Y",
        "front_axis": "-Z",
    }


# ---------------------------------------------------------------------------
# 5. Point cloud generation from depth + mask
# ---------------------------------------------------------------------------

def _generate_point_cloud(image: Image.Image, depth: np.ndarray,
                          stats: dict, max_points: int = 4096) -> list[dict]:
    """
    Generate a sparse colored point cloud from the depth map and mask.
    Points are in normalized object-centered coordinates.
    """
    arr = np.array(image)
    alpha = arr[:, :, 3]
    h, w = alpha.shape
    subject = alpha > 10

    # Sample subject pixels
    ys, xs = np.where(subject)
    n_subject = len(ys)
    if n_subject == 0:
        return []

    # Subsample if too many
    if n_subject > max_points:
        indices = np.random.choice(n_subject, max_points, replace=False)
        xs = xs[indices]
        ys = ys[indices]

    # Map to 3D coordinates
    target_w = stats["width"]
    target_h = stats["height"]
    target_d = stats["depth"]

    points = []
    for i in range(len(xs)):
        px, py = int(xs[i]), int(ys[i])
        # Normalize to -0.5..0.5
        nx = (px / w) - 0.5
        ny = 0.5 - (py / h)
        d_val = float(depth[py, px])
        nz = (d_val - 0.5) * target_d

        color = arr[py, px, :3].tolist()
        points.append({
            "x": round(nx * target_w, 5),
            "y": round(ny * target_h, 5),
            "z": round(nz, 5),
            "intensity": round(d_val, 4),
            "size": 0.015,
            "r": color[0],
            "g": color[1],
            "b": color[2],
        })

    return points


# ---------------------------------------------------------------------------
# 6. Layout post-optimization (optional)
# ---------------------------------------------------------------------------

def _optimize_layout(stats: dict, pose: dict, point_cloud: list) -> dict:
    """
    Optional post-processing: adjust bounding box, recenter, check watertight-ness.
    Currently a passthrough — hook in optimization when available.
    """
    return {
        "optimized": False,
        "message": "Layout optimization not yet implemented. Using raw inference.",
        "adjustments": {},
    }


# ---------------------------------------------------------------------------
# Build construction steps from server-side data
# ---------------------------------------------------------------------------

def _build_construction_steps(stats: dict, point_cloud: list) -> list[dict]:
    """
    Build the 3-phase construction animation steps:
      Phase 1 (trace)  — beam-lock onto structure points
      Phase 2 (spin)   — spiral scaffold densification
      Phase 3 (ring)   — vertical skin wrap
    """
    steps = []
    w = stats["width"]
    h = stats["height"]
    d = stats["depth"]
    center_y = 0.15 + h / 2

    # Phase 1: Trace — sample key points from cloud
    n_trace = min(48, len(point_cloud))
    sample_indices = np.linspace(0, len(point_cloud) - 1, n_trace, dtype=int)
    for i, idx in enumerate(sample_indices):
        pt = point_cloud[int(idx)]
        steps.append({
            "phase": "trace",
            "layer": i,
            "action": "trace",
            "x": pt["x"],
            "y": pt["y"] + center_y,
            "z": pt["z"],
        })

    # Phase 2: Spin — spiral around center
    n_spin = 36
    for i in range(n_spin):
        angle = (i / n_spin) * math.pi * 4
        r = (w + d) * 0.25
        progress = i / n_spin
        steps.append({
            "phase": "spin",
            "layer": n_trace + i,
            "action": "spin",
            "x": round(math.cos(angle) * r, 5),
            "y": round(0.15 + progress * h, 5),
            "z": round(math.sin(angle) * r, 5),
        })

    # Phase 3: Ring — vertical sweep
    n_ring = 24
    for i in range(n_ring):
        progress = i / n_ring
        steps.append({
            "phase": "ring",
            "layer": n_trace + n_spin + i,
            "action": "ring",
            "x": 0,
            "y": round(0.15 + progress * h, 5),
            "z": 0,
        })

    return steps


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_inference(image_bytes: bytes,
                  mask_bytes: bytes | None = None,
                  preset_class: str = DEFAULT_PRESET,
                  user_dimensions: dict | None = None) -> dict[str, Any]:
    """
    Full image-to-3D inference pipeline.

    Args:
        image_bytes:    Raw uploaded image file content.
        mask_bytes:     Optional mask (white = subject, black = background).
        preset_class:   One of the preset class keys.
        user_dimensions: Optional user-overridden {width, height, depth}.

    Returns:
        Dict with structure stats, point cloud, pose, construction steps,
        and a base64 depth preview.
    """
    t0 = time.time()
    preset = get_preset(preset_class)

    # 1. Preprocess
    rgba = _load_rgba(image_bytes)
    rgba = _apply_mask(rgba, mask_bytes)
    cropped, bbox = _crop_to_subject(rgba)

    # 2. Depth
    depth = _estimate_depth(cropped)

    # Encode depth as base64 PNG for frontend preview
    depth_u8 = (depth * 255).astype(np.uint8)
    depth_img = Image.fromarray(depth_u8, mode="L")
    buf = io.BytesIO()
    depth_img.save(buf, format="PNG")
    depth_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    # 3. Structure
    stats = _analyze_structure(cropped, depth, preset)

    # Override with user dimensions if provided
    if user_dimensions:
        for key in ("width", "height", "depth"):
            v = user_dimensions.get(key)
            if v is not None and isinstance(v, (int, float)) and v > 0:
                stats[key] = float(v)

    # 4. Pose
    pose = _decode_pose(stats, preset)

    # 5. Point cloud
    point_cloud = _generate_point_cloud(cropped, depth, stats)

    # 6. Layout optimization
    optimization = _optimize_layout(stats, pose, point_cloud)

    # 7. Construction steps
    construction_steps = _build_construction_steps(stats, point_cloud)

    elapsed = round(time.time() - t0, 3)

    return {
        "ok": True,
        "preset_class": preset_class,
        "preset_label": preset["label"],
        "stats": stats,
        "pose": pose,
        "bbox": bbox,
        "point_cloud": {
            "points": point_cloud,
            "totalPoints": len(point_cloud),
        },
        "depth_preview_b64": depth_b64,
        "depth_width": int(cropped.size[0]),
        "depth_height": int(cropped.size[1]),
        "construction_steps": construction_steps,
        "optimization": optimization,
        "elapsed_seconds": elapsed,
    }
