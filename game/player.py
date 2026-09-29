import math
from engine.transform import Transform
from engine.vector2 import Vector2

class Player:
    def __init__(self, x=640.0, y=360.0, speed=200.0):

        self.transform = Transform(
            position=Vector2(x,y),
            scale=Vector2(32.0, 32.0),
        )
        self.color = (0.1,0.2,0.9,1.0)
        self.speed = speed

    def move(self, direction: Vector2, dt):

        self.transform.position.x += direction.x * self.speed * dt
        self.transform.position.y += direction.y * self.speed * dt