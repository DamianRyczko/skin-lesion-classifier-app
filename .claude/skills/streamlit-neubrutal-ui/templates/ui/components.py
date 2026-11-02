"""Reusable UI pieces. Pages build their layout from these and from native
Streamlit widgets; they never write raw HTML or CSS themselves.

Escaping: every text argument is HTML-escaped. Functions that return an
HTML fragment (tag, status, ...) return `Html`, which is passed through
unescaped when used inside another component.

Adding a component: write it here, use only tokens and nb-* classes
(add new classes in theme.py), add it to ui_demo.py and document it in
.claude/skills/streamlit-neubrutal-ui/references/components.md.
"""

from contextlib import contextmanager
from html import escape
from typing import Iterable, Sequence

import streamlit as st

from .theme import KEY_CARD, KEY_CARD_ACTIVE, KEY_PANEL
from .tokens import C, TAG


class Html(str):
    """A string that is already safe HTML."""


def _e(value) -> str:
    if isinstance(value, Html):
        return str(value)
    return escape("" if value is None else str(value))


def _join(parts: Iterable) -> str:
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


def tag(text, kind: str = "highlight") -> Html:
    """Small bordered uppercase label. kind: highlight | info | neutral | warn | bad | dark."""
    if kind == "dark":
        return Html(f'<span class="nb-tag nb-tag-dark">{_e(text)}</span>')
    bg = _TAG_BG.get(kind, TAG.HIGHLIGHT)
    return Html(f'<span class="nb-tag" style="background:{bg}">{_e(text)}</span>')


def tags(items: Iterable, kind: str = "neutral") -> Html:
    return Html('<span class="nb-tags">' + "".join(tag(i, kind) for i in items) + "</span>")


def status(ok: bool, ok_label: str = "ONLINE", bad_label: str = "OFFLINE") -> Html:
    """Colored dot + text. Never color alone: the label carries the meaning."""
    color, label = (C.OK, ok_label) if ok else (C.BAD, bad_label)
    return Html(f'<span class="nb-status"><span class="nb-dot" style="background:{color}"></span>{_e(label)}</span>')


def mono(text, color: str | None = None, bold: bool = False) -> Html:
    style = ""
    if color:
        style += f"color:{color};"
    if bold:
        style += "font-weight:700;"
    return Html(f'<span class="nb-mono" style="{style}">{_e(text)}</span>')


def two_line(primary, secondary) -> Html:
    """Bold first line + small mono second line, e.g. station name + code in a table cell."""
    return Html(f'<span style="display:flex;flex-direction:column;gap:2px"><b>{_e(primary)}</b>'
                f'<span class="nb-mono" style="font-size:11px;color:{C.MUTED}">{_e(secondary)}</span></span>')


def join(*parts, sep: str = " ") -> Html:
    """Put several Html pieces in one line."""
    return Html(_e(sep).join(_e(p) for p in parts))


def swatch(name: str, color: str) -> Html:
    """Color sample with its name, for the style guide."""
    return Html(f'<div style="height:48px;background:{_e(color)};border:2px solid {C.INK}"></div>'
                f'<span class="nb-mono" style="font-size:11px;color:{C.SOFT}">{_e(name)} {_e(color)}</span>')


# ---------------------------------------------------------------- blocks

def page_header(title: str, eyebrow: str | None = None, subtitle: str | None = None,
                side: Sequence = ()) -> None:
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


def status_bar(*parts, end=None, inside: bool = False) -> None:
    """Thin bar of status items: status_bar(status(True,'CONNECTED'), tag('EU'), end='UPDATED 14:00').

    inside=True: last element of a panel() -> only a top rule, the panel draws the frame.
    """
    end_html = f'<span class="nb-bar-end">{_e(end)}</span>' if end is not None else ""
    cls = "nb-bar nb-bar-inside" if inside else "nb-bar"
    html(f'<div class="{cls}">' + "".join(f"<span>{_e(p)}</span>" for p in parts) + end_html + "</div>")


def stat_box(label: str, value, suffix: str | None = None, dark: bool = True) -> None:
    """Large single number in a box, e.g. '5/6 stations online'."""
    bg, fg = (C.INK, C.BG) if dark else (C.SURFACE, C.INK)
    suffix_html = f'<span style="font-size:22px;opacity:.75">{_e(suffix)}</span>' if suffix else ""
    html(f'<div class="nb-stat" style="background:{bg};color:{fg}">'
         f'<span class="nb-stat-label">{_e(label)}</span>'
         f'<span class="nb-stat-value">{_e(value)}{suffix_html}</span></div>')


