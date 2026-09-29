import unittest
from unittest.mock import patch
from engine.resource_manager import ResourceManager

class ResourceManagerTests(unittest.TestCase):
    def test_texture_is_cached(self):
        resources = ResourceManager()

        with patch("engine.resource_manager.Texture") as texture_class:
            texture1 = resources.get_texture("assets/enemy.png")
            texture2 = resources.get_texture("assets/enemy.png")

            assert texture1 is texture2
            texture_class.assert_called_once_with("assets/enemy.png")


if __name__ == "__main__":
    unittest.main()