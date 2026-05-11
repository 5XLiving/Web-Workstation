import os
import json
import base64
import requests


WORKER_URL = os.getenv("FIVEXLIVING_SHARED_WORKER_URL", "").rstrip("/")
TIMEOUT = int(os.getenv("FIVEXLIVING_SHARED_WORKER_TIMEOUT_SECONDS", "45"))


def create_shape_plan(image_path: str) -> dict:
    if not WORKER_URL:
        raise RuntimeError("FIVEXLIVING_SHARED_WORKER_URL is empty in .env")

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    prompt = """
You are a 3D asset planner. Analyze the uploaded cutout image and return ONLY valid JSON.
Do not return markdown, explanation, or code fence.

Create a procedural lowpoly 3D plan.

Allowed shapes:
box, sphere, cylinder, capsule, flat_plate, armor_plate, tapered_box

JSON schema:
{
  "object_type": "short category",
  "style": "lowpoly_ai_vision",
  "parts": [
    {
      "name": "part_name",
      "shape": "allowed_shape",
      "position": [x,y,z],
      "scale": [x,y,z],
      "taper_top": 0.7,
      "color": [r,g,b,1]
    }
  ],
  "details": []
}

Rules:
- Make the model resemble the uploaded image category.
- Detect animal, mech, humanoid, vehicle, weapon, building, furniture, prop, or unknown.
- Detect visible large components: head, body, arms, legs, wings, wheels, cannons, shield, armor, base, ears, tail, horns, claws, glow panels.
- Use different JSON for every image.
- Use 6 to 22 total parts.
- Coordinate system: y is height, z is depth, front faces positive z.
- Model height should be around 3 units.
- Colors must be floats from 0 to 1.
- Do not always create humanoid head/body/arms/legs unless the image is humanoid.
"""

    payload = {
        "mode": "vision_json",
        "prompt": prompt,
        "image_base64": image_b64,
        "mime_type": "image/png",
    }

    res = requests.post(WORKER_URL, json=payload, timeout=TIMEOUT)

    if not res.ok:
        raise RuntimeError(
            f"Worker HTTP {res.status_code}: {res.text[:1000]}"
        )

    try:
        data = res.json()
    except Exception:
        raise RuntimeError(
            f"Worker returned non-JSON response: {res.text[:1000]}"
        )

    if isinstance(data, dict) and "plan" in data:
        plan = data["plan"]
    elif isinstance(data, dict) and "parts" in data:
        plan = data
    elif isinstance(data, dict) and "text" in data:
        try:
            plan = json.loads(data["text"])
        except Exception:
            raise RuntimeError(f"Worker text is not valid JSON: {data['text'][:1000]}")
    elif isinstance(data, str):
        try:
            plan = json.loads(data)
        except Exception:
            raise RuntimeError(f"Worker string is not valid JSON: {data[:1000]}")
    else:
        raise RuntimeError(f"Worker response missing plan/parts/text: {str(data)[:1000]}")

    if not isinstance(plan, dict):
        raise RuntimeError("AI plan is not a JSON object")

    if "parts" not in plan or not isinstance(plan["parts"], list):
        raise RuntimeError(f"AI plan missing parts list: {str(plan)[:1000]}")

    plan.setdefault("object_type", "unknown")
    plan.setdefault("style", "lowpoly_ai_vision")
    plan.setdefault("details", [])

    return plan