import io

import pytest
from PIL import Image

from core.imaging import ImageError, apply_crop, load_image


def test_phone_photo_is_turned_upright():
    exif = Image.Exif()
    exif[0x0112] = 6  # phone held upright: rotate 90 degrees
    buffer = io.BytesIO()
    Image.new("RGB", (40, 20)).save(buffer, "JPEG", exif=exif)
    assert load_image(buffer.getvalue()).size == (20, 40)


def test_non_image_gives_a_message_for_the_user():
    with pytest.raises(ImageError, match="Nie udało się"):
        load_image(b"this is not a picture")


@pytest.mark.parametrize(
    "box",
    [
        {"x": 0.9, "y": 0.9, "w": 0.5, "h": 0.5},  # past the edge
        {"x": -0.2, "y": 0.0, "w": 0.5, "h": 0.5},
        {"x": 0.25, "y": 0.1, "w": 0.5, "h": 0.8},  # not square
    ],
)
def test_crop_stays_square_and_inside(box):
    width, height = apply_crop(Image.new("RGB", (300, 200)), box).size
    assert width == height <= 200
