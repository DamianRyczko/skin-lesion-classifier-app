import itertools
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .config import CLASS_CODES, LEVELS, load_config
from .explain import GRID, occlusion_map
from .models import OnnxModel, Step, percentages, softmax
from .views import fit_training_scale

Progress = Callable[[int, int], None]  # done, total


def _counter(total: int, report: Progress | None) -> Step | None:
    if report is None:
        return None
    done = itertools.count(1)
    return lambda: report(next(done), total)


def _with_bias(p: np.ndarray, bias: list[float]) -> np.ndarray:
    return softmax(np.log(np.clip(p, 1e-8, 1.0)) + np.asarray(bias))


class SkinLesionPredictor:
    def __init__(self, package_dir: Path) -> None:
        self.config = load_config(package_dir)
        self.models = {key: OnnxModel(spec, package_dir) for key, spec in self.config["models"].items()}
        self.options: dict[str, dict[str, Any]] = {o["id"]: o for o in self.config["options"]}
        self.default_option: str = self.config["default_option"]

    def prepare(self, option: str) -> None:
        """Loads the option's models and unloads the rest: memory holds one option at a time."""
        members = self.options[option]["members"]
        for key, model in self.models.items():
            if key not in members:
                model.unload()
        for key in members:
            self.models[key].load()

    def predict(self, image: Image.Image, option: str, level: str, on_view: Progress | None = None) -> dict[str, float]:
        """Percent per class code, highest first. on_view(done, total) counts views over all members."""
        members, biases = self.options[option]["members"], self.options[option]["bias"][level]
        self.prepare(option)
        img, n_views = fit_training_scale(image), LEVELS[level]
        step = _counter(n_views * len(members), on_view)
        shares = np.mean(
            [
                _with_bias(self.models[member].view_probabilities(img, n_views, step).mean(0), bias)
                for member, bias in zip(members, biases, strict=True)
            ],
            axis=0,
        )
        pct = percentages(shares)
        return {CLASS_CODES[i]: float(pct[i]) for i in np.argsort(-shares)}

    def explain(self, image: Image.Image, class_code: str, option: str, on_step: Progress | None = None) -> np.ndarray:
        """Where the option's models find class_code, (GRID, GRID) in 0..1."""
        self.prepare(option)
        img, members = fit_training_scale(image), self.options[option]["members"]
        step = _counter(GRID * len(members), on_step)
        index = CLASS_CODES.index(class_code)
        heat = np.mean([occlusion_map(self.models[m], img, index, step) for m in members], axis=0)
        peak = float(heat.max())
        return heat / peak if peak > 0 else heat
