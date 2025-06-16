from Ejercicio7 import sort_string

def test_sort_string_normal():
    assert sort_string("python-variable-funcion-computadora-monitor") == "computadora-funcion-monitor-python-variable"

def test_sort_string_single_word():
    assert sort_string("solitario") == "solitario"

def test_sort_string_already_sorted():
    assert sort_string("a-b-c-d") == "a-b-c-d"

def test_sort_string_reverse_order():
    assert sort_string("d-c-b-a") == "a-b-c-d"

def test_sort_string_empty():
    assert sort_string("") == ""