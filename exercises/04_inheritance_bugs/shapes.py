import math


class Shape:
    def __init__(self, name):
        self.name = name

    def area(self):
        raise NotImplementedError("Subclasses must implement area()")

    def __str__(self):
        return f"{self.name}: area={self.area}"


class Rectangle(Shape):
    def __init__(self, width, height):
        super().__init__("Rectangle")
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)
        self.name = "Square"
        self.side = side

    def resize(self, new_side):
        self.side = new_side


class Circle(Shape):
    def __init__(self, radius):
        super().__init__("Circle")
        self.radius = radius

    def area(self):
        return self.radius * 2 * math.pi
