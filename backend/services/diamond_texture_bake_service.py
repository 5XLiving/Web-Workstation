from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

from PIL import Image, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS_DIR = PROJECT_ROOT / "storage" / "outputs"

VIEWS = ["front", "side", "back", "top", "bottom"]


def _public_url(job_id: str, filename: str) -> str:
    return f"/outputs/{job_id}/{filename}"


def _open_view(job_dir: Path, view: str, size: int = 512) -> Image.Image:
    p = job_dir / f"{view}.png"
    if not p.exists():
        raise FileNotFoundError(f"Missing {view}.png in {job_dir}")

    img = Image.open(p).convert("RGBA")
    img = ImageOps.contain(img, (size, size), Image.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    canvas.paste(img, (x, y), img)
    return canvas


def _diamond_mask(tile_size: int) -> Image.Image:
    mask = Image.new("L", (tile_size, tile_size), 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(mask)
    c = tile_size // 2
    d.polygon(
        [(c, 0), (tile_size - 1, c), (c, tile_size - 1), (0, c)],
        fill=255,
    )
    return mask


def bake_diamond_texture_atlas(
    multiview_job_id: str,
    atlas_size: int = 2048,
    grid_rows: int = 8,
    grid_cols: int = 8,
) -> Dict[str, Any]:
    job_dir = OUTPUTS_DIR / multiview_job_id
    if not job_dir.exists():
        raise FileNotFoundError(f"Multiview job not found: {multiview_job_id}")

    bake_job_id = f"{multiview_job_id}_bake"
    bake_dir = OUTPUTS_DIR / bake_job_id
    bake_dir.mkdir(parents=True, exist_ok=True)

    view_imgs = {
        view: _open_view(job_dir, view, size=512)
        for view in VIEWS
    }

    atlas = Image.new("RGBA", (atlas_size, atlas_size), (0, 0, 0, 0))

    # 5 views arranged vertically.
    # Each view contains grid_rows x grid_cols diamond tiles.
    view_band_h = atlas_size // len(VIEWS)
    tile_w = atlas_size // grid_cols
    tile_h = view_band_h // grid_rows
    tile_size = min(tile_w, tile_h)

    mask = _diamond_mask(tile_size)

    cells = []

    for view_index, view in enumerate(VIEWS):
        src = view_imgs[view]
        band_y = view_index * view_band_h

        for row in range(grid_rows):
            for col in range(grid_cols):
                src_x0 = int((col / grid_cols) * src.width)
                src_y0 = int((row / grid_rows) * src.height)
                src_x1 = int(((col + 1) / grid_cols) * src.width)
                src_y1 = int(((row + 1) / grid_rows) * src.height)

                crop = src.crop((src_x0, src_y0, src_x1, src_y1))
                crop = crop.resize((tile_size, tile_size), Image.LANCZOS)

                dst_x = col * tile_w + (tile_w - tile_size) // 2
                dst_y = band_y + row * tile_h + (tile_h - tile_size) // 2

                atlas.paste(crop, (dst_x, dst_y), mask)

                u0 = dst_x / atlas_size
                v0 = dst_y / atlas_size
                u1 = (dst_x + tile_size) / atlas_size
                v1 = (dst_y + tile_size) / atlas_size

                cells.append({
                    "cell_id": f"{view}_{row}_{col}",
                    "view": view,
                    "row": row,
                    "col": col,
                    "atlas_uv_rect": [u0, v0, u1, v1],
                    "diamond_uv": [
                        [(u0 + u1) / 2, v0],
                        [u1, (v0 + v1) / 2],
                        [(u0 + u1) / 2, v1],
                        [u0, (v0 + v1) / 2],
                    ],
                })

    atlas_path = bake_dir / "diamond_texture_atlas.png"
    atlas.save(atlas_path)

    texture_map = {
        "ok": True,
        "type": "diamond_texture_bake",
        "source_multiview_job_id": multiview_job_id,
        "bake_job_id": bake_job_id,
        "atlas_size": atlas_size,
        "grid_rows": grid_rows,
        "grid_cols": grid_cols,
        "views": VIEWS,
        "cell_count": len(cells),
        "cells": cells,
        "atlas_url": _public_url(bake_job_id, "diamond_texture_atlas.png"),
        "rule": "Universal diamond atlas. Later mesh UV faces should point into atlas_uv_rect / diamond_uv.",
    }

    map_path = bake_dir / "diamond_texture_map.json"
    map_path.write_text(json.dumps(texture_map, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "mode": "diamond_texture_bake",
        "source_multiview_job_id": multiview_job_id,
        "bake_job_id": bake_job_id,
        "atlas_url": _public_url(bake_job_id, "diamond_texture_atlas.png"),
        "map_url": _public_url(bake_job_id, "diamond_texture_map.json"),
        "atlas_path": str(atlas_path),
        "map_path": str(map_path),
        "cell_count": len(cells),
    }