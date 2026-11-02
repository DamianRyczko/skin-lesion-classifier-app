# Skin lesion classifier app

Polish Streamlit app that classifies skin lesions into the 7 HAM10000 classes.
Upload a photo, crop it, and see per-class percentages next to the image. Click a
class for a description and recommendation. The theme is Cat City, in warm white
or dark blue cyberpunk.

Until the trained models are in `weights/skin_lesions_app/`, **results are mock data**
and the app labels them "Dane przykładowe". See [weights/README.md](weights/README.md).

## Run

```bash
mise trust && mise install   # trusts this repo's mise.toml, installs uv
mise run setup               # Python 3.14, dependencies, git hooks
mise run dev                 # http://localhost:8501, logs in this terminal
```

Without mise: `uv sync && uv run pre-commit install && uv run streamlit run app.py`.
With Docker: `mise run docker` or `docker compose up --build`.

| Task | What it does |
|---|---|
| `mise run test` | unit and app tests |
| `mise run e2e` | browser tests with Playwright |
| `mise run check` | ruff, mypy and the UI style rules |
| `mise run format` | format and auto-fix with ruff |
| `mise run sprites` | regenerate the pixel art |

Browser tests need two system libraries that Ubuntu on WSL lacks by default. Install
them once with `sudo apt-get install libnspr4 libnss3`.

## Code quality

Every commit runs ruff, the UI style rules, mypy and the unit and app tests, about 20
seconds in total. If ruff changes a file, stage it and commit again. Browser tests stay
out of the hook because they take a minute; run `mise run e2e` before bigger changes.

In VS Code, open the inner `skin_lesion_classifier_app/` folder itself. Settings in `.vscode/` then format and
fix each Python file with ruff on save, and use the project's `.venv` for mypy and tests.
Opened from a parent folder, VS Code ignores them.

## Logs

The terminal running the app shows what the site is doing, one line per event, with
a short session id so parallel tabs stay readable:

```
02:50:40 INFO    e9177a crop 2adf90 576x576
02:50:41 INFO    e9177a model Swin-Base loading
02:50:43 INFO    e9177a result Swin-Base balanced 2adf90: mel 91.7%, risk 94.0%, melanoma score 91.7%/50.0%, consult (4 views, 1.00s)
```

`LOG_LEVEL=DEBUG mise run dev` also prints every TTA view. Photos are never logged.

## How a result is made

1. **Crop:** a square crop, scaled to the 600 px the models saw in training.
2. **TTA** ([skin_lesion_app/views.py](skin_lesion_app/views.py)): 1 or 12 views per
   model, depending on the level, plus 4 with a full `app_config.json`. They are fixed,
   picked per model in the TTA search, so the same photo always gives the same result.
   With `app_package.json`, every model's 12 views include the photo moved up, down, left
   and right: a shift the search left out replaces the last view that isn't a shift.
3. **Average:** softmax over each model's views, which adds up to 100%.
4. **Decision bias:** an offset per class, tuned for the model and level. The bars show
   the result, so the tallest bar is the predicted class. With `app_package.json` an
   ensemble does this for each of its models and averages the three results; a full
   `app_config.json` has one bias tuned for their average.
5. **Recommendation** ([core/inference.py](core/inference.py)): the app recommends a
   dermatologist if `mel` + `bcc` + `akiec` reach 25% of the bars together
   (`RISK_THRESHOLD` in [core/classes.py](core/classes.py)), or if one of them is the
   tallest bar. With a full `app_config.json`
   it also does so if the melanoma score before the bias reaches the threshold tuned
   for 90% sensitivity; `app_package.json` has no such thresholds.
6. **XAI** ([skin_lesion_app/explain.py](skin_lesion_app/explain.py)): the toggle
   overlays a map for the top class, or the last clicked one. ONNX files hold no
   gradients, so this is occlusion rather than Grad-CAM: 7 × 7 parts of the image are
   covered in turn, and the map shows where the class score falls most. That is 49
   model runs, three times that for the ensemble, and the result is cached per photo.

## Models

| Option | Network | Training |
|---|---|---|
| `my_resnet` | custom 14-block residual CNN | from scratch on HAM10000 |
| `swin` (default) | Swin-Base | ImageNet-22k pretrained |
| `dinov2` | DINOv2 ViT-B | self-supervised on 142 M images |
| `seresnext` | SE-ResNeXt-101 | ImageNet-12k pretrained |
| `ensemble` | Swin-Base + DINOv2 ViT-B + SE-ResNeXt-101 | average of the three |

[skin_lesion_app/](skin_lesion_app/) holds everything about them and knows nothing about
Streamlit. It also works from the command line:

```bash
uv run python -m skin_lesion_app options                 # the options and their test scores
uv run python -m skin_lesion_app predict lesion.jpg --option ensemble --level best
uv run python -m skin_lesion_app benchmark               # every option and level: heavy, use Colab rather than WSL
```

`build` runs once in Colab and writes a fuller folder for `weights/`; it needs pandas,
which the app does not install. [model.py](model.py) only chooses between that folder
and the mock, which runs through the same predictor.

## Layout

```
app.py          entry: theme, top bar, the page
model.py        trained package or mock, shared loading
skin_lesion_app/  the models: config, TTA views, ONNX, predictor, occlusion map, Colab build, CLI
pages/          analyze.py
core/           classes and texts, imaging, inference, xai overlay, logging
ui/             neubrutal kit: tokens, theme, components, widgets, assets
assets/         pixel art, optional class sample photos (the panel shows a placeholder without them)
weights/        the model folder, git-ignored
.vscode/        ruff on save, interpreter, test discovery
scripts/        pixel art generator
tests/          unit/, apptest/, e2e/
```

Rules for UI work are in `.claude/skills/streamlit-neubrutal-ui/`.

## Data

HAM10000: Tschandl, Rosendahl, Kittler. *The HAM10000 dataset*, Scientific Data 5:180161
(2018). CC BY-NC 4.0: non-commercial use with attribution.
