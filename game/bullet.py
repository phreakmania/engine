from engine.transform import Transform
from engine.vector2 import Vector2


class Bullet:
    def __init__(self, position):
        self.transform = Transform(
            position=Vector2(position.x, position.y),
            scale=Vector2(8.0, 16.0),
        )

        self.velocity = Vector2(0.0, -500.0)

        self.color = (
            1.0,
            0.8,
            0.2,
            1.0,
        )

    def update(self, dt):
        self.transform.position.x += self.velocity.x * dt
        self.transform.position.y += self.velocity.y * dt