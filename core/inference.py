import time
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from loguru import logger
from PIL import Image

from model import PREDICTOR, ModelSpec, exclusive
from skin_lesion_app.config import LEVELS

from .classes import needs_consultation, risk_score


@dataclass(frozen=True)
class Prediction:
    model_id: str
    level: str
    probs: dict[str, float]  # class code -> share, highest first; includes the decision bias
    risk: float
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
    def report(done: int, total: int) -> None:
        logger.debug("tta view {}/{}", done, total)
        if on_view:
            on_view(done, total)

    with exclusive(spec.id):
        started = time.perf_counter()
        percent = PREDICTOR.predict(image, spec.id, level, on_view=report)
    probs = {code: value / 100 for code, value in percent.items()}
    prediction = Prediction(spec.id, level, probs, risk_score(probs), needs_consultation(probs), LEVELS[level])
    logger.info(
        "result {} {} {}: {} {:.1%}, risk {:.1%}, {} ({} views, {:.2f}s)",
        spec.label,
        level,
        image_key[:6],
        prediction.top,
        probs[prediction.top],
        prediction.risk,
        "consult" if prediction.consult else "watch",
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
    with exclusive(spec.id):
        started = time.perf_counter()
        heat = PREDICTOR.explain(image, code, spec.id, on_step=on_step)
    logger.info("xai {} {} ({:.2f}s)", spec.label, code, time.perf_counter() - started)
    return heat
