import glfw
from .key import Key

KEY_MAP = {
    Key.W: glfw.KEY_W,
    Key.A: glfw.KEY_A,
    Key.S: glfw.KEY_S,
    Key.D: glfw.KEY_D,
    Key.SPACE: glfw.KEY_SPACE,
}

class Window:
    def __init__(self, width=1280, height=720, title="New Window"):
        if not glfw.init():
            raise RuntimeError("Could not initialize glfw.")
        self.window = glfw.create_window(width, height, title, None, None)

        if not self.window:
            glfw.terminate()
            raise RuntimeError("Could not create window.")

        glfw.make_context_current(self.window)

    def is_key_pressed(self, key):
        glfw_key = KEY_MAP[key]

        return glfw.get_key(
            self.window,
            glfw_key,
        ) == glfw.PRESS

    def should_close(self):
        return glfw.window_should_close(self.window)

    def poll_events(self):
        glfw.poll_events()

    def swap_buffers(self):
        glfw.swap_buffers(self.window)

    def get_framebuffer_size(self):
        return glfw.get_framebuffer_size(self.window)

    def shutdown(self):
        glfw.destroy_window(self.window)
        glfw.terminate()
