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
        return [120, 120, 120, alpha]

    hex_color = hex_color.replace("#", "")

    if len(hex_color) != 6:
        return [120, 120, 120, alpha]

    return [
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
        alpha,
    ]


def make_material(name, color, alpha=255, metallic=0.05, roughness=0.75):
    return trimesh.visual.material.PBRMaterial(
        name=name,
        baseColorFactor=hex_to_rgba(color, alpha),
        metallicFactor=metallic,
        roughnessFactor=roughness,
        alphaMode="BLEND" if alpha < 255 else "OPAQUE",
    )


def add(scene, mesh, name):
    scene.add_geometry(mesh, node_name=name)


def box(size, pos, material):
    mesh = trimesh.creation.box(extents=size)
    mesh.visual.material = material
    mesh.apply_translation(pos)
    return mesh


def cylinder(radius, height, pos, material):
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
    mesh.visual.material = material
    mesh.apply_translation(pos)
    return mesh


def sphere(radius, pos, material):
    mesh = trimesh.creation.uv_sphere(radius=radius, count=[32, 16])
    mesh.visual.material = material
    mesh.apply_translation(pos)
    return mesh


def cone(radius, height, pos, material):
    mesh = trimesh.creation.cone(radius=radius, height=height, sections=32)
    mesh.visual.material = material
    mesh.apply_translation(pos)
    return mesh


def capsule_between(a, b, radius, material):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    vec = b - a
    length = float(np.linalg.norm(vec))

    if length <= 0.0001:
        return sphere(radius, a.tolist(), material)

    mid = (a + b) / 2
    mesh = trimesh.creation.capsule(radius=radius, height=length)

    direction = vec / length
    axis = np.cross([0, 0, 1], direction)
    axis_len = np.linalg.norm(axis)

    if axis_len > 0.0001:
        axis = axis / axis_len
        angle = np.arccos(np.clip(np.dot([0, 0, 1], direction), -1.0, 1.0))
        mesh.apply_transform(trimesh.transformations.rotation_matrix(angle, axis))

    mesh.visual.material = material
    mesh.apply_translation(mid)
    return mesh


def build_irregular_rock(width, height, depth, material):
    verts = []
    faces = []
    rings = 4
    sections = 10

    for r in range(rings):
        y = (r / (rings - 1)) * height
        scale = 1.0 - abs((r / (rings - 1)) - 0.5) * 0.45

        for i in range(sections):
            ang = 2 * math.pi * i / sections
            wobble = 0.82 + 0.22 * math.sin(i * 1.7 + r)
            x = math.cos(ang) * width * 0.5 * scale * wobble
            z = math.sin(ang) * depth * 0.5 * scale * wobble
            verts.append([x, y, z])

    for r in range(rings - 1):
        for i in range(sections):
            j = (i + 1) % sections
            a = r * sections + i
            b = r * sections + j
            c = (r + 1) * sections + i
            d = (r + 1) * sections + j
            faces.append([a, b, d])
            faces.append([a, d, c])

    mesh = trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces), process=True)
    mesh.visual.material = material
    return mesh


