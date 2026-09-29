import math

from .player import Player
from .enemy import Enemy
from .bullet import Bullet

from engine.vector2 import Vector2
from engine.key import Key
from engine.input import Input

class Game:
    def __init__(self):
        self.player = Player()
        self.enemy = Enemy(x=320,y=240)
        self.bullets = []

    def update(self, dt, input):
        
        direction = Vector2()

        if input.was_key_pressed(Key.SPACE):
            bullet = Bullet(self.player.transform.position)
            self.bullets.append(bullet)

        for bullet in self.bullets:
            bullet.update(dt)

        if input.is_key_down(Key.D):
            direction.x += 1.0

        if input.is_key_down(Key.A):
            direction.x -= 1.0

        if input.is_key_down(Key.W):
            direction.y -= 1.0

        if input.is_key_down(Key.S):
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

        for bullet in self.bullets:
            renderer.render(
                bullet.transform,
                bullet.color
            )
