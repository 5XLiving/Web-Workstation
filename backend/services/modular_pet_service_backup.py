from pathlib import Path
import numpy as np
import trimesh
from PIL import Image
from shapely.geometry import Polygon
from shapely.ops import unary_union
from skimage import measure
from trimesh.creation import extrude_polygon


def make_mat(name, color, metallic=0.0, roughness=0.96):
    return trimesh.visual.material.PBRMaterial(
        name=name,
        baseColorFactor=color,
        metallicFactor=metallic,
        roughnessFactor=roughness,
    )


def load_mask_polygon(image_path):
    img = Image.open(image_path).convert("RGBA")
    arr = np.array(img)

    alpha = arr[:, :, 3]
    mask = alpha > 20

    contours = measure.find_contours(mask.astype(np.uint8), 0.5)
    polygons = []

    for contour in contours:
        if len(contour) < 20:
            continue

        pts = [(float(x), float(-y)) for y, x in contour]
        poly = Polygon(pts)

        if poly.is_valid and poly.area > 100:
            polygons.append(poly)

    if not polygons:
        raise RuntimeError("No valid silhouette polygon found")

    merged = unary_union(polygons)

    if merged.geom_type == "MultiPolygon":
        merged = max(merged.geoms, key=lambda g: g.area)

    if not merged.is_valid:
        merged = merged.buffer(0)

    merged = merged.simplify(2.5, preserve_topology=True)

    if merged.is_empty or merged.area <= 0:
        raise RuntimeError("Silhouette polygon became empty after simplify")

    return merged, mask.shape


def normalize_mesh(mesh, img_shape):
    h, w = img_shape

    scale = 6.0 / max(w, h)
    mesh.apply_scale(scale)

    bounds = mesh.bounds
    center = (bounds[0] + bounds[1]) / 2.0
    mesh.apply_translation(-center)

    bounds = mesh.bounds
    min_z = bounds[0][2]
    mesh.apply_translation([0, 0, -min_z])

    rotate = trimesh.transformations.euler_matrix(
        -np.pi / 2,
        0,
        0,
        "sxyz"
    )
    mesh.apply_transform(rotate)

    return mesh


def safe_lowpoly_cleanup(mesh):
    try:
        if hasattr(mesh, "faces") and len(mesh.faces) > 600:
            # Trimesh expects a reduction ratio here, not face count.
            mesh = mesh.simplify_quadric_decimation(0.45)
    except Exception as e:
        print("[WARN] simplify skipped:", e)

    try:
        mesh.remove_duplicate_faces()
        mesh.remove_degenerate_faces()
        mesh.remove_unreferenced_vertices()
    except Exception as e:
        print("[WARN] cleanup skipped:", e)

    return mesh


def generate_modular_pet(image_path: str, output_dir: str):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    polygon, img_shape = load_mask_polygon(image_path)

    mesh = extrude_polygon(
        polygon,
        height=0.8
    )

    mesh = normalize_mesh(mesh, img_shape)
    mesh = safe_lowpoly_cleanup(mesh)

    body = make_mat(
        "dark readable clay body",
        [0.26, 0.28, 0.30, 1],
        0.0,
        0.96,
    )

    mesh.visual.material = body

    scene = trimesh.Scene()
    scene.add_geometry(mesh, node_name="true_silhouette_mesh", geom_name="true_silhouette_mesh")

    bounds = scene.bounds
    if bounds is not None:
        min_y = bounds[0][1]
        scene.apply_transform(
            trimesh.transformations.translation_matrix([0, -min_y, 0])
        )

    model_path = output_dir / "model.glb"
    scene.export(model_path)

    return {
        "model_glb": str(model_path),
        "source_image": image_path,
        "style": "true_silhouette_extrusion_lowpoly",
    }