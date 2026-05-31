from pathlib import Path
import uuid
import json
import math
import random
import trimesh
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "storage" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def hex_to_rgba(hex_color: str, alpha=255):
    if not hex_color:
        return [90, 130, 70, alpha]

    hex_color = hex_color.replace("#", "")

    if len(hex_color) != 6:
        return [90, 130, 70, alpha]

    return [
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
        alpha
    ]


def make_material(name, color, alpha=255):
    return trimesh.visual.material.PBRMaterial(
        name=name,
        baseColorFactor=hex_to_rgba(color, alpha),
        metallicFactor=0.02,
        roughnessFactor=0.85,
        alphaMode="BLEND" if alpha < 255 else "OPAQUE"
    )


def build_height_value(x, z, shape, height_mode, width, depth):
    if height_mode == "flat":
        return 0.0

    # smooth random-like terrain from multiple wave points
    h = (
        math.sin(x * 1.7 + z * 0.8) * 0.12 +
        math.sin(x * 2.8 - z * 1.3) * 0.07 +
        math.cos(z * 2.2) * 0.06
    )

    # soften border for round/irregular
    nx = x / max(width / 2, 0.001)
    nz = z / max(depth / 2, 0.001)
    dist = math.sqrt(nx * nx + nz * nz)

    if shape in ["round", "irregular"]:
        h *= max(0.15, 1.0 - dist * 0.35)

    return h


def inside_shape(x, z, shape, width, depth):
    nx = x / max(width / 2, 0.001)
    nz = z / max(depth / 2, 0.001)

    if shape == "square":
        return True

    if shape == "round":
        return (nx * nx + nz * nz) <= 1.0

    if shape == "irregular":
        angle = math.atan2(nz, nx)
        radius_limit = 0.78 + 0.16 * math.sin(angle * 3.0) + 0.09 * math.cos(angle * 5.0)
        dist = math.sqrt(nx * nx + nz * nz)
        return dist <= radius_limit

    return True


def build_terrain_mesh(
    shape="square",
    height_mode="flat",
    width=4.0,
    depth=4.0,
    base_thickness=0.18,
    segments=24
):
    vertices_top = []
    vertices_bottom = []
    index_map = {}

    for iz in range(segments + 1):
        z = -depth / 2 + depth * iz / segments

        for ix in range(segments + 1):
            x = -width / 2 + width * ix / segments

            if not inside_shape(x, z, shape, width, depth):
                continue

            y = build_height_value(x, z, shape, height_mode, width, depth)

            index_map[(ix, iz)] = len(vertices_top)
            vertices_top.append([x, y, z])
            vertices_bottom.append([x, -base_thickness, z])

    vertices = vertices_top + vertices_bottom
    bottom_offset = len(vertices_top)

    faces = []

    for iz in range(segments):
        for ix in range(segments):
            keys = [
                (ix, iz),
                (ix + 1, iz),
                (ix, iz + 1),
                (ix + 1, iz + 1)
            ]

            if not all(k in index_map for k in keys):
                continue

            a = index_map[(ix, iz)]
            b = index_map[(ix + 1, iz)]
            c = index_map[(ix, iz + 1)]
            d = index_map[(ix + 1, iz + 1)]

            faces.append([a, b, d])
            faces.append([a, d, c])

            faces.append([bottom_offset + a, bottom_offset + d, bottom_offset + b])
            faces.append([bottom_offset + a, bottom_offset + c, bottom_offset + d])

    # side walls along missing-neighbor borders
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for (ix, iz), top_i in index_map.items():
        for dx, dz in directions:
            nk = (ix + dx, iz + dz)

            if nk in index_map:
                continue

            # create small side face to neighbor direction using nearest cell edge approximation
            x, y, z = vertices_top[top_i]
            bx, by, bz = vertices_bottom[top_i]

            x2 = x + (width / segments) * dx * 0.5
            z2 = z + (depth / segments) * dz * 0.5

            v1 = len(vertices)
            vertices.append([x, y, z])
            v2 = len(vertices)
            vertices.append([x2, y, z2])
            v3 = len(vertices)
            vertices.append([x2, -base_thickness, z2])
            v4 = len(vertices)
            vertices.append([bx, by, bz])

            faces.append([v1, v2, v3])
            faces.append([v1, v3, v4])

    mesh = trimesh.Trimesh(
        vertices=np.array(vertices),
        faces=np.array(faces),
        process=True
    )

    mesh.visual.material = make_material("terrain_surface", "#4f7f3a")
    return mesh


def build_terrain_from_form(build_form: dict):
    shape = build_form.get("shape") or build_form.get("terrain_shape") or "square"
    height_mode = build_form.get("height_mode") or "flat"

    width = float(build_form.get("width") or 4.0)
    depth = float(build_form.get("depth") or 4.0)
    base_thickness = float(build_form.get("height") or 0.18)
    segments = int(build_form.get("segments") or 24)

    if shape not in ["square", "round", "irregular"]:
        shape = "square"

    if height_mode not in ["flat", "random_multi_point"]:
        height_mode = "flat"

    mesh = build_terrain_mesh(
        shape=shape,
        height_mode=height_mode,
        width=width,
        depth=depth,
        base_thickness=base_thickness,
        segments=segments
    )

    scene = trimesh.Scene()
    scene.add_geometry(mesh, node_name=f"{shape}_{height_mode}_terrain")

    job_id = uuid.uuid4().hex
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    out_path = job_dir / "model.glb"
    scene.export(out_path)

    metadata = {
        "asset_type": "terrain",
        "shape": shape,
        "height_mode": height_mode,
        "width": width,
        "depth": depth,
        "height": base_thickness,
        "segments": segments,
        "rules": {
            "square": "grid terrain tile",
            "round": "radial terrain island",
            "irregular": "organic uneven landmass",
            "flat": "same height surface",
            "random_multi_point": "generated wave-control height variation"
        }
    }

    meta_path = job_dir / "terrain_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2))

    return {
        "job_id": job_id,
        "model_path": str(out_path),
        "model_url": f"/outputs/{job_id}/model.glb",
        "metadata_path": str(meta_path),
        "metadata_url": f"/outputs/{job_id}/terrain_metadata.json",
        "asset_type": "terrain",
        "shape": shape,
        "height_mode": height_mode
    } 
