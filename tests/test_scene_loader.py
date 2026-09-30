import unittest

from engine.ecs.component_registry import ComponentRegistry
from engine.ecs.components.parent import Parent
from engine.ecs.components.quad_renderable import QuadRenderable
from engine.ecs.components.transform import Transform
from engine.scene import Scene
from engine.scene_loader import SceneLoader


class SceneLoaderTests(unittest.TestCase):
    def test_loads_scene_from_file(self):
        registry = ComponentRegistry()
        scene = SceneLoader(registry).load("tests/assets/test_scene.json")

        self.assertIsInstance(scene, Scene)

    def test_loads_scene_has_transform(self):
        registry = ComponentRegistry()
        scene = SceneLoader(registry).load("tests/assets/test_scene.json")
        results = list(scene.world.query(Transform))

        self.assertEqual(len(results), 4)

        entity, transform = results[0]

        self.assertEqual(transform.position.x, 400.0)
        self.assertEqual(transform.position.y, 300.0)
        self.assertEqual(transform.scale.x, 64.0)
        self.assertEqual(transform.scale.y, 64.0)
        self.assertEqual(transform.rotation, 0.0)

    def test_loads_scene_has_renderable(self):
        registry = ComponentRegistry()
        scene = SceneLoader(registry).load("tests/assets/test_scene.json")
        results = list(scene.world.query(QuadRenderable))

        self.assertEqual(len(results), 2)

        entity, renderable = results[0]

        self.assertEqual(renderable.color, tuple([1.0, 0.0, 0.0, 1.0]))
        self.assertEqual(renderable.texture, "assets/tile_0000.png")

    def test_loads_scene_has_zindex_0(self):
        registry = ComponentRegistry()
        scene = SceneLoader(registry).load("tests/assets/test_scene.json")
        results = list(scene.world.query(QuadRenderable))

        self.assertEqual(len(results), 2)

        entity, renderable = results[1]
        self.assertEqual(renderable.z_index, 0)

    def test_loads_parent_relationship(self):
        registry = ComponentRegistry()
        scene = SceneLoader(registry).load(
            "tests/assets/test_scene.json"
        )

        results = list(
            scene.world.query(
                Transform,
                Parent,
            )
        )

        self.assertEqual(len(results), 1)

        child_entity, child_transform, parent = results[0]

        parent_transform = scene.world.get_component(
            parent.entity,
            Transform,
        )

        self.assertEqual(child_transform.position.x, 20.0)
        self.assertEqual(child_transform.position.y, 10.0)

        self.assertEqual(parent_transform.position.x, 100.0)
        self.assertEqual(parent_transform.position.y, 50.0)

    def test_loads_duplicate_scene_id(self):
        registry = ComponentRegistry()
        with self.assertRaises(ValueError):
            scene = SceneLoader(registry).load(
                "tests/assets/test_duplicate.json"
            )

    def test_loads_invalid_scene_id(self):
        registry = ComponentRegistry()
        with self.assertRaises(ValueError):
            scene = SceneLoader(registry).load(
                "tests/assets/test_duplicate.json"
            )

if __name__ == "__main__":
    unittest.main()