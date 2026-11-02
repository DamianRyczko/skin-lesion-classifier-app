"""Entry point: theme, top bar, the page.   mise run dev  /  uv run streamlit run app.py"""

import streamlit as st
from loguru import logger

from core.log import setup_logging
from ui import components as ui
from ui.assets import PIXEL
from ui.theme import setup_page
from ui.tokens import THEME_LABELS, THEMES

setup_logging()

if "theme" not in st.session_state:
    requested = st.query_params.get("theme", "light")
    st.session_state.theme = requested if requested in THEMES else "light"

setup_page("Klasyfikator zmian skórnych", st.session_state.theme, icon=str(PIXEL / f"mark-{st.session_state.theme}.png"))


def on_theme_change() -> None:
    st.query_params["theme"] = st.session_state.theme  # survives a page reload
    logger.info("theme {}", st.session_state.theme)


if "seen" not in st.session_state:
    st.session_state.seen = True
    logger.info("session started")

nav = st.navigation([st.Page("pages/analyze.py", title="Analiza", default=True)], position="hidden")

with st.container(key="nbtop", gap=None):
    ui.skyline(st.session_state.theme)
    with st.container(key="nbbar", horizontal=True):
        ui.brand("KLASYFIKATOR ZMIAN SKÓRNYCH", st.session_state.theme)
        st.segmented_control(
            "Motyw",
            list(THEMES),
            format_func=THEME_LABELS.__getitem__,
            key="theme",
            required=True,
            label_visibility="collapsed",
            on_change=on_theme_change,
        )

with st.container(key="nbpage"):
    nav.run()
    ui.disclaimer(
        "To nie jest diagnoza",
        "Projekt edukacyjny, nie wyrób medyczny. Niepokojącą zmianę zawsze pokaż lekarzowi, nawet jeśli wynik wygląda dobrze.",
    )
