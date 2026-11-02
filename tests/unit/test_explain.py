import numpy as np
import pytest
from PIL import Image

from skin_lesion_app import GRID
from skin_lesion_app.explain import occlusion_map
from skin_lesion_app.models import OnnxModel


class LovesDark(OnnxModel):
    """Class 0 scores by how much of the image is dark: covering dark pixels lowers it."""

    def __init__(self, confidence: float = 8.0):
        super().__init__("dark", {"onnx": "", "img_size": 70, "mean": [0, 0, 0], "std": [1, 1, 1]}, ".")
        self.confidence = confidence

    def logits(self, batch):
        dark = (batch.mean(axis=1) < 0.4).mean(axis=(1, 2))
        row = np.zeros((len(batch), 7))
        row[:, 0] = dark * 50 * self.confidence
        return row


def test_map_finds_the_lesion(lesion_image):
    heat = occlusion_map(LovesDark(), lesion_image, 0)
    row, col = np.unravel_index(np.argmax(heat), heat.shape)
    assert heat.shape == (GRID, GRID)
    assert 2 <= col <= 4 and 1 <= row <= 4  # the blob sits at about (120, 105) of 240
    assert heat[0, 0] == pytest.approx(0)
    assert heat[-1, -1] == pytest.approx(0)


def test_confident_model_still_gives_a_map(lesion_image):
    """In plain softmax the score stays 1.0 whatever is covered, and the map would be blank."""
    assert occlusion_map(LovesDark(confidence=100), lesion_image, 0).max() > 0


def test_unrelated_class_gives_a_map_of_its_own(lesion_image):
    assert not np.array_equal(occlusion_map(LovesDark(), lesion_image, 0), occlusion_map(LovesDark(), lesion_image, 1))


def test_nothing_to_cover_gives_an_empty_map():
    assert occlusion_map(LovesDark(), Image.new("RGB", (240, 240), (224, 176, 146)), 0).max() == 0
