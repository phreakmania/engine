import unittest
from unittest.mock import Mock, call

from engine.ecs.components.parent import Parent
from engine.vector2 import Vector2
from engine.ecs.world import World
from engine.ecs.systems.quad_render import quad_render_system
from engine.ecs.components.transform import Transform
from engine.ecs.components.quad_renderable import QuadRenderable


class QuadRenderSystemTests(unittest.TestCase):
    def test_renders_lower_z_index_before_higher_z_index(self):
        world = World()
        high_entity = world.create_entity()
        low_entity = world.create_entity()
        high_transform = Transform(position=Vector2(20.0, 20.0))
        low_transform = Transform(position=Vector2(10.0, 10.0))
        high_renderable = QuadRenderable(
            color=(1.0, 0.0, 0.0, 1.0),
            z_index=5,
        )
        low_renderable = QuadRenderable(
            color=(0.0, 1.0, 0.0, 1.0),
            z_index=-2,
        )
        world.add_component(high_entity, high_transform)
        world.add_component(high_entity, high_renderable)
        world.add_component(low_entity, low_transform)
        world.add_component(low_entity, low_renderable)
        renderer = Mock()

        quad_render_system(world, renderer, Mock())

        self.assertEqual(renderer.render.call_args_list, [
            call(low_transform, low_renderable.color, None),
            call(high_transform, high_renderable.color, None),
        ])

    def test_renders_without_requesting_optional_texture(self):
        transform = Transform(position=Vector2(10.0, 20.0))
        renderable = QuadRenderable(color=(1.0, 1.0, 1.0, 1.0))
        world = World()

        entity = world.create_entity()
        world.add_component(entity, transform)
        world.add_component(entity, renderable)
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

        world = World()

        entity = world.create_entity()
        world.add_component(entity, transform)
        world.add_component(entity, renderable)

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

    def test_renders_child_at_world_position_relative_to_parent(self):
        world = World()

        parent = world.create_entity()
        world.add_component(
            parent,
            Transform(
                position=Vector2(100.0, 50.0),
            ),
        )

        child = world.create_entity()
        local_transform = Transform(
            position=Vector2(20.0, 10.0),
            scale=Vector2(8.0, 8.0),
        )
        renderable = QuadRenderable(
            color=(1.0, 1.0, 0.0, 1.0),
        )

        world.add_component(child, local_transform)
        world.add_component(child, Parent(parent))
        world.add_component(child, renderable)

        renderer = Mock()
        resources = Mock()

        quad_render_system(
            world,
            renderer,
            resources,
        )

        renderer.render.assert_called_once()

        rendered_transform = renderer.render.call_args.args[0]

        self.assertEqual(
            rendered_transform.position,
            Vector2(120.0, 60.0),
        )
        self.assertEqual(
            rendered_transform.scale,
            Vector2(8.0, 8.0),
        )

if __name__ == "__main__":
    unittest.main()
