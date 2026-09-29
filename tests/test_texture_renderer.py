import unittest
from contextlib import ExitStack
from unittest.mock import Mock, call, patch

from PIL import Image

from engine.camera import Camera2D
from engine.ecs.components.transform import Transform
from engine.renderer import Renderer
from engine.texture import Texture
from engine import texture as texture_module
from engine.vector2 import Vector2


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
        image = Image.new("RGBA", (2, 1))
        image.putdata(((255, 0, 0, 255), (0, 255, 0, 64)))
        open_image.return_value = image
        gl = Mock()
        gl.attach_mock(gen_texture, "generate")
        gl.attach_mock(bind, "bind")
        gl.attach_mock(tex_parameter, "parameter")
        gl.attach_mock(tex_image, "upload")
        gl.attach_mock(delete_texture, "delete")

        texture = Texture("image.png")
        texture.shutdown()

        self.assertEqual((texture.width, texture.height, texture.id), (2, 1, 42))
        open_image.assert_called_once_with("image.png")
        self.assertEqual(gl.mock_calls, [
            call.generate(1),
            call.bind(texture_module.GL_TEXTURE_2D, 42),
            call.parameter(
                texture_module.GL_TEXTURE_2D,
                texture_module.GL_TEXTURE_MIN_FILTER,
                texture_module.GL_NEAREST,
            ),
            call.parameter(
                texture_module.GL_TEXTURE_2D,
                texture_module.GL_TEXTURE_MAG_FILTER,
                texture_module.GL_NEAREST,
            ),
            call.upload(
                texture_module.GL_TEXTURE_2D,
                0,
                texture_module.GL_RGBA,
                2,
                1,
                0,
                texture_module.GL_RGBA,
                texture_module.GL_UNSIGNED_BYTE,
                bytes((255, 0, 0, 255, 0, 255, 0, 64)),
            ),
            call.delete(1, [42]),
        ])

    @patch("engine.texture.glTexImage2D")
    @patch("engine.texture.glTexParameteri")
    @patch("engine.texture.glBindTexture")
    @patch("engine.texture.glGenTextures", return_value=7)
    @patch("engine.texture.Image.open")
    def test_rgb_image_gets_opaque_alpha_channel(
        self, open_image, gen_texture, bind, tex_parameter, tex_image
    ):
        open_image.return_value = Image.new("RGB", (1, 1), (10, 20, 30))

        Texture("rgb.png")

        self.assertEqual(tex_image.call_args.args[-1], bytes((10, 20, 30, 255)))

    @patch("engine.texture.glTexImage2D", side_effect=RuntimeError("GPU upload failed"))
    @patch("engine.texture.glTexParameteri")
    @patch("engine.texture.glBindTexture")
    @patch("engine.texture.glGenTextures", return_value=7)
    @patch("engine.texture.Image.open")
    def test_gpu_upload_error_is_propagated(
        self, open_image, gen_texture, bind, tex_parameter, tex_image
    ):
        open_image.return_value = Image.new("RGBA", (1, 1))

        with self.assertRaisesRegex(RuntimeError, "GPU upload failed"):
            Texture("image.png")

        tex_image.assert_called_once()

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
