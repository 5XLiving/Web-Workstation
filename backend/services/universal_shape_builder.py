from pathlib import Path
import trimesh
import numpy as np


def make_material(name, color):
    return trimesh.visual.material.PBRMaterial(
        name=name,
        baseColorFactor=color,
        metallicFactor=0.0,
        roughnessFactor=0.85,
    )


def apply_transform(mesh, part):
    mesh.apply_scale(part.get("scale", [1, 1, 1]))
    mesh.apply_translation(part.get("position", [0, 0, 0]))
    return mesh


def build_box(part):
    mesh = trimesh.creation.box(extents=[1, 1, 1])
    return apply_transform(mesh, part)


def build_sphere(part):
    mesh = trimesh.creation.icosphere(subdivisions=2, radius=1.0)
    return apply_transform(mesh, part)


def build_cylinder(part):
    mesh = trimesh.creation.cylinder(radius=0.5, height=1.0, sections=16)
    return apply_transform(mesh, part)


def build_capsule(part):
    mesh = trimesh.creation.capsule(radius=0.35, height=1.0, count=[12, 12])
    return apply_transform(mesh, part)


def build_flat_plate(part):
    mesh = trimesh.creation.box(extents=[1, 0.08, 1])
    return apply_transform(mesh, part)


def build_armor_plate(part):
    mesh = trimesh.creation.box(extents=[1, 0.12, 1])
    mesh = apply_transform(mesh, part)
    return mesh


def build_tapered_box(part):
    sx, sy, sz = part.get("scale", [1, 1, 1])
    taper_top = part.get("taper_top", 0.65)

    bottom = np.array([
        [-0.5, -0.5, -0.5],
        [ 0.5, -0.5, -0.5],
        [ 0.5, -0.5,  0.5],
        [-0.5, -0.5,  0.5],
    ])

    top = np.array([
        [-0.5 * taper_top, 0.5, -0.5 * taper_top],
        [ 0.5 * taper_top, 0.5, -0.5 * taper_top],
        [ 0.5 * taper_top, 0.5,  0.5 * taper_top],
        [-0.5 * taper_top, 0.5,  0.5 * taper_top],
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
    mesh.apply_scale([sx, sy, sz])
    mesh.apply_translation(part.get("position", [0, 0, 0]))
    return mesh


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
        return build_armor_plate(part)
    if shape == "tapered_box":
        return build_tapered_box(part)

    return build_box(part)


def build_universal_model(plan: dict, output_dir: str) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scene = trimesh.Scene()

    all_parts = []
    all_parts.extend(plan.get("parts", []))
    all_parts.extend(plan.get("details", []))

    for part in all_parts:
        mesh = build_shape(part)

        color = part.get("color", [0.6, 0.6, 0.6, 1])
        mesh.visual.material = make_material(part.get("name", "part"), color)

        scene.add_geometry(mesh, node_name=part.get("name", "part"))

    model_path = output_dir / "model.glb"
    scene.export(model_path)

    return {
        "model_glb": str(model_path),
        "style": plan.get("style", "lowpoly_universal_builder_v2"),
        "plan": plan,
    }