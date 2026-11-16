"""The app without a browser. AppTest cannot drive the custom cropper, so it analyses the default crop."""

import io
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def app() -> AppTest:
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20)
    at.run()
    return at


def html_text(at: AppTest) -> str:
    return " ".join(str(element.proto.body) for element in at.html)


def upload(at: AppTest, data: bytes) -> None:
    at.file_uploader[0].upload("lesion.png", data, "image/png").run()


def test_photo_to_result(app, lesion_image):
    buffer = io.BytesIO()
    lesion_image.save(buffer, "PNG")
    upload(app, buffer.getvalue())
    app.button(key="analyze").click().run()
    assert not app.exception
    text = html_text(app)
    assert "Wynik: Swin-Base" in text
    assert "Zalecana konsultacja" in text or "Zalecenie: obserwacja" in text
    app.toggle(key="xai").set_value(True).run()  # the occlusion map on top
    assert not app.exception


def test_each_model_and_level_runs_once(app, lesion_image):
    buffer = io.BytesIO()
    lesion_image.save(buffer, "PNG")
    upload(app, buffer.getvalue())
    app.button(key="analyze").click().run()
    app.button_group(key="model_choice").set_value("ensemble").run()
    app.button_group(key="level_choice").set_value("fast").run()
    assert not app.exception
    assert len(app.session_state["results"]) == 3
    app.button_group(key="model_choice").set_value("swin").run()
    app.button_group(key="level_choice").set_value("best").run()
    assert len(app.session_state["results"]) == 4


def test_broken_file_stays_on_upload_with_a_message(app):
    upload(app, b"not an image")
    assert app.session_state["step"] == "upload"
    assert "Nie można użyć tego pliku" in html_text(app)
