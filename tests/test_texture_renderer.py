import unittest
from contextlib import ExitStack
from unittest.mock import Mock, patch

from engine.camera import Camera2D
from engine.ecs.components.transform import Transform
from engine.renderer import Renderer
from engine.texture import Texture
from engine.vector2 import Vector2


class FakeImage:
    width = 2
    height = 3

    def convert(self, mode):
        self.converted_mode = mode
        return self

    def tobytes(self):
        return b"pixels"


class TextureTests(unittest.TestCase):
    @patch("engine.texture.glDeleteTextures")
    @patch("engine.texture.glTexImage2D")
    @patch("engine.texture.glTexParameteri")
    @patch("engine.texture.glBindTexture")
    @patch("engine.texture.glGenTextures", return_value=42)
    @patch("engine.texture.Image.open")
    def test_loads_image_and_uploads_rgba_texture(
        self, open_image, gen_texture, bind, tex_parameter, tex_image, delete_texture
    ):
        image = FakeImage()
        open_image.return_value = image

        texture = Texture("image.png")

        self.assertEqual((texture.width, texture.height, texture.id), (2, 3, 42))
        open_image.assert_called_once_with("image.png")
        self.assertEqual(image.converted_mode, "RGBA")
        tex_image.assert_called_once()

        texture.shutdown()

    @patch("engine.texture.Image.open", side_effect=OSError("missing"))
    def test_image_loading_errors_are_propagated(self, open_image):
        with self.assertRaisesRegex(OSError, "missing"):
            Texture("missing.png")


class RendererTests(unittest.TestCase):
    def make_renderer(self):
        import engine.renderer as module

        stack = ExitStack()
        functions = [
            "glClearColor", "glEnable", "glBlendFunc", "glBindVertexArray",
            "glBindBuffer", "glBufferData", "glVertexAttribPointer",
            "glEnableVertexAttribArray", "glUseProgram", "glUniform1i",
            "glUniformMatrix4fv", "glUniform2f", "glUniform1f", "glUniform4f",
            "glActiveTexture", "glBindTexture", "glDrawElements", "glClear",
            "glViewport", "glDeleteBuffers", "glDeleteVertexArrays", "glDeleteProgram",
        ]
        mocks = {name: stack.enter_context(patch.object(module, name)) for name in functions}
        mocks["glGenVertexArrays" ] = stack.enter_context(patch.object(module, "glGenVertexArrays", return_value=10))
        buffer_ids = iter((20, 30))
        mocks["glGenBuffers"] = stack.enter_context(
            patch.object(module, "glGenBuffers", side_effect=lambda count: next(buffer_ids))
        )
        mocks["compileShader"] = stack.enter_context(patch.object(module, "compileShader", side_effect=lambda source, kind: kind))
        mocks["compileProgram"] = stack.enter_context(patch.object(module, "compileProgram", return_value=99))
        location = iter(range(1, 8))
        mocks["glGetUniformLocation"] = stack.enter_context(
            patch.object(module, "glGetUniformLocation", side_effect=lambda shader, name: next(location))
        )
        renderer = Renderer(Camera2D(), virtual_width=100, virtual_height=50)
        return stack, renderer, mocks

    def test_initialization_resize_render_and_shutdown(self):
        stack, renderer, mocks = self.make_renderer()
        try:
            renderer.resize(300, 100)
            self.assertEqual(mocks["glViewport"].call_args.args, (50, 0, 200, 100))

            renderer.resize(100, 100)
            self.assertEqual(mocks["glViewport"].call_args.args, (0, 25, 100, 50))

            renderer.begin_frame()
            texture = Mock(id=123)
            renderer.render(
                Transform(position=Vector2(10, 20), scale=Vector2(2, 3), rotation=0.5),
                (1.0, 0.5, 0.25, 1.0),
                texture,
            )
            renderer.render(
                Transform(position=Vector2(0, 0)),
                (0.0, 1.0, 0.0, 1.0),
            )
            renderer.shutdown()

            self.assertEqual(mocks["glDrawElements"].call_count, 2)
            self.assertEqual(mocks["glBindTexture"].call_args.args[-1], 123)
            self.assertEqual(mocks["glUniform1i"].call_args.args[-1], 0)
            mocks["glDeleteProgram"].assert_called_once_with(99)
        finally:
            stack.close()
