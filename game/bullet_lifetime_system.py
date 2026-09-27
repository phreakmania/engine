from .components import BulletTag

from engine.ecs.components.transform import Transform

def bullet_lifetime_system(world):
    to_destroy = []

    for entity, tag, transform in world.query(
        BulletTag,
        Transform,
    ):
        half_height = transform.scale.y * 0.5

        if transform.position.y + half_height < 0:
            to_destroy.append(entity)

    for entity in to_destroy:
        world.destroy_entity(entity)
