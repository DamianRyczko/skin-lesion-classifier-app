"""Colours of both themes. theme.py writes the active one as --nb-* CSS variables, so C.* are var() references.

.streamlit/config.toml repeats the LIGHT colours for Streamlit's own base theme: change both together.
"""

LIGHT = {
    "BG": "#F4EFEA",  # app background (warm white)
    "SURFACE": "#FBF9F6",  # cards, panels
    "SURFACE_RAISED": "#FFFFFF",  # selected / emphasised card
    "INK": "#2B2B2B",  # text
    "LINE": "#2B2B2B",  # borders
    "SHADOW": "#2B2B2B",  # hard offset shadows
    "MUTED": "#5F5A54",  # secondary text (>= 4.5:1 on BG)
    "SOFT": "#45413C",  # body copy a bit quieter than INK
    "ACCENT": "#6FC2FF",  # selected state, active nav, meters
    "ON_ACCENT": "#2B2B2B",  # text on ACCENT
    "SELECTED": "#2B2B2B",  # chosen segment
    "ON_SELECTED": "#F4EFEA",
    "RISK": "#FF9538",  # meters of the high-risk classes
    "OK": "#1F9D55",  # good status dot
    "SCRIM": "rgba(43, 43, 43, .38)",
    "TAG_INK": "#2B2B2B",  # text on any tag
    "TAG_INFO": "#CDEBFF",
    "TAG_HIGHLIGHT": "#FFE14D",
    "TAG_WARN": "#FFC48F",
}

DARK = {
    "BG": "#0A1230",  # dark blue
    "SURFACE": "#101B45",
    "SURFACE_RAISED": "#16245A",
    "INK": "#E8EEFF",
    "LINE": "#22E3F2",  # neon cyan frames
    "SHADOW": "#FF2E88",  # hard magenta shadows, no glow
    "MUTED": "#A9B6E2",
    "SOFT": "#C9D3F2",
    "ACCENT": "#22E3F2",
    "ON_ACCENT": "#06102B",
    "SELECTED": "#22E3F2",
    "ON_SELECTED": "#06102B",
    "RISK": "#FF2E88",
    "OK": "#3DF2A0",
    "SCRIM": "rgba(4, 8, 30, .62)",
    "TAG_INK": "#06102B",
    "TAG_INFO": "#8FF1FA",
    "TAG_HIGHLIGHT": "#FFE14D",
    "TAG_WARN": "#FF8FC0",
}

# XAI heatmap, low to high attention. Same in both themes: it sits on the photo.
XAI_SCALE = ("#1B2A8C", "#1E8CD8", "#22E3C8", "#FFE14D", "#FF9538", "#E5243B")

THEMES = {"light": LIGHT, "dark": DARK}
THEME_LABELS = {"light": "Jasny", "dark": "Cyberpunk"}


def css_var(name: str) -> str:
    return "--nb-" + name.lower().replace("_", "-")


def _ref(name: str) -> str:
    return f"var({css_var(name)})"


class C:
    """Colors, resolved in the browser from the active palette."""

    BG = _ref("BG")
    SURFACE = _ref("SURFACE")
    SURFACE_RAISED = _ref("SURFACE_RAISED")
    INK = _ref("INK")
    LINE = _ref("LINE")
    SHADOW = _ref("SHADOW")
    MUTED = _ref("MUTED")
    SOFT = _ref("SOFT")
    ACCENT = _ref("ACCENT")
    ON_ACCENT = _ref("ON_ACCENT")
    SELECTED = _ref("SELECTED")
    ON_SELECTED = _ref("ON_SELECTED")
    RISK = _ref("RISK")
    OK = _ref("OK")
    SCRIM = _ref("SCRIM")


class TAG:
    """Background colors for tags. Tag text is always TAG_INK."""

    INK = _ref("TAG_INK")
    INFO = _ref("TAG_INFO")
    WARN = _ref("TAG_WARN")
