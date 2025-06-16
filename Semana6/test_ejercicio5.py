from Ejercicio5 import reverse_string

def test_reverse_string_normal():
    assert reverse_string("Hola mundo") == "odnum aloH"

def test_reverse_string_empty():
    assert reverse_string("") == ""

def test_reverse_string_single_char():
    assert reverse_string("a") == "a"

def test_reverse_string_numbers():
    assert reverse_string("12345") == "54321"

def test_reverse_string_palindrome():
    assert reverse_string("oso") == "oso"