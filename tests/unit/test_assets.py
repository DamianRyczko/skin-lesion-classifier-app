from ui import assets


def test_no_sample_photo_means_no_image(tmp_path, monkeypatch):
    monkeypatch.setattr(assets, "SAMPLES", tmp_path)
    assert assets.sample("mel") is None


def test_sample_photo_is_used_once_it_is_there(tmp_path, monkeypatch):
    (tmp_path / "mel.jpg").write_bytes(b"jpeg")
    monkeypatch.setattr(assets, "SAMPLES", tmp_path)
    assert assets.sample("mel") == "data:image/jpeg;base64,anBlZw=="
