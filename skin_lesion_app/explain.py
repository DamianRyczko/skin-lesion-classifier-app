import numpy as np
from PIL import Image

from .models import OnnxModel, Step
from .views import render_view, to_input

GRID = 7


def _log_odds(model: OnnxModel, images: list[np.ndarray], class_index: int) -> np.ndarray:
    batch = to_input(images, model.spec["mean"], model.spec["std"])
    z = np.concatenate([model.logits(batch[i : i + 1]) for i in range(len(batch))]).astype(np.float64)
    return z[:, class_index] - np.logaddexp.reduce(np.delete(z, class_index, axis=1), axis=1)


def occlusion_map(model: OnnxModel, img: Image.Image, class_index: int, on_step: Step | None = None) -> np.ndarray:
    """Drop of the class's log-odds per covered cell, (GRID, GRID). on_step runs once per row."""
    size = model.spec["img_size"]
    plain = render_view(img, {}, size)
    filler = plain.mean(axis=(0, 1))
    base = _log_odds(model, [plain], class_index)[0]
    cell = size / GRID
    half = round(cell)
    heat = np.zeros((GRID, GRID))
    for row in range(GRID):
        covered = []
        for col in range(GRID):
            x, y = round((col + 0.5) * cell), round((row + 0.5) * cell)
            image = plain.copy()
            image[max(y - half, 0) : y + half, max(x - half, 0) : x + half] = filler
            covered.append(image)
        heat[row] = base - _log_odds(model, covered, class_index)
        if on_step:
            on_step()
    return np.clip(heat, 0.0, None)
