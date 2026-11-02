"""Reusable UI pieces. Pages build their layout from these and from native
Streamlit widgets; they never write raw HTML or CSS themselves.

Escaping: every text argument is HTML-escaped. Functions that return an
HTML fragment (tag, status, ...) return `Html`, which is passed through
unescaped when used inside another component.

Adding a component: write it here, use only tokens and nb-* classes
(add new classes in theme.py), add it to ui_demo.py and document it in
.claude/skills/streamlit-neubrutal-ui/references/components.md.
"""

from collections.abc import Iterable, Iterator, Sequence
from contextlib import contextmanager
from html import escape
from typing import Literal

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from .assets import pixel, sample
from .theme import KEY_CARD, KEY_CARD_ACTIVE, KEY_PANEL, KEY_SPLIT
from .tokens import TAG, XAI_SCALE, C


class Html(str):
    """A string that is already safe HTML."""


def _e(value: object) -> str:
    if isinstance(value, Html):
        return str(value)
    return escape("" if value is None else str(value))


def _join(parts: Iterable[object]) -> str:
    return "".join(_e(p) for p in parts)


def html(fragment: str) -> None:
    """Render an Html fragment built by this module."""
    st.html(str(fragment))


# ---------------------------------------------------------------- inline pieces

_TAG_BG = {
    "highlight": TAG.HIGHLIGHT,
    "info": TAG.INFO,
    "neutral": TAG.NEUTRAL,
    "warn": TAG.WARN,
    "bad": TAG.BAD,
}


def tag(text: object, kind: str = "highlight") -> Html:
    """Small bordered uppercase label. kind: highlight | info | neutral | warn | bad."""
    bg = _TAG_BG.get(kind, TAG.HIGHLIGHT)
    return Html(f'<span class="nb-tag" style="background:{bg}">{_e(text)}</span>')


def tags(items: Iterable[object], kind: str = "neutral") -> Html:
    return Html('<span class="nb-tags">' + "".join(tag(i, kind) for i in items) + "</span>")


def status(ok: bool, ok_label: str, bad_label: str = "") -> Html:
    """Colored dot + text. Never color alone: the label carries the meaning."""
    color, label = (C.OK, ok_label) if ok else (C.BAD, bad_label)
    return Html(f'<span class="nb-status"><span class="nb-dot" style="background:{color}"></span>{_e(label)}</span>')


def mono(text: object, color: str | None = None, bold: bool = False) -> Html:
    style = ""
    if color:
        style += f"color:{color};"
    if bold:
        style += "font-weight:700;"
    return Html(f'<span class="nb-mono" style="{style}">{_e(text)}</span>')


def two_line(primary: object, secondary: object) -> Html:
    """Bold first line + small mono second line, e.g. station name + code in a table cell."""
    return Html(
        f'<span style="display:flex;flex-direction:column;gap:2px"><b>{_e(primary)}</b>'
        f'<span class="nb-mono" style="font-size:11px;color:{C.MUTED}">{_e(secondary)}</span></span>'
    )


def join(*parts: object, sep: str = " ") -> Html:
    """Put several Html pieces in one line."""
    return Html(_e(sep).join(_e(p) for p in parts))


def swatch(name: str, color: str) -> Html:
    """Color sample with its name, for the style guide."""
    return Html(
        f'<div style="height:48px;background:{_e(color)};border:2px solid {C.LINE}"></div>'
        f'<span class="nb-mono" style="font-size:11px;color:{C.SOFT}">{_e(name)} {_e(color)}</span>'
    )


# ---------------------------------------------------------------- blocks


def page_header(title: str, eyebrow: str | None = None, subtitle: str | None = None, side: Sequence[object] = ()) -> None:
    """Big uppercase mono title. `side`: Html/str items stacked on the right (tags, timestamp)."""
    left = ""
    if eyebrow:
        left += f'<div class="nb-eyebrow">{_e(eyebrow)}</div>'
    left += f"<h1>{_e(title)}</h1>"
    if subtitle:
        left += f"<p>{_e(subtitle)}</p>"
    right = "".join(f"<div>{_e(s)}</div>" for s in side)
    html(f'<div class="nb-header"><div>{left}</div><div class="nb-header-side nb-mono">{right}</div></div>')


def section_label(text: str, meta: str | None = None) -> None:
    """Uppercase mono section title with a rule running to the right: AKTUALNE STĘŻENIA ─────── meta."""
    meta_html = f'<span class="nb-label-meta">{_e(meta)}</span>' if meta else ""
    html(f'<div class="nb-label"><span>{_e(text)}</span><span class="nb-label-line"></span>{meta_html}</div>')


def status_bar(*parts: object, end: object = None, inside: bool = False) -> None:
    """Thin bar of status items: status_bar(status(True,'CONNECTED'), tag('EU'), end='UPDATED 14:00').

    inside=True: last element of a panel() -> only a top rule, the panel draws the frame.
    """
    end_html = f'<span class="nb-bar-end">{_e(end)}</span>' if end is not None else ""
    cls = "nb-bar nb-bar-inside" if inside else "nb-bar"
    html(f'<div class="{cls}">' + "".join(f"<span>{_e(p)}</span>" for p in parts) + end_html + "</div>")


# ---------------------------------------------------------------- containers


