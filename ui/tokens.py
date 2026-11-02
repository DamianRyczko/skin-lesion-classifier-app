"""Design tokens: the single source of truth for the app's look.

Every color, font and size used anywhere in the app comes from here.
Pages and components import C / TAG and never contain hex values.

The app has two themes, so C.* are CSS variables, not colors. theme.py writes
the active palette (LIGHT or DARK) into :root on every run, which is what
makes the switch work without touching the rest of the CSS.

After changing LIGHT, regenerate the Streamlit base theme:
    uv run python .claude/skills/streamlit-neubrutal-ui/scripts/sync_theme.py
"""

LIGHT = {
    "BG": "#F4EFEA",  # app background (warm white)
    "SURFACE": "#FBF9F6",  # cards, panels
    "SURFACE_RAISED": "#FFFFFF",  # selected / emphasised card
    "SIDEBAR": "#EDE5DC",  # theme base only, the app has no sidebar
    "INK": "#2B2B2B",  # text
    "LINE": "#2B2B2B",  # borders
    "SHADOW": "#2B2B2B",  # hard offset shadows
    "MUTED": "#5F5A54",  # secondary text (>= 4.5:1 on BG)
    "SOFT": "#45413C",  # body copy a bit quieter than INK
    "ACCENT": "#6FC2FF",  # selected state, active nav, meters
    "ACCENT_DARK": "#1A6FB0",  # accent for links on the background
    "ON_ACCENT": "#2B2B2B",  # text on ACCENT
    "SELECTED": "#2B2B2B",  # chosen segment
    "ON_SELECTED": "#F4EFEA",
    "HIGHLIGHT": "#FFE14D",  # yellow tags
    "RISK": "#FF9538",  # meters of the high-risk classes
    "OK": "#1F9D55",  # good status dot
    "BAD": "#D64545",  # error dot
    "BAD_TEXT": "#B3261E",  # red text that passes contrast
    "SCRIM": "rgba(43, 43, 43, .38)",
    "TAG_INK": "#2B2B2B",  # text on any tag
    "TAG_INFO": "#CDEBFF",
    "TAG_NEUTRAL": "#F4EFEA",
    "TAG_HIGHLIGHT": "#FFE14D",
    "TAG_WARN": "#FFC48F",
    "TAG_BAD": "#F8C9C9",
}

DARK = {
    "BG": "#0A1230",  # dark blue
    "SURFACE": "#101B45",
    "SURFACE_RAISED": "#16245A",
    "SIDEBAR": "#0D1638",
    "INK": "#E8EEFF",
    "LINE": "#22E3F2",  # neon cyan frames
    "SHADOW": "#FF2E88",  # hard magenta shadows, no glow
    "MUTED": "#A9B6E2",
    "SOFT": "#C9D3F2",
    "ACCENT": "#22E3F2",
    "ACCENT_DARK": "#8FF1FA",
    "ON_ACCENT": "#06102B",
    "SELECTED": "#22E3F2",
    "ON_SELECTED": "#06102B",
    "HIGHLIGHT": "#FFE14D",
    "RISK": "#FF2E88",
    "OK": "#3DF2A0",
    "BAD": "#FF5C7A",
    "BAD_TEXT": "#FF8FA3",
    "SCRIM": "rgba(4, 8, 30, .62)",
    "TAG_INK": "#06102B",
    "TAG_INFO": "#8FF1FA",
    "TAG_NEUTRAL": "#C9D3F2",
    "TAG_HIGHLIGHT": "#FFE14D",
    "TAG_WARN": "#FF8FC0",
    "TAG_BAD": "#FF8FC0",
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
    SIDEBAR = _ref("SIDEBAR")
    INK = _ref("INK")
    LINE = _ref("LINE")
    SHADOW = _ref("SHADOW")
    MUTED = _ref("MUTED")
    SOFT = _ref("SOFT")
    ACCENT = _ref("ACCENT")
    ACCENT_DARK = _ref("ACCENT_DARK")
    ON_ACCENT = _ref("ON_ACCENT")
    SELECTED = _ref("SELECTED")
    ON_SELECTED = _ref("ON_SELECTED")
    HIGHLIGHT = _ref("HIGHLIGHT")
    RISK = _ref("RISK")
    OK = _ref("OK")
    BAD = _ref("BAD")
    BAD_TEXT = _ref("BAD_TEXT")
    SCRIM = _ref("SCRIM")


class TAG:
    """Background colors for tags. Tag text is always TAG_INK."""

    INK = _ref("TAG_INK")
    INFO = _ref("TAG_INFO")
    NEUTRAL = _ref("TAG_NEUTRAL")
    HIGHLIGHT = _ref("TAG_HIGHLIGHT")
    WARN = _ref("TAG_WARN")
    BAD = _ref("TAG_BAD")


class F:
    """Fonts. *_URL are Google Fonts css2 links loaded by the Streamlit theme."""

    BODY = "IBM Plex Sans"
    BODY_URL = "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap"
    MONO = "JetBrains Mono"
    MONO_URL = "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap"
    MONO_STACK = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
    BODY_STACK = "'IBM Plex Sans', system-ui, sans-serif"


class S:
    """Sizes and effects."""

    BORDER = "2px"
    BORDER_THIN = "1px"
    SHADOW = f"6px 6px 0 {C.SHADOW}"  # hard offset shadow, only for the selected/emphasised element
    LABEL_SPACING = "0.1em"  # letter-spacing for uppercase mono labels
    MAX_WIDTH = "1280px"  # main content max width
    NARROW = "900px"  # below this the layout stacks and the panel comes from the bottom
