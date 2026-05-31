from backend.services.ai_scan_service import scan_image_to_build_form
import json

result = scan_image_to_build_form("test.png")

print(json.dumps(result, indent=2))
