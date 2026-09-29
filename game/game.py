
from .player import Player
from .enemy import Enemy
from .wall import Wall
from .components import BulletTag, Damage
from .bullet_lifetime_system import bullet_lifetime_system

from engine.vector2 import Vector2
from engine.key import Key
from engine.collision import intersects
from engine.ecs.world import World
from engine.ecs.systems.movement import movement_system
from engine.ecs.systems.quad_render import quad_render_system
from engine.ecs.components.transform import Transform
from engine.ecs.components.velocity import Velocity
from engine.ecs.components.quad_renderable import QuadRenderable

class Game:
    def __init__(self, width, height):
        self.game_over = False
        self.width = width
        self.height = height
        self.player = Player()
        self.enemies = []
        self.world = World()

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

        movement_system(
            self.world,
            dt,
        )

        self._update_enemies(dt)

        self._handle_bullet_enemy_collisions()
        self._handle_enemy_player_collisions()

        self._cleanup_destroyed_objects()
        self._check_game_over()

        bullet_lifetime_system(
            self.world
        )

    def _update_enemies(self, dt):
        for enemy in self.enemies:
            enemy.update(dt, self.player.transform.position)
        pass

    def _handle_bullet_enemy_collisions(self):
        bullets_to_destroy = []

        for entity, bullet_tag, transform, damage in self.world.query(
            BulletTag,
            Transform,
            Damage,
        ):
            for enemy in self.enemies:
                if intersects(
                    transform,
                    enemy.transform,
                ):
                    enemy.take_damage(damage.value)

                    bullets_to_destroy.append(entity)
                    break

        for entity in bullets_to_destroy:
            self.world.destroy_entity(entity)

    def _handle_enemy_player_collisions(self):
        for enemy in self.enemies:
            if intersects(enemy.transform, self.player.transform,):
                self.player.take_damage(enemy.damage)
                break

    def _cleanup_destroyed_objects(self):
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
            self._spawn_bullet()

    def _spawn_bullet(self):
        entity = self.world.create_entity()

        player_position = self.player.transform.position

        self.world.add_component(
            entity,
            Transform(
                position=Vector2(
                    player_position.x,
                    player_position.y,
                ),
                scale=Vector2(8.0, 16.0),
            ),
        )

        self.world.add_component(
            entity,
            Velocity(
                Vector2(0.0, -500.0)
            ),
        )

        self.world.add_component(
            entity,
            Damage(1),
        )

        self.world.add_component(
            entity,
            BulletTag(),
        )

        self.world.add_component(
            entity,
            QuadRenderable(
                color=(1.0, 0.8, 0.2, 1.0),
            ),
        )

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

        quad_render_system(
            self.world,
            renderer,
        )
