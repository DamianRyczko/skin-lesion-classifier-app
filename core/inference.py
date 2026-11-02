"""One analysis: an option of the predictor + its TTA views -> what the page shows."""

import time
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from loguru import logger
from PIL import Image

from model import PREDICTOR, ModelSpec, exclusive

from .classes import needs_consultation, risk_score


@dataclass(frozen=True)
class Prediction:
    model_id: str
    level: str
    probs: dict[str, float]  # class code -> share of the bars, highest first; includes the decision bias
    risk: float
    melanoma: bool  # the tuned melanoma threshold fired; always False for a package without thresholds
    consult: bool
    n_views: int  # per model

    @property
    def top(self) -> str:
        return next(iter(self.probs))


def analyze(
    spec: ModelSpec,
    image: Image.Image,
    image_key: str,
    level: str,
    on_view: Callable[[int, int], None] | None = None,
) -> Prediction:
    """Run every view through the option's models. on_view(done, total) reports progress."""

    def report(done: int, total: int) -> None:
        logger.debug("tta view {}/{}", done, total)
        if on_view:
            on_view(done, total)

    with exclusive(spec.id):
        started = time.perf_counter()
        result = PREDICTOR.predict(image, spec.id, level, on_view=report)
    probs = {code: percent / 100 for code, percent in result["percentages"].items()}
    warning = result["melanoma_warning"]
    melanoma = warning is not None and warning["flag"]
    consult = needs_consultation(probs) or melanoma
    prediction = Prediction(spec.id, level, probs, risk_score(probs), melanoma, consult, result["views_per_model"])
    logger.info(
        "result {} {} {}: {} {:.1%}, risk {:.1%}, melanoma score {}, {} ({} views, {:.2f}s)",
        spec.label,
        level,
        image_key[:6],
        prediction.top,
        probs[prediction.top],
        prediction.risk,
        "off" if warning is None else f"{warning['score']:.1%}/{warning['threshold']:.1%}",
        "consult" if consult else "watch",
        prediction.n_views * len(spec.members),
        time.perf_counter() - started,
    )
    return prediction


def explain(
    spec: ModelSpec,
    image: Image.Image,
    code: str,
    on_step: Callable[[int, int], None] | None = None,
) -> np.ndarray:
    """Occlusion map for one class, 2D in 0..1."""
    with exclusive(spec.id):
        started = time.perf_counter()
        heat = PREDICTOR.explain(image, code, spec.id, on_step=on_step)
    logger.info("xai {} {} ({:.2f}s)", spec.label, code, time.perf_counter() - started)
    return heat
