import os
import base64
import requests
from io import BytesIO
from pathlib import Path
from PIL import Image


DEFAULT_WORKER_URL = "https://throbbing-lab-1440.hello5xliving.workers.dev/multiview"


def _fit_on_canvas(img: Image.Image, canvas_size=(1024, 1024)) -> Image.Image:
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    work = img.copy().convert("RGBA")
    work.thumbnail(canvas_size, Image.LANCZOS)
    x = (canvas_size[0] - work.width) // 2
    y = (canvas_size[1] - work.height) // 2
    canvas.paste(work, (x, y), work)
    return canvas


def _encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _decode_base64_image(value: str) -> Image.Image:
    if value.startswith("data:image"):
        value = value.split(",", 1)[1]
    image_bytes = base64.b64decode(value)
    return Image.open(BytesIO(image_bytes)).convert("RGBA")


def _generate_ai_view(source_image_path: str, view_name: str, prompt: str) -> Image.Image:
    ai_url = os.getenv("AI_IMAGE_API_URL", DEFAULT_WORKER_URL)
    ai_key = os.getenv("AI_IMAGE_API_KEY", "")

    image_data = _encode_image_to_base64(source_image_path)

    headers = {"Content-Type": "application/json"}
    if ai_key:
        headers["Authorization"] = f"Bearer {ai_key}"

    payload = {
        "mode": "multiview",
        "view": view_name,
        "prompt": prompt,
        "image": f"data:image/png;base64,{image_data}",
        "size": "1024x1024",
        "canvas_size": [1024, 1024],
    }

    response = requests.post(ai_url, json=payload, headers=headers, timeout=180)
    response.raise_for_status()

    result = response.json()

    if result.get("ok") is False:
        raise ValueError(result.get("error") or "Worker AI returned ok=false")

    if "image_url" in result:
        img_response = requests.get(result["image_url"], timeout=60)
        img_response.raise_for_status()
        return Image.open(BytesIO(img_response.content)).convert("RGBA")

    if "image" in result:
        return _decode_base64_image(result["image"])

    if "image_base64" in result:
        return _decode_base64_image(result["image_base64"])

    if "data" in result:
        if isinstance(result["data"], dict):
            if "image" in result["data"]:
                return _decode_base64_image(result["data"]["image"])
            if "image_base64" in result["data"]:
                return _decode_base64_image(result["data"]["image_base64"])
            if "image_url" in result["data"]:
                img_response = requests.get(result["data"]["image_url"], timeout=60)
                img_response.raise_for_status()
                return Image.open(BytesIO(img_response.content)).convert("RGBA")

        if isinstance(result["data"], str):
            return _decode_base64_image(result["data"])

    raise ValueError(
        f"Unexpected Worker response keys: {list(result.keys())}. "
        "Expected image, image_base64, image_url, or data."
    )


def create_multiview_from_image(
    image_path: str,
    job_dir: str = None,
    detect: dict = None,
) -> dict:
    job_dir = Path(job_dir or "/tmp/5xliving_multiview")
    detect = detect or {}

    view_dir = job_dir / "multiview"
    view_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(image_path).convert("RGBA")
    front = _fit_on_canvas(img, (1024, 1024))

    paths = {
        "front": view_dir / "front.png",
        "side": view_dir / "side.png",
        "back": view_dir / "back.png",
        "top": view_dir / "top.png",
        "bottom": view_dir / "bottom.png",
    }

    front.save(paths["front"])

    prompts = {
        "side": (
            "Generate the exact same character or object as a clean orthographic RIGHT SIDE view. "
            "Keep the same proportions, same design, same colors, same armor/clothing details, centered, full body, plain dark or transparent background."
        ),
        "back": (
            "Generate the exact same character or object as a clean orthographic BACK view. "
            "Keep the same proportions, same design language, same colors, centered, full body, plain dark or transparent background."
        ),
        "top": (
            "Generate the exact same character or object as a clean TOP DOWN orthographic view. "
            "Keep the same design, centered, plain dark or transparent background."
        ),
        "bottom": (
            "Generate the exact same character or object as a clean BOTTOM UP orthographic view. "
            "Keep the same design, centered, plain dark or transparent background."
        ),
    }

    generated = {}
    errors = {}

    for view_name, prompt in prompts.items():
        try:
            view_img = _generate_ai_view(str(paths["front"]), view_name, prompt)
            view_img = _fit_on_canvas(view_img, (1024, 1024))
            view_img.save(paths[view_name])
            generated[view_name] = True
        except Exception as e:
            errors[view_name] = str(e)
            generated[view_name] = False

    if errors:
        return {
            "ok": False,
            "mode": "multiview_ai_generation_failed",
            "error": "One or more AI multiview generations failed.",
            "errors": errors,
            "view_dir": str(view_dir),
            "views": {
                name: {
                    "path": str(path),
                    "url": f"/uploads/{job_dir.name}/multiview/{name}.png",
                    "generated": generated.get(name, name == "front"),
                    "exists": path.exists(),
                }
                for name, path in paths.items()
            },
            "source": str(image_path),
            "canvas_size": [1024, 1024],
        }

    return {
        "ok": True,
        "mode": "multiview_worker_ai_5view",
        "asset_type": detect.get("asset_type") or detect.get("type") or "unknown",
        "view_dir": str(view_dir),
        "views": {
            name: {
                "path": str(path),
                "url": f"/uploads/{job_dir.name}/multiview/{name}.png",
                "generated": True,
                "exists": path.exists(),
            }
            for name, path in paths.items()
        },
        "source": str(image_path),
        "canvas_size": [1024, 1024],
        "note": "Worker AI-generated multiview: front original, side, back, top, bottom.",
    }