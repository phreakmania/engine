import json

from engine.scene import Scene
from engine.vector2 import Vector2
from engine.ecs.components.transform import Transform
from engine.ecs.components.quad_renderable import QuadRenderable


class SceneLoader:
    def __init__(self, registry):
        self.component_registry = registry

    def load(self, path):
        with open(path, "r") as file:
            data = json.load(file)

        scene = Scene()

        for entity_data in data["entities"]:
            entity = scene.world.create_entity()

            components = entity_data["components"]

            for component_name, component_data in components.items():
                component = self.component_registry.create(
                    component_name,
                    component_data
                )

                scene.world.add_component(entity, component)

        return scene