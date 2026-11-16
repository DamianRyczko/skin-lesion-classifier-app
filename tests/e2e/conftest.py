"""Starts the app once, on the tiny package from tests/conftest.py, for the browser tests."""

import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import pytest

from tests.tiny_package import draw_lesion

ROOT = Path(__file__).resolve().parents[2]
PHOTO = Path(tempfile.mkdtemp(prefix="skin_app_photo_")) / "lesion.jpg"
draw_lesion((960, 720)).save(PHOTO, quality=90)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="session")
def base_url():
    port = _free_port()
    server = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true", f"--server.port={port}"],
        cwd=ROOT,
        env=os.environ,  # SKIN_APP_PACKAGE: the tiny package from tests/conftest.py
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

    def assert_healthy(self):
        assert self.page.locator('[data-testid="stException"]').count() == 0


@pytest.fixture
def app(page, base_url):
    yield App(page, base_url)
    App(page, base_url).assert_healthy()
