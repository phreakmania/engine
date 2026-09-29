import unittest
from unittest.mock import Mock

from engine.vector2 import Vector2
from engine.ecs.systems.quad_render import quad_render_system
from engine.ecs.components.transform import Transform
from engine.ecs.components.quad_renderable import QuadRenderable


class QuadRenderSystemTests(unittest.TestCase):
    def test_renders_without_requesting_optional_texture(self):
        transform = Transform(position=Vector2(10.0, 20.0))
        renderable = QuadRenderable(color=(1.0, 1.0, 1.0, 1.0))
        world = Mock()
        world.query.return_value = [(1, transform, renderable)]
        renderer = Mock()
        resources = Mock()

        quad_render_system(world, renderer, resources)

        resources.get_texture.assert_not_called()
        renderer.render.assert_called_once_with(transform, renderable.color, None)

    def test_resolves_texture_before_rendering(self):
        transform = Transform(
            position=Vector2(10.0, 20.0)
        )
        renderable = QuadRenderable(
            color=(0.3,0.3,0.3,1.0),
            texture="assets/enemy.png",
        )

        world = Mock()
        world.query.return_value = [
            (1, transform, renderable)
        ]

        renderer = Mock()
        resources = Mock()

        texture = Mock()
        resources.get_texture.return_value = texture

        quad_render_system(world, renderer, resources)

        resources.get_texture.assert_called_once_with(
            "assets/enemy.png"
        )

        renderer.render.assert_called_once_with(
            transform,
            renderable.color,
            texture,
        )


if __name__ == "__main__":
    unittest.main()
