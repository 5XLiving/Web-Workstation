import math
import json
from pathlib import Path

import numpy as np
import trimesh


def _vec(value):
    if isinstance(value, dict):
        return np.array(
            [float(value.get("x", 0)), float(value.get("y", 0)), float(value.get("z", 0))],
            dtype=float,
        )

    if isinstance(value, (list, tuple)) and len(value) >= 3:
        return np.array([float(value[0]), float(value[1]), float(value[2])], dtype=float)

    return np.array([0.0, 0.0, 0.0], dtype=float)


def _align(mesh, from_axis, to_axis):
    from_axis = np.array(from_axis, dtype=float)
    to_axis = np.array(to_axis, dtype=float)

    if np.linalg.norm(from_axis) < 0.0001 or np.linalg.norm(to_axis) < 0.0001:
        return mesh

    from_axis /= np.linalg.norm(from_axis)
    to_axis /= np.linalg.norm(to_axis)

    axis = np.cross(from_axis, to_axis)
    axis_len = np.linalg.norm(axis)

    if axis_len > 0.0001:
        axis /= axis_len
        angle = math.acos(float(np.clip(np.dot(from_axis, to_axis), -1, 1)))
        mesh.apply_transform(trimesh.transformations.rotation_matrix(angle, axis))

    return mesh


def _make_material(name, rgba):
    rgba = list(rgba or [28, 30, 34, 255])
    return trimesh.visual.material.SimpleMaterial(
        name=name,
        diffuse=rgba,
        ambient=rgba,
        specular=[70, 70, 70, 255],
    )


def _materials(template):
    mats = {}

    for key, value in template.get("materials", {}).items():
        if isinstance(value, dict):
            mats[key] = _make_material(value.get("name", key), value.get("rgba", [28, 30, 34, 255]))
        elif isinstance(value, list):
            mats[key] = _make_material(key, value)

    if "body_mat" not in mats:
        mats["body_mat"] = _make_material("body_mat", [28, 30, 34, 255])

    return mats


def _apply_mat(mesh, mat):
    try:
        mesh.visual.material = mat
    except Exception:
        pass
    return mesh


def _sphere(scale, pos, mat):
    mesh = trimesh.creation.uv_sphere(radius=1.0, count=[32, 16])
    mesh.apply_scale(_vec(scale))
    mesh.apply_translation(_vec(pos))
    return _apply_mat(mesh, mat)


def _box(scale, pos, mat):
    mesh = trimesh.creation.box(extents=_vec(scale))
    mesh.apply_translation(_vec(pos))
    return _apply_mat(mesh, mat)


def _capsule(a, b, radius, mat):
    a = _vec(a)
    b = _vec(b)

    vec = b - a
    length = float(np.linalg.norm(vec))

    if length < 0.001:
        return _sphere([radius, radius, radius], a, mat)

    mesh = trimesh.creation.capsule(radius=float(radius), height=length)
    _align(mesh, [0, 0, 1], vec / length)
    mesh.apply_translation((a + b) / 2)

    return _apply_mat(mesh, mat)


def _rear_pivot_foot(width, height, length, pos, profile, mat):
    x = float(width) / 2
    y = float(height) / 2

    z_back = float(profile.get("z_back", 0.0))
    z_front = float(length)

    vp = profile.get("vertex_profile", {})
    back_bottom = float(vp.get("back_bottom_width_multiplier", 0.70))
    front_bottom = float(vp.get("front_bottom_width_multiplier", 1.00))
    back_top = float(vp.get("back_top_width_multiplier", 0.60))
    front_top = float(vp.get("front_top_width_multiplier", 0.82))
    front_top_h = float(vp.get("front_top_height_multiplier", 0.55))

    verts = np.array([
        [-x * back_bottom, -y, z_back],
        [ x * back_bottom, -y, z_back],
        [-x * front_bottom, -y, z_front],
        [ x * front_bottom, -y, z_front],

        [-x * back_top,  y, z_back],
        [ x * back_top,  y, z_back],
        [-x * front_top,  y * front_top_h, z_front],
        [ x * front_top,  y * front_top_h, z_front],
    ])

    faces = np.array(profile.get("faces") or [
        [0, 1, 3], [0, 3, 2],
        [4, 6, 7], [4, 7, 5],
        [0, 4, 5], [0, 5, 1],
        [2, 3, 7], [2, 7, 6],
        [0, 2, 6], [0, 6, 4],
        [1, 5, 7], [1, 7, 3],
    ])

    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    mesh.apply_translation(_vec(pos))
    return _apply_mat(mesh, mat)


def _socket(template, name, preview=False):
    if preview:
        sockets = template.get("current_final_mesh_preview", {}).get("sockets", {})
    else:
        sockets = template.get("sockets", {})

    return _vec(sockets.get(name, [0, 0, 0]))


def _part_pos(template, part, preview=False):
    if "socket" in part:
        return _socket(template, part["socket"], preview=preview)

    if "position" in part:
        return _vec(part["position"])

    return np.array([0.0, 0.0, 0.0], dtype=float)


