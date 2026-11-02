import numpy as np

from core.xai import overlay


def test_keeps_the_image_size(lesion_image):
    assert overlay(lesion_image, np.ones((7, 7)), 0.7).size == lesion_image.size


def test_zero_opacity_changes_nothing(lesion_image):
    assert np.array_equal(np.asarray(overlay(lesion_image, np.ones((7, 7)), 0)), np.asarray(lesion_image))


def test_paints_where_attention_is(lesion_image):
    heat = np.zeros((64, 64))
    heat[:10, :10] = 1
    before, after = np.asarray(lesion_image, dtype=int), np.asarray(overlay(lesion_image, heat, 1), dtype=int)
    assert np.abs(after[5, 5] - before[5, 5]).sum() > 50
    assert np.abs(after[-5, -5] - before[-5, -5]).sum() == 0


def test_flat_empty_map_is_safe(lesion_image):
    assert overlay(lesion_image, np.zeros((7, 7)), 1).size == lesion_image.size
