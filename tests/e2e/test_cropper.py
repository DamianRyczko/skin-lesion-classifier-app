"""The cropper is our own JavaScript: it has to work with keyboard and finger, on a phone too."""

from conftest import PHOTO
from helpers import PHONE_CONTEXT, box_style, drag_touch
from playwright.sync_api import expect


def test_keyboard_crop_is_the_one_analysed_and_is_kept(app):
    app.open().upload()
    before = box_style(app.page)
    app.page.locator(".nb-crop-box").focus()
    for _ in range(8):
        app.page.keyboard.press("ArrowLeft")
    moved = box_style(app.page)
    assert moved != before
    app.page.wait_for_timeout(600)
    app.analyze()
    app.page.get_by_role("button", name="Zmień kadr").click()
    expect(app.page.locator(".nb-crop-box")).to_have_attribute("style", moved, timeout=8000)


def test_touch_drag_on_a_phone(browser, base_url):
    context = browser.new_context(**PHONE_CONTEXT)
    page = context.new_page()
    page.goto(base_url)
    page.locator('input[type="file"]').set_input_files(str(PHOTO), timeout=30000)
    page.locator(".nb-crop-box").wait_for(timeout=15000)
    stage = page.locator(".nb-crop").bounding_box()
    assert stage["x"] + stage["width"] <= PHONE_CONTEXT["viewport"]["width"]
    before = box_style(page)
    drag_touch(context, page, -40, -20)
    assert box_style(page) != before
    context.close()
