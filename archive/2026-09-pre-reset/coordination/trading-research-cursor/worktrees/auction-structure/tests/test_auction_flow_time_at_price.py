from pathlib import Path
import tempfile
import unittest

import pyarrow as pa

from trading_research.errors import IntegrityError
from trading_research.research.auction_flow_data import AuctionFlowStream
from trading_research.research.auction_flow_time_at_price import TimeAtPrice
from tests import test_auction_flow_data as source
from references import auction_measurements_literal as literal


class AuctionFlowTimeAtPriceTests(unittest.TestCase):
    def rows(self):
        return [source.raw(0), source.raw(1, action='T', price=100., flags=0),
            source.raw(3, action='T', price=102., flags=0), source.raw(3, action='T', price=101., flags=0),
            source.raw(9, action='T', price=101., flags=0), source.raw(21, action='T', price=103., flags=0),
            source.raw(25), source.raw(29, action='T', price=102., flags=0),
            source.raw(41, action='T', price=101., flags=0), source.raw(60)]

    def accumulator(self):
        return TimeAtPrice(instrument_id=1, start_ns=0, end_ns=60, atomic_width_ns=10,
            bracket_widths_ns=(20, 30), stale_caps_ns=(3, 10), initial_balance_ns=20, latency_ns=250)

    def batches(self, root, footer, batch_rows):
        return AuctionFlowStream(data_root=root, index=footer, dataset=source.DATASET, start_ns=0, end_ns=60,
            maximum_scan_rows=100, latency_ns=250, batch_rows=batch_rows)

    def measure(self, rows, *, intervals=((0, 60),), batch_rows=2):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            footer = source.AuctionFlowDataTests().write(root, rows)
            value = self.accumulator()
            for batch in self.batches(root, footer, batch_rows):
                value.add(batch.raw, batch.trades[0] if batch.trades else None, source_key=batch.source['source_key'])
            return value.finish(covered_intervals=intervals, minimum_brackets=2)

    def test_actual_visits_do_not_fill_price_gaps_and_equal_time_prints_keep_their_order(self):
        result = self.measure(self.rows())
        tpo = result['tpo'][0]
        self.assertEqual(tpo['row_bracket_incidence'], ((400, (0,)), (404, (0, 2)), (408, (0, 1)), (412, (1,))))
        self.assertEqual(tpo['confirmed_single_rows'], (400, 412))
        self.assertEqual(tpo['observed_tails'], {'low': (400,), 'high': (412,), 'low_same_bracket': True, 'high_same_bracket': True})
        self.assertEqual(tpo['value_areas']['7/10'].poc_maximizers, (404, 408))
        self.assertEqual(result['initial_balance']['observed_low_ticks'], 400)
        self.assertEqual(result['initial_balance']['observed_high_ticks'], 408)
        self.assertTrue(result['initial_balance']['history_complete'])
        self.assertEqual(result['eligible_prints'], 7)
        events = [(row['t'], round(row['price'] * 4)) for row in self.rows() if row['action'] == 'T']
        expected = literal.tpo(events, [(0, 20), (20, 40), (40, 60)])
        self.assertEqual(tpo['row_bracket_incidence'], expected)

    def test_dwell_is_bounded_and_same_time_intermediate_print_has_no_positive_duration(self):
        result = self.measure(self.rows())
        small, large = result['dwell']
        self.assertEqual(small['observed_assigned_duration_ns'], 17)
        self.assertEqual(large['observed_assigned_duration_ns'], 46)
        masses = {}
        for _, row, amount in small['atomic_duration_ns_by_row']:
            masses[row] = masses.get(row, 0) + amount
        self.assertEqual(masses, {400: 2, 404: 9, 408: 3, 412: 3})
        self.assertIn((1, 404, 2), small['atomic_duration_ns_by_row'])
        self.assertEqual(small['unassigned_duration_ns'], 43)
        self.assertEqual(large['true_per_row_upper_ns'], 60)
        self.assertFalse(result['true_residence_claim'])

    def test_batch_layout_preserves_physical_first_visits_and_all_integer_durations(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            footer = source.AuctionFlowDataTests().write(root, self.rows())
            outputs = []
            for batch_rows in (1, 2, 17):
                value = self.accumulator()
                for batch in self.batches(root, footer, batch_rows):
                    value.add(batch.raw, batch.trades[0] if batch.trades else None, source_key=batch.source['source_key'])
                outputs.append(value.finish(covered_intervals=((0, 20), (20, 60)), minimum_brackets=2))
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(outputs[1], outputs[2])

    def test_actual_invalidation_stops_dwell_without_erasing_prints_or_accepting_a_complete_bracket(self):
        rows = self.rows()
        rows[6] = source.raw(22, action='N', flags=4)
        result = self.measure(rows)
        self.assertEqual(result['eligible_prints'], 7)
        self.assertEqual(result['dwell'][1]['observed_assigned_duration_ns'], 39)
        self.assertFalse(result['dwell'][1]['history_complete'])
        self.assertFalse(result['tpo'][0]['brackets'][1]['history_complete'])
        self.assertIsNone(result['tpo'][0]['confirmed_single_rows'])
        self.assertEqual(result['tpo'][0]['row_bracket_incidence'], self.measure(self.rows())['tpo'][0]['row_bracket_incidence'])

    def test_unpriced_and_unobserved_are_separate_from_an_observed_quiet_window(self):
        rows = self.rows()
        rows[8] = source.raw(41, action='T', price=100.1, flags=0)
        result = self.measure(rows)
        self.assertEqual(result['unpriced_prints'], 1)
        self.assertEqual(result['dwell'][1]['observed_assigned_duration_ns'], 36)
        self.assertFalse(result['tpo'][0]['brackets'][2]['history_complete'])
        quiet = self.measure([source.raw(0), source.raw(60)])
        missing = self.measure([source.raw(0), source.raw(60)], intervals=())
        self.assertTrue(quiet['tpo'][0]['history_complete'])
        self.assertEqual(quiet['dwell'][0]['observed_assigned_duration_ns'], 0)
        self.assertFalse(missing['tpo'][0]['history_complete'])
        self.assertIsNone(missing['dwell'][0]['true_per_row_upper_ns'])

    def test_changed_trade_address_poisoned_window_cannot_publish_or_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            footer = source.AuctionFlowDataTests().write(root, self.rows())
            batch = next(iter(self.batches(root, footer, 17)))
            table = batch.trades[0]
            forged = table.set_column(table.schema.get_field_index('source_row'), 'source_row',
                pa.array([999] * len(table), type=pa.int64()))
            value = self.accumulator()
            with self.assertRaises(IntegrityError):
                value.add(batch.raw, forged, source_key=batch.source['source_key'])
            with self.assertRaises(IntegrityError):
                value.finish(covered_intervals=((0, 60),))
            with self.assertRaises(IntegrityError):
                value.add(batch.raw, table, source_key=batch.source['source_key'])
