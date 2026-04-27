import sys
import os
sys.path.append(os.getcwd())
from backend.services.segment_service import segment_main_object

# Use the image found in the debug folder
image_path = "backend/storage/masks/ebe46c416e914839b418cad07d8702ef_debug/original_image.png"
if os.path.exists(image_path):
    result = segment_main_object(image_path)
    print("Test Result:")
    for key, value in result.items():
        if key != 'mask_png_base64':
            print(f"{key}: {value}")
else:
    print(f"Error: {image_path} not found")
