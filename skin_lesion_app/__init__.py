"""Skin-lesion classifier (HAM10000, 7 classes): ONNX models + test-time augmentation + ensemble.

    from skin_lesion_app import SkinLesionPredictor
    predictor = SkinLesionPredictor("weights/skin_lesions_app")
    predictor.options()                                   # the 5 options with their scores
    result = predictor.predict("lesion.jpg", option="ensemble", level="balanced")
    result["prediction"], result["percentages"], result["melanoma_warning"]

Options: my_resnet | swin | dinov2 | seresnext | ensemble (Swin + DINOv2 + SE-ResNeXt)
Levels:  fast = 1 view per model | balanced = 4 views | best = 12 views (the views picked per model in the TTA search)

Knows nothing about Streamlit; `python -m skin_lesion_app` is the command line. Not a medical device: a student
project for decision support only.
"""

from .config import CLASS_CODES, CLASS_NAMES, CLASSES, DEFAULT_OPTIONS, DEFAULT_PACKAGE, DISCLAIMER, LEVELS, load_config
from .explain import GRID
from .predictor import SkinLesionPredictor

__all__ = [
    "SkinLesionPredictor",
    "CLASSES",
    "CLASS_CODES",
    "CLASS_NAMES",
    "DEFAULT_OPTIONS",
    "DEFAULT_PACKAGE",
    "DISCLAIMER",
    "GRID",
    "LEVELS",
    "load_config",
]
__version__ = "1.0.0"
