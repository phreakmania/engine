import ctypes
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

class Renderer:
    def __init__(self):
        vertex_shader_source = """
        #version 330 core

        layout (location = 0) in vec2 position;

        void main()
        {
            gl_Position = vec4(position, 0.0, 1.0);
        }
        """

        fragment_shader_source = """
        #version 330 core

        out vec4 fragment_color;

        void main()
        {
            fragment_color = vec4(0.2, 0.8, 0.7, 1.0);
        }
        """

        glClearColor(0.1,0.15,0.2,1.0)

        vertices = np.array([
            0.0,  0.5,
            -0.5, -0.5,
            0.5, -0.5,
        ], dtype=np.float32)

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

        glVertexAttribPointer(
            0,
            2,
            GL_FLOAT,
            GL_FALSE,
            2 * vertices.itemsize,
            ctypes.c_void_p(0),
        )

        glEnableVertexAttribArray(0)

        self.shader = compileProgram(
            compileShader(vertex_shader_source, GL_VERTEX_SHADER),
            compileShader(fragment_shader_source, GL_FRAGMENT_SHADER),
        )

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(self.shader)
        glBindVertexArray(self.vao)

        glDrawArrays(GL_TRIANGLES, 0, 3)

    def shutdown(self):
        glDeleteBuffers(1, [self.vbo])
        glDeleteVertexArrays(1, [self.vao])
        glDeleteProgram(self.shader)
