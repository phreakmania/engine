from PIL import Image
from OpenGL.GL import *


class Texture:
    def __init__(self, path):
        image = Image.open(path).convert("RGBA")

        self.width = image.width
        self.height = image.height

        pixels = image.tobytes()

        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)

        glTexParameteri(
            GL_TEXTURE_2D,
            GL_TEXTURE_MIN_FILTER,
            GL_NEAREST,
        )

        glTexParameteri(
            GL_TEXTURE_2D,
            GL_TEXTURE_MAG_FILTER,
            GL_NEAREST,
        )

        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            self.width,
            self.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            pixels,
        )

    def shutdown(self):
        glDeleteTextures(1, [self.id])