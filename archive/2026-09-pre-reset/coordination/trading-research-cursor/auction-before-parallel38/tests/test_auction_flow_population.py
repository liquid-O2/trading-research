import unittest

from trading_research.errors import IntegrityError
from trading_research.research.auction_flow_population import (
    choose_receipts, projected_resources, validate_catalog,
)


class PopulationTests(unittest.TestCase):
    def test_exact_membership_and_no_duplicate_physical_receipt(self):
        a = {"path": "/a", "sha256": "a" * 64, "size_bytes": 12}
        b = {"path": "/b", "sha256": "b" * 64, "size_bytes": 14}
        refs = validate_catalog({"receipts": [a, b], "receipt_count": 2}, expected_windows=2)
        self.assertEqual(choose_receipts(refs, {"phase": "full"}), [a, b])
        self.assertEqual(choose_receipts(refs, {"phase": "pilot", "pilot_receipts": [b]}), [b])
        with self.assertRaises(IntegrityError):
            validate_catalog({"receipts": [a, a], "receipt_count": 2}, expected_windows=2)
        with self.assertRaises(IntegrityError):
            choose_receipts(refs, {"phase": "pilot", "pilot_receipts": [{**b, "size_bytes": 15}]})

    def test_projection_uses_larger_cost_basis_and_preserves_population(self):
        inventory = [{"input_uncompressed_bytes": 1000, "atomic_cells_upper": 10},
                     {"input_uncompressed_bytes": 1000, "atomic_cells_upper": 30}]
        units = [{"input_uncompressed_bytes": 100, "observation_rows": 2,
                  "cpu_seconds": 1., "output_bytes": 20}]
        result = projected_resources(inventory, units)
        self.assertEqual(result["cpu_seconds_with_margin"], 30.)
        self.assertEqual(result["output_bytes_with_margin"], 600 + 16 * 1024**2)
        self.assertEqual(result["population_units"], 2)
        with self.assertRaises(IntegrityError):
            projected_resources(inventory, [{**units[0], "observation_rows": 0}])
