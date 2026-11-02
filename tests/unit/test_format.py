import pytest

from ui.components import _e, prob_row, tag
from ui.components import pct as percent


@pytest.mark.parametrize(("value", "text"), [(0.78, "78%"), (0.1, "10%"), (0.015, "1,5%"), (0.004, "0,4%")])
def test_polish_percent(value, text):
    assert percent(value) == text


def test_text_is_escaped_but_fragments_pass_through():
    assert _e("<b>") == "&lt;b&gt;"
    assert _e(tag("x")) == str(tag("x"))


def test_prob_row_is_a_named_button():
    html = prob_row("mel", "Czerniak", "78%", 78, True, True, False, "Czerniak, 78%")
    assert html.startswith("<button")
    assert 'data-code="mel"' in html and "Ryzyko" in html and "width:78.0%" in html
