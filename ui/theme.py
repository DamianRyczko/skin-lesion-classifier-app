"""Puts styles/*.css and the active theme's colours (as --nb-* variables) on the page.

Streamlit cannot switch its theme from Python, so config.toml stays light and styles/ paints every
widget. A widget that looks light in the dark theme is missing a rule there.
"""

from functools import cache
from pathlib import Path

import streamlit as st

from .assets import pixel
from .tokens import THEMES, css_var

STYLES_DIR = Path(__file__).with_name("styles")

KEY_PANEL = "nbpanel_"
KEY_SPLIT = "nbsplit_"  # columns stack below 900px


def get_palette_css(theme: str) -> str:
    colors = "".join(f"{css_var(name)}:{value};" for name, value in THEMES[theme].items())
    sprites = "".join(
        f'--nb-{var}:url("{pixel(name)}");'
        for var, name in (("sky", f"sky-{theme}"), ("cat", f"cat-doctor-{theme}"), ("walk", f"cat-walk-{theme}"), ("paw", "paw"))
    )
    return ":root{" + colors + sprites + "}"


def stylesheet_files() -> list[Path]:
    return sorted(STYLES_DIR.glob("*.css"))


@cache
def _rules() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in stylesheet_files())


def setup_page(title: str, theme: str, icon: str | None = None) -> None:
    st.set_page_config(page_title=title, page_icon=icon, layout="wide", initial_sidebar_state="collapsed")
    st.html(f"<style>{get_palette_css(theme)}{_rules()}</style>")
