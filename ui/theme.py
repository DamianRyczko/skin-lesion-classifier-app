"""Global styling: page setup and CSS.

This is the ONLY file that contains CSS selectors for Streamlit internals
(data-testid / st-key-* classes). If a Streamlit upgrade breaks a rule,
it is fixed here and nowhere else.

Streamlit cannot switch its theme from Python, so .streamlit/config.toml stays
on the light palette and everything visible is painted here from the C.*
variables, native widgets included. A widget that looks light in the dark theme
is missing a rule in this file.
"""

import streamlit as st

from .assets import pixel
from .tokens import TAG, THEMES, C, F, S, css_var

# Key prefixes recognised by the CSS below. Use them through components.py.
KEY_CARD = "nbcard_"  # bordered card
KEY_CARD_ACTIVE = "nbcard_active_"  # bordered card with hard shadow
KEY_PANEL = "nbpanel_"  # bordered panel, no padding change
KEY_SPLIT = "nbsplit_"  # st.columns inside stack below S.NARROW

_CSS = f"""
/* ---------- app frame ---------- */
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
  background: {C.BG} !important; color: {C.INK};
}}
[data-testid="stHeader"], [data-testid="stStatusWidget"], [data-testid="stDecoration"],
[data-testid="stElementToolbar"] {{ display: none !important; }}
[data-testid="stMainBlockContainer"], .block-container {{ padding: 0 !important; max-width: none !important; }}
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stCaptionContainer"], [data-testid="stWidgetLabel"] {{ color: inherit; }}
h1, h2, h3 {{ text-transform: uppercase; letter-spacing: -0.01em; color: {C.INK}; }}
h1 {{ font-weight: 500 !important; }}
.st-key-nbtop {{ gap: 0 !important; }}
/* Horizontal containers: Streamlit turns them into columns on narrow screens, these stay rows. */
.st-key-nbbar, .st-key-nbctrl, [class*="st-key-nbphead_"], [class*="st-key-nbpfoot_"] {{
  flex-direction: row !important; flex-wrap: wrap; align-items: center; }}
.st-key-nbbar > *, .st-key-nbctrl > *, [class*="st-key-nbphead_"] > *, [class*="st-key-nbpfoot_"] > * {{
  flex: 0 0 auto !important; width: auto !important; }}
.st-key-nbbar {{ padding: 8px 28px; background: {C.SURFACE}; border-top: {S.BORDER} solid {C.LINE};
  border-bottom: {S.BORDER} solid {C.LINE}; gap: 8px 20px; justify-content: flex-start; }}
.st-key-nbbar > :last-child {{ margin-left: auto; }}
.st-key-nbpage {{ max-width: {S.MAX_WIDTH}; width: 100%; margin: 0 auto; padding: 24px 28px 36px; box-sizing: border-box; gap: 18px; }}
.nb-px {{ image-rendering: pixelated; }}
.nb-sky {{ display: flex; height: 108px; overflow: hidden; background: {C.BG}; }}
.nb-sky img {{ flex: none; width: 960px; height: 108px; display: block; }}
.nb-brand {{ display: flex; align-items: center; gap: 10px; font-family: {F.MONO_STACK}; font-weight: 700; font-size: 20px;
  letter-spacing: 0.04em; color: {C.INK}; white-space: nowrap; }}
.nb-brand img {{ width: 48px; height: 48px; }}

/* ---------- buttons and segmented controls ---------- */
[data-testid^="stBaseButton"] p, [data-testid="stButtonGroup"] button p {{
  font-family: {F.MONO_STACK}; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 700; font-size: 13px;
}}
[data-testid^="stBaseButton"] {{ min-height: 44px; border: {S.BORDER} solid {C.LINE} !important; border-radius: 0 !important;
  background: {C.SURFACE} !important; color: {C.INK} !important; }}
[data-testid^="stBaseButton"] p {{ color: inherit !important; }}
[data-testid^="stBaseButton"]:hover {{ box-shadow: 3px 3px 0 {C.SHADOW}; }}
[data-testid="stBaseButton-primary"] {{ background: {C.ACCENT} !important; color: {C.ON_ACCENT} !important; }}
[data-testid="stButtonGroup"] button {{ min-height: 44px; border: {S.BORDER} solid {C.LINE} !important; border-radius: 0 !important;
  background: {C.SURFACE} !important; color: {C.INK} !important; padding: 0 16px; }}
[data-testid="stButtonGroup"] button p {{ color: inherit !important; }}
[data-testid="stButtonGroup"] button:hover {{ box-shadow: none; }}
[data-testid="stButtonGroup"] button[aria-checked="true"], [data-testid="stBaseButton-segmented_controlActive"] {{
  background: {C.SELECTED} !important; color: {C.ON_SELECTED} !important;
}}
[data-testid="stButtonGroup"] {{ gap: 0; }}
[data-testid="stButtonGroup"] label[data-baseweb] {{ display: none; }}
:focus-visible {{ outline: 3px solid {C.ACCENT} !important; outline-offset: 2px; }}

/* ---------- widget labels ---------- */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] {{
  font-family: {F.MONO_STACK}; text-transform: uppercase; letter-spacing: {S.LABEL_SPACING}; font-size: 0.72rem;
  color: {C.MUTED};
}}

/* ---------- toggle ---------- */
[data-testid="stCheckbox"] label {{ align-items: center; min-height: 44px; gap: 10px; }}
[data-testid="stCheckbox"] label p {{ font-family: {F.MONO_STACK}; font-size: 13px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.04em; color: {C.INK} !important; }}
[data-testid="stCheckbox"] label > span:first-child + div {{ width: 44px !important; height: 24px !important; border-radius: 0 !important;
  border: {S.BORDER} solid {C.LINE} !important; background: {C.SURFACE} !important; flex: none; box-sizing: border-box; padding: 0 !important;
  display: flex; align-items: center; justify-content: flex-start; }}
[data-testid="stCheckbox"] label > span:first-child + div > div {{ width: 16px !important; height: 16px !important; margin: 0 2px !important;
  border-radius: 0 !important; background: {C.INK} !important; box-shadow: none !important; transform: none !important; left: auto !important; }}
[data-testid="stCheckbox"] label:has(input:checked) > span:first-child + div {{ background: {C.ACCENT} !important; justify-content: flex-end; }}
[data-testid="stCheckbox"] label:has(input:checked) > span:first-child + div > div {{ background: {C.ON_ACCENT} !important; }}

/* ---------- slider ---------- */
[data-testid="stSlider"] [role="slider"] {{ border-radius: 0 !important; background: {C.ACCENT} !important;
  border: {S.BORDER} solid {C.LINE} !important; box-shadow: none !important; }}
[data-testid="stSliderThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {{
  color: {C.SOFT} !important; font-family: {F.MONO_STACK}; }}

/* ---------- file uploader: the whole card is the drop target ---------- */
[data-testid="stFileUploader"] {{ width: 100%; }}
[data-testid="stFileUploaderDropzone"] {{ display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px;
  min-height: 460px; padding: 24px; border: {S.BORDER} dashed {C.LINE} !important; border-radius: 0 !important;
  background: {C.SURFACE} !important; text-align: center; }}
[data-testid="stFileUploaderDropzone"]::before {{ content: ""; width: 192px; height: 300px; flex: none;
  background: var(--nb-cat) center / contain no-repeat; image-rendering: pixelated; }}
[data-testid="stFileUploaderDropzoneInstructions"] {{ order: 1; display: flex; flex-direction: column; gap: 6px; align-items: center; text-align: center; }}
[data-testid="stFileUploaderDropzoneInstructions"] * {{ display: none; }}
[data-testid="stFileUploaderDropzoneInstructions"]::before {{ content: "Przeciągnij zdjęcie tutaj"; font-family: {F.MONO_STACK};
  font-size: 18px; font-weight: 700; text-transform: uppercase; color: {C.INK}; }}
[data-testid="stFileUploaderDropzoneInstructions"]::after {{ content: "JPG, PNG lub WEBP, do 10 MB. Zdjęcie jest przetwarzane tylko w pamięci.";
  font-size: 14px; color: {C.SOFT}; max-width: 44ch; }}
[data-testid="stFileUploaderDropzone"] > span {{ order: 2; }}
[data-testid="stFileUploaderDropzone"] button {{ background: {C.ACCENT} !important; color: {C.ON_ACCENT} !important; }}
[data-testid="stFileUploaderDropzone"] button span:has(> [data-testid="stIconMaterial"]) {{ display: none; }}
[data-testid="stFileUploaderDropzone"] button p {{ font-size: 0 !important; }}
[data-testid="stFileUploaderDropzone"] button p::after {{ content: "Wybierz zdjęcie"; font-size: 13px; }}

/* ---------- drawer: right side, bottom sheet on narrow layouts ---------- */
[data-testid="stDialog"] {{ background: {C.SCRIM} !important; }}
[data-testid="stDialog"] > div {{ background: {C.SURFACE_RAISED} !important; border-radius: 0 !important; border-left: {S.BORDER} solid {C.LINE};
  box-shadow: -8px 0 0 {C.SHADOW} !important; animation: nb-slide-x .24s cubic-bezier(.2, .8, .2, 1); }}
[data-testid="stDialog"] [role="dialog"] {{ background: transparent !important; color: {C.INK}; border-radius: 0 !important; box-shadow: none !important; }}
[data-testid="stDialog"] [role="dialog"] h2 {{ font-family: {F.MONO_STACK}; font-size: 24px; line-height: 1.15; font-weight: 500;
  text-transform: uppercase; color: {C.INK}; }}
[data-testid="stDialog"] [role="dialog"] h2 p {{ font-size: inherit; font-weight: inherit; color: inherit; }}
[data-testid="stDialog"] [role="dialog"] > button {{ color: {C.INK}; }}
@keyframes nb-slide-x {{ from {{ transform: translateX(100%); }} to {{ transform: translateX(0); }} }}
@keyframes nb-slide-y {{ from {{ transform: translateY(100%); }} to {{ transform: translateY(0); }} }}

/* ---------- cards and panels (keys set by components.py) ---------- */
[class*="st-key-{KEY_CARD}"], [class*="st-key-{KEY_PANEL}"] {{
  border: {S.BORDER} solid {C.LINE} !important; border-radius: 0 !important; background: {C.SURFACE};
}}
[class*="st-key-{KEY_CARD}"] {{ padding: 1.1rem 1.2rem; }}
[class*="st-key-{KEY_CARD_ACTIVE}"] {{ box-shadow: {S.SHADOW}; background: {C.SURFACE_RAISED}; }}
[class*="st-key-{KEY_PANEL}"] [data-testid="stImage"] img {{ border-radius: 0; display: block; }}
[class*="st-key-nbphead_"] {{ padding: 6px 16px; border-bottom: {S.BORDER} solid {C.LINE}; justify-content: space-between;
  min-height: 58px; gap: 4px 12px; }}
[class*="st-key-nbpbody_"] {{ padding: 12px 16px; gap: 10px; }}
[class*="st-key-nbpfoot_"] {{ padding: 12px 16px; border-top: {S.BORDER} solid {C.LINE}; gap: 10px; justify-content: flex-start; }}
.st-key-nbctrl {{ gap: 10px 16px; justify-content: flex-start; }}

/* ---------- component classes (nb-*) ---------- */
.nb-mono {{ font-family: {F.MONO_STACK}; }}
.nb-eyebrow {{ font-family: {F.MONO_STACK}; font-size: 12px; letter-spacing: {S.LABEL_SPACING}; color: {C.MUTED};
  text-transform: uppercase; }}
.nb-header {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 14px 24px; }}
.nb-header h1 {{ margin: 4px 0 0; padding: 0; font-family: {F.MONO_STACK}; font-size: 34px; line-height: 1.1;
  font-weight: 500; text-transform: uppercase; letter-spacing: -0.01em; color: {C.INK}; }}
.nb-header p {{ margin: 0; max-width: 720px; font-size: 1.05rem; line-height: 1.55; color: {C.SOFT}; }}
.nb-header-side {{ display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }}
.nb-steps {{ display: flex; flex-wrap: wrap; gap: 6px; list-style: none; margin: 0 !important; padding: 0 !important; }}
.nb-steps li {{ margin: 0; padding: 4px 10px; border: {S.BORDER} solid {C.LINE}; font-family: {F.MONO_STACK}; font-size: 12px; font-weight: 700;
  text-transform: uppercase; color: {C.MUTED}; background: {C.SURFACE}; }}
.nb-steps li.on {{ background: {TAG.HIGHLIGHT}; color: {TAG.INK}; }}
.nb-lbl {{ font-family: {F.MONO_STACK}; font-size: 13px; font-weight: 700; letter-spacing: {S.LABEL_SPACING}; text-transform: uppercase;
  color: {C.INK}; }}
.nb-label {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px; margin: 1.5rem 0 0.25rem;
  font-family: {F.MONO_STACK}; font-size: 13px; font-weight: 700; letter-spacing: {S.LABEL_SPACING}; color: {C.INK};
  text-transform: uppercase; }}
.nb-label-line {{ flex: 1 1 60px; height: 1px; background: {C.LINE}; opacity: 0.4; }}
.nb-label-meta {{ font-weight: 400; font-size: 12px; color: {C.MUTED}; }}
.nb-tag {{ display: inline-block; font-family: {F.MONO_STACK}; font-size: 11px; font-weight: 700; letter-spacing: 0.04em;
  padding: 2px 6px; border: {S.BORDER_THIN} solid {TAG.INK}; color: {TAG.INK}; text-transform: uppercase;
  white-space: nowrap; line-height: 1.5; }}
.nb-status {{ display: inline-flex; align-items: center; gap: 7px; font-family: {F.MONO_STACK}; font-size: 12px;
  font-weight: 700; white-space: nowrap; color: {C.INK}; }}
.nb-dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; flex: none; }}
.nb-bar {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px 18px; padding: 10px 16px;
  border: {S.BORDER} solid {C.LINE}; background: {C.SURFACE}; font-family: {F.MONO_STACK}; font-size: 12px; color: {C.SOFT}; }}
.nb-bar-end {{ margin-left: auto; }}
.nb-bar-inside {{ border: none; border-top: {S.BORDER} solid {C.LINE}; }}
.nb-note {{ font-size: 13px; color: {C.SOFT}; }}
.nb-note b {{ color: {C.INK}; }}
.nb-disc {{ display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: center; padding: 10px 16px; border: {S.BORDER} dashed {C.LINE};
  font-size: 13px; color: {C.SOFT}; }}
.nb-tips {{ display: flex; flex-direction: column; gap: 10px; margin: 0; padding: 14px 16px; list-style: none; font-size: 14px; color: {C.SOFT}; }}
.nb-tips li {{ margin: 0; padding-left: 36px; background: url("{pixel("paw")}") left 1px / 24px 24px no-repeat; image-rendering: pixelated; }}
.nb-card-text {{ display: flex; flex-direction: column; gap: 8px; font-size: 14px; color: {C.SOFT}; }}

/* probability rows */
.nb-rows {{ display: flex; flex-direction: column; gap: 8px; padding: 14px 16px 6px; }}
.nb-row {{ display: flex; flex-direction: column; gap: 6px; width: 100%; padding: 8px 10px; text-align: left; cursor: pointer; font: inherit;
  color: {C.INK}; background: {C.SURFACE}; border: {S.BORDER} solid transparent; border-radius: 0; }}
.nb-row:hover {{ border-color: {C.LINE}; }}
.nb-row.top {{ background: {C.SURFACE_RAISED}; border-color: {C.LINE}; box-shadow: 5px 5px 0 {C.SHADOW}; }}
.nb-row.sel {{ border-color: {C.LINE}; box-shadow: 5px 5px 0 {C.ACCENT}; }}
.nb-rtop {{ display: flex; align-items: baseline; gap: 8px; min-width: 0; }}
.nb-rname {{ flex: 1 1 auto; min-width: 0; font-family: {F.BODY_STACK}; font-size: 15px; font-weight: 500; }}
.nb-rpct {{ flex: none; font-family: {F.MONO_STACK}; font-size: 18px; font-weight: 700; }}
.nb-row.top .nb-rpct {{ font-size: 24px; }}
.nb-meter {{ display: block; height: 12px; border: {S.BORDER} solid {C.LINE}; background: {C.BG}; }}
.nb-fill {{ display: block; height: 100%; background: {C.ACCENT}; }}
.nb-fill.high {{ background: {C.RISK}; }}
.nb-hint {{ padding: 6px 18px 12px; font-size: 13px; color: {C.SOFT}; }}
.nb-banner {{ margin: 0 16px 14px; padding: 12px 14px; border: {S.BORDER} solid {C.LINE}; background: {C.SURFACE_RAISED}; font-size: 14px; color: {C.INK}; }}
.nb-banner b {{ display: block; font-family: {F.MONO_STACK}; font-size: 13px; letter-spacing: 0.02em; text-transform: uppercase; margin-bottom: 2px; }}
.nb-banner.warn {{ background: {TAG.WARN}; color: {TAG.INK}; border-color: {TAG.INK}; }}

/* XAI legend */
.nb-legend {{ display: flex; align-items: center; gap: 8px; font-family: {F.MONO_STACK}; font-size: 11px; color: {C.SOFT}; }}
.nb-scale {{ display: flex; flex: 1 1 auto; height: 12px; border: {S.BORDER} solid {C.LINE}; }}
.nb-scale span {{ flex: 1 1 0; }}

/* cropper */
.nb-crop {{ position: relative; overflow: hidden; line-height: 0; background: {C.BG}; user-select: none; -webkit-user-select: none; }}
.nb-crop img {{ display: block; width: 100%; height: auto; pointer-events: none; }}
.nb-crop-box {{ position: absolute; box-sizing: border-box; border: 2px solid #FFFFFF; cursor: move; touch-action: none; /* nb: fixed over any photo */
  box-shadow: 0 0 0 9999px rgba(8, 10, 26, .55);
  background-image: linear-gradient(rgba(255, 255, 255, .5), rgba(255, 255, 255, .5)), linear-gradient(rgba(255, 255, 255, .5), rgba(255, 255, 255, .5)),
    linear-gradient(rgba(255, 255, 255, .5), rgba(255, 255, 255, .5)), linear-gradient(rgba(255, 255, 255, .5), rgba(255, 255, 255, .5));
  background-size: 1px 100%, 1px 100%, 100% 1px, 100% 1px; background-position: 33.3% 0, 66.6% 0, 0 33.3%, 0 66.6%; background-repeat: no-repeat; }}
.nb-crop-h {{ position: absolute; width: 18px; height: 18px; box-sizing: border-box; background: {TAG.HIGHLIGHT}; border: 2px solid {TAG.INK}; touch-action: none; }}
.nb-crop-h::after {{ content: ""; position: absolute; inset: -13px; }}
.nb-crop-h.nw {{ top: -10px; left: -10px; cursor: nwse-resize; }} .nb-crop-h.ne {{ top: -10px; right: -10px; cursor: nesw-resize; }}
.nb-crop-h.sw {{ bottom: -10px; left: -10px; cursor: nesw-resize; }} .nb-crop-h.se {{ bottom: -10px; right: -10px; cursor: nwse-resize; }}

/* loader */
[class*="st-key-nbload_"] {{ max-width: 620px; width: 100%; margin: 0 auto; padding: 36px 24px; gap: 14px; align-items: center; text-align: center;
  background: {C.SURFACE}; border: {S.BORDER} solid {C.LINE}; box-shadow: {S.SHADOW}; box-sizing: border-box; }}
[class*="st-key-nbload_"] [data-testid="stElementContainer"] {{ width: 100%; }}
.nb-track {{ position: relative; height: 112px; width: 100%; max-width: 480px; margin: 0 auto; overflow: hidden; }}
.nb-walk {{ position: absolute; bottom: 0; left: 0; width: 144px; height: 112px; background: var(--nb-walk) 0 0 / 864px 112px no-repeat;
  image-rendering: pixelated; animation: nb-walk-steps .5s steps(6) infinite, nb-walk-move 4s linear infinite; }}
@keyframes nb-walk-steps {{ from {{ background-position: 0 0; }} to {{ background-position: -864px 0; }} }}
@keyframes nb-walk-move {{ from {{ transform: translateX(-144px); }} to {{ transform: translateX(480px); }} }}
.nb-big {{ font-family: {F.MONO_STACK}; font-size: 18px; font-weight: 700; text-transform: uppercase; color: {C.INK}; }}
.nb-blocks {{ display: grid; grid-template-columns: repeat(16, minmax(0, 1fr)); gap: 4px; width: 100%; max-width: 480px; margin: 0 auto; }}
.nb-blocks span {{ aspect-ratio: 1 / 1; border: {S.BORDER} solid {C.LINE}; background: {C.BG}; box-sizing: border-box; }}
.nb-blocks span.on {{ background: {C.ACCENT}; }}
.nb-stage {{ font-family: {F.MONO_STACK}; font-size: 13px; color: {C.SOFT}; }}

/* panel content */
.nb-score {{ display: flex; flex-wrap: wrap; align-items: center; gap: 10px 14px; color: {C.INK}; }}
.nb-score-num {{ font-family: {F.MONO_STACK}; font-size: 44px; font-weight: 500; line-height: 1; }}
.nb-fig {{ margin: 0; border: {S.BORDER} solid {C.LINE}; background: {C.SURFACE}; }}
.nb-fig img {{ display: block; width: 100%; height: 230px; object-fit: cover; }}
.nb-fig .nb-fig-empty {{ display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; height: 230px; padding: 12px; text-align: center; font-family: {F.MONO_STACK}; font-size: 13px; color: {C.SOFT}; }}
.nb-fig .nb-fig-empty img {{ width: 36px; height: 36px; object-fit: contain; }}
.nb-fig figcaption {{ padding: 6px 10px; font-size: 12px; color: {C.SOFT}; border-top: {S.BORDER} solid {C.LINE}; }}
.nb-sec {{ color: {C.SOFT}; font-size: 15px; }}
.nb-sec h3 {{ margin: 0 0 4px; padding: 0; font-family: {F.MONO_STACK}; font-size: 13px; font-weight: 700; letter-spacing: 0.08em; }}
.nb-advice {{ padding: 12px 14px; border: {S.BORDER} solid {C.LINE}; background: {C.SURFACE}; box-shadow: 4px 4px 0 {C.SHADOW}; }}
.nb-src {{ font-family: {F.MONO_STACK}; font-size: 11px; color: {C.MUTED}; }}

/* ---------- narrow layout ---------- */
@media (max-width: {S.NARROW}) {{
  .st-key-nbbar {{ padding: 8px 16px; }}
  .st-key-nbpage {{ padding: 18px 16px 28px; gap: 14px; }}
  .nb-header h1 {{ font-size: 24px; }}
  .nb-header-side {{ align-items: flex-start; }}
  [class*="st-key-{KEY_SPLIT}"] [data-testid="stHorizontalBlock"] {{ flex-direction: column; }}
  [class*="st-key-{KEY_SPLIT}"] [data-testid="stColumn"] {{ width: 100% !important; flex: 1 1 auto !important; min-width: 100% !important; }}
  [data-testid="stFileUploaderDropzone"] {{ min-height: 340px; }}
  [data-testid="stFileUploaderDropzone"]::before {{ width: 96px; height: 150px; }}
  [data-testid="stDialog"] {{ align-items: flex-end !important; }}
  [data-testid="stDialog"] > div {{ width: 100% !important; max-width: 100% !important; height: auto !important; max-height: 86vh !important;
    border-left: 0; border-top: {S.BORDER} solid {C.LINE}; box-shadow: 0 -8px 0 {C.SHADOW} !important; animation-name: nb-slide-y; }}
  [data-testid="stDialog"] [role="dialog"] {{ width: 100% !important; max-height: 86vh !important; overflow-y: auto; }}
  [data-testid="stDialogResizeHandle"] {{ display: none !important; }}
  .nb-fig img {{ height: 170px; }}
  .nb-fig .nb-fig-empty {{ height: 170px; }}
  .nb-score-num {{ font-size: 36px; }}
}}
@media (prefers-reduced-motion: reduce) {{
  [data-testid="stDialog"] > div, .nb-walk {{ animation: none !important; }}
}}
"""


def _palette(theme: str) -> str:
    colors = "".join(f"{css_var(name)}:{value};" for name, value in THEMES[theme].items())
    sprites = f'--nb-cat:url("{pixel(f"cat-doctor-{theme}")}");--nb-walk:url("{pixel(f"cat-walk-{theme}")}");'
    return ":root{" + colors + sprites + "}"


def inject_css(theme: str) -> None:
    st.html(f"<style>{_palette(theme)}{_CSS}</style>")


def setup_page(title: str, theme: str, icon: str | None = None) -> None:
    """Call once, as the first Streamlit call of the entry script (app.py)."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide", initial_sidebar_state="collapsed")
    inject_css(theme)
