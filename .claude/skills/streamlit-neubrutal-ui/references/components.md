# Component catalogue

Imports used everywhere:

```python
import streamlit as st
from ui import components as ui
from ui import widgets
from ui.theme import setup_page          # only in app.py
from ui.tokens import C, TAG             # only when a component takes a color
```

Text arguments are HTML-escaped. Functions marked **→ Html** return a fragment you can pass into other
components; render a lone fragment with `ui.html(fragment)`.

When you add a component: put it in `ui/components.py` and add it here. Only keep what a page uses.

## Page

| Call | What |
|---|---|
| `setup_page(title, theme, icon=None)` | Page config + global CSS + active palette. Once, first, in `app.py`. |
| `ui.skyline(theme)` / `ui.brand(name, theme)` | Cat city strip and logo of the top bar. |
| `ui.page_header(title, side=[...])` | Big uppercase mono H1. One per page. |
| `ui.disclaimer(title, text)` | Dashed bar with a warning tag. |

## Structure

| Call | What |
|---|---|
| `with ui.panel(key):` | Frame without padding. Inside, use containers keyed `nbphead_*` (header row), `nbpbody_*` (padded body), `nbpfoot_*` (footer row), all with `horizontal=True` except the body. |
| `with ui.split(key, [5, 6]) as (left, right):` | Columns that stack below 900px instead of Streamlit's 640px. |

## Inline pieces → Html

| Call | What |
|---|---|
| `ui.tag(text, kind)` | kinds: `info`, `warn`. |
| `ui.status(label)` | Green dot + label. |
| `ui.mono(text)` | Monospace span. |
| `ui.bold(text)` | Bold span, e.g. inside `ui.note`. |
| `ui.steps(labels, current)` | Step tags, current one in yellow. |
| `ui.join(*parts, sep=" ")` | Several fragments in one line. |

## Text blocks

`ui.label(text)`, `ui.note(text)`, `ui.hint(text)`, `ui.tips(items)` (paw bullets),
`ui.banner(title, text, warn)`, `ui.status_bar(*parts, end=None)` (last element of a panel).

## Result

| Call | What |
|---|---|
| `widgets.prob_rows(rows, key)` | Clickable bars, real buttons. Returns the code clicked in this run. |
| `widgets.cropper(src, box, key)` | Square crop for mouse, touch and keyboard. Box in fractions of the image. |
| `ui.class_detail(...)` | Body of the slide-out panel, with the class photo from `assets/samples/<code>.jpg`. |
| `ui.xai_legend(low, high)` | Heatmap scale. |
| `ui.Loader()` then `.update(title, stage, done, total)` | Walking cat, one block per step. |
| `ui.pct(value)` | Polish percent: `78%`, `1,5%`. |

The slide-out panel is `st.dialog(title, position="right")`; `ui/styles/04-drawer.css` turns it into a bottom sheet below 900px.

## Controls (native, styled by the kit)

- Single choice among few options: `st.segmented_control(label, options, format_func=..., key=..., required=True)`.
- Buttons: `st.button(..., type="primary")` = ACCENT fill; secondary = outlined.
- `st.toggle`, `st.slider`, `st.file_uploader` are styled. Any other native widget needs rules in `ui/styles/02-controls.css` first.
