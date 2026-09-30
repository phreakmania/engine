import glfw

from .input import Input
from .renderer import Renderer
from .resource_manager import ResourceManager
from .window import Window


class Application:
    def __init__(self, game, width=1280, height=720, title="New Game"):
        self.window = Window(width, height, title)
        self.input = Input(self.window)
        self.renderer = Renderer(
            game.camera,
            virtual_width=1024,
            virtual_height=768,
        )
        self.resources = ResourceManager()
        self.game = game

    def run(self):
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
        self.game.render(self.renderer, self.resources)

    def shutdown(self):
        self.resources.shutdown()
        self.renderer.shutdown()
        self.window.shutdown()
