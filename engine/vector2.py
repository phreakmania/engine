import math

class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def length(self):
        return math.sqrt(
            self.x * self.x +
            self.y * self.y
        )

    def normalized(self):
        length = self.length()

        if length == 0:
            return Vector2()

        return self / length;

    def __add__(self, other: Vector2):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide Vector2 by zero")

        return Vector2(
            self.x / scalar,
            self.y / scalar,
        )