---
name: streamlit-neubrutal-ui
description: Use for any UI work in this Streamlit project (new page, layout, component, chart, restyle). Sets up the project's soft neo-brutalist UI kit (ui/ package) on first use and keeps every page consistent with it.
---

# Streamlit UI kit: soft neo-brutalist style

This project's frontend is Streamlit with a shared UI kit in `ui/`. The look:
warm off-white or dark blue background, 2px borders, square corners, uppercase
monospace labels, flat pastel accents, a hard offset shadow on the selected
element. The person who owns this project is a backend developer: give them
working pages built from the kit, not CSS lessons. Reply in their language.

Everything below assumes the current directory is the project root.
`SKILL` = `.claude/skills/streamlit-neubrutal-ui`.

## 0. The kit is installed

`ui/` is the project's own and has been extended; read `ui/components.py` and `ui/tokens.py` before
building, and prefer what is there. Dependencies are managed with uv (`pyproject.toml`). Do not use
`scripts/bootstrap.py` or pip here.

## 1. Building or changing pages

1. Read `SKILL/references/components.md` (what exists and how to call it)
   and, for anything non-trivial, `SKILL/references/rules.md`.
2. Recommended app structure for anything with more than one page:
   ```
   app.py            # setup_page(...), top bar, st.navigation([...]).run()
   pages/<name>.py   # one file per page, only layout + calls into core/ and ui/
   core/, model.py   # logic and models - no Streamlit layout here
   ui/               # the kit
   ```
   `setup_page()` is called once, in `app.py`, before `nav.run()`. Pages do not
   call it again.
3. Compose pages from `ui.components` and native widgets
   (`st.segmented_control`, `st.columns`, inputs). Use
   `pages/analyze.py` as the reference for patterns.
4. **Hard rules** (the linter enforces them outside `ui/`):
   - no hex colors in pages: use `C.*` / `TAG.*` from `ui.tokens` (CSS variables, so both themes work);
   - no `st.markdown(..., unsafe_allow_html=True)`, `st.html`, `<style>`:
     use or add a component;
   - the app has no Plotly; result bars are `ui.widgets.prob_rows`, not a chart;
   - never target generated classes (`st-emotion-cache-*`, `css-*`);
   - status is never color alone: dot + text label.
5. **Need something the kit does not have?** Do not inline it in the page.
   Add it to `ui/components.py` (new CSS classes go in the matching `ui/styles/*.css` file, colors
   from tokens) and document it in `SKILL/references/components.md`. Then use it in the page.
6. Changing the overall look (a color, a font): edit `ui/tokens.py` only, in BOTH palettes, then
   `uv run python SKILL/scripts/sync_theme.py` to regenerate `.streamlit/config.toml`.
7. Streamlit cannot switch themes from Python. `config.toml` stays on the light palette and
   `ui/styles/` paints every native widget from the variables. A new kind of native widget needs
   rules there, or it stays light in the cyberpunk theme.

## 2. Check before handing over

1. `mise run check` must pass (ruff, mypy and `check_style.py`). A deliberate exception gets `# nb: ignore`
   on that line plus a reason.
2. `mise run test`, and `mise run e2e` for anything visible. Look at screenshots in BOTH themes and at
   390px wide; the layout stacks below 900px.
3. Tell the user which files changed and how to run it. Do not paste whole files into the chat.

## Project context

Domain facts for this project (what the app shows, units, thresholds, data
sources, naming) are in `SKILL/references/project.md`. Read it before writing
copy or choosing what a page displays, and keep it updated when the project
changes.
