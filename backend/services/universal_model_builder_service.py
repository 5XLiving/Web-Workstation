from pathlib import Path
from typing import Any, Dict, List
import math

import numpy as np
import trimesh


def make_material(name, color):
    return trimesh.visual.material.PBRMaterial(
        name=name,
        baseColorFactor=color,
        metallicFactor=0.0,
        roughnessFactor=0.85,
    )


def _to_vec3(value, default=None):
    if default is None:
        default = [0, 0, 0]

    if isinstance(value, dict):
        return [
            float(value.get("x", default[0])),
            float(value.get("y", default[1])),
            float(value.get("z", default[2])),
        ]

    if isinstance(value, (list, tuple)) and len(value) >= 3:
        return [float(value[0]), float(value[1]), float(value[2])]

    return default


def apply_transform(mesh, part):
    mesh.apply_scale(_to_vec3(part.get("scale"), [1, 1, 1]))

    rx, ry, rz = [math.radians(v) for v in _to_vec3(part.get("rotation"), [0, 0, 0])]

    if rx:
        mesh.apply_transform(trimesh.transformations.rotation_matrix(rx, [1, 0, 0]))
    if ry:
        mesh.apply_transform(trimesh.transformations.rotation_matrix(ry, [0, 1, 0]))
    if rz:
        mesh.apply_transform(trimesh.transformations.rotation_matrix(rz, [0, 0, 1]))

    mesh.apply_translation(_to_vec3(part.get("position"), [0, 0, 0]))
    return mesh


def build_box(part):
    return apply_transform(trimesh.creation.box(extents=[1, 1, 1]), part)


def build_sphere(part):
    return apply_transform(trimesh.creation.icosphere(subdivisions=2, radius=1.0), part)


def build_cylinder(part):
    return apply_transform(trimesh.creation.cylinder(radius=0.5, height=1.0, sections=16), part)


def build_capsule(part):
    return apply_transform(trimesh.creation.capsule(radius=0.35, height=1.0, count=[12, 12]), part)


def build_flat_plate(part):
    return apply_transform(trimesh.creation.box(extents=[1, 0.08, 1]), part)


def build_tapered_box(part):
    sx, sy, sz = _to_vec3(part.get("scale"), [1, 1, 1])
    taper_top = float(part.get("taper_top", 0.65))

    bottom = np.array([
        [-0.5, -0.5, -0.5],
        [0.5, -0.5, -0.5],
        [0.5, -0.5, 0.5],
        [-0.5, -0.5, 0.5],
    ])

    top = np.array([
        [-0.5 * taper_top, 0.5, -0.5 * taper_top],
        [0.5 * taper_top, 0.5, -0.5 * taper_top],
        [0.5 * taper_top, 0.5, 0.5 * taper_top],
        [-0.5 * taper_top, 0.5, 0.5 * taper_top],
    ])

    vertices = np.vstack([bottom, top])
    faces = np.array([
        [0, 1, 2], [0, 2, 3],
        [4, 6, 5], [4, 7, 6],
        [0, 4, 5], [0, 5, 1],
        [1, 5, 6], [1, 6, 2],
        [2, 6, 7], [2, 7, 3],
        [3, 7, 4], [3, 4, 0],
    ])

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)

    part_copy = dict(part)
    part_copy["scale"] = [sx, sy, sz]
    return apply_transform(mesh, part_copy)


def build_shape(part):
    shape = part.get("shape", "box")

    if shape == "sphere":
        return build_sphere(part)
    if shape == "cylinder":
        return build_cylinder(part)
    if shape == "capsule":
        return build_capsule(part)
    if shape == "flat_plate":
        return build_flat_plate(part)
    if shape == "armor_plate":
        return build_flat_plate(part)
    if shape == "tapered_box":
        return build_tapered_box(part)

    return build_box(part)


def build_universal_model(plan: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scene = trimesh.Scene()

    all_parts: List[Dict[str, Any]] = []
    all_parts.extend(plan.get("parts", []))
    all_parts.extend(plan.get("details", []))

    if not all_parts:
        return {
            "ok": False,
            "error": "No parts/details found in plan",
            "model_glb": None,
            "part_count": 0,
            "style": plan.get("style", "lowpoly_universal_builder_v2"),
        }

    for index, part in enumerate(all_parts):
        mesh = build_shape(part)

        name = part.get("name", f"part_{index + 1}")
        color = part.get("color", [0.6, 0.6, 0.6, 1])

        mesh.visual.material = make_material(name, color)
        scene.add_geometry(mesh, node_name=name)

    model_path = output_dir / "model.glb"
    scene.export(str(model_path))

    return {
        "ok": True,
        "model_glb": str(model_path),
        "part_count": len(all_parts),
        "style": plan.get("style", "lowpoly_universal_builder_v2"),
    }
