from engine.ecs.components.quad_renderable import QuadRenderable
from engine.ecs.components.transform import Transform
from engine.ecs.transform_resolver import get_world_transform


def quad_render_system(world, renderer, resources):

    entities = world.query(Transform, QuadRenderable)

    for entity, transform, renderable in sorted(
        entities,
        key=lambda item: item[2].z_index,
    ):
        texture = None

        if renderable.texture is not None:
            texture = resources.get_texture(renderable.texture)

        world_transform = get_world_transform(world, entity)

        renderer.render(
            world_transform,
            renderable.color,
            texture,
        )
