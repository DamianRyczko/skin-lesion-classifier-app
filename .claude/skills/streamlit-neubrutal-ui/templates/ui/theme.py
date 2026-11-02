"""Global styling: page setup, CSS and the Plotly template.

This is the ONLY file that contains CSS selectors for Streamlit internals
(data-testid / st-key-* classes). If a Streamlit upgrade breaks a rule,
it is fixed here and nowhere else.
"""

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

from .tokens import CHART_COLORS, CHART_GRID, C, F, S, TAG

PLOTLY_TEMPLATE = "neubrutal"

# Key prefixes recognised by the CSS below. Use them through components.py.
KEY_CARD = "nbcard_"           # bordered card
KEY_CARD_ACTIVE = "nbcard_active_"  # bordered card with hard shadow
KEY_PANEL = "nbpanel_"         # bordered panel for charts/tables, no padding change

_CSS = f"""
<style>
/* ---------- layout ---------- */
[data-testid="stMainBlockContainer"], .block-container {{
  padding-top: 2.25rem; padding-bottom: 3rem; max-width: {S.MAX_WIDTH};
}}
h1, h2, h3 {{ text-transform: uppercase; letter-spacing: -0.01em; }}
h1 {{ font-weight: 500 !important; }}

/* ---------- sidebar navigation ---------- */
[data-testid="stSidebarNavLink"] [data-testid="stMarkdownContainer"] p,
[data-testid="stPageLink-NavLink"] [data-testid="stMarkdownContainer"] p {{
  font-family: {F.MONO_STACK}; text-transform: uppercase; font-size: 13px; letter-spacing: 0.04em;
}}
[data-testid="stSidebarNavLink"],
[data-testid="stPageLink-NavLink"] {{ border: {S.BORDER} solid transparent; border-radius: 0 !important; }}
[data-testid="stSidebarNavLink"][aria-current="page"],
[data-testid="stPageLink-NavLink"][aria-current="page"] {{
  background: {C.ACCENT} !important; border-color: {C.INK};
}}
[data-testid="stSidebarNavLink"][aria-current="page"] p {{ font-weight: 700; }}

/* ---------- buttons and segmented controls ---------- */
[data-testid^="stBaseButton"] p,
[data-testid="stButtonGroup"] button p {{
  font-family: {F.MONO_STACK}; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 700;
}}
[data-testid^="stBaseButton"] {{ border-width: {S.BORDER} !important; }}
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primary"] p {{ color: {C.INK} !important; }}
[data-testid="stBaseButton-primary"] {{ border-color: {C.INK} !important; }}
[data-testid="stButtonGroup"] button {{ border-color: {C.INK} !important; border-width: {S.BORDER} !important; }}
[data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stButtonGroup"] button[aria-checked="true"] p {{
  background: {C.INK} !important; color: {C.BG} !important;
}}

/* ---------- widget labels and metrics ---------- */
[data-testid="stWidgetLabel"] p,
[data-testid="stMetricLabel"] p {{
  font-family: {F.MONO_STACK}; text-transform: uppercase; letter-spacing: {S.LABEL_SPACING}; font-size: 0.72rem;
  color: {C.MUTED};
}}
[data-testid="stMetricValue"] {{ font-family: {F.MONO_STACK}; }}

/* ---------- cards and panels (keys set by components.py) ---------- */
[class*="st-key-{KEY_CARD}"], [class*="st-key-{KEY_PANEL}"] {{
  border: {S.BORDER} solid {C.INK} !important; border-radius: 0 !important; background: {C.SURFACE};
}}
[class*="st-key-{KEY_CARD}"] {{ padding: 1.1rem 1.2rem; }}
[class*="st-key-{KEY_CARD_ACTIVE}"] {{ box-shadow: {S.SHADOW}; background: {C.SURFACE_RAISED}; }}

/* ---------- component classes (nb-*) ---------- */
.nb-mono {{ font-family: {F.MONO_STACK}; }}
.nb-eyebrow {{ font-family: {F.MONO_STACK}; font-size: 12px; letter-spacing: {S.LABEL_SPACING}; color: {C.MUTED};
  text-transform: uppercase; }}
.nb-header {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 16px 24px;
  margin-bottom: 0.5rem; }}
.nb-header h1 {{ margin: 0.4rem 0 0.6rem; padding: 0; font-family: {F.MONO_STACK}; font-size: 2.6rem; line-height: 1.08;
  font-weight: 500; text-transform: uppercase; letter-spacing: -0.01em; color: {C.INK}; }}
.nb-header p {{ margin: 0; max-width: 720px; font-size: 1.05rem; line-height: 1.55; color: {C.SOFT}; }}
.nb-header-side {{ display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }}
.nb-label {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; margin: 1.5rem 0 0.25rem;
  font-family: {F.MONO_STACK}; font-size: 13px; font-weight: 700; letter-spacing: {S.LABEL_SPACING}; color: {C.INK};
  text-transform: uppercase; }}
.nb-label-line {{ flex: 1 1 60px; height: 1px; background: {C.INK}; opacity: 0.4; }}
.nb-label-meta {{ font-weight: 400; font-size: 12px; color: {C.MUTED}; }}
.nb-tag {{ display: inline-block; font-family: {F.MONO_STACK}; font-size: 11px; font-weight: 700; letter-spacing: 0.04em;
  padding: 2px 6px; border: {S.BORDER_THIN} solid {C.INK}; color: {C.INK}; text-transform: uppercase;
  white-space: nowrap; line-height: 1.5; }}
.nb-tag-dark {{ background: {TAG.DARK}; color: {C.BG}; }}
.nb-status {{ display: inline-flex; align-items: center; gap: 7px; font-family: {F.MONO_STACK}; font-size: 12px;
  font-weight: 700; white-space: nowrap; }}
.nb-dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; flex: none; }}
.nb-bar {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px 20px; padding: 10px 16px;
  border: {S.BORDER} solid {C.INK}; background: {C.SURFACE}; font-family: {F.MONO_STACK}; font-size: 12px; color: {C.SOFT}; }}
.nb-bar-end {{ margin-left: auto; }}
.nb-bar-inside {{ border: none; border-top: {S.BORDER} solid {C.INK}; }}
.nb-kpi {{ display: flex; flex-direction: column; gap: 12px; color: {C.INK}; }}
.nb-kpi-top {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; }}
.nb-kpi-label {{ font-family: {F.MONO_STACK}; font-size: 20px; font-weight: 700; }}
.nb-kpi-sub {{ font-size: 13px; color: {C.SOFT}; }}
.nb-kpi-value {{ display: flex; align-items: baseline; gap: 8px; }}
.nb-kpi-num {{ font-family: {F.MONO_STACK}; font-size: 48px; font-weight: 500; line-height: 1; }}
.nb-kpi-unit {{ font-family: {F.MONO_STACK}; font-size: 13px; color: {C.SOFT}; }}
.nb-meter {{ position: relative; height: 10px; box-sizing: border-box; border: 1.5px solid {C.INK}; background: {C.BG}; }}
.nb-meter-fill {{ height: 100%; }}
.nb-meter-mark {{ position: absolute; top: -5px; bottom: -5px; width: 2px; background: {C.INK}; }}
.nb-kpi-row {{ display: flex; justify-content: space-between; gap: 8px; font-family: {F.MONO_STACK}; font-size: 11px;
  color: {C.SOFT}; }}
.nb-kpi-foot {{ display: flex; justify-content: space-between; gap: 8px; padding-top: 10px;
  border-top: {S.BORDER_THIN} dashed {C.INK}; font-family: {F.MONO_STACK}; font-size: 12px; }}
.nb-kpi-foot b {{ color: {C.INK}; }}
.nb-table-wrap {{ overflow-x: auto; border: {S.BORDER} solid {C.INK}; background: {C.SURFACE}; }}
.nb-table {{ width: 100%; border-collapse: collapse; font-size: 14px; color: {C.INK}; }}
.nb-table th {{ text-align: left; padding: 12px 16px; border-bottom: {S.BORDER} solid {C.INK};
  font-family: {F.MONO_STACK}; font-size: 11px; font-weight: 500; letter-spacing: 0.08em; color: {C.MUTED};
  text-transform: uppercase; white-space: nowrap; }}
.nb-table td {{ padding: 12px 16px; border-bottom: 1px solid rgba(43, 43, 43, 0.18); vertical-align: middle; }}
.nb-table tr:last-child td {{ border-bottom: none; }}
.nb-tags {{ display: flex; flex-wrap: wrap; gap: 4px; }}
.nb-stat {{ display: flex; flex-direction: column; gap: 6px; padding: 18px 20px; border: {S.BORDER} solid {C.INK}; }}
.nb-stat-label {{ font-family: {F.MONO_STACK}; font-size: 11px; letter-spacing: {S.LABEL_SPACING}; text-transform: uppercase; }}
.nb-stat-value {{ font-family: {F.MONO_STACK}; font-size: 44px; font-weight: 500; line-height: 1; }}
.nb-box {{ display: flex; flex-direction: column; gap: 4px; padding: 14px; border: {S.BORDER} solid {C.INK};
  background: {C.BG}; font-size: 13px; color: {C.SOFT}; }}
.nb-box b {{ color: {C.INK}; font-size: 14px; }}
.nb-placeholder {{ display: flex; align-items: center; justify-content: center; min-height: 140px; padding: 20px;
  border: {S.BORDER} dashed {C.INK}; font-family: {F.MONO_STACK}; font-size: 12px; color: {C.SOFT}; text-align: center; }}
</style>
"""


