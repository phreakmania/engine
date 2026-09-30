
from .components import PlayerTag, EnemyTag, BulletTag, WallTag, Damage, Health, Invulnerability
from .systems import invulnerability_system, bullet_lifetime_system

from engine.camera import Camera2D
from engine.vector2 import Vector2
from engine.key import Key
from engine.texture import Texture
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
        
        self.world_width = 3000.0
        self.world_height = 2000.0

        self.world = World()
        self.camera = Camera2D()

        self.enemy_spawn_interval = 2.0
        self.enemy_spawn_timer = 0.0

        wall_size = 32.0
        half_wall = wall_size * 0.5

        self._spawn_walls([
            Transform(Vector2(self.world_width * 0.5, half_wall),
                            Vector2(self.world_width, wall_size)),
            Transform(Vector2(self.world_width * 0.5, self.world_height - half_wall),
                            Vector2(self.world_width, wall_size)),
            Transform(Vector2(half_wall, self.world_height * 0.5),
                            Vector2(wall_size, self.world_height)),
            Transform(Vector2(self.world_width - half_wall, self.world_height * 0.5),
                            Vector2(wall_size, self.world_height)),
        ])
        self._spawn_player()

    def update(self, dt, input):
        if self.game_over:
            return

        self._update_player(dt, input)
        self._spawn_bullets(input)
        self._spawn_enemies(dt)

        self._update_enemies()

        movement_system(
            self.world,
            dt,
        )

        self._update_camera(dt)

        self._handle_bullet_enemy_collisions()
        self._handle_enemy_player_collisions()

        self._check_game_over()

        invulnerability_system(
            self.world,
            dt
        )
        bullet_lifetime_system(
            self.world
        )

    def _update_camera(self, dt):
        player_position = self._get_player_position()

        self.camera.position = Vector2(
            player_position.x - self.width * 0.5,
            player_position.y - self.height * 0.5,
        )

    def _spawn_walls(self, transforms):
        for transform in transforms:
            entity = self.world.create_entity()
            self.world.add_component(
                entity,
                WallTag()
            )

            self.world.add_component(
                entity,
                transform
            )

            self.world.add_component(
                entity,
                QuadRenderable(
                    color=(0.3,0.3,0.3,1.0)
                )
            )

    def _spawn_player(self):
        entity = self.world.create_entity()
        self.world.add_component(
            entity,
            PlayerTag()
        )

        self.world.add_component(
            entity,
            Transform(
                position=Vector2(640.0, 360.0),
                scale=Vector2(32.0, 32.0),
            ),
        )

        self.world.add_component(
            entity,
            Health(5)
        )

        self.world.add_component(
            entity,
            Invulnerability(0.5)
        )

        self.world.add_component(
            entity,
            QuadRenderable(
                color=(0.2, 0.2, 0.7, 1.0),
            ),
        )

    def _spawn_enemies(self, dt):
        self.enemy_spawn_timer += dt

        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer -= self.enemy_spawn_interval

            entity = self.world.create_entity()

            self.world.add_component(
                entity,
                EnemyTag(),
            )

            self.world.add_component(
                entity,
                Transform(
                    position=Vector2(self.width * 0.5, 80.0),
                    scale=Vector2(64.0, 16.0),
                ),
            )

            self.world.add_component(
                entity,
                Health(3)
            )

            self.world.add_component(
                entity,
                Damage(1)
            )

            self.world.add_component(
                entity,
                QuadRenderable(
                    color=(0.9, 0.2, 0.2, 1.0),
                ),
            )
            self.world.add_component(
                entity,
                Velocity(Vector2()),
            )

    def _get_player_position(self):
        return self._get_player_transform().position

    def _get_player_transform(self):
        results = list(self.world.query(PlayerTag, Transform))
        (entity, player_tag, player_transform) = (results[0])
        return player_transform

    def _update_enemies(self):
        player_position = self._get_player_position()

        for entity, enemy_tag, transform, velocity in self.world.query(
            EnemyTag,
            Transform,
            Velocity,
        ):

            direction = (
                player_position
                - transform.position
            ).normalized()

            velocity.value = direction * 100.0

    def _handle_bullet_enemy_collisions(self):
        bullets_to_destroy = []

        for bullet_entity, bullet_tag, bullet_transform, damage in self.world.query(
            BulletTag,
            Transform,
            Damage,
        ):
            for enemy_entity, enemy_tag, enemy_transform, health in self.world.query(
                EnemyTag,
                Transform,
                Health,
            ):
                if intersects(
                    bullet_transform,
                    enemy_transform,
                ):
                    health.current -= damage.value

                    if health.current <= 0:
                        self.world.destroy_entity(enemy_entity)

                    bullets_to_destroy.append(bullet_entity)
                    break

        for entity in bullets_to_destroy:
            self.world.destroy_entity(entity)

    def _handle_enemy_player_collisions(self):
        for player_entity, player_tag, player_transform, health, invulnerability in self.world.query(
            PlayerTag,
            Transform,
            Health,
            Invulnerability,
        ):
            if invulnerability.remaining > 0.0:
                return

                
            for entity, enemy_tag, transform, damage in self.world.query(
                EnemyTag,
                Transform,
                Damage,
            ):
                if intersects(transform, player_transform):
                    health.current -= damage.value
                    invulnerability.remaining = invulnerability.duration
                    break

    def _check_game_over(self):
        results = list(self.world.query(PlayerTag, Health))
        (entity, player_tag, player_health) = (results[0])
        
        if player_health.current <= 0:
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

        self._move_player(direction, dt)

    def _move_player(self, direction, dt):
        transform = self._get_player_transform()

        direction = direction.normalized()
        movement = direction * 200.0 * dt

        transform.position.x += movement.x

        for entity, wall_tag, wall_transform in self.world.query(WallTag, Transform):
            if intersects(transform, wall_transform):
                transform.position.x -= movement.x
                break

        transform.position.y += movement.y

        for entity, wall_tag, wall_transform in self.world.query(WallTag, Transform):
            if intersects(transform, wall_transform):
                transform.position.y -= movement.y
                break

    def set_test_texture(self, texture):
        self.test_texture = texture

    def _spawn_bullets(self, input):
        if input.was_key_pressed(Key.SPACE):
            self._spawn_bullet()

    def _spawn_bullet(self):
        entity = self.world.create_entity()

        player_position = self._get_player_position()

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
        quad_render_system(
            self.world,
            renderer,
        )
