"""Living style guide + reference dashboard.

Run:  streamlit run ui_demo.py

Page 1 is a full dashboard built only from ui/ components (copy its
patterns). Page 2 lists every component. Keep this file in sync when
components are added or changed.
"""

import math
from datetime import datetime, timedelta

import streamlit as st

from ui import charts
from ui import components as ui
from ui.theme import setup_page
from ui.tokens import C, TAG

setup_page("UI demo")

# ------------------------------------------------------------------ sample data
POLLUTANTS = {
    "O3": dict(label="O₃", full="Ozon (O₃)", base=56, amp=22, phase=5, who=100),
    "NO2": dict(label="NO₂", full="Dwutlenek azotu (NO₂)", base=30, amp=11, phase=-3, who=25),
    "PM25": dict(label="PM2.5", full="Pył zawieszony PM2.5", base=20, amp=6, phase=-2, who=15),
    "PM10": dict(label="PM10", full="Pył zawieszony PM10", base=26, amp=9, phase=5, who=45),
}
NOW = datetime(2026, 10, 19, 14, 0)


def value(p: dict, t: float) -> float:
    return (p["base"] + p["amp"] * math.sin(2 * math.pi * (t + p["phase"]) / 24)
            + p["amp"] * 0.18 * math.sin(t * 1.37) + p["amp"] * 0.1 * math.sin(t * 0.53 + 1))


def forecast(p: dict, t: float) -> float:
    return value(p, t) + p["amp"] * 0.01 * t


def ci(p: dict, t: float) -> float:
    return p["amp"] * 0.12 * math.sqrt(t)


def level(ratio: float):
    """(status text, tag kind, meter color) for a ratio to the guideline."""
    if ratio >= 1.1:
        return "PODWYŻSZONY", "warn", C.WARN
    if ratio >= 0.8:
        return "UMIARKOWANY", "highlight", C.HIGHLIGHT
    return "DOBRY", "info", C.ACCENT


STATIONS = [
    ("Centrum", "ST-01", "GIOŚ", True, "14:00", ["O₃", "NO₂", "PM2.5", "PM10"]),
    ("Aleja komunikacyjna", "ST-02", "GIOŚ", True, "14:00", ["NO₂", "PM2.5", "PM10"]),
    ("Park miejski", "ST-03", "GIOŚ", True, "14:00", ["O₃", "NO₂"]),
    ("Osiedle północne", "ST-04", "Airly", True, "14:05", ["PM2.5", "PM10"]),
    ("Strefa przemysłowa", "ST-05", "Airly", False, "09:40 · 4H TEMU", ["PM2.5", "PM10"]),
    ("Czujnik testowy", "ST-06", "Własny", True, "14:03", ["PM2.5", "PM10"]),
]
SOURCE_KIND = {"GIOŚ": "highlight", "Airly": "info", "Własny": "neutral"}


# ------------------------------------------------------------------ pages
def dashboard() -> None:
    ui.page_header(
        "Prognoza jakości powietrza",
        eyebrow="Model szeregów czasowych · prognoza zanieczyszczeń",
        subtitle="Bieżące odczyty ze stacji pomiarowych i prognoza stężeń O₃, NO₂, PM2.5 i PM10 na kolejne godziny.",
        side=[ui.tag("Dane przykładowe"), ui.mono("PON 19.10.2026 · 14:00", color=C.SOFT)],
    )

    c1, c2 = st.columns([3, 2], vertical_alignment="bottom")
    with c1:
        pol = st.segmented_control("Zanieczyszczenie", list(POLLUTANTS), default="PM25",
                                   format_func=lambda k: POLLUTANTS[k]["label"], key="pol", required=True)
    with c2:
        horizon = st.segmented_control("Horyzont", [24, 48, 72], default=24,
                                       format_func=lambda h: f"{h}H", key="horizon", required=True)
    p = POLLUTANTS[pol]

    hx = [NOW + timedelta(hours=t) for t in range(-48, 1)]
    hy = [value(p, t) for t in range(-48, 1)]
    fx = [NOW + timedelta(hours=t) for t in range(0, horizon + 1)]
    fy = [forecast(p, t) for t in range(0, horizon + 1)]
    lo = [max(0.0, forecast(p, t) - ci(p, t)) for t in range(0, horizon + 1)]
    hi = [forecast(p, t) + ci(p, t) for t in range(0, horizon + 1)]

    fig = charts.forecast_chart(hx, hy, fx, fy, lower=lo, upper=hi, threshold=p["who"],
                                threshold_label=f"WHO {p['who']}", unit="µg/m³")
    with ui.panel("forecast"):
        charts.show(fig, key="forecast")
        ui.status_bar(ui.status(True, "POŁĄCZONO"), ui.tag("GIOŚ + Airly"), "MODEL: [NAZWA MODELU]",
                      end="AKTUALIZACJA 14:00 · NASTĘPNA 15:00", inside=True)

    ui.section_label("Aktualne stężenia", meta="Odczyt 14:00 · średnia ze stacji online")
    cols = st.columns(4)
    for col, (key, q) in zip(cols, POLLUTANTS.items()):
        now, prev = value(q, 0), value(q, -1)
        ratio = now / q["who"]
        text, kind, color = level(ratio)
        d = now - prev
        with col:
            ui.kpi_card(
                key, q["label"], round(now), "µg/m³", subtitle=q["full"], badge=ui.tag(text, kind),
                meter=ratio, meter_color=color, meter_caption=f"{round(ratio * 100)}% wytycznej WHO",
                delta=f"{'+' if d >= 0 else '−'}{abs(d):.1f} / 1H",
                footer=("Prognoza +24H", f"{round(forecast(q, 24))} µg/m³"), active=(key == pol),
            )

    online = sum(s[3] for s in STATIONS)
    ui.section_label("Stacje pomiarowe", meta=f"{online}/{len(STATIONS)} online · odświeżanie co 5 min")
    left, right = st.columns([5, 2], gap="medium")
    with left:
        ui.table(
            ["Status", "Stacja", "Źródło", "Mierzone", "Ostatni odczyt"],
            [
                [ui.status(ok), ui.two_line(name, code),
                 ui.tag(src, SOURCE_KIND[src]), ui.tags(params), ui.mono(last, color=C.SOFT if ok else C.BAD_TEXT)]
                for name, code, src, ok, last, params in STATIONS
            ],
        )
    with right:
        ui.stat_box("Stacje online", online, suffix=f"/{len(STATIONS)}")
        ui.placeholder("[MAPA STACJI] · np. st.map lub streamlit-folium")


