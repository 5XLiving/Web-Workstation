import math
import numpy as np
import trimesh


def _mat(name, color):
    return trimesh.visual.material.SimpleMaterial(
        name=name,
        diffuse=color,
        ambient=color,
        specular=[80, 80, 80, 255],
    )


MAT_DARK = _mat("shell_dark_armor", [30, 32, 36, 255])
MAT_METAL = _mat("shell_metal_armor", [105, 100, 92, 255])
MAT_GOLD = _mat("shell_gold_trim", [190, 140, 70, 255])
MAT_GLOW = _mat("shell_orange_glow", [255, 120, 20, 255])
MAT_CLOTH = _mat("shell_red_cloth", [105, 28, 24, 255])


def _apply(mesh, mat):
    mesh.visual.material = mat
    return mesh


def _box(scale, pos, mat=MAT_METAL):
    mesh = trimesh.creation.box(extents=scale)
    mesh.apply_translation(pos)
    return _apply(mesh, mat)


def _sphere(scale, pos, mat=MAT_METAL):
    mesh = trimesh.creation.uv_sphere(radius=1.0, count=[24, 12])
    mesh.apply_scale(scale)
    mesh.apply_translation(pos)
    return _apply(mesh, mat)


def _capsule_between(a, b, radius, mat=MAT_METAL):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    vec = b - a
    length = float(np.linalg.norm(vec))

    if length < 0.001:
        return _sphere([radius, radius, radius], a, mat)

    mesh = trimesh.creation.capsule(radius=radius, height=length)
    z = np.array([0, 0, 1], dtype=float)
    direction = vec / length

    axis = np.cross(z, direction)
    axis_len = np.linalg.norm(axis)

    if axis_len > 0.0001:
        axis = axis / axis_len
        angle = math.acos(float(np.clip(np.dot(z, direction), -1, 1)))
        mesh.apply_transform(trimesh.transformations.rotation_matrix(angle, axis))

    mesh.apply_translation((a + b) / 2)
    return _apply(mesh, mat)


def _tapered_box(scale, pos, taper_top=0.72, mat=MAT_METAL):
    sx, sy, sz = scale
    x1, y1, z1 = sx / 2, sy / 2, sz / 2
    x2, z2 = x1 * taper_top, z1 * taper_top

    vertices = np.array([
        [-x1, -y1, -z1], [x1, -y1, -z1], [x1, -y1, z1], [-x1, -y1, z1],
        [-x2, y1, -z2], [x2, y1, -z2], [x2, y1, z2], [-x2, y1, z2],
    ], dtype=float)

    faces = np.array([
        [0, 1, 2], [0, 2, 3],
        [4, 6, 5], [4, 7, 6],
        [0, 4, 5], [0, 5, 1],
        [1, 5, 6], [1, 6, 2],
        [2, 6, 7], [2, 7, 3],
        [3, 7, 4], [3, 4, 0],
    ])

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    mesh.apply_translation(pos)
    return _apply(mesh, mat)


def _plate(scale, pos, mat=MAT_METAL):
    return _tapered_box(scale, pos, taper_top=0.85, mat=mat)


def _launcher(pos, height=0.95, radius=0.105, mat=MAT_DARK):
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=24)
    cyl.apply_transform(trimesh.transformations.rotation_matrix(math.radians(10), [1, 0, 0]))
    cyl.apply_translation(pos)
    return _apply(cyl, mat)


def _cape(scale, pos, mat=MAT_CLOTH):
    sx, sy, sz = scale
    verts = np.array([
        [-sx * 0.50, sy * 0.50, 0],
        [sx * 0.50, sy * 0.50, 0],
        [sx * 0.38, -sy * 0.20, 0],
        [sx * 0.22, -sy * 0.50, 0],
        [0, -sy * 0.35, 0],
        [-sx * 0.22, -sy * 0.55, 0],
        [-sx * 0.42, -sy * 0.18, 0],
    ])

    faces = np.array([
        [0, 1, 2],
        [0, 2, 6],
        [6, 2, 3],
        [6, 3, 5],
        [5, 3, 4],
    ])

    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    mesh.apply_transform(trimesh.transformations.rotation_matrix(math.radians(90), [1, 0, 0]))
    mesh.apply_translation(pos)
    return _apply(mesh, mat)


def _layer_strength(layers, name):
    summary = layers.get("summary", {})
    total = max(1, sum(summary.values()))
    return summary.get(name, 0) / total


