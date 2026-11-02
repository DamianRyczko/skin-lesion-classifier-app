from helpers import close_panel
from playwright.sync_api import expect


def test_clicking_a_class_shows_its_details(app):
    app.to_result()
    row = app.page.locator(".nb-row").first
    name = row.locator(".nb-rname").inner_text()
    pct = row.locator(".nb-rpct").inner_text()
    row.click()
    dialog = app.page.locator('[data-testid="stDialog"] [role="dialog"]')
    expect(dialog).to_be_visible(timeout=8000)
    expect(dialog.get_by_text(name.upper()).or_(dialog.get_by_text(name)).first).to_be_visible()
    expect(dialog.get_by_text(pct)).to_be_visible()
    expect(dialog.get_by_text("Co to jest")).to_be_visible()
    expect(dialog.get_by_text("Co zrobić")).to_be_visible()
    expect(dialog.get_by_text("Miejsce na zdjęcie przykładowe")).to_be_visible()


def test_every_class_opens(app):
    app.to_result()
    for index in range(7):
        app.page.locator(".nb-row").nth(index).click()
        dialog = app.page.locator('[data-testid="stDialog"] [role="dialog"]')
        expect(dialog).to_be_visible(timeout=8000)
        close_panel(app.page)


def test_rows_work_from_the_keyboard(app):
    app.to_result()
    app.page.locator(".nb-row").first.focus()
    app.page.keyboard.press("Enter")
    expect(app.page.locator('[data-testid="stDialog"] [role="dialog"]')).to_be_visible(timeout=8000)


def test_xai_follows_the_clicked_class(app):
    app.to_result()
    app.page.get_by_text("Mapa XAI").click()
    expect(app.page.get_by_text("mała uwaga")).to_be_visible()
    row = app.page.locator(".nb-row").nth(2)
    name = row.locator(".nb-rname").inner_text()
    row.click()
    dialog = app.page.locator('[data-testid="stDialog"] [role="dialog"]')
    expect(dialog).to_be_visible(timeout=8000)
    close_panel(app.page)
    expect(app.page.locator(".nb-note b")).to_have_text(name, timeout=8000)


def test_closed_panel_stays_closed(app):
    app.to_result()
    app.page.locator(".nb-row").nth(1).click()
    close_panel(app.page)
    app.page.wait_for_timeout(700)
    expect(app.page.locator('[data-testid="stDialog"]')).to_have_count(0)
