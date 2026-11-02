import json
import shutil
import time
from pathlib import Path
from typing import Any

import numpy as np

from .config import CLASSES, DEFAULT_OPTIONS, DISCLAIMER, LEVELS, MEL, PACKAGE_FORMAT
from .predictor import SkinLesionPredictor

# Run ONCE in Colab (Drive mounted). Not needed by the app itself.
DRIVE = Path("/content/drive/MyDrive")
DEFAULT_COMPARE_DIR = DRIVE / "skin_lesions_v3_compare"  # the TTA comparison notebook's output
DEFAULT_V3_DIR = DRIVE / "skin_lesions_v3_cnn"  # split_cv.csv (same split in both v3 folders)
DEFAULT_OUT_DIR = DRIVE / "skin_lesions_app"

TARGETS = ("0.90", "0.95")  # melanoma warning: target sensitivities (thresholds stored for both)
BIAS_GRID = np.linspace(-2.5, 2.5, 101)


def _macro_f1(y: np.ndarray, pred: np.ndarray, k: int = len(CLASSES)) -> float:
    cm = np.bincount(np.asarray(y) * k + np.asarray(pred), minlength=k * k).reshape(k, k)
    tp, denom = np.diag(cm), cm.sum(0) + cm.sum(1)
    return float(np.where(denom > 0, 2 * tp / np.maximum(denom, 1), 0.0).mean())


def _tune_bias(probs: np.ndarray, y: np.ndarray, grid: np.ndarray = BIAS_GRID, passes: int = 4) -> np.ndarray:
    """Same search as the notebooks: one offset per class on log-probabilities, maximising macro-F1."""
    logp = np.log(np.clip(probs, 1e-8, 1.0))
    bias = np.zeros(probs.shape[1])
    best = _macro_f1(y, logp.argmax(1))
    for _ in range(passes):
        improved = False
        for c in range(probs.shape[1]):
            for value in grid:
                trial = bias.copy()
                trial[c] = value
                score = _macro_f1(y, (logp + trial).argmax(1))
                if score > best + 1e-6:
                    best, bias, improved = score, trial, True
        if not improved:
            break
    return bias - bias.mean()


def _apply_bias(probs: np.ndarray, bias: np.ndarray | list[float]) -> np.ndarray:
    return (np.log(np.clip(probs, 1e-8, 1.0)) + np.asarray(bias)).argmax(1)


def _cv_macro_f1(probs: np.ndarray, y: np.ndarray, folds: np.ndarray) -> float:
    """Honest OOF score: the bias for fold k is tuned on the other folds only."""
    pred = np.empty(len(y), dtype=int)
    for k in np.unique(folds):
        tr, va = folds != k, folds == k
        pred[va] = _apply_bias(probs[va], _tune_bias(probs[tr], y[tr]))
    return _macro_f1(y, pred)


def _bootstrap_ci(y: np.ndarray, pred: np.ndarray, n: int = 2000, seed: int = 42) -> list[float]:
    rng = np.random.default_rng(seed)
    vals = [_macro_f1(y[idx], pred[idx]) for idx in (rng.integers(0, len(y), len(y)) for _ in range(n))]
    return [round(float(np.percentile(vals, 2.5)), 4), round(float(np.percentile(vals, 97.5)), 4)]


