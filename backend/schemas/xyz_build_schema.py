from copy import deepcopy

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


def build_default_package() -> dict:
    return deepcopy(DEFAULT_BUILD_PACKAGE)


def normalize_xyz_build_package(input_data: dict) -> dict:
    package = build_default_package()

    if not isinstance(input_data, dict):
        return package

    if isinstance(input_data.get("build_mode"), str) and input_data["build_mode"].strip():
        package["build_mode"] = input_data["build_mode"].strip()

    if isinstance(input_data.get("template"), str) and input_data["template"].strip():
        package["template"] = input_data["template"].strip()

    if isinstance(input_data.get("material"), str) and input_data["material"].strip():
        package["material"] = input_data["material"].strip()

    if isinstance(input_data.get("path_strategy"), str) and input_data["path_strategy"].strip():
        package["path_strategy"] = input_data["path_strategy"].strip()

    if isinstance(input_data.get("layer_height"), (int, float)):
        package["layer_height"] = float(input_data["layer_height"])

    dimensions = input_data.get("dimensions", {})
    if isinstance(dimensions, dict):
        for key in ("width", "height", "depth"):
            if isinstance(dimensions.get(key), (int, float)):
                package["dimensions"][key] = float(dimensions[key])

    origin = input_data.get("origin", {})
    if isinstance(origin, dict):
        for key in ("x", "y", "z"):
            if isinstance(origin.get(key), (int, float)):
                package["origin"][key] = float(origin[key])

    return package


def validate_xyz_build_package(package: dict) -> list[str]:
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
    if not isinstance(layer_height, (int, float)) or float(layer_height) <= 0:
        errors.append("layer_height must be a positive number")

    dimensions = package.get("dimensions")
    if not isinstance(dimensions, dict):
        errors.append("dimensions must be an object")
    else:
        for key in ("width", "height", "depth"):
            value = dimensions.get(key)
            if not isinstance(value, (int, float)) or float(value) <= 0:
                errors.append(f"dimensions.{key} must be a positive number")

    origin = package.get("origin")
    if not isinstance(origin, dict):
        errors.append("origin must be an object")
    else:
        for key in ("x", "y", "z"):
            value = origin.get(key)
            if not isinstance(value, (int, float)):
                errors.append(f"origin.{key} must be a number")

    material = package.get("material")
    if not isinstance(material, str) or not material.strip():
        errors.append("material must be a non-empty string")

    return errors