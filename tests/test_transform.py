import unittest
from dataclasses import dataclass

from engine.ecs.transform_resolver import get_world_transform
from engine.ecs.world import World, Entity
from engine.ecs.components.parent import Parent
from engine.ecs.components.transform import Transform
from engine.vector2 import Vector2

class TransformTests(unittest.TestCase):
    def test_child_world_position_is_relative_to_parent(self):
        world = World()

        parent = world.create_entity()
        world.add_component(
            parent,
            Transform(
                position=Vector2(100, 50),
            ),
        )

        child = world.create_entity()
        world.add_component(
            child,
            Transform(
                position=Vector2(20, 10),
            ),
        )
        world.add_component(
            child,
            Parent(parent),
        )

        transform = get_world_transform(world, child)

        self.assertEqual(transform.position.x, 120)
        self.assertEqual(transform.position.y, 60)

    def test_root_world_transform_is_its_transform(self):
        world = World()

        entity = world.create_entity()
        transform = Transform(
            position=Vector2(100, 50),
        )
        world.add_component(entity, transform)

        result = get_world_transform(world, entity)

        self.assertIs(result, transform)
        
if __name__ == "__main__":
    unittest.main()