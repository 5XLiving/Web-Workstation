DIST_THRESHOLD = 40
BRIGHTNESS_THRESHOLD = 30
STRICT_DIST_THRESHOLD = 56
STRICT_BRIGHTNESS_THRESHOLD = 40
 
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
    # Initial mask: color/brightness threshold (tighter)
    mask = ((dist > DIST_THRESHOLD) & (brightness > BRIGHTNESS_THRESHOLD)).astype(np.uint8)
    initial_fg = mask > 0
    initial_coverage = float(initial_fg.mean())
    # Remove border-connected foreground using binary propagation
    fg = initial_fg.copy()
    seed = np.zeros_like(fg, dtype=bool)
    seed[0, :] = fg[0, :]
    seed[-1, :] = fg[-1, :]
    seed[:, 0] = fg[:, 0]
    seed[:, -1] = fg[:, -1]
    border_connected = ndi.binary_propagation(seed, mask=fg)
    fg = fg & (~border_connected)
    # Clean mask (morphology)
    mask_clean = _clean_mask((fg.astype(np.uint8) * 255))
    fg_clean = mask_clean > 0
    coverage = float(fg_clean.mean())
    # Safety: if mask is still too large, try stricter threshold once
    tried_strict = False
    if coverage > 0.90:
        tried_strict = True
        mask2 = ((dist > STRICT_DIST_THRESHOLD) & (brightness > STRICT_BRIGHTNESS_THRESHOLD)).astype(np.uint8)
        fg2 = mask2 > 0
        seed2 = np.zeros_like(fg2, dtype=bool)
        seed2[0, :] = fg2[0, :]
        seed2[-1, :] = fg2[-1, :]
        seed2[:, 0] = fg2[:, 0]
        seed2[:, -1] = fg2[:, -1]
        border_connected2 = ndi.binary_propagation(seed2, mask=fg2)
        fg2 = fg2 & (~border_connected2)
        mask_clean2 = _clean_mask((fg2.astype(np.uint8) * 255))
        fg_clean2 = mask_clean2 > 0
        coverage2 = float(fg_clean2.mean())
        if coverage2 < 0.90:
            fg_clean = fg_clean2
            mask_clean = mask_clean2
            coverage = coverage2
        else:
            fg_clean = np.zeros_like(fg_clean)
            mask_clean = np.zeros_like(mask_clean)
            coverage = 0.0
    # Connected components
    labeled, num = ndi.label(fg_clean)
    component_count = int(num)
    if num > 0:
        # Find largest component near image center
        center = (h // 2, w // 2)
        sizes = ndi.sum(fg_clean, labeled, range(1, num + 1))
        centroids = ndi.center_of_mass(fg_clean, labeled, range(1, num + 1))
        max_dist = np.hypot(h, w)
        scores = [s * (1 - (np.hypot(c[0] - center[0], c[1] - center[1]) / max_dist)) for s, c in zip(sizes, centroids)]
        best_idx = int(np.argmax(scores))
        main_label = best_idx + 1
        mask_final = (labeled == main_label).astype(np.uint8) * 255
        # Fill holes in main object
        mask_final = ndi.binary_fill_holes(mask_final > 0).astype(np.uint8) * 255
        final_fg_coverage = float((mask_final > 0).mean())
    else:
        mask_final = np.zeros_like(mask_clean, dtype=np.uint8)
        final_fg_coverage = 0.0
    mask_img = Image.fromarray(mask_final, mode="L")
    image_id = os.path.splitext(os.path.basename(image_path))[0]
    mask_path = os.path.join(MASKS_DIR, f"{image_id}_mask.png")
    image_service.save_png(mask_img, mask_path)
    mask_b64 = image_service.image_to_base64(mask_img)
    return {
        "mask_png_base64": mask_b64,
        "width": w,
        "height": h,
        "mask_coverage": final_fg_coverage,
        "bg_color": [float(x) for x in bg_color],
        "initial_foreground_coverage": initial_coverage,
        "final_foreground_coverage": coverage,
        "component_count": component_count,
        "strict_threshold_used": tried_strict,
    }
