import numpy as np
from PIL import Image

def pad_to_square(image: Image.Image, fill=0) -> Image.Image:
    w, h = image.size
    if w == h:
        return image
    size = max(w, h)
    new_im = Image.new("RGBA" if image.mode == "RGBA" else image.mode, (size, size), color=fill)
    new_im.paste(image, ((size - w) // 2, (size - h) // 2))
    return new_im

def resize_image(image: Image.Image, size: int) -> Image.Image:
    return image.resize((size, size), Image.BILINEAR)

def crop_around_mask(image: Image.Image, mask: Image.Image, margin=16) -> Image.Image:
    mask_np = np.array(mask)
    coords = np.argwhere(mask_np > 0)
    if coords.size == 0:
        return image
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)
    y0 = max(y0 - margin, 0)
    x0 = max(x0 - margin, 0)
    y1 = min(y1 + margin, image.height)
    x1 = min(x1 + margin, image.width)
    return image.crop((x0, y0, x1, y1))

def preprocess(image: Image.Image, mask: Image.Image = None, preset: str = None) -> Image.Image:
    # Pad, crop, resize (order can be tuned)
    if mask is not None:
        image = crop_around_mask(image, mask)
    image = pad_to_square(image)
    image = resize_image(image, 512)
    return image
