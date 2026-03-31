import math
from typing import Any


def _round4(value: float) -> float:
    return round(float(value), 4)


def generate_xyz_path_steps(build_package: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Phase 1:
    Create a simple layer-by-layer construction path.
    This is a virtual XYZ builder path, not a final mesh generator.
    """

    dimensions = build_package["dimensions"]
    origin = build_package["origin"]
    layer_height = float(build_package["layer_height"])

    width = float(dimensions["width"])
    height = float(dimensions["height"])
    depth = float(dimensions["depth"])

    origin_x = float(origin["x"])
    origin_y = float(origin["y"])
    origin_z = float(origin["z"])

    total_layers = max(1, math.ceil(height / layer_height))
    steps: list[dict[str, Any]] = []

    for layer_index in range(total_layers):
        current_z = origin_z + min((layer_index + 1) * layer_height, height)

        steps.append(
            {
                "step_index": len(steps) + 1,
                "kind": "move",
                "layer_index": layer_index + 1,
                "position": {
                    "x": _round4(origin_x),
                    "y": _round4(origin_y),
                    "z": _round4(current_z),
                },
                "meta": {
                    "note": "Move toolhead to layer origin",
                },
            }
        )

        steps.append(
            {
                "step_index": len(steps) + 1,
                "kind": "deposit",
                "layer_index": layer_index + 1,
                "position": {
                    "x": _round4(origin_x),
                    "y": _round4(origin_y),
                    "z": _round4(current_z),
                },
                "build_slice": {
                    "width": _round4(width),
                    "depth": _round4(depth),
                    "layer_height": _round4(min(layer_height, height - (layer_index * layer_height))),
                },
                "meta": {
                    "note": "Deposit rectangular layer slice",
                },
            }
        )

    return steps


def summarize_xyz_path(steps: list[dict[str, Any]]) -> dict[str, Any]:
    deposit_steps = [step for step in steps if step.get("kind") == "deposit"]
    move_steps = [step for step in steps if step.get("kind") == "move"]

    return {
        "total_steps": len(steps),
        "move_steps": len(move_steps),
        "deposit_steps": len(deposit_steps),
        "total_layers": len(deposit_steps),
    }