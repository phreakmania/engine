import unittest

from engine.ecs.components.transform import Transform
from engine.ecs.world import World
from engine.vector2 import Vector2
from game.components import BulletTag, Invulnerability
from game.systems import bullet_lifetime_system, invulnerability_system


class GameSystemsTests(unittest.TestCase):
    def test_invulnerability_counts_down_but_never_below_zero(self):
        world = World()
        entity = world.create_entity()
        state = Invulnerability(duration=1.0, remaining=0.5)
        world.add_component(entity, state)

        invulnerability_system(world, 0.2)
        self.assertEqual(state.remaining, 0.3)

        invulnerability_system(world, 1.0)
        self.assertEqual(state.remaining, 0.0)

    def test_invulnerability_with_zero_remaining_is_unchanged(self):
        world = World()
        entity = world.create_entity()
        state = Invulnerability(duration=1.0)
        world.add_component(entity, state)

        invulnerability_system(world, 1.0)

        self.assertEqual(state.remaining, 0.0)

    def test_bullet_lifetime_removes_only_bullets_above_world(self):
        world = World()
        expired = world.create_entity()
        active = world.create_entity()
        touching_edge = world.create_entity()
        just_visible = world.create_entity()
        unrelated = world.create_entity()
        world.add_component(expired, BulletTag())
        world.add_component(expired, Transform(position=Vector2(0, -9), scale=Vector2(1, 16)))
        world.add_component(active, BulletTag())
        world.add_component(active, Transform(position=Vector2(0, -7), scale=Vector2(1, 16)))
        world.add_component(touching_edge, BulletTag())
        world.add_component(touching_edge, Transform(position=Vector2(0, -8), scale=Vector2(1, 16)))
        world.add_component(just_visible, BulletTag())
        world.add_component(just_visible, Transform(position=Vector2(0, -7.5), scale=Vector2(1, 16)))
        world.add_component(unrelated, Transform(position=Vector2(0, -100), scale=Vector2(1, 1)))

        bullet_lifetime_system(world)

        self.assertIsNone(world.get_component(expired, BulletTag))
        self.assertIsNotNone(world.get_component(active, BulletTag))
        self.assertIsNotNone(world.get_component(touching_edge, BulletTag))
        self.assertIsNotNone(world.get_component(just_visible, BulletTag))
        self.assertIsNotNone(world.get_component(unrelated, Transform))
