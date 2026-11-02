import pytest

from core.classes import CLASSES, HIGH_RISK, RISK_THRESHOLD, needs_consultation, risk_score
from skin_lesion_app import CLASS_CODES


def probs(mel=0.0, bcc=0.0, akiec=0.0, nv=0.0):
    rest = 1 - mel - bcc - akiec - nv
    return {"mel": mel, "bcc": bcc, "akiec": akiec, "nv": nv, "bkl": rest, "df": 0.0, "vasc": 0.0}


def test_all_seven_ham_classes_are_described():
    assert set(CLASSES) == set(CLASS_CODES)
    assert all(lesion.name and lesion.about and lesion.advice for lesion in CLASSES.values())


def test_threshold_and_risk_classes():
    assert RISK_THRESHOLD == 0.25
    assert set(HIGH_RISK) == {"mel", "bcc", "akiec"}


def test_risk_sums_the_high_risk_classes_only():
    assert risk_score(probs(mel=0.1, bcc=0.05, akiec=0.05, nv=0.7)) == pytest.approx(0.2)


@pytest.mark.parametrize(
    ("sample", "expected"),
    [
        (probs(mel=0.25), True),  # exactly on the threshold
        (probs(mel=0.2499), False),
        (probs(mel=0.10, bcc=0.10, akiec=0.10, nv=0.70), True),  # spread out, benign class on top
        (probs(mel=0.05, nv=0.90), False),
    ],
)
def test_consultation_rule(sample, expected):
    assert needs_consultation(sample) is expected
