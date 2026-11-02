"""Upload -> crop -> analysis -> result."""

import streamlit as st
from loguru import logger
from PIL import Image
from streamlit.delta_generator import DeltaGenerator

from core.classes import CLASSES, RISK_THRESHOLD
from core.imaging import ALLOWED_TYPES, ImageError, apply_crop, default_box, image_id, load_image, preview_uri
from core.inference import Prediction, analyze, explain
from core.xai import overlay
from model import MODELS, PREDICTOR, is_loaded, load_model
from ui import components as ui
from ui import widgets

STEPS = ("1 Zdjęcie", "2 Kadrowanie", "3 Wynik")
STEP_INDEX = {"upload": 0, "crop": 1, "result": 2}
DISPLAY_SIDE = 720
LEVEL_LABELS = {"fast": "Bez TTA", "balanced": "TTA 4", "best": "TTA 12"}

s = st.session_state
s.setdefault("step", "upload")
s.setdefault("upload_round", 0)  # a new key is what clears st.file_uploader
s.setdefault("model_id", PREDICTOR.default_option)
s.setdefault("level", PREDICTOR.default_level)
s.setdefault("results", {})
s.setdefault("heatmaps", {})
s.setdefault("picked", None)


def reset() -> None:
    logger.info("reset")
    s.step = "upload"
    s.upload_round += 1
    s.results, s.heatmaps, s.picked = {}, {}, None
    s.pop("crop_box", None)


def on_upload() -> None:
    upload = s.get(f"upload_{s.upload_round}")
    if upload is None:
        return
    s.pop("upload_error", None)
    data = upload.getvalue()
    try:
        image = load_image(data)
    except ImageError as exc:
        logger.warning("upload rejected: {:.2f} MB", len(data) / 1e6)
        s.upload_error = str(exc)
        return
    s.original = image
    s.preview = preview_uri(image)
    s.step = "crop"
    logger.info("upload {:.2f} MB, {}x{}", len(data) / 1e6, *image.size)


def on_analyze(box: dict[str, float]) -> None:
    s.crop_box = box  # "Zmień kadr" comes back to this box
    s.crop = apply_crop(s.original, box)
    s.crop_key = image_id(s.crop)
    s.step = "result"
    s.picked = None
    logger.info("crop {} {}x{}", s.crop_key[:6], *s.crop.size)


def to_crop() -> None:
    s.step = "crop"


def on_model_change() -> None:
    s.model_id = s.model_choice
    s.picked = None
    logger.info("model switched to {}", MODELS[s.model_id].label)


def on_level_change() -> None:
    s.level = s.level_choice
    s.picked = None
    logger.info("level switched to {}", s.level)


def on_xai_change() -> None:
    logger.info("xai {}", "on" if s.xai else "off")


def model_control() -> DeltaGenerator:
    """The selector, plus a slot for its status: that is only known once the step has run."""
    s.model_choice = s.model_id  # the widgets' state is dropped whenever the upload step hides them
    s.level_choice = s.level
    with st.container(key="nbctrl", horizontal=True):
        ui.label("Model")
        st.segmented_control(
            "Model",
            list(MODELS),
            format_func=lambda m: MODELS[m].label,
            key="model_choice",
            required=True,
            label_visibility="collapsed",
            on_change=on_model_change,
        )
        ui.label("TTA")
        st.segmented_control(
            "TTA",
            PREDICTOR.levels,
            format_func=LEVEL_LABELS.__getitem__,
            key="level_choice",
            required=True,
            label_visibility="collapsed",
            on_change=on_level_change,
        )
        return st.empty()


def model_status(slot: DeltaGenerator) -> None:
    label = MODELS[s.model_id].label
    slot.html(ui.status(True, f"{label} załadowany") if is_loaded(s.model_id) else ui.mono(f"{label} załaduje się przy analizie"))


def upload_step() -> None:
    with ui.split("upload", [3, 2]) as (left, right):
        with left:
            if "upload_error" in s:
                ui.banner("Nie można użyć tego pliku", s.upload_error, warn=True)
            st.file_uploader(
                "Zdjęcie",
                type=list(ALLOWED_TYPES),
                key=f"upload_{s.upload_round}",
                label_visibility="collapsed",
                on_change=on_upload,
            )
        with right, ui.panel("tips"):
            with st.container(key="nbphead_tips", horizontal=True):
                ui.label("Dobre zdjęcie")
            ui.tips(
                [
                    "Ostre, zrobione z bliska.",
                    "Równe światło, bez lampy błyskowej.",
                    "Zmiana w środku kadru, z odrobiną zdrowej skóry wokół.",
                ]
            )


def crop_step() -> None:
    with ui.split("crop", [3, 2]) as (left, right):
        with left, ui.panel("crop"):
            start = s.get("crop_box") or default_box(s.original)
            box = widgets.cropper(s.preview, start, key=f"crop_{s.upload_round}")
        with right, ui.panel("crop_help"):
            with st.container(key="nbphead_crop", horizontal=True):
                ui.label("Wykadruj zmianę")
            with st.container(key="nbpbody_crop"):
                ui.note(
                    "Przesuń kwadrat tak, aby zmiana była na środku. Kadr jest kwadratowy, "
                    "bo w takim formacie model analizuje zdjęcie."
                )
            with st.container(key="nbpfoot_crop", horizontal=True):
                st.button("Analizuj", type="primary", on_click=on_analyze, args=(box,), key="analyze")
                st.button("Zmień zdjęcie", on_click=reset, key="change_photo")


