from Ejercicio4 import sum_list

def test_sum_list_positive_numbers():
    assert sum_list([4, 6, 2, 29]) == 41

def test_sum_list_empty():
    assert sum_list([]) == 0

def test_sum_list_negative_numbers():
    assert sum_list([-1, -2, -3]) == -6

def test_sum_list_mixed_numbers():
    assert sum_list([10, -5, 3]) == 8