import os
import tempfile
from pathlib import Path

import pytest
from PIL import Image

os.environ["SKIN_APP_PACKAGE"] = str(Path(tempfile.mkdtemp(prefix="skin_app_")) / "skin_lesions_app")

from tests.tiny_package import draw_lesion, write_package  # noqa: E402

write_package(Path(os.environ["SKIN_APP_PACKAGE"]))


@pytest.fixture
def lesion_image() -> Image.Image:
    return draw_lesion()
