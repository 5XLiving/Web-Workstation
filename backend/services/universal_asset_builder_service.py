from typing import Any, Dict

from backend.services.asset_type_detector_service import detect_asset_type
from backend.services.ai_socket_fit_service import fit_image_to_skeleton
from backend.services.humanoid_skeleton import build_model_from_socket_form
from backend.services.vehicle_builder_service import build_vehicle_from_form
from backend.services.terrain_builder_service import build_terrain_from_form
from backend.services.prop_builder_service import build_prop_from_form
from backend.services.building_builder_service import build_building_from_form
from backend.services.tree_builder_service import build_tree_from_form


def build_universal_asset_from_image(image_path: str) -> Dict[str, Any]:
    detected = detect_asset_type(image_path) or {}
    asset_type = detected.get("asset_type", "prop")

    try:
        if asset_type == "humanoid":
            form = fit_image_to_skeleton(image_path, "humanoid_mech_v2")
            result = build_model_from_socket_form(form)

        elif asset_type in ["vehicle", "bike", "car", "truck", "transport"]:
            form = {"asset_type": asset_type, "image_path": image_path, "scan_result": detected}
            result = build_vehicle_from_form(form)

        elif asset_type in ["terrain", "road", "hill", "ground"]:
            form = {"asset_type": asset_type, "image_path": image_path, "scan_result": detected}
            result = build_terrain_from_form(form)

        elif asset_type in ["building", "house", "tower"]:
            form = {"asset_type": asset_type, "image_path": image_path, "scan_result": detected}
            result = build_building_from_form(form)

        elif asset_type in ["tree", "plant"]:
            form = {"asset_type": asset_type, "image_path": image_path, "scan_result": detected}
            result = build_tree_from_form(form)

        else:
            form = {"asset_type": "prop", "image_path": image_path, "scan_result": detected}
            result = build_prop_from_form(form)

        if not isinstance(result, dict):
            result = {"ok": False, "error": "Builder returned non-dict result", "raw_type": str(type(result))}

        result["ok"] = result.get("ok", True)
        result["asset_type"] = asset_type
        result["detected"] = detected
        return result

    except Exception as e:
        return {
            "ok": False,
            "error": "Universal image asset build failed",
            "message": str(e),
            "asset_type": asset_type,
            "detected": detected,
        }