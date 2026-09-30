import unittest

from engine.collision import intersects
from engine.ecs.components.transform import Transform
from engine.vector2 import Vector2


class Vector2Tests(unittest.TestCase):
    def test_defaults_and_length(self):
        vector = Vector2()

        self.assertEqual((vector.x, vector.y), (0.0, 0.0))
        self.assertEqual(Vector2(3.0, 4.0).length(), 5.0)

    def test_arithmetic_returns_new_vectors(self):
        left = Vector2(3.0, 4.0)
        right = Vector2(1.0, 2.0)

        self.assertEqual((left + right).x, 4.0)
        self.assertEqual((left + right).y, 6.0)
        self.assertEqual((left - right).x, 2.0)
        self.assertEqual((left - right).y, 2.0)
        self.assertEqual((left * 2.0).x, 6.0)
        self.assertEqual((left * 2.0).y, 8.0)
        self.assertEqual((left / 2.0).x, 1.5)
        self.assertEqual((left / 2.0).y, 2.0)

    def test_normalized_vector_has_unit_length(self):
        normalized = Vector2(3.0, 4.0).normalized()

        self.assertAlmostEqual(normalized.length(), 1.0)
        self.assertEqual((normalized.x, normalized.y), (0.6, 0.8))

    def test_zero_vector_normalizes_to_zero(self):
        self.assertEqual(
            (Vector2().normalized().x, Vector2().normalized().y),
            (0.0, 0.0),
        )

    def test_dividing_by_zero_is_rejected(self):
        with self.assertRaisesRegex(ZeroDivisionError, "Cannot divide Vector2 by zero"):
            Vector2(1.0, 2.0) / 0


class CollisionTests(unittest.TestCase):
    def test_overlapping_boxes_intersect(self):
        self.assertTrue(
            intersects(
                Transform(position=Vector2(0.0, 0.0), scale=Vector2(2.0, 2.0)),
                Transform(position=Vector2(1.0, 1.0), scale=Vector2(2.0, 2.0)),
            )
        )

    def test_touching_boxes_do_not_intersect(self):
        self.assertFalse(
            intersects(
                Transform(position=Vector2(0.0, 0.0), scale=Vector2(2.0, 2.0)),
                Transform(position=Vector2(2.0, 0.0), scale=Vector2(2.0, 2.0)),
            )
        )

    def test_separated_boxes_do_not_intersect(self):
        self.assertFalse(
            intersects(
                Transform(position=Vector2(0.0, 0.0), scale=Vector2(2.0, 2.0)),
                Transform(position=Vector2(5.0, 0.0), scale=Vector2(2.0, 2.0)),
            )
        )
