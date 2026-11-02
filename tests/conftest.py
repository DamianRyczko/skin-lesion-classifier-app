import os

import pytest
from PIL import Image, ImageDraw

os.environ["SKIN_APP_PACKAGE"] = "/nonexistent"  # the tests never touch real weights in weights/
os.environ.setdefault("SKIN_APP_MOCK_LOAD", "0")
os.environ.setdefault("SKIN_APP_MOCK_VIEW", "0")


@pytest.fixture
def lesion_image() -> Image.Image:
    """Skin-coloured square with a dark blob, off-centre so that rotations are visible."""
    image = Image.new("RGB", (240, 240), (224, 176, 146))
    ImageDraw.Draw(image).ellipse((70, 60, 170, 150), fill=(60, 30, 25))
    return image
