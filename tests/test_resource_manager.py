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

    def test_different_paths_are_loaded_independently(self):
        resources = ResourceManager()

        with patch("engine.resource_manager.Texture") as texture_class:
            texture_class.side_effect = [object(), object()]
            first = resources.get_texture("one.png")
            second = resources.get_texture("two.png")

            self.assertIsNot(first, second)
            self.assertEqual(texture_class.call_count, 2)

    def test_failed_texture_load_can_be_retried(self):
        resources = ResourceManager()
        recovered_texture = object()

        with patch("engine.resource_manager.Texture") as texture_class:
            texture_class.side_effect = [OSError("missing"), recovered_texture]

            with self.assertRaisesRegex(OSError, "missing"):
                resources.get_texture("image.png")

            self.assertIs(resources.get_texture("image.png"), recovered_texture)
            self.assertIs(resources.get_texture("image.png"), recovered_texture)
            self.assertEqual(texture_class.call_count, 2)


if __name__ == "__main__":
    unittest.main()
