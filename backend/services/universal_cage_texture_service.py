from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import json
import shutil

from PIL import Image, ImageEnhance, ImageOps, ImageDraw


TEXTURE_SIZE = 2048


def _open_image(path: Optional[str]) -> Optional[Image.Image]:
    if not path:
        return None

    p = Path(path)
    if not p.exists():
        return None

    return Image.open(p).convert("RGBA")


def _fit_to_box(img: Image.Image, size: Tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))

    copy = img.copy()
    copy.thumbnail(size, Image.LANCZOS)

    x = (size[0] - copy.width) // 2
    y = (size[1] - copy.height) // 2
    canvas.paste(copy, (x, y), copy)

    return canvas


def _crop_projection(
    img: Image.Image,
    projection: str,
) -> Image.Image:
    w, h = img.size

    if projection == "left":
        return img.crop((0, 0, w // 2, h))

    if projection == "right":
        return img.crop((w // 2, 0, w, h))

    if projection == "center":
        margin = int(w * 0.18)
        return img.crop((margin, 0, w - margin, h))

    return img


def _paste_uv(
    atlas: Image.Image,
    source: Image.Image,
    uv_min: list,
    uv_max: list,
    projection: str,
) -> None:
    size = atlas.size[0]

    x0 = int(uv_min[0] * size)
    y0 = int((1.0 - uv_max[1]) * size)
    x1 = int(uv_max[0] * size)
    y1 = int((1.0 - uv_min[1]) * size)

    box_w = max(1, x1 - x0)
    box_h = max(1, y1 - y0)

    projected = _crop_projection(source, projection)
    fitted = _fit_to_box(projected, (box_w, box_h))

    atlas.alpha_composite(fitted, (x0, y0))


def _draw_debug_uv(
    atlas: Image.Image,
    cage: Dict[str, Any],
) -> Image.Image:
    debug = atlas.copy()
    draw = ImageDraw.Draw(debug)
    size = debug.size[0]

    for zone in cage.get("zones", []):
        for uv in zone.get("uv_zones", []) or []:
            uv_min = uv.get("uv_min", [0, 0])
            uv_max = uv.get("uv_max", [1, 1])

            x0 = int(uv_min[0] * size)
            y0 = int((1.0 - uv_max[1]) * size)
            x1 = int(uv_max[0] * size)
            y1 = int((1.0 - uv_min[1]) * size)

            draw.rectangle((x0, y0, x1, y1), outline=(255, 220, 90, 255), width=2)
            draw.text((x0 + 6, y0 + 6), uv.get("name", "uv"), fill=(255, 255, 255, 255))

    return debug


def _make_fallback_views(front: Image.Image) -> Dict[str, Image.Image]:
    side = ImageEnhance.Contrast(front.copy()).enhance(0.85)
    side = side.resize((max(1, int(side.width * 0.58)), side.height), Image.LANCZOS)

    side_canvas = Image.new("RGBA", front.size, (0, 0, 0, 0))
    side_canvas.paste(side, ((front.width - side.width) // 2, 0), side)

    back = ImageOps.mirror(front.copy())
    back = ImageEnhance.Brightness(back).enhance(0.78)
    back = ImageEnhance.Contrast(back).enhance(0.75)

    return {
        "front": front,
        "back": back,
        "left": side_canvas,
        "right": ImageOps.mirror(side_canvas),
    }


def build_universal_cage_texture(
    cage: Dict[str, Any],
    job_dir: str,
    front_image_path: str,
    back_image_path: Optional[str] = None,
    left_image_path: Optional[str] = None,
    right_image_path: Optional[str] = None,
    texture_size: int = TEXTURE_SIZE,
    make_debug: bool = True,
) -> Dict[str, Any]:
    job_path = Path(job_dir)
    texture_dir = job_path / "cage_texture"
    texture_dir.mkdir(parents=True, exist_ok=True)

    front = _open_image(front_image_path)
    if front is None:
        raise ValueError(f"Front image not found: {front_image_path}")

    front = front.convert("RGBA")

    fallback = _make_fallback_views(front)

    views = {
        "front": front,
        "back": _open_image(back_image_path) or fallback["back"],
        "left": _open_image(left_image_path) or fallback["left"],
        "right": _open_image(right_image_path) or fallback["right"],
    }

    atlas = Image.new("RGBA", (texture_size, texture_size), (0, 0, 0, 0))

    projection_records = []

    for zone in cage.get("zones", []):
        zone_name = zone.get("name", "unknown_zone")

        for uv in zone.get("uv_zones", []) or []:
            projection = uv.get("projection", "front")
            source = views.get(projection) or views["front"]

            _paste_uv(
                atlas=atlas,
                source=source,
                uv_min=uv.get("uv_min", [0, 0]),
                uv_max=uv.get("uv_max", [1, 1]),
                projection="center",
            )

            projection_records.append(
                {
                    "zone": zone_name,
                    "uv_name": uv.get("name"),
                    "projection": projection,
                    "uv_min": uv.get("uv_min"),
                    "uv_max": uv.get("uv_max"),
                    "source": projection,
                    "rule": "image projected onto cage UV zone",
                }
            )

    cage_texture_path = texture_dir / "cage_texture.png"
    atlas.save(cage_texture_path)

    debug_path = None
    if make_debug:
        debug = _draw_debug_uv(atlas, cage)
        debug_path = texture_dir / "cage_texture_debug.png"
        debug.save(debug_path)

    uv_map = {
        "version": "universal_cage_texture_v1",
        "texture_size": texture_size,
        "cage_id": cage.get("cage_id"),
        "cage_type": cage.get("cage_type"),
        "asset_type": cage.get("asset_type"),
        "texture_file": str(cage_texture_path),
        "debug_file": str(debug_path) if debug_path else None,
        "projection_records": projection_records,
        "rule": "texture belongs to cage surface, shell mounts above it",
    }

    uv_map_path = texture_dir / "cage_uv_projection_map.json"
    uv_map_path.write_text(json.dumps(uv_map, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "message": "Universal cage texture generated",
        "cage_texture_path": str(cage_texture_path),
        "debug_texture_path": str(debug_path) if debug_path else None,
        "uv_map_path": str(uv_map_path),
        "uv_map": uv_map,
    }


def copy_cage_texture_to_output(
    texture_result: Dict[str, Any],
    output_dir: str,
) -> Dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    copied = {}

    for key in ["cage_texture_path", "debug_texture_path", "uv_map_path"]:
        src = texture_result.get(key)
        if not src:
            continue

        src_path = Path(src)
        if src_path.exists():
            dst = out / src_path.name
            shutil.copy2(src_path, dst)
            copied[key] = str(dst)

    return {
        "ok": True,
        "copied": copied,
    }