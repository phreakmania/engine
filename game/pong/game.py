from .components import LeftPlayerTag, RightPlayerTag

from engine.ecs.component_registry import ComponentRegistry
from engine.scene_loader import SceneLoader
from engine.camera import Camera2D
from engine.ecs.systems.quad_render import quad_render_system

class Game:
    def __init__(self, width, height):
        self.viewport_width = width
        self.viewport_height = height
        self.world_width = 800.0
        self.world_height = 600.0

        registry = ComponentRegistry()

        registry.register(
            "LeftPlayer",
            lambda data: LeftPlayerTag()
        )
        registry.register(
            "RightPlayer",
            lambda data: RightPlayerTag()
        )

        self.scene_loader = SceneLoader(registry)
        self.scene = self.scene_loader.load("game/pong/assets/scenes/main.json")
        self.world = self.scene.world
        self.camera = Camera2D()

    def update(self, dt, input):
        pass

    def render(self, renderer, resources):
        quad_render_system(
            self.world,
            renderer,
            resources,
        )

