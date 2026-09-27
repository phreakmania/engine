from ..components.transform import Transform
from ..components.velocity import Velocity


def movement_system(world, dt):
    for entity, transform, velocity in world.query(
        Transform,
        Velocity,
    ):
        transform.position = (
            transform.position
            + velocity.value * dt
        )