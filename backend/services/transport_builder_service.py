from pathlib import Path
import uuid
import json
import math
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
        alpha
    ]


def mat(name, color, alpha=255, metallic=0.35, roughness=0.45):
    return trimesh.visual.material.PBRMaterial(
        name=name,
        baseColorFactor=hex_to_rgba(color, alpha),
        metallicFactor=metallic,
        roughnessFactor=roughness,
        alphaMode="BLEND" if alpha < 255 else "OPAQUE"
    )


def add(scene, mesh, name):
    scene.add_geometry(mesh, node_name=name)


def box(size, pos, material):
    mesh = trimesh.creation.box(extents=size)
    mesh.visual.material = material
    mesh.apply_translation(pos)
    return mesh


def cylinder(radius, height, pos, material, axis="z"):
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=32)

    if axis == "x":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    elif axis == "y":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))

    mesh.visual.material = material
    mesh.apply_translation(pos)
    return mesh


def sphere(radius, pos, material):
    mesh = trimesh.creation.uv_sphere(radius=radius, count=[32, 16])
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
    transform = trimesh.geometry.align_vectors(np.array([0, 0, 1.0]), direction)
    mesh.apply_transform(transform)
    mesh.visual.material = material
    mesh.apply_translation(mid)
    return mesh


def resolve_transport_profile(profile=None):
    profile = (profile or "car").lower().strip()

    profiles = {
        "bike": {"wheel_count": 2, "mode": "ground", "width": 0.55, "height": 0.65, "body": "bike"},
        "car": {"wheel_count": 4, "mode": "ground", "width": 1.25, "height": 0.75, "body": "car"},
        "lorry": {"wheel_count": 6, "mode": "ground", "width": 1.45, "height": 1.05, "body": "lorry"},
        "tank": {"wheel_count": 6, "mode": "ground", "width": 1.6, "height": 0.8, "body": "tank"},

        "drone": {"wheel_count": 2, "mode": "flying", "width": 1.0, "height": 0.35, "body": "drone"},
        "helicopter": {"wheel_count": 4, "mode": "flying", "width": 1.3, "height": 0.55, "body": "helicopter"},
        "airplane": {"wheel_count": 6, "mode": "flying", "width": 1.6, "height": 0.5, "body": "airplane"},
    }

    return profiles.get(profile, profiles["car"])


def wheel_positions(wheel_count, length, width, y):
    if wheel_count == 2:
        return [
            {"name": "front", "x": 0, "y": y, "z": length * 0.36},
            {"name": "rear", "x": 0, "y": y, "z": -length * 0.36},
        ]

    if wheel_count == 4:
        return [
            {"name": "front_left", "x": -width * 0.52, "y": y, "z": length * 0.34},
            {"name": "front_right", "x": width * 0.52, "y": y, "z": length * 0.34},
            {"name": "rear_left", "x": -width * 0.52, "y": y, "z": -length * 0.34},
            {"name": "rear_right", "x": width * 0.52, "y": y, "z": -length * 0.34},
        ]

    return [
        {"name": "front_left", "x": -width * 0.52, "y": y, "z": length * 0.38},
        {"name": "front_right", "x": width * 0.52, "y": y, "z": length * 0.38},
        {"name": "mid_left", "x": -width * 0.52, "y": y, "z": 0},
        {"name": "mid_right", "x": width * 0.52, "y": y, "z": 0},
        {"name": "rear_left", "x": -width * 0.52, "y": y, "z": -length * 0.38},
        {"name": "rear_right", "x": width * 0.52, "y": y, "z": -length * 0.38},
    ]


