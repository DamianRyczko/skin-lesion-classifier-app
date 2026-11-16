# Skin lesion classifier app

Streamlit app that classifies a skin lesion photo into the 7 HAM10000 classes. Student project, not a medical device.

## Setup

Needs [mise](https://mise.jdx.dev).

```bash
mise trust && mise install
mise run setup
mise run dev        # http://localhost:8501
```

Or with Docker: `docker compose up --build`.

## Weights

Not in git. Put the training notebook's export here:

```
weights/skin_lesions_app/
├── app_package.json
└── onnx/
    ├── custom_resnet.onnx
    ├── dinov2_vitb.onnx
    ├── seresnext101.onnx
    └── swin_base.onnx
```

Without them the app does not start.

## Structure

```
app.py, pages/      the app
skin_lesion_app/    the models
core/, ui/          logic and look
assets/             images, including one sample photo per class
tests/              mise run test, mise run e2e
```

## Data

HAM10000, Tschandl et al. 2018, CC BY-NC 4.0 (sample photos in `assets/samples/` included).
