// Square crop box: drag to move, corners to resize, arrow keys to nudge.
// Pointer events cover mouse and touch; geometry is in fractions of the image, so it survives resizes.
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
