import math

from .player import Player
from .enemy import Enemy
from .bullet import Bullet
from .wall import Wall

from engine.vector2 import Vector2
from engine.key import Key
from engine.input import Input
from engine.collision import intersects

class Game:
    def __init__(self, width, height):
        self.game_over = False
        self.width = width
        self.height = height
        self.player = Player()
        self.enemy = Enemy(x=320,y=240)
        self.enemy2 = Enemy(x=640, y=60)
        self.enemies = [self.enemy, self.enemy2]
        self.bullets = []

        wall_size = 32.0

        self.walls = [
            # oben
            Wall(
                Vector2(640.0, 16.0),
                Vector2(1280.0, 32.0),
            ),

            # unten
            Wall(
                Vector2(640.0, 704.0),
                Vector2(1280.0, 32.0),
            ),

            # links
            Wall(
                Vector2(16.0, 360.0),
                Vector2(32.0, 720.0),
            ),

            # rechts
            Wall(
                Vector2(1264.0, 360.0),
                Vector2(32.0, 720.0),
            ),
        ]


    def update(self, dt, input):
        if self.game_over:
            return
        direction = Vector2()

        if input.was_key_pressed(Key.SPACE):
            bullet = Bullet(self.player.transform.position)
            self.bullets.append(bullet)

        for bullet in self.bullets:
            bullet.update(dt)
            for enemy in self.enemies:
                if intersects(bullet.transform,enemy.transform,):
                    bullet.destroyed = True
                    enemy.take_damage(bullet.damage)

        for enemy in self.enemies:
            enemy.update(dt, self.player.transform.position)
            if intersects(enemy.transform, self.player.transform,):
                self.player.take_damage(enemy.damage)

        if self.player.is_dead():
            self.game_over = True
            print("Game Over!")

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
            self.walls
        )

        self.player.update(dt)

        self.bullets = [
            bullet
            for bullet in self.bullets
            if not bullet.is_outside()
            and not bullet.destroyed
        ]

        self.enemies = [
            enemy
            for enemy in self.enemies
            if not enemy.destroyed
        ]

    def render(self, renderer):
        for wall in self.walls:
            renderer.render(
                wall.transform,
                wall.color,
            )

        renderer.render(
            self.player.transform,
            self.player.color
        )

        for enemy in self.enemies:
            renderer.render(
                enemy.transform,
                enemy.color
            )

        for bullet in self.bullets:
            renderer.render(
                bullet.transform,
                bullet.color
            )
