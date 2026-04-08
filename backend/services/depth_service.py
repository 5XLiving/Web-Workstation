import numpy as np
from PIL import Image


def _mask_array(mask: Image.Image | None, size: tuple[int, int]) -> np.ndarray | None:
    if mask is None:
        return None

    if mask.size != size:
        mask = mask.resize(size, Image.NEAREST)

    mask_np = np.array(mask.convert("L")).astype(np.float32) / 255.0
    return mask_np


def compute_depth(image: Image.Image, mask: Image.Image | None = None) -> np.ndarray:
    """
    Placeholder depth:
    use image luminance as fake depth, optionally masked.
    """
    gray = image.convert("L")
    depth = np.array(gray).astype(np.float32) / 255.0

    mask_np = _mask_array(mask, image.size)
    if mask_np is not None:
        depth = depth * mask_np

    return depth


def compute_pointmap(depth: np.ndarray, mask: Image.Image | None = None) -> np.ndarray:
    """
    Placeholder pointmap:
    simple XY grid + depth as Z, optionally masked.
    """
    h, w = depth.shape

    y, x = np.meshgrid(
        np.linspace(-1.0, 1.0, h, dtype=np.float32),
        np.linspace(-1.0, 1.0, w, dtype=np.float32),
        indexing="ij",
    )

    pointmap = np.stack([x, y, depth.astype(np.float32)], axis=-1)

    if mask is not None:
        mask_np = _mask_array(mask, (w, h))
        if mask_np is not None:
            pointmap[:, :, 0] *= mask_np
            pointmap[:, :, 1] *= mask_np
            pointmap[:, :, 2] *= mask_np

    return pointmap


def get_pointmap(
    image: Image.Image,
    mask: Image.Image | None = None,
    preset: str | None = None,
) -> dict:
    depth = compute_depth(image, mask=mask)
    pointmap = compute_pointmap(depth, mask=mask)

    return {
        "depth": depth,
        "pointmap": pointmap,
        "meta": {
            "preset": preset,
            "masked": mask is not None,
        },
    }
