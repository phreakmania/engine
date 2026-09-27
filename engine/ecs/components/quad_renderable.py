from dataclasses import dataclass


@dataclass
class QuadRenderable:
    color: tuple[float, float, float, float]