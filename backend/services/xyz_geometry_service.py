from typing import Any


def _round4(value: float) -> float:
    return round(float(value), 4)


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _positive_num(value: Any, default: float) -> float:
    num = _num(value, default)
    return num if num > 0 else float(default)


def _point(x: Any = 0.0, y: Any = 0.0, z: Any = 0.0) -> dict[str, float]:
    return {
        "x": _round4(_num(x)),
        "y": _round4(_num(y)),
        "z": _round4(_num(z)),
    }


def _step_position(step: dict[str, Any], fallback: dict[str, float]) -> dict[str, float]:
    pos = step.get("position") or {}
    return {
        "x": _round4(_num(pos.get("x"), fallback["x"])),
        "y": _round4(_num(pos.get("y"), fallback["y"])),
        "z": _round4(_num(pos.get("z"), fallback["z"])),
    }


def _build_segments(
    steps: list[dict[str, Any]],
    origin: dict[str, float],
    default_layer_height: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    all_segments: list[dict[str, Any]] = []
    travel_segments: list[dict[str, Any]] = []
    deposit_segments: list[dict[str, Any]] = []

    previous = _point(origin["x"], origin["y"], origin["z"])

    for idx, step in enumerate(steps):
        current = _step_position(step, previous)
        kind = str(step.get("kind") or "move")
        layer_index = _int(step.get("layer_index"), 0)
        step_index = _int(step.get("step_index"), idx + 1)

        segment: dict[str, Any] = {
            "step_index": step_index,
            "layer_index": layer_index,
            "kind": kind,
            "from": previous,
            "to": current,
            "length": _round4(
                (
                    (current["x"] - previous["x"]) ** 2
                    + (current["y"] - previous["y"]) ** 2
                    + (current["z"] - previous["z"]) ** 2
                ) ** 0.5
            ),
        }

        if kind == "deposit":
            build_slice = step.get("build_slice") or {}
            segment["slice"] = {
                "width": _round4(_num(build_slice.get("width"), 0.0)),
                "depth": _round4(_num(build_slice.get("depth"), 0.0)),
                "layer_height": _round4(
                    _positive_num(build_slice.get("layer_height"), default_layer_height)
                ),
            }
            deposit_segments.append(segment)
        else:
            travel_segments.append(segment)

        all_segments.append(segment)
        previous = current

    return all_segments, travel_segments, deposit_segments


def build_xyz_geometry_state(
    build_package: dict[str, Any],
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    dimensions = build_package.get("dimensions", {}) or {}
    origin_raw = build_package.get("origin", {}) or {}
    template = str(build_package.get("template") or "box_block")
    layer_height = _positive_num(build_package.get("layer_height"), 0.05)

    width = _positive_num(dimensions.get("width"), 1.0)
    height = _positive_num(dimensions.get("height"), 1.0)
    depth = _positive_num(dimensions.get("depth"), 1.0)

    origin = {
        "x": _round4(_num(origin_raw.get("x"), 0.0)),
        "y": _round4(_num(origin_raw.get("y"), 0.0)),
        "z": _round4(_num(origin_raw.get("z"), 0.0)),
    }

    deposited_layers = [step for step in steps if step.get("kind") == "deposit"]

    all_segments, travel_segments, deposit_segments = _build_segments(
        steps=steps,
        origin=origin,
        default_layer_height=layer_height,
    )

    built_height = _round4(
        min(
            height,
            sum(
                _positive_num(
                    (segment.get("slice") or {}).get("layer_height"),
                    layer_height,
                )
                for segment in deposit_segments
            ),
        )
    )

    last_toolhead_position = (
        _step_position(steps[-1], origin)
        if steps
        else _point(origin["x"], origin["y"], origin["z"])
    )

    current_layer = 0
    if deposited_layers:
        current_layer = max(_int(step.get("layer_index"), 0) for step in deposited_layers)

    bed_margin = 1.0
    bed = {
        "origin": _point(
            origin["x"] - bed_margin,
            origin["y"] - bed_margin,
            origin["z"],
        ),
        "size": {
            "width": _round4(width + (bed_margin * 2.0)),
            "depth": _round4(depth + (bed_margin * 2.0)),
            "height": _round4(max(height + 1.0, 1.0)),
        },
    }

    build_volume = {
        "origin": _point(origin["x"], origin["y"], origin["z"]),
        "size": {
            "width": _round4(width),
            "depth": _round4(depth),
            "height": _round4(height),
        },
    }

    build_progress = {
        "built_height": built_height,
        "progress_ratio": _round4(built_height / height if height > 0 else 0.0),
        "completed_layers": len(deposited_layers),
        "current_layer": current_layer,
        "total_layers": current_layer,
        "total_steps": len(steps),
    }

    chamber_state = {
        "machine_type": "spatial_fabrication",
        "axis_map": {
            "x": "width_axis",
            "y": "depth_axis",
            "z": "height_axis",
        },
        "platform": bed,
        "build_volume": build_volume,
        "emitter": {
            "kind": "tri_pointer_emitter",
            "position": last_toolhead_position,
            "current_step_index": _int(steps[-1].get("step_index"), len(steps)) if steps else 0,
            "current_layer": current_layer,
        },
        "build_progress": build_progress,
        "path_segments": all_segments,
        "travel_segments": travel_segments,
        "deposit_segments": deposit_segments,
    }

    return {
        "template": template,
        "dimensions": {
            "width": _round4(width),
            "height": _round4(height),
            "depth": _round4(depth),
        },
        "origin": origin,
        "build_progress": build_progress,
        "chamber_state": chamber_state,
        "fabrication_preview": {
            "kind": "xyz_fabrication_preview",
            "platform": bed,
            "build_volume": build_volume,
            "emitter": chamber_state["emitter"],
            "current_layer": current_layer,
            "built_height": built_height,
        },
        "debug_proxy": {
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


def build_xyz_preview_payload(
    build_package: dict[str, Any],
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    geometry_state = build_xyz_geometry_state(build_package, steps)

    return {
        "placeholder": False,
        "kind": "xyz_fabrication_preview",
        "template": geometry_state["template"],
        "geometry_state": geometry_state,
        "chamber_state": geometry_state["chamber_state"],
        "message": "XYZ spatial fabrication preview generated.",
    }