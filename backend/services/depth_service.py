import numpy as np
from PIL import Image

def compute_depth(image: Image.Image) -> np.ndarray:
    # Placeholder: use image luminance as fake depth
    gray = image.convert("L")
    depth = np.array(gray).astype(np.float32) / 255.0
    return depth

def compute_pointmap(depth: np.ndarray) -> np.ndarray:
    # Placeholder: simple XY grid + depth as Z
    h, w = depth.shape
    y, x = np.meshgrid(np.linspace(-1, 1, h), np.linspace(-1, 1, w), indexing="ij")
    pointmap = np.stack([x, y, depth], axis=-1)
    return pointmap

def get_pointmap(image: Image.Image, mask: Image.Image = None, preset: str = None):
    depth = compute_depth(image)
    pointmap = compute_pointmap(depth)
    return {"depth": depth, "pointmap": pointmap}
