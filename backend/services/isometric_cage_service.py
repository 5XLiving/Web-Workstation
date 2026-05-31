from pathlib import Path
from PIL import Image
import numpy as np
import json


def _load_mask_from_alpha(image_path: str, size: int = 64):
    img = Image.open(image_path).convert("RGBA")
    img.thumbnail((size, size), Image.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    canvas.paste(img, (x, y), img)

    arr = np.array(canvas)
    alpha = arr[:, :, 3] > 20
    return alpha


def build_isometric_cage(image_path: str, job_dir: str, grid_size: int = 64) -> dict:
    job_dir = Path(job_dir)

    cage_dir = job_dir / "cage"
    cage_dir.mkdir(parents=True, exist_ok=True)

    mask = _load_mask_from_alpha(image_path, grid_size)

    ys, xs = np.where(mask)

    if len(xs) == 0:
        result = {
            "ok": False,
            "error": "No object mask found.",
            "grid_size": [grid_size, grid_size, grid_size],
            "occupied_cells": [],
        }

        (cage_dir / "isometric_cage.json").write_text(
            json.dumps(result, indent=2)
        )

        return result

    min_x = int(xs.min())
    max_x = int(xs.max())
    min_y = int(ys.min())
    max_y = int(ys.max())

    occupied = []
    surface = []

    for y in range(min_y, max_y + 1):

        row_x = np.where(mask[y])[0]

        if len(row_x) == 0:
            continue

        row_min = int(row_x.min())
        row_max = int(row_x.max())

        row_width = max(1, row_max - row_min)

        for x in row_x:

            nx = (x - row_min) / row_width

            center_depth = 1.0 - abs(nx - 0.5) * 2.0

            depth_radius = max(
                1,
                int(center_depth * grid_size * 0.18)
            )

            z_center = grid_size // 2

            for dz in range(-depth_radius, depth_radius + 1):

                z = z_center + dz

                if 0 <= z < grid_size:

                    occupied.append([
                        int(x),
                        int(y),
                        int(z)
                    ])

                    if abs(dz) == depth_radius:
                        surface.append([
                            int(x),
                            int(y),
                            int(z)
                        ])

    result = {
        "ok": True,
        "type": "isometric_voxel_cage",
        "grid_size": [grid_size, grid_size, grid_size],

        "bounds_2d": {
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
        },

        "occupied_cells": occupied,
        "surface_cells": surface,

        "symmetry_axis": "x",

        "note": (
            "CPU fallback isometric cage from "
            "2D alpha silhouette."
        ),
    }

    (cage_dir / "isometric_cage.json").write_text(
        json.dumps(result, indent=2)
    )

    return result