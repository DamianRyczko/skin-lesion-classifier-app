"""HTML pieces for the pages. Every text argument is escaped; Html fragments pass through as they are."""

from collections.abc import Iterable, Iterator, Sequence
from contextlib import contextmanager
from html import escape
from typing import Literal

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from .assets import pixel, sample
from .theme import KEY_PANEL, KEY_SPLIT
from .tokens import TAG, XAI_SCALE, C


class Html(str):
    """Already safe HTML."""


def _e(value: object) -> str:
    if isinstance(value, Html):
        return str(value)
    return escape("" if value is None else str(value))


def html(fragment: str) -> None:
    st.html(str(fragment))


# ---------------------------------------------------------------- inline pieces

_TAG_BG = {"info": TAG.INFO, "warn": TAG.WARN}


def tag(text: object, kind: Literal["info", "warn"]) -> Html:
    return Html(f'<span class="nb-tag" style="background:{_TAG_BG[kind]}">{_e(text)}</span>')


def status(label: str) -> Html:
    """Green dot + text."""
    return Html(f'<span class="nb-status"><span class="nb-dot" style="background:{C.OK}"></span>{_e(label)}</span>')


def mono(text: object) -> Html:
    return Html(f'<span class="nb-mono">{_e(text)}</span>')


def bold(text: object) -> Html:
    return Html(f"<b>{_e(text)}</b>")


def join(*parts: object, sep: str = " ") -> Html:
    return Html(_e(sep).join(_e(p) for p in parts))


def pct(value: float) -> str:
    """Polish percent: 78%, 1,5%."""
    percent = value * 100
    return f"{percent:.0f}%" if percent >= 10 else f"{percent:.1f}%".replace(".", ",")


# ---------------------------------------------------------------- containers


def _key(prefix: str, key: str) -> str:
    return prefix + "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in str(key))


@contextmanager
def panel(key: str) -> Iterator[None]:
    """Bordered frame with no padding or gaps."""
    with st.container(key=_key(KEY_PANEL, key), gap=None):
        yield


@contextmanager
def split(key: str, spec: Sequence[float], gap: Literal["small", "medium", "large"] = "large") -> Iterator[list[DeltaGenerator]]:
    """st.columns that stack below 900px instead of Streamlit's 640px."""
    with st.container(key=_key(KEY_SPLIT, key)):
        yield st.columns(spec, gap=gap)


# ---------------------------------------------------------------- page chrome


def skyline() -> None:
    # The picture is the theme's --nb-sky, see styles/01-base.css.
    html('<div class="nb-sky" aria-hidden="true"></div>')


def brand(name: str, theme: str) -> None:
    html(f'<div class="nb-brand"><img class="nb-px" src="{pixel(f"mark-{theme}")}" alt=""><span>{_e(name)}</span></div>')


def page_header(title: str, side: Sequence[object] = ()) -> None:
    right = "".join(f"<div>{_e(s)}</div>" for s in side)
    html(f'<div class="nb-header"><div><h1>{_e(title)}</h1></div><div class="nb-header-side nb-mono">{right}</div></div>')


def steps(labels: Sequence[str], current: int) -> Html:
    items = "".join(f'<li class="{"on" if i == current else ""}">{_e(text)}</li>' for i, text in enumerate(labels))
    return Html(f'<ol class="nb-steps" aria-label="Kroki">{items}</ol>')


def label(text: str) -> None:
    html(f'<span class="nb-lbl">{_e(text)}</span>')


def note(text: object) -> None:
    html(f'<div class="nb-note">{_e(text)}</div>')


def hint(text: str) -> None:
    html(f'<p class="nb-hint">{_e(text)}</p>')


def tips(items: Iterable[str]) -> None:
    html('<ul class="nb-tips">' + "".join(f"<li>{_e(i)}</li>" for i in items) + "</ul>")


