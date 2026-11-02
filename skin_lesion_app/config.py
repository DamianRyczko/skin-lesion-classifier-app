import json
import os
from pathlib import Path
from typing import Any

PACKAGE_FORMAT = "skin-lesion-app/1"
CONFIG_FILES = ("app_config.json", "app_package.json")  # build.py's output, or the notebook's export

# Where the model folder lives: build.py's output, dropped into weights/ unchanged.
DEFAULT_PACKAGE = Path(os.environ.get("SKIN_APP_PACKAGE", Path(__file__).parents[1] / "weights" / "skin_lesions_app"))

# Index order = the order every model was trained with (sorted codes). Never reorder.
CLASSES: list[dict[str, Any]] = [
    {"index": 0, "code": "akiec", "name": "Actinic keratoses / intraepithelial carcinoma"},
    {"index": 1, "code": "bcc", "name": "Basal cell carcinoma"},
    {"index": 2, "code": "bkl", "name": "Benign keratosis-like lesions"},
    {"index": 3, "code": "df", "name": "Dermatofibroma"},
    {"index": 4, "code": "mel", "name": "Melanoma"},
    {"index": 5, "code": "nv", "name": "Melanocytic nevi"},
    {"index": 6, "code": "vasc", "name": "Vascular lesions"},
]
CLASS_CODES: list[str] = [c["code"] for c in CLASSES]
CLASS_NAMES: dict[str, str] = {c["code"]: c["name"] for c in CLASSES}
MEL = CLASS_CODES.index("mel")

# Quality levels = how many test-time-augmentation views each model sees. The views of every model are
# stored in greedy order (most useful first; the first one is always the plain image), so a level simply
# uses the first N. Each level has its own decision bias and melanoma thresholds, tuned for exactly that N.
LEVELS = {"fast": 1, "balanced": 4, "best": 12}

# The photo moved by 5%, as crop windows: the notebook's shift views.
SHIFTS = {
    "shift_up": [0.05, 0.0, 0.95, 0.9],
    "shift_down": [0.05, 0.1, 0.95, 1.0],
    "shift_left": [0.0, 0.05, 0.9, 0.95],
    "shift_right": [0.1, 0.05, 1.0, 0.95],
}

# The 5 app options. Edit here to change the line-up (members = model tags from the v3 notebooks).
DEFAULT_OPTIONS: list[dict[str, Any]] = [
    {
        "id": "my_resnet",
        "label": "My ResNet",
        "description": "My 14-block residual CNN, trained from scratch on HAM10000",
        "members": ["custom_resnet"],
    },
    {
        "id": "swin",
        "label": "Swin-Base",
        "description": "Hierarchical vision transformer, pretrained on ImageNet-22k",
        "members": ["swin_base"],
    },
    {
        "id": "dinov2",
        "label": "DINOv2 ViT-B",
        "description": "Vision transformer pretrained without labels on 142 M images (Meta DINOv2)",
        "members": ["dinov2_vitb"],
    },
    {
        "id": "seresnext",
        "label": "SE-ResNeXt-101",
        "description": "101-layer ResNet with grouped convolutions and channel attention, ImageNet-12k pretrained",
        "members": ["seresnext101"],
    },
    {
        "id": "ensemble",
        "label": "Ensemble: Swin + DINOv2 + SE-ResNeXt",
        "description": "Average of the three transfer-learning models (different families, different mistakes)",
        "members": ["swin_base", "dinov2_vitb", "seresnext101"],
    },
]

DISCLAIMER = (
    "Student project for decision support only, not a medical device. The models were trained on "
    "dermoscopy images (HAM10000); ordinary phone photos are outside what they were trained on. "
    "Percentages are model scores, not calibrated probabilities. Have any changing or worrying "
    "lesion checked by a doctor."
)


def _notebook_levels(model: dict[str, Any]) -> dict[str, Any]:
    """The notebook tuned the bias for all 12 views and for none, so these are the only levels it can offer."""
    return {
        "fast": {"decision_bias": model["decision_bias_without_tta"], "scores": {}},
        "best": {"decision_bias": model["decision_bias"], "scores": {"test_macro_f1": model["test_macro_f1"]}},
    }


def _notebook_ensemble_levels(members: list[dict[str, Any]]) -> dict[str, Any]:
    """Each model keeps its own bias and predict() averages the results, so this line-up needs no bias of its own."""
    single = [_notebook_levels(member) for member in members]
    return {level: {"member_bias": [s[level]["decision_bias"] for s in single], "scores": {}} for level in single[0]}


def _with_all_shifts(views: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every model sees the photo moved all four ways. The TTA search skipped some per model, so a missing shift
    replaces the last view that isn't one: views are sorted most useful first, and the bias still fits 12 views."""
    views = list(views)
    missing = [name for name in SHIFTS if name not in {view["name"] for view in views}]
    spare = [index for index in range(len(views) - 1, 0, -1) if views[index]["name"] not in SHIFTS]
    for index, name in zip(spare, missing, strict=False):
        views[index] = {"name": name, "crop": SHIFTS[name]}
    return views


def _from_notebook(raw: dict[str, Any], package_dir: Path) -> dict[str, Any]:
    """app_package.json -> the shape build.py writes. It holds no melanoma thresholds, so that warning stays off.
    Options whose .onnx files are not in the folder are left out."""
    ready = {tag: model for tag, model in raw["single_models"].items() if (package_dir / model["onnx"]).exists()}
    options = []
    for option in DEFAULT_OPTIONS:
        if all(tag in ready for tag in option["members"]):
            members = [ready[tag] for tag in option["members"]]
            levels = _notebook_levels(members[0]) if len(members) == 1 else _notebook_ensemble_levels(members)
            options.append({**option, "levels": levels})
    if not options:
        raise FileNotFoundError(f"no model from app_package.json found in {package_dir}")
    used = {tag for option in options for tag in option["members"]}
    return {
        "format": PACKAGE_FORMAT,
        "classes": raw["classes"],
        "default_option": "swin" if "swin_base" in used else options[0]["id"],
        "default_level": "best",
        "models": {
            tag: {
                "label": ready[tag]["model"],
                **{key: ready[tag][key] for key in ("onnx", "img_size", "mean", "std")},
                "tta_views": _with_all_shifts(ready[tag]["tta_views"]),
            }
            for tag in used
        },
        "options": options,
    }


def load_config(package_dir: str | Path) -> dict[str, Any]:
    """Reads and checks the package's settings: app_config.json if there is one, else app_package.json."""
    package_dir = Path(package_dir)
    built, notebook = (package_dir / name for name in CONFIG_FILES)
    if built.exists():
        cfg = json.loads(built.read_text(encoding="utf-8"))
    else:
        cfg = _from_notebook(json.loads(notebook.read_text(encoding="utf-8")), package_dir)
    if cfg.get("format") != PACKAGE_FORMAT:
        raise ValueError(f"unexpected app_config format {cfg.get('format')!r}, expected {PACKAGE_FORMAT!r}")
    if [c["code"] for c in cfg["classes"]] != CLASS_CODES:
        raise ValueError("class order in app_config.json differs from the one the models were trained with")
    missing = [m["onnx"] for m in cfg["models"].values() if not (package_dir / m["onnx"]).exists()]
    if missing:
        raise FileNotFoundError(f"model files missing in {package_dir}: {missing}")
    return cfg
