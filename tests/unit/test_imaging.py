import io

import pytest
from PIL import Image

from core.imaging import ImageError, apply_crop, default_box, image_id, load_image, preview_uri


def encoded(image, fmt="JPEG", **kwargs):
    buffer = io.BytesIO()
    image.save(buffer, fmt, **kwargs)
    return buffer.getvalue()


def test_decodes_to_rgb():
    assert load_image(encoded(Image.new("RGBA", (10, 20)), "PNG")).mode == "RGB"


def test_applies_exif_rotation():
    exif = Image.Exif()
    exif[0x0112] = 6  # phone held upright: rotate 90 degrees
    assert load_image(encoded(Image.new("RGB", (40, 20)), exif=exif)).size == (20, 40)


def test_rejects_non_images():
    with pytest.raises(ImageError):
        load_image(b"this is not a picture")


def test_default_box_is_centred_and_square_in_pixels():
    image = Image.new("RGB", (400, 200))
    box = default_box(image)
    assert box["w"] * 400 == pytest.approx(box["h"] * 200)
    assert box["x"] + box["w"] / 2 == pytest.approx(0.5)
    assert apply_crop(image, box).size == (160, 160)


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
    assert width == height
    assert width <= 200


def test_image_id_tracks_content():
    first, second = Image.new("RGB", (8, 8), "red"), Image.new("RGB", (8, 8), "blue")
    assert image_id(first) == image_id(first.copy())
    assert image_id(first) != image_id(second)


def test_preview_is_a_limited_data_uri():
    uri = preview_uri(Image.new("RGB", (3000, 1000)), side=100)
    assert uri.startswith("data:image/jpeg;base64,")
    assert len(uri) < 5000
