"""Interactive pieces Streamlit lacks, built on Components v2 (no iframe, so they follow the theme)."""

import json

import streamlit as st

from .components import Html, _e, prob_row

# Square crop box: drag to move, corners to resize, arrow keys to nudge.
# Pointer events cover mouse and touch alike; all geometry is in fractions of
# the image, so the box survives window resizes.
_CROP_JS = """
export default function (component) {
  const { data, parentElement, setStateValue } = component;
  let stage = parentElement.querySelector('.nb-crop');
  if (!stage) {
    stage = document.createElement('div');
    stage.className = 'nb-crop';
    stage.innerHTML = '<img alt="Zdjęcie do wykadrowania"><div class="nb-crop-box" tabindex="0" role="application" ' +
      'aria-label="Kadr. Przeciągnij lub użyj strzałek."><span class="nb-crop-h nw"></span><span class="nb-crop-h ne"></span>' +
      '<span class="nb-crop-h sw"></span><span class="nb-crop-h se"></span></div>';
    parentElement.appendChild(stage);

    const boxEl = stage.querySelector('.nb-crop-box');
    const clamp = (v, lo, hi) => Math.min(Math.max(v, lo), hi);
    const paint = () => {
      const b = stage.box;
      boxEl.style.left = b.x * 100 + '%';
      boxEl.style.top = b.y * 100 + '%';
      boxEl.style.width = b.w * 100 + '%';
      boxEl.style.height = b.h * 100 + '%';
    };
    stage.paint = paint;
    const send = () => stage.setState('box', { ...stage.box });

    let drag = null;
    boxEl.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      boxEl.setPointerCapture(e.pointerId);
      const handle = e.target.classList.contains('nb-crop-h') ? e.target.classList[1] : null;
      drag = { handle, px: e.clientX, py: e.clientY, start: { ...stage.box } };
    });
    boxEl.addEventListener('pointermove', (e) => {
      if (!drag) return;
      const { width, height } = stage.getBoundingClientRect();
      const dx = (e.clientX - drag.px) / width, dy = (e.clientY - drag.py) / height;
      const s = drag.start;
      if (!drag.handle) {
        stage.box = { ...s, x: clamp(s.x + dx, 0, 1 - s.w), y: clamp(s.y + dy, 0, 1 - s.h) };
      } else {
        const west = drag.handle.includes('w'), north = drag.handle.includes('n');
        const grow = Math.max((west ? -dx : dx) * width, (north ? -dy : dy) * height);
        const sidePx = s.w * width;
        const room = Math.min(west ? (s.x + s.w) * width : (1 - s.x) * width,
                              north ? (s.y + s.h) * height : (1 - s.y) * height);
        const side = clamp(sidePx + grow, Math.min(48, room), room);
        const w = side / width, h = side / height;
        stage.box = { x: west ? s.x + s.w - w : s.x, y: north ? s.y + s.h - h : s.y, w, h };
      }
      paint();
    });
    const end = () => { if (drag) { drag = null; send(); } };
    boxEl.addEventListener('pointerup', end);
    boxEl.addEventListener('pointercancel', end);
    boxEl.addEventListener('keydown', (e) => {
      const step = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[e.key];
      if (!step) return;
      e.preventDefault();
      const b = stage.box;
      stage.box = { ...b, x: clamp(b.x + step[0] * 0.01, 0, 1 - b.w), y: clamp(b.y + step[1] * 0.01, 0, 1 - b.h) };
      paint();
      send();
    });
  }
  stage.setState = setStateValue;
  const img = stage.querySelector('img');
  if (img.getAttribute('src') !== data.src) {
    img.setAttribute('src', data.src);
    stage.box = { ...data.box };
    stage.paint();
  }
}
"""

# Rows are real buttons, so keyboard and touch work and each has a role and name.
_ROWS_JS = """
export default function (component) {
  const { data, parentElement, setTriggerValue } = component;
  let rows = parentElement.querySelector('.nb-rows');
  if (!rows) {
    rows = document.createElement('div');
    rows.className = 'nb-rows';
    parentElement.appendChild(rows);
    rows.addEventListener('click', (e) => {
      const button = e.target.closest('button[data-code]');
      if (button) rows.trigger('open', button.dataset.code);
    });
  }
  rows.trigger = setTriggerValue;
  if (rows.dataset.signature !== data.signature) {
    rows.dataset.signature = data.signature;
    rows.innerHTML = data.html;
  }
}
"""

_cropper = st.components.v2.component("skin_lesion_cropper", js=_CROP_JS, isolate_styles=False)
_rows = st.components.v2.component("skin_lesion_rows", js=_ROWS_JS, isolate_styles=False)


def cropper(src: str, box: dict[str, float], key: str) -> dict[str, float]:
    """Square crop box over a preview image. Returns the box as fractions of width and height."""
    result = _cropper(key=key, data={"src": src, "box": box}, default={"box": box}, on_box_change=lambda: None)
    return result.box or box


def prob_rows(rows: list[dict], key: str) -> str | None:
    """Clickable probability bars. Returns the class code clicked in this run, if any."""
    markup = Html("".join(prob_row(**row) for row in rows))
    signature = json.dumps([[row["code"], row["pct"], row["top"], row["selected"]] for row in rows])
    result = _rows(key=key, data={"html": _e(markup), "signature": signature}, on_open_change=lambda: None)
    return result.open