def banner(title: str, text: str, warn: bool) -> None:
    cls = "nb-banner warn" if warn else "nb-banner"
    html(f'<div class="{cls}"><b>{_e(title)}</b>{_e(text)}</div>')


def disclaimer(title: str, text: str) -> None:
    html(f'<div class="nb-disc">{tag(title, "warn")}<span>{_e(text)}</span></div>')


def status_bar(*parts: object, end: object = None) -> None:
    """Thin bar at the bottom of a panel."""
    end_html = f'<span class="nb-bar-end">{_e(end)}</span>' if end is not None else ""
    html('<div class="nb-bar nb-bar-inside">' + "".join(f"<span>{_e(p)}</span>" for p in parts) + end_html + "</div>")


# ---------------------------------------------------------------- result


def prob_row(code: str, name: str, pct: str, width: float, high: bool, top: bool, selected: bool, aria: str) -> Html:
    """One clickable bar, mounted through widgets.prob_rows."""
    cls = "nb-row" + (" top" if top else "") + (" sel" if selected else "")
    fill = "nb-fill high" if high else "nb-fill"
    risk = tag("Ryzyko", "warn") if high else ""
    return Html(
        f'<button class="{cls}" type="button" data-code="{_e(code)}" aria-label="{_e(aria)}">'
        f'<span class="nb-rtop"><span class="nb-rname">{_e(name)}</span>{risk}'
        f'<span class="nb-rpct">{_e(pct)}</span></span>'
        f'<span class="nb-meter"><span class="{fill}" style="width:{width:.1f}%"></span></span></button>'
    )


def xai_legend(low: str, high: str) -> None:
    scale = "".join(f'<span style="background:{color}"></span>' for color in XAI_SCALE)
    html(
        f'<div class="nb-legend"><span>{_e(low)}</span><span class="nb-scale" aria-hidden="true">{scale}</span>'
        f"<span>{_e(high)}</span></div>"
    )


def class_detail(code: str, pct: str, tier: str, high: bool, about: str, advice: str, source: str) -> None:
    """Body of the slide-out panel."""
    caption = "Przykładowe zdjęcie z HAM10000."
    figure = f'<img src="{sample(code)}" alt="{caption}"><figcaption>{caption}</figcaption>'
    html(
        f'<div class="nb-eyebrow">{_e(code)} · HAM10000</div>'
        f'<div class="nb-score"><span class="nb-score-num">{_e(pct)}</span>{tag(tier, "warn" if high else "info")}</div>'
    )
    html(f'<figure class="nb-fig">{figure}</figure>')
    html(f'<div class="nb-sec"><h3>Co to jest</h3><p>{_e(about)}</p></div>')
    html(f'<div class="nb-sec nb-advice"><h3>Co zrobić</h3><p>{_e(advice)}</p></div>')
    html(f'<p class="nb-src">{_e(source)}</p>')


# ---------------------------------------------------------------- loading

_LOADER_BLOCKS = 16  # columns of .nb-blocks


class Loader:
    """Walking cat plus progress, in separate placeholders so updates don't restart the animation."""

    def __init__(self, name: str = "main") -> None:
        self._box = st.container(key=f"nbload_{name}")  # one run can show two: the analysis, then the map
        with self._box:
            html('<div class="nb-track" aria-hidden="true"><div class="nb-walk"></div></div>')
            self._title = st.empty()
            self._blocks = st.empty()
            self._stage = st.empty()

    def update(self, title: str, stage: str, done: int, total: int) -> None:
        filled = round(done / total * _LOADER_BLOCKS)
        blocks = "".join(f'<span class="{"on" if i < filled else ""}"></span>' for i in range(_LOADER_BLOCKS))
        self._title.html(f'<div class="nb-big" role="status">{_e(title)}</div>')
        self._blocks.html(f'<div class="nb-blocks" aria-hidden="true">{blocks}</div>')
        self._stage.html(f'<div class="nb-stage">{_e(stage)}</div>')
