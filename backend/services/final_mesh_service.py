from pathlib import Path
import uuid
import json

from backend.services.asset_detect_service import detect_asset_from_image
from backend.services.universal_multiview_service import create_multiview_from_image
from backend.services.texture_bake_service import bake_multiview_to_scene
from backend.services.ai_blueprint_engineer_service import generate_blueprint_from_image
from backend.services.isometric_cage_service import build_isometric_cage
from backend.services.cage_layer_detect_service import detect_cage_layers
from backend.services.json_template_mesh_builder_service import build_scene_from_template_file


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "storage" / "outputs"
TEMPLATE_DIR = PROJECT_ROOT / "backend" / "templates"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


HUMANOID_TYPES = {
    "humanoid",
    "humanoid_mech",
    "human",
    "character",
    "robot",
    "mech",
}


def _safe_asset_type(detect: dict) -> str:
    asset_type = str(detect.get("asset_type") or "").strip().lower()

    if not asset_type:
        return "generic_object"

    if asset_type in HUMANOID_TYPES:
        return "humanoid_mech"

    return asset_type


def _template_for_asset(asset_type: str) -> Path | None:
    """
    Only humanoid/mech uses humanoid_mech_v2.json.
    Unknown/object/flower must NOT fallback to humanoid.
    """
    if asset_type == "humanoid_mech":
        return TEMPLATE_DIR / "humanoid_mech_v2.json"

    return None


def build_generic_placeholder_scene(image_path: str, cage: dict):
    """
    Temporary safe fallback.
    This avoids wrongly creating humanoids for flowers/objects.
    Later replace this with plant_builder / generic_object_builder.
    """
    import trimesh

    scene = trimesh.Scene()

    mesh = trimesh.creation.box(extents=[0.8, 0.8, 0.8])
    mesh.apply_translation([0, 0.4, 0])

    scene.add_geometry(mesh, node_name="generic_object_placeholder")
    return scene


def build_final_mesh_from_image(image_path: str) -> dict:
    job_id = uuid.uuid4().hex
    job_dir = OUTPUT_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    detect = detect_asset_from_image(image_path)
    asset_type = _safe_asset_type(detect)

    views = create_multiview_from_image(image_path, str(job_dir), detect)
    cage = build_isometric_cage(image_path, str(job_dir), grid_size=64)
    layers = detect_cage_layers(image_path, cage, str(job_dir))
    blueprint = generate_blueprint_from_image(image_path, detect)

    template_path = _template_for_asset(asset_type)

    if template_path and template_path.exists():
        scene = build_scene_from_template_file(str(template_path))
        builder_mode = "json_template"
        template_used = str(template_path)
    else:
        scene = build_generic_placeholder_scene(image_path, cage)
        builder_mode = "generic_placeholder"
        template_used = None

    bake = bake_multiview_to_scene(scene, views, str(job_dir))

    final_path = job_dir / "final_model.glb"
    scene.export(final_path)

    result = {
        "ok": True,
        "stage": "final_mesh",
        "job_id": job_id,
        "asset_type": asset_type,
        "detected_parts": detect.get("parts", []),
        "detect": detect,
        "multiview": views,
        "cage": "generated",
        "layers": layers,
        "blueprint": blueprint,
        "builder_mode": builder_mode,
        "template_used": template_used,
        "bake": "completed",
        "final_model_url": f"/outputs/{job_id}/final_model.glb",
        "note": (
            "Final mesh pipeline now uses JSON template builder for humanoid_mech. "
            "Unknown/non-humanoid assets no longer fallback to humanoid."
        ),
    }

    (job_dir / "final_mesh_metadata.json").write_text(json.dumps(result, indent=2))
    return result
