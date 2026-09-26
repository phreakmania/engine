import math


class Player:
    def __init__(self, x=640.0, y=360.0, speed=200.0):
        self.x = x
        self.y = y
        self.speed = speed

    def move(self, direction_x, direction_y, dt):
        length = math.sqrt(
            direction_x * direction_x +
            direction_y * direction_y
        )

        if length > 0:
            direction_x /= length
            direction_y /= length

        self.x += direction_x * self.speed * dt
        self.y += direction_y * self.speed * dt