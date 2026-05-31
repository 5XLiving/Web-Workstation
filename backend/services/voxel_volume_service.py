import trimesh
import numpy as np


def cage_to_voxel_mesh(cage: dict, scale: float = 0.035) -> trimesh.Trimesh:
    cells = cage.get("surface_cells") or cage.get("occupied_cells") or []
    if not cells:
        return trimesh.creation.box(extents=[0.1, 0.1, 0.1])

    grid = cage.get("grid_size", [64, 64, 64])
    gx, gy, gz = grid

    meshes = []

    # sample only surface cells to avoid insane mesh count
    step = max(1, len(cells) // 1200)
    for cell in cells[::step]:
        x, y, z = cell

        px = (x - gx / 2) * scale
        py = (gy / 2 - y) * scale
        pz = (z - gz / 2) * scale

        cube = trimesh.creation.box(extents=[scale, scale, scale])
        cube.apply_translation([px, py, pz])
        meshes.append(cube)

    if not meshes:
        return trimesh.creation.box(extents=[0.1, 0.1, 0.1])

    return trimesh.util.concatenate(meshes)