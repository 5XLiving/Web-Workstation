from pathlib import Path
from PIL import Image
import numpy as np
import json


def detect_cage_layers(image_path: str, cage: dict, job_dir: str) -> dict:
    job_dir = Path(job_dir)
    layer_dir = job_dir / "cage_layers"
    layer_dir.mkdir(parents=True, exist_ok=True)

    grid = cage.get("grid_size", [64, 64, 64])
    size = int(grid[0])

    img = Image.open(image_path).convert("RGBA").resize((size, size))
    arr = np.array(img)

    occupied = cage.get("occupied_cells", [])

    layers = {
        "base_body": [],
        "dark_armor": [],
        "metal_armor": [],
        "gold_trim": [],
        "orange_glow": [],
        "red_cloth": [],
        "unknown_detail": [],
    }

    for cell in occupied:
        x, y, z = cell
        if not (0 <= x < size and 0 <= y < size):
            continue

        r, g, b, a = arr[y, x]

        if a < 20:
            continue

        if r > 90 and g < 80 and b < 80:
            layers["red_cloth"].append(cell)

        elif r > 180 and g > 80 and b < 80:
            layers["orange_glow"].append(cell)

        elif r > 120 and g > 85 and b < 90:
            layers["gold_trim"].append(cell)

        elif r < 75 and g < 75 and b < 75:
            layers["dark_armor"].append(cell)

        elif abs(int(r) - int(g)) < 40 and abs(int(g) - int(b)) < 40:
            layers["metal_armor"].append(cell)

        else:
            layers["unknown_detail"].append(cell)

    result = {
        "ok": True,
        "type": "cage_layer_map",
        "layers": layers,
        "summary": {k: len(v) for k, v in layers.items()},
        "note": "CPU color-based cage layer detection. Later this becomes AI vision layer labeling."
    }

    (layer_dir / "cage_layers.json").write_text(json.dumps(result, indent=2))
    return result
