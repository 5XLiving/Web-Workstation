
import os
import numpy as np
from PIL import Image
from backend.services import image_service

MASKS_DIR = os.path.join(os.path.dirname(__file__), '..', 'storage', 'masks')
os.makedirs(MASKS_DIR, exist_ok=True)

def segment_main_object(image_path: str) -> dict:
	# Load image
	img = image_service.load_image(image_path)
	arr = np.array(img.convert('RGB'))
	h, w = arr.shape[:2]

	# Estimate background color from corners
	corners = [arr[0,0], arr[0,-1], arr[-1,0], arr[-1,-1]]
	bg_color = np.mean(corners, axis=0)

	# Compute distance from background color
	dist = np.linalg.norm(arr - bg_color, axis=2)
	brightness = arr.mean(axis=2)
	# Mask: far from bg and not too dark
	mask = ((dist > 32) & (brightness > 32)).astype(np.uint8) * 255

	# Simple morphological clean (dilate then erode)
	from scipy.ndimage import binary_dilation, binary_erosion
	mask = binary_dilation(mask, iterations=2)
	mask = binary_erosion(mask, iterations=2)
	mask = (mask * 255).astype(np.uint8)

	# Save mask as PNG
	mask_img = Image.fromarray(mask, mode='L')
	image_id = os.path.splitext(os.path.basename(image_path))[0]
	mask_path = os.path.join(MASKS_DIR, f"{image_id}_mask.png")
	image_service.save_png(mask_img, mask_path)

	# Encode mask as base64
	mask_b64 = image_service.image_to_base64(mask_img)

	return {
		"mask_png_base64": mask_b64,
		"width": w,
		"height": h
	}
