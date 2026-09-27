import unittest

from engine.ecs.world import World
from engine.ecs.components.transform import Transform
from engine.vector2 import Vector2
from engine.ecs.components.velocity import Velocity
from engine.ecs.systems.movement import movement_system


class MovementSystemTests(unittest.TestCase):
    def test_moves_entity_using_velocity_and_delta_time(self):
        world = World()

        entity = world.create_entity()

        world.add_component(
            entity,
            Transform(
                position=Vector2(10.0, 20.0)
            ),
        )

        world.add_component(
            entity,
            Velocity(
                Vector2(100.0, 50.0)
            ),
        )

        movement_system(
            world,
            dt=0.5,
        )

        transform = world.get_component(
            entity,
            Transform,
        )

        self.assertEqual(
            transform.position.x,
            60.0,
        )

        self.assertEqual(
            transform.position.y,
            45.0,
        )


if __name__ == "__main__":
    unittest.main()