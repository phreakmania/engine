from .texture import Texture

class ResourceManager:
    def __init__(self):
        self._textures: dict[str, Texture] = {}

    def get_texture(self, path: str) -> Texture:
        if path not in self._textures:
            self._textures[path] = Texture(path)

        return self._textures[path]