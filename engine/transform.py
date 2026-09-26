from .vector2 import Vector2


class Transform:
    def __init__(
        self,
        position=None,
        scale=None,
        rotation=0.0,
    ):
        self.position = position or Vector2()
        self.scale = scale or Vector2(1.0, 1.0)
        self.rotation = rotation