""" xyz_construct_service.py 

Converts a blueprint into chamber build steps for XYZ modular system. This is the only module that feeds the chamber build. """

from typing import Dict, Any
from .xyz_blueprint_schema import validate_blueprint


def _vec3(value: Any, field_name: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{field_name} must be a list of 3 numbers.")
    try:
        return [float(value[0]), float(value[1]), float(value[2])]
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must contain numeric values.")


def construct_from_blueprint(blueprint: Dict[str, Any]) -> Dict[str, Any]:
    validate_blueprint(blueprint)

    raw_parts = blueprint["parts"]
    build_order = blueprint["build_order"]

    parts: Dict[str, Dict[str, Any]] = {}
    for part in raw_parts:
        name = part["name"]
        if name in parts:
            raise ValueError(f"Duplicate part name in blueprint: {name}")
        parts[name] = part

    steps = []
    path_summary = []

    for index, part_name in enumerate(build_order):
        part = parts.get(part_name)
        if not part:
            raise ValueError(f"build_order references missing part: {part_name}")

        step = {
            "step_index": index,
            "action": "place_part",
            "part": str(part_name),
            "anchor": str(part["anchor"]),
            "primitive_type": str(part["primitive_type"]),
            "size": _vec3(part["size"], f"size for {part_name}"),
            "category": str(part.get("category", "generic")),
            "rotation": _vec3(part.get("rotation", [0.0, 0.0, 0.0]), f"rotation for {part_name}"),
            "offset": _vec3(part.get("offset", [0.0, 0.0, 0.0]), f"offset for {part_name}"),
            "shell_thickness": float(part.get("shell_thickness", 0.0)),
        }

        steps.append(step)
        path_summary.append({
            "step_index": index,
            "part": str(part_name),
            "anchor": str(part["anchor"]),
            "category": str(part.get("category", "generic")),
        })

    total_steps = len(steps)
    total_layers = total_steps  # placeholder until you add real chamber/layer slicing

    return {
        "steps": steps,
        "path_summary": path_summary,
        "total_steps": total_steps,
        "total_layers": total_layers,
        "build_order": list(build_order),
    }
