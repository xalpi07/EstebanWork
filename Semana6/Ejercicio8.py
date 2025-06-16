def check_is_prime(num):
    if num < 2:
        return False
    for i in range(2, num):
        if num % i == 0:
            return False
    return True

def prime_numbers(lst): 
    prime_lst = []
    for num in lst:
        if check_is_prime(num):
            prime_lst.append(num)
    return prime_lst

prime_numbers_lst = prime_numbers([1, 4, 6, 7, 13, 9, 67])
print(prime_numbers_lst)