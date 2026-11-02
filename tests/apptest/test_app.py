"""The app without a browser. The cropper and rows are custom components that
AppTest cannot click, so the flow starts from a confirmed crop."""

import io
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import model

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def app() -> AppTest:
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20)
    at.run()
    assert not at.exception
    return at


def html_text(at: AppTest) -> str:
    return " ".join(str(element.proto.body) for element in at.html)


def png_bytes(lesion_image) -> bytes:
    buffer = io.BytesIO()
    lesion_image.save(buffer, "PNG")
    return buffer.getvalue()


def to_crop(at: AppTest, data: bytes) -> AppTest:
    at.file_uploader[0].upload("lesion.png", data, "image/png").run()
    assert not at.exception
    return at


def test_starts_on_upload_in_polish(app):
    text = html_text(app)
    assert "ANALIZA ZMIANY" in text.upper()
    assert "To nie jest diagnoza" in text
    assert app.session_state["step"] == "upload"


def test_no_photo_quality_notice(app):
    assert "dermatoskopow" not in html_text(app)


def test_theme_comes_from_the_url(app):
    """The click itself is covered in tests/e2e: AppTest loses state after a callback changes query params."""
    assert "--nb-bg:#F4EFEA" in html_text(app)
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20)
    at.query_params["theme"] = "dark"
    at.run()
    assert "--nb-bg:#0A1230" in html_text(at)


def test_unknown_theme_in_url_falls_back(app):
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20)
    at.query_params["theme"] = "neon"
    at.run()
    assert not at.exception
    assert at.session_state["theme"] == "light"


def test_bad_file_stays_on_upload_with_a_message(app):
    to_crop(app, b"not an image")
    assert app.session_state["step"] == "upload"
    assert "Nie można użyć tego pliku" in html_text(app)


def test_upload_moves_to_crop(app, lesion_image):
    to_crop(app, png_bytes(lesion_image))
    assert app.session_state["step"] == "crop"
    assert [button.label for button in app.button] == ["Analizuj", "Zmień zdjęcie"]


def test_analysis_gives_a_result_and_caches_it(app, lesion_image):
    to_crop(app, png_bytes(lesion_image))
    app.button(key="analyze").click().run()
    assert not app.exception
    assert app.session_state["step"] == "result"
    assert "Wynik: Swin-Base" in html_text(app)
    assert "Dane przykładowe" in html_text(app)
    assert "załadowany" in html_text(app)
    assert len(app.session_state["results"]) == 1
    app.toggle(key="xai").set_value(True).run()
    assert not app.exception
    assert len(app.session_state["results"]) == 1


def test_switching_models_runs_each_once(app, lesion_image):
    to_crop(app, png_bytes(lesion_image))
    app.button(key="analyze").click().run()
    app.button_group(key="model_choice").set_value("dinov2").run()
    assert not app.exception
    assert "Wynik: DINOv2 ViT-B" in html_text(app)
    assert len(app.session_state["results"]) == 2
    app.button_group(key="model_choice").set_value("swin").run()
    assert len(app.session_state["results"]) == 2


def test_level_is_part_of_the_result(app, lesion_image):
    to_crop(app, png_bytes(lesion_image))
    app.button(key="analyze").click().run()
    assert "Widoki TTA na model: 4" in html_text(app)
    app.button_group(key="level_choice").set_value("best").run()
    assert not app.exception
    assert "Widoki TTA na model: 12" in html_text(app)
    assert len(app.session_state["results"]) == 2


def test_map_and_analysis_can_load_in_one_run(app, lesion_image):
    to_crop(app, png_bytes(lesion_image))
    app.button(key="analyze").click().run()
    app.toggle(key="xai").set_value(True).run()
    app.button_group(key="model_choice").set_value("ensemble").run()
    assert not app.exception
    assert len(app.session_state["heatmaps"]) == 2


def test_new_photo_clears_everything(app, lesion_image):
    to_crop(app, png_bytes(lesion_image))
    app.button(key="analyze").click().run()
    app.button(key="new_photo").click().run()
    assert app.session_state["step"] == "upload"
    assert app.session_state["results"] == {}


@pytest.mark.parametrize("model_id", list(model.MODELS))
def test_every_model_is_reachable(app, lesion_image, model_id):
    to_crop(app, png_bytes(lesion_image))
    app.button(key="analyze").click().run()
    app.button_group(key="model_choice").set_value(model_id).run()
    assert not app.exception


def test_style_guide_runs_in_both_themes():
    at = AppTest.from_file(str(ROOT / "ui_demo.py"), default_timeout=20)
    at.run()
    assert not at.exception
