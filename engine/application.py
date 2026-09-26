import glfw
from .window import Window
from .renderer import Renderer

class Application:
    def __init__(self, width=1280, height=720, title="New Game"):
        self.window = Window(width, height, title)
        self.renderer = Renderer()
        self.player_x = 0.0
        self.player_y = 0.0 

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

    def update(self, dt):
        speed = 0.5

        if self.window.is_key_pressed("d"):
            self.player_x += speed * dt

        if self.window.is_key_pressed("a"):
            self.player_x -= speed * dt

        if self.window.is_key_pressed("w"):
            self.player_y += speed * dt

        if self.window.is_key_pressed("s"):
            self.player_y -= speed * dt

    def render(self):
        self.renderer.render(
            self.player_x,
            self.player_y,
        )

    def shutdown(self: Application):
        self.renderer.shutdown()
        self.window.shutdown()
