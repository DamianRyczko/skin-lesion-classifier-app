import pytest

from core.classes import needs_consultation


def probs(mel=0.0, bcc=0.0, akiec=0.0, nv=0.0):
    rest = 1 - mel - bcc - akiec - nv
    return {"mel": mel, "bcc": bcc, "akiec": akiec, "nv": nv, "bkl": rest, "df": 0.0, "vasc": 0.0}


@pytest.mark.parametrize(
    ("sample", "expected"),
    [
        (probs(mel=0.25), True),  # exactly on the 25% threshold
        (probs(mel=0.2499), False),
        (probs(mel=0.10, bcc=0.10, akiec=0.10, nv=0.70), True),  # high-risk classes together, benign on top
        (probs(mel=0.05, nv=0.90), False),
        ({"bcc": 0.22, "nv": 0.20, "bkl": 0.20, "df": 0.19, "vasc": 0.19, "mel": 0.0, "akiec": 0.0}, True),  # on top, under 25%
    ],
)
def test_consultation_rule(sample, expected):
    assert needs_consultation(sample) is expected
