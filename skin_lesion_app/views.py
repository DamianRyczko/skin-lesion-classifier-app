import io
from pathlib import Path
from typing import Any, BinaryIO

import numpy as np
from PIL import Image, ImageOps

# HAM10000 images are 600 x 450 and every model saw them at that scale; uploads are brought to the same
# scale first, so the crop-based views (zoom in, shifts) cut the same regions as during the TTA search.
TRAIN_LONG_SIDE = 600
MAX_ASPECT = 4 / 3  # training crops covered aspect ratios 3:4 .. 4:3
GRAY = np.array([0.2989, 0.587, 0.114], dtype=np.float32)
BILINEAR = Image.Resampling.BILINEAR

ImageSource = str | Path | bytes | bytearray | BinaryIO | Image.Image | np.ndarray


def load_image(source: ImageSource) -> Image.Image:
    """Path, bytes, file object, PIL image or HxWx3 uint8 array -> RGB PIL image at training scale."""
    if isinstance(source, Image.Image):
        img = source
    elif isinstance(source, np.ndarray):
        img = Image.fromarray(source)
    elif isinstance(source, bytes | bytearray):
        img = Image.open(io.BytesIO(source))
    else:
        img = Image.open(source)
    img = ImageOps.exif_transpose(img)  # phone photos keep their rotation in EXIF
    img = img.convert("RGB")
    w, h = img.size
    if w > h * MAX_ASPECT:  # wider than 4:3 -> centre crop
        nw = round(h * MAX_ASPECT)
        img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    elif h > w * MAX_ASPECT:  # taller than 3:4 -> centre crop
        nh = round(w * MAX_ASPECT)
        img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    w, h = img.size
    scale = TRAIN_LONG_SIDE / max(w, h)
    if abs(scale - 1.0) > 1e-9:
        img = img.resize((max(1, round(w * scale)), max(1, round(h * scale))), BILINEAR)
    return img


def render_view(img: Image.Image, view: dict[str, Any], size: int) -> np.ndarray:
    """One TTA view -> float32 array (size, size, 3) in [0, 1]. Same steps as the GPU version used for the search:
    crop (zoom in / shift) or shrink + mirrored edges (zoom out) -> resize -> rotate -> colour -> 90-degree turns / flip."""
    w, h = img.size
    if view.get("crop"):
        x0, y0, x1, y1 = view["crop"]
        img = img.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
    if view.get("zoom_out"):
        s = round(size * view["zoom_out"])
        pad = (size - s) // 2
        arr = np.asarray(img.resize((s, s), BILINEAR), dtype=np.float32)
        arr = np.pad(arr, ((pad, size - s - pad), (pad, size - s - pad), (0, 0)), mode="reflect")
    else:
        arr = np.asarray(img.resize((size, size), BILINEAR), dtype=np.float32)
    if view.get("angle"):
        rotated = Image.fromarray(arr.astype(np.uint8)).rotate(view["angle"], resample=BILINEAR, fillcolor=(0, 0, 0))
        arr = np.asarray(rotated, dtype=np.float32)
    x = arr / 255.0
    if view.get("brightness"):
        x = np.clip(x * view["brightness"], 0.0, 1.0)
    if view.get("contrast"):
        m = float((x @ GRAY).mean())
        x = np.clip(m + view["contrast"] * (x - m), 0.0, 1.0)
    if view.get("saturation"):
        g = (x @ GRAY)[..., None]
        x = np.clip(g + view["saturation"] * (x - g), 0.0, 1.0)
    if view.get("k90"):
        x = np.rot90(x, view["k90"], axes=(0, 1))
    if view.get("flip"):
        x = x[:, ::-1]
    return x


def to_input(views: list[np.ndarray], mean: list[float], std: list[float]) -> np.ndarray:
    """Rendered HxWx3 views -> float32 NCHW batch, normalised."""
    mean_ = np.asarray(mean, dtype=np.float32)
    std_ = np.asarray(std, dtype=np.float32)
    return np.stack([((x - mean_) / std_).transpose(2, 0, 1) for x in views]).astype(np.float32)


def view_batch(img: Image.Image, views: list[dict[str, Any]], size: int, mean: list[float], std: list[float]) -> np.ndarray:
    """All views of one image for one model -> float32 NCHW batch, normalised."""
    return to_input([render_view(img, v, size) for v in views], mean, std)
