import numpy as np
from PIL import Image


def _default_fill_for_mode(mode: str):
    if mode == "RGBA":
        return (0, 0, 0, 0)
    if mode == "RGB":
        return (0, 0, 0)
    return 0


def pad_to_square(image: Image.Image, fill=None) -> Image.Image:
    w, h = image.size
    if w == h:
        return image

    size = max(w, h)
    if fill is None:
        fill = _default_fill_for_mode(image.mode)

    new_im = Image.new(image.mode, (size, size), color=fill)
    new_im.paste(image, ((size - w) // 2, (size - h) // 2))
    return new_im


def resize_image(image: Image.Image, size: int, is_mask: bool = False) -> Image.Image:
    resample = Image.NEAREST if is_mask else Image.BILINEAR
    return image.resize((size, size), resample)


def _mask_crop_box(mask: Image.Image, margin: int = 16) -> tuple[int, int, int, int] | None:
    mask_np = np.array(mask)
    coords = np.argwhere(mask_np > 0)
    if coords.size == 0:
        return None

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)

    y0 = max(int(y0) - margin, 0)
    x0 = max(int(x0) - margin, 0)

    # right / bottom are exclusive in PIL crop
    y1 = min(int(y1) + margin + 1, mask.height)
    x1 = min(int(x1) + margin + 1, mask.width)

    return (x0, y0, x1, y1)


def crop_around_mask(image: Image.Image, mask: Image.Image, margin: int = 16) -> Image.Image:
    box = _mask_crop_box(mask, margin=margin)
    if box is None:
        return image
    return image.crop(box)


def crop_image_and_mask(
    image: Image.Image,
    mask: Image.Image,
    margin: int = 16,
) -> tuple[Image.Image, Image.Image]:
    box = _mask_crop_box(mask, margin=margin)
    if box is None:
        return image, mask
    return image.crop(box), mask.crop(box)


def preprocess(
    image: Image.Image,
    mask: Image.Image = None,
    preset: str = None,
    return_mask: bool = False,
    target_size: int = 512,
):
    """
    Preprocess image (and optionally mask) for inference.

    Current flow:
    - crop around mask if provided
    - pad to square
    - resize to target_size

    If return_mask=True, returns:
        (processed_image, processed_mask)

    Otherwise returns:
        processed_image
    """
    if mask is not None:
        image, mask = crop_image_and_mask(image, mask)

    image = pad_to_square(image)
    image = resize_image(image, target_size, is_mask=False)

    if mask is not None:
        mask = pad_to_square(mask, fill=0)
        mask = resize_image(mask, target_size, is_mask=True)

    if return_mask:
        return image, mask

    return image
