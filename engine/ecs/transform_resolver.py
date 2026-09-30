from engine.ecs.components.parent import Parent
from engine.ecs.components.transform import Transform


def get_world_transform(world, entity):
    transform = world.get_component(entity, Transform)

    parent = world.get_component(entity, Parent)

    if parent is None:
        return transform

    parent_transform = get_world_transform(
        world,
        parent.entity,
    )

    return Transform(
        position=parent_transform.position + transform.position,
        scale=transform.scale,
        rotation=transform.rotation,
    )
