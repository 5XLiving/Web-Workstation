from pathlib import Path
import uuid
import json
import trimesh
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "storage" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def hex_to_rgba(hex_color: str, alpha=90):
    if not hex_color:
        return [120, 180, 255, alpha]
    hex_color = hex_color.replace("#", "")
    if len(hex_color) != 6:
        return [120, 180, 255, alpha]
    return [int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16), alpha]


def make_material(name, color, alpha=90):
    lname = (name or "").lower()
    metallic = 0.05
    roughness = 0.55

    if "axle" in lname or "joint" in lname:
        metallic = 0.25
        roughness = 0.2
        alpha = 220

    return trimesh.visual.material.PBRMaterial(
        name=name or "material",
        baseColorFactor=hex_to_rgba(color, alpha),
        metallicFactor=metallic,
        roughnessFactor=roughness,
        alphaMode="BLEND",
    )


def add(scene, mesh, name):
    scene.add_geometry(mesh, node_name=name)


def sphere(radius, pos, material):
    mesh = trimesh.creation.uv_sphere(radius=radius, count=[32, 16])
    mesh.visual.material = material
    mesh.apply_translation(pos)
    return mesh


def oval_sphere(scale, pos, material):
    mesh = trimesh.creation.uv_sphere(radius=1.0, count=[32, 16])
    mesh.apply_scale(scale)
    mesh.visual.material = material
    mesh.apply_translation(pos)
    return mesh


def safe_align(mesh, from_axis, to_axis):
    from_axis = np.array(from_axis, dtype=float)
    to_axis = np.array(to_axis, dtype=float)

    from_axis = from_axis / np.linalg.norm(from_axis)
    to_axis = to_axis / np.linalg.norm(to_axis)

    axis = np.cross(from_axis, to_axis)
    axis_len = np.linalg.norm(axis)

    if axis_len > 0.0001:
        axis = axis / axis_len
        angle = np.arccos(np.clip(np.dot(from_axis, to_axis), -1.0, 1.0))
        mesh.apply_transform(trimesh.transformations.rotation_matrix(angle, axis))

    return mesh


def capsule_between(a, b, radius, material):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)

    vec = b - a
    length = float(np.linalg.norm(vec))

    if length <= 0.0001:
        return sphere(radius, a.tolist(), material)

    mid = (a + b) / 2.0
    mesh = trimesh.creation.capsule(radius=radius, height=length)

    safe_align(mesh, [0, 0, 1], vec / length)

    mesh.visual.material = material
    mesh.apply_translation(mid)
    return mesh


def tapered_between(a, b, radius_a, radius_b, material, sections=32):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)

    vec = b - a
    length = float(np.linalg.norm(vec))

    if length <= 0.0001:
        return sphere(max(radius_a, radius_b), a.tolist(), material)

    verts = []
    faces = []

    for z, r in [(0, radius_a), (length, radius_b)]:
        for i in range(sections):
            ang = 2 * np.pi * i / sections
            verts.append([np.cos(ang) * r, np.sin(ang) * r, z])

    for i in range(sections):
        j = (i + 1) % sections
        faces.append([i, j, sections + j])
        faces.append([i, sections + j, sections + i])

    mesh = trimesh.Trimesh(
        vertices=np.array(verts),
        faces=np.array(faces),
        process=True,
    )

    safe_align(mesh, [0, 0, 1], vec / length)

    mesh.visual.material = material
    mesh.apply_translation(a)
    return mesh


def boot_block(width, height, length, pos, material):
    x = width / 2
    y = height / 2
    z_back = -length * 0.38
    z_front = length * 0.62

    verts = np.array([
        [-x * 0.75, -y, z_back],
        [x * 0.75, -y, z_back],
        [-x, -y, z_front],
        [x, -y, z_front],
        [-x * 0.68, y, z_back],
        [x * 0.68, y, z_back],
        [-x * 0.90, y * 0.55, z_front],
        [x * 0.90, y * 0.55, z_front],
    ])

    faces = np.array([
        [0, 1, 3], [0, 3, 2],
        [4, 6, 7], [4, 7, 5],
        [0, 4, 5], [0, 5, 1],
        [2, 3, 7], [2, 7, 6],
        [0, 2, 6], [0, 6, 4],
        [1, 5, 7], [1, 7, 3],
    ])

    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    mesh.visual.material = material
    mesh.apply_translation(pos)
    return mesh


def get_palette(build_form):
    colors = build_form.get("scan_result", {}).get("main_colors", [])
    primary = colors[0] if len(colors) > 0 else "#7fb7ff"
    accent = colors[2] if len(colors) > 2 else "#ff4d4d"
    return primary, accent


