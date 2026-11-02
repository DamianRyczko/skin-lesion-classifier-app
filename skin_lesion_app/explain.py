import numpy as np
from PIL import Image

from .models import OnnxModel, Step
from .views import render_view, to_input

# The ONNX files hold no gradients, so Grad-CAM is not possible here. Occlusion works on any model: cover one
# part of the image at a time and see how far the class score falls. Costs GRID x GRID model runs.
GRID = 7


def _log_odds(model: OnnxModel, images: list[np.ndarray], class_index: int) -> np.ndarray:
    """Taken from the logits: a confident softmax rounds to 1.0, and covering part of the image would change nothing.
    One image at a time: a batch takes that many times the memory at the models' 448 px."""
    batch = to_input(images, model.spec["mean"], model.spec["std"])
    z = np.concatenate([model.logits(batch[i : i + 1]) for i in range(len(batch))]).astype(np.float64)
    return z[:, class_index] - np.logaddexp.reduce(np.delete(z, class_index, axis=1), axis=1)


def occlusion_map(model: OnnxModel, img: Image.Image, class_index: int, on_step: Step | None = None) -> np.ndarray:
    """Drop of the class's log-odds when each cell is covered: array (GRID, GRID), 0 where covering didn't hurt.
    on_step is called once per grid row."""
    size = model.spec["img_size"]
    plain = render_view(img, {}, size)
    filler = plain.mean(axis=(0, 1))
    base = _log_odds(model, [plain], class_index)[0]
    cell = size / GRID
    half = round(cell)  # the patch is two cells wide, so neighbouring rows overlap and the map stays smooth
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
