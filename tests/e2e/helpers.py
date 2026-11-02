from typing import Any

PHONE_CONTEXT: dict[str, Any] = {
    "viewport": {"width": 390, "height": 844},
    "has_touch": True,
    "is_mobile": True,
    "device_scale_factor": 2,
}


def box_style(page) -> str:
    return page.locator(".nb-crop-box").get_attribute("style")


def drag_touch(context, page, dx: float, dy: float) -> None:
    """Real touch events through the browser protocol; Playwright has no touch drag."""
    target = page.locator(".nb-crop-box")
    target.scroll_into_view_if_needed()
    box = target.bounding_box()
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    session = context.new_cdp_session(page)
    session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x, "y": y}]})
    for step in range(1, 9):
        point = {"x": x + dx * step / 8, "y": y + dy * step / 8}
        session.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [point]})
        page.wait_for_timeout(20)
    session.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    page.wait_for_timeout(300)


def close_panel(page) -> None:
    """Escape, once the panel has opened: Streamlit can drop a key pressed during the opening animation."""
    dialog = page.locator('[data-testid="stDialog"]')
    dialog.wait_for(timeout=8000)
    page.locator('[data-testid="stDialog"]:not([data-entering])').wait_for(timeout=8000)
    page.keyboard.press("Escape")
    dialog.wait_for(state="detached", timeout=5000)