def _key(prefix: str, key: str) -> str:
    return prefix + "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in str(key))


@contextmanager
def card(key: str, active: bool = False) -> Iterator[None]:
    """Bordered card container. `active=True` adds the hard offset shadow.

    with card("pm25", active=True):
        st.write(...)
    """
    prefix = KEY_CARD_ACTIVE if active else KEY_CARD
    with st.container(key=_key(prefix, key)):
        yield


@contextmanager
def panel(key: str) -> Iterator[None]:
    """Bordered frame with no padding or gaps: a chart plus status_bar(inside=True) under it.

    with panel("forecast"):
        charts.show(fig)
        status_bar(status(True, "CONNECTED"), end="UPDATED 14:00", inside=True)
    """
    with st.container(key=_key(KEY_PANEL, key), gap=None):
        yield


@contextmanager
def split(key: str, spec: Sequence[float], gap: Literal["small", "medium", "large"] = "large") -> Iterator[list[DeltaGenerator]]:
    """st.columns that stack below the S.NARROW breakpoint instead of Streamlit's 640px.

    with split("result", [5, 6]) as (left, right):
        ...
    """
    with st.container(key=_key(KEY_SPLIT, key)):
        yield st.columns(spec, gap=gap)


# ---------------------------------------------------------------- app chrome


def skyline(theme: str) -> None:
    """Cat city strip above the top bar. Decorative, twice over so wide screens stay covered."""
    src = pixel(f"sky-{theme}")
    html(
        f'<div class="nb-sky" aria-hidden="true"><img class="nb-px" src="{src}" alt="">'
        f'<img class="nb-px" src="{src}" alt=""></div>'
    )


def brand(name: str, theme: str) -> None:
    html(f'<div class="nb-brand"><img class="nb-px" src="{pixel(f"mark-{theme}")}" alt=""><span>{_e(name)}</span></div>')


def steps(labels: Sequence[str], current: int) -> Html:
    items = "".join(f'<li class="{"on" if i == current else ""}">{_e(text)}</li>' for i, text in enumerate(labels))
    return Html(f'<ol class="nb-steps" aria-label="Kroki">{items}</ol>')


def label(text: str) -> None:
    html(f'<span class="nb-lbl">{_e(text)}</span>')


def note(text: object) -> None:
    html(f'<div class="nb-note">{_e(text)}</div>')


def bold(text: object) -> Html:
    return Html(f"<b>{_e(text)}</b>")


def tips(items: Iterable[str]) -> None:
    html('<ul class="nb-tips">' + "".join(f"<li>{_e(i)}</li>" for i in items) + "</ul>")


def disclaimer(title: str, text: str) -> None:
    html(f'<div class="nb-disc">{tag(title, "warn")}<span>{_e(text)}</span></div>')


def text_card(title: str, text: str) -> None:
    html(f'<div class="nb-card-text"><span class="nb-lbl">{_e(title)}</span><p>{_e(text)}</p></div>')


# ---------------------------------------------------------------- result


def prob_row(code: str, name: str, pct: str, width: float, high: bool, top: bool, selected: bool, aria: str) -> Html:
    """One clickable bar. Mounted through widgets.prob_rows."""
    cls = "nb-row" + (" top" if top else "") + (" sel" if selected else "")
    fill = "nb-fill high" if high else "nb-fill"
    risk = tag("Ryzyko", "warn") if high else ""
    return Html(
        f'<button class="{cls}" type="button" data-code="{_e(code)}" aria-label="{_e(aria)}">'
        f'<span class="nb-rtop"><span class="nb-rname">{_e(name)}</span>{risk}'
        f'<span class="nb-rpct">{_e(pct)}</span></span>'
        f'<span class="nb-meter"><span class="{fill}" style="width:{width:.1f}%"></span></span></button>'
    )


def hint(text: str) -> None:
    html(f'<p class="nb-hint">{_e(text)}</p>')


def banner(title: str, text: str, warn: bool) -> None:
    cls = "nb-banner warn" if warn else "nb-banner"
    html(f'<div class="{cls}"><b>{_e(title)}</b>{_e(text)}</div>')


def xai_legend(low: str, high: str) -> None:
    scale = "".join(f'<span style="background:{color}"></span>' for color in XAI_SCALE)
    html(
        f'<div class="nb-legend"><span>{_e(low)}</span><span class="nb-scale" aria-hidden="true">{scale}</span>'
        f"<span>{_e(high)}</span></div>"
    )


def class_detail(code: str, pct: str, tier: str, high: bool, about: str, advice: str, source: str) -> None:
    """Body of the slide-out panel."""
    photo = sample(code)
    caption = "Przykładowe zdjęcie z HAM10000."
    figure = (
        f'<img src="{photo}" alt="{caption}"><figcaption>{caption}</figcaption>'
        if photo
        else f'<div class="nb-fig-empty"><img class="nb-px" src="{pixel("paw")}" alt="">Miejsce na zdjęcie przykładowe</div>'
    )
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
    """Loading panel: a walking cat plus progress in separate placeholders, so updates don't restart its animation."""

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


def pct(value: float) -> str:
    """Polish percent: 78%, 1,5%."""
    percent = value * 100
    return f"{percent:.0f}%" if percent >= 10 else f"{percent:.1f}%".replace(".", ",")
