from dataclasses import dataclass

from engine.ecs.world import Entity


@dataclass
class Parent:
    entity: Entity
