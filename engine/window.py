import glfw

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
        keys = {
            "w": glfw.KEY_W,
            "a": glfw.KEY_A,
            "s": glfw.KEY_S,
            "d": glfw.KEY_D,
        }

        glfw_key = keys[key]

        return glfw.get_key(self.window, glfw_key) == glfw.PRESS

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
