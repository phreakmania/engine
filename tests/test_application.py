import unittest
from unittest.mock import Mock, patch

from engine.application import Application


class ApplicationTests(unittest.TestCase):
    @patch("engine.application.glfw")
    @patch("engine.application.ResourceManager")
    @patch("engine.application.Renderer")
    @patch("engine.application.Input")
    @patch("engine.application.Window")
    def test_run_updates_renders_and_shuts_down(self, window_class, input_class, renderer_class, resources_class, glfw):
        window = window_class.return_value
        window.should_close.side_effect = (False, True)
        window.get_framebuffer_size.return_value = (800, 600)
        game = Mock(camera=Mock())
        app = Application(game, 800, 600, "Game")
        glfw.get_time.side_effect = (1.0, 1.25)

        app.run()

        game.update.assert_called_once_with(0.25, input_class.return_value)
        game.render.assert_called_once_with(renderer_class.return_value, resources_class.return_value)
        renderer_class.return_value.resize.assert_called_once_with(800, 600)
        renderer_class.return_value.begin_frame.assert_called_once()
        window.poll_events.assert_called_once()
        window.swap_buffers.assert_called_once()
        resources_class.return_value.shutdown.assert_called_once()
        renderer_class.return_value.shutdown.assert_called_once()
        window.shutdown.assert_called_once()

    @patch("engine.application.ResourceManager")
    @patch("engine.application.Renderer")
    @patch("engine.application.Window")
    def test_resources_are_created_after_renderer_and_shut_down_first(
        self, window_class, renderer_class, resources_class
    ):
        events = []
        window = window_class.return_value
        renderer = Mock()
        resources = Mock()

        def create_renderer(*args, **kwargs):
            events.append("renderer created")
            return renderer

        def create_resources():
            events.append("resources created")
            return resources

        renderer_class.side_effect = create_renderer
        resources_class.side_effect = create_resources
        resources.shutdown.side_effect = lambda: events.append("resources shut down")
        renderer.shutdown.side_effect = lambda: events.append("renderer shut down")
        window.shutdown.side_effect = lambda: events.append("window shut down")

        app = Application(Mock(camera=Mock()))
        app.shutdown()

        self.assertEqual(events, [
            "renderer created",
            "resources created",
            "resources shut down",
            "renderer shut down",
            "window shut down",
        ])

    @patch("engine.application.Renderer")
    @patch("engine.application.Input")
    @patch("engine.application.Window")
    def test_update_and_render_forward_to_game(self, window_class, input_class, renderer_class):
        game = Mock(camera=Mock())
        app = Application(game)

        app.update(0.5)
        app.render()

        game.update.assert_called_once_with(0.5, input_class.return_value)
        game.render.assert_called_once_with(renderer_class.return_value, app.resources)
