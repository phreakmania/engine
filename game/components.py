from dataclasses import dataclass

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
    duration: float
    remaining: float = 0.0