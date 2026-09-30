from engine.vector2 import Vector2


class Camera2D:
    def __init__(self):
        self.position = Vector2()

    def world_to_screen(self, world_position):
        return world_position - self.position