def build_fixture_scene(fixture_type="crate", opts=None):
    opts = opts or {}
    fixture_type = (fixture_type or "crate").lower().strip()

    scene = trimesh.Scene()

    wood = make_material("wood", "#8a5a2b")
    dark_wood = make_material("dark_wood", "#4a2d18")
    stone = make_material("stone", "#777777")
    grass = make_material("grass", "#3c7a3e")
    leaf = make_material("leaf", "#2f8a3a")
    water = make_material("water", "#4bb7ff", alpha=130, roughness=0.2)
    road = make_material("road", "#4f4a45")
    metal = make_material("metal", "#888888", metallic=0.35, roughness=0.35)
    light = make_material("light", "#ffe08a", alpha=230, roughness=0.15)
    wall = make_material("wall", "#9c8b72")
    roof = make_material("roof", "#7a2f2f")

    if fixture_type == "building":
        add(scene, box([1.6, 1.25, 1.2], [0, 0.625, 0], wall), "building_body")
        add(scene, cone(1.05, 0.55, [0, 1.55, 0], roof), "roof")
        add(scene, box([0.32, 0.55, 0.06], [0, 0.35, 0.63], dark_wood), "door")
        add(scene, box([0.25, 0.25, 0.06], [-0.48, 0.75, 0.63], water), "window_left")
        add(scene, box([0.25, 0.25, 0.06], [0.48, 0.75, 0.63], water), "window_right")

    elif fixture_type == "tree":
        add(scene, cylinder(0.16, 1.05, [0, 0.525, 0], wood), "trunk")
        add(scene, sphere(0.62, [0, 1.35, 0], leaf), "leaf_crown")
        add(scene, sphere(0.38, [-0.35, 1.2, 0.05], leaf), "leaf_left")
        add(scene, sphere(0.38, [0.35, 1.2, -0.05], leaf), "leaf_right")

    elif fixture_type == "bridge":
        add(scene, box([2.6, 0.16, 0.9], [0, 0.45, 0], wood), "bridge_deck")
        add(scene, box([0.12, 0.45, 0.12], [-1.0, 0.22, -0.32], dark_wood), "support_1")
        add(scene, box([0.12, 0.45, 0.12], [1.0, 0.22, -0.32], dark_wood), "support_2")
        add(scene, box([0.12, 0.45, 0.12], [-1.0, 0.22, 0.32], dark_wood), "support_3")
        add(scene, box([0.12, 0.45, 0.12], [1.0, 0.22, 0.32], dark_wood), "support_4")
        add(scene, capsule_between([-1.25, 0.75, -0.45], [1.25, 0.75, -0.45], 0.035, dark_wood), "rail_left")
        add(scene, capsule_between([-1.25, 0.75, 0.45], [1.25, 0.75, 0.45], 0.035, dark_wood), "rail_right")

    elif fixture_type == "hill":
        add(scene, sphere(0.95, [0, 0.05, 0], grass), "hill_mound")
        scene.geometry["hill_mound"].apply_scale([1.4, 0.42, 1.1])

    elif fixture_type == "rock":
        mesh = build_irregular_rock(0.9, 0.55, 0.75, stone)
        mesh.apply_translation([0, 0, 0])
        add(scene, mesh, "irregular_rock")

    elif fixture_type == "road":
        add(scene, box([0.85, 0.04, 3.2], [0, 0.02, 0], road), "road_strip")
        add(scene, box([0.04, 0.045, 3.2], [-0.32, 0.05, 0], make_material("road_line", "#dddddd")), "left_line")
        add(scene, box([0.04, 0.045, 3.2], [0.32, 0.05, 0], make_material("road_line", "#dddddd")), "right_line")

    elif fixture_type == "water":
        add(scene, box([2.2, 0.035, 2.2], [0, 0.02, 0], water), "water_plane")

    elif fixture_type == "table":
        add(scene, box([1.15, 0.12, 0.8], [0, 0.75, 0], wood), "table_top")
        for x in [-0.45, 0.45]:
            for z in [-0.3, 0.3]:
                add(scene, cylinder(0.045, 0.7, [x, 0.35, z], dark_wood), f"table_leg_{x}_{z}")

    elif fixture_type == "chair":
        add(scene, box([0.55, 0.10, 0.55], [0, 0.45, 0], wood), "chair_seat")
        add(scene, box([0.55, 0.65, 0.08], [0, 0.82, -0.25], wood), "chair_back")
        for x in [-0.22, 0.22]:
            for z in [-0.22, 0.22]:
                add(scene, cylinder(0.035, 0.45, [x, 0.22, z], dark_wood), f"chair_leg_{x}_{z}")

    elif fixture_type == "lamp":
        add(scene, cylinder(0.06, 1.35, [0, 0.675, 0], metal), "lamp_pole")
        add(scene, sphere(0.18, [0, 1.45, 0], light), "lamp_light")
        add(scene, cylinder(0.18, 0.08, [0, 0.04, 0], metal), "lamp_base")

    elif fixture_type == "barrel":
        add(scene, cylinder(0.28, 0.85, [0, 0.425, 0], wood), "barrel_body")
        add(scene, cylinder(0.30, 0.035, [0, 0.18, 0], metal), "barrel_ring_low")
        add(scene, cylinder(0.30, 0.035, [0, 0.68, 0], metal), "barrel_ring_high")

    elif fixture_type == "signboard":
        add(scene, cylinder(0.045, 0.9, [0, 0.45, 0], wood), "sign_post")
        add(scene, box([0.95, 0.42, 0.08], [0, 1.05, 0], wood), "sign_board")

    else:
        add(scene, box([0.72, 0.72, 0.72], [0, 0.36, 0], wood), "crate_body")
        add(scene, box([0.08, 0.78, 0.08], [-0.26, 0.36, 0.38], dark_wood), "crate_strap_1")
        add(scene, box([0.08, 0.78, 0.08], [0.26, 0.36, 0.38], dark_wood), "crate_strap_2")
        fixture_type = "crate"

    return scene, fixture_type


def build_world_fixture_from_form(build_form: dict):
    build_form = build_form or {}
    fixture_type = build_form.get("fixture_type") or build_form.get("type") or "crate"

    scene, fixture_type = build_fixture_scene(fixture_type, build_form)

    job_id = uuid.uuid4().hex
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    out_path = job_dir / "model.glb"
    scene.export(out_path)

    metadata = {
        "asset_type": "world_fixture",
        "fixture_type": fixture_type,
        "supported_types": [
            "building", "tree", "bridge", "hill", "rock", "road", "water",
            "table", "chair", "lamp", "crate", "barrel", "signboard",
        ],
    }

    meta_path = job_dir / "world_fixture_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2))

    return {
        "ok": True,
        "job_id": job_id,
        "model_path": str(out_path),
        "model_url": f"/outputs/{job_id}/model.glb",
        "metadata_path": str(meta_path),
        "metadata_url": f"/outputs/{job_id}/world_fixture_metadata.json",
        "asset_type": "world_fixture",
        "fixture_type": fixture_type,
    }


def build_world_fixture(
    fixture_type="crate",
    style="lowpoly",
    seed=None,
    **kwargs,
):
    if seed is not None:
        random.seed(seed)

    build_form = {
        "fixture_type": fixture_type,
        "style": style,
        **kwargs,
    }

    return build_world_fixture_from_form(build_form)