"""The package on real ONNX files, the tiny networks from tests/tiny_package.py."""

import json

import numpy as np
import pytest

from skin_lesion_app import CLASS_CODES, GRID, LEVELS, SkinLesionPredictor, load_config
from skin_lesion_app.cli import main
from skin_lesion_app.models import percentages, softmax
from skin_lesion_app.views import load_image, view_batch
from tests.tiny_package import VIEWS, write_notebook_package, write_package


@pytest.fixture(scope="module")
def package(tmp_path_factory):
    return write_package(tmp_path_factory.mktemp("weights") / "skin_lesions_app")


@pytest.fixture(scope="module")
def predictor(package):
    return SkinLesionPredictor(package)


def test_models_load_on_first_use_only(package, lesion_image):
    fresh = SkinLesionPredictor(package)
    assert not any(model.loaded for model in fresh.models.values())
    fresh.predict(lesion_image, "swin", "fast")
    assert [key for key, model in fresh.models.items() if model.loaded] == ["swin_base"]


def test_switching_options_keeps_one_in_memory(package, lesion_image):
    fresh = SkinLesionPredictor(package)
    fresh.predict(lesion_image, "ensemble", "fast")
    fresh.predict(lesion_image, "my_resnet", "fast")
    assert [key for key, model in fresh.models.items() if model.loaded] == ["custom_resnet"]
    fresh.explain(lesion_image, "mel", "swin")
    assert [key for key, model in fresh.models.items() if model.loaded] == ["swin_base"]


@pytest.mark.parametrize("option", ["my_resnet", "swin", "dinov2", "seresnext", "ensemble"])
@pytest.mark.parametrize("level", list(LEVELS))
def test_every_option_and_level_predicts(predictor, lesion_image, option, level):
    result = predictor.predict(lesion_image, option, level)
    shares = list(result["percentages"].values())
    assert set(result["percentages"]) == set(CLASS_CODES)
    assert sum(shares) == pytest.approx(100)
    assert shares == sorted(shares, reverse=True)
    assert result["prediction"]["code"] == next(iter(result["percentages"]))
    assert result["views_per_model"] == LEVELS[level]


def test_one_view_at_a_time_equals_one_batch(predictor, lesion_image):
    model = predictor.models["swin_base"]
    image = load_image(lesion_image)
    together = model.logits(view_batch(image, VIEWS[:4], 64, model.spec["mean"], model.spec["std"]))
    assert model.view_probabilities(image, 4) == pytest.approx(softmax(together, axis=1), abs=1e-6)


def test_ensemble_averages_its_members(predictor, lesion_image):
    members = [predictor.probabilities(lesion_image, option, "balanced") for option in ("swin", "dinov2", "seresnext")]
    assert predictor.probabilities(lesion_image, "ensemble", "balanced") == pytest.approx(np.mean(members, axis=0))


def test_level_decides_how_many_views_are_used(predictor, lesion_image):
    assert not np.allclose(
        predictor.probabilities(lesion_image, "swin", "fast"),
        predictor.probabilities(lesion_image, "swin", "best"),
    )


def test_defaults_come_from_the_package(predictor, lesion_image):
    result = predictor.predict(lesion_image)
    assert (result["option"], result["level"]) == ("swin", "balanced")


@pytest.mark.parametrize(("option", "level"), [("nope", "fast"), ("swin", "nope")])
def test_unknown_choice_names_the_valid_ones(predictor, lesion_image, option, level):
    with pytest.raises(ValueError, match="choose from"):
        predictor.predict(lesion_image, option, level)


def test_melanoma_warning_compares_the_score_to_the_threshold(tmp_path, lesion_image):
    always = SkinLesionPredictor(write_package(tmp_path / "low", mel_threshold=0.0))
    never = SkinLesionPredictor(write_package(tmp_path / "high", mel_threshold=1.1))
    assert always.predict(lesion_image, "swin", "fast")["melanoma_warning"]["flag"] is True
    assert never.predict(lesion_image, "swin", "fast")["melanoma_warning"]["flag"] is False


