def decorators_example(func):
    def wrapper(*args, **kwargs):
        print(f"Calling function '{func.__name__}' with:")
        print(f"  Positional arguments: {args}")
        print(f"  Keyword arguments: {kwargs}")
        result = func(*args, **kwargs)
        print(f"Result: {result}")
        print("---")
    return wrapper

@decorators_example
def add(a, b):
    print(f"Adding {a} and {b}")
    return a + b

@decorators_example
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")
    return f"{greeting}, {name}!"

add(3, 5)
greet("Esteban")
greet("Esteban", greeting="Hi")