# Style rules and review checklist

## Visual language

- Background `C.BG`, panels/cards `C.SURFACE`. Text `C.INK`, borders `C.LINE`, hard shadows `C.SHADOW`.
- Borders 2px solid ink; thin 1px only inside tags and dashed dividers.
- Square corners everywhere (theme `baseRadius = "none"`). No soft or blurred shadows.
- Hard offset shadow `S.SHADOW` only on the one selected/emphasised element of a group.
- Typography: titles, labels, numbers, tags in JetBrains Mono, UPPERCASE with letter-spacing;
  body text and descriptions in IBM Plex Sans, normal case.
- Accents are flat and few: ACCENT = selected/active/meters, HIGHLIGHT (yellow) = tags, RISK = high-risk
  classes. Never more than 2 accents in one block.
- No gradients, no emoji icons (use `:material/...:` icons in navigation), no rounded pills.

## Contrast and accessibility

- Text only in `INK`, `SOFT`, `MUTED`, `BAD_TEXT`. Text on ACCENT uses `ON_ACCENT`. ACCENT/RISK/HIGHLIGHT
  are fills, not text colors.
- Tag text is always `TAG.INK` on a tag fill.
- Meaning is never color alone: status = dot + label; levels = tag text + meter.

## Code rules (enforced by `scripts/check_style.py` outside `ui/`)

| Code | Rule |
|---|---|
| NB001 | No hex colors in pages; import from `ui.tokens`. |
| NB002 | No `unsafe_allow_html=True`. |
| NB003 | No `st.html` / `components.html` in pages; add a component. |
| NB004 | No `st.plotly_chart`: the app has no charts. |
| NB005 | No `<style>` outside `ui/theme.py`. |
| NB006 | Never select generated classes (`st-emotion-cache-*`, `css-xxxxx`). |
| NB007 | No `st.set_page_config`; use `setup_page` once in `app.py`. |

Silence one line with `# nb: ignore` only with a reason in a comment.

## Where things live

- `ui/tokens.py`: every value (colors in `LIGHT` and `DARK`, fonts, sizes). Change the look here, then run `scripts/sync_theme.py`.
- `ui/theme.py`: the only place with CSS and with selectors for Streamlit internals (`data-testid`,
  `st-key-*`). If a Streamlit upgrade changes the DOM, fix selectors here. Current selectors were
  checked against Streamlit 1.66.
- `ui/components.py`: all HTML. Components escape text (`_e`) and return `Html` for fragments.
- `ui/widgets.py`: Components v2 pieces (cropper, probability rows). No iframe, so they follow the theme.
- `ui/assets.py`: images as data URIs.
- Card/panel styling works through container keys: `st.container(key="nbcard_...")` gets the CSS class
  `st-key-nbcard_...`. Use `ui.card()` / `ui.panel()` rather than writing these keys by hand.

## Known Streamlit quirks

- Horizontal containers turn into columns below 640px; `ui/theme.py` keeps the app's own as rows.
- `streamlit-cropper` overflows narrow screens and ignores touch; that is why `ui/widgets.py` has its own.
- AppTest loses state after a callback changes query params. Test the theme click in `tests/e2e/`.
- Google Fonts are loaded by the theme from the internet; offline the app falls back to system mono/sans.
- After upgrading Streamlit: run `ui_demo.py` in both themes and `mise run e2e`, fix `ui/theme.py` if needed,
  update the pin in `pyproject.toml`.

## Review checklist (before handing over)

- [ ] `check_style.py` passes.
- [ ] App starts headless, no tracebacks in the log.
- [ ] One `page_header` per page; blocks separated by `section_label`.
- [ ] Every status has a text label; no text in accent colors.
- [ ] New components documented in `components.md` and shown in `ui_demo.py`.
- [ ] Sample data clearly tagged (`ui.tag("Dane przykładowe")`) until real data is wired in.
