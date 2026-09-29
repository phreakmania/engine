from engine.transform import Transform
from engine.vector2 import Vector2
from engine.collision import intersects

class Player:
    def __init__(self, x=640.0, y=360.0, speed=200.0):

        self.transform = Transform(
            position=Vector2(x,y),
            scale=Vector2(32.0, 32.0),
        )
        self.color = (0.1,0.2,0.9,1.0)
        self.speed = speed
        self.health = 5

        self.invulnerability_duration = 0.5
        self.invulnerability_remaining = 0.0

    def is_dead(self):
        return self.health <= 0

    def take_damage(self, damage):
        if self.invulnerability_remaining > 0.0:
            return

        self.health -= damage

        self.invulnerability_remaining = self.invulnerability_duration

    def move(self, direction, dt, walls):
        direction = direction.normalized()

        movement = direction * self.speed * dt

        # X
        self.transform.position.x += movement.x

        for wall in walls:
            if intersects(self.transform, wall.transform):
                self.transform.position.x -= movement.x
                break

        # Y
        self.transform.position.y += movement.y

        for wall in walls:
            if intersects(self.transform, wall.transform):
                self.transform.position.y -= movement.y
                break

    def update(self, dt):
        if self.invulnerability_remaining > 0.0:
            self.invulnerability_remaining -= dt