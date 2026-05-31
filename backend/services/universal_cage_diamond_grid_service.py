from __future__ import annotations

from typing import Any, Dict, List
import copy


VIEW_BY_NORMAL = {
    "front": [0, 0, 1],
    "back": [0, 0, -1],
    "left": [-1, 0, 0],
    "right": [1, 0, 0],
    "top": [0, 1, 0],
    "bottom": [0, -1, 0],
}


def _make_diamond_cell(
    zone_name: str,
    view: str,
    row: int,
    col: int,
    rows: int,
    cols: int,
) -> Dict[str, Any]:
    u0 = col / cols
    u1 = (col + 1) / cols
    v0 = row / rows
    v1 = (row + 1) / rows

    uc = (u0 + u1) / 2
    vc = (v0 + v1) / 2

    return {
        "cell_id": f"{zone_name}_{view}_{row}_{col}",
        "view": view,
        "row": row,
        "col": col,
        "diamond_uv": [
            [uc, v0],
            [u1, vc],
            [uc, v1],
            [u0, vc],
        ],
        "rect_uv": [
            [u0, v0],
            [u1, v0],
            [u1, v1],
            [u0, v1],
        ],
        "mesh_anchor": f"{zone_name}_{view}",
        "normal_hint": VIEW_BY_NORMAL.get(view, [0, 0, 1]),
    }


def build_zone_diamond_grid(
    zone_name: str,
    rows: int = 8,
    cols: int = 8,
    views: List[str] | None = None,
) -> Dict[str, Any]:
    views = views or ["front", "back", "left", "right", "top", "bottom"]

    cells = []

    for view in views:
      for row in range(rows):
        for col in range(cols):
          cells.append(
              _make_diamond_cell(
                  zone_name=zone_name,
                  view=view,
                  row=row,
                  col=col,
                  rows=rows,
                  cols=cols,
              )
          )

    return {
        "type": "universal_diamond_grid",
        "version": "diamond_grid_v1",
        "rows": rows,
        "cols": cols,
        "views": views,
        "cell_count": len(cells),
        "cells": cells,
        "rule": "Every cage zone receives universal view-based diamond texture cells.",
    }


def add_diamond_grid_to_cage(
    cage: Dict[str, Any],
    rows: int = 8,
    cols: int = 8,
) -> Dict[str, Any]:
    out = copy.deepcopy(cage)

    zones = out.get("zones", [])

    for zone in zones:
        zone_name = zone.get("name") or "zone"

        zone["diamond_grid"] = build_zone_diamond_grid(
            zone_name=zone_name,
            rows=rows,
            cols=cols,
        )

    metadata = out.setdefault("metadata", {})
    metadata["diamond_grid_enabled"] = True
    metadata["diamond_grid_rows"] = rows
    metadata["diamond_grid_cols"] = cols
    metadata["diamond_grid_rule"] = (
        "Texture projection should use diamond_grid cells first, "
        "semantic body zones second."
    )

    return out