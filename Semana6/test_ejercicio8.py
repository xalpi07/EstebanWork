from Ejercicio8 import prime_numbers

def test_prime_numbers_mixed():
    assert prime_numbers([1, 4, 6, 7, 13, 9, 67]) == [7, 13, 67]

def test_prime_numbers_all_primes():
    assert prime_numbers([2, 3, 5, 7, 11]) == [2, 3, 5, 7, 11]

def test_prime_numbers_no_primes():
    assert prime_numbers([1, 4, 6, 8, 9, 10]) == []

def test_prime_numbers_empty():
    assert prime_numbers([]) == []

def test_prime_numbers_with_zero_and_one():
    assert prime_numbers([0, 1, 2]) == [2]