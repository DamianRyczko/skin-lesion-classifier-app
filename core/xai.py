"""Draws an attention heatmap over the photo, in blocky steps that suit the pixel style."""

import numpy as np
from PIL import Image

from ui.tokens import XAI_SCALE as SCALE

_GRID = 64
_FLOOR = 0.12  # weaker attention stays transparent


def _scale_rgb() -> np.ndarray:
    return np.array([[int(c[i : i + 2], 16) for i in (1, 3, 5)] for c in SCALE], dtype=np.uint8)


def overlay(image: Image.Image, heatmap: np.ndarray, opacity: float) -> Image.Image:
    """Blend the heatmap over the image. opacity in 0..1 scales the whole layer."""
    resized = Image.fromarray((np.clip(heatmap, 0, 1) * 255).astype(np.uint8)).resize((_GRID, _GRID), Image.Resampling.BILINEAR)
    heat = np.asarray(resized, dtype=np.float32) / 255
    peak = float(heat.max())
    if peak > 0:
        heat = heat / peak
    steps = np.clip((heat * len(SCALE)).astype(int), 0, len(SCALE) - 1)
    alpha = np.clip((heat - _FLOOR) * 1.5, 0, 0.95) * opacity
    rgba = np.dstack([_scale_rgb()[steps], (alpha * 255).astype(np.uint8)])
    layer = Image.fromarray(rgba, "RGBA").resize(image.size, Image.Resampling.NEAREST)
    return Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB")