def info_box(title: str, *lines: str, eyebrow: str | None = None) -> None:
    """Small bordered box with a bold first line, e.g. author / supervisor block in the sidebar."""
    eb = f'<span class="nb-eyebrow" style="font-size:11px">{_e(eyebrow)}</span>' if eyebrow else ""
    body = "".join(f"<span>{_e(l)}</span>" for l in lines)
    html(f'<div class="nb-box">{eb}<b>{_e(title)}</b>{body}</div>')


def placeholder(text: str, height: int = 140) -> None:
    """Dashed box for something not built yet (map, chart)."""
    html(f'<div class="nb-placeholder" style="min-height:{int(height)}px">{_e(text)}</div>')


def table(headers: Sequence[str], rows: Iterable[Sequence], min_width: int = 640) -> None:
    """Styled HTML table. Cells can be plain values or Html (status(), tags(), mono())."""
    head = "".join(f"<th>{_e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{_e(c)}</td>" for c in r) + "</tr>" for r in rows)
    html(f'<div class="nb-table-wrap"><table class="nb-table" style="min-width:{int(min_width)}px">'
         f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>")


# ---------------------------------------------------------------- sidebar

def sidebar_brand(name: str) -> None:
    """Logo at the top of the sidebar (above st.navigation links): orange square + name."""
    width = 44 + 12 * len(name)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="32" viewBox="0 0 {width} 32">'
           f'<rect x="1" y="3" width="26" height="26" fill="{C.WARN}" stroke="{C.INK}" stroke-width="2"/>'
           f'<text x="38" y="23" font-family="JetBrains Mono, Menlo, Consolas, monospace" font-size="18" '
           f'font-weight="700" letter-spacing="1" fill="{C.INK}">{_e(name)}</text></svg>')
    st.logo(svg, size="large")


# ---------------------------------------------------------------- containers

def _key(prefix: str, key: str) -> str:
    return prefix + "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in str(key))


@contextmanager
def card(key: str, active: bool = False):
    """Bordered card container. `active=True` adds the hard offset shadow.

        with card("pm25", active=True):
            st.write(...)
    """
    prefix = KEY_CARD_ACTIVE if active else KEY_CARD
    with st.container(key=_key(prefix, key)):
        yield


@contextmanager
def panel(key: str):
    """Bordered frame with no padding or gaps: a chart plus status_bar(inside=True) under it.

        with panel("forecast"):
            charts.show(fig)
            status_bar(status(True, "CONNECTED"), end="UPDATED 14:00", inside=True)
    """
    with st.container(key=_key(KEY_PANEL, key), gap=None):
        yield


def kpi_card(key: str, label: str, value, unit: str = "", subtitle: str | None = None,
             badge: Html | None = None, meter: float | None = None, meter_mark: float | None = 1.0,
             meter_color: str | None = None, meter_caption: str | None = None, delta: str | None = None,
             footer: tuple[str, str] | None = None, active: bool = False) -> None:
    """Metric card: label + badge, big value with unit, optional meter and footer.

    meter: ratio 0..1.5 (1.0 = threshold); meter_mark draws the threshold line.
    footer: (left label, right value), e.g. ("FORECAST +24H", "21 µg/m³").
    """
    parts = [f'<div class="nb-kpi"><div class="nb-kpi-top"><span class="nb-kpi-label">{_e(label)}</span>'
             f'{_e(badge) if badge else ""}</div>']
    if subtitle:
        parts.append(f'<span class="nb-kpi-sub">{_e(subtitle)}</span>')
    parts.append(f'<div class="nb-kpi-value"><span class="nb-kpi-num">{_e(value)}</span>'
                 f'<span class="nb-kpi-unit">{_e(unit)}</span></div>')
    if meter is not None:
        scale = 1.5
        width = max(0.0, min(meter, scale)) / scale * 100
        fill = meter_color or C.ACCENT
        mark = ""
        if meter_mark is not None:
            mark = f'<span class="nb-meter-mark" style="left:{min(meter_mark, scale) / scale * 100:.2f}%"></span>'
        parts.append(f'<div class="nb-meter"><div class="nb-meter-fill" style="width:{width:.1f}%;background:{fill}">'
                     f"</div>{mark}</div>")
    if meter_caption or delta:
        parts.append(f'<div class="nb-kpi-row"><span>{_e(meter_caption or "")}</span><span>{_e(delta or "")}</span></div>')
    if footer:
        parts.append(f'<div class="nb-kpi-foot"><span style="color:{C.SOFT}">{_e(footer[0])}</span>'
                     f"<b>{_e(footer[1])}</b></div>")
    parts.append("</div>")
    with card(key, active=active):
        html("".join(parts))
