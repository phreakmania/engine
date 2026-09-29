from dataclasses import dataclass
from engine.texture import Texture

@dataclass
class QuadRenderable:
    color: tuple[float, float, float, float]
    texture: str | None = None