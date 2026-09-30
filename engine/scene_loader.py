import json

from engine.scene import Scene
from engine.vector2 import Vector2
from engine.ecs.components.transform import Transform


class SceneLoader:
    def load(self, path):
        with open(path, "r") as file:
            data = json.load(file)

        scene = Scene()

        for entity_data in data["entities"]:
            entity = scene.world.create_entity()

            components = entity_data["components"]

            if "Transform" in components:
                data = components["Transform"]

                transform = Transform(
                    position=Vector2(*data["position"]),
                    scale=Vector2(*data["scale"]),
                    rotation=data["rotation"],
                )

                scene.world.add_component(entity, transform)

        return scene