import unittest
from unittest.mock import Mock

from engine.ecs.components.transform import Transform
from engine.ecs.components.velocity import Velocity
from engine.key import Key
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

        self.assertEqual((transform.position.x, transform.position.y), (640.0, 820.0))
        self.assertEqual(health.current, 5)
        self.assertEqual(invulnerability.remaining, 0.0)
        self.assertEqual(len(self.enemies()), 1)
        self.assertEqual(len(list(self.game.world.query(WallTag))), 4)

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

    def test_all_player_direction_inputs_are_accepted(self):
        before = self.player()[2].position

        self.game._update_player(
            0.0,
            FakeInput(pressed=(Key.A, Key.W, Key.S)),
        )

        self.assertEqual((before.x, before.y), (640.0, 820.0))

    def test_spawn_walls_adds_wall_tags_and_renderables(self):
        transform = Transform(position=Vector2(100, 100), scale=Vector2(20, 20))

        self.game._spawn_walls([transform])

        walls = list(self.game.world.query(WallTag, Transform))
        self.assertTrue(any(item[2] is transform for item in walls))

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
        self.assertEqual(invulnerability.remaining, invulnerability.duration)

        self.game._handle_enemy_player_collisions()
        self.assertEqual(health.current, 3)

    def test_zero_health_sets_game_over(self):
        _, _, _, health, _ = self.player()
        health.current = 0

        self.game._check_game_over()

        self.assertTrue(self.game.game_over)

    def test_render_delegates_world_to_quad_render_system(self):
        renderer = Mock()
        resources = Mock()

        self.game.render(renderer, resources)

        self.assertGreater(renderer.render.call_count, 0)
