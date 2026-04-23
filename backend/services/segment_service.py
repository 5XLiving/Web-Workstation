```python id="8u7d2n"
import os
import numpy as np
from PIL import Image, ImageFilter
from backend.services import image_service

MASKS_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "masks")
os.makedirs(MASKS_DIR, exist_ok=True)


def _estimate_background_color(arr: np.ndarray) -> np.ndarray:
    h, w = arr.shape[:2]
    patch = max(1, min(h, w) // 20)

    patches = [
        arr[:patch, :patch],
        arr[:patch, w - patch:w],
        arr[h - patch:h, :patch],
        arr[h - patch:h, w - patch:w],
    ]

    samples = np.concatenate([p.reshape(-1, 3) for p in patches], axis=0)
    return samples.mean(axis=0)


def _clean_mask(mask: np.ndarray) -> np.ndarray:
    mask_img = Image.fromarray(mask, mode="L")
    mask_img = mask_img.filter(ImageFilter.MaxFilter(size=5))
    mask_img = mask_img.filter(ImageFilter.MinFilter(size=5))
    return np.array(mask_img, dtype=np.uint8)


def segment_main_object(image_path: str) -> dict:
    img = image_service.load_image(image_path).convert("RGB")
    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape[:2]

    bg_color = _estimate_background_color(arr)

    dist = np.linalg.norm(arr - bg_color, axis=2)
    brightness = arr.mean(axis=2)

    mask = ((dist > 32) & (brightness > 24)).astype(np.uint8) * 255
    mask = _clean_mask(mask)

    mask_img = Image.fromarray(mask, mode="L")

    image_id = os.path.splitext(os.path.basename(image_path))[0]
    mask_path = os.path.join(MASKS_DIR, f"{image_id}_mask.png")
    image_service.save_png(mask_img, mask_path)

    mask_b64 = image_service.image_to_base64(mask_img)

    return {
        "mask_png_base64": mask_b64,
        "width": w,
        "height": h,
    }
```
