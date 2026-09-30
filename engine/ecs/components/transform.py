from dataclasses import dataclass, field

from ...vector2 import Vector2


@dataclass
class Transform:
    position: Vector2 = field(default_factory=Vector2)

    scale: Vector2 = field(
        default_factory=lambda: Vector2(1.0, 1.0)
    )

    rotation: float = 0.0