import ctypes

import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from engine.camera import Camera2D


class Renderer:
    def __init__(self, camera: Camera2D, virtual_width=1280, virtual_height=720):
        self.camera = camera
        self.virtual_width = virtual_width
        self.virtual_height = virtual_height

        vertex_shader_source = """
        #version 330 core

        layout (location = 0) in vec2 position;
        layout (location = 1) in vec2 uv;

        out vec2 texture_uv;

        uniform vec2 offset;
        uniform vec2 size;
        uniform float rotation;
        uniform mat4 projection;

        void main()
        {
            vec2 scaled_position = position * size;

            float c = cos(rotation);
            float s = sin(rotation);

            vec2 rotated_position = vec2(
                scaled_position.x * c - scaled_position.y * s,
                scaled_position.x * s + scaled_position.y * c
            );

            gl_Position = projection * vec4(
                rotated_position + offset,
                0.0,
                1.0
            );

            texture_uv = uv;
        }
        """

        fragment_shader_source = """
        #version 330 core

        in vec2 texture_uv;

        out vec4 fragment_color;

        uniform vec4 color;
        uniform sampler2D texture_sampler;
        uniform bool use_texture;

        void main()
        {
            if (use_texture)
            {
                fragment_color = texture(
                    texture_sampler,
                    texture_uv
                );
            }
            else
            {
                fragment_color = color;
            }
        }
        """


        glClearColor(0.1,0.15,0.2,1.0)


        glEnable(GL_BLEND)

        glBlendFunc(
            GL_SRC_ALPHA,
            GL_ONE_MINUS_SRC_ALPHA,
        )
        
        vertices = np.array([
            -0.5, -0.5,  0.0, 0.0,
            0.5, -0.5,  1.0, 0.0,
            0.5,  0.5,  1.0, 1.0,
            -0.5,  0.5,  0.0, 1.0,
        ], dtype=np.float32)

        indices = np.array([
            0, 3, 1,
            1, 3, 2,
        ], dtype=np.uint32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glBufferData(
            GL_ARRAY_BUFFER,
            vertices.nbytes,
            vertices,
            GL_STATIC_DRAW,
        )

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)

        glBufferData(
            GL_ELEMENT_ARRAY_BUFFER,
            indices.nbytes,
            indices,
            GL_STATIC_DRAW,
        )

        glVertexAttribPointer(
            0,
            2,
            GL_FLOAT,
            GL_FALSE,
            4 * vertices.itemsize,
            ctypes.c_void_p(0),
        )
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(
            1,
            2,
            GL_FLOAT,
            GL_FALSE,
            4 * vertices.itemsize,
            ctypes.c_void_p(2 * vertices.itemsize),
        )
        glEnableVertexAttribArray(1)

        self.shader = compileProgram(
            compileShader(vertex_shader_source, GL_VERTEX_SHADER),
            compileShader(fragment_shader_source, GL_FRAGMENT_SHADER),
        )
 
        self.offset_location = glGetUniformLocation(
            self.shader,
            "offset",
        )

        self.size_location = glGetUniformLocation(
            self.shader,
            "size",
        )

        self.rotation_location = glGetUniformLocation(
            self.shader,
            "rotation",
        )

        self.projection_location = glGetUniformLocation(
            self.shader,
            "projection",
        )

        self.color_location = glGetUniformLocation(
            self.shader,
            "color",
        )

        self.use_texture_location = glGetUniformLocation(
            self.shader,
            "use_texture",
        )

        self.texture_sampler_location = glGetUniformLocation(
            self.shader,
            "texture_sampler",
        )

        projection = np.array([
            [2.0 / virtual_width,    0.0,                   0.0, -1.0],
            [0.0,                   -2.0 / virtual_height,  0.0,  1.0],
            [0.0,                    0.0,                   1.0,  0.0],
            [0.0,                    0.0,                   0.0,  1.0],
        ], dtype=np.float32)

        glUseProgram(self.shader)

        glUniform1i(
            self.texture_sampler_location,
            0,
        )
        
        glUniformMatrix4fv(
            self.projection_location,
            1,
            GL_TRUE,
            projection,
        )


    def resize(self, framebuffer_width, framebuffer_height):
        target_aspect = self.virtual_width / self.virtual_height
        window_aspect = framebuffer_width / framebuffer_height

        if window_aspect > target_aspect:
            viewport_height = framebuffer_height
            viewport_width = int(viewport_height * target_aspect)

            viewport_x = (framebuffer_width - viewport_width) // 2
            viewport_y = 0
        else:
            viewport_width = framebuffer_width
            viewport_height = int(viewport_width / target_aspect)

            viewport_x = 0
            viewport_y = (framebuffer_height - viewport_height) // 2

        glViewport(
            viewport_x,
            viewport_y,
            viewport_width,
            viewport_height,
        )

    def begin_frame(self):
        glClear(GL_COLOR_BUFFER_BIT)

    def render(self, transform, color, texture=None):
        glUseProgram(self.shader)
        glBindVertexArray(self.vao)

        screen_position = self.camera.world_to_screen(
            transform.position
        )

        glUniform2f(
            self.offset_location,
            screen_position.x,
            screen_position.y,
        )

        glUniform2f(
            self.size_location,
            transform.scale.x,
            transform.scale.y,
        )

        glUniform1f(
            self.rotation_location,
            transform.rotation
        )

        glUniform4f(
            self.color_location,
            color[0],
            color[1],
            color[2],
            color[3]
        )

        if texture is not None:
            glUniform1i(
                self.use_texture_location,
                1,
            )

            glActiveTexture(GL_TEXTURE0)
            glBindTexture(
                GL_TEXTURE_2D,
                texture.id,
            )
        else:
            glUniform1i(
                self.use_texture_location,
                0,
            )

        glDrawElements(
            GL_TRIANGLES,
            6,
            GL_UNSIGNED_INT,
            None,
        )

    def shutdown(self):
        glDeleteBuffers(1, [self.vbo])
        glDeleteBuffers(1, [self.ebo])
        glDeleteVertexArrays(1, [self.vao])
        glDeleteProgram(self.shader)
