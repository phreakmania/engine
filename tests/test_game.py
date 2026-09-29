import math
import unittest
from unittest.mock import Mock

from engine.ecs.components.transform import Transform
from engine.ecs.components.quad_renderable import QuadRenderable
from engine.ecs.components.velocity import Velocity
from engine.key import Key
from engine.collision import intersects
from engine.vector2 import Vector2
from game.components import (
    BulletTag,
    Damage,
    EnemyTag,
    Health,
    Invulnerability,
    PlayerTag,
    WallTag,
)
from game.game import Game


class FakeInput:
    def __init__(self, pressed=(), just_pressed=()):
        self.pressed = set(pressed)
        self.just_pressed = set(just_pressed)

    def is_key_down(self, key):
        return key in self.pressed

    def was_key_pressed(self, key):
        return key in self.just_pressed


class GameTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(1280, 720)

    def player(self):
        return list(self.game.world.query(PlayerTag, Transform, Health, Invulnerability))[0]

    def enemies(self):
        return list(self.game.world.query(EnemyTag, Transform, Health, Damage))

    def bullets(self):
        return list(self.game.world.query(BulletTag, Transform, Damage))

    def test_initial_scene_creates_player_and_loaded_world_entities(self):
        entity, player, transform, health, invulnerability = self.player()

        self.assertIs(self.game.game_over, False)
        self.assertEqual((transform.position.x, transform.position.y), (640.0, 820.0))
        self.assertEqual(health.current, 5)
        self.assertEqual(invulnerability.timer.remaining, 0.0)
        self.assertEqual(invulnerability.timer.duration, 0.5)
        self.assertEqual(len(self.enemies()), 1)
        self.assertEqual(len(list(self.game.world.query(WallTag))), 4)

        _, _, _, enemy_health, enemy_damage = self.enemies()[0]
        self.assertEqual(enemy_health.current, 3)
        self.assertEqual(enemy_damage.value, 1)

        player_renderable = self.game.world.get_component(entity, QuadRenderable)
        self.assertEqual(player_renderable.color, (0.2, 0.2, 0.7, 1.0))
        self.assertIsNone(player_renderable.texture)

    def test_update_moves_player_updates_camera_and_spawns_bullet(self):
        self.game.update(0.1, FakeInput(pressed=(Key.D,), just_pressed=(Key.SPACE,)))

        _, _, transform, _, _ = self.player()
        self.assertAlmostEqual(transform.position.x, 660.0)
        self.assertAlmostEqual(transform.position.y, 820.0)
        self.assertAlmostEqual(self.game.camera.position.x, 20.0)
        self.assertAlmostEqual(self.game.camera.position.y, 460.0)
        self.assertEqual(len(self.bullets()), 1)

    def test_update_does_not_change_game_when_already_over(self):
        self.game.game_over = True
        before = self.player()[2].position.x

        self.game.update(1.0, FakeInput(pressed=(Key.D,), just_pressed=(Key.SPACE,)))

        self.assertEqual(self.player()[2].position.x, before)
        self.assertEqual(self.bullets(), [])

    def test_enemy_spawns_only_after_interval_and_moves_toward_player(self):
        self.game.update(1.9, FakeInput())
        self.assertEqual(len(self.enemies()), 1)
        self.game.update(0.1, FakeInput())
        self.assertEqual(len(self.enemies()), 2)
        self.game.update(0.1, FakeInput())
        self.assertEqual(len(self.enemies()), 2)

        for _, _, transform, _, _ in self.enemies():
            self.assertIsNotNone(transform)
        enemy_velocity = list(self.game.world.query(EnemyTag, Velocity))[0][2]
        self.assertGreater(enemy_velocity.value.y, 0.0)

    def test_wall_collision_reverts_player_movement(self):
        _, _, player_transform, _, _ = self.player()
        wall_entity = self.game.world.create_entity()
        self.game.world.add_component(wall_entity, WallTag())
        self.game.world.add_component(
            wall_entity,
            Transform(position=Vector2(650.0, 820.0), scale=Vector2(32.0, 32.0)),
        )

        original = (player_transform.position.x, player_transform.position.y)
        self.game.update(0.1, FakeInput(pressed=(Key.D,)))

        self.assertEqual((player_transform.position.x, player_transform.position.y), original)

    def test_player_moves_in_each_direction_and_normalizes_diagonal_input(self):
        diagonal = 20.0 / math.sqrt(2.0)
        cases = (
            ((Key.D,), 20.0, 0.0),
            ((Key.A,), -20.0, 0.0),
            ((Key.W,), 0.0, -20.0),
            ((Key.S,), 0.0, 20.0),
            ((Key.D, Key.W), diagonal, -diagonal),
            ((Key.A, Key.S), -diagonal, diagonal),
            ((Key.D, Key.A), 0.0, 0.0),
            ((Key.W, Key.S), 0.0, 0.0),
        )

        for pressed, expected_x, expected_y in cases:
            with self.subTest(pressed=pressed):
                game = Game(1280, 720)
                transform = list(game.world.query(PlayerTag, Transform))[0][2]

                game.update(0.1, FakeInput(pressed=pressed))

                self.assertAlmostEqual(transform.position.x, 640.0 + expected_x)
                self.assertAlmostEqual(transform.position.y, 820.0 + expected_y)

    def test_wall_blocks_x_movement_but_allows_y_movement(self):
        transform = self.player()[2]
        wall = self.game.world.create_entity()
        self.game.world.add_component(wall, WallTag())
        self.game.world.add_component(
            wall, Transform(position=Vector2(675, 820), scale=Vector2(16, 16))
        )

        self.game.update(0.1, FakeInput(pressed=(Key.D, Key.W)))

        self.assertAlmostEqual(transform.position.x, 640.0)
        self.assertAlmostEqual(transform.position.y, 820.0 - 20.0 / math.sqrt(2.0))

    def test_wall_blocks_y_movement_but_allows_x_movement(self):
        transform = self.player()[2]
        wall = self.game.world.create_entity()
        self.game.world.add_component(wall, WallTag())
        self.game.world.add_component(
            wall, Transform(position=Vector2(640, 785), scale=Vector2(16, 16))
        )

        self.game.update(0.1, FakeInput(pressed=(Key.D, Key.W)))

        self.assertAlmostEqual(transform.position.x, 640.0 + 20.0 / math.sqrt(2.0))
        self.assertAlmostEqual(transform.position.y, 820.0)

    def test_spawn_timer_carries_remaining_time_to_next_spawn(self):
        initial_count = len(self.enemies())

        self.game.update(1.25, FakeInput())
        self.assertEqual(len(self.enemies()), initial_count)
        self.game.update(1.0, FakeInput())
        self.assertEqual(len(self.enemies()), initial_count + 1)
        self.game.update(1.5, FakeInput())
        self.assertEqual(len(self.enemies()), initial_count + 1)
        self.game.update(0.25, FakeInput())
        self.assertEqual(len(self.enemies()), initial_count + 2)

    def test_spawned_enemy_has_playable_components_and_follows_player(self):
        existing = {entity for entity, *_ in self.enemies()}

        self.game.update(2.0, FakeInput())

        entity, _, transform, health, damage = next(
            enemy for enemy in self.enemies() if enemy[0] not in existing
        )
        self.assertEqual((transform.position.x, transform.position.y), (1000.0, 80.0))
        self.assertEqual((transform.scale.x, transform.scale.y), (64.0, 16.0))
        self.assertEqual(health.current, 3)
        self.assertEqual(damage.value, 1)
        self.assertEqual(self.game.world.get_component(entity, QuadRenderable).color,
                         (0.9, 0.2, 0.2, 1.0))

        velocity = self.game.world.get_component(entity, Velocity)
        self.assertEqual((velocity.value.x, velocity.value.y), (0.0, 0.0))
        self.game._update_enemies()
        toward_player = self.player()[2].position - transform.position
        self.assertAlmostEqual(velocity.value.x, toward_player.normalized().x * 100.0)
        self.assertAlmostEqual(velocity.value.y, toward_player.normalized().y * 100.0)

    def test_bullet_spawns_at_player_and_moves_upward(self):
        self.game._spawn_bullets(FakeInput())
        self.assertEqual(self.bullets(), [])

        self.game._spawn_bullets(FakeInput(just_pressed=(Key.SPACE,)))

        entity, _, transform, damage = self.bullets()[0]
        self.assertEqual(len(self.bullets()), 1)
        self.assertEqual((transform.position.x, transform.position.y), (640.0, 820.0))
        self.assertEqual((transform.scale.x, transform.scale.y), (8.0, 16.0))
        self.assertEqual(damage.value, 1)
        self.assertEqual(self.game.world.get_component(entity, QuadRenderable).color,
                         (1.0, 0.8, 0.2, 1.0))
        velocity = self.game.world.get_component(entity, Velocity)
        self.assertEqual((velocity.value.x, velocity.value.y), (0.0, -500.0))

        self.game.update(0.1, FakeInput())

        self.assertEqual((transform.position.x, transform.position.y), (640.0, 770.0))

    def test_spawn_walls_adds_wall_tags_and_renderables(self):
        transform = Transform(position=Vector2(100, 100), scale=Vector2(20, 20))

        self.game._spawn_walls([transform])

        walls = list(self.game.world.query(WallTag, Transform))
        added_entity = next(entity for entity, _, item in walls if item is transform)
        self.assertEqual(self.game.world.get_component(added_entity, QuadRenderable).color,
                         (0.3, 0.3, 0.3, 1.0))

    def test_test_texture_can_be_set(self):
        texture = object()

        self.game.set_test_texture(texture)

        self.assertIs(self.game.test_texture, texture)

    def test_bullet_enemy_collision_damages_enemy_and_removes_bullet(self):
        enemy_entity, _, enemy_transform, health, _ = self.enemies()[0]
        bullet_entity = self.game.world.create_entity()
        self.game.world.add_component(bullet_entity, BulletTag())
        self.game.world.add_component(
            bullet_entity,
            Transform(position=Vector2(enemy_transform.position.x, enemy_transform.position.y), scale=Vector2(8, 8)),
        )
        self.game.world.add_component(bullet_entity, Damage(1))

        self.game._handle_bullet_enemy_collisions()

        self.assertEqual(health.current, 2)
        self.assertIsNone(self.game.world.get_component(bullet_entity, BulletTag))
        self.assertIsNotNone(self.game.world.get_component(enemy_entity, EnemyTag))

    def test_bullet_enemy_collision_destroys_enemy_when_health_reaches_zero(self):
        enemy_entity, _, enemy_transform, health, _ = self.enemies()[0]
        health.current = 1
        bullet_entity = self.game.world.create_entity()
        self.game.world.add_component(bullet_entity, BulletTag())
        self.game.world.add_component(
            bullet_entity,
            Transform(position=Vector2(enemy_transform.position.x, enemy_transform.position.y), scale=Vector2(8, 8)),
        )
        self.game.world.add_component(bullet_entity, Damage(1))

        self.game._handle_bullet_enemy_collisions()

        self.assertIsNone(self.game.world.get_component(enemy_entity, EnemyTag))
        self.assertIsNone(self.game.world.get_component(bullet_entity, BulletTag))

    def test_bullet_does_not_destroy_enemy_with_one_health_remaining(self):
        enemy_entity, _, enemy_transform, health, _ = self.enemies()[0]
        health.current = 2
        bullet_entity = self.game.world.create_entity()
        self.game.world.add_component(bullet_entity, BulletTag())
        self.game.world.add_component(
            bullet_entity,
            Transform(position=Vector2(enemy_transform.position.x, enemy_transform.position.y),
                      scale=Vector2(8, 8)),
        )
        self.game.world.add_component(bullet_entity, Damage(1))

        self.game._handle_bullet_enemy_collisions()

        self.assertEqual(health.current, 1)
        self.assertIsNotNone(self.game.world.get_component(enemy_entity, EnemyTag))

    def test_bullet_missing_enemy_does_not_damage_it(self):
        _, _, _, health, _ = self.enemies()[0]
        bullet_entity = self.game.world.create_entity()
        self.game.world.add_component(bullet_entity, BulletTag())
        self.game.world.add_component(
            bullet_entity,
            Transform(position=Vector2(1400, 700), scale=Vector2(8, 16)),
        )
        self.game.world.add_component(bullet_entity, Damage(1))

        self.game._handle_bullet_enemy_collisions()

        self.assertEqual(health.current, 3)
        self.assertIsNotNone(self.game.world.get_component(bullet_entity, BulletTag))

    def test_enemy_player_collision_damages_and_starts_invulnerability(self):
        _, _, player_transform, health, invulnerability = self.player()
        enemy_entity = self.game.world.create_entity()
        self.game.world.add_component(enemy_entity, EnemyTag())
        self.game.world.add_component(
            enemy_entity,
            Transform(position=Vector2(player_transform.position.x, player_transform.position.y), scale=Vector2(8, 8)),
        )
        self.game.world.add_component(enemy_entity, Damage(2))

        self.game._handle_enemy_player_collisions()

        self.assertEqual(health.current, 3)
        self.assertEqual(invulnerability.timer.remaining, invulnerability.timer.duration)

        self.game._handle_enemy_player_collisions()
        self.assertEqual(health.current, 3)

    def test_enemy_can_damage_player_again_after_invulnerability_expires(self):
        _, _, player_transform, health, invulnerability = self.player()
        enemy = self.game.world.create_entity()
        self.game.world.add_component(enemy, EnemyTag())
        self.game.world.add_component(
            enemy,
            Transform(position=Vector2(player_transform.position.x, player_transform.position.y),
                      scale=Vector2(8, 8)),
        )
        self.game.world.add_component(enemy, Damage(1))

        self.game.update(0.1, FakeInput())
        self.assertEqual(health.current, 4)
        self.assertAlmostEqual(invulnerability.timer.remaining, 0.4)

        self.game.update(0.4, FakeInput())
        self.assertEqual(health.current, 4)
        self.assertEqual(invulnerability.timer.remaining, 0.0)

        self.game.update(0.1, FakeInput())
        self.assertEqual(health.current, 3)

    def test_zero_health_sets_game_over(self):
        _, _, _, health, _ = self.player()
        health.current = 0

        self.game._check_game_over()

        self.assertTrue(self.game.game_over)

    def test_one_remaining_health_does_not_end_game(self):
        self.player()[3].current = 1

        self.game._check_game_over()

        self.assertFalse(self.game.game_over)

    def test_render_delegates_world_to_quad_render_system(self):
        renderer = Mock()
        resources = Mock()

        self.game.render(renderer, resources)

        self.assertGreater(renderer.render.call_count, 0)
