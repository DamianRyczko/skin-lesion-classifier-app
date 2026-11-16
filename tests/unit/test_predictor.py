import json

import numpy as np
import pytest

from skin_lesion_app.config import CLASS_CODES, LEVELS, PACKAGE_DIR, load_config
from skin_lesion_app.models import OnnxModel
from skin_lesion_app.predictor import SkinLesionPredictor
from tests.tiny_package import write_package


class Fixed(OnnxModel):
    """Always the same answer."""

    def __init__(self, spec, **probs):
        super().__init__(spec, PACKAGE_DIR)
        self.row = np.log([probs[code] for code in CLASS_CODES])
        self._session = self

    def logits(self, batch):
        return np.tile(self.row, (len(batch), 1))


@pytest.mark.parametrize("option", ["my_resnet", "swin", "dinov2", "seresnext", "ensemble"])
@pytest.mark.parametrize("level", list(LEVELS))
def test_every_option_gives_percentages_that_add_up_to_100(lesion_image, option, level):
    shares = SkinLesionPredictor(PACKAGE_DIR).predict(lesion_image, option, level)
    assert list(shares) == sorted(shares, key=shares.__getitem__, reverse=True)
    assert set(shares) == set(CLASS_CODES)
    assert sum(shares.values()) == pytest.approx(100)


def test_ensemble_applies_each_models_own_bias_then_averages(lesion_image):
    predictor = SkinLesionPredictor(PACKAGE_DIR)
    answer = {code: 0.01 for code in CLASS_CODES} | {"nv": 0.94}
    for tag in ("swin_base", "dinov2_vitb", "seresnext101"):
        predictor.models[tag] = Fixed(predictor.config["models"][tag], **answer)
    to_mel = [0, 0, 0, 0, 10.0, 0, 0]
    no_bias = [0.0] * 7
    predictor.options["ensemble"]["bias"]["fast"] = [to_mel, no_bias, no_bias]
    shares = predictor.predict(lesion_image, "ensemble", "fast")
    assert shares["mel"] == pytest.approx(33.9, abs=0.5)
    assert next(iter(shares)) == "nv"


def test_switching_options_keeps_one_in_memory(lesion_image):
    predictor = SkinLesionPredictor(PACKAGE_DIR)
    predictor.predict(lesion_image, "ensemble", "fast")
    predictor.predict(lesion_image, "my_resnet", "fast")
    assert [key for key, model in predictor.models.items() if model.loaded] == ["custom_resnet"]


def test_ensemble_is_offered_only_with_all_three_models(tmp_path):
    package = write_package(tmp_path / "package", ("custom_resnet", "swin_base", "dinov2_vitb"))
    assert list(SkinLesionPredictor(package).options) == ["my_resnet", "swin", "dinov2"]


def test_another_class_order_is_refused(tmp_path):
    package = write_package(tmp_path / "package")
    export = json.loads((package / "app_package.json").read_text())
    export["classes"].reverse()
    (package / "app_package.json").write_text(json.dumps(export))
    with pytest.raises(ValueError, match="class order"):
        load_config(package)
