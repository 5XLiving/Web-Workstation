from copy import deepcopy
from typing import Any

ALLOWED_TEMPLATES = {
    "box_block",
    "cylinder_block",
}

ALLOWED_BUILD_MODES = {
    "xyz_construct",
}

ALLOWED_PATH_STRATEGIES = {
    "layer_fill",
}

DEFAULT_BUILD_PACKAGE = {
    "build_mode": "xyz_construct",
    "template": "box_block",
    "dimensions": {
        "width": 1.2,
        "height": 1.0,
        "depth": 0.35,
    },
    "material": "default_shell",
    "layer_height": 0.05,
    "path_strategy": "layer_fill",
    "origin": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
    },
}


def build_default_package() -> dict[str, Any]:
    return deepcopy(DEFAULT_BUILD_PACKAGE)


def _clean_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value if value else None


def _to_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None
    return None


def normalize_xyz_build_package(input_data: dict[str, Any]) -> dict[str, Any]:
    package = build_default_package()

    if not isinstance(input_data, dict):
        return package

    build_mode = _clean_string(input_data.get("build_mode"))
    if build_mode:
        package["build_mode"] = build_mode.lower()

    template = _clean_string(input_data.get("template"))
    if template:
        package["template"] = template.lower()

    material = _clean_string(input_data.get("material"))
    if material:
        package["material"] = material

    path_strategy = _clean_string(input_data.get("path_strategy"))
    if path_strategy:
        package["path_strategy"] = path_strategy.lower()

    layer_height = _to_number(input_data.get("layer_height"))
    if layer_height is not None:
        package["layer_height"] = layer_height

    dimensions = input_data.get("dimensions", {})
    if isinstance(dimensions, dict):
        for key in ("width", "height", "depth"):
            value = _to_number(dimensions.get(key))
            if value is not None:
                package["dimensions"][key] = value

    origin = input_data.get("origin", {})
    if isinstance(origin, dict):
        for key in ("x", "y", "z"):
            value = _to_number(origin.get(key))
            if value is not None:
                package["origin"][key] = value

    return package


def validate_xyz_build_package(package: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(package, dict):
        return ["XYZ build package must be an object"]

    build_mode = package.get("build_mode")
    if build_mode not in ALLOWED_BUILD_MODES:
        errors.append(f"Invalid build_mode: {build_mode}")

    template = package.get("template")
    if template not in ALLOWED_TEMPLATES:
        errors.append(f"Invalid template: {template}")

    path_strategy = package.get("path_strategy")
    if path_strategy not in ALLOWED_PATH_STRATEGIES:
        errors.append(f"Invalid path_strategy: {path_strategy}")

    layer_height = package.get("layer_height")
    if isinstance(layer_height, bool) or not isinstance(layer_height, (int, float)) or float(layer_height) <= 0:
        errors.append("layer_height must be a positive number")

    dimensions = package.get("dimensions")
    if not isinstance(dimensions, dict):
        errors.append("dimensions must be an object")
    else:
        for key in ("width", "height", "depth"):
            value = dimensions.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) <= 0:
                errors.append(f"dimensions.{key} must be a positive number")

    origin = package.get("origin")
    if not isinstance(origin, dict):
        errors.append("origin must be an object")
    else:
        for key in ("x", "y", "z"):
            value = origin.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errors.append(f"origin.{key} must be a number")

    material = package.get("material")
    if not isinstance(material, str) or not material.strip():
        errors.append("material must be a non-empty string")

    return errors