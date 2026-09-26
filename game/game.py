from .player import Player

class Game:
    def __init__(self):
        self.player = Player()

    def update(self, dt, window):
        direction_x = 0.0
        direction_y = 0.0

        if window.is_key_pressed("d"):
            direction_x += 1.0

        if window.is_key_pressed("a"):
            direction_x -= 1.0

        if window.is_key_pressed("w"):
            direction_y -= 1.0

        if window.is_key_pressed("s"):
            direction_y += 1.0

        self.player.move(
            direction_x,
            direction_y,
            dt,
        )