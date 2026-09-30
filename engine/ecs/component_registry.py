
from ..vector2 import Vector2
from .components.player_spawn import PlayerSpawn
from .components.transform import Transform
from .components.velocity import Velocity
from .components.quad_renderable import QuadRenderable

class ComponentRegistry:
    def __init__(self):
        self._loaders = {}
        self._register_engine_components()

    def _register_engine_components(self):
        self.register(
                    "Transform",
                    lambda data: Transform(
                        position=Vector2(*data["position"]),
                        scale=Vector2(*data["scale"]),
                        rotation=data["rotation"],
                    )
                )
        
        self.register(
            "QuadRenderable",
            lambda data: QuadRenderable(
                color=tuple(data["color"]),
                texture=data.get("texture")
            )
        )

        self.register(
            "Velocity",
            lambda data: Velocity(
                value=Vector2(*data["value"])
            )
        )

        self.register(
            "PlayerSpawn",
            lambda data: PlayerSpawn()
        )
        

    def register(self, name, loader):
        self._loaders[name] = loader

    def create(self, name, data):
        return self._loaders[name](data)