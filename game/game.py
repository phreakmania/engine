
from .player import Player
from .enemy import Enemy
from .bullet import Bullet
from .wall import Wall

from engine.vector2 import Vector2
from engine.key import Key
from engine.collision import intersects

class Game:
    def __init__(self, width, height):
        self.game_over = False
        self.width = width
        self.height = height
        self.player = Player()
        self.enemies = []
        self.bullets = []

        self.enemy_spawn_interval = 2.0
        self.enemy_spawn_timer = 0.0

        wall_size = 32.0
        half_wall = wall_size * 0.5

        self.walls = [
            Wall(
                Vector2(width * 0.5, half_wall),
                Vector2(width, wall_size),
            ),
            Wall(
                Vector2(width * 0.5, height - half_wall),
                Vector2(width, wall_size),
            ),
            Wall(
                Vector2(half_wall, height * 0.5),
                Vector2(wall_size, height),
            ),
            Wall(
                Vector2(width - half_wall, height * 0.5),
                Vector2(wall_size, height),
            ),
        ]

    def _spawn_enemies(self, dt):
        self.enemy_spawn_timer += dt

        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer -= self.enemy_spawn_interval

            enemy = Enemy(
                x=self.width * 0.5,
                y=80.0,
            )

            self.enemies.append(enemy)

    def update(self, dt, input):
        if self.game_over:
            return

        self._update_player(dt, input)
        self._spawn_bullets(input)
        self._spawn_enemies(dt)

        self._update_bullets(dt)
        self._update_enemies(dt)

        self._handle_bullet_enemy_collisions()
        self._handle_enemy_player_collisions()

        self._cleanup_destroyed_objects()
        self._check_game_over()

    def _update_enemies(self, dt):
        for enemy in self.enemies:
            enemy.update(dt, self.player.transform.position)
        pass

    def _update_bullets(self, dt):
        for bullet in self.bullets:
            bullet.update(dt)
        pass

    def _handle_bullet_enemy_collisions(self):
        for bullet in self.bullets:
            for enemy in self.enemies:
                if intersects(bullet.transform,enemy.transform,):
                    bullet.destroyed = True
                    enemy.take_damage(bullet.damage)
                    break

    def _handle_enemy_player_collisions(self):
        for enemy in self.enemies:
            if intersects(enemy.transform, self.player.transform,):
                self.player.take_damage(enemy.damage)
                break

    def _cleanup_destroyed_objects(self):
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

    def _check_game_over(self):
        if self.player.is_dead():
            self.game_over = True
            print("Game Over!")

    def _update_player(self, dt, input):
        direction = Vector2()
        if input.is_key_down(Key.D):
            direction.x += 1.0

        if input.is_key_down(Key.A):
            direction.x -= 1.0

        if input.is_key_down(Key.W):
            direction.y -= 1.0

        if input.is_key_down(Key.S):
            direction.y += 1.0

        self.player.move(
            direction,
            dt,
            self.walls
        )

        self.player.update(dt)

    def _spawn_bullets(self, input):
        if input.was_key_pressed(Key.SPACE):
            bullet = Bullet(self.player.transform.position)
            self.bullets.append(bullet)

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
