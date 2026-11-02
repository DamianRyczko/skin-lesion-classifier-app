"""Starts the real app once for the browser tests."""

import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

from tests.tiny_package import write_notebook_package, write_package

ROOT = Path(__file__).resolve().parents[2]
PHOTO = ROOT / "tests" / "fixtures" / "lesion.jpg"


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _serve(**env: str):
    port = _free_port()
    server = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true", f"--server.port={port}"],
        cwd=ROOT,
        env={**os.environ, **env},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    for _ in range(60):
        try:
            if urllib.request.urlopen(f"{url}/_stcore/health", timeout=1).read() == b"ok":
                break
        except OSError:
            time.sleep(0.5)
    yield url
    server.terminate()
    server.wait(timeout=10)


@pytest.fixture(scope="session")
def base_url():
    yield from _serve(SKIN_APP_MOCK_LOAD="0.3", SKIN_APP_MOCK_VIEW="0.02")


@pytest.fixture(scope="session")
def package_url(tmp_path_factory):
    """The same app on a real model package."""
    yield from _serve(SKIN_APP_PACKAGE=str(write_package(tmp_path_factory.mktemp("weights") / "skin_lesions_app")))


@pytest.fixture(scope="session")
def notebook_url(tmp_path_factory):
    """The same app on the notebook's app_package.json."""
    yield from _serve(SKIN_APP_PACKAGE=str(write_notebook_package(tmp_path_factory.mktemp("weights") / "skin_lesions_app")))


class App:
    def __init__(self, page, base_url):
        self.page = page
        self.base_url = base_url

    def open(self, theme: str = "light"):
        self.page.goto(f"{self.base_url}/?theme={theme}")
        self.page.locator('input[type="file"]').wait_for(state="attached", timeout=30000)
        return self

    def upload(self):
        self.page.locator('input[type="file"]').set_input_files(str(PHOTO))
        self.page.locator(".nb-crop-box").wait_for(timeout=15000)
        return self

    def analyze(self):
        self.page.get_by_role("button", name="Analizuj").click()
        self.page.locator(".nb-row").first.wait_for(timeout=20000)
        return self

    def to_result(self):
        return self.open().upload().analyze()

    def segment(self, text: str):
        return self.page.locator('[data-testid="stButtonGroup"] button', has_text=text)

    def css(self, selector: str, prop: str) -> str:
        return self.page.locator(selector).first.evaluate(f"e => getComputedStyle(e).{prop}")

    def assert_healthy(self):
        assert self.page.locator('[data-testid="stException"]').count() == 0


@pytest.fixture
def app(page, base_url):
    yield App(page, base_url)
    App(page, base_url).assert_healthy()


@pytest.fixture
def package_app(page, package_url):
    yield App(page, package_url)
    App(page, package_url).assert_healthy()


@pytest.fixture
def notebook_app(page, notebook_url):
    yield App(page, notebook_url)
    App(page, notebook_url).assert_healthy()