def build_transport_model(profile="car", build_form=None):
    cfg = resolve_transport_profile(profile)
    build_form = build_form or {}

    wheel_count = int(build_form.get("wheel_count") or cfg["wheel_count"])
    mode = build_form.get("mode") or cfg["mode"]
    body_type = build_form.get("body_type") or cfg["body"]

    length = 1.55 + (wheel_count * 0.38)
    width = float(build_form.get("width") or cfg["width"])
    height = float(build_form.get("height") or cfg["height"])

    body_mat = mat("transport_body", "#5f6f80")
    dark_mat = mat("dark_detail", "#16191d")
    wheel_mat = mat("wheel_or_hover_rotor", "#111111")
    glow_mat = mat("hover_glow", "#00d4ff", alpha=180, metallic=0.1, roughness=0.2)
    glass_mat = mat("glass", "#7fb7ff", alpha=120, metallic=0.05, roughness=0.15)

    scene = trimesh.Scene()
    sockets = {}

    body_y = 0.65

    add(scene, box([width, height, length], [0, body_y, 0], body_mat), "main_body")

    if body_type in ["car", "lorry", "tank"]:
        add(scene, box([width * 0.65, height * 0.45, length * 0.35], [0, body_y + height * 0.55, length * 0.05], glass_mat), "cabin")
    elif body_type == "bike":
        add(scene, capsule_between([0, body_y, -length * 0.25], [0, body_y + 0.25, length * 0.25], 0.08, body_mat), "bike_frame")
        add(scene, box([0.35, 0.12, 0.28], [0, body_y + 0.35, -0.05], dark_mat), "bike_seat")
    elif body_type == "drone":
        add(scene, capsule_between([-width * 0.5, body_y, 0], [width * 0.5, body_y, 0], 0.055, body_mat), "drone_crossbar")
    elif body_type == "helicopter":
        add(scene, cylinder(width * 0.45, 0.035, [0, body_y + height * 0.8, 0], dark_mat, axis="y"), "top_main_rotor")
        add(scene, capsule_between([0, body_y, -length * 0.35], [0, body_y, -length * 0.72], 0.06, body_mat), "tail_boom")
    elif body_type == "airplane":
        add(scene, box([width * 2.2, 0.06, length * 0.32], [0, body_y + 0.05, 0], body_mat), "main_wings")
        add(scene, box([width * 0.9, 0.05, length * 0.16], [0, body_y + 0.12, -length * 0.48], body_mat), "tail_wing")

    wheel_y = 0.22
    positions = wheel_positions(wheel_count, length, width, wheel_y)

    for p in positions:
        sockets[p["name"]] = {"x": p["x"], "y": p["y"], "z": p["z"]}

        if mode == "ground":
            # vertical side wheel
            axis = "x" if abs(p["x"]) > 0.01 else "x"
            add(scene, cylinder(0.20, 0.16, [p["x"], p["y"], p["z"]], wheel_mat, axis=axis), f"{p['name']}_vertical_wheel")
            add(scene, sphere(0.055, [p["x"], p["y"], p["z"]], dark_mat), f"{p['name']}_wheel_axle_joint")
        else:
            # flying transport: wheel slot becomes horizontal hover rotor
            add(scene, cylinder(0.24, 0.035, [p["x"], p["y"] + 0.18, p["z"]], wheel_mat, axis="y"), f"{p['name']}_horizontal_hover_rotor")
            add(scene, cylinder(0.28, 0.02, [p["x"], p["y"] + 0.14, p["z"]], glow_mat, axis="y"), f"{p['name']}_hover_glow_disc")
            add(scene, sphere(0.05, [p["x"], p["y"] + 0.18, p["z"]], glow_mat), f"{p['name']}_hover_axle_joint")

    if body_type == "tank":
        add(scene, box([0.35, 0.28, 0.35], [0, body_y + height * 0.72, 0.1], dark_mat), "turret")
        add(scene, capsule_between([0, body_y + height * 0.72, 0.25], [0, body_y + height * 0.72, 1.05], 0.045, dark_mat), "tank_barrel")

    job_id = uuid.uuid4().hex
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    out_path = job_dir / "model.glb"
    scene.export(out_path)

    metadata = {
        "asset_type": "transport",
        "profile": profile,
        "mode": mode,
        "body_type": body_type,
        "wheel_count": wheel_count,
        "length": length,
        "width": width,
        "height": height,
        "sockets": sockets,
        "rule": "length controlled by wheel count, width controlled by transport class, flying mode converts wheels into horizontal hover rotors"
    }

    meta_path = job_dir / "transport_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2))

    return {
        "job_id": job_id,
        "model_path": str(out_path),
        "model_url": f"/outputs/{job_id}/model.glb",
        "metadata_path": str(meta_path),
        "metadata_url": f"/outputs/{job_id}/transport_metadata.json",
        "asset_type": "transport",
        "profile": profile,
        "mode": mode,
        "wheel_count": wheel_count
    }


def build_transport_from_form(build_form: dict):
    profile = build_form.get("profile") or build_form.get("body_type") or "car"
    return build_transport_model(profile=profile, build_form=build_form)