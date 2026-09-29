import math
from engine.transform import Transform
from engine.vector2 import Vector2

class Enemy:
    def __init__(self, x=0.0, y=0.0, speed=100.0):

        self.transform = Transform(
            position=Vector2(x,y),
            scale=Vector2(64.0, 16.0),
            rotation=0
        )
        self.color = (0.9,0.2,0.2,1.0)
        self.speed = speed
        self.health = 3
        self.damage = 1
        self.destroyed = False

    def is_dead(self):
        return self.health <= 0

    def take_damage(self, damage):
        self.health -= damage
        if self.is_dead():
            self.destroyed = True

    def update(self, dt, player_position):
        direction = (
            player_position
            - self.transform.position
        ).normalized()

        self.transform.position = (
            self.transform.position
            + direction * self.speed * dt
        )