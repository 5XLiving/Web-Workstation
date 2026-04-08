import math
from typing import Any


def _round4(value: float) -> float:
    return round(float(value), 4)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _to_positive_float(value: Any, default: float) -> float:
    num = _to_float(value, default)
    return num if num > 0 else float(default)


def generate_xyz_path_steps(build_package: dict[str, Any]) -> list[dict[str, Any]]:
    dimensions = build_package.get("dimensions", {}) or {}
    origin = build_package.get("origin", {}) or {}

    width = _to_positive_float(dimensions.get("width"), 1.0)
    height = _to_positive_float(dimensions.get("height"), 1.0)
    depth = _to_positive_float(dimensions.get("depth"), 1.0)

    origin_x = _to_float(origin.get("x"), 0.0)
    origin_y = _to_float(origin.get("y"), 0.0)
    origin_z = _to_float(origin.get("z"), 0.0)

    layer_height = _to_positive_float(build_package.get("layer_height"), 0.05)

    total_layers = max(1, math.ceil(height / layer_height))
    steps: list[dict[str, Any]] = []

    for layer_index in range(total_layers):
        layer_number = layer_index + 1
        layer_start_height = layer_index * layer_height
        remaining_height = max(0.0, height - layer_start_height)
        actual_layer_height = min(layer_height, remaining_height)

        if actual_layer_height <= 0:
            continue

        current_z = origin_z + layer_start_height + actual_layer_height

        position = {
            "x": _round4(origin_x),
            "y": _round4(origin_y),
            "z": _round4(current_z),
        }

        steps.append(
            {
                "step_index": len(steps) + 1,
                "kind": "move",
                "layer_index": layer_number,
                "total_layers": total_layers,
                "position": position,
                "meta": {
                    "note": "Move toolhead to layer origin",
                    "phase": "layer_start",
                },
            }
        )

        steps.append(
            {
                "step_index": len(steps) + 1,
                "kind": "deposit",
                "layer_index": layer_number,
                "total_layers": total_layers,
                "position": position,
                "build_slice": {
                    "width": _round4(width),
                    "depth": _round4(depth),
                    "layer_height": _round4(actual_layer_height),
                },
                "meta": {
                    "note": "Deposit rectangular layer slice",
                    "phase": "layer_deposit",
                    "origin": {
                        "x": _round4(origin_x),
                        "y": _round4(origin_y),
                        "z": _round4(origin_z),
                    },
                },
            }
        )

    return steps


def summarize_xyz_path(steps: list[dict[str, Any]]) -> dict[str, Any]:
    deposit_steps = [step for step in steps if step.get("kind") == "deposit"]
    move_steps = [step for step in steps if step.get("kind") == "move"]

    total_layers = 0
    if deposit_steps:
        total_layers = max(int(step.get("layer_index", 0) or 0) for step in deposit_steps)

    return {
        "total_steps": len(steps),
        "move_steps": len(move_steps),
        "deposit_steps": len(deposit_steps),
        "total_layers": total_layers,
    }