def build_universal_shell_from_layers(
    cage: dict,
    layers: dict,
    blueprint: dict | None = None,
    rig: dict | None = None,
) -> trimesh.Scene:
    """
    Universal shell builder v1.
    Uses cage/layer summary to create visible shell modules around the oval base.
    Cage remains analysis data; this creates geometry only from interpreted zones.
    """

    scene = trimesh.Scene()

    dark = _layer_strength(layers, "dark_armor")
    metal = _layer_strength(layers, "metal_armor")
    gold = _layer_strength(layers, "gold_trim")
    glow = _layer_strength(layers, "orange_glow")
    cloth = _layer_strength(layers, "red_cloth")

    heavy = max(0.0, min(1.0, dark + metal + gold))
    bulky = 1.0 + heavy * 0.55

    # CHEST ARMOR
    scene.add_geometry(
        _plate([0.78 * bulky, 0.18, 0.38], [0, 1.30, 0.08], MAT_METAL),
        node_name="shell_chest_front_armor",
    )

    scene.add_geometry(
        _plate([0.58 * bulky, 0.12, 0.28], [0, 1.08, 0.13], MAT_DARK),
        node_name="shell_abdomen_armor",
    )

    # CENTER CORE / GLOW
    if glow > 0.01:
        scene.add_geometry(
            _sphere([0.14, 0.14, 0.055], [0, 1.31, 0.28], MAT_GLOW),
            node_name="shell_chest_glow_core",
        )

    # SHOULDERS
    for side, sx in [("left", -1), ("right", 1)]:
        scene.add_geometry(
            _plate([0.34 * bulky, 0.16, 0.30], [sx * 0.52, 1.30, 0.05], MAT_METAL),
            node_name=f"shell_{side}_shoulder_plate",
        )

        scene.add_geometry(
            _plate([0.30 * bulky, 0.13, 0.24], [sx * 0.62, 1.21, 0.10], MAT_DARK),
            node_name=f"shell_{side}_outer_shoulder_layer",
        )

    # ARMS
    for side, sx in [("left", -1), ("right", 1)]:
        scene.add_geometry(
            _capsule_between([sx * 0.42, 1.10, 0.06], [sx * 0.62, 0.78, 0.08], 0.105 * bulky, MAT_DARK),
            node_name=f"shell_{side}_upper_arm_armor",
        )
        scene.add_geometry(
            _capsule_between([sx * 0.62, 0.75, 0.08], [sx * 0.66, 0.48, 0.08], 0.115 * bulky, MAT_METAL),
            node_name=f"shell_{side}_forearm_armor",
        )
        scene.add_geometry(
            _sphere([0.12, 0.09, 0.09], [sx * 0.68, 0.42, 0.08], MAT_DARK),
            node_name=f"shell_{side}_gauntlet",
        )

    # HIPS / LEGS / BOOTS
    for side, sx in [("left", -1), ("right", 1)]:
        scene.add_geometry(
            _plate([0.20, 0.12, 0.22], [sx * 0.24, 0.72, 0.08], MAT_GOLD if gold > 0.01 else MAT_METAL),
            node_name=f"shell_{side}_hip_plate",
        )
        scene.add_geometry(
            _capsule_between([sx * 0.19, 0.64, 0.07], [sx * 0.25, 0.08, 0.08], 0.13 * bulky, MAT_METAL),
            node_name=f"shell_{side}_thigh_armor",
        )
        scene.add_geometry(
            _capsule_between([sx * 0.25, 0.02, 0.08], [sx * 0.28, -0.54, 0.09], 0.115 * bulky, MAT_DARK),
            node_name=f"shell_{side}_shin_armor",
        )
        scene.add_geometry(
            _box([0.28, 0.14, 0.38], [sx * 0.22, -0.78, 0.18], MAT_METAL),
            node_name=f"shell_{side}_boot_armor",
        )

    # BACK LAUNCHER / BACKPACK: dynamic rule from vertical dark/metal mass
    # For current mech image, cage/layer mass implies tall back structures.
    if heavy > 0.12:
        launcher_positions = [
            [-0.42, 1.68, -0.18],
            [-0.16, 1.80, -0.22],
            [0.16, 1.80, -0.22],
            [0.42, 1.68, -0.18],
        ]
        for i, pos in enumerate(launcher_positions):
            scene.add_geometry(
                _launcher(pos, height=0.75 + heavy * 0.55, radius=0.085 + heavy * 0.03, mat=MAT_DARK),
                node_name=f"shell_dynamic_back_launcher_{i+1}",
            )
            if glow > 0.005:
                scene.add_geometry(
                    _box([0.08, 0.15, 0.025], [pos[0], pos[1], pos[2] + 0.095], MAT_GLOW),
                    node_name=f"shell_launcher_glow_panel_{i+1}",
                )

    # CAPE / CLOTH
    if cloth > 0.02:
        scene.add_geometry(
            _cape([1.40, 1.25, 0.02], [0, 0.62, -0.26], MAT_CLOTH),
            node_name="shell_red_cape_layer",
        )

    # SURFACE DETAIL PLATES
    detail_count = int(10 + heavy * 28)
    for i in range(detail_count):
        side = -1 if i % 2 == 0 else 1
        row = i // 2
        y = 1.18 - row * 0.055
        x = side * (0.12 + (row % 3) * 0.055)
        z = 0.255
        scene.add_geometry(
            _box([0.08, 0.025, 0.018], [x, y, z], MAT_DARK if i % 3 else MAT_GOLD),
            node_name=f"shell_micro_panel_{i+1}",
        )

    return scene