from playwright.sync_api import expect


def test_real_package_gives_a_result_without_the_mock_tag(package_app):
    package_app.to_result()
    expect(package_app.page.get_by_text("Wynik: Swin-Base")).to_be_visible()
    expect(package_app.page.locator(".nb-row")).to_have_count(7)
    expect(package_app.page.get_by_text("Dane przykładowe")).to_have_count(0)


def test_ensemble_at_the_best_level_with_the_map_on(package_app):
    package_app.to_result()
    package_app.page.get_by_text("Mapa XAI").click()
    expect(package_app.page.get_by_text("mała uwaga")).to_be_visible(timeout=20000)
    package_app.segment("TTA 12").click()
    expect(package_app.page.get_by_text("Widoki TTA na model: 12")).to_be_visible(timeout=20000)
    package_app.segment("Ensemble").click()
    expect(package_app.page.get_by_text("Wynik: Ensemble")).to_be_visible(timeout=20000)
    expect(package_app.page.locator(".nb-row")).to_have_count(7)
    expect(package_app.page.locator(".nb-walk")).to_have_count(0, timeout=20000)


def test_notebook_export_offers_only_what_it_was_tuned_for(notebook_app):
    notebook_app.to_result()
    expect(notebook_app.page.get_by_text("Wynik: Swin-Base")).to_be_visible()
    expect(notebook_app.page.get_by_text("Widoki TTA na model: 12")).to_be_visible()
    expect(notebook_app.page.get_by_text("Dane przykładowe")).to_have_count(0)
    expect(notebook_app.segment("TTA 4")).to_have_count(0)
    expect(notebook_app.segment("Ensemble")).to_have_count(1)
    notebook_app.segment("Bez TTA").click()
    expect(notebook_app.page.get_by_text("Widoki TTA na model: 1", exact=True)).to_be_visible(timeout=20000)
