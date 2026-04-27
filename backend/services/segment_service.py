import os
import io
import numpy as np
from PIL import Image, ImageFilter
from rembg import remove
from scipy import ndimage as ndi
from backend.services import image_service

MASKS_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "masks")
os.makedirs(MASKS_DIR, exist_ok=True)

def _clean_mask(mask: np.ndarray) -> np.ndarray:
    mask_img = Image.fromarray(mask, mode="L")
    mask_img = mask_img.filter(ImageFilter.MaxFilter(size=5))
    mask_img = mask_img.filter(ImageFilter.MinFilter(size=5))
    return np.array(mask_img, dtype=np.uint8)

def _largest_center_component(mask_bool: np.ndarray):
    h, w = mask_bool.shape
    labeled, num = ndi.label(mask_bool)
    if num == 0:
        return np.zeros_like(mask_bool, dtype=bool), 0

    center = (h // 2, w // 2)
    sizes = ndi.sum(mask_bool, labeled, range(1, num + 1))
    centroids = ndi.center_of_mass(mask_bool, labeled, range(1, num + 1))
    max_dist = max(np.hypot(h, w) / 2, 1)

    scores = []
    for size, centroid in zip(sizes, centroids):
        dist_to_center = np.hypot(centroid[0] - center[0], centroid[1] - center[1])
        center_score = max(0.0, 1.0 - (dist_to_center / max_dist)) ** 2
        scores.append(float(size) * center_score)

    best_idx = int(np.argmax(scores)) + 1
    final_bool = labeled == best_idx
    final_bool = ndi.binary_fill_holes(final_bool)
    return final_bool, int(num)

def segment_main_object(image_path: str) -> dict:
    image_id = os.path.splitext(os.path.basename(image_path))[0]
    debug_dir = os.path.join(MASKS_DIR, f"{image_id}_debug")
    os.makedirs(debug_dir, exist_ok=True)

    img_rgba = image_service.load_image(image_path).convert("RGBA")
    img_rgba.save(os.path.join(debug_dir, "original_image.png"))

    warning = None
    rejected_reason = None
    component_count = 0

    buf = io.BytesIO()
    img_rgba.save(buf, format="PNG")
    removed = remove(buf.getvalue())

    rembg_img = Image.open(io.BytesIO(removed)).convert("RGBA")
    alpha = np.array(rembg_img.getchannel("A"), dtype=np.uint8)
    Image.fromarray(alpha, mode="L").save(os.path.join(debug_dir, "rembg_mask.png"))

    mask_clean = _clean_mask(alpha)
    mask_bool = mask_clean > 8
    final_bool, component_count = _largest_center_component(mask_bool)
    final_mask = final_bool.astype(np.uint8) * 255

    returned_mask_coverage = float((final_mask > 0).mean())
    if returned_mask_coverage > 0.60:
        final_mask = np.zeros_like(final_mask, dtype=np.uint8)
        rejected_reason = f"final mask coverage {returned_mask_coverage:.3f} > 0.60"
        warning = "mask rejected: coverage too high"
        returned_mask_coverage = 0.0

    Image.fromarray(final_mask, mode="L").save(os.path.join(debug_dir, "final_mask.png"))

    mask_img = Image.fromarray(final_mask, mode="L")
    mask_path = os.path.join(MASKS_DIR, f"{image_id}_mask.png")
    image_service.save_png(mask_img, mask_path)
    mask_b64 = image_service.image_to_base64(mask_img)

    return {
        "ok": True,
        "mask_png_base64": mask_b64,
        "width": img_rgba.width,
        "height": img_rgba.height,
        "mask_coverage": returned_mask_coverage,
        "returned_mask_coverage": returned_mask_coverage,
        "component_count": component_count,
        "rejected_reason": rejected_reason,
        "warning": warning,
        "debug_dir": debug_dir,
        "segment_version": "REMBG_PRIMARY_V1",
    }