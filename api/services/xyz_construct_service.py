"""
xyz_construct_service.py

Converts a blueprint into chamber build steps for XYZ modular system.
This is the only module that feeds the chamber build.
"""
from typing import Dict, Any, List
from .xyz_blueprint_schema import validate_blueprint



def construct_from_blueprint(blueprint: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts a blueprint into chamber build steps.
    Returns dict with: steps, path_summary, total_layers, build_order
    """
    validate_blueprint(blueprint)
    steps = []
    path_summary = []
    build_order = blueprint["build_order"]
    parts = {p["name"]: p for p in blueprint["parts"]}

    for part_name in build_order:
        part = parts.get(part_name)
        if not part:
            raise ValueError(f"build_order references missing part: {part_name}")
        step = {
            "action": "place_part",
            "part": part_name,
            "anchor": part["anchor"],
            "primitive_type": part["primitive_type"],
            "size": part["size"],
            "category": part.get("category", "generic"),
            "rotation": part.get("rotation", [0.0, 0.0, 0.0]),
            "offset": part.get("offset", [0.0, 0.0, 0.0]),
            "shell_thickness": part.get("shell_thickness", 0.0)
        }
        steps.append(step)
        path_summary.append({
            "part": part_name,
            "anchor": part["anchor"],
            "category": part.get("category", "generic")
        })

    total_layers = len(steps)
    return {
        "steps": steps,
        "path_summary": path_summary,
        "total_layers": total_layers,
        "build_order": build_order
    }