def _build_part(template, part, mats, preview=False):
    mat_key = part.get("material") or "body_mat"
    mat = mats.get(mat_key) or mats.get("body_mat")

    shape = part.get("shape")
    name = part.get("name", shape or "part")

    if shape in ("sphere", "oval_sphere", "flattened_sphere"):
        return name, _sphere(part.get("scale", [0.1, 0.1, 0.1]), _part_pos(template, part, preview=preview), mat)

    if shape in ("box", "torso_block", "pelvis_block"):
        return name, _box(part.get("scale", [0.1, 0.1, 0.1]), _part_pos(template, part, preview=preview), mat)

    if shape == "capsule_between":
        if "from_pos" in part:
            a = part["from_pos"]
        else:
            a = _socket(template, part.get("from"), preview=preview)

        if "to_pos" in part:
            b = part["to_pos"]
        else:
            b = _socket(template, part.get("to"), preview=preview)

        return name, _capsule(a, b, float(part.get("radius", 0.05)), mat)

    return None, None


def _add_current_preview_body(scene, template, mats):
    preview = template.get("current_final_mesh_preview", {})
    for part in preview.get("body_parts", []):
        name, mesh = _build_part(template, part, mats, preview=True)
        if mesh is not None:
            scene.add_geometry(mesh, node_name=f"json_{name}")


def _add_preview_hands(scene, template, mats):
    preview = template.get("current_final_mesh_preview", {})
    hands = preview.get("hands", {})
    sockets = preview.get("sockets", {})
    mat = mats.get("body_mat")

    palm_cfg = hands.get("palm", {})
    fingers_cfg = hands.get("fingers", {})
    thumb_cfg = hands.get("thumb", {})

    for side, sx in [("left", -1), ("right", 1)]:
        wrist = _vec(sockets.get(f"{side}_wrist", [sx * 0.62, 0.50, 0.04]))
        palm_offset = _vec(palm_cfg.get("offset_from_wrist", [0, -0.055, 0.030]))
        palm_pos = wrist + palm_offset

        scene.add_geometry(
            _sphere(palm_cfg.get("scale", [0.040, 0.052, 0.034]), palm_pos, mat),
            node_name=f"json_{side}_palm",
        )

        base_offset = _vec(fingers_cfg.get("base_offset", [0, -0.035, 0.022]))
        r1, r2 = fingers_cfg.get("radius", [0.0085, 0.0065])
        mid_z_add = float(fingers_cfg.get("mid_z_add", 0.022))
        tip_z_add = float(fingers_cfg.get("tip_z_add", 0.040))
        mid_mult = float(fingers_cfg.get("spread_mid_multiplier", 1.20))
        tip_mult = float(fingers_cfg.get("spread_tip_multiplier", 1.45))

        for item in fingers_cfg.get("items", []):
            spread_x = float(item.get("spread_x", 0))
            length_y = float(item.get("length_y", 0.08))
            finger_name = item.get("name", "finger")

            base = palm_pos + base_offset + np.array([spread_x, 0, 0], dtype=float)
            mid = np.array([
                palm_pos[0] + spread_x * mid_mult,
                base[1] - length_y * 0.50,
                base[2] + mid_z_add,
            ])
            tip = np.array([
                palm_pos[0] + spread_x * tip_mult,
                base[1] - length_y,
                base[2] + tip_z_add,
            ])

            scene.add_geometry(
                _capsule(base, mid, float(r1), mat),
                node_name=f"json_{side}_{finger_name}_finger_bone_1",
            )
            scene.add_geometry(
                _capsule(mid, tip, float(r2), mat),
                node_name=f"json_{side}_{finger_name}_finger_bone_2",
            )

        if thumb_cfg:
            tr1, tr2 = thumb_cfg.get("radius", [0.010, 0.006])

            def sx_offset(key):
                raw = thumb_cfg.get(key, [0, 0, 0])
                return np.array([float(raw[0]) * sx, float(raw[1]), float(raw[2])], dtype=float)

            thumb_base = palm_pos + sx_offset("base_offset_by_sx")
            thumb_mid = palm_pos + sx_offset("mid_offset_by_sx")
            thumb_tip = palm_pos + sx_offset("tip_offset_by_sx")

            scene.add_geometry(
                _capsule(thumb_base, thumb_mid, float(tr1), mat),
                node_name=f"json_{side}_thumb_bone_1",
            )
            scene.add_geometry(
                _capsule(thumb_mid, thumb_tip, float(tr2), mat),
                node_name=f"json_{side}_thumb_bone_2",
            )


def _add_preview_feet(scene, template, mats):
    preview = template.get("current_final_mesh_preview", {})
    foot_cfg = preview.get("feet", {})
    mat = mats.get("body_mat")

    scale = foot_cfg.get("scale", [0.14, 0.08, 0.28])
    width, height, length = scale

    scene.add_geometry(
        _rear_pivot_foot(width, height, length, foot_cfg.get("left_position", [-0.24, -0.76, -0.02]), foot_cfg, mat),
        node_name="json_left_mech_foot",
    )

    scene.add_geometry(
        _rear_pivot_foot(width, height, length, foot_cfg.get("right_position", [0.24, -0.76, -0.02]), foot_cfg, mat),
        node_name="json_right_mech_foot",
    )


def build_scene_from_template(template: dict) -> trimesh.Scene:
    scene = trimesh.Scene()
    mats = _materials(template)

    preview = template.get("current_final_mesh_preview")

    if not isinstance(preview, dict):
        raise ValueError("Missing current_final_mesh_preview in humanoid_mech_v2.json")

    if not preview.get("enabled", False):
        raise ValueError("current_final_mesh_preview.enabled must be true")

    _add_current_preview_body(scene, template, mats)
    _add_preview_hands(scene, template, mats)
    _add_preview_feet(scene, template, mats)

    return scene


def build_scene_from_template_file(template_path: str) -> trimesh.Scene:
    path = Path(template_path)
    template = json.loads(path.read_text())
    return build_scene_from_template(template)
