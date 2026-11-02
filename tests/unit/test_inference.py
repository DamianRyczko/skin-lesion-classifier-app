import numpy as np
import pytest

import core.inference
from core.imaging import image_id
from core.inference import analyze, explain
from model import MODELS, MockModel, MockPredictor
from skin_lesion_app import CLASS_CODES


class Fixed(MockModel):
    """Always the same answer."""

    def __init__(self, key, spec, probs):
        super().__init__(key, spec)
        self.row = np.log([probs[code] for code in CLASS_CODES])

    def logits(self, batch):
        return np.tile(self.row, (len(batch), 1))


@pytest.fixture
def answer(monkeypatch):
    """Makes the Swin option answer with the given probabilities, decision bias and melanoma threshold."""

    def set_answer(threshold=0.5, bias=None, **probs):
        predictor = MockPredictor()
        predictor.models["swin_base"] = Fixed("swin_base", predictor.config["models"]["swin_base"], probs)
        settings = predictor._options["swin"]["levels"]["fast"]
        settings = {**settings, "melanoma_thresholds": {"0.90": threshold}, "decision_bias": bias or settings["decision_bias"]}
        levels = {**predictor._options["swin"]["levels"], "fast": settings}
        predictor._options["swin"] = {**predictor._options["swin"], "levels": levels}
        monkeypatch.setattr(core.inference, "PREDICTOR", predictor)

    return set_answer


def run(lesion_image):
    return analyze(MODELS["swin"], lesion_image, "abcdef123456", "fast")


def test_probabilities_sum_to_one_and_are_sorted(lesion_image):
    prediction = analyze(MODELS["swin"], lesion_image, image_id(lesion_image), "balanced")
    values = list(prediction.probs.values())
    assert sum(values) == pytest.approx(1)
    assert values == sorted(values, reverse=True)
    assert prediction.top == next(iter(prediction.probs))


def test_same_photo_same_result(lesion_image):
    key = image_id(lesion_image)
    assert analyze(MODELS["swin"], lesion_image, key, "best").probs == analyze(MODELS["swin"], lesion_image, key, "best").probs


@pytest.mark.parametrize(
    ("model_id", "level", "total"), [("swin", "fast", 1), ("swin", "best", 12), ("ensemble", "balanced", 12)]
)
def test_reports_progress_for_every_view_of_every_model(lesion_image, model_id, level, total):
    seen = []
    prediction = analyze(MODELS[model_id], lesion_image, "abcdef123456", level, lambda done, of: seen.append((done, of)))
    assert seen == [(i, total) for i in range(1, total + 1)]
    assert prediction.n_views == total // len(MODELS[model_id].members)


def test_low_risk_is_watch(lesion_image, answer):
    answer(mel=0.05, bcc=0.05, akiec=0.05, bkl=0.05, df=0.05, nv=0.70, vasc=0.05)
    prediction = run(lesion_image)
    assert prediction.top == "nv"
    assert prediction.risk == pytest.approx(0.15)
    assert prediction.consult is False


def test_risk_rule_fires_with_a_benign_class_on_top(lesion_image, answer):
    answer(mel=0.10, bcc=0.10, akiec=0.05, bkl=0.05, df=0.05, nv=0.60, vasc=0.05)
    prediction = run(lesion_image)
    assert (prediction.top, prediction.melanoma, prediction.consult) == ("nv", False, True)


def test_melanoma_threshold_fires_below_the_risk_rule(lesion_image, answer):
    answer(threshold=0.08, mel=0.10, bcc=0.02, akiec=0.02, bkl=0.05, df=0.05, nv=0.71, vasc=0.05)
    prediction = run(lesion_image)
    assert prediction.risk < 0.25
    assert (prediction.melanoma, prediction.consult) == (True, True)


def test_bars_include_the_decision_bias_but_the_melanoma_score_does_not(lesion_image, answer):
    bias = [0, 0, 0, 0, 2.0, -1.0, 0]  # class order: mel up, nv down
    answer(threshold=0.2, bias=bias, mel=0.10, bcc=0.02, akiec=0.02, bkl=0.05, df=0.05, nv=0.71, vasc=0.05)
    prediction = run(lesion_image)
    assert prediction.top == "mel"
    assert prediction.probs["mel"] > 0.5
    assert prediction.melanoma is False  # 0.10 before the bias, under the threshold


def test_package_without_melanoma_thresholds_uses_the_risk_rule_alone(lesion_image, answer, monkeypatch):
    answer(mel=0.10, bcc=0.10, akiec=0.05, bkl=0.05, df=0.05, nv=0.60, vasc=0.05)
    monkeypatch.delitem(core.inference.PREDICTOR.config, "melanoma_warning")
    prediction = run(lesion_image)
    assert (prediction.melanoma, prediction.consult) == (False, True)


def test_explain_is_a_map_in_range(lesion_image):
    heat = explain(MODELS["swin"], lesion_image, "mel")
    assert heat.ndim == 2
    assert 0 <= heat.min() and heat.max() <= 1
