from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .views import view_batch

Step = Callable[[], None]


def percentages(shares: np.ndarray, decimals: int = 1) -> np.ndarray:
    """Percentages that add up to exactly 100 (largest-remainder rounding)."""
    unit = 10**decimals
    raw = np.asarray(shares, dtype=np.float64) / np.sum(shares) * 100 * unit
    out = np.floor(raw)
    out[np.argsort(raw - out)[::-1][: int(round(100 * unit - out.sum()))]] += 1
    return out / unit


def softmax(z: np.ndarray, axis: int = -1) -> np.ndarray:
    z = np.asarray(z, dtype=np.float64)
    e = np.exp(z - z.max(axis=axis, keepdims=True))
    return e / e.sum(axis=axis, keepdims=True)


class OnnxModel:
    """One exported network (raw logits). The TTA views are applied here."""

    def __init__(self, spec: dict[str, Any], package_dir: Path) -> None:
        self.spec = spec
        self.path = package_dir / spec["onnx"]
        self._session: Any = None

    @property
    def loaded(self) -> bool:
        return self._session is not None

    def load(self) -> Any:
        if self._session is None:
            import onnxruntime as ort

            opts = ort.SessionOptions()
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            opts.enable_cpu_mem_arena = False
            opts.enable_mem_pattern = False
            self._session = ort.InferenceSession(str(self.path), sess_options=opts, providers=["CPUExecutionProvider"])
        return self._session

    def unload(self) -> None:
        self._session = None

    def logits(self, batch: np.ndarray) -> np.ndarray:
        sess = self.load()
        return sess.run(None, {sess.get_inputs()[0].name: batch})[0]

    def view_probabilities(self, img: Image.Image, n_views: int, on_step: Step | None = None) -> np.ndarray:
        """Softmax of the first n_views views, shape (n_views, 7). One view per run, so on_step can report."""
        views = self.spec["tta_views"][:n_views]
        batch = view_batch(img, views, self.spec["img_size"], self.spec["mean"], self.spec["std"])
        rows = []
        for i in range(len(batch)):
            rows.append(self.logits(batch[i : i + 1]))
            if on_step:
                on_step()
        return softmax(np.concatenate(rows), axis=1)
