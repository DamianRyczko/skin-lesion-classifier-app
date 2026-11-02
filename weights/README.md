# Model weights

The app reads one folder. The settings file is either the notebook's `app_package.json`
or `app_config.json` from `skin_lesion_app build`; if both are there, `app_config.json` wins.

```
weights/skin_lesions_app/
├── app_package.json    or app_config.json
└── onnx/
    ├── custom_resnet.onnx
    ├── dinov2_vitb.onnx
    ├── seresnext101.onnx
    └── swin_base.onnx
```

Then restart the app. The terminal prints `weights: ...` with the folder and the options
in use, and the "Dane przykładowe" tag is gone. To check the folder without the app:

```bash
uv run python -m skin_lesion_app options
```

## What each settings file gives

| | `app_package.json` | `app_config.json` |
|---|---|---|
| TTA buttons | Bez TTA (1 view), TTA 12 | also TTA 4 |
| Melanoma threshold | no, the 25% rule decides alone | yes |
| Ensemble bias | each model's own, results averaged | one tuned for the average |

The ensemble is Swin + DINOv2 + SE-ResNeXt with either file. `app_package.json` has no 4-view
bias and no melanoma thresholds, so the app does not offer what would have to be invented.
A model whose `.onnx` is missing just has no button, and neither does an ensemble that needs it.

## When something is wrong

- **No settings file:** the app runs on the mock.
- **`app_package.json` with no matching `.onnx` file:** the app stops with an error.
- **`app_config.json` with a missing `.onnx` file:** the app stops with an error.
- **A different class order in either file:** the app stops with an error.

The app never falls back to the mock here, because mock results must not pass for real ones.

Everything in this folder except this README is git-ignored. Docker mounts it read-only.
To keep the folder somewhere else, set `SKIN_APP_PACKAGE`.

## Later: S3 and SageMaker

The folder is the whole contract, format `skin-lesion-app/1`. An S3 sync that fills
it before the app starts, or a SageMaker retraining job that ends in `build`, needs no
change in the app.
