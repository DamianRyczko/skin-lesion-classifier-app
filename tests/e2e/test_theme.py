LIGHT_BG = "rgb(244, 239, 234)"
DARK_BG = "rgb(10, 18, 48)"


def test_clicking_the_switch_changes_everything(app):
    app.open()
    assert app.css('[data-testid="stApp"]', "backgroundColor") == LIGHT_BG
    app.segment("Cyberpunk").click()
    app.page.wait_for_function(
        f"getComputedStyle(document.querySelector('[data-testid=\"stApp\"]')).backgroundColor === '{DARK_BG}'", timeout=8000
    )
    assert app.css(".st-key-nbbar", "backgroundColor") == "rgb(16, 27, 69)"
    assert app.css('[data-testid="stFileUploaderDropzone"]', "backgroundColor") == "rgb(16, 27, 69)"
    assert "theme=dark" in app.page.url
    app.segment("Jasny").click()
    app.page.wait_for_function(
        f"getComputedStyle(document.querySelector('[data-testid=\"stApp\"]')).backgroundColor === '{LIGHT_BG}'", timeout=8000
    )


def test_switching_keeps_the_result(app):
    app.to_result()
    results = app.page.locator(".nb-rows").inner_text()
    app.segment("Cyberpunk").click()
    app.page.wait_for_function(
        f"getComputedStyle(document.querySelector('[data-testid=\"stApp\"]')).backgroundColor === '{DARK_BG}'", timeout=8000
    )
    assert app.page.locator(".nb-rows").inner_text() == results


def test_theme_survives_a_reload(app):
    app.open("dark")
    app.page.reload()
    app.page.locator('input[type="file"]').wait_for(state="attached", timeout=30000)
    assert app.css('[data-testid="stApp"]', "backgroundColor") == DARK_BG


def test_dark_widgets_are_not_left_light(app):
    app.open("dark").upload().analyze()
    app.page.wait_for_timeout(300)
    for selector in ('[data-testid="stBaseButton-secondary"]', ".st-key-nbpanel_photo", ".st-key-nbpanel_result"):
        assert app.css(selector, "backgroundColor") not in (LIGHT_BG, "rgb(255, 255, 255)", "rgb(251, 249, 246)")
