from __future__ import annotations

import unittest

from core.detector import _first_row_values, _first_scalar


class DetectorHelperTests(unittest.TestCase):
    def test_first_row_values_returns_empty_list_for_empty_input(self):
        self.assertEqual([], _first_row_values([]))

    def test_first_row_values_reads_plain_nested_list(self):
        self.assertEqual([1, 2, 3, 4], _first_row_values([[1, 2, 3, 4]]))

    def test_first_scalar_uses_default_for_empty_input(self):
        self.assertEqual(0.5, _first_scalar([], default=0.5))


if __name__ == "__main__":
    unittest.main()
