from .key import Key


class Input:
    def __init__(self, window):
        self.window = window

        self.current_keys = {}
        self.previous_keys = {}

    def update(self):
        self.previous_keys = self.current_keys.copy()

        self.current_keys = {
            key: self.window.is_key_pressed(key)
            for key in Key
        }

    def is_key_down(self, key):
        return self.current_keys.get(key, False)

    def was_key_pressed(self, key):
        return (
            self.current_keys.get(key, False)
            and not self.previous_keys.get(key, False)
        )