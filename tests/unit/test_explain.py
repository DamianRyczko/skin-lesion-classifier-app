from pathlib import Path

import numpy as np

from skin_lesion_app.explain import GRID, occlusion_map
from skin_lesion_app.models import OnnxModel


class LovesDark(OnnxModel):
    """Class 0 scores by how much of the image is dark, very confidently."""

    def __init__(self):
        super().__init__({"onnx": "", "img_size": 70, "mean": [0, 0, 0], "std": [1, 1, 1]}, Path("."))

    def logits(self, batch):
        row = np.zeros((len(batch), 7))
        row[:, 0] = (batch.mean(axis=1) < 0.4).mean(axis=(1, 2)) * 5000
        return row


def test_map_finds_the_lesion_even_on_a_confident_model(lesion_image):
    # Softmax would be 1.0 whatever is covered, and the map blank: that is why it uses log-odds.
    heat = occlusion_map(LovesDark(), lesion_image, 0)
    row, col = np.unravel_index(np.argmax(heat), heat.shape)
    assert heat.shape == (GRID, GRID)
    assert 2 <= col <= 4 and 1 <= row <= 4  # the blob sits at about (120, 105) of 240
    assert heat[-1, -1] == 0
