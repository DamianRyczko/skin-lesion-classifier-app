import argparse
import json
import time

import numpy as np
from PIL import Image

from .build import build_package
from .config import DEFAULT_PACKAGE, LEVELS
from .predictor import SkinLesionPredictor


def _print_options(predictor: SkinLesionPredictor) -> None:
    print(f"{'option':12s} {'label':40s} test macro-F1")
    for o in predictor.options():
        scores = ", ".join(f"{level} {f1:.3f}" for level, f1 in o["test_macro_f1"].items() if f1 is not None)
        print(f"{o['id']:12s} {o['label']:40s} {scores}")
    print(f"default: {predictor.default_option} / {predictor.default_level}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="HAM10000 skin-lesion classifier (ONNX)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("options", help="list the options and their test scores")
    p.add_argument("--package", default=DEFAULT_PACKAGE)
    p = sub.add_parser("predict", help="classify one or more images")
    p.add_argument("images", nargs="+")
    p.add_argument("--package", default=DEFAULT_PACKAGE)
    p.add_argument("--option", default=None)
    p.add_argument("--level", default=None, choices=list(LEVELS))
    p = sub.add_parser("benchmark", help="seconds per image for every option and level")
    p.add_argument("--package", default=DEFAULT_PACKAGE)
    p.add_argument("--image", default=None, help="image to use (default: a synthetic one)")
    p.add_argument("--repeat", type=int, default=2)
    p = sub.add_parser("build", help="(Colab) build the model folder from the v3 results")
    p.add_argument("--compare-dir", default=None)
    p.add_argument("--v3-dir", default=None)
    p.add_argument("--out", default=None)
    p.add_argument("--images-dir", default=None, help="HAM10000 images for the self-test (default: kagglehub)")
    p.add_argument("--selftest", type=int, default=5, help="test images for the CPU self-test (0 = skip)")
    p.add_argument("--default-option", default="swin")
    p.add_argument("--default-level", default="balanced", choices=list(LEVELS))
    args = ap.parse_args(argv)

    if args.cmd == "build":
        kw = {k: v for k, v in {"compare_dir": args.compare_dir, "v3_dir": args.v3_dir, "out_dir": args.out}.items() if v}
        build_package(
            **kw,
            default_option=args.default_option,
            default_level=args.default_level,
            selftest=args.selftest,
            images_dir=args.images_dir,
        )
        return
    predictor = SkinLesionPredictor(args.package)
    if args.cmd == "options":
        _print_options(predictor)
    elif args.cmd == "predict":
        for image in args.images:
            print(json.dumps({"image": image, **predictor.predict(image, args.option, args.level)}, indent=2))
    elif args.cmd == "benchmark":
        img = args.image or Image.fromarray(np.random.default_rng(0).integers(0, 255, (450, 600, 3), dtype=np.uint8))
        print(f"{'option':12s} {'level':9s} seconds per image")
        for o in predictor.options():
            for level in predictor.levels:
                predictor.predict(img, o["id"], level)  # warm-up (loads the models)
                t0 = time.perf_counter()
                for _ in range(args.repeat):
                    predictor.predict(img, o["id"], level)
                print(f"{o['id']:12s} {level:9s} {(time.perf_counter() - t0) / args.repeat:.2f}")