def _auc(scores: np.ndarray, positive: np.ndarray) -> float:
    """ROC AUC via average ranks (ties counted half)."""
    scores, positive = np.asarray(scores, dtype=np.float64), np.asarray(positive, dtype=bool)
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(len(scores))
    s = scores[order]
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2 + 1
        i = j + 1
    n_pos, n_neg = positive.sum(), (~positive).sum()
    return float((ranks[positive].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def _threshold_for_sensitivity(scores: np.ndarray, positive: np.ndarray, target: float) -> float:
    """Largest threshold that still flags at least `target` of the positives (score >= threshold)."""
    pos = np.sort(np.asarray(scores)[np.asarray(positive, dtype=bool)])
    return float(pos[int(np.floor((1 - target) * len(pos)))])


def _warning_stats(scores: np.ndarray, positive: np.ndarray, threshold: float) -> dict[str, float]:
    flagged, positive = np.asarray(scores) >= threshold, np.asarray(positive, dtype=bool)
    tp, fp = int((flagged & positive).sum()), int((flagged & ~positive).sum())
    return {
        "sensitivity": round(tp / max(positive.sum(), 1), 4),
        "specificity": round(int((~flagged & ~positive).sum()) / max((~positive).sum(), 1), 4),
        "ppv": round(tp / max(tp + fp, 1), 4),
        "alerts_per_100": round(100 * flagged.mean(), 1),
    }


def _find_images(images_dir: str | Path | None = None) -> dict[str, str] | None:
    """image_id -> path, for the self-test. Uses images_dir, or the Kaggle copy (kagglehub) when available."""
    import glob

    try:
        if images_dir is None:
            import kagglehub

            images_dir = kagglehub.dataset_download("kmader/skin-cancer-mnist-ham10000")
        paths = glob.glob(str(Path(images_dir) / "**" / "*.jpg"), recursive=True)
        return {Path(p).stem: p for p in paths} or None
    except Exception as e:  # no kagglehub / no network: skip the self-test
        print(f"self-test skipped (images not found: {type(e).__name__})")
        return None


def build_package(
    compare_dir: str | Path = DEFAULT_COMPARE_DIR,
    v3_dir: str | Path = DEFAULT_V3_DIR,
    out_dir: str | Path = DEFAULT_OUT_DIR,
    options: list[dict[str, Any]] | None = None,
    default_option: str = "swin",
    default_level: str = "balanced",
    n_boot: int = 2000,
    selftest: int = 5,
    images_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Builds out_dir/{app_config.json, onnx/*.onnx, app_report.md} from the TTA comparison notebook's results."""
    import pandas as pd

    t_start = time.time()
    compare_dir, v3_dir, out_dir = Path(compare_dir), Path(v3_dir), Path(out_dir)
    options = options or DEFAULT_OPTIONS
    (out_dir / "onnx").mkdir(parents=True, exist_ok=True)

    split = pd.read_csv(v3_dir / "split_cv.csv")
    dev, test = ~split["is_test"].values, split["is_test"].values
    y_dev, y_test = split["label"].values[dev], split["label"].values[test]
    folds = split["cv_fold"].values[dev]
    pkg = json.loads((compare_dir / "app_package.json").read_text())
    policy = json.loads((compare_dir / "tta_policy.json").read_text())

    # per-view predictions saved by the comparison notebook -> reordered into each model's greedy view order
    tags = sorted({t for o in options for t in o["members"]})
    oof: dict[str, np.ndarray] = {}
    tst: dict[str, np.ndarray] = {}
    models: dict[str, dict[str, Any]] = {}
    for t in tags:
        d = compare_dir / "tta_probs" / t
        names = json.loads((d / "views.json").read_text())
        order = [names.index(v) for v in policy[t]]
        o = np.full((dev.sum(), len(names), len(CLASSES)), np.nan, dtype=np.float32)
        for k in np.unique(folds):
            o[folds == k] = np.load(d / f"oof_fold{k}.npy")
        assert not np.isnan(o).any(), f"{t}: out-of-fold predictions incomplete"
        oof[t], tst[t] = o[:, order], np.load(d / "final_test.npy")[:, order]
        single = pkg["single_models"][t]
        assert [v["name"] for v in single["tta_views"]] == policy[t], f"{t}: view order mismatch"
        src = compare_dir / single["onnx"]
        dst = out_dir / "onnx" / f"{t}.onnx"
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dst)
        models[t] = {
            "label": single["model"],
            "onnx": f"onnx/{t}.onnx",
            "img_size": single["img_size"],
            "mean": single["mean"],
            "std": single["std"],
            "tta_views": single["tta_views"],
        }
        print(f"loaded {single['model']}: {len(policy[t])} views, ONNX {dst.stat().st_size / 1e6:.0f} MB")

    rows: list[dict[str, str]] = []
    option_entries: list[dict[str, Any]] = []
    expected: dict[tuple[str, str], np.ndarray] = {}
    for opt in options:
        levels = {}
        for level, n in LEVELS.items():
            p_oof = np.mean([oof[t][:, :n].mean(1) for t in opt["members"]], axis=0)
            p_test = np.mean([tst[t][:, :n].mean(1) for t in opt["members"]], axis=0)
            bias = _tune_bias(p_oof, y_dev)
            pred = _apply_bias(p_test, bias)
            mel_oof, mel_test = y_dev == MEL, y_test == MEL
            thresholds = {tg: _threshold_for_sensitivity(p_oof[:, MEL], mel_oof, float(tg)) for tg in TARGETS}
            scores: dict[str, Any] = {
                "test_macro_f1": round(_macro_f1(y_test, pred), 4),
                "test_macro_f1_ci95": _bootstrap_ci(y_test, pred, n_boot),
                "oof_macro_f1": round(_cv_macro_f1(p_oof, y_dev, folds), 4),
                "test_accuracy": round(float((pred == y_test).mean()), 4),
                "melanoma_auc_oof": round(_auc(p_oof[:, MEL], mel_oof), 4),
                "melanoma_auc_test": round(_auc(p_test[:, MEL], mel_test), 4),
                "melanoma_warning_test": {tg: _warning_stats(p_test[:, MEL], mel_test, thresholds[tg]) for tg in TARGETS},
            }
            levels[level] = {
                "views": n,
                "decision_bias": [round(float(b), 4) for b in bias],
                "melanoma_thresholds": {tg: round(v, 6) for tg, v in thresholds.items()},
                "scores": scores,
            }
            expected[(opt["id"], level)] = p_test
            w = scores["melanoma_warning_test"]["0.90"]
            low, high = scores["test_macro_f1_ci95"]
            warning = f"{w['sensitivity']:.2f} / {w['specificity']:.2f} / {w['alerts_per_100']:.0f}"
            rows.append(
                {
                    "option": opt["label"],
                    "level": f"{level} ({n})",
                    "test macro-F1 [95% CI]": f"{scores['test_macro_f1']:.3f} [{low:.3f}-{high:.3f}]",
                    "OOF macro-F1": f"{scores['oof_macro_f1']:.3f}",
                    "melanoma AUC (test)": f"{scores['melanoma_auc_test']:.3f}",
                    "mel warning @90%: sens / spec / alerts per 100": warning,
                }
            )
        option_entries.append({**opt, "levels": levels})

    config = {
        "format": PACKAGE_FORMAT,
        "created": time.strftime("%Y-%m-%d %H:%M"),
        "classes": CLASSES,
        "levels": LEVELS,
        "default_option": default_option,
        "default_level": default_level,
        "models": models,
        "options": option_entries,
        "melanoma_warning": {
            "source": "option",
            "target_sensitivity": "0.90",
            "note": "score = the option's mean softmax probability of 'mel' (before the decision "
            "bias); flag when score >= threshold tuned on out-of-fold data",
        },
        "preprocessing": "EXIF rotation -> RGB -> centre crop to at most 4:3 -> long side 600 px -> per view: crop / "
        "shrink -> resize to img_size (bilinear) -> rotate -> colour -> 90-degree turns / flip -> "
        "/255 -> (x - mean) / std -> NCHW float32",
        "disclaimer": DISCLAIMER,
    }
    (out_dir / "app_config.json").write_text(json.dumps(config, indent=1), encoding="utf-8")

    table = pd.DataFrame(rows)
    try:
        table_text = table.to_markdown(index=False)  # needs the 'tabulate' package (Colab has it)
    except ImportError:
        table_text = table.to_string(index=False)
    report = [
        "# Skin-lesion app: model options",
        "",
        f"Built {config['created']}. Test set: {test.sum()} HAM10000 images that were never used for any "
        f"choice. OOF = out-of-fold predictions on the other {dev.sum()} images (decision bias tuned per "
        "fold). Melanoma warning: threshold tuned on OOF to catch 90 % of melanomas.",
        "",
        table_text,
    ]
    (out_dir / "app_report.md").write_text("\n".join(report), encoding="utf-8")
    with pd.option_context("display.max_colwidth", 60, "display.width", 250):
        print("\n" + table.to_string(index=False))

    if selftest:  # the app pipeline vs. the notebook's GPU pipeline
        id_to_path = _find_images(images_dir)
        if id_to_path:
            predictor = SkinLesionPredictor(out_dir)
            test_ids = split["image_id"].values[test][:selftest]
            print(f"\nself-test on {len(test_ids)} test images (app pipeline on CPU vs. notebook pipeline on GPU):")
            for opt in options:
                for level in ("fast", "best"):
                    t0 = time.time()
                    mine = np.array([predictor.probabilities(id_to_path[i], opt["id"], level) for i in test_ids])
                    ref = expected[(opt["id"], level)][: len(test_ids)]
                    bias = option_entries[[o["id"] for o in options].index(opt["id"])]["levels"][level]["decision_bias"]
                    same = np.mean(_apply_bias(mine, bias) == _apply_bias(ref, bias)) * 100
                    print(
                        f"  {opt['label']:40s} {level:8s} same class {same:5.1f}% | max prob diff "
                        f"{np.abs(mine - ref).max():.3f} | {(time.time() - t0) / len(test_ids):.2f}s per image"
                    )
    print(f"\nApp package written to {out_dir} in {(time.time() - t_start) / 60:.1f} min")
    return config
