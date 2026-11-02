"""The app's models: the trained package from weights/, or a mock until it is there.

The models themselves live in skin_lesion_app/. This module picks the source and
offers it to the pages, and knows nothing about Streamlit. A package that is there
but broken raises instead of falling back: mock results must never pass for real ones.
"""

import os
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

import numpy as np
from loguru import logger

from skin_lesion_app import CLASS_CODES, DEFAULT_OPTIONS, DEFAULT_PACKAGE, LEVELS, SkinLesionPredictor
from skin_lesion_app.config import CONFIG_FILES
from skin_lesion_app.models import OnnxModel

# Shorter than the package's labels: these go on buttons.
_BUTTON_LABELS = {"my_resnet": "ResNet", "ensemble": "Ensemble"}


# ---------------------------------------------------------------- mock
# How colour statistics push the mock towards each class: dark, uneven photos
# lean to melanoma, red ones to vascular lesions and so on. Not a real model,
# but it answers to the image, so TTA and model switching behave believably.
_MOCK_BASE = {
    #         dark  spread  red  uneven  bias
    "akiec": (-0.4, 0.6, 1.0, 0.4, -1.3),
    "bcc": (-0.2, 0.4, 0.8, 0.0, -0.9),
    "bkl": (0.2, -0.2, -0.2, 0.2, 0.2),
    "df": (-0.1, -0.3, 0.2, -0.3, -1.6),
    "mel": (3.2, 1.6, -0.3, 1.8, -1.0),
    "nv": (1.2, -1.2, -0.4, -0.8, 1.3),
    "vasc": (0.1, 0.2, 2.2, 0.2, -2.0),
}
_MOCK_VIEWS: list[dict[str, Any]] = [
    {"name": "plain"},
    {"name": "turn 90", "k90": 1},
    {"name": "flip", "flip": True},
    {"name": "zoom in", "crop": [0.08, 0.08, 0.92, 0.92]},
    {"name": "turn 180", "k90": 2},
    {"name": "turn 270", "k90": 3},
    {"name": "zoom out", "zoom_out": 0.85},
    {"name": "rotate 30", "angle": 30},
    {"name": "rotate -30", "angle": -30},
    {"name": "rotate 45", "angle": 45},
    {"name": "rotate -45", "angle": -45},
    {"name": "colour", "brightness": 1.08, "saturation": 0.95},
]


def _load_delay() -> float:
    return float(os.getenv("SKIN_APP_MOCK_LOAD", "1.2"))


def _view_delay() -> float:
    return float(os.getenv("SKIN_APP_MOCK_VIEW", "0.06"))


class MockModel(OnnxModel):
    """Believable logits from simple colour statistics. Everything around them is the real pipeline."""

    def __init__(self, key: str, spec: dict[str, Any]):
        super().__init__(key, spec, ".")
        rng = np.random.default_rng(sum(ord(ch) for ch in key))
        weights = np.array([_MOCK_BASE[code] for code in CLASS_CODES])
        self.weights = weights + rng.normal(0, 0.45, weights.shape)

    def load(self) -> Any:
        if self._session is None:
            time.sleep(_load_delay())
            self._session = self
        return self._session

    @staticmethod
    def _features(view: np.ndarray) -> np.ndarray:
        luma = view.mean(axis=2)
        dark = float((luma < np.median(luma) * 0.75).mean()) * 2
        spread = float(luma.std()) * 4
        red = float((view[..., 0] - view[..., 2]).mean()) * 3 - 0.6
        side = luma.shape[0] // 4
        tiles = [luma[y : y + side, x : x + side].mean() for y in range(0, side * 4, side) for x in range(0, side * 4, side)]
        return np.array([dark, spread, red, float(np.std(tiles)) * 6, 1.0])

    def logits(self, batch: np.ndarray) -> np.ndarray:
        self.load()
        time.sleep(_view_delay() * len(batch))
        return np.stack([self.weights @ self._features(view) for view in batch.transpose(0, 2, 3, 1)])


class MockPredictor(SkinLesionPredictor):
    """The real predictor over mock models: no decision bias, a plain melanoma threshold, no scores."""

    def __init__(self) -> None:
        settings = {
            level: {
                "decision_bias": [0.0] * len(CLASS_CODES),
                "melanoma_thresholds": {"0.90": 0.5},
                "scores": {"test_macro_f1": 0.0},
            }
            for level in LEVELS
        }
        spec = {"onnx": "", "img_size": 224, "mean": [0, 0, 0], "std": [1, 1, 1], "tta_views": _MOCK_VIEWS}
        tags = {tag for option in DEFAULT_OPTIONS for tag in option["members"]}
        self.config = {
            "models": {tag: {**spec, "label": tag} for tag in tags},
            "options": [{**option, "levels": settings} for option in DEFAULT_OPTIONS],
            "default_option": "swin",
            "default_level": "balanced",
            "melanoma_warning": {"source": "option", "target_sensitivity": "0.90"},
        }
        self.models = {key: MockModel(key, spec) for key, spec in self.config["models"].items()}
        self._options = {option["id"]: option for option in self.config["options"]}


# ---------------------------------------------------------------- registry
@dataclass(frozen=True)
class ModelSpec:
    id: str
    label: str
    members: tuple[str, ...]
    mock: bool


def _open_predictor() -> SkinLesionPredictor:
    if any((DEFAULT_PACKAGE / name).exists() for name in CONFIG_FILES):
        predictor = SkinLesionPredictor(DEFAULT_PACKAGE)
        logger.info("weights: {}, options {}", DEFAULT_PACKAGE, [option["id"] for option in predictor.options()])
        return predictor
    logger.warning("weights: no settings file in {}, using the mock", DEFAULT_PACKAGE)
    return MockPredictor()


PREDICTOR = _open_predictor()
MODELS: dict[str, ModelSpec] = {
    option["id"]: ModelSpec(
        option["id"],
        _BUTTON_LABELS.get(option["id"], option["label"]),
        tuple(option["members"]),
        isinstance(PREDICTOR, MockPredictor),
    )
    for option in PREDICTOR.options()
}

_lock = threading.RLock()


def is_loaded(model_id: str) -> bool:
    return all(PREDICTOR.models[member].loaded for member in MODELS[model_id].members)


def load_model(model_id: str) -> None:
    """Load once per server process; browser sessions share the result."""
    with _lock:
        if is_loaded(model_id):
            return
        spec = MODELS[model_id]
        logger.info("model {} loading", spec.label)
        started = time.perf_counter()
        PREDICTOR.prepare(model_id)
        logger.info("model {} ready in {:.1f}s", spec.label, time.perf_counter() - started)


@contextmanager
def exclusive(model_id: str) -> Iterator[None]:
    """The option's models, kept for one whole analysis. Browser tabs take turns: a tab that switched options
    mid-run would unload them, and the run's next view would load them back on top of that tab's models."""
    with _lock:
        load_model(model_id)
        yield
