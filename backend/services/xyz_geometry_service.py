from typing import Any


def _round4(value: float) -> float:
    return round(float(value), 4)


def build_xyz_geometry_state(build_package: dict[str, Any], steps: list[dict[str, Any]]) -> dict[str, Any]:
    dimensions = build_package["dimensions"]
    origin = build_package["origin"]
    layer_height = float(build_package["layer_height"])

    width = float(dimensions["width"])
    height = float(dimensions["height"])
    depth = float(dimensions["depth"])

    deposited_layers = [step for step in steps if step.get("kind") == "deposit"]
    built_height = min(height, len(deposited_layers) * layer_height)

    return {
        "template": build_package["template"],
        "dimensions": {
            "width": _round4(width),
            "height": _round4(height),
            "depth": _round4(depth),
        },
        "origin": {
            "x": _round4(origin["x"]),
            "y": _round4(origin["y"]),
            "z": _round4(origin["z"]),
        },
        "build_progress": {
            "built_height": _round4(built_height),
            "progress_ratio": _round4(built_height / height if height > 0 else 0.0),
            "completed_layers": len(deposited_layers),
        },
        "preview_object": {
            "kind": "box_proxy",
            "position": {
                "x": _round4(origin["x"]),
                "y": _round4(origin["y"]),
                "z": _round4(origin["z"] + (built_height / 2.0)),
            },
            "size": {
                "x": _round4(width),
                "y": _round4(depth),
                "z": _round4(built_height),
            },
        },
    }


def build_xyz_preview_payload(build_package: dict[str, Any], steps: list[dict[str, Any]]) -> dict[str, Any]:
    geometry_state = build_xyz_geometry_state(build_package, steps)

    return {
        "placeholder": True,
        "kind": "xyz_construct_preview",
        "template": build_package["template"],
        "geometry_state": geometry_state,
        "message": "XYZ construction preview generated.",
    }