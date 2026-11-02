import itertools
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .config import CLASS_CODES, CLASS_NAMES, DISCLAIMER, LEVELS, MEL, load_config
from .explain import GRID, occlusion_map
from .models import OnnxModel, Step, percentages, softmax
from .views import ImageSource, load_image

Progress = Callable[[int, int], None]  # done, total


def _counter(total: int, report: Progress | None) -> Step | None:
    """Turns report(done, total) into the step() a model calls after each run."""
    if report is None:
        return None
    done = itertools.count(1)
    return lambda: report(next(done), total)


def _with_bias(p: np.ndarray, bias: list[float]) -> np.ndarray:
    return softmax(np.log(np.clip(p, 1e-8, 1.0)) + np.asarray(bias))


def _bars(per_model: np.ndarray, settings: dict[str, Any]) -> np.ndarray:
    """The percentages: one bias on the models' mean, or with member_bias each model's own, then the mean of the results."""
    if "member_bias" in settings:
        return np.mean([_with_bias(p, bias) for p, bias in zip(per_model, settings["member_bias"], strict=True)], axis=0)
    return _with_bias(per_model.mean(0), settings["decision_bias"])


class SkinLesionPredictor:
    """
    predictor = SkinLesionPredictor("skin_lesions_app")
    predictor.predict(image, option="swin", level="balanced") -> dict

    image: file path, bytes, file object, PIL image or HxWx3 uint8 array.
    option: id from predictor.options() (default from app_config.json).
    level: "fast" (1 view per model), "balanced" (4) or "best" (12).
    """

    def __init__(
        self,
        package_dir: str | Path,
        providers: list[str] | None = None,
        threads: int = 0,
        preload: bool = False,
    ) -> None:
        self.package_dir = Path(package_dir)
        self.config = load_config(self.package_dir)
        self.models: dict[str, OnnxModel] = {
            key: OnnxModel(key, spec, self.package_dir, providers, threads) for key, spec in self.config["models"].items()
        }
        self._options = {o["id"]: o for o in self.config["options"]}
        if preload:
            for model in self.models.values():
                model.load()

    # ── what the app can offer ───────────────────────────────────────────────
    def options(self) -> list[dict[str, Any]]:
        out = []
        for o in self.config["options"]:
            out.append(
                {
                    "id": o["id"],
                    "label": o["label"],
                    "description": o.get("description", ""),
                    "members": list(o["members"]),
                    "models": [self.config["models"][m]["label"] for m in o["members"]],
                    "test_macro_f1": {lv: o["levels"][lv]["scores"].get("test_macro_f1") for lv in o["levels"]},
                }
            )
        return out

    @property
    def default_option(self) -> str:
        return self.config["default_option"]

    @property
    def default_level(self) -> str:
        return self.config["default_level"]

    @property
    def levels(self) -> list[str]:
        """The levels this package has settings for, fastest first."""
        tuned = self.config["options"][0]["levels"]
        return [level for level in LEVELS if level in tuned]

    # ── prediction ───────────────────────────────────────────────────────────
    def _resolve(self, option: str | None, level: str | None) -> tuple[dict[str, Any], str]:
        option = option or self.default_option
        level = level or self.default_level
        if option not in self._options:
            raise ValueError(f"unknown option {option!r}; choose from {list(self._options)}")
        if level not in self.levels:
            raise ValueError(f"unknown level {level!r}; choose from {self.levels}")
        return self._options[option], level

    def prepare(self, option: str) -> None:
        """Loads the option's models and unloads the others, so memory holds one option at a time."""
        members = self._options[option]["members"]
        for key, model in self.models.items():
            if key not in members:
                model.unload()
        for key in members:
            self.models[key].load()

    def _member_probabilities(
        self, img: Image.Image, opt: dict[str, Any], level: str, on_view: Progress | None = None
    ) -> np.ndarray:
        """Mean softmax over the views, one row per model of the option: array (models, 7)."""
        self.prepare(opt["id"])
        n_views, members = LEVELS[level], opt["members"]
        step = _counter(n_views * len(members), on_view)
        return np.stack([self.models[m].view_probabilities(img, n_views, step).mean(0) for m in members])

    def probabilities(self, image: ImageSource, option: str | None = None, level: str | None = None) -> np.ndarray:
        """Mean softmax over the option's models and their views (before the decision bias): array (7,)."""
        opt, level = self._resolve(option, level)
        return self._member_probabilities(load_image(image), opt, level).mean(0)

    def predict(
        self,
        image: ImageSource,
        option: str | None = None,
        level: str | None = None,
        melanoma_warning: bool = True,
        on_view: Progress | None = None,
    ) -> dict[str, Any]:
        """on_view(done, total) reports progress over all views of all the option's models."""
        t0 = time.perf_counter()
        opt, level = self._resolve(option, level)
        img = load_image(image)
        per_model = self._member_probabilities(img, opt, level, on_view)
        p = per_model.mean(0)
        shown = _bars(per_model, opt["levels"][level])  # tallest bar = predicted class
        order = np.argsort(-shown)
        pct = percentages(shown)
        top = CLASS_CODES[order[0]]
        result: dict[str, Any] = {
            "option": opt["id"],
            "option_label": opt["label"],
            "level": level,
            "views_per_model": LEVELS[level],
            "prediction": {"code": top, "name": CLASS_NAMES[top]},
            "percentages": {CLASS_CODES[i]: float(pct[i]) for i in order},
        }
        if melanoma_warning:
            result["melanoma_warning"] = self._melanoma_warning(img, p, opt, level)
        result["seconds"] = round(time.perf_counter() - t0, 3)
        result["disclaimer"] = DISCLAIMER
        return result

    def explain(
        self, image: ImageSource, class_code: str, option: str | None = None, on_step: Progress | None = None
    ) -> np.ndarray:
        """Where the option's models find class_code: array (GRID, GRID) in 0..1, see explain.py."""
        opt, _ = self._resolve(option, None)
        self.prepare(opt["id"])
        img, members = load_image(image), opt["members"]
        step = _counter(GRID * len(members), on_step)
        index = CLASS_CODES.index(class_code)
        heat = np.mean([occlusion_map(self.models[m], img, index, step) for m in members], axis=0)
        peak = float(heat.max())
        return heat / peak if peak > 0 else heat

    def _melanoma_warning(self, img: Image.Image, p: np.ndarray, opt: dict[str, Any], level: str) -> dict[str, Any] | None:
        """Flags lesions where melanoma can't be ruled out. Threshold tuned on out-of-fold data for a target
        sensitivity (e.g. 0.90 = catch 9 of 10 melanomas), so it fires more often than 'mel' is the top class.
        None when the package has no thresholds."""
        warn = self.config.get("melanoma_warning")
        if warn is None:
            return None
        target = warn["target_sensitivity"]
        spec = self.config.get("melanoma_specialist")
        if warn.get("source") == "specialist" and spec:
            score = float(self.models[spec["model"]].view_probabilities(img, LEVELS[level]).mean(0)[MEL])
            threshold = spec["levels"][level]["melanoma_thresholds"][target]
            source = spec["label"]
        else:
            score = float(p[MEL])
            threshold = opt["levels"][level]["melanoma_thresholds"][target]
            source = opt["label"]
        flag = score >= threshold
        return {
            "flag": bool(flag),
            "score": round(score, 4),
            "threshold": round(float(threshold), 4),
            "target_sensitivity": float(target),
            "source": source,
            "message": ("Melanoma can't be ruled out for this lesion. Please have it checked by a doctor." if flag else None),
        }