def components_page() -> None:
    ui.page_header("Komponenty", eyebrow="Style guide", subtitle="Wszystko, z czego budujemy strony. "
                   "Nowy element: najpierw tutaj, potem na stronie.")

    ui.section_label("Tagi i statusy")
    ui.html(ui.join(ui.tag("highlight"), ui.tag("info", "info"), ui.tag("neutral", "neutral"),
                    ui.tag("warn", "warn"), ui.tag("bad", "bad"), ui.tag("dark", "dark"),
                    ui.status(True), ui.status(False), sep="  "))

    ui.section_label("Przyciski i kontrolki")
    b1, b2, b3 = st.columns(3)
    b1.button("Primary", type="primary")
    b2.button("Secondary")
    b3.segmented_control("Segmented", ["A", "B", "C"], default="A", key="seg_demo")
    i1, i2 = st.columns(2)
    i1.text_input("Text input", placeholder="Wpisz coś…")
    i2.selectbox("Selectbox", ["Opcja 1", "Opcja 2"])

    ui.section_label("Karty")
    k1, k2, k3 = st.columns(3)
    with k1:
        ui.kpi_card("demo_a", "Metric", 42, "unit", subtitle="Subtitle", badge=ui.tag("OK", "info"),
                    meter=0.6, meter_caption="60% of limit", delta="+1.2", footer=("Footer", "value"))
    with k2:
        ui.kpi_card("demo_b", "Active", 87, "unit", badge=ui.tag("Warn", "warn"), meter=1.3,
                    meter_color=C.WARN, meter_caption="130% of limit", active=True)
    with k3:
        with ui.card("demo_c"):
            st.metric("st.metric in a card", "1 234", "+5%")
            st.caption("Any native widget can sit inside ui.card().")

    ui.section_label("Statystyka, info, placeholder")
    s1, s2, s3 = st.columns(3)
    with s1:
        ui.stat_box("Dark stat", 5, suffix="/6")
    with s2:
        ui.info_box("[Imię i nazwisko]", "Promotor: [—]", "[Uczelnia] · 2026", eyebrow="Praca inżynierska")
    with s3:
        ui.placeholder("[PLACEHOLDER]")

    ui.section_label("Wykresy")
    g1, g2 = st.columns(2)
    with g1:
        charts.show(charts.bar_chart(["A", "B", "C", "D"], [12, 30, 22, 9], highlight=[False, True, False, False]),
                    key="bar_demo")
    with g2:
        charts.show(charts.line_chart(list(range(24)), {"Seria 1": [math.sin(i / 3) * 10 + 20 for i in range(24)],
                                                        "Seria 2": [math.cos(i / 4) * 8 + 15 for i in range(24)]}),
                    key="line_demo")

    ui.section_label("Tabela i pasek statusu")
    ui.table(["Kolumna", "Status", "Tagi"], [["Wiersz 1", ui.status(True), ui.tags(["A", "B"])],
                                              ["Wiersz 2", ui.status(False), ui.tags(["C"])]])
    ui.status_bar(ui.status(True, "CONNECTED"), ui.tag("EU-CENTRAL"), end="UPDATED 14:00")

    ui.section_label("Paleta")
    swatches = [("BG", C.BG), ("SURFACE", C.SURFACE), ("INK", C.INK), ("MUTED", C.MUTED), ("ACCENT", C.ACCENT),
                ("ACCENT_DARK", C.ACCENT_DARK), ("HIGHLIGHT", C.HIGHLIGHT), ("WARN", C.WARN), ("OK", C.OK),
                ("BAD", C.BAD), ("TAG.INFO", TAG.INFO), ("TAG.WARN", TAG.WARN)]
    cols = st.columns(6)
    for i, (name, hexv) in enumerate(swatches):
        with cols[i % 6]:
            ui.html(ui.swatch(name, hexv))


# ------------------------------------------------------------------ navigation
ui.sidebar_brand("AIRCAST")
nav = st.navigation([
    st.Page(dashboard, title="Prognoza", icon=":material/show_chart:", default=True),
    st.Page(components_page, title="Komponenty", icon=":material/widgets:"),
])
with st.sidebar:
    ui.info_box("[Imię i nazwisko]", "Promotor: [tytuł, imię i nazwisko]", "[Uczelnia] · 2026",
                eyebrow="Praca inżynierska")
nav.run()
