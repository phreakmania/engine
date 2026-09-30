from dataclasses import dataclass


@dataclass
class QuadRenderable:
    color: tuple[float, float, float, float]
    texture: str | None = None
    z_index: int = 0
