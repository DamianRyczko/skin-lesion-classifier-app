"""Generate the app's pixel art into assets/pixel/ (deterministic).

Run: uv run python scripts/make_sprites.py

Soft, higher-res pixel art: shapes are lit like 3D forms, then quantised to
small palette ramps with ordered dithering.
"""

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "assets" / "pixel"
OUT.mkdir(parents=True, exist_ok=True)

BAYER = (
    np.array(
        [
            [0, 32, 8, 40, 2, 34, 10, 42],
            [48, 16, 56, 24, 50, 18, 58, 26],
            [12, 44, 4, 36, 14, 46, 6, 38],
            [60, 28, 52, 20, 62, 30, 54, 22],
            [3, 35, 11, 43, 1, 33, 9, 41],
            [51, 19, 59, 27, 49, 17, 57, 25],
            [15, 47, 7, 39, 13, 45, 5, 37],
            [63, 31, 55, 23, 61, 29, 53, 21],
        ]
    )
    / 64.0
)


def hexes(*cs):
    return np.array([[int(c[i : i + 2], 16) for i in (1, 3, 5)] for c in cs], dtype=np.float32)


def bayer(h, w):
    return np.tile(BAYER, (h // 8 + 1, w // 8 + 1))[:h, :w]


def ramp(t, colors, dither=0.9):
    """t in 0..1 to palette ramp with ordered dithering between neighbouring steps."""
    n = len(colors)
    h, w = t.shape
    v = np.clip(t, 0, 1) * (n - 1) + (bayer(h, w) - 0.5) * dither
    return colors[np.clip(np.round(v).astype(int), 0, n - 1)]


def noise(h, w, cell, seed):
    rng = np.random.default_rng(seed)
    gh, gw = max(2, h // cell + 2), max(2, w // cell + 2)
    g = (rng.random((gh, gw)) * 255).astype(np.uint8)
    img = Image.fromarray(g).resize((w, h), Image.Resampling.BICUBIC)
    return np.asarray(img, dtype=np.float32) / 255.0


def fractal(h, w, cell, seed, octaves=4):
    out, amp, tot = np.zeros((h, w), np.float32), 1.0, 0.0
    for i in range(octaves):
        out += noise(h, w, max(1, cell >> i), seed + i) * amp
        tot += amp
        amp *= 0.55
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


def save(rgb, name, alpha=None):
    a = np.clip(rgb, 0, 255).astype(np.uint8)
    if alpha is None:
        Image.fromarray(a, "RGB").save(OUT / name, optimize=True)
    else:
        al = (np.clip(alpha, 0, 1) * 255).astype(np.uint8)
        Image.fromarray(np.dstack([a, al]), "RGBA").save(OUT / name, optimize=True)


SKIN = hexes("#C98F6E", "#D6A07F", "#E0B092", "#E9C0A4", "#F1D0B8", "#F7DFCC")


def skin(h, w, seed):
    t = 0.30 + 0.42 * fractal(h, w, 26, seed) + 0.10 * (noise(h, w, 2, seed + 9) - 0.5)
    return ramp(t, SKIN, 0.85)


LESIONS: dict[str, dict[str, Any]] = {
    "nv": dict(a=0.30, b=0.27, irr=0.10, cols=("#3A2318", "#4F2F1E", "#6A4128", "#855636", "#9C6B47"), bias=0.2, tex=0.12, c=26),
    "mel": dict(
        a=0.36,
        b=0.28,
        irr=0.42,
        cols=("#17121C", "#2B1B22", "#4A2424", "#6E2F27", "#94422F", "#5B6B86", "#A8583C"),
        bias=0.0,
        tex=0.75,
        c=12,
    ),
    "bkl": dict(a=0.34, b=0.25, irr=0.18, cols=("#6E4A2E", "#8A6240", "#A67D55", "#BD966C", "#D0AE86"), bias=0.1, tex=0.55, c=5),
    "bcc": dict(
        a=0.29,
        b=0.26,
        irr=0.16,
        cols=("#B25A62", "#C87476", "#DA9391", "#E9B3AA", "#F4D0C6", "#FAE6DE"),
        bias=0.25,
        tex=0.25,
        c=14,
    ),
    "akiec": dict(
        a=0.38, b=0.30, irr=0.30, cols=("#A24A42", "#BA5E50", "#CE7A68", "#DE9C86", "#EFC9B2", "#F8E8D8"), bias=0.05, tex=0.8, c=4
    ),
    "vasc": dict(
        a=0.27, b=0.25, irr=0.20, cols=("#3D1230", "#5E1838", "#84203F", "#A92E46", "#CB4855", "#E2747A"), bias=0.15, tex=0.5, c=9
    ),
    "df": dict(
        a=0.26, b=0.26, irr=0.09, cols=("#6B3F2C", "#85543D", "#A16F55", "#BC8E74", "#D5B19A", "#E8CFBE"), bias=0.3, tex=0.2, c=16
    ),
}


def lesion(key, n=96, seed=7, skin_px=None):
    p = LESIONS[key]
    y, x = np.mgrid[0:n, 0:n] / n - 0.5
    off = fractal(n, n, max(4, n // 5), seed + 40) - 0.5
    d = np.sqrt((x / p["a"]) ** 2 + (y / p["b"]) ** 2) + off * p["irr"] * 2.1
    if key == "mel":
        d += 0.25 * (x > 0.08) * (y < 0) * (x + 0.1)
    base = skin(n, n, seed) if skin_px is None else skin_px
    cols = hexes(*p["cols"])
    tex = fractal(n, n, max(2, p["c"] * n // 96), seed + 11)
    t = (
        p["bias"]
        + (1 - p["bias"]) * ((1 - np.clip(d, 0, 1)) * (1 - p["tex"]) * 0.2 + tex * (0.3 + p["tex"] * 0.7))
        + np.clip(d - 0.55, 0, 1) * 0.9
    )
    if key == "df":
        t = 0.15 + np.abs(d - 0.05) * 0.9 + (tex - 0.5) * 0.2
    px = ramp(t, cols, 0.8)
    if key == "bcc":
        vessels = np.abs(fractal(n, n, 11, seed + 21) - 0.5) < 0.012
        px[vessels & (d < 0.95)] = hexes("#B2333F")[0]
    if key == "vasc":
        lob = fractal(n, n, 7, seed + 5)
        px[(lob > 0.62) & (d < 0.9)] = hexes("#2A0D22")[0]
    if key == "akiec":
        flakes = fractal(n, n, 3, seed + 3) > 0.72
        px[flakes & (d < 1)] = hexes("#FBF1E6")[0]
    edge = d + (bayer(n, n) - 0.5) * 0.14
    out = base.copy()
    halo = (d < 1.28) & (d >= 1.0)
    out[halo] = (
        out[halo] * (1 - 0.16 * np.clip((1.28 - d[halo]) / 0.28, 0, 1))[..., None]
        + hexes("#C77F66")[0] * (0.16 * np.clip((1.28 - d[halo]) / 0.28, 0, 1))[..., None]
    )
    out[edge < 1] = px[edge < 1]
    return out


# class illustrations
for i, k in enumerate(LESIONS):
    save(lesion(k, 96, 7 + i * 13), f"les-{k}.png")


# ---------------------------------------------------------------- cats
GINGER = hexes("#9C4A1F", "#C4662B", "#E08A3C", "#F2A95C", "#F9C583", "#FDE0B0")
CREAM = hexes("#D9B48C", "#EBCFA8", "#F7E6CC", "#FFF6E6")
PINK = hexes("#E98A98", "#F7B2B8", "#FFD3D3")
METAL = hexes("#1E2B5C", "#31468A", "#4E6DB5", "#7AA0D6", "#AEC9EA", "#DCEBFA", "#FFFFFF")
HANDLE = hexes("#7A2F4A", "#A8405A", "#D65D62", "#EF8A63", "#FFB98A")
OUTLINE = hexes("#3A1F2B")[0]
EYE = hexes("#1B1630")[0]
WHITE = hexes("#FFFFFF")[0]
WHISKER = hexes("#B98A78")[0]


class Canvas:
    def __init__(self, h, w):
        self.h, self.w = h, w
        self.rgb = np.zeros((h, w, 3), np.float32)
        self.a = np.zeros((h, w), np.float32)
        self.y, self.x = np.mgrid[0:h, 0:w].astype(np.float32)

    def paint(self, mask, colors):
        self.rgb[mask] = colors[mask] if colors.ndim == 3 else colors
        self.a[mask] = 1

    def blob(self, cx, cy, rx, ry, ramp_colors=GINGER, gain=1.0):
        """Ellipse lit like a sphere from the top-left."""
        nx, ny = (self.x - cx) / rx, (self.y - cy) / ry
        d = nx**2 + ny**2
        mask = d < 1
        nz = np.sqrt(np.clip(1 - d, 0, 1))
        t = np.clip((-0.42 * nx - 0.58 * ny + 0.7 * nz) * 0.62 + 0.34, 0, 1) * gain
        self.paint(mask, ramp(t, ramp_colors, 0.75))
        return mask

    def tri(self, a, b, c, colors):
        def side(p, q):
            return (q[0] - p[0]) * (self.y - p[1]) - (q[1] - p[1]) * (self.x - p[0])

        s = [side(a, b), side(b, c), side(c, a)]
        mask = (s[0] >= 0) & (s[1] >= 0) & (s[2] >= 0) | (s[0] <= 0) & (s[1] <= 0) & (s[2] <= 0)
        shade = np.clip(0.72 - (self.y - min(a[1], b[1], c[1])) * 0.012 - (self.x - self.w / 2) * 0.004, 0, 1)
        self.paint(mask, ramp(shade, colors, 0.7) if colors.ndim == 2 and len(colors) > 1 else colors[0])

    def tube(self, points, r, colors, n=90):
        """Round tube along a polyline-free quadratic bezier of three points."""
        (x0, y0), (x1, y1), (x2, y2) = points
        for t in np.linspace(0, 1, n):
            px = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t**2 * x2
            py = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t**2 * y2
            self.blob(px, py, r, r, colors)

    def line(self, x0, y0, x1, y1, color):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for t in np.linspace(0, 1, n):
            self.rgb[int(y0 + t * (y1 - y0)), int(x0 + t * (x1 - x0))] = color
            self.a[int(y0 + t * (y1 - y0)), int(x0 + t * (x1 - x0))] = 1

    def outline(self, color=OUTLINE):
        grown = np.asarray(Image.fromarray((self.a > 0).astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(3))) > 0
        edge = grown & (self.a == 0)
        self.rgb[edge] = color
        self.a[edge] = 1


class Figure(Canvas):
    """Clean pixel art: flat shapes with a one-pixel outline and two-step shading, no dithering."""

    def ellipse(self, cx, cy, rx, ry):
        return ((self.x - cx) / rx) ** 2 + ((self.y - cy) / ry) ** 2 < 1

    def poly(self, *points):
        img = Image.new("1", (self.w, self.h))
        ImageDraw.Draw(img).polygon(points, fill=1)
        return np.asarray(img)

    def limb(self, x0, y0, x1, y1, r):
        dx, dy = x1 - x0, y1 - y0
        t = np.clip(((self.x - x0) * dx + (self.y - y0) * dy) / (dx * dx + dy * dy), 0, 1)
        return np.hypot(self.x - x0 - t * dx, self.y - y0 - t * dy) < r

    def part(self, mask, colors, depth=2):
        """colors: shadow, base, light. Light falls from the top left, as on the other sprites."""
        grown = mask | np.roll(mask, 1, 0) | np.roll(mask, -1, 0) | np.roll(mask, 1, 1) | np.roll(mask, -1, 1)
        edge = grown & ~mask
        self.rgb[edge], self.a[edge] = OUTLINE, 1
        self.paint(mask, colors[1])
        self.rgb[mask & ~np.roll(mask, (1, 1), (0, 1))] = colors[2]
        self.rgb[mask & ~np.roll(mask, (-depth, -depth), (0, 1))] = colors[0]

    def ink(self, x0, y0, x1, y1, color=OUTLINE, width=1):
        for offset in range(width):
            self.line(x0 + offset, y0, x1 + offset, y1, color)

    def stamp(self, layer, angle, pivot, behind=False):
        """Paints another figure over this one, or behind it, turned around pivot."""
        rgba = np.dstack([layer.rgb, layer.a * 255]).astype(np.uint8)
        turned = Image.fromarray(rgba, "RGBA").rotate(angle, Image.Resampling.NEAREST, center=pivot)
        px = np.asarray(turned)
        mask = (px[..., 3] > 0) & (self.a == 0 if behind else True)
        self.rgb[mask], self.a[mask] = px[mask][:, :3], 1


FUR = GINGER[[1, 3, 4]]
FUR_PALE = CREAM[[0, 2, 3]]
COAT = hexes("#AEBBD4", "#E4EAF3", "#FFFFFF")
SCRUBS = hexes("#2A5C86", "#3F86B3", "#6FB4D6")
NEON = hexes("#0E8FA0", "#22E3F2", "#D6FBFF")
HOT = hexes("#5A1450", "#B0207A", "#FF2E88")
GEAR = hexes("#1B1E52", "#3A3F9A", "#7C84E0")
NIGHT_VISION = hexes("#0E7A45", "#39FF88", "#D9FFE9")
DOCTOR = dict(
    coat=COAT,
    scrubs=SCRUBS,
    tube=hexes("#26304F")[0],
    steel=METAL[[3, 4, 6]],
    ring=METAL[[2, 4, 6]],
    handle=HANDLE[[1, 2, 3]],
    button=METAL[2],
    pen=hexes("#D64545")[0],
    ribbon=hexes("#9E2B3A", "#D64545", "#F58A80"),
    cyber=False,
)
CYBER = dict(
    coat=hexes("#1B1E52", "#2C2F7A", "#22E3F2"),
    scrubs=HOT,
    tube=HOT[2],
    steel=NEON,
    ring=NEON,
    handle=HOT,
    button=hexes("#FFE14D")[0],
    pen=hexes("#FFE14D")[0],
    ribbon=hexes("#B0207A", "#FF2E88", "#FFB3D6"),
    cyber=True,
)


def magnifier(c, cx, cy, R, look):
    """Upright, the handle down into the paw. The lens shows a magnified mole."""
    c.part(c.limb(cx, cy + R, cx - 1, cy + R + 17, 2.6), look["handle"], 1)
    c.part(c.ellipse(cx, cy, R + 3, R + 3), look["ring"])
    size = int(R * 2) + 2
    mole = lesion("mel", size, 31)
    x0, y0 = int(cx - size / 2), int(cy - size / 2)
    glass = c.ellipse(cx, cy, R, R)
    yy, xx = np.nonzero(glass)
    c.rgb[yy, xx] = mole[np.clip(yy - y0, 0, size - 1), np.clip(xx - x0, 0, size - 1)]
    r, th = np.hypot(c.x - cx, c.y - cy), np.arctan2(c.y - cy, c.x - cx)
    c.rgb[glass & (np.abs(r - R * 0.74) < 1) & (th > -2.8) & (th < -1.8)] = WHITE


def cat_whiskers(c, cx, cy, color=WHISKER, k=1.0):
    for y, slope in ((9, -2), (13, 0), (17, 2)):
        for sign in (-1, 1):
            c.ink(round(cx + 26 * k * sign), round(cy + y * k), round(cx + 38 * k * sign), round(cy + (y + slope) * k), color)


def cat_head(c, cx, cy, k=1.0, whiskers=True, goggles=False):
    """Pleased, with a wink, or in night vision goggles. The same head on the doctor and in the logo, k is its scale."""

    def oval(x, y, rx, ry):
        return c.ellipse(cx + x * k, cy + y * k, rx * k, ry * k)

    def stroke(x0, y0, x1, y1, *style):
        c.ink(round(cx + x0 * k), round(cy + y0 * k), round(cx + x1 * k), round(cy + y1 * k), *style)

    def corner(x, y):
        return cx + x * k, cy + y * k

    # ears, head
    for sign in (-1, 1):
        c.part(c.poly(corner(-26 * sign, -2), corner(-25 * sign, -31), corner(-5 * sign, -19)), FUR)
        c.part(c.poly(corner(-22 * sign, -8), corner(-22 * sign, -25), corner(-9 * sign, -17)), PINK, 1)
    c.part(oval(0, 0, 26, 22), FUR, max(1, round(3 * k)))
    # tabby stripes
    for x0, x1 in ((0, 0), (-7, -6), (7, 6)):
        stroke(x0, -13, x1, -7, GINGER[1], 2)
    for sign in (-1, 1):
        for y in (1, 7):
            stroke(-25 * sign, y, -19 * sign, y + 1, GINGER[1])
    # muzzle
    c.rgb[oval(0, 11, 12, 8.5)] = CREAM[2]
    # the open eye and the wink
    if not goggles:
        c.rgb[oval(-12, 1, 5, 6.5)] = EYE
        c.rgb[oval(-12, 4, 3.2, 3)] = hexes("#3F86B3")[0]
        c.rgb[oval(-13.5, -2, 2, 2.4)] = WHITE
        stroke(7, 4, 12, -1, OUTLINE, 2)
        stroke(12, -1, 17, 4, OUTLINE, 2)
    # nose, open smile, blush
    c.rgb[oval(0, 8.5, 2.6, 1.8)] = PINK[0]
    stroke(0, 10, 0, 12)
    mouth = oval(0, 13, 6, 6) & (c.y >= cy + 13 * k)
    c.rgb[mouth] = HANDLE[0]
    c.rgb[mouth & oval(0, 18, 3.5, 2.5)] = PINK[1]
    stroke(-7, 13, 7, 13)
    for sign in (-1, 1):
        c.rgb[oval(21 * sign, 9, 4.5, 2.5)] = PINK[1]
    if whiskers:
        cat_whiskers(c, cx, cy)
    if goggles:
        # strap, the mount on the forehead with its light, two glowing tubes joined by a bridge
        strap = oval(0, 0, 26, 22) & (np.abs(c.y - cy) < 2.5 * k)
        c.rgb[strap] = GEAR[0]
        c.part(c.poly(corner(-5, -23), corner(5, -23), corner(5, -9), corner(-5, -9)), GEAR, 1)
        c.rgb[oval(0, -18, 1.8, 1.8)] = HOT[2]
        for sign in (-1, 1):
            c.part(oval(12 * sign, 0, 9.5, 9.5), GEAR, 1)
            c.rgb[oval(12 * sign, 0, 6.5, 6.5)] = NIGHT_VISION[0]
            c.rgb[oval(12 * sign, 0, 5, 5)] = NIGHT_VISION[1]
            c.rgb[oval(12 * sign - 2, -2, 1.7, 1.7)] = NIGHT_VISION[2]
        c.rgb[oval(0, 0, 3.5, 2.2)] = GEAR[1]
        return
    # head mirror
    band = oval(0, 0, 26, 22) & (np.abs(c.y - (cy - 19 * k + (c.x - cx) ** 2 * 0.012 / k)) < 1.5 * k)
    c.rgb[band] = METAL[1]
    c.part(oval(0, -20, 6.5, 6.5), METAL[[3, 5, 6]], 1)
    c.rgb[oval(0, -20, 1.6, 1.6)] = METAL[1]


def cat_doctor(look, h=150, w=96):
    """Confident: paw on the hip, feet apart, the magnifier held up by the head. Shown at exactly 2x."""
    c = Figure(h, w)
    coat_colors, cyber = look["coat"], look["cyber"]
    # tail, up behind the coat
    c.part(c.limb(54, 110, 72, 118, 4) | c.limb(72, 118, 80, 104, 4) | c.limb(80, 104, 73, 92, 4), FUR)
    for sx, sy in ((64, 113), (74, 108), (72, 97)):
        c.rgb[sy : sy + 2, sx : sx + 6] = np.where(c.a[sy : sy + 2, sx : sx + 6, None] > 0, GINGER[1], 0)
    # legs and feet
    c.part(c.limb(34, 112, 27, 133, 6.5), look["scrubs"])
    c.part(c.limb(47, 112, 54, 133, 6.5), look["scrubs"])
    for foot in (24, 58):
        c.part(c.ellipse(foot, 139, 9, 5.5), FUR)
        for toe in (-3, 1):
            c.ink(foot + toe, 140, foot + toe, 143, GINGER[0])
    # coat
    coat = c.poly((27, 56), (53, 56), (60, 72), (65, 116), (15, 116), (20, 72))
    c.part(coat, coat_colors, 3)
    c.ink(40, 74, 40, 115, coat_colors[0])
    for by in (84, 95, 106):
        c.rgb[by : by + 2, 42:44] = look["button"]
    # pocket with a pen
    c.part(c.poly((47, 96), (57, 96), (57, 106), (47, 106)), coat_colors)
    c.rgb[92:97, 50:52] = look["pen"]
    # the arm on the hip and the sleeve of the raised one, over the coat
    c.part(c.limb(25, 65, 9, 84, 6.5) | c.limb(9, 84, 22, 96, 6), coat_colors)
    c.part(c.ellipse(24, 97, 5.5, 5.5), FUR)
    c.part(c.limb(55, 65, 70, 76, 6.5) | c.limb(70, 76, 76, 67, 6), coat_colors)
    # scrubs in the collar, lapels
    c.part(c.poly((32, 55), (48, 55), (40, 73)), look["scrubs"])
    c.part(c.poly((25, 56), (33, 54), (40, 73), (32, 78)), coat_colors)
    c.part(c.poly((55, 56), (47, 54), (40, 73), (48, 78)), coat_colors)
    # stethoscope
    for x0, y0, x1, y1 in ((30, 57, 34, 76), (49, 57, 45, 76), (34, 76, 39, 84), (45, 76, 40, 84), (40, 84, 40, 89)):
        c.ink(x0, y0, x1, y1, look["tube"], 2)
    c.part(c.ellipse(40.5, 92, 4, 4), look["steel"], 1)
    # the head, tilted, on its own layer
    head = Figure(h, w)
    cat_head(head, 40, 36, whiskers=not cyber, goggles=cyber)
    c.stamp(head, 6, (40, 56))
    # the magnifier, in front of the whiskers, and the paw around its handle
    magnifier(c, 81, 34, 11, look)
    c.part(c.ellipse(80, 58, 6.5, 6), FUR)
    for toe in (77, 80, 83):
        c.ink(toe, 56, toe, 59, GINGER[0])
    if cyber:  # a neon edge, or the dark outline would vanish on the dark page
        c.outline(NEON[1])
        whiskers = Figure(h, w)
        cat_whiskers(whiskers, 40, 36, HOT[2])
        c.stamp(whiskers, 6, (40, 56), behind=True)
    return c


for theme, look in (("light", DOCTOR), ("dark", CYBER)):
    c = cat_doctor(look)
    save(c.rgb, f"cat-doctor-{theme}.png", c.a)


def mark(cyber):
    """App logo: the doctor's head. Shown at exactly 1x, 48 px."""
    c = Figure(48, 48)
    cat_head(c, 24, 28, 0.8, whiskers=False, goggles=cyber)
    if cyber:
        c.outline(NEON[1])
    return c.rgb, c.a


for theme, cyber in (("light", False), ("dark", True)):
    _r, _a = mark(cyber)
    save(_r, f"mark-{theme}.png", _a)


def paw():
    """Four toe beans over a pad. Shown at exactly 2x in lists and 3x in the empty photo slot."""
    grid = [
        "...OO..OO...",
        "..OLPOOLPO..",
        "..OPPOOPPO..",
        ".OOPPOOPPOO.",
        "OLPOOOOOOLPO",
        "OPPOOLLOOPPO",
        "OPPOLPPPOPPO",
        ".OOLPPPPPOO.",
        "..OPPPPPPO..",
        "..OPPPPPPO..",
        "...OOOOOO...",
        "............",
    ]
    pal = {"O": OUTLINE, "P": PINK[1], "L": PINK[2]}
    rgb, a = np.zeros((12, 12, 3), np.float32), np.zeros((12, 12), np.float32)
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch != ".":
                rgb[y, x], a[y, x] = pal[ch], 1
    return rgb, a


_r, _a = paw()
save(_r, "paw.png", _a)


def walk_leg(c, hip, ph, colors, shadow):
    """One leg of the trot: forward through the air, back along the ground."""
    x, lift = hip + 5 * np.cos(ph), max(0.0, np.sin(ph)) * 3.5
    c.part(c.limb(hip, 38, x, 50 - lift, 3.2), colors)
    c.part(c.ellipse(x + 1, 51.5 - lift, 4.5, 2.6), colors)
    c.ink(round(x + 2), round(51 - lift), round(x + 2), round(53 - lift), shadow)


def ribbon_tail(c, y0, length, slope, ph, colors):
    """A ribbon end streaming back from the neck, more loose towards its forked tip."""
    run = 34 - c.x
    middle = y0 - slope * run + run / length * 3 * np.sin(run * 0.3 - ph)
    strip = (run >= 0) & (run < length) & (np.abs(c.y - middle) < 2.2)
    c.part(strip & ~((run > length - 4) & (np.abs(c.y - middle) < (run - length + 4) * 0.6)), colors, 1)


def walk_frame(look, ph, fh, fw):
    c = Figure(fh, fw)
    cyber, ribbon, far = look["cyber"], look["ribbon"], GINGER[[0, 1, 3]]
    bob = round(abs(np.sin(ph)))
    # far legs, near legs
    walk_leg(c, 43, ph + np.pi, far, OUTLINE)
    walk_leg(c, 22, ph, far, OUTLINE)
    walk_leg(c, 37, ph, FUR, GINGER[0])
    walk_leg(c, 16, ph + np.pi, FUR, GINGER[0])
    # tail, up and swaying
    sway = round(np.sin(ph) * 2)
    tail = c.limb(11, 29 + bob, 6, 21, 3) | c.limb(6, 21, 6 + sway, 12, 3) | c.limb(6 + sway, 12, 10 + sway, 6, 2.6)
    c.part(tail, FUR, 1)
    c.rgb[tail & ((np.abs(c.y - 11) < 1) | (np.abs(c.y - 18) < 1))] = GINGER[1]
    # body: haunch and chest with a waist between them, cream under the chest, tabby stripes
    body = c.ellipse(16, 32 + bob, 10, 9.5) | c.ellipse(36, 32 + bob, 10, 10) | c.limb(16, 32 + bob, 36, 32 + bob, 7.5)
    c.part(body, FUR, 3)
    c.rgb[body & c.ellipse(36, 42 + bob, 10, 6)] = CREAM[2]
    for x in (12, 19, 26):
        c.rgb[body & (c.y < 31 + bob) & (np.abs(c.x - x - (c.y - 24) * 0.2) < 1)] = GINGER[1]
    # the ribbon: its ends in the wind behind the neck, a band round the neck, then the head, the bow under the chin
    ribbon_tail(c, 25 + bob, 21, 0.55, ph, ribbon)
    ribbon_tail(c, 27 + bob, 16, 0.3, ph + 1.4, ribbon)
    c.part(c.limb(37, 24 + bob, 45, 39 + bob, 2.4), ribbon, 1)
    cat_head(c, 48, 21 + bob, 0.58, whiskers=False, goggles=cyber)
    for sign in (-1, 1):
        c.part(c.poly((46, 36 + bob), (46 + 8 * sign, 31 + bob), (46 + 8 * sign, 41 + bob)), ribbon, 1)
    c.part(c.ellipse(46, 36 + bob, 2.6, 2.6), ribbon, 1)
    if cyber:  # as on the doctor
        c.outline(NEON[1])
    whiskers = Figure(fh, fw)
    cat_whiskers(whiskers, 48, 21 + bob, HOT[2] if cyber else WHISKER, 0.58)
    c.stamp(whiskers, 0, (0, 0), behind=True)
    return c


def cat_walk(look, frames=6, fw=72, fh=56):
    """Side-on trot, frames left to right, for a CSS steps() animation. Shown at exactly 2x."""
    sheet = Figure(fh, fw * frames)
    for f in range(frames):
        c = walk_frame(look, f / frames * 2 * np.pi, fh, fw)
        sheet.rgb[:, f * fw : (f + 1) * fw] = c.rgb
        sheet.a[:, f * fw : (f + 1) * fw] = c.a
    return sheet


for theme, look in (("light", DOCTOR), ("dark", CYBER)):
    c = cat_walk(look)
    save(c.rgb, f"cat-walk-{theme}.png", c.a)


# ---------------------------------------------------------------- cat city skyline
SITTING_CAT = [
    "#.....#..",
    "##...##..",
    "#######..",
    "#o###o#..",
    "#######.#",
    ".#####..#",
    ".######.#",
    ".#######.",
    ".#.#.#.#.",
]


def put_cat(rgb, x, base, body, eye):
    for j, row in enumerate(SITTING_CAT):
        for i, ch in enumerate(row):
            yy, xx = base - len(SITTING_CAT) + j, x + i
            if ch != "." and 0 <= yy < rgb.shape[0] and 0 <= xx < rgb.shape[1]:
                rgb[yy, xx] = eye if ch == "o" else body


def skyline(palette, name, seed):
    h, w = 72, 640
    rng = np.random.default_rng(seed)
    rgb = ramp(np.linspace(0, 1, h)[:, None] * np.ones((h, w)), hexes(*palette["sky"]), 1.0)
    yy, xx = np.mgrid[0:h, 0:w]
    # sun or moon with cat ears
    dcx, dcy, dr = 520, 25, 15
    disc = np.hypot(xx - dcx, yy - dcy) < dr
    shade = ramp(1 - (yy.astype(np.float32) - 8) / 32, hexes(*palette["disc"]), 0.9)
    rgb[disc] = shade[disc]
    for sgn in (-1, 1):
        a, b, d = (dcx + sgn * 14, dcy - 5), (dcx + sgn * 4, dcy - 13), (dcx + sgn * 14, dcy - 22)
        sides = [(q[0] - p[0]) * (yy - p[1]) - (q[1] - p[1]) * (xx - p[0]) for p, q in ((a, b), (b, d), (d, a))]
        ear = (sides[0] >= 0) & (sides[1] >= 0) & (sides[2] >= 0) | (sides[0] <= 0) & (sides[1] <= 0) & (sides[2] <= 0)
        rgb[ear] = shade[ear]
    for ex in (-5, 5):
        rgb[dcy - 3 : dcy, dcx + ex - 1 : dcx + ex + 1] = hexes(palette["face"])[0]
    rgb[dcy + 3, dcx - 1 : dcx + 1] = hexes(palette["face"])[0]
    roofs = []
    for layer, (lo, hi, wmin, wmax, key) in enumerate([(26, 50, 20, 44, "far"), (14, 40, 16, 38, "near")]):
        x = -int(rng.integers(0, 12))
        col = hexes(palette[key])[0]
        while x < w:
            bw = int(rng.integers(wmin, wmax))
            top = h - int(rng.integers(lo, hi))
            x0, x1 = max(x, 0), min(x + bw, w)
            rgb[top:h, x0:x1] = col
            ears = rng.random() < 0.6
            if ears and x1 - x0 > 14:  # cat-eared rooftops
                for i in range(6):
                    rgb[top - 6 + i, x0 + 1 : x0 + 2 + i] = col
                    rgb[top - 6 + i, x1 - 2 - i : x1 - 1] = col
            if layer == 1:
                rgb[top:h, x0 : min(x0 + 1, w)] = col * 1.25
                for wy in range(top + 4, h - 3, 5):
                    for wx in range(x0 + 3, x1 - 3, 5):
                        if rng.random() < palette["lit"]:
                            rgb[wy : wy + 3, wx : wx + 2] = hexes(*palette["win"])[rng.integers(0, len(palette["win"]))]
                if not ears and x1 - x0 > 16:
                    roofs.append((x0 + int(rng.integers(2, x1 - x0 - 11)), top))
            x += bw + (int(rng.integers(0, 4)) if layer else 0)
    for rx, top in roofs[::2]:
        if not 92 < rx < 140:
            put_cat(rgb, rx, top, hexes(palette["cat"])[0], hexes(palette["eye"])[0])
    # the clinic: cat-eared tower with a cross on a pole
    cx0, cx1, top = 96, 136, 20
    col = hexes(palette["clinic"])[0]
    rgb[top:h, cx0:cx1] = col
    for i in range(9):
        rgb[top - 9 + i, cx0 + 1 : cx0 + 2 + i] = col
        rgb[top - 9 + i, cx1 - 2 - i : cx1 - 1] = col
    for wy in range(top + 6, h - 3, 6):
        for wx in range(cx0 + 4, cx1 - 4, 7):
            rgb[wy : wy + 3, wx : wx + 3] = hexes(palette["win"][0])[0]
    c = hexes(palette["cross"])[0]
    rgb[top - 13 : top - 2, 114:118] = c
    rgb[top - 10 : top - 7, 110:122] = c
    save(rgb, name)


skyline(
    dict(
        sky=("#FBE9D4", "#F8DCC0", "#F6CFB0", "#F4EFEA"),
        disc=("#FF9538", "#FFC24D", "#FFE14D"),
        face="#9A430A",
        far="#EAD9C6",
        near="#DCC6AF",
        win=("#FFE14D", "#FBF9F6"),
        lit=0.28,
        clinic="#CDEBFF",
        cross="#D64545",
        cat="#8C5A3C",
        eye="#FFE14D",
    ),
    "sky-light.png",
    3,
)
skyline(
    dict(
        sky=("#0A1230", "#141A4A", "#2A1B5C", "#4A1C6E"),
        disc=("#FF2E88", "#FF6FB0", "#FFD1E4"),
        face="#4A1C6E",
        far="#101B45",
        near="#0C1538",
        win=("#22E3F2", "#FF2E88", "#FFE14D"),
        lit=0.34,
        clinic="#16245A",
        cross="#22E3F2",
        cat="#FF6FB0",
        eye="#22E3F2",
    ),
    "sky-dark.png",
    3,
)
print(sorted(p.name for p in OUT.iterdir()))
