"""Writes a real model package with tiny ONNX networks: the same files build.py writes, a few KB each.

Each network is average colour -> linear layer -> 7 logits, so the numbers mean nothing,
but ONNX Runtime really runs them.
"""

import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper

from skin_lesion_app import CLASSES, DEFAULT_OPTIONS, LEVELS
from skin_lesion_app.config import PACKAGE_FORMAT

VIEWS: list[dict[str, Any]] = [
    {"name": "plain"},
    {"name": "flip", "flip": True},
    {"name": "turn", "k90": 1},
    {"name": "zoom in", "crop": [0.1, 0.1, 0.9, 0.9]},
    {"name": "zoom out", "zoom_out": 0.8},
    {"name": "rotate", "angle": 30},
    {"name": "bright", "brightness": 1.1},
    {"name": "contrast", "contrast": 0.9},
    {"name": "saturation", "saturation": 1.1},
    {"name": "turn 2", "k90": 2},
    {"name": "turn flip", "k90": 3, "flip": True},
    {"name": "rotate back", "angle": -45},
]


def tiny_network(seed: int) -> onnx.ModelProto:
    rng = np.random.default_rng(seed)
    graph = helper.make_graph(
        [
            helper.make_node("GlobalAveragePool", ["image"], ["pooled"]),
            helper.make_node("Flatten", ["pooled"], ["colour"]),
            helper.make_node("MatMul", ["colour", "weights"], ["logits"]),
        ],
        "tiny",
        [helper.make_tensor_value_info("image", TensorProto.FLOAT, ["batch", 3, "height", "width"])],
        [helper.make_tensor_value_info("logits", TensorProto.FLOAT, ["batch", 7])],
        [numpy_helper.from_array(rng.normal(0, 1, (3, 7)).astype(np.float32), "weights")],
    )
    network = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    network.ir_version = 9
    return network


def write_notebook_package(
    folder: Path, tags: tuple[str, ...] = ("custom_resnet", "swin_base", "dinov2_vitb", "seresnext101")
) -> Path:
    """The notebook's app_package.json, with .onnx files for the given models only."""
    (folder / "onnx").mkdir(parents=True)
    for seed, tag in enumerate(tags):
        onnx.save(tiny_network(seed), folder / "onnx" / f"{tag}.onnx")

    def settings(tag: str, shift: float) -> dict[str, Any]:
        return {
            "model": tag.upper(),
            "onnx": f"onnx/{tag}.onnx",
            "img_size": 64,
            "mean": [0.5, 0.5, 0.5],
            "std": [0.25, 0.25, 0.25],
            "tta_views": VIEWS,
            "decision_bias": [shift] * 6 + [0.0],
            "decision_bias_without_tta": [0.0] * 6 + [shift],
            "test_macro_f1": 0.7,
        }

    all_tags = ("custom_resnet", "swin_base", "dinov2_vitb", "seresnext101", "convnextv2_base", "eva02_base")
    singles = {tag: settings(tag, float(index)) for index, tag in enumerate(all_tags, 1)}
    package = {
        "classes": CLASSES,
        "ensemble": {
            "members": [singles[tag] for tag in ("convnextv2_base", "eva02_base", "swin_base")],
            "decision_bias": [0.5] * 6 + [0.0],
            "decision_bias_without_tta": [0.0] * 6 + [0.5],
            "test_macro_f1": 0.75,
        },
        "single_models": singles,
    }
    (folder / "app_package.json").write_text(json.dumps(package), encoding="utf-8")
    return folder


def write_package(folder: Path, mel_threshold: float = 0.3) -> Path:
    (folder / "onnx").mkdir(parents=True)
    tags = sorted({tag for option in DEFAULT_OPTIONS for tag in option["members"]})
    models = {}
    for seed, tag in enumerate(tags):
        onnx.save(tiny_network(seed), folder / "onnx" / f"{tag}.onnx")
        models[tag] = {
            "label": tag,
            "onnx": f"onnx/{tag}.onnx",
            "img_size": 64,
            "mean": [0.5, 0.5, 0.5],
            "std": [0.25, 0.25, 0.25],
            "tta_views": VIEWS,
        }
    settings = {
        level: {
            "views": n,
            "decision_bias": [0.1, 0.1, 0.0, -0.1, 0.2, -0.4, 0.1],
            "melanoma_thresholds": {"0.90": mel_threshold, "0.95": mel_threshold / 2},
            "scores": {"test_macro_f1": 0.8},
        }
        for level, n in LEVELS.items()
    }
    config = {
        "format": PACKAGE_FORMAT,
        "classes": CLASSES,
        "levels": LEVELS,
        "default_option": "swin",
        "default_level": "balanced",
        "models": models,
        "options": [{**option, "levels": settings} for option in DEFAULT_OPTIONS],
        "melanoma_warning": {"source": "option", "target_sensitivity": "0.90"},
    }
    (folder / "app_config.json").write_text(json.dumps(config), encoding="utf-8")
    return folder
