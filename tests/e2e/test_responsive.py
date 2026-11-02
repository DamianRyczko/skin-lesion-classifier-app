"""Layout follows the window width: resizing alone has to change it."""

WIDE = {"width": 1280, "height": 900}
NARROW = {"width": 700, "height": 900}
PHONE = {"width": 390, "height": 844}


def boxes(app):
    photo = app.page.locator(".st-key-nbpanel_photo").bounding_box()
    result = app.page.locator(".st-key-nbpanel_result").bounding_box()
    return photo, result


def test_chart_moves_under_the_photo_when_narrowed(app):
    app.page.set_viewport_size(WIDE)
    app.to_result()
    photo, result = boxes(app)
    assert result["x"] > photo["x"] + photo["width"] - 1  # side by side
    app.page.set_viewport_size(NARROW)
    app.page.wait_for_timeout(400)
    photo, result = boxes(app)
    assert result["y"] >= photo["y"] + photo["height"] - 1  # chart underneath
    app.page.set_viewport_size(WIDE)
    app.page.wait_for_timeout(400)
    photo, result = boxes(app)
    assert result["x"] > photo["x"] + photo["width"] - 1


def test_panel_slides_from_the_right_on_desktop(app):
    app.page.set_viewport_size(WIDE)
    app.to_result()
    app.page.locator(".nb-row").nth(1).click()
    dialog = app.page.locator('[data-testid="stDialog"] [role="dialog"]')
    dialog.wait_for(timeout=8000)
    app.page.wait_for_timeout(500)
    box = dialog.bounding_box()
    assert box["x"] + box["width"] >= WIDE["width"] - 2 and box["x"] > 600
    assert box["height"] >= WIDE["height"] - 2


def test_panel_is_a_bottom_sheet_on_narrow_screens(app):
    app.page.set_viewport_size(PHONE)
    app.to_result()
    app.page.locator(".nb-row").nth(1).click()
    dialog = app.page.locator('[data-testid="stDialog"] [role="dialog"]')
    dialog.wait_for(timeout=8000)
    app.page.wait_for_timeout(500)
    box = dialog.bounding_box()
    assert box["x"] == 0 and box["width"] == PHONE["width"]
    assert box["y"] > 0 and box["y"] + box["height"] >= PHONE["height"] - 2


def test_no_sideways_scrolling_on_a_phone(app):
    app.page.set_viewport_size(PHONE)
    app.to_result()
    assert app.page.locator('[data-testid="stMain"]').evaluate("e => e.scrollWidth <= e.clientWidth")
