from __future__ import annotations

import unittest

from core.zone import point_in_polygon, validate_zones


class ZoneTests(unittest.TestCase):
    def test_point_inside_polygon(self):
        polygon = [[0, 0], [10, 0], [10, 10], [0, 10]]
        self.assertTrue(point_in_polygon((5, 5), polygon))

    def test_point_outside_polygon(self):
        polygon = [[0, 0], [10, 0], [10, 10], [0, 10]]
        self.assertFalse(point_in_polygon((15, 5), polygon))

    def test_point_on_boundary_is_inside(self):
        polygon = [[0, 0], [10, 0], [10, 10], [0, 10]]
        self.assertTrue(point_in_polygon((10, 5), polygon))

    def test_validate_rejects_empty_zones(self):
        ok, error, zones = validate_zones([])
        self.assertFalse(ok)
        self.assertIsNotNone(error)
        self.assertEqual([], zones)

    def test_validate_rejects_zone_with_less_than_three_points(self):
        ok, error, _ = validate_zones([[[0, 0], [1, 1]]])
        self.assertFalse(ok)
        self.assertIn("at least 3 points", error or "")

    def test_validate_accepts_json_friendly_lists(self):
        ok, error, zones = validate_zones([[[0, 0], [10, 0], [10, 10]]])
        self.assertTrue(ok)
        self.assertIsNone(error)
        self.assertEqual([[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0]]], zones)

    def test_validate_rejects_bad_point(self):
        ok, error, _ = validate_zones([[[0, 0], [10, 0], ["x", 10]]])
        self.assertFalse(ok)
        self.assertIn("not numeric", error or "")


if __name__ == "__main__":
    unittest.main()