def run_analysis() -> Prediction:
    """Result for the current crop and model, with the loading panel while it is computed."""
    result_key = (s.crop_key, s.model_id, s.level)
    if result_key not in s.results:
        spec = MODELS[s.model_id]
        slot = st.empty()
        with slot.container():
            loader = ui.Loader()
            if not is_loaded(spec.id):
                loader.update(f"Ładowanie: {spec.label}", "Wczytywanie wag modelu", 0, 1)
                load_model(spec.id)

            def on_view(done: int, total: int) -> None:
                loader.update(f"Analiza: {spec.label}", f"Widok TTA {done} z {total}", done, total)

            s.results[result_key] = analyze(spec, s.crop, s.crop_key, s.level, on_view)
        slot.empty()
    return s.results[result_key]


def shown_photo(prediction: Prediction, display: Image.Image) -> Image.Image:
    if not s.get("xai"):
        return display
    code = s.picked or prediction.top
    heat_key = (s.crop_key, s.model_id, code)
    if heat_key not in s.heatmaps:
        spec = MODELS[s.model_id]
        slot = st.empty()
        with slot.container():
            loader = ui.Loader("xai")

            def on_step(done: int, total: int) -> None:
                loader.update(f"Mapa XAI: {spec.label}", f"Zasłanianie fragmentów {done} z {total}", done, total)

            on_step(0, 1)
            s.heatmaps[heat_key] = explain(spec, s.crop, code, on_step)
        slot.empty()
    return overlay(display, s.heatmaps[heat_key], s.get("xai_opacity", 70) / 100)


def open_panel(code: str, prediction: Prediction) -> None:
    lesion = CLASSES[code]

    def body() -> None:
        ui.class_detail(
            code,
            ui.pct(prediction.probs[code]),
            lesion.tier,
            lesion.high_risk,
            lesion.about,
            lesion.advice,
            "Dane: HAM10000, Tschandl i in. 2018, CC BY-NC 4.0",
        )

    st.dialog(lesion.name, position="right", width="small", on_dismiss="rerun")(body)()


def photo_panel(prediction: Prediction) -> None:
    display = s.crop.copy()
    display.thumbnail((DISPLAY_SIDE, DISPLAY_SIDE))
    with ui.panel("photo"):
        with st.container(key="nbphead_photo", horizontal=True):
            ui.label("Twoje zdjęcie")
            st.toggle("Mapa XAI", key="xai", on_change=on_xai_change)
        st.image(shown_photo(prediction, display), width="stretch")
        if s.get("xai"):
            with st.container(key="nbpbody_xai"):
                code = s.picked or prediction.top
                ui.note(ui.join("Obszary, bez których spada wynik klasy:", ui.bold(CLASSES[code].name)))
                ui.xai_legend("mała uwaga", "duża uwaga")
                st.slider("Krycie", 20, 100, 70, key="xai_opacity")
        with st.container(key="nbpfoot_photo", horizontal=True):
            st.button("Nowe zdjęcie", on_click=reset, key="new_photo")
            st.button("Zmień kadr", on_click=to_crop, key="change_crop")


def result_panel(prediction: Prediction) -> str | None:
    """Returns the class code clicked in this run, if any."""
    spec = MODELS[prediction.model_id]
    with ui.panel("result"):
        with st.container(key="nbphead_result", horizontal=True):
            ui.label(f"Wynik: {spec.label}")
            if spec.mock:
                ui.html(ui.tag("Dane przykładowe"))
        rows = [
            dict(
                code=code,
                name=CLASSES[code].name,
                pct=ui.pct(p),
                width=p * 100,
                high=CLASSES[code].high_risk,
                top=code == prediction.top,
                selected=code == s.picked,
                aria=f"{CLASSES[code].name}, {ui.pct(p)}. Pokaż opis i zalecenia",
            )
            for code, p in prediction.probs.items()
        ]
        clicked = widgets.prob_rows(rows, key=f"rows_{prediction.model_id}")
        ui.hint("Kliknij klasę, aby zobaczyć opis i zalecenia.")
        if prediction.consult:
            if prediction.risk >= RISK_THRESHOLD:
                reason = f"Klasy złośliwe i przednowotworowe razem: {ui.pct(prediction.risk)}."
            elif prediction.melanoma:
                reason = "Model nie może wykluczyć czerniaka."
            else:
                reason = f"Najwyższy wynik: {CLASSES[prediction.top].name}."
            ui.banner("Zalecana konsultacja z dermatologiem", f"{reason} Pokaż tę zmianę lekarzowi.", warn=True)
        else:
            ui.banner(
                "Zalecenie: obserwacja",
                f"Klasy ryzyka razem: {ui.pct(prediction.risk)}, poniżej progu {ui.pct(RISK_THRESHOLD)}.",
                warn=False,
            )
        ui.status_bar(
            f"Widoki TTA na model: {prediction.n_views}", "średnia prawdopodobieństw", end="HAM10000 · 7 klas", inside=True
        )
    return clicked


def result_step() -> None:
    prediction = run_analysis()
    with ui.split("result", [5, 6]) as (left, right):
        with right:
            clicked = result_panel(prediction)
        if clicked:
            s.picked = clicked
            logger.info("panel opened: {}", clicked)
        with left:
            photo_panel(prediction)
    if clicked:
        open_panel(clicked, prediction)


ui.page_header("Analiza zmiany skórnej", side=[ui.steps(STEPS, STEP_INDEX[s.step])])

status_slot = model_control() if s.step != "upload" else None

{"upload": upload_step, "crop": crop_step, "result": result_step}[s.step]()

if status_slot:
    model_status(status_slot)
