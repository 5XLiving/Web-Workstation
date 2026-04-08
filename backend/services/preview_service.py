from services.preprocess_service import preprocess
from services.depth_service import get_pointmap
from PIL import Image
import io


def generate_preview(image_bytes, mask_bytes=None, preset=None):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

    mask = None
    if mask_bytes:
        mask = Image.open(io.BytesIO(mask_bytes)).convert("L")

    proc_img = preprocess(image, mask, preset)
    result = get_pointmap(proc_img, mask, preset)

    pointmap = result.get("pointmap")
    if pointmap is None:
        raise ValueError("Preview generation failed: missing pointmap.")

    return {
        "preview_type": "point_cloud",
        "type": "point_cloud",
        "data": pointmap.tolist(),
        "meta": {
            "preset": preset or "armored_biped"
        }
    }
