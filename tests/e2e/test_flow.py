from playwright.sync_api import expect


def test_photo_to_result_and_class_details(app):
    app.to_result()
    expect(app.page.locator(".nb-row")).to_have_count(7)
    row = app.page.locator(".nb-row").nth(2)
    name = row.locator(".nb-rname").inner_text()
    row.click()
    dialog = app.page.locator('[data-testid="stDialog"] [role="dialog"]')
    expect(dialog).to_be_visible(timeout=8000)
    expect(dialog.get_by_text("Co zrobić")).to_be_visible()
    expect(dialog.get_by_text(name, exact=False).first).to_be_visible()
