from playwright.sync_api import expect


def test_full_flow_shows_seven_classes(app):
    app.to_result()
    expect(app.page.locator(".nb-row")).to_have_count(7)
    expect(app.page.get_by_text("To nie jest diagnoza")).to_be_visible()
    total = sum(float(t.replace("%", "").replace(",", ".")) for t in app.page.locator(".nb-rpct").all_inner_texts())
    assert 98 <= total <= 102  # rounded percentages


def test_loader_appears_while_analysing(app):
    app.open().upload()
    app.page.get_by_role("button", name="Analizuj").click()
    expect(app.page.locator(".nb-walk")).to_be_visible(timeout=5000)
    expect(app.page.locator(".nb-row").first).to_be_visible(timeout=20000)
    expect(app.page.locator(".nb-walk")).to_have_count(0)


def test_switching_models_changes_the_result(app):
    app.to_result()
    before = app.page.locator(".nb-rows").inner_text()
    app.segment("Ensemble").click()
    expect(app.page.get_by_text("Wynik: Ensemble")).to_be_visible(timeout=20000)
    expect(app.page.locator(".nb-row").first).to_be_visible()
    assert app.page.locator(".nb-rows").inner_text() != before


def test_xai_toggle_changes_the_photo(app):
    app.to_result()
    image = app.page.locator(".st-key-nbpanel_photo img")
    before = image.get_attribute("src")
    app.page.get_by_text("Mapa XAI").click()
    expect(app.page.get_by_text("mała uwaga")).to_be_visible()
    expect(image).not_to_have_attribute("src", before)


def test_new_photo_returns_to_upload(app):
    app.to_result()
    app.page.get_by_role("button", name="Nowe zdjęcie").click()
    expect(app.page.get_by_text("Dobre zdjęcie")).to_be_visible()
