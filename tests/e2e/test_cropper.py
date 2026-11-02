"""The reason the cropper is our own: it has to fit narrow screens and work with a finger."""

from conftest import PHOTO
from helpers import PHONE_CONTEXT, box_style, drag_touch
from playwright.sync_api import expect


def test_mouse_drag_moves_the_box(app):
    app.open().upload()
    before = box_style(app.page)
    box = app.page.locator(".nb-crop-box").bounding_box()
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    app.page.mouse.move(x, y)
    app.page.mouse.down()
    app.page.mouse.move(x + 40, y + 10, steps=6)
    app.page.mouse.up()
    assert box_style(app.page) != before


def test_corner_resizes_and_stays_square(app):
    app.page.set_viewport_size({"width": 1280, "height": 1100})
    app.open().upload()
    box = app.page.locator(".nb-crop-box").bounding_box()
    handle = app.page.locator(".nb-crop-h.se").bounding_box()
    x, y = handle["x"] + 9, handle["y"] + 9
    app.page.mouse.move(x, y)
    app.page.mouse.down()
    app.page.mouse.move(x - 80, y - 80, steps=6)
    app.page.mouse.up()
    after = app.page.locator(".nb-crop-box").bounding_box()
    assert after["width"] < box["width"]
    assert abs(after["width"] - after["height"]) <= 1


def test_box_cannot_leave_the_photo(app):
    app.open().upload()
    box = app.page.locator(".nb-crop-box").bounding_box()
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    app.page.mouse.move(x, y)
    app.page.mouse.down()
    app.page.mouse.move(x - 2000, y - 2000, steps=6)
    app.page.mouse.up()
    stage = app.page.locator(".nb-crop").bounding_box()
    after = app.page.locator(".nb-crop-box").bounding_box()
    assert after["x"] >= stage["x"] - 1 and after["y"] >= stage["y"] - 1


def test_crop_changes_the_analysed_image_and_is_kept(app):
    app.open().upload()
    app.page.locator(".nb-crop-box").focus()
    for _ in range(8):
        app.page.keyboard.press("ArrowLeft")
    app.page.wait_for_timeout(600)
    moved = box_style(app.page)
    app.analyze()
    app.page.get_by_role("button", name="Zmień kadr").click()
    app.page.locator(".nb-crop-box").wait_for(timeout=8000)
    expect(app.page.locator(".nb-crop-box")).to_have_attribute("style", moved)


def test_touch_drag_on_a_phone(browser, base_url):
    context = browser.new_context(**PHONE_CONTEXT)
    page = context.new_page()
    page.goto(base_url)
    page.locator('input[type="file"]').wait_for(state="attached", timeout=30000)
    page.locator('input[type="file"]').set_input_files(str(PHOTO))
    page.locator(".nb-crop-box").wait_for(timeout=15000)
    stage = page.locator(".nb-crop").bounding_box()
    assert stage["x"] + stage["width"] <= PHONE_CONTEXT["viewport"]["width"]  # fits the screen
    before = box_style(page)
    drag_touch(context, page, -40, -20)
    assert box_style(page) != before
    context.close()
