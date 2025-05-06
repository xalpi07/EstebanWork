def validate_numbers(func):
    def wrapper(*args):
        for arg in args:
            if not isinstance(arg, (int, float)):
                raise TypeError(f"Invalid argument: {arg}.")        
        return func(*args)
    return wrapper

@validate_numbers
def add(a, b):
    return a + b

@validate_numbers
def multiply(a, b):
    return a * b

try:
    print(add(3, 5))
    print(multiply(2, 3))
    print(add(3, "five"))
except TypeError as e:
    print(e)