from dataclasses import dataclass

@dataclass
class BulletTag:
    pass

@dataclass
class EnemyTag:
    pass

@dataclass
class Damage:
    value: int

@dataclass
class Health:
    current: int    