import unittest
from dataclasses import dataclass

from engine.ecs.world import World


@dataclass
class Position:
    x: float
    y: float


@dataclass
class Health:
    value: int


class WorldTests(unittest.TestCase):
    def test_create_entity_returns_unique_ids(self):
        world = World()

        first = world.create_entity()
        second = world.create_entity()
        third = world.create_entity()

        self.assertNotEqual(first, second)
        self.assertGreater(second, first)
        self.assertLess(second, third)

    def test_add_and_get_component(self):
        world = World()
        entity = world.create_entity()

        position = Position(10.0, 20.0)

        world.add_component(entity, position)

        result = world.get_component(
            entity,
            Position,
        )

        self.assertIs(result, position)

    def test_query_returns_entities_with_all_components(self):
        world = World()

        first = world.create_entity()
        second = world.create_entity()

        world.add_component(
            first,
            Position(10.0, 20.0),
        )
        world.add_component(
            first,
            Health(100),
        )

        world.add_component(
            second,
            Position(30.0, 40.0),
        )

        results = list(
            world.query(Position, Health)
        )

        self.assertEqual(len(results), 1)

        entity, position, health = results[0]

        self.assertEqual(entity, first)
        self.assertEqual(position.x, 10.0)
        self.assertEqual(health.value, 100)

    def test_destroy_entity_removes_components(self):
        world = World()
        entity = world.create_entity()

        world.add_component(
            entity,
            Position(10.0, 20.0),
        )

        world.destroy_entity(entity)

        results = list(
            world.query(Position)
        )

        self.assertEqual(results, [])

    def test_cannot_add_component_to_destroyed_entity(self):
        world = World()
        entity = world.create_entity()

        world.destroy_entity(entity)

        with self.assertRaises(ValueError):
            world.add_component(
                entity,
                Position(10.0, 20.0),
            )


if __name__ == "__main__":
    unittest.main()