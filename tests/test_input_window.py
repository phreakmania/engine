import unittest
from unittest.mock import patch

from engine.input import Input
from engine.key import Key
from engine.window import Window


class InputTests(unittest.TestCase):
    def test_update_tracks_current_and_previous_key_states(self):
        window = unittest.mock.Mock()
        window.is_key_pressed.side_effect = lambda key: key is Key.SPACE
        input_state = Input(window)

        input_state.update()
        self.assertTrue(input_state.is_key_down(Key.SPACE))
        self.assertTrue(input_state.was_key_pressed(Key.SPACE))
        self.assertFalse(input_state.is_key_down(Key.W))

        input_state.update()
        self.assertFalse(input_state.was_key_pressed(Key.SPACE))
        self.assertEqual(window.is_key_pressed.call_count, len(Key) * 2)

    def test_unknown_key_is_not_pressed(self):
        input_state = Input(unittest.mock.Mock())

        self.assertFalse(input_state.is_key_down("unknown"))
        self.assertFalse(input_state.was_key_pressed("unknown"))


class WindowTests(unittest.TestCase):
    @patch("engine.window.glfw")
    def test_window_lifecycle_and_queries(self, glfw):
        glfw.init.return_value = True
        glfw.create_window.return_value = object()
        glfw.get_key.return_value = glfw.PRESS
        glfw.window_should_close.return_value = False
        glfw.get_framebuffer_size.return_value = (800, 600)

        window = Window(800, 600, "Test")

        self.assertTrue(window.is_key_pressed(Key.W))
        self.assertFalse(window.should_close())
        self.assertEqual(window.get_framebuffer_size(), (800, 600))
        window.poll_events()
        window.swap_buffers()
        window.shutdown()

        glfw.make_context_current.assert_called_once_with(window.window)
        glfw.destroy_window.assert_called_once_with(window.window)
        glfw.terminate.assert_called_once()

    @patch("engine.window.glfw")
    def test_window_rejects_failed_initialization(self, glfw):
        glfw.init.return_value = False

        with self.assertRaisesRegex(RuntimeError, "initialize glfw"):
            Window()

    @patch("engine.window.glfw")
    def test_window_rejects_failed_creation_and_terminates(self, glfw):
        glfw.init.return_value = True
        glfw.create_window.return_value = None

        with self.assertRaisesRegex(RuntimeError, "create window"):
            Window()

        glfw.terminate.assert_called_once()
