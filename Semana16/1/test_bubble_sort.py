import pytest

from bubble_sort import bubble_sort

def test_small_list():
    arr = [3, 1, 2]
    bubble_sort(arr)
    assert arr == [1, 2, 3]

def test_large_list():
    arr = list(range(200, 0, -1))
    expected = list(range(1, 201))
    bubble_sort(arr)
    assert arr == expected

def test_empty_list():
    arr = []
    bubble_sort(arr)
    assert arr == []

def test_invalid_parameter():
    with pytest.raises(TypeError):
        bubble_sort("not a list")
    with pytest.raises(TypeError):
        bubble_sort(123)
    with pytest.raises(TypeError):
        bubble_sort(None)