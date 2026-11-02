import numpy as np
import pytest

from skin_lesion_app.build import _apply_bias, _auc, _macro_f1, _threshold_for_sensitivity, _tune_bias, _warning_stats


def test_macro_f1_perfect_and_missing_class():
    y = np.array([0, 1, 2, 3, 4, 5, 6])
    assert _macro_f1(y, y) == pytest.approx(1)
    assert _macro_f1(y, np.array([0, 1, 2, 3, 4, 5, 0])) < 1


def test_auc_counts_ties_as_half():
    assert _auc(np.array([0.1, 0.2, 0.8, 0.9]), np.array([0, 0, 1, 1])) == pytest.approx(1)
    assert _auc(np.array([0.5, 0.5]), np.array([0, 1])) == pytest.approx(0.5)


def test_threshold_catches_the_target_share_of_positives():
    scores = np.arange(100) / 100
    threshold = _threshold_for_sensitivity(scores, np.ones(100, dtype=bool), 0.90)
    assert (scores >= threshold).mean() >= 0.90


def test_warning_stats():
    stats = _warning_stats(np.array([0.9, 0.6, 0.2, 0.1]), np.array([1, 0, 1, 0]), 0.5)
    assert stats == {"sensitivity": 0.5, "specificity": 0.5, "ppv": 0.5, "alerts_per_100": 50.0}


def test_bias_rescues_a_class_the_raw_argmax_never_picks():
    probs = np.array([[0.6, 0.4] + [0.0] * 5] * 3 + [[0.7, 0.3] + [0.0] * 5] * 3)
    y = np.array([1, 1, 1, 0, 0, 0])
    bias = _tune_bias(probs, y)
    assert _macro_f1(y, _apply_bias(probs, bias)) > _macro_f1(y, probs.argmax(1))
