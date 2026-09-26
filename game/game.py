import math
from .player import Player
from .enemy import Enemy
from engine.vector2 import Vector2

class Game:
    def __init__(self):
        self.player = Player()
        self.enemy = Enemy(x=320,y=240)

    def update(self, dt, window):
        
        direction = Vector2()

        if window.is_key_pressed("d"):
            direction.x += 1.0

        if window.is_key_pressed("a"):
            direction.x -= 1.0

        if window.is_key_pressed("w"):
            direction.y -= 1.0

        if window.is_key_pressed("s"):
            direction.y += 1.0

        direction = direction.normalized()

        self.player.move(
            direction,
            dt,
        )

    def render(self, renderer):
        renderer.render(
            self.player.transform,
            self.player.color
        )

        renderer.render(
            self.enemy.transform,
            self.enemy.color
        )
