# Model weights

The app reads one folder: the training notebook's export, unchanged.

```
weights/skin_lesions_app/
├── app_package.json
└── onnx/
    ├── custom_resnet.onnx
    ├── dinov2_vitb.onnx
    ├── seresnext101.onnx
    └── swin_base.onnx
```

Then restart the app. The terminal prints `weights: ...` with the folder and the options
in use.

A model whose `.onnx` is missing just has no button, and neither does an ensemble that needs it.
The ensemble is Swin + DINOv2 + SE-ResNeXt; each model keeps its own decision bias and the
results are averaged.

## When something is wrong

- **No `app_package.json`:** the app stops with an error that points here.
- **`app_package.json` with no matching `.onnx` file:** the app stops with an error.
- **A different class order:** the app stops with an error.

Everything in this folder except this README is git-ignored. Docker mounts it read-only.
To keep the folder somewhere else, set `SKIN_APP_PACKAGE`.
