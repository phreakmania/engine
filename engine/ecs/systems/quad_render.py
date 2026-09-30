from engine.ecs.components.transform import Transform
from engine.ecs.components.quad_renderable import QuadRenderable


def quad_render_system(world, renderer, resources):

    entities = world.query(Transform, QuadRenderable)

    for entity, transform, renderable in sorted(
        entities,
        key=lambda item: item[2].z_index,
    ):
        texture = None

        if renderable.texture is not None:
            texture = resources.get_texture(renderable.texture)

        renderer.render(
            transform,
            renderable.color,
            texture,
        )