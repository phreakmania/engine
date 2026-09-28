import unittest

from engine.scene import Scene
from engine.scene_loader import SceneLoader
from engine.ecs.component_registry import ComponentRegistry
from engine.ecs.components.transform import Transform
from engine.ecs.components.quad_renderable import QuadRenderable


class SceneLoaderTests(unittest.TestCase):
    def test_loads_scene_from_file(self):
        registry = ComponentRegistry()
        scene = SceneLoader(registry).load("game/assets/scenes/test_scene.json")

        self.assertIsInstance(scene, Scene)

    def test_loads_scene_has_transform(self):
        registry = ComponentRegistry()
        scene = SceneLoader(registry).load("game/assets/scenes/test_scene.json")
        results = list(scene.world.query(Transform))

        self.assertEqual(len(results), 1)

        entity, transform = results[0]

        self.assertEqual(transform.position.x, 400.0)
        self.assertEqual(transform.position.y, 300.0)
        self.assertEqual(transform.scale.x, 64.0)
        self.assertEqual(transform.scale.y, 64.0)
        self.assertEqual(transform.rotation, 0.0)

    def test_loads_scene_has_renderable(self):
        registry = ComponentRegistry()
        scene = SceneLoader(registry).load("game/assets/scenes/test_scene.json")
        results = list(scene.world.query(QuadRenderable))

        self.assertEqual(len(results), 1)

        entity, renderable = results[0]

        self.assertEqual(renderable.color, tuple([1.0, 0.0, 0.0, 1.0]))


if __name__ == "__main__":
    unittest.main()