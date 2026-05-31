from pathlib import Path
from PIL import Image, ImageDraw
import json
import uuid
import math


def _is_foreground(r, g, b, a):
    if a < 20:
        return False
    if r > 238 and g > 238 and b > 238:
        return False
    if r < 8 and g < 8 and b < 8:
        return False
    return True


def _find_non_bg_bbox(img: Image.Image):
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()

    xs, ys = [], []

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if _is_foreground(r, g, b, a):
                xs.append(x)
                ys.append(y)

    if not xs or not ys:
        return [0, 0, w, h]

    return [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)]


def _draw_iso_grid(draw, canvas_w, canvas_h, cell=36):
    color = (148, 243, 222, 95)

    # vertical lines
    x = 0
    while x <= canvas_w:
        draw.line([(x, 0), (x, canvas_h)], fill=color, width=1)
        x += cell

    # left diagonal /
    start = -canvas_h
    end = canvas_w + canvas_h
    x = start
    while x <= end:
        draw.line([(x, canvas_h), (x + canvas_h, 0)], fill=color, width=1)
        x += cell

    # right diagonal \
    x = -canvas_h
    while x <= canvas_w + canvas_h:
        draw.line([(x, 0), (x + canvas_h, canvas_h)], fill=color, width=1)
        x += cell


