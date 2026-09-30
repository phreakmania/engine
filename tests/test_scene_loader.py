import unittest

from engine.scene_loader import SceneLoader
from engine.ecs.components.transform import Transform


class SceneLoaderTests(unittest.TestCase):
    def test_loads_scene_from_file(self):
        scene = SceneLoader().load("..game/assets/scenese/test_scene.json")

        results = list(scene.world.query(Transform))

        self.assertEqual(len(results), 1)

        entity, transform = results[0]

        self.assertEqual(transform.position.x, 400.0)
        self.assertEqual(transform.position.y, 300.0)
        self.assertEqual(transform.scale.x, 64.0)
        self.assertEqual(transform.scale.y, 64.0)
        self.assertEqual(transform.rotation, 0.0)

if __name__ == "__main__":
    unittest.main()