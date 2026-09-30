from engine.transform import Transform
from engine.vector2 import Vector2


class Wall:
    def __init__(self, position, size):
        self.transform = Transform(
            position=position,
            scale=size,
        )

        self.color = (
            0.35,
            0.35,
            0.4,
            1.0,
        )