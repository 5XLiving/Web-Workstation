from typing import Any, Dict

from backend.services.asset_type_detector_service import detect_asset_type
from backend.services.universal_asset_service import build_universal_asset
from backend.services.custom_asset_builder_service import build_custom_asset_from_image


def normalize_base_form(raw: str) -> str:
    raw = (raw or "unknown").lower().strip()

    if raw in {"humanoid", "mech", "robot", "character", "person", "humanoid_mech"}:
        return "humanoid"

    if raw in {"vehicle", "transport", "transportation", "car", "bike", "truck", "ship"}:
        return "transportation"

    if raw in {"terrain", "scenery", "road", "ground", "hill", "landscape"}:
        return "scenery"

    if raw in {"building", "house", "tower"}:
        return "building"

    if raw in {"tree", "plant", "rock", "fixture", "prop", "crate", "barrel", "table", "chair"}:
        return "fixture"

    return "custom"


def route_asset_from_image(
    image_path: str,
    style: str = "lowpoly",
    count: int = 1,
    manual_type: str | None = None,
) -> Dict[str, Any]:

    detected = detect_asset_type(image_path) or {}
    raw_type = manual_type or detected.get("asset_type") or detected.get("base_form") or "custom"
    base_form = normalize_base_form(raw_type)

    if base_form == "humanoid":
        result = build_custom_asset_from_image(
            image_path=image_path,
            asset_id="humanoid_1",
            label="humanoid_mech",
            style=style,
        )

    elif base_form == "transportation":
        result = build_custom_asset_from_image(
            image_path=image_path,
            asset_id="transport_1",
            label="transportation",
            style=style,
        )

    elif base_form == "scenery":
        result = build_universal_asset(
            asset_type="terrain",
            style=style,
            count=count,
            options={"source_image": image_path, "detected": detected},
        )

    elif base_form == "building":
        result = build_universal_asset(
            asset_type="building",
            style=style,
            count=count,
            options={"source_image": image_path, "detected": detected},
        )

    elif base_form == "fixture":
        asset_type = raw_type if raw_type in {
            "tree", "rock", "bridge", "hill", "building", "house", "tower",
            "table", "chair", "crate", "barrel", "fence", "lamp", "sign",
            "terrain", "fixture", "prop"
        } else "prop"

        result = build_universal_asset(
            asset_type=asset_type,
            style=style,
            count=count,
            options={"source_image": image_path, "detected": detected},
        )

    else:
        result = build_custom_asset_from_image(
            image_path=image_path,
            asset_id="custom_1",
            label=raw_type or "custom_asset",
            style=style,
        )

    result["detected"] = detected
    result["raw_asset_type"] = raw_type
    result["base_form"] = base_form
    result["source_image"] = image_path

    return result
