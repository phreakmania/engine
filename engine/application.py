import glfw
from .window import Window
from .renderer import Renderer

class Application:
    def __init__(self, width=1280, height=720, title="New Game"):
        self.window = Window(width, height, title)
        self.renderer = Renderer()

    def run(self: Application):
        last_time = glfw.get_time()

        while not self.window.should_close():
            current_time = glfw.get_time()
            dt = current_time-last_time
            last_time = current_time

            self.window.poll_events()
            self.update(dt)
            self.render()
            self.window.swap_buffers()

        self.shutdown()

    def update(self: Application, dt:float):
        print(f"dt: {dt:.6f}")

    def render(self: Application):
        self.renderer.render()

    def shutdown(self: Application):
        self.renderer.shutdown()
        self.window.shutdown()
