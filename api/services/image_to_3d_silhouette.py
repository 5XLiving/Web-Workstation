from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


@dataclass
class SilhouetteConfig:
    width: float = 1.2
    height: float = 1.05
    depth: float = 0.35
    scale: float = 1.0
    quality: str = "draft"   # draft | standard | high
    texture: bool = False
    bg_distance_threshold: float = 28.0
    alpha_threshold: int = 16


QUALITY_TO_GRID = {
    "draft": 40,
    "standard": 64,
    "high": 96,
}

QUALITY_TO_DEPTH_LAYERS = {
    "draft": 6,
    "standard": 10,
    "high": 14,
}


def _clamp_quality(quality: str) -> str:
    return quality if quality in QUALITY_TO_GRID else "draft"


def _load_rgba(image_path: Path) -> Image.Image:
    img = Image.open(image_path).convert("RGBA")
    return img


def _corner_bg_color(arr: np.ndarray) -> np.ndarray:
    h, w, _ = arr.shape
    patch = max(2, min(h, w) // 20)

    corners = [
        arr[:patch, :patch, :3],
        arr[:patch, w - patch:w, :3],
        arr[h - patch:h, :patch, :3],
        arr[h - patch:h, w - patch:w, :3],
    ]
    samples = np.concatenate([c.reshape(-1, 3) for c in corners], axis=0)
    return samples.mean(axis=0)


def _neighbor_count(mask: np.ndarray) -> np.ndarray:
    p = np.pad(mask.astype(np.uint8), 1)
    return (
        p[:-2, :-2] + p[:-2, 1:-1] + p[:-2, 2:] +
        p[1:-1, :-2] +                 p[1:-1, 2:] +
        p[2:, :-2] + p[2:, 1:-1] + p[2:, 2:]
    )


def _cleanup_mask(mask: np.ndarray, rounds: int = 2) -> np.ndarray:
    out = mask.astype(bool)
    for _ in range(rounds):
        n = _neighbor_count(out)
        out = np.where(out, n >= 2, n >= 5)
    return out


def _mask_from_image(img: Image.Image, alpha_threshold: int, bg_distance_threshold: float) -> np.ndarray:
    arr = np.asarray(img).astype(np.float32)
    rgb = arr[..., :3]
    alpha = arr[..., 3]

    # Prefer real transparency if present
    if float(alpha.min()) < 250.0:
        mask = alpha > alpha_threshold
        return _cleanup_mask(mask, rounds=2)

    # Otherwise estimate subject against corner background
    bg = _corner_bg_color(arr)
    dist = np.linalg.norm(rgb - bg[None, None, :], axis=-1)

    luminance = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    near_white = luminance > 246.0

    mask = (dist > bg_distance_threshold) & (~near_white | (dist > bg_distance_threshold * 1.5))
    mask = _cleanup_mask(mask, rounds=2)
    return mask


def _resize_mask(mask: np.ndarray, max_side: int) -> np.ndarray:
    h, w = mask.shape
    scale = min(1.0, max_side / max(h, w))
    new_w = max(8, int(round(w * scale)))
    new_h = max(8, int(round(h * scale)))

    pil = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    resized = pil.resize((new_w, new_h), Image.Resampling.NEAREST)
    arr = np.asarray(resized) > 127
    return _cleanup_mask(arr, rounds=1)


def _sample_color_grid(img: Image.Image, target_w: int, target_h: int) -> np.ndarray:
    small = img.convert("RGB").resize((target_w, target_h), Image.Resampling.BILINEAR)
    return np.asarray(small).astype(np.float32) / 255.0


def _add_face(
    vertices: list[float],
    indices: list[int],
    normals: list[float],
    colors: list[float],
    quad: list[tuple[float, float, float]],
    normal: tuple[float, float, float],
    color: tuple[float, float, float],
) -> None:
    base = len(vertices) // 3
    for vx, vy, vz in quad:
        vertices.extend([float(vx), float(vy), float(vz)])
        normals.extend([float(normal[0]), float(normal[1]), float(normal[2])])
        colors.extend([float(color[0]), float(color[1]), float(color[2])])

    indices.extend([
        base + 0, base + 1, base + 2,
        base + 0, base + 2, base + 3,
    ])


def _voxel_surface_mesh(
    mask: np.ndarray,
    color_grid: np.ndarray,
    width: float,
    height: float,
    depth: float,
    depth_layers: int,
) -> dict[str, list[float] | list[int] | None]:
    h, w = mask.shape
    occ = np.repeat(mask[:, :, None], depth_layers, axis=2)

    dx = width / max(w, 1)
    dy = height / max(h, 1)
    dz = depth / max(depth_layers, 1)

    x_start = -width / 2.0
    y_start = -height / 2.0
    z_start = -depth / 2.0

    vertices: list[float] = []
    indices: list[int] = []
    normals: list[float] = []
    colors: list[float] = []

    def filled(x: int, y: int, z: int) -> bool:
        if x < 0 or x >= w or y < 0 or y >= h or z < 0 or z >= depth_layers:
            return False
        return bool(occ[y, x, z])

    for y in range(h):
        for x in range(w):
            if not mask[y, x]:
                continue

            # Flip Y for nicer upright preview
            yy = h - 1 - y

            col = tuple(color_grid[yy, x].tolist())

            for z in range(depth_layers):
                if not occ[yy, x, z]:
                    continue

                x0 = x_start + x * dx
                x1 = x0 + dx
                y0 = y_start + yy * dy
                y1 = y0 + dy
                z0 = z_start + z * dz
                z1 = z0 + dz

                # -X
                if not filled(x - 1, yy, z):
                    _add_face(
                        vertices, indices, normals, colors,
                        [(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)],
                        (-1.0, 0.0, 0.0), col
                    )

                # +X
                if not filled(x + 1, yy, z):
                    _add_face(
                        vertices, indices, normals, colors,
                        [(x1, y0, z1), (x1, y1, z1), (x1, y1, z0), (x1, y0, z0)],
                        (1.0, 0.0, 0.0), col
                    )

                # -Y
                if not filled(x, yy - 1, z):
                    _add_face(
                        vertices, indices, normals, colors,
                        [(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)],
                        (0.0, -1.0, 0.0), col
                    )

                # +Y
                if not filled(x, yy + 1, z):
                    _add_face(
                        vertices, indices, normals, colors,
                        [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
                        (0.0, 1.0, 0.0), col
                    )

                # -Z
                if not filled(x, yy, z - 1):
                    _add_face(
                        vertices, indices, normals, colors,
                        [(x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z0)],
                        (0.0, 0.0, -1.0), col
                    )

                # +Z
                if not filled(x, yy, z + 1):
                    _add_face(
                        vertices, indices, normals, colors,
                        [(x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)],
                        (0.0, 0.0, 1.0), col
                    )

    return {
        "vertices": vertices,
        "indices": indices,
        "normals": normals,
        "uvs": None,
        "colors": colors if colors else None,
    }


def run_image_to_3d_silhouette(
    image_path: Path,
    *,
    prompt: str = "",
    preset: str = "generic_object",
    width: float = 1.2,
    height: float = 1.05,
    depth: float = 0.35,
    scale: float = 1.0,
    texture: bool = False,
    return_format: str = "json_mesh",
    quality: str = "draft",
) -> dict[str, Any]:
    quality = _clamp_quality(quality)
    max_side = QUALITY_TO_GRID[quality]
    depth_layers = QUALITY_TO_DEPTH_LAYERS[quality]

    img = _load_rgba(image_path)
    mask = _mask_from_image(
        img,
        alpha_threshold=16,
        bg_distance_threshold=28.0,
    )
    mask_small = _resize_mask(mask, max_side=max_side)

    if not mask_small.any():
        raise ValueError("Could not detect a usable subject silhouette from the image.")

    color_grid = _sample_color_grid(img, target_w=mask_small.shape[1], target_h=mask_small.shape[0])

    mesh = _voxel_surface_mesh(
        mask=mask_small,
        color_grid=color_grid,
        width=width * scale,
        height=height * scale,
        depth=depth * scale,
        depth_layers=depth_layers,
    )

    return {
        "ok": True,
        "type": "mesh",
        "format": "json_mesh",
        "mesh": {
            "vertices": mesh["vertices"],
            "indices": mesh["indices"],
            "normals": mesh["normals"],
            "uvs": mesh["uvs"],
            "colors": mesh["colors"],
            "material": {
                "color": 0x94F3DE,
                "metalness": 0.12,
                "roughness": 0.78,
                "transparent": False,
                "opacity": 1.0,
            },
        },
        "meta": {
            "source_image": image_path.name,
            "preset": preset,
            "prompt": prompt,
            "bbox": {
                "width": width,
                "height": height,
                "depth": depth,
                "scale": scale,
            },
            "quality": quality,
            "texture": texture,
            "mask_resolution": {
                "width": int(mask_small.shape[1]),
                "height": int(mask_small.shape[0]),
            },
            "depth_layers": depth_layers,
            "vertex_count": len(mesh["vertices"]) // 3,
            "face_count": len(mesh["indices"]) // 3,
            "note": "Silhouette extrusion stage. Real AI reconstruction not plugged in yet.",
        },
    }
