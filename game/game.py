
from .components import PlayerTag, EnemyTag, BulletTag, WallTag, Damage, Health, Invulnerability
from .systems import invulnerability_system, bullet_lifetime_system

from engine.camera import Camera2D
from engine.vector2 import Vector2
from engine.key import Key
from engine.texture import Texture
from engine.timer import Timer
from engine.collision import intersects
from engine.scene_loader import SceneLoader
from engine.ecs.hierarchy import destroy_entity_tree
from engine.ecs.component_registry import ComponentRegistry
from engine.ecs.components.parent import Parent
from engine.ecs.components.transform import Transform
from engine.ecs.components.velocity import Velocity
from engine.ecs.components.player_spawn import PlayerSpawn
from engine.ecs.components.quad_renderable import QuadRenderable
from engine.ecs.systems.movement import movement_system
from engine.ecs.systems.quad_render import quad_render_system

class Game:
    def __init__(self, width, height):
        self.game_over = False
        self.viewport_width = width
        self.viewport_height = height

        self.world_width = 2000.0
        self.world_height = 1000.0

        registry = ComponentRegistry()

        registry.register(
            "WallTag",
            lambda data: WallTag()
        )

        registry.register(
            "EnemyTag",
            lambda data: EnemyTag()
        )

        registry.register(
            "Health",
            lambda data: Health(
                current=data["current"]
            )
        )
 
        registry.register(
            "Damage",
            lambda data: Damage(
                value=data["value"]
            )
        )

        self.scene_loader = SceneLoader(registry)
        self.scene = self.scene_loader.load("game/assets/scenes/main.json")
        self.world = self.scene.world
        self.camera = Camera2D()

        self.enemy_spawn_timer = Timer(2.0, can_overflow=True)

        wall_size = 32.0
        half_wall = wall_size * 0.5

        self._spawn_player()

    def update(self, dt, input):
        if self.game_over:
            return

        self._update_player(dt, input)
        self._spawn_bullets(input)

        self._update_enemies()

        movement_system(
            self.world,
            dt,
        )

        self._update_camera(dt)

        self._handle_bullet_enemy_collisions()
        self._handle_enemy_player_collisions()

        self._check_game_over()

        bullet_lifetime_system(
            self.world
        )
        self._update_timers(dt)
        self._spawn_enemies(dt)

    def _update_camera(self, dt):
        player_position = self._get_player_position()

        self.camera.position = Vector2(
            player_position.x - self.viewport_width * 0.5,
            player_position.y - self.viewport_height * 0.5,
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

        results = list(self.world.query(
            Transform,
            PlayerSpawn
        ))

        player_spawn_entity, player_spawn_transform, player_spawn = results[0]
              
        entity = self.world.create_entity()
        self.world.add_component(
            entity,
            PlayerTag()
        )

        self.world.add_component(
            entity,
            player_spawn_transform,
        )

        self.world.add_component(
            entity,
            Health(5)
        )

        self.world.add_component(
            entity,
            Invulnerability(Timer(
                duration=0.5,
                remaining=0.0
            ))
        )

        self.world.add_component(
            entity,
            QuadRenderable(
                color=(0.2, 0.2, 0.7, 1.0),
            ),
        )

    def _spawn_enemies(self, dt):
        self.enemy_spawn_timer.update(dt)

        if self.enemy_spawn_timer.remaining == 0.0:
            self.enemy_spawn_timer.restart()

            entity = self.world.create_entity()

            self.world.add_component(
                entity,
                EnemyTag(),
            )

            self.world.add_component(
                entity,
                Transform(
                    position=Vector2(self.world_width * 0.5, 80.0),
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
                        destroy_entity_tree(self.world, enemy_entity)

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
            if invulnerability.timer.remaining > 0.0:
                return

                
            for entity, enemy_tag, transform, damage in self.world.query(
                EnemyTag,
                Transform,
                Damage,
            ):
                if intersects(transform, player_transform):
                    health.current -= damage.value
                    invulnerability.timer.restart()
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
        
    def _update_timers(self, dt):
        for _, invulnerability in self.world.query(Invulnerability):
            invulnerability.timer.update(dt)

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

    def render(self, renderer, resources):
        quad_render_system(
            self.world,
            renderer,
            resources,
        )
