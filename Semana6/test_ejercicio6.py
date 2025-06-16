from Ejercicio6 import count_cases

def test_count_cases_mixed():
    assert count_cases("I love Sushi") == "There’s 2 upper cases and 8 lower cases"

def test_count_cases_all_upper():
    assert count_cases("HELLO") == "There’s 5 upper cases and 0 lower cases"

def test_count_cases_all_lower():
    assert count_cases("world") == "There’s 0 upper cases and 5 lower cases"

def test_count_cases_empty():
    assert count_cases("") == "There’s 0 upper cases and 0 lower cases"

def test_count_cases_numbers_and_symbols():
    assert count_cases("1234!@#") == "There’s 0 upper cases and 0 lower cases"