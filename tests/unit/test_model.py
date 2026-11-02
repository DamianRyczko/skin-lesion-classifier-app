import json

import numpy as np
import pytest
from PIL import Image, ImageDraw

import model
from model import MODELS, MockPredictor, is_loaded, load_model
from skin_lesion_app import CLASS_CODES
from tests.tiny_package import write_notebook_package, write_package


@pytest.fixture
def mock() -> MockPredictor:
    return MockPredictor()


def test_offers_the_five_options_with_labels_that_fit_a_button():
    assert list(MODELS) == ["my_resnet", "swin", "dinov2", "seresnext", "ensemble"]
    assert MODELS["my_resnet"].label == "ResNet"
    assert MODELS["ensemble"].label == "Ensemble"
    assert MODELS["ensemble"].members == ("swin_base", "dinov2_vitb", "seresnext101")


def test_marked_as_mock_without_a_package():
    assert all(spec.mock for spec in MODELS.values())


def test_view_probabilities(mock, lesion_image):
    probs = mock.models["swin_base"].view_probabilities(lesion_image, 4)
    assert probs.shape == (4, len(CLASS_CODES))
    assert probs.sum(axis=1) == pytest.approx([1, 1, 1, 1])


def test_mock_answers_to_the_image(mock, lesion_image):
    plain = Image.new("RGB", (240, 240), (224, 176, 146))
    assert not np.allclose(mock.probabilities(lesion_image, "swin"), mock.probabilities(plain, "swin"))


def test_models_disagree(mock, lesion_image):
    assert not np.allclose(mock.probabilities(lesion_image, "swin"), mock.probabilities(lesion_image, "dinov2"))


def test_dark_uneven_lesion_leans_to_melanoma(mock):
    image = Image.new("RGB", (240, 240), (224, 176, 146))
    ImageDraw.Draw(image).ellipse((40, 40, 200, 180), fill=(25, 15, 20))
    assert mock.predict(image, "swin", "fast")["prediction"]["code"] == "mel"


def test_loads_once_and_reports_it(monkeypatch, mock):
    monkeypatch.setattr(model, "PREDICTOR", mock)
    assert not is_loaded("ensemble")
    load_model("swin")
    assert not is_loaded("ensemble")  # one of its three members only
    session = mock.models["swin_base"].load()
    load_model("ensemble")
    assert is_loaded("ensemble")
    assert mock.models["swin_base"].load() is session


def test_empty_folder_means_mock(monkeypatch, tmp_path):
    monkeypatch.setattr(model, "DEFAULT_PACKAGE", tmp_path)
    assert isinstance(model._open_predictor(), MockPredictor)


def test_package_replaces_the_mock(monkeypatch, tmp_path):
    monkeypatch.setattr(model, "DEFAULT_PACKAGE", write_package(tmp_path / "package"))
    assert not isinstance(model._open_predictor(), MockPredictor)


def test_notebook_export_replaces_the_mock(monkeypatch, tmp_path):
    monkeypatch.setattr(model, "DEFAULT_PACKAGE", write_notebook_package(tmp_path / "package"))
    assert not isinstance(model._open_predictor(), MockPredictor)


def test_notebook_export_without_models_does_not_fall_back_to_the_mock(monkeypatch, tmp_path):
    monkeypatch.setattr(model, "DEFAULT_PACKAGE", write_notebook_package(tmp_path / "package", ()))
    with pytest.raises(FileNotFoundError, match="no model"):
        model._open_predictor()


def test_broken_package_does_not_fall_back_to_the_mock(monkeypatch, tmp_path):
    package = write_package(tmp_path / "package")
    (package / "onnx" / "swin_base.onnx").unlink()
    monkeypatch.setattr(model, "DEFAULT_PACKAGE", package)
    with pytest.raises(FileNotFoundError, match="swin_base"):
        model._open_predictor()


def test_wrong_format_does_not_fall_back_to_the_mock(monkeypatch, tmp_path):
    package = write_package(tmp_path / "package")
    config = json.loads((package / "app_config.json").read_text())
    (package / "app_config.json").write_text(json.dumps({**config, "format": "something-else"}))
    monkeypatch.setattr(model, "DEFAULT_PACKAGE", package)
    with pytest.raises(ValueError, match="format"):
        model._open_predictor()
