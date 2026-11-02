# Project context

Keep current. Claude reads this before writing UI copy or deciding what a page shows.

## What the app is

Skin lesion classifier app: a study project (computer engineering, medical IT specialisation). Polish-language
Streamlit app classifying skin lesions into the 7 HAM10000 classes. It is not published.

- The trained models live in `weights/skin_lesions_app/`, git-ignored. Without that folder `model.py` serves
  a mock, and results are tagged `ui.tag("Dane przykładowe")` automatically while `ModelSpec.mock` is true.
- UI language: Polish. Reply to the owner in their language.

## Notices

Only "To nie jest diagnoza" is shown, at the bottom of every page. Do not add other notices,
warnings or limitations (photo quality, skin tone, etc.) unless the owner asks for them.

## Classes and recommendations

Names, tiers and panel texts live in `core/classes.py`, the only source.

- High-risk classes: `mel`, `bcc`, `akiec`.
- `RISK_THRESHOLD = 0.25`: when their sum reaches it, the app recommends a dermatologist even if a
  benign class is on top. It was raised from 15% because 7 classes share one probability. High recall
  matters, but an app that only ever says "see a dermatologist" is useless, so do not lower it casually.

## Visual motif

Cat City: pixel art cats and a skyline with cat-eared buildings. Two themes: warm white, and cyberpunk
on dark blue. The doctor cat is clean pixel art about 150 px tall, standing in a white coat with the magnifier, with a cyberpunk version in night vision goggles for the dark theme, shown at exact multiples of its size so pixels stay even. The loading cat is the same character trotting side-on in a ribbon, in the same two versions. `scripts/make_sprites.py` generates all of it.

## Pages

The app has one page, Analiza: upload, square crop, loading panel, photo + clickable probability bars,
slide-out panel, XAI toggle. The owner removed the "O projekcie" page; do not add pages they did not ask for.

## Naming

- App name in the top bar: KLASYFIKATOR ZMIAN SKÓRNYCH (`app.py`).
- Percentages use Polish format through `ui.pct`: `78%`, `1,5%`.
