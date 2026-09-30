import unittest
from dataclasses import dataclass

from engine.ecs.world import World


@dataclass
class CustomTag:
    pass

@dataclass
class AnotherTag:
    pass

class TagTests(unittest.TestCase):
    def test_query_tag_returns_only_matching_entities(self):
        world = World()

        first = world.create_entity()
        second = world.create_entity()

        world.add_component(first, CustomTag())
        world.add_component(second, AnotherTag())

        results = list(world.query(CustomTag))

        self.assertEqual(len(results), 1)

        entity, tag = results[0]

        self.assertEqual(entity, first)
        self.assertIsInstance(tag, CustomTag)
        
if __name__ == "__main__":
    unittest.main()