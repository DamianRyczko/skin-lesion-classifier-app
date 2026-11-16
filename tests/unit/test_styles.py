from ui.theme import stylesheet_files


def test_no_less_than_sign_in_the_css():
    for path in stylesheet_files():
        assert "<" not in path.read_text(encoding="utf-8"), path.name