_AXIS_X = dict(showgrid=False, linecolor=C.INK, linewidth=2, ticks="outside", tickcolor=C.INK, zeroline=False,
               tickfont=dict(family=F.MONO_STACK, color=C.SOFT, size=11),
               title=dict(font=dict(family=F.MONO_STACK, size=11, color=C.MUTED)))
_AXIS_Y = dict(showgrid=True, gridcolor=CHART_GRID, linecolor=C.INK, linewidth=2, zeroline=False,
               tickfont=dict(family=F.MONO_STACK, color=C.SOFT, size=11),
               title=dict(font=dict(family=F.MONO_STACK, size=11, color=C.MUTED)))
_LAYOUT = dict(
    font=dict(family=F.MONO_STACK, color=C.INK, size=12),
    paper_bgcolor=C.SURFACE,
    plot_bgcolor=C.SURFACE,
    colorway=CHART_COLORS,
    hoverlabel=dict(bgcolor=C.INK, bordercolor=C.INK, font=dict(color=C.BG, family=F.MONO_STACK)),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, traceorder="normal",
                font=dict(family=F.MONO_STACK, size=11, color=C.INK)),
    margin=dict(l=56, r=20, t=48, b=44),
    hovermode="x unified",
)


def register_plotly_template() -> None:
    """Register the 'neubrutal' Plotly template (idempotent), e.g. for plotly.express(template="neubrutal")."""
    if PLOTLY_TEMPLATE in pio.templates:
        return
    pio.templates[PLOTLY_TEMPLATE] = go.layout.Template(layout=dict(_LAYOUT, xaxis=_AXIS_X, yaxis=_AXIS_Y))


