"""Bundled images as data URIs, so components can place them in plain HTML."""

import base64
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "assets"
PIXEL = ROOT / "pixel"
SAMPLES = ROOT / "samples"


@cache
def _uri(path: Path) -> str:
    mime = "image/png" if path.suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def pixel(name: str) -> str:
    return _uri(PIXEL / f"{name}.png")


def sample(code: str) -> str | None:
    """A HAM10000 photo from assets/samples/, if one exists."""
    photo = SAMPLES / f"{code}.jpg"
    return _uri(photo) if photo.exists() else None
