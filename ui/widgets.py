"""Components v2 widgets (no iframe, so they follow the theme). Their JS is in ui/js/."""

import json
from pathlib import Path

import streamlit as st

from .components import Html, _e, prob_row

JS_DIR = Path(__file__).with_name("js")

_cropper = st.components.v2.component(
    "skin_lesion_cropper", js=(JS_DIR / "cropper.js").read_text(encoding="utf-8"), isolate_styles=False
)
_rows = st.components.v2.component("skin_lesion_rows", js=(JS_DIR / "rows.js").read_text(encoding="utf-8"), isolate_styles=False)


def cropper(src: str, box: dict[str, float], key: str) -> dict[str, float]:
    """Returns the box as fractions of width and height."""
    result = _cropper(key=key, data={"src": src, "box": box}, default={"box": box}, on_box_change=lambda: None)
    return result.box or box


def prob_rows(rows: list[dict], key: str) -> str | None:
    """Returns the class code clicked in this run, if any."""
    markup = Html("".join(prob_row(**row) for row in rows))
    signature = json.dumps([[row["code"], row["pct"], row["top"], row["selected"]] for row in rows])
    result = _rows(key=key, data={"html": _e(markup), "signature": signature}, on_open_change=lambda: None)
    return result.open
