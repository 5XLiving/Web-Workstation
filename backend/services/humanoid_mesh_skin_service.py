from pathlib import Path
import uuid
import json
import numpy as np
import trimesh
from PIL import Image
from skimage import measure


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "storage" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def make_material(name, color=(120, 180, 255, 120)):
    return trimesh.visual.material.PBRMaterial(
        name=name,
        baseColorFactor=list(color),
        metallicFactor=0.05,
        roughnessFactor=0.55,
        alphaMode="BLEND",
    )


def load_mask_from_image(image_path, size=96):
    img = Image.open(image_path).convert("RGBA")
    img.thumbnail((size, size), Image.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    canvas.paste(img, (x, y), img)

    arr = np.array(canvas)
    alpha = arr[:, :, 3]
    rgb = arr[:, :, :3]

    if alpha.max() > 10:
        mask = alpha > 20
    else:
        gray = rgb.mean(axis=2)
        mask = gray < 245

    return mask.astype(np.uint8), arr


def mask_metrics(mask):
    ys, xs = np.where(mask > 0)

    if len(xs) == 0:
        return {
            "aspect": 0.5,
            "height_ratio": 1.0,
            "width_ratio": 0.5,
            "upper_density": 1.0,
            "middle_density": 1.0,
            "lower_density": 1.0,
        }

    h, w = mask.shape
    min_x, max_x = xs.min(), xs.max()
    min_y, max_y = ys.min(), ys.max()

    subject_w = max_x - min_x + 1
    subject_h = max_y - min_y + 1

    crop = mask[min_y:max_y + 1, min_x:max_x + 1]
    ch = crop.shape[0]

    upper = crop[: max(1, ch // 3), :]
    middle = crop[max(1, ch // 3): max(2, 2 * ch // 3), :]
    lower = crop[max(2, 2 * ch // 3):, :]

    return {
        "aspect": float(subject_w / max(1, subject_h)),
        "height_ratio": float(subject_h / h),
        "width_ratio": float(subject_w / w),
        "upper_density": float(upper.mean()),
        "middle_density": float(middle.mean()),
        "lower_density": float(lower.mean()),
        "bbox": [int(min_x), int(min_y), int(max_x), int(max_y)],
    }


def humanoid_profile_from_mask(mask):
    m = mask_metrics(mask)

    aspect = max(0.38, min(0.95, m["aspect"]))

    total_height = 2.80
    shoulder_width = max(0.85, min(1.35, aspect * 1.65))
    torso_width = shoulder_width * 0.88
    lower_width = torso_width * 0.62

    return {
        "total_height": total_height,
        "ground_y": -0.80,
        "head_center": [0, 1.78, 0],
        "head_scale": [0.18, 0.24, 0.18],
        "neck_low": [0, 1.48, 0],
        "neck_high": [0, 1.58, 0],
        "upper_chest_center": [0, 1.25, 0],
        "upper_chest_scale": [torso_width * 0.52, 0.25, 0.22],
        "lower_chest_center": [0, 0.88, 0],
        "lower_chest_scale": [lower_width * 0.50, 0.12, 0.18],
        "pelvis_center": [0, 0.58, 0],
        "pelvis_scale": [0.09, 0.10, 0.09],
        "shoulder_x": shoulder_width * 0.50,
        "hip_x": lower_width * 0.24,
        "knee_x": lower_width * 0.30,
        "ankle_x": lower_width * 0.28,
    }


def oval(scale, pos, mat):
    mesh = trimesh.creation.uv_sphere(radius=1.0, count=[32, 16])
    mesh.apply_scale(scale)
    mesh.visual.material = mat
    mesh.apply_translation(pos)
    return mesh


def capsule_between(a, b, radius, mat):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    vec = b - a
    length = float(np.linalg.norm(vec))

    if length <= 0.0001:
        return oval([radius, radius, radius], a.tolist(), mat)

    mesh = trimesh.creation.capsule(radius=radius, height=length, count=[32, 16])

    direction = vec / length
    axis = np.cross([0, 0, 1], direction)
    axis_len = np.linalg.norm(axis)

    if axis_len > 0.0001:
        axis = axis / axis_len
        angle = np.arccos(np.clip(np.dot([0, 0, 1], direction), -1.0, 1.0))
        mesh.apply_transform(trimesh.transformations.rotation_matrix(angle, axis))

    mesh.visual.material = mat
    mesh.apply_translation((a + b) / 2.0)
    return mesh


def boot(width, height, length, pos, mat):
    x = width / 2
    y = height / 2
    zb = -length * 0.38
    zf = length * 0.62

    verts = np.array([
        [-x * 0.75, -y, zb], [x * 0.75, -y, zb],
        [-x, -y, zf], [x, -y, zf],
        [-x * 0.68, y, zb], [x * 0.68, y, zb],
        [-x * 0.90, y * 0.55, zf], [x * 0.90, y * 0.55, zf],
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
    mesh.visual.material = mat
    mesh.apply_translation(pos)
    return mesh


def build_humanoid_mesh_skin(image_path):
    mask, arr = load_mask_from_image(image_path)
    profile = humanoid_profile_from_mask(mask)

    body_mat = make_material("image_guided_body_skin", (120, 180, 255, 105))
    joint_mat = make_material("skeleton_joint_points", (0, 212, 255, 220))
    foot_mat = make_material("boot_feet", (255, 179, 71, 120))

    scene = trimesh.Scene()

    sx = profile["shoulder_x"]
    hx = profile["hip_x"]
    kx = profile["knee_x"]
    ax = profile["ankle_x"]

    points = {
        "head": profile["head_center"],
        "neck_low": profile["neck_low"],
        "neck_high": profile["neck_high"],

        "upper_chest": profile["upper_chest_center"],
        "lower_chest": profile["lower_chest_center"],
        "pelvis": profile["pelvis_center"],

        "left_shoulder": [-sx, 1.28, 0],
        "right_shoulder": [sx, 1.28, 0],
        "left_elbow": [-sx - 0.16, 0.76, 0],
        "right_elbow": [sx + 0.16, 0.76, 0],
        "left_wrist": [-sx - 0.10, 0.28, 0],
        "right_wrist": [sx + 0.10, 0.28, 0],

        "left_hip": [-hx, 0.52, 0],
        "right_hip": [hx, 0.52, 0],
        "left_knee": [-kx, -0.15, 0],
        "right_knee": [kx, -0.15, 0],
        "left_ankle": [-ax, -0.68, 0],
        "right_ankle": [ax, -0.68, 0],
        "left_foot": [-ax, -0.80, 0.12],
        "right_foot": [ax, -0.80, 0.12],
    }

    parts = []

    parts.append(oval(profile["head_scale"], points["head"], body_mat))
    parts.append(capsule_between(points["neck_low"], points["neck_high"], 0.045, joint_mat))

    parts.append(oval(profile["upper_chest_scale"], points["upper_chest"], body_mat))
    parts.append(oval(profile["lower_chest_scale"], points["lower_chest"], body_mat))
    parts.append(oval(profile["pelvis_scale"], points["pelvis"], body_mat))

    parts.append(capsule_between([0, 1.03, 0], [0, 1.00, 0], 0.055, body_mat))
    parts.append(capsule_between([0, 0.76, 0], [0, 0.66, 0], 0.055, body_mat))

    for side in ["left", "right"]:
        shoulder = points[f"{side}_shoulder"]
        elbow = points[f"{side}_elbow"]
        wrist = points[f"{side}_wrist"]
        hip = points[f"{side}_hip"]
        knee = points[f"{side}_knee"]
        ankle = points[f"{side}_ankle"]
        foot = points[f"{side}_foot"]

        parts.append(oval([0.095, 0.095, 0.095], shoulder, joint_mat))
        parts.append(oval([0.070, 0.070, 0.070], elbow, joint_mat))
        parts.append(oval([0.052, 0.052, 0.052], wrist, joint_mat))

        parts.append(capsule_between(shoulder, elbow, 0.075, body_mat))
        parts.append(capsule_between(elbow, wrist, 0.062, body_mat))
        parts.append(oval([0.060, 0.085, 0.040], [wrist[0], wrist[1] - 0.11, 0], body_mat))

        parts.append(oval([0.070, 0.070, 0.070], hip, joint_mat))
        parts.append(oval([0.068, 0.068, 0.068], knee, joint_mat))
        parts.append(oval([0.052, 0.052, 0.052], ankle, joint_mat))

        parts.append(capsule_between(hip, knee, 0.11, body_mat))
        parts.append(capsule_between(knee, ankle, 0.070, body_mat))
        parts.append(boot(0.24, 0.14, 0.36, foot, foot_mat))

    for i, mesh in enumerate(parts):
        scene.add_geometry(mesh, node_name=f"skin_part_{i}")

    job_id = uuid.uuid4().hex
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    model_path = job_dir / "model.glb"
    meta_path = job_dir / "mesh_skin_metadata.json"

    scene.export(model_path)

    meta = {
        "ok": True,
        "type": "humanoid_mesh_skin",
        "note": "CPU image-guided mesh skin over humanoid proportion guide. Not GPU photo-to-mesh.",
        "profile": profile,
        "points": points,
    }

    meta_path.write_text(json.dumps(meta, indent=2))

    return {
        "ok": True,
        "job_id": job_id,
        "model_path": str(model_path),
        "model_url": f"/outputs/{job_id}/model.glb",
        "metadata_path": str(meta_path),
        "metadata_url": f"/outputs/{job_id}/mesh_skin_metadata.json",
    }


if __name__ == "__main__":
    import sys
    image = sys.argv[1]
    print(json.dumps(build_humanoid_mesh_skin(image), indent=2))
