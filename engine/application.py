import glfw
from .window import Window
from .renderer import Renderer
from .input import Input

class Application:
    def __init__(self, game, width=1280, height=720, title="New Game"):
        self.window = Window(width, height, title)
        self.input = Input(self.window)
        self.renderer = Renderer(
            virtual_width=1280,
            virtual_height=720,
        )
        self.game = game

    def run(self: Application):
        last_time = glfw.get_time()

        while not self.window.should_close():
            current_time = glfw.get_time()
            dt = current_time-last_time
            last_time = current_time

            self.window.poll_events()
            self.input.update()
            self.update(dt)

            framebuffer_width, framebuffer_height = self.window.get_framebuffer_size()
            self.renderer.resize(framebuffer_width, framebuffer_height)

            self.renderer.begin_frame()
            self.render()
            self.window.swap_buffers()

        self.shutdown()

    def update(self, dt):
        self.game.update(dt, self.input)

    def render(self):
        self.game.render(self.renderer)

    def shutdown(self: Application):
        self.renderer.shutdown()
        self.window.shutdown()
