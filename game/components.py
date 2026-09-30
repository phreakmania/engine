from dataclasses import dataclass

from engine.timer import Timer


@dataclass
class BulletTag:
    pass

@dataclass
class EnemyTag:
    pass

@dataclass
class WallTag:
    pass

@dataclass
class PlayerTag:
    pass

@dataclass
class Damage:
    value: int

@dataclass
class Health:
    current: int    

@dataclass
class Invulnerability:
    timer: Timer