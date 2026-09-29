from engine.ecs.components.transform import Transform
from engine.ecs.components.quad_renderable import QuadRenderable


def quad_render_system(world, renderer, resources):
    for entity, transform, renderable in world.query(
        Transform,
        QuadRenderable,
    ):
        texture = None

        if renderable.texture is not None:
            texture = resources.get_texture(renderable.texture)

        renderer.render(
            transform,
            renderable.color,
            texture,
        )