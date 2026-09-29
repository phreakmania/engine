import unittest
from dataclasses import dataclass

from engine.ecs.world import World


@dataclass
class Marker:
    value: int = 0


@dataclass
class Other:
    value: int = 0


class WorldEdgeTests(unittest.TestCase):
    def test_query_without_component_types_is_empty(self):
        self.assertEqual(list(World().query()), [])

    def test_query_is_empty_when_component_store_is_missing(self):
        world = World()
        entity = world.create_entity()
        world.add_component(entity, Marker())

        self.assertEqual(list(world.query(Other)), [])
        self.assertEqual(list(world.query(Marker, Other)), [])

    def test_query_uses_requested_component_order_and_replaces_components(self):
        world = World()
        entity = world.create_entity()
        world.add_component(entity, Marker(1))
        world.add_component(entity, Other(2))
        replacement = Marker(3)
        world.add_component(entity, replacement)

        result = list(world.query(Other, Marker))

        self.assertEqual(result, [(entity, world.get_component(entity, Other), replacement)])

    def test_query_filters_entities_missing_one_of_existing_component_types(self):
        world = World()
        first = world.create_entity()
        second = world.create_entity()
        third = world.create_entity()
        world.add_component(first, Marker(1))
        world.add_component(second, Marker(2))
        world.add_component(second, Other(2))
        world.add_component(third, Other(3))

        results = list(world.query(Marker, Other))

        self.assertEqual([entity for entity, *_ in results], [second])

    def test_remove_component_and_destroy_unknown_entity_are_safe(self):
        world = World()
        entity = world.create_entity()
        world.add_component(entity, Marker())

        world.remove_component(entity, Other)
        world.remove_component(entity, Marker)
        world.destroy_entity(999)

        self.assertIsNone(world.get_component(entity, Marker))
        self.assertEqual(list(world.query(Marker)), [])

    def test_missing_component_type_or_entity_returns_none(self):
        world = World()
        entity = world.create_entity()
        world.add_component(entity, Marker(1))

        self.assertIsNone(world.get_component(entity, Other))
        self.assertIsNone(world.get_component(entity + 1, Marker))

    def test_removing_component_twice_is_safe_and_keeps_other_components(self):
        world = World()
        entity = world.create_entity()
        other_entity = world.create_entity()
        other = Other(2)
        world.add_component(entity, Marker(1))
        world.add_component(entity, other)
        world.add_component(other_entity, Marker(3))

        world.remove_component(entity, Marker)
        world.remove_component(entity, Marker)

        self.assertIsNone(world.get_component(entity, Marker))
        self.assertIs(world.get_component(entity, Other), other)
        self.assertEqual([item[0] for item in world.query(Marker)], [other_entity])

    def test_destroy_removes_every_component_and_does_not_reuse_entity_id(self):
        world = World()
        entity = world.create_entity()
        world.add_component(entity, Marker(1))
        world.add_component(entity, Other(2))

        world.destroy_entity(entity)
        next_entity = world.create_entity()

        self.assertNotEqual(next_entity, entity)
        self.assertIsNone(world.get_component(entity, Marker))
        self.assertIsNone(world.get_component(entity, Other))
        self.assertEqual(list(world.query(Marker, Other)), [])
