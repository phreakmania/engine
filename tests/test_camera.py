import unittest

from engine.camera import Camera2D
from engine.vector2 import Vector2


class CameraTests(unittest.TestCase):
    def test_world_to_screen(self):
        camera = Camera2D()
        camera.position = Vector2(500.0, 300.0)

        screen_position = camera.world_to_screen(
            Vector2(700.0, 400.0)
        )

        self.assertEqual(screen_position.x, 200.0)
        self.assertEqual(screen_position.y, 100.0)


if __name__ == "__main__":
    unittest.main()
