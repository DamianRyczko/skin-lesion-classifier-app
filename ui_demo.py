"""Living style guide: every component, in both themes.

Run:  uv run streamlit run ui_demo.py

Keep this file in sync when components are added or changed.
"""

import streamlit as st

from ui import components as ui
from ui.theme import setup_page
from ui.tokens import TAG, THEME_LABELS, THEMES, C

st.session_state.setdefault("theme", "light")
setup_page("UI demo", st.session_state.theme)

ui.skyline(st.session_state.theme)
with st.container(key="nbpage"):
    ui.page_header("Komponenty", eyebrow="Style guide", side=[ui.steps(["1 Pierwszy", "2 Drugi"], 1)])
    st.segmented_control("Motyw", list(THEMES), format_func=THEME_LABELS.__getitem__, key="theme", required=True)

    ui.section_label("Tagi i statusy")
    ui.html(
        ui.join(
            *(ui.tag(kind, kind) for kind in ("highlight", "info", "neutral", "warn", "bad")),
            ui.status(True, "OK"),
            ui.status(False, "", "BŁĄD"),
            sep="  ",
        )
    )

    ui.section_label("Przyciski i kontrolki")
    b1, b2, b3 = st.columns(3)
    b1.button("Primary", type="primary")
    b2.button("Secondary")
    b3.toggle("Przełącznik", key="demo_toggle")
    st.segmented_control("Segmented", ["A", "B", "C"], default="A", key="seg_demo", required=True)
    st.slider("Suwak", 0, 100, 40, key="demo_slider")

    ui.section_label("Karty i panele")
    k1, k2 = st.columns(2)
    with k1, ui.card("demo"):
        ui.text_card("Karta", "Dowolna treść w ramce.")
    with k2, ui.card("demo_active", active=True):
        ui.text_card("Karta aktywna", "Twardy cień tylko dla wyróżnionego elementu.")
    with ui.panel("demo_panel"):
        with st.container(key="nbphead_demo", horizontal=True):
            ui.label("Panel")
            ui.html(ui.tag("Tag"))
        ui.banner("Baner", "Zwykły komunikat.", warn=False)
        ui.banner("Baner ostrzegawczy", "Wymaga uwagi.", warn=True)
        ui.status_bar("Pozycja", ui.status(True, "OK"), end="Koniec", inside=True)

    ui.section_label("Wynik", meta="Paski są mountowane przez ui.widgets.prob_rows")
    ui.html(
        "".join(
            ui.prob_row(code, name, pct, width, high, top, False, name)
            for code, name, pct, width, high, top in [
                ("mel", "Czerniak", "78%", 78, True, True),
                ("nv", "Znamię melanocytowe", "12%", 12, False, False),
            ]
        )
    )
    ui.xai_legend("mała uwaga", "duża uwaga")
    ui.disclaimer("Tag", "Stała informacja na dole strony.")
    ui.tips(["Pierwsza wskazówka.", "Druga wskazówka."])

    ui.section_label("Ładowanie")
    ui.Loader().update("Analiza: Model A", "Widok TTA 7 z 16", 7, 16)

    ui.section_label("Paleta")
    swatches = [
        ("BG", C.BG),
        ("SURFACE", C.SURFACE),
        ("INK", C.INK),
        ("LINE", C.LINE),
        ("SHADOW", C.SHADOW),
        ("ACCENT", C.ACCENT),
        ("RISK", C.RISK),
        ("HIGHLIGHT", C.HIGHLIGHT),
        ("OK", C.OK),
        ("BAD", C.BAD),
        ("TAG.INFO", TAG.INFO),
        ("TAG.WARN", TAG.WARN),
    ]
    cols = st.columns(6)
    for i, (name, value) in enumerate(swatches):
        with cols[i % 6]:
            ui.html(ui.swatch(name, value))
