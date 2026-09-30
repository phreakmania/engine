import json

from engine.scene import Scene


class SceneLoader:
    def __init__(self, registry):
        self.component_registry = registry

    def load(self, path):
        with open(path, "r") as file:
            data = json.load(file)

        scene = Scene()

        entities = []
        entities_by_id = {}

        # Pass 1:
        # Alle Runtime-Entities erzeugen und Scene-IDs auflösen.
        for entity_data in data["entities"]:
            entity = scene.world.create_entity()

            entities.append(
                (entity_data, entity)
            )

            scene_id = entity_data.get("id")

            if scene_id is not None:
                if scene_id in entities_by_id:
                    raise ValueError(
                        f"Duplicate scene entity id: {scene_id}"
                    )

                entities_by_id[scene_id] = entity

        # Pass 2:
        # Components erzeugen.
        for entity_data, entity in entities:
            components = entity_data["components"]

            for component_name, component_data in components.items():

                if component_name == "Parent":
                    parent_id = component_data["entity"]

                    if parent_id not in entities_by_id:
                        raise ValueError(
                            f"Unknown parent entity id: {parent_id}"
                        )

                    component_data = {
                        "entity": entities_by_id[parent_id]
                    }

                component = self.component_registry.create(
                    component_name,
                    component_data,
                )

                scene.world.add_component(
                    entity,
                    component,
                )

        return scene