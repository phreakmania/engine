from dataclasses import dataclass

from engine.vector2 import Vector2


@dataclass
class Velocity:
    value: Vector2


@dataclass
class Health:
    value: int


@dataclass
class Damage:
    value: int


@dataclass
class Renderable:
    color: tuple

@dataclass
class Player:
    pass


@dataclass
class Enemy:
    pass


@dataclass
class Bullet:
    pass


@dataclass
class Wall:
    pass    