def _fill(obj, values: dict) -> None:
    """Set values only where the figure has nothing explicit, recursing into nested objects."""
    for key, value in values.items():
        current = obj[key]
        if isinstance(value, dict):
            _fill(current, value)
        elif current is None:
            obj[key] = value


def apply_chart_style(fig: go.Figure) -> go.Figure:
    """Write the style straight into fig.layout.

    Needed because the Streamlit frontend fills colors/fonts from the app
    theme into any layout key left empty, which beats values coming from a
    template. Explicit settings already on the figure are kept.
    """
    register_plotly_template()
    fig.update_layout(template=PLOTLY_TEMPLATE)
    _fill(fig.layout, _LAYOUT)
    fig.for_each_xaxis(lambda ax: _fill(ax, _AXIS_X))
    fig.for_each_yaxis(lambda ax: _fill(ax, _AXIS_Y))
    return fig


def inject_css() -> None:
    st.html(_CSS)


def setup_page(title: str, icon: str | None = None, sidebar: str = "expanded") -> None:
    """Call once, as the first Streamlit call of the entry script (app.py).

    With st.navigation, call it in app.py before pg.run(); pages then only
    import components, they do not call setup_page again.
    """
    st.set_page_config(page_title=title, page_icon=icon, layout="wide", initial_sidebar_state=sidebar)
    inject_css()
    register_plotly_template()
