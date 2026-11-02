"""Design tokens: the single source of truth for the app's look.

Every color, font and size used anywhere in the app comes from here.
Pages and components import these names; they never contain hex values.

After changing anything in this file, regenerate the Streamlit theme:
    python .claude/skills/streamlit-neubrutal-ui/scripts/sync_theme.py
"""


class C:
    """Colors."""

    BG = "#F4EFEA"           # app background (warm off-white)
    SURFACE = "#FBF9F6"      # cards, chart panels, tables
    SURFACE_RAISED = "#FFFFFF"  # selected / emphasised card
    SIDEBAR = "#EDE5DC"      # sidebar background
    INK = "#2B2B2B"          # text, borders, hard shadows
    MUTED = "#5F5A54"        # secondary text (>= 4.5:1 on BG)
    SOFT = "#45413C"         # body copy that should be a bit quieter than INK

    ACCENT = "#6FC2FF"       # primary accent: selected state, active nav, bands
    ACCENT_DARK = "#1A6FB0"  # accent for lines/text on light bg (ACCENT is too light)
    HIGHLIGHT = "#FFE14D"    # yellow tags and highlights
    WARN = "#FF9538"         # warnings, bars over threshold
    WARN_DARK = "#D9620F"    # threshold lines
    WARN_TEXT = "#9A430A"    # orange text that passes contrast
    OK = "#1F9D55"           # online / good dot
    BAD = "#D64545"          # offline / error dot
    BAD_TEXT = "#B3261E"     # red text that passes contrast


class TAG:
    """Background colors for tags. Tag text is always C.INK."""

    INFO = "#CDEBFF"
    NEUTRAL = "#F4EFEA"
    HIGHLIGHT = "#FFE14D"
    WARN = "#FFC48F"
    BAD = "#F8C9C9"
    DARK = "#2B2B2B"  # inverted tag: use with light text, see components.tag(kind="dark")


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
    SHADOW = "6px 6px 0 #2B2B2B"   # hard offset shadow, only for the selected/emphasised element
    LABEL_SPACING = "0.1em"        # letter-spacing for uppercase mono labels
    MAX_WIDTH = "1280px"           # main content max width


# Series colors for charts, in order. INK first: measured/actual data is black.
CHART_COLORS = [C.INK, C.ACCENT_DARK, C.WARN_DARK, "#7A5AF8", C.OK]
CHART_BAND = "rgba(111, 194, 255, 0.45)"   # C.ACCENT at 45%: confidence intervals
CHART_GRID = "rgba(43, 43, 43, 0.15)"      # C.INK at 15%
