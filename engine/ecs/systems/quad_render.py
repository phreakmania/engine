from engine.ecs.components.transform import Transform
from engine.ecs.components.quad_renderable import QuadRenderable


def quad_render_system(world, renderer):
    for entity, transform, renderable in world.query(
        Transform,
        QuadRenderable,
    ):
        renderer.render(
            transform,
            renderable.color,
        )