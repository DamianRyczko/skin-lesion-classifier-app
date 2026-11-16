import json
import os
from pathlib import Path
from typing import Any

PACKAGE_DIR = Path(os.environ.get("SKIN_APP_PACKAGE", Path(__file__).parents[1] / "weights" / "skin_lesions_app"))
CONFIG_FILE = "app_package.json"

# Index order = the order every model was trained with. Never reorder.
CLASS_CODES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]

# TTA views per model. The notebook tuned a decision bias for exactly these two counts.
LEVELS = {"fast": 1, "best": 12}
DEFAULT_LEVEL = "best"

OPTIONS: list[dict[str, Any]] = [
    {"id": "my_resnet", "label": "ResNet", "members": ["custom_resnet"]},
    {"id": "swin", "label": "Swin-Base", "members": ["swin_base"]},
    {"id": "dinov2", "label": "DINOv2 ViT-B", "members": ["dinov2_vitb"]},
    {"id": "seresnext", "label": "SE-ResNeXt-101", "members": ["seresnext101"]},
    {"id": "ensemble", "label": "Ensemble", "members": ["swin_base", "dinov2_vitb", "seresnext101"]},
]

# The photo moved by 5%, as crop windows.
SHIFTS = {
    "shift_up": [0.05, 0.0, 0.95, 0.9],
    "shift_down": [0.05, 0.1, 0.95, 1.0],
    "shift_left": [0.0, 0.05, 0.9, 0.95],
    "shift_right": [0.1, 0.05, 1.0, 0.95],
}


def _with_all_shifts(views: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # The TTA search skipped some shifts per model. A missing one replaces the last non-shift view,
    # so there are still 12 views (sorted most useful first) and the bias still fits.
    views = list(views)
    missing = [name for name in SHIFTS if name not in {view["name"] for view in views}]
    spare = [index for index in range(len(views) - 1, 0, -1) if views[index]["name"] not in SHIFTS]
    for index, name in zip(spare, missing, strict=False):
        views[index] = {"name": name, "crop": SHIFTS[name]}
    return views


def load_config(package_dir: Path) -> dict[str, Any]:
    """Options whose .onnx files are missing are left out."""
    if not (package_dir / CONFIG_FILE).exists():
        raise FileNotFoundError(f"no {CONFIG_FILE} in {package_dir}: put the trained models there, see weights/README.md")
    raw = json.loads((package_dir / CONFIG_FILE).read_text(encoding="utf-8"))
    if [c["code"] for c in raw["classes"]] != CLASS_CODES:
        raise ValueError(f"class order in {CONFIG_FILE} differs from the one the models were trained with")
    ready = {tag: model for tag, model in raw["single_models"].items() if (package_dir / model["onnx"]).exists()}
    # Each model keeps its own bias; an ensemble averages the biased results.
    options = [
        {
            **option,
            "bias": {
                "fast": [ready[tag]["decision_bias_without_tta"] for tag in option["members"]],
                "best": [ready[tag]["decision_bias"] for tag in option["members"]],
            },
        }
        for option in OPTIONS
        if all(tag in ready for tag in option["members"])
    ]
    if not options:
        raise FileNotFoundError(f"no model from {CONFIG_FILE} found in {package_dir}")
    used = {tag for option in options for tag in option["members"]}
    models = {
        tag: {
            **{key: ready[tag][key] for key in ("onnx", "img_size", "mean", "std")},
            "tta_views": _with_all_shifts(ready[tag]["tta_views"]),
        }
        for tag in used
    }
    ids = [option["id"] for option in options]
    return {"models": models, "options": options, "default_option": "swin" if "swin" in ids else ids[0]}
