"""Chart builders on the 'neubrutal' Plotly template.

Always render with show(fig): it passes theme=None, otherwise Streamlit
replaces the template with its own styling.
"""

from typing import Sequence

import plotly.graph_objects as go
import streamlit as st

from .theme import PLOTLY_TEMPLATE, apply_chart_style, register_plotly_template
from .tokens import CHART_BAND, C


def base_figure(height: int = 380, y_title: str | None = None, x_title: str | None = None) -> go.Figure:
    register_plotly_template()
    fig = go.Figure()
    fig.update_layout(template=PLOTLY_TEMPLATE, height=height)
    if y_title:
        fig.update_yaxes(title_text=y_title)
    if x_title:
        fig.update_xaxes(title_text=x_title)
    return fig


def show(fig: go.Figure, key: str | None = None) -> None:
    """Render any Plotly figure (also plotly.express) in the house style."""
    apply_chart_style(fig)
    st.plotly_chart(fig, width="stretch", theme=None, key=key, config={"displaylogo": False})


def add_threshold(fig: go.Figure, y: float, label: str) -> None:
    """Dashed orange horizontal line with a label, e.g. a norm or limit."""
    fig.add_hline(y=y, line=dict(color=C.WARN_DARK, dash="dash", width=1.5),
                  annotation_text=label, annotation_position="top right",
                  annotation_font=dict(color=C.WARN_TEXT, size=11))


def add_now_marker(fig: go.Figure, x, label: str = "TERAZ") -> None:
    """Dotted vertical line at x. Uses add_shape: add_vline with text breaks on datetime axes."""
    fig.add_shape(type="line", x0=x, x1=x, y0=0, y1=1, yref="paper",
                  line=dict(color=C.INK, dash="dot", width=1.5))
    fig.add_annotation(x=x, y=1, yref="paper", text=label, showarrow=False, yanchor="bottom",
                       font=dict(color=C.BG, size=11), bgcolor=C.INK, borderpad=3)


def forecast_chart(history_x: Sequence, history_y: Sequence, forecast_x: Sequence, forecast_y: Sequence,
                   lower: Sequence | None = None, upper: Sequence | None = None,
                   threshold: float | None = None, threshold_label: str = "LIMIT",
                   unit: str = "", height: int = 380, names: tuple[str, str, str] =
                   ("Pomiar", "Prognoza", "Przedział ufności")) -> go.Figure:
    """Measured series (solid ink) + forecast (dashed blue) + optional confidence band and threshold.

    Pass forecast_x starting at the last measured point so the lines join.
    """
    fig = base_figure(height=height, y_title=unit or None)
    hover = "%{y:.1f} " + unit
    fig.add_scatter(x=list(history_x), y=list(history_y), name=names[0], mode="lines",
                    line=dict(color=C.INK, width=2.5), hovertemplate=hover)
    if lower is not None and upper is not None:
        fig.add_scatter(x=list(forecast_x), y=list(upper), mode="lines", line=dict(width=0),
                        showlegend=False, hoverinfo="skip")
        fig.add_scatter(x=list(forecast_x), y=list(lower), name=names[2], mode="lines", line=dict(width=0),
                        fill="tonexty", fillcolor=CHART_BAND, hoverinfo="skip")
    fig.add_scatter(x=list(forecast_x), y=list(forecast_y), name=names[1], mode="lines",
                    line=dict(color=C.ACCENT_DARK, width=2.5, dash="dash"), hovertemplate=hover)
    if threshold is not None:
        add_threshold(fig, threshold, threshold_label)
    if len(forecast_x):
        add_now_marker(fig, list(forecast_x)[0])
    fig.update_yaxes(rangemode="tozero")
    return fig


def bar_chart(x: Sequence, y: Sequence, unit: str = "", height: int = 320, highlight: Sequence[bool] | None = None,
              horizontal: bool = False) -> go.Figure:
    """Flat bars with black outline. highlight: per-bar True -> accent color."""
    fig = base_figure(height=height, y_title=None if horizontal else (unit or None))
    colors = [C.ACCENT if (highlight and highlight[i]) else C.SURFACE_RAISED for i in range(len(x))]
    kwargs = dict(marker=dict(color=colors, line=dict(color=C.INK, width=2)))
    if horizontal:
        fig.add_bar(x=list(y), y=list(x), orientation="h", **kwargs)
    else:
        fig.add_bar(x=list(x), y=list(y), **kwargs)
    fig.update_layout(showlegend=False, bargap=0.35)
    return fig


def line_chart(x: Sequence, series: dict[str, Sequence], unit: str = "", height: int = 340) -> go.Figure:
    """Several plain lines, colors from CHART_COLORS in order."""
    fig = base_figure(height=height, y_title=unit or None)
    for name, ys in series.items():
        fig.add_scatter(x=list(x), y=list(ys), name=name, mode="lines", line=dict(width=2.5))
    return fig
