"""The trained models from weights/, shared by all browser sessions."""

import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from loguru import logger

from skin_lesion_app.config import PACKAGE_DIR
from skin_lesion_app.predictor import SkinLesionPredictor


@dataclass(frozen=True)
class ModelSpec:
    id: str
    label: str
    members: tuple[str, ...]


PREDICTOR = SkinLesionPredictor(PACKAGE_DIR)
MODELS: dict[str, ModelSpec] = {o["id"]: ModelSpec(o["id"], o["label"], tuple(o["members"])) for o in PREDICTOR.options.values()}
logger.info("weights: {}, options {}", PACKAGE_DIR, list(MODELS))

_lock = threading.RLock()


def is_loaded(model_id: str) -> bool:
    return all(PREDICTOR.models[member].loaded for member in MODELS[model_id].members)


def load_model(model_id: str) -> None:
    """Once per server process; browser sessions share the result."""
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
    # Held for a whole analysis. A tab that switched options mid-run would unload these models,
    # and this run's next view would load them back on top of that tab's models.
    with _lock:
        load_model(model_id)
        yield
