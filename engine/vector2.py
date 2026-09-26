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

        return Vector2(
            self.x / length,
            self.y / length,
        )