from typing import TypeAlias

Entity: TypeAlias = int

class World:
    def __init__(self):
        self._next_entity = 1
        self._alive = set()
        self._components = {}

    def create_entity(self):
        entity = self._next_entity
        self._next_entity += 1

        self._alive.add(entity)

        return entity

    def destroy_entity(self, entity):
        self._alive.discard(entity)

        for store in self._components.values():
            store.pop(entity, None)

    def add_component(self, entity, component):
        component_type = type(component)

        store = self._components.setdefault(
            component_type,
            {},
        )

        store[entity] = component

    def get_component(self, entity, component_type):
        return self._components[component_type][entity]

    def remove_component(self, entity, component_type):
        store = self._components.get(component_type)

        if store is not None:
            store.pop(entity, None)

    def query(self, *component_types):
        if not component_types:
            return

        stores = [
            self._components.get(component_type, {})
            for component_type in component_types
        ]

        if any(not store for store in stores):
            return

        smallest_store = min(stores, key=len)

        for entity in tuple(smallest_store.keys()):
            if all(entity in store for store in stores):
                components = tuple(
                    store[entity]
                    for store in stores
                )

                yield entity, *components