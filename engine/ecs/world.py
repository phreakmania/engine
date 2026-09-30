from typing import TypeAlias

Entity: TypeAlias = int

class World:
    def __init__(self):
        self._next_entity: Entity = 1
        self._alive: set[Entity] = set()

        self._components: dict[
            type,
            dict[Entity, object],
        ] = {}

    def create_entity(self) -> Entity:
        entity = self._next_entity
        self._next_entity += 1

        self._alive.add(entity)

        return entity

    def destroy_entity(self, entity: Entity):
        self._alive.discard(entity)

        for store in self._components.values():
            store.pop(entity, None)

    def add_component(self, entity: Entity, component):
        if entity not in self._alive:
            raise ValueError(
                f"Entity {entity} does not exist"
            )

        component_type = type(component)

        store = self._components.setdefault(
            component_type,
            {},
        )

        store[entity] = component

    def remove_component(self, entity: Entity, component_type: type):
        store = self._components.get(component_type)

        if store is not None:
            store.pop(entity, None)

    def get_component(self, entity: Entity, component_type: type):
        return self._components.get(component_type, {}).get(entity)

    def is_alive(self, entity: Entity) -> bool:
        return entity in self._alive

    def query(self, *component_types):
        if not component_types:
            return

        stores = [
            self._components.get(component_type, {})
            for component_type in component_types
        ]

        if any(not store for store in stores):
            return

        smallest_store = min(
            stores,
            key=len,
        )

        for entity in tuple(smallest_store):
            if all(entity in store for store in stores):
                components = tuple(
                    store[entity]
                    for store in stores
                )

                yield entity, *components