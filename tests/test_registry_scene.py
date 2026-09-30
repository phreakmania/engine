import json
import tempfile
import unittest
from pathlib import Path

from engine.ecs.component_registry import ComponentRegistry
from engine.ecs.components.player_spawn import PlayerSpawn
from engine.ecs.components.transform import Transform
from engine.ecs.components.velocity import Velocity
from engine.scene_loader import SceneLoader


class ComponentRegistryTests(unittest.TestCase):
    def test_builtin_loaders_create_components_and_optional_texture(self):
        registry = ComponentRegistry()

        transform = registry.create(
            "Transform",
            {"position": [1, 2], "scale": [3, 4], "rotation": 0.5},
        )
        renderable = registry.create("QuadRenderable", {"color": [1, 0, 0, 1]})
        velocity = registry.create("Velocity", {"value": [5, 6]})
        spawn = registry.create("PlayerSpawn", {})

        self.assertEqual((transform.position.x, transform.position.y), (1, 2))
        self.assertEqual((transform.scale.x, transform.scale.y), (3, 4))
        self.assertEqual(transform.rotation, 0.5)
        self.assertEqual(renderable.texture, None)
        self.assertEqual((velocity.value.x, velocity.value.y), (5, 6))
        self.assertIsInstance(spawn, PlayerSpawn)

    def test_custom_loader_can_be_registered(self):
        registry = ComponentRegistry()
        registry.register("Custom", lambda data: data["value"] + 1)

        self.assertEqual(registry.create("Custom", {"value": 4}), 5)

    def test_unknown_component_name_is_rejected(self):
        with self.assertRaises(KeyError):
            ComponentRegistry().create("Missing", {})


class SceneLoaderTests(unittest.TestCase):
    def load_scene(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scene.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return SceneLoader(ComponentRegistry()).load(path)

    def test_loads_multiple_entities_and_components(self):
        scene = self.load_scene(
            {
                "entities": [
                    {"components": {"Transform": {
                        "position": [10, 20], "scale": [2, 3], "rotation": 1
                    }}},
                    {"components": {"Velocity": {"value": [4, 5]}}},
                ]
            }
        )

        self.assertEqual(len(list(scene.world.query(Transform))), 1)
        self.assertEqual(len(list(scene.world.query(Velocity))), 1)

    def test_missing_scene_structure_is_reported(self):
        with self.assertRaises(KeyError):
            self.load_scene({})

    def test_invalid_json_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text("not json", encoding="utf-8")

            with self.assertRaises(json.JSONDecodeError):
                SceneLoader(ComponentRegistry()).load(path)