def build_base_humanoid_scene(build_form: dict):
    primary, accent = get_palette(build_form)

    body_mat = make_material("transparent_body_form", primary, 70)
    limb_mat = make_material("transparent_limb_bone", "#9ad7ff", 80)
    axle_mat = make_material("blue_axle_joint_controller", "#00d4ff", 220)
    foot_mat = make_material("transparent_foot_form", "#ffb347", 105)

    scene = trimesh.Scene()

    points = {
        "head": [0, 1.78, 0],
        "neck_low": [0, 1.48, 0],
        "neck_high": [0, 1.58, 0],

        "upper_chest": [0, 1.25, 0],
        "lower_chest": [0, 0.88, 0],
        "pelvis": [0, 0.58, 0],

        "left_shoulder": [-0.50, 1.28, 0],
        "right_shoulder": [0.50, 1.28, 0],
        "left_elbow": [-0.78, 0.76, 0],
        "right_elbow": [0.78, 0.76, 0],
        "left_wrist": [-0.72, 0.28, 0],
        "right_wrist": [0.72, 0.28, 0],

        "left_hip": [-0.18, 0.52, 0],
        "right_hip": [0.18, 0.52, 0],
        "left_knee": [-0.24, -0.15, 0],
        "right_knee": [0.24, -0.15, 0],
        "left_ankle": [-0.23, -0.68, 0],
        "right_ankle": [0.23, -0.68, 0],
        "left_foot": [-0.23, -0.80, 0.12],
        "right_foot": [0.23, -0.80, 0.12],
    }

    add(
        scene,
        oval_sphere([0.18, 0.24, 0.18], points["head"], body_mat),
        "vertical_oval_head",
    )

    add(
        scene,
        capsule_between(points["neck_low"], points["neck_high"], 0.045, axle_mat),
        "neck_short_capsule",
    )

    add(
        scene,
        oval_sphere([0.48, 0.25, 0.22], points["upper_chest"], body_mat),
        "upper_chest_long_oval",
    )

    add(
        scene,
        oval_sphere([0.39, 0.12, 0.18], points["lower_chest"], body_mat),
        "lower_chest_flat_oval",
    )

    add(
        scene,
        oval_sphere([0.09, 0.10, 0.09], points["pelvis"], body_mat),
        "small_center_pelvis",
    )

    add(
        scene,
        capsule_between([0, 1.03, 0], [0, 1.00, 0], 0.055, body_mat),
        "chest_connector",
    )

    add(
        scene,
        capsule_between([0, 0.76, 0], [0, 0.66, 0], 0.055, body_mat),
        "pelvis_connector",
    )

    for side in ["left", "right"]:
        shoulder = points[f"{side}_shoulder"]
        elbow = points[f"{side}_elbow"]
        wrist = points[f"{side}_wrist"]

        add(scene, sphere(0.095, shoulder, axle_mat), f"{side}_shoulder_joint")
        add(scene, sphere(0.070, elbow, axle_mat), f"{side}_elbow_joint")
        add(scene, sphere(0.052, wrist, axle_mat), f"{side}_wrist_joint")

        add(scene, capsule_between(shoulder, elbow, 0.075, limb_mat), f"{side}_upper_arm")
        add(scene, capsule_between(elbow, wrist, 0.062, limb_mat), f"{side}_forearm")

        add(
            scene,
            oval_sphere([0.060, 0.085, 0.040], [wrist[0], wrist[1] - 0.11, 0], limb_mat),
            f"{side}_hand",
        )

    for side in ["left", "right"]:
        hip = points[f"{side}_hip"]
        knee = points[f"{side}_knee"]
        ankle = points[f"{side}_ankle"]
        foot = points[f"{side}_foot"]

        add(scene, sphere(0.070, hip, axle_mat), f"{side}_hip_joint")
        add(scene, sphere(0.068, knee, axle_mat), f"{side}_knee_joint")
        add(scene, sphere(0.052, ankle, axle_mat), f"{side}_ankle_joint")

        add(scene, capsule_between(hip, knee, 0.11, limb_mat), f"{side}_thigh_oval_capsule")
        add(scene, tapered_between(knee, ankle, 0.090, 0.060, limb_mat), f"{side}_shin_tapered")
        add(scene, boot_block(0.24, 0.14, 0.36, foot, foot_mat), f"{side}_boot_foot")

    return scene, points


def build_rig_metadata(build_form, points):
    return {
        "skeleton": "humanoid_reference_v13_pelvis_fixed",
        "rig_type": "organic_oval_mech",
        "notes": "Pelvis reduced. Hip spacing narrowed. Thigh radius reduced so thigh+pelvis width fits lower body.",
        "points": points,
    }


def build_model_from_socket_form(build_form: dict):
    job_id = uuid.uuid4().hex
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    scene, points = build_base_humanoid_scene(build_form or {})

    out_path = job_dir / "model.glb"
    scene.export(out_path)

    rig_meta = build_rig_metadata(build_form or {}, points)
    rig_path = job_dir / "rig_metadata.json"
    rig_path.write_text(json.dumps(rig_meta, indent=2))

    return {
        "job_id": job_id,
        "model_path": str(out_path),
        "model_url": f"/outputs/{job_id}/model.glb",
        "rig_metadata_path": str(rig_path),
        "rig_metadata_url": f"/outputs/{job_id}/rig_metadata.json",
    }


def build_humanoid(gender="male", scale=1.0):
    return {
        "skeleton_name": "humanoid_mech",
        "gender": gender,
        "scale": scale,
        "builder": "organic_oval_mech_v13_pelvis_fixed",
    }


def get_humanoid_skeleton(gender="male", scale=1.0):
    return build_humanoid(gender=gender, scale=scale)