def test_percentages_add_up_exactly():
    shares = np.array([1, 1, 1, 1, 1, 1, 1]) / 7
    assert percentages(shares).sum() == pytest.approx(100)


@pytest.mark.parametrize("option", ["swin", "ensemble"])
def test_explain_reports_one_step_per_grid_row_of_every_model(predictor, lesion_image, option):
    seen = []
    heat = predictor.explain(lesion_image, "mel", option, on_step=lambda done, total: seen.append((done, total)))
    total = GRID * len(predictor.config["options"][-1]["members"] if option == "ensemble" else ["swin_base"])
    assert seen == [(i, total) for i in range(1, total + 1)]
    assert heat.shape == (GRID, GRID)
    assert 0 <= heat.min() and heat.max() <= 1


def test_config_with_another_class_order_is_refused(package, tmp_path):
    config = json.loads((package / "app_config.json").read_text())
    config["classes"] = list(reversed(config["classes"]))
    (tmp_path / "app_config.json").write_text(json.dumps(config))
    with pytest.raises(ValueError, match="class order"):
        load_config(tmp_path)


def test_command_line_reads_the_package(package, tmp_path, capsys, lesion_image):
    photo = tmp_path / "lesion.png"
    lesion_image.save(photo)
    main(["options", "--package", str(package)])
    assert "Swin-Base" in capsys.readouterr().out
    main(["predict", str(photo), "--package", str(package), "--option", "dinov2", "--level", "fast"])
    assert json.loads(capsys.readouterr().out)["option"] == "dinov2"


# ---------------------------------------------------------------- the notebook's app_package.json
@pytest.fixture(scope="module")
def notebook(tmp_path_factory):
    return write_notebook_package(tmp_path_factory.mktemp("weights") / "skin_lesions_app")


def test_notebook_export_offers_the_models_in_the_folder(notebook):
    predictor = SkinLesionPredictor(notebook)
    assert [o["id"] for o in predictor.options()] == ["my_resnet", "swin", "dinov2", "seresnext", "ensemble"]
    assert predictor.default_option == "swin"
    assert predictor.config["models"]["swin_base"]["label"] == "SWIN_BASE"


def test_ensemble_needs_all_three_of_its_models(tmp_path):
    tags = ("custom_resnet", "swin_base", "dinov2_vitb")
    predictor = SkinLesionPredictor(write_notebook_package(tmp_path / "package", tags))
    assert [o["id"] for o in predictor.options()] == ["my_resnet", "swin", "dinov2"]


def test_notebook_export_has_only_the_levels_it_was_tuned_for(notebook, lesion_image):
    predictor = SkinLesionPredictor(notebook)
    assert predictor.levels == ["fast", "best"]
    assert predictor.predict(lesion_image, "swin", "best")["views_per_model"] == 12
    with pytest.raises(ValueError, match="balanced"):
        predictor.predict(lesion_image, "swin", "balanced")


def test_levels_use_their_own_bias(notebook):
    settings = SkinLesionPredictor(notebook)._options["swin"]["levels"]
    assert settings["best"]["decision_bias"] == [2.0] * 6 + [0.0]
    assert settings["fast"]["decision_bias"] == [0.0] * 6 + [2.0]


def test_notebook_export_has_no_melanoma_warning(notebook, lesion_image):
    assert SkinLesionPredictor(notebook).predict(lesion_image, "swin", "fast")["melanoma_warning"] is None


def test_built_config_wins_over_the_notebook_export(tmp_path, notebook):
    package = write_package(tmp_path / "package")
    (package / "app_package.json").write_bytes((notebook / "app_package.json").read_bytes())
    assert "balanced" in SkinLesionPredictor(package).levels


def test_notebook_export_with_another_class_order_is_refused(tmp_path):
    package = write_notebook_package(tmp_path / "package")
    export = json.loads((package / "app_package.json").read_text())
    export["classes"].reverse()
    (package / "app_package.json").write_text(json.dumps(export))
    with pytest.raises(ValueError, match="class order"):
        load_config(package)


def test_options_command_prints_the_notebook_export(notebook, capsys):
    main(["options", "--package", str(notebook)])
    assert "best 0.700" in capsys.readouterr().out