def _point_in_poly(px, py, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
        j = i
    return inside


def _diamond_points(cx, cy, cell_w, cell_h):
    hw = cell_w / 2.0
    hh = cell_h / 2.0
    return [
        (cx, cy - hh),
        (cx + hw, cy),
        (cx, cy + hh),
        (cx - hw, cy),
    ]


def _sample_diamond_cell(img: Image.Image, polygon):
    px = img.load()
    minx = max(0, int(math.floor(min(p[0] for p in polygon))))
    miny = max(0, int(math.floor(min(p[1] for p in polygon))))
    maxx = min(img.width, int(math.ceil(max(p[0] for p in polygon))))
    maxy = min(img.height, int(math.ceil(max(p[1] for p in polygon))))

    count = 0
    rsum = gsum = bsum = asum = 0

    for y in range(miny, maxy):
        for x in range(minx, maxx):
            if _point_in_poly(x + 0.5, y + 0.5, polygon):
                r, g, b, a = px[x, y]
                if _is_foreground(r, g, b, a):
                    count += 1
                    rsum += r
                    gsum += g
                    bsum += b
                    asum += a

    if count == 0:
        return {
            "occupied": False,
            "pixel_count": 0,
            "color": [0, 0, 0, 0],
        }

    return {
        "occupied": True,
        "pixel_count": count,
        "color": [
            int(rsum / count),
            int(gsum / count),
            int(bsum / count),
            int(asum / count),
        ],
    }


def _build_iso_diamond_cells(img: Image.Image, cell_w=28, cell_h=16):
    img_w, img_h = img.size
    cols = math.ceil(img_w / cell_w)
    rows = math.ceil(img_h / cell_h)

    cells = []
    occupied_count = 0

    for row in range(rows):
        row_offset = (cell_w / 2.0) if (row % 2 == 1) else 0.0
        for col in range(cols):
            cx = col * cell_w + row_offset + cell_w / 2.0
            cy = row * cell_h + cell_h / 2.0
            poly = _diamond_points(cx, cy, cell_w, cell_h)

            cell = {
                "col": col,
                "row": row,
                "cx": cx,
                "cy": cy,
                "polygon": poly,
            }
            sample = _sample_diamond_cell(img, poly)
            cell.update(sample)
            cells.append(cell)
            if cell["occupied"]:
                occupied_count += 1

    if occupied_count == 0:
        occupied_count = 0
        for cell in cells:
            if not cell["occupied"] and cell["pixel_count"] >= 3:
                cell["occupied"] = True
                occupied_count += 1

    return {
        "cell_w": cell_w,
        "cell_h": cell_h,
        "cell_count": len(cells),
        "occupied_count": occupied_count,
        "occupied_ratio": round(occupied_count / max(1, len(cells)), 4),
        "cells": cells,
    }


def _draw_iso_texture_preview(img: Image.Image, cells, out_path: Path):
    base = img.convert("RGBA").copy()
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    outline_color = (148, 243, 222, 80)
    fill_alpha = 150
    border_color = (196, 255, 242, 210)

    for cell in cells:
        poly = cell["polygon"]
        draw.line(poly + [poly[0]], fill=outline_color, width=1)
        if cell["occupied"]:
            r, g, b, a = cell["color"]
            draw.polygon(poly, fill=(r, g, b, fill_alpha))
            draw.line(poly + [poly[0]], fill=border_color, width=2)

    result = Image.alpha_composite(base, overlay)
    result.save(out_path)


def _draw_cage_preview(img: Image.Image, objects: list, out_path: Path):
    preview = img.convert("RGBA").copy()
    overlay = Image.new("RGBA", preview.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    for obj in objects:
        x, y, w, h = obj["bbox"]

        pad = max(8, int(min(w, h) * 0.03))
        gx = max(0, x - pad)
        gy = max(0, y - pad)
        gw = min(preview.width - gx, w + pad * 2)
        gh = min(preview.height - gy, h + pad * 2)
    

        # isometric lattice
        cell = max(24, int(min(preview.width, preview.height) / 24))
        _draw_iso_grid(draw, preview.width, preview.height, cell=cell)


        # center axis
        cx = gx + gw // 2
        draw.line(
            [(cx, gy), (cx, gy + gh)],
            fill=(255, 211, 122, 230),
            width=2,
        )

        label = obj["id"]
        draw.rectangle([gx, max(0, gy - 28), gx + 150, gy], fill=(0, 0, 0, 190))
        draw.text((gx + 8, max(0, gy - 24)), label, fill=(216, 255, 245, 255))

    preview = Image.alpha_composite(preview, overlay)
    preview.save(out_path)


def build_debug_cage_from_image(image_path: str, job_dir: str | None = None) -> dict:
    image_path = Path(image_path)

    if job_dir is None:
        job_dir = image_path.parent

    job_dir = Path(job_dir)
    job_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(image_path).convert("RGBA")
    img.thumbnail((1024, 1024), Image.LANCZOS)

    img_w, img_h = img.size
    bbox = _find_non_bg_bbox(img)

    obj = {
        "id": "object_0",
        "label": "main_iso_grid_cage",
        "bbox": bbox,
        "image_size": [img_w, img_h],
        "cage_type": "isometric_grid_cage",
        "rule": "isometric grid cage only, no humanoid, no glb",
    }

    preview_path = job_dir / "cage_preview.png"
    _draw_cage_preview(img, [obj], preview_path)

    # --- ISO CELL EXTRACTION (diamond sampling) ---
    iso = _build_iso_diamond_cells(img, cell_w=28, cell_h=16)

    iso_json_path = job_dir / "iso_cells.json"
    job_id = uuid.uuid4().hex
    iso_json = {
        "ok": True,
        "mode": "debug_cage_image_only",
        "job_id": job_id,
        "object_count": 1,
        "objects": [obj],
        "cage_preview_url": f"/uploads/{job_dir.name}/cage_preview.png",
        "iso_texture_preview_url": f"/uploads/{job_dir.name}/iso_texture_preview.png",
        "iso_cells_json_url": f"/uploads/{job_dir.name}/iso_cells.json",
        "iso": {
            "cell_w": iso["cell_w"],
            "cell_h": iso["cell_h"],
            "cell_count": iso["cell_count"],
            "occupied_count": iso["occupied_count"],
            "occupied_ratio": iso["occupied_ratio"],
            "cells": iso["cells"],
        },
    }
    iso_json_path.write_text(json.dumps(iso_json, indent=2), encoding="utf-8")

    iso_tex_path = job_dir / "iso_texture_preview.png"
    _draw_iso_texture_preview(img, iso["cells"], iso_tex_path)

    result = {
        "ok": True,
        "mode": "debug_cage_image_only",
        "job_id": job_id,
        "image": str(image_path),
        "object_count": 1,
        "objects": [obj],
        "cage_preview_path": str(preview_path),
        "cage_preview_url": f"/uploads/{job_dir.name}/cage_preview.png",
        "iso_cells_json_path": str(iso_json_path),
        "iso_texture_preview_path": str(iso_tex_path),
        "iso_cells_json_url": f"/uploads/{job_dir.name}/iso_cells.json",
        "iso_texture_preview_url": f"/uploads/{job_dir.name}/iso_texture_preview.png",
        "iso": {
            "cell_w": iso["cell_w"],
            "cell_h": iso["cell_h"],
            "cell_count": iso["cell_count"],
            "occupied_count": iso["occupied_count"],
            "occupied_ratio": iso["occupied_ratio"],
        },
        "rule": "This draws isometric grid cage overlay on uploaded image. No 3D. No humanoid. No GLB.",
    }

    out = job_dir / "debug_cage_detect.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    result["debug_json_path"] = str(out)
    return result