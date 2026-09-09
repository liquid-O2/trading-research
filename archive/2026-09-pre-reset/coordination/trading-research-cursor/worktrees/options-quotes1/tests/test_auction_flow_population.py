import unittest

from trading_research.errors import IntegrityError
from trading_research.research.auction_flow_population import (
    choose_receipts, projected_resources, validate_catalog, require_serial_parity,
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

    def test_zero_row_fixed_cost_does_not_scale_by_nonempty_input_bytes(self):
        inventory = [{"input_uncompressed_bytes": 1000, "atomic_cells_upper": 100}] * 10
        units = [{"input_uncompressed_bytes": 1000, "observation_rows": 100,
                  "cpu_seconds": 1., "wall_seconds": 2., "output_bytes": 100},
                 {"input_uncompressed_bytes": 1, "observation_rows": 0,
                  "cpu_seconds": .1, "wall_seconds": .2, "output_bytes": 0}]
        result = projected_resources(inventory, units)
        self.assertEqual(result['cpu_seconds_with_margin'], 16.5)
        self.assertEqual(result['sequential_wall_seconds_with_margin'], 33.)

    def test_parallel_parity_joins_every_logical_value_and_validity(self):
        import copy
        row = {'receipt': {'sha256': 'a'}, 'atomic_rows': 2, 'instruments': 1,
               'trade_prints': 3, 'trade_volume': 7, 'eligibility_counts': {'full': 1},
               'whole_mass_checks': {'mass': True}, 'original_refs': {'measurement': 'b'},
               'series': {'rows': 2, 'schema': 'independent', 'roundtrip_exact': True,
                          'files': [{'rows': 2, 'path': '/serial',
                                     'row_group_values': [{'rows': 2, 'sha256': 'literalvalues'}]}]}}
        parallel = copy.deepcopy(row)
        parallel['series']['files'][0]['path'] = '/parallel'
        self.assertTrue(require_serial_parity([parallel], [row])['passed'])
        parallel['series']['files'][0]['row_group_values'][0]['sha256'] = 'changednullorvalue'
        with self.assertRaises(IntegrityError):
            require_serial_parity([parallel], [row])
        with self.assertRaises(IntegrityError):
            require_serial_parity([], [row])
