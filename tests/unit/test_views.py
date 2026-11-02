import io
from typing import Any

import numpy as np
import pytest
from PIL import Image

from skin_lesion_app.views import TRAIN_LONG_SIDE, load_image, render_view, view_batch


@pytest.mark.parametrize(
    ("size", "expected"),
    [
        ((240, 240), (600, 600)),  # the app's square crop
        ((1200, 900), (600, 450)),  # HAM10000 shape
        ((1000, 500), (600, 450)),  # wider than 4:3: centre crop
        ((500, 1000), (450, 600)),  # taller than 3:4
    ],
)
def test_load_image_brings_uploads_to_training_scale(size, expected):
    assert load_image(Image.new("RGB", size)).size == expected


def test_load_image_takes_every_source(lesion_image):
    buffer = io.BytesIO()
    lesion_image.save(buffer, "PNG")
    sources = [lesion_image, np.asarray(lesion_image), buffer.getvalue(), io.BytesIO(buffer.getvalue())]
    assert {load_image(source).size for source in sources} == {(TRAIN_LONG_SIDE, TRAIN_LONG_SIDE)}


def test_load_image_applies_exif_rotation():
    exif = Image.Exif()
    exif[0x0112] = 6  # rotated 90 degrees
    buffer = io.BytesIO()
    Image.new("RGB", (400, 300)).save(buffer, "JPEG", exif=exif)
    width, height = load_image(buffer.getvalue()).size
    assert height > width


def test_plain_view_is_the_scaled_image_in_0_1(lesion_image):
    view = render_view(lesion_image, {}, 64)
    assert view.shape == (64, 64, 3)
    assert view.dtype == np.float32
    assert 0 <= view.min() and view.max() <= 1


@pytest.mark.parametrize(
    "view",
    [
        {"flip": True},
        {"k90": 1},
        {"angle": 30},
        {"crop": [0.1, 0.1, 0.9, 0.9]},
        {"zoom_out": 0.8},
        {"brightness": 1.2},
        {"contrast": 0.8},
        {"saturation": 1.2},
    ],
)
def test_each_view_changes_the_image_and_keeps_the_size(lesion_image, view):
    plain = render_view(lesion_image, {}, 64)
    changed = render_view(lesion_image, view, 64)
    assert changed.shape == plain.shape
    assert not np.array_equal(changed, plain)
    assert 0 <= changed.min() and changed.max() <= 1


def test_batch_is_normalised_nchw(lesion_image):
    views: list[dict[str, Any]] = [{}, {"flip": True}, {"k90": 1}]
    batch = view_batch(lesion_image, views, 64, [0.5, 0.5, 0.5], [0.25, 0.25, 0.25])
    assert batch.shape == (3, 3, 64, 64)
    assert batch.dtype == np.float32
    expected = (render_view(lesion_image, {}, 64) - 0.5) / 0.25
    assert batch[0].transpose(1, 2, 0) == pytest.approx(expected)
