import math
from engine.transform import Transform
from engine.vector2 import Vector2

class Enemy:
    def __init__(self, x=0.0, y=0.0, speed=200.0):

        self.transform = Transform(
            position=Vector2(x,y),
            scale=Vector2(64.0, 16.0),
            rotation=math.radians(45.0)
        )
        self.color = (0.9,0.2,0.2,1.0)
        self.speed = speed
