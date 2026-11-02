"""Decoding, orientation and cropping of uploaded photos. Everything stays in memory."""

import base64
import hashlib
import io

from PIL import Image, ImageOps, UnidentifiedImageError

ALLOWED_TYPES = ("jpg", "jpeg", "png", "webp")
PREVIEW_SIDE = 1024


class ImageError(ValueError):
    """The upload is not a usable image. The message is shown to the user."""


def load_image(data: bytes) -> Image.Image:
    """Decode to RGB with the phone's EXIF rotation applied."""
    try:
        return ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError) as exc:
        raise ImageError("Nie udało się odczytać tego pliku jako zdjęcia.") from exc


def image_id(image: Image.Image) -> str:
    """Short content hash: logs and cache keys."""
    digest = hashlib.sha256()
    digest.update(f"{image.size}".encode())
    digest.update(image.tobytes())
    return digest.hexdigest()[:12]


def default_box(image: Image.Image) -> dict[str, float]:
    """Centred square covering 80% of the shorter side, as fractions of width and height."""
    width, height = image.size
    side = 0.8 * min(width, height)
    w, h = side / width, side / height
    return {"x": (1 - w) / 2, "y": (1 - h) / 2, "w": w, "h": h}


def apply_crop(image: Image.Image, box: dict[str, float]) -> Image.Image:
    """Crop by a fractional box. The result is forced square: the model input is."""
    width, height = image.size
    left, top = box["x"] * width, box["y"] * height
    side = max(1, round(min(box["w"] * width, box["h"] * height)))
    left = min(max(0, round(left)), width - side)
    top = min(max(0, round(top)), height - side)
    return image.crop((left, top, left + side, top + side))


def preview_uri(image: Image.Image, side: int = PREVIEW_SIDE) -> str:
    """Downscaled JPEG data URI for the browser cropper."""
    preview = image.copy()
    preview.thumbnail((side, side))
    buffer = io.BytesIO()
    preview.save(buffer, "JPEG", quality=85)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()
