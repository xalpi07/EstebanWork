import math

class Circle:
    def __init__(self, radius):
        if radius <= 0:
            raise ValueError("Radius must be positive.")
        self.radius = radius

    def get_area(self):
        return math.pi * (self.radius ** 2)

try:
    my_circle = Circle(5)
    print(my_circle.get_area())
    
    invalid_circle = Circle(-3)  
except ValueError as error:
    print(error)
    
    