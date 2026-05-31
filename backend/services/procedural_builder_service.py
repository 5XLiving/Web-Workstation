from pathlib import Path
import uuid
import math
import trimesh

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


def make_material(name, color):
    return trimesh.visual.material.PBRMaterial(
        name=name,
        baseColorFactor=hex_to_rgba(color),
        metallicFactor=0.7,
        roughnessFactor=0.35
    )


def build_primitive(part):

    primitive = (part.get("primitive") or "box").lower()

    size = part.get("size") or {}
    pos = part.get("position") or {}

    w = float(size.get("width") or 0.5)
    h = float(size.get("height") or 0.5)
    d = float(size.get("depth") or 0.5)

    x = float(pos.get("x") or 0)
    y = float(pos.get("y") or 0)
    z = float(pos.get("z") or 0)

    material_name = part.get("material") or "material"
    color = part.get("color") or "#666666"

    material = make_material(material_name, color)

    if primitive == "sphere":

        mesh = trimesh.creation.uv_sphere(
            radius=max(w, h, d) / 2,
            count=[32, 16]
        )

    elif primitive == "cylinder":

        mesh = trimesh.creation.cylinder(
            radius=max(w, d) / 2,
            height=h,
            sections=32
        )

    elif primitive == "cone":

        mesh = trimesh.creation.cone(
            radius=max(w, d) / 2,
            height=h,
            sections=32
        )

    elif primitive == "capsule":

        mesh = trimesh.creation.capsule(
            radius=max(w, d) / 2,
            height=h
        )

    else:

        mesh = trimesh.creation.box(
            extents=[w, h, d]
        )

    mesh.visual.material = material

    rotation = part.get("rotation") or {}

    rx = math.radians(float(rotation.get("x") or 0))
    ry = math.radians(float(rotation.get("y") or 0))
    rz = math.radians(float(rotation.get("z") or 0))

    if rx != 0:
        mesh.apply_transform(
            trimesh.transformations.rotation_matrix(rx, [1, 0, 0])
        )

    if ry != 0:
        mesh.apply_transform(
            trimesh.transformations.rotation_matrix(ry, [0, 1, 0])
        )

    if rz != 0:
        mesh.apply_transform(
            trimesh.transformations.rotation_matrix(rz, [0, 0, 1])
        )

    mesh.apply_translation([x, y, z])

    return mesh


def build_procedural_model_from_form(build_form: dict):

    job_id = uuid.uuid4().hex

    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    scene = trimesh.Scene()

    parts = build_form.get("parts", [])

    for part in parts:

        if part.get("exists") is not True:
            continue

        count = int(part.get("count") or 1)

        for i in range(count):

            clone = dict(part)

            if count > 1:

                spacing = float(part.get("spacing") or 0.5)

                pos = dict(part.get("position") or {})

                offset = (i - (count - 1) / 2) * spacing

                axis = part.get("spread_axis") or "x"

                pos[axis] = float(pos.get(axis) or 0) + offset

                clone["position"] = pos

            mesh = build_primitive(clone)

            scene.add_geometry(
                mesh,
                node_name=f"{part.get('part_id','part')}_{i}"
            )

    out_path = job_dir / "model.glb"

    scene.export(out_path)

    return {
        "job_id": job_id,
        "model_url": f"/outputs/{job_id}/model.glb"
    }