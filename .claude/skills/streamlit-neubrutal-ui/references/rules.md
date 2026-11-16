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

- `ui/tokens.py`: colors (in `LIGHT` and `DARK`) and font names. Change the look here, then run `scripts/sync_theme.py`.
- `ui/styles/*.css`: all CSS, one file per area, loaded in name order (the number prefix is the cascade
  order). Sizes and font stacks are at the top of `01-base.css`. Each file ends with its own narrow-layout
  (`max-width: 900px`) rules. The only place with selectors for Streamlit internals (`data-testid`,
  `st-key-*`); if a Streamlit upgrade changes the DOM, fix selectors here. Current selectors were checked
  against Streamlit 1.66. Colors are `var(--nb-*)`, never hex. No less-than sign anywhere, not even in a
  comment (DOMPurify drops the whole block).
- `ui/theme.py`: puts `ui/styles/` on the page with the active palette as `--nb-*` variables.
- `ui/components.py`: all HTML. Components escape text (`_e`) and return `Html` for fragments.
- `ui/widgets.py`: Components v2 pieces (cropper, probability rows). No iframe, so they follow the theme.
  Their JavaScript is in `ui/js/`.
- `ui/assets.py`: images as data URIs.
- Panel styling works through container keys: `st.container(key="nbpanel_...")` gets the CSS class
  `st-key-nbpanel_...`. Use `ui.panel()` rather than writing these keys by hand.

## Known Streamlit quirks

- Horizontal containers turn into columns below 640px; `ui/styles/01-base.css` keeps the app's own as rows.
- `streamlit-cropper` overflows narrow screens and ignores touch; that is why `ui/widgets.py` has its own.
- AppTest loses state after a callback changes query params. Test the theme click in `tests/e2e/`.
- Google Fonts are loaded by the theme from the internet; offline the app falls back to system mono/sans.
- After upgrading Streamlit: run the app in both themes and `mise run e2e`, fix `ui/styles/` if needed,
  update the pin in `pyproject.toml`.

## Review checklist (before handing over)

- [ ] `check_style.py` passes.
- [ ] App starts headless, no tracebacks in the log.
- [ ] One `page_header` per page.
- [ ] Every status has a text label; no text in accent colors.
- [ ] New components documented in `components.md`.
