from typing import Any, Dict
from backend.services.custom_asset_plan_service import build_custom_asset_plan


def build_custom_asset_from_image(
    image_path: str,
    asset_id: str = "custom_1",
    label: str = "custom_asset",
    style: str = "lowpoly_custom",
) -> Dict[str, Any]:

    plan = build_custom_asset_plan(
        image_path=image_path,
        asset_id=asset_id,
        label=label,
        style=style,
    )

    return {
        "ok": True,
        "type": "custom_asset",
        "asset_type": "custom",
        "custom_asset_type": label,
        "style": style,
        "assets": [
            {
                "id": asset_id,
                "asset_type": "custom",
                "custom_asset_type": label,
                "style": style,
                "plan": plan,
                "build_profile": {
                    "primitive_mode": "custom_image_decomposition",
                    "mesh_skin": "pending_visual_detail",
                    "collider": "auto",
                },
                "status": "generated",
            }
        ],
    }