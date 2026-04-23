 
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
    from scipy import ndimage as ndi
    img = image_service.load_image(image_path).convert("RGB")
    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape[:2]
    bg_color = _estimate_background_color(arr)
    dist = np.linalg.norm(arr - bg_color, axis=2)
    brightness = arr.mean(axis=2)
    # Initial mask: color/brightness threshold
    mask = ((dist > 32) & (brightness > 24)).astype(np.uint8)
    # Clean mask (morphology)
    mask = _clean_mask((mask * 255).astype(np.uint8))
    # --- New logic: keep only largest central object ---
    # Remove border-connected regions (likely background)
    border = np.zeros_like(mask, dtype=bool)
    border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
    border_labels, _ = ndi.label((mask > 0) & border)
    mask_border = ndi.binary_fill_holes(border_labels > 0)
    mask[mask_border] = 0
    # Connected components
    labeled, num = ndi.label(mask > 0)
    if num > 0:
        # Find largest component near image center
        center = (h // 2, w // 2)
        sizes = ndi.sum(mask > 0, labeled, range(1, num + 1))
        centroids = ndi.center_of_mass(mask > 0, labeled, range(1, num + 1))
        # Score: size * (1 - normalized distance from center)
        max_dist = np.hypot(h, w)
        scores = [s * (1 - (np.hypot(c[0] - center[0], c[1] - center[1]) / max_dist)) for s, c in zip(sizes, centroids)]
        best_idx = int(np.argmax(scores))
        main_label = best_idx + 1
        mask = (labeled == main_label).astype(np.uint8) * 255
        # Fill holes in main object
        mask = ndi.binary_fill_holes(mask > 0).astype(np.uint8) * 255
    else:
        mask = np.zeros_like(mask, dtype=np.uint8)
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
