from pathlib import Path
import tempfile
import unittest

from trading_research.errors import IntegrityError
from trading_research.research.auction_flow_coordinates import RetainedCoordinateIndex
from trading_research.research.auction_flow_native_bins import NativeEventBins, QUOTE_FIELDS
from trading_research.research.auction_flow_pipeline import coordinate_window, measure_raw_window
from trading_research.research.auction_flow_preflight import measured_unit
from trading_research.research.auction_flow_quotes import QuoteWindow
from trading_research.research.auction_flow_storage import BoundedOutputs
from tests.test_auction_flow_coordinates import record, manifest
from tests.test_auction_flow_data import AuctionFlowDataTests
from tests.test_auction_flow_quotes import frozen_quote_window, raw, replay_atomic


class AuctionFlowPipelineTests(unittest.TestCase):
    def test_native_and_event_values_survive_an_aligned_partition_without_book_or_age_reset(self):
        import pyarrow as pa
        from trading_research.research.auction_flow_arrow import value_digest
        rows = self.rows()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            footer = AuctionFlowDataTests().write(root, rows)
            def run(a, b, continuation=None):
                native, trades, quotes = [], [], []
                def retain(table, metadata):
                    native.append(table)
                    return {'rows': len(table)}
                result = measure_raw_window(data_root=root, index=footer, coordinates=self.coordinates(), root='NQ',
                    start_ns=a, end_ns=b, maximum_scan_rows=100, latency_ns=250,
                    atomic_width_ns=20, native_width_ns=20, continuation=continuation,
                    retain_native_table=retain,
                    retain_trade_batch=lambda table, source: trades.append(table),
                    retain_quote_batch=lambda table, source: quotes.append(table))
                return result, native, trades, quotes
            full = run(10, 90)
            first = run(10, 50)
            second = run(50, 90, first[0]['measurement_continuation'])
            for index in (1, 2, 3):
                expected = pa.concat_tables(full[index]).combine_chunks()
                actual = pa.concat_tables(first[index] + second[index]).combine_chunks()
                # All times, original source order, integer paths and the
                # original standing quote are equal. Grid indices are local.
                if index == 1 and 'bin' in actual.schema.names:
                    expected, actual = expected.drop(['bin']), actual.drop(['bin'])
                self.assertEqual(value_digest(expected), value_digest(actual))
            quote = second[0]['instruments'][0]['atomic_windows'][0]['quote']
            self.assertEqual(quote['initial_projection']['t'], 20)
            self.assertEqual(quote['initial_projection']['economic_at'], 20)
            self.assertTrue(quote['full_pressure_transition_window_eligible'])
            a = full[0]['instruments'][0]['time_at_price']['dwell']
            b = first[0]['instruments'][0]['time_at_price']['dwell']
            c = second[0]['instruments'][0]['time_at_price']['dwell']
            self.assertEqual([r['observed_assigned_duration_ns'] for r in a],
                             [x['observed_assigned_duration_ns'] + y['observed_assigned_duration_ns'] for x, y in zip(b, c)])

    def test_gap_before_cut_remains_blocked_and_empty_owned_intervals_remain_observable(self):
        rows = [raw(0), raw(1), raw(2), raw(80), raw(81), raw(82)]
        for gap in (False, True):
            values = [dict(r) for r in rows]
            if gap:
                values[1]['flags'] = 132
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                footer = AuctionFlowDataTests().write(root, values)
                def run(a, b, continuation=None):
                    return measure_raw_window(data_root=root, index=footer, coordinates=self.coordinates(), root='NQ',
                        start_ns=a, end_ns=b, maximum_scan_rows=100, latency_ns=250,
                        atomic_width_ns=10, native_width_ns=10, continuation=continuation)
                first = run(0, 10)
                quiet = run(10, 60, first['measurement_continuation'])
                self.assertEqual(quiet['source_manifest']['physical_scan_rows'], 0)
                windows = quiet['instruments'][0]['atomic_windows']
                self.assertTrue(all(w['trade']['empty_observed_window'] for w in windows))
                self.assertTrue(all(w['quote']['full_standing_window_eligible'] == (not gap) for w in windows))
                final = run(60, 90, quiet['measurement_continuation'])
                states = final['instruments'][0]['atomic_windows']
                if gap:
                    self.assertTrue(all(not w['quote']['full_standing_window_eligible'] for w in states))
                    self.assertEqual(final['measurement_continuation']['source']['blocked'],
                                     first['measurement_continuation']['source']['blocked'])

    def test_continuation_is_bound_to_exact_coordinate_definition_and_clock_configuration(self):
        from trading_research.errors import IntegrityError
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            footer = AuctionFlowDataTests().write(root, self.rows())
            arguments = dict(data_root=root, index=footer, coordinates=self.coordinates(), root='NQ',
                             maximum_scan_rows=100, latency_ns=250, atomic_width_ns=20, native_width_ns=20)
            first = measure_raw_window(**arguments, start_ns=10, end_ns=50)
            with self.assertRaises(IntegrityError):
                measure_raw_window(**{**arguments, 'latency_ns': 0}, start_ns=50, end_ns=90,
                                   continuation=first['measurement_continuation'])
            with self.assertRaises(IntegrityError):
                measure_raw_window(**arguments, start_ns=60, end_ns=90,
                                   continuation=first['measurement_continuation'])
            other = RetainedCoordinateIndex(manifest([record(0, known=0, activation=0, expiry=1000,
                instrument=1, symbol='NQH0')]), source_version='different-retained-definition')
            with self.assertRaises(IntegrityError):
                measure_raw_window(**{**arguments, 'coordinates': other}, start_ns=50, end_ns=90,
                                   continuation=first['measurement_continuation'])

    def test_source_schedule_retains_duplicate_acquisitions_and_resolves_nonconstant_identity_groups(self):
        import pyarrow.parquet as pq
        from trading_research.data.reconcile import footer_index
        from trading_research.research.auction_flow_schedule import source_instrument_inventory, plan_source_windows
        from tests.test_auction_flow_data import DATASET
        rows = [dict(r) for r in self.rows()]
        rows[3]['instrument_id'] = 2
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            AuctionFlowDataTests().write(root, rows)
            pq.write_table(pq.read_table(root / DATASET / 'fixture.parquet'), root / DATASET / 'copy.parquet', row_group_size=3)
            index = footer_index(root, datasets=(DATASET,), max_files=2)
            protocol = {'roots': ['NQ'], 'primary_start_ns': 10, 'frozen_available_cut_ns': 90,
                'native_width_ns': 20, 'atomic_width_ns': 20, 'resources': {'maximum_source_day_scan_rows': 100}}
            ids = source_instrument_inventory(protocol, index, root, maximum_decoded_identity_rows=100)
            self.assertEqual(ids['checked_files'], 2)
            self.assertGreater(ids['decoded_identity_rows'], 0)
            self.assertTrue(all(v['instrument_ids'] == [1, 2] for v in ids['files']))
            schedule = plan_source_windows(protocol, index, instrument_inventory=ids)
            self.assertEqual(schedule['source_windows'], 2)
            self.assertEqual([v['native_instrument_cells_upper'] for v in schedule['windows']], [8, 8])
            self.assertFalse(schedule['source_overlap_aliases_applied'])
            self.assertEqual({v['source_path'] for v in schedule['windows']},
                             {f'{DATASET}/fixture.parquet', f'{DATASET}/copy.parquet'})

    def test_ownership_allocation_bound_uses_attained_flags_without_snapshot_or_future_owner_selection(self):
        import copy
        from trading_research.research.auction_flow_schedule import _window_instrument_bound
        source = {'groups': [{'group': n, 'minimum': 10 * n, 'maximum': 10 * n + 5} for n in range(4)]}
        ordinary = {'contains_proven_non_snapshot': True, 'all_rows_proven_snapshot': False}
        snapshot = {'contains_proven_non_snapshot': False, 'all_rows_proven_snapshot': True}
        identity = {'instrument_ids': [1, 2, 3], 'groups': [
            {'group': 0, 'instrument_ids': [1], 'ownership_flag_footer_evidence': ordinary},
            {'group': 1, 'instrument_ids': [2], 'ownership_flag_footer_evidence': snapshot},
            {'group': 2, 'instrument_ids': [2], 'ownership_flag_footer_evidence': ordinary},
            {'group': 3, 'instrument_ids': [3], 'ownership_flag_footer_evidence': ordinary}]}
        self.assertEqual(_window_instrument_bound(source, identity, 16, 20)[0], [1])
        self.assertEqual(_window_instrument_bound(source, identity, 20, 26)[0], [1, 2])
        self.assertEqual(_window_instrument_bound(source, identity, 26, 30)[0], [2])
        self.assertEqual(_window_instrument_bound(source, identity, 30, 36)[0], [2, 3])
        unknown = copy.deepcopy(identity)
        unknown['groups'][2]['ownership_flag_footer_evidence'] = {
            'contains_proven_non_snapshot': False, 'all_rows_proven_snapshot': False}
        self.assertEqual(_window_instrument_bound(source, unknown, 26, 30)[0], [1, 2])
        unordered = copy.deepcopy(source)
        unordered['groups'][1]['minimum'] = 3
        self.assertEqual(_window_instrument_bound(unordered, identity, 26, 30)[0], [1, 2, 3])

    def test_raw_cadence_reduction_preserves_flag_combinations_nulls_unknown_actions_and_physical_cuts(self):
        import pyarrow as pa
        from trading_research.research.auction_flow_pipeline import InstrumentWindows
        values = pa.table({'t': [1, 3, 12, 18, 22, 25, 41, 44],
            'flags': [128, 0, 4, 32, None, 128, 160, 132],
            'action': ['A', 'T', 'T', 'T', None, 'R', 'N', 'T'],
            'size': [1, 5, 0, 0, 0, 1, 0, 2]})
        names = ('raw_rows', 'gap_rows', 'unknown_action_rows', 'invalid_trade_size_rows', 'snapshot_rows', 'non_snapshot_rows')
        expected = {number: dict(zip(names, totals, strict=True)) for number, totals in (
            (0, (2, 0, 0, 0, 0, 2)), (1, (2, 1, 0, 1, 1, 1)),
            (2, (2, 0, 1, 0, 0, 1)), (4, (2, 1, 0, 0, 1, 1)))}
        for cuts in ((values,), (values.slice(0, 3), values.slice(3))):
            windows = InstrumentWindows(1, 0, 50, 10, 0, 100, 100, 10)
            for part in cuts:
                windows.raw_rows(part)
            self.assertEqual({k: dict(v) for k, v in windows.raw.items()}, expected)
            self.assertEqual((windows.first_raw, windows.last_raw), (1, 44))

    def test_full_resource_path_uses_real_source_projection_interfaces_and_literal_event_reference(self):
        rows = self.rows()
        for row in rows:
            row['t'] *= 10_000_000
        coordinates = RetainedCoordinateIndex(manifest([record(0, known=0, activation=0, expiry=10**12,
            instrument=1, symbol='NQH0')]), source_version='actual-retained-fixture')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            footer = AuctionFlowDataTests().write(root, rows)
            outputs = BoundedOutputs(root / 'output', maximum_total_bytes=4 * 1024**2, maximum_file_bytes=2 * 1024**2)
            protocol = {'resources': {'maximum_source_day_scan_rows': 100, 'maximum_native_array_bytes': 1024**2},
                        'native_width_ns': 100_000_000, 'atomic_width_ns': 200_000_000}
            unit = {'root': 'NQ', 'event_start_ns': 100_000_000, 'event_end_ns': 900_000_000,
                    'source_variant': 'fixture', 'role': 'fixture',
                    'source_path': footer['datasets']['quantpad/cme__nq-continuous-futures__mbp-1'][0]['path']}
            result, reference = measured_unit(unit, protocol=protocol, index=footer, coordinates=coordinates,
                                              outputs=outputs, data_root=root)
            self.assertEqual(result['counts']['volume'], 108)
            self.assertEqual(result['actual_reference']['raw_events'], 8)
            self.assertTrue(result['actual_reference']['passed'])
            self.assertEqual(result['native_cells'], 8)
            self.assertEqual(result['event_storage']['trades']['rows'], 3)
            self.assertEqual(result['event_storage']['quotes']['rows'], 4)
            self.assertFalse(result['family_statistics_or_model_complete'])
            self.assertTrue(Path(reference['path']).is_file())
            from trading_research.research.auction_flow_resources import source_cost_projection
            import copy
            work = result['workload_counts']
            schedule = {'instrument_allocation_bound_established': True,
                'windows': [{'native_cells_per_instrument': result['native_cells'], 'raw_instruments_per_window_upper': 1}],
                'partitions': [{'root': 'NQ', 'year': 2020, 'source_windows': 1,
                    'reader_batches_upper': result['source_manifest']['physical_reader_batches'],
                    'instrument_batches_upper': work['raw_instrument_batches'],
                    'atomic_parts_per_consumer_upper': max(work.get(k, 0) for k in ('raw_atomic_parts', 'trade_atomic_parts', 'quote_atomic_parts')),
                    'instrument_native_cells_upper': result['native_cells'], 'instrument_window_allocations_upper': 1,
                    'instrument_atomic_cells_upper': work['instrument_atomic_cells'], 'selected_raw_rows_upper': result['raw_physical_rows']}]}
            resources = {'resources': {'maximum_derived_output_bytes': 1024**2}}
            initial = source_cost_projection([result], resources, schedule, excluded_storage_reserve_bytes_per_source_year=1024)
            changed = copy.deepcopy(result)
            changed['raw_physical_rows'] *= 1000
            changed['counts']['raw_rows'] *= 1000
            changed['reference_cpu_seconds'] *= 1000000
            changed['plain_json_storage_comparator']['cpu_seconds'] *= 1000000
            later = source_cost_projection([changed], resources, schedule, excluded_storage_reserve_bytes_per_source_year=1024)
            self.assertEqual(initial['source_pipeline_cpu_allowance'], later['source_pipeline_cpu_allowance'])
            self.assertFalse(initial['full_extraction_feasibility_established'])
            changed = copy.deepcopy(result)
            changed['scan_cpu_components_disjoint']['raw_atomic_consumers'] = changed['scan_cpu_components_disjoint'].pop('raw_atomic_batch_reduction')
            with self.assertRaises(IntegrityError):
                source_cost_projection([changed], resources, schedule, excluded_storage_reserve_bytes_per_source_year=1024)

    def coordinates(self, *, inactive=False, second=False):
        rows = [record(0, known=0, activation=0, expiry=1000, instrument=1, symbol="NQH0")]
        if inactive:
            rows.append(record(1, known=50, activation=200, expiry=1000, instrument=1, symbol="NQH0"))
        if second:
            rows.append(record(2, known=0, activation=0, expiry=1000, instrument=2, symbol="NQM0"))
        return RetainedCoordinateIndex(manifest(rows), source_version="actual-retained-fixture")

    def rows(self):
        return [raw(0), raw(10, action="A"), raw(12, action="T", flags=0, size=5),
                raw(20, qb=10, qa=6), raw(25, action="T", flags=0, size=3, side="A"),
                raw(40, action="N"), raw(65, qb=8, qa=8),
                raw(70, action="T", flags=0, size=100, side="N"), raw(89, qb=9, qa=7), raw(100)]

    def run_rows(self, rows, *, index=None, start=10, end=90):
        retained, native_rows = [], {}
        def native_writer(table, metadata):
            native_rows[metadata['instrument_id']] = table.to_pylist()
            return {'fixture_rows': len(table), 'instrument_id': metadata['instrument_id']}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            footer = AuctionFlowDataTests().write(root, rows)
            result = measure_raw_window(data_root=root, index=footer, coordinates=index or self.coordinates(), root="NQ",
                start_ns=start, end_ns=end, maximum_scan_rows=100, latency_ns=250, atomic_width_ns=20,
                native_width_ns=20, retain_native_table=native_writer,
                retain_trade_batch=lambda table, source: retained.extend(table.to_pylist()))
        result['fixture_native_rows'] = native_rows
        return result, retained

    def test_complete_raw_pass_exact_cache_and_atomic_whole_reconciliation(self):
        result, retained = self.run_rows(self.rows())
        values = result["instruments"][0]
        windows = values["atomic_windows"]
        self.assertEqual([r["source_row"] for r in retained], [2, 4, 7])
        self.assertEqual([r["raw_side"] for r in retained], ["B", "A", "N"])
        self.assertEqual([w["trade"]["flows"]["all"]["volume"] for w in windows], [8, 0, 0, 100])
        self.assertEqual(values["whole_window"]["flows"]["all"]["volume"], 108)
        self.assertEqual(sum(w["quote"]["ofi_contracts"] for w in windows), 4)
        self.assertTrue(windows[1]["trade"]["empty_observed_window"])
        self.assertTrue(windows[2]["trade"]["empty_observed_window"])
        self.assertTrue(all(w["coordinate"]["complete"] for w in windows))
        self.assertEqual(result["source_manifest"]["projection"]["counts"]["raw_rows"], 8)
        self.assertFalse(windows[0]["quote"]["full_pressure_transition_window_eligible"])
        self.assertTrue(windows[1]["quote"]["full_pressure_transition_window_eligible"])
        self.assertFalse(result["statistics_or_predictive_family_complete"])
        native = result['fixture_native_rows'][1]
        self.assertEqual([r['all__volume'] for r in native], [8, 0, 0, 100])
        self.assertEqual([r['all__high'] for r in native], [5, 0, 0, 0])
        self.assertEqual([r['all__close'] for r in native], [2, 0, 0, 0])
        self.assertEqual(native[0]['all__high_at_ns'], 12)
        self.assertEqual(native[0]['all__high_source_order'], 1)
        self.assertEqual(sum(r['standing_ns'] for r in native), sum(w['quote']['observed_trusted_standing_duration_ns'] for w in windows))
        self.assertEqual([r['price_history_complete'] for r in native], [True] * 4)

    def test_known_definition_change_blocks_later_price_windows_without_rewriting_earlier_flow(self):
        original, _ = self.run_rows(self.rows())
        changed, _ = self.run_rows(self.rows(), index=self.coordinates(inactive=True))
        a, b = original["instruments"][0]["atomic_windows"], changed["instruments"][0]["atomic_windows"]
        self.assertEqual([w["coordinate"]["complete"] for w in b], [True, True, False, False])
        self.assertEqual(a[0]["trade"]["flows"], b[0]["trade"]["flows"])
        self.assertEqual(b[3]["trade"]["flows"]["all"]["volume"], 100)
        self.assertTrue(b[3]["trade"]["flow_history_complete"])
        self.assertFalse(b[3]["trade"]["price_history_complete"])
        self.assertFalse(coordinate_window(self.coordinates(inactive=True), 1, 10, 90)["complete"])
        self.assertEqual([r['coordinate_eligible'] for r in changed['fixture_native_rows'][1]], [True, True, False, False])

    def test_gap_does_not_discard_observed_trades_or_synthesize_book_recovery(self):
        rows = self.rows()
        rows[5] = raw(40, action="T", flags=132, size=2)
        result, retained = self.run_rows(rows)
        windows = result["instruments"][0]["atomic_windows"]
        self.assertFalse(windows[1]["trade"]["flow_history_complete"])
        self.assertEqual(windows[1]["trade"]["flows"]["all"]["volume"], 2)
        self.assertIn(40, [r["t"] for r in retained])
        self.assertFalse(windows[2]["quote"]["full_standing_window_eligible"])
        self.assertFalse(windows[3]["quote"]["full_standing_window_eligible"])
        # A later explicitly reset local flow window can describe its own
        # observed volume; the full original anchor remains incomplete.
        self.assertTrue(windows[2]["trade"]["flow_history_complete"])
        self.assertFalse(result["instruments"][0]["whole_window"]["flow_history_complete"])

    def test_future_prints_do_not_decide_earlier_quiet_eligibility_and_raw_rolls_are_not_zero_volume(self):
        rows = self.rows()
        rows[5] = raw(40, flags=32)
        a, _ = self.run_rows(rows)
        later = [dict(r) for r in rows]
        for r in later:
            if r["t"] >= 65:
                r["instrument_id"] = 2
        b, _ = self.run_rows(later, index=self.coordinates(second=True))
        old_a = a["instruments"][0]["atomic_windows"]
        old_b = b["instruments"][0]["atomic_windows"]
        self.assertFalse(old_a[1]["source_instrument_presence"])
        self.assertEqual(old_a[1]["source_instrument_presence"], old_b[1]["source_instrument_presence"])
        self.assertFalse(old_b[3]["trade"]["empty_observed_window"])
        self.assertFalse(old_b[3]["supplied_raw_coordinate_stable"])
        new = b["instruments"][1]["atomic_windows"]
        self.assertFalse(new[2]["trade"]["flow_history_complete"])
        self.assertTrue(new[3]["trade"]["flow_history_complete"])

    def test_missing_window_does_not_become_an_empty_observed_instrument(self):
        result, retained = self.run_rows(self.rows(), start=200, end=240)
        self.assertEqual(result["status"], "unavailable_source_window")
        self.assertEqual(result["instruments"], [])
        self.assertEqual(retained, [])

    def test_prepared_pipeline_quotes_match_frozen_reference_native_sink_and_continuation(self):
        rows = self.rows()
        quotes, native_rows = [], {}

        def keep_quote(table, source):
            quotes.append(table)

        def keep_native(table, metadata):
            native_rows[metadata["instrument_id"]] = table.to_pylist()
            return {"fixture_rows": len(table), "instrument_id": metadata["instrument_id"]}

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            footer = AuctionFlowDataTests().write(root, rows)
            result = measure_raw_window(data_root=root, index=footer, coordinates=self.coordinates(), root="NQ",
                start_ns=10, end_ns=90, maximum_scan_rows=100, latency_ns=250, atomic_width_ns=20,
                native_width_ns=20, retain_native_table=keep_native, retain_quote_batch=keep_quote)
        compare = ("quote_or_invalidation_rows", "fresh_quote_updates", "pressure_transitions",
                   "invalid_book_rows", "snapshot_rows", "gap_rows", "clear_rows",
                   "equal_time_adjacent_quote_rows", "action_side_counts", "ofi_contracts",
                   "same_price_size_ofi", "price_change_ofi", "ofi_path",
                   "sum_depth_normalized_ofi", "update_mean_imbalance", "update_positive_fraction",
                   "update_mean_microprice_minus_midpoint_ticks", "update_mean_spread_ticks",
                   "observed_trusted_standing_duration_ns", "duration_mean_imbalance",
                   "duration_positive_fraction", "duration_mean_spread_ticks",
                   "displayed_midpoint_occupancy", "initial_projection", "terminal_projection")
        frozen = replay_atomic(quotes, Window=frozen_quote_window(), start=10, end=90, width=20, delay=250,
                               native_sink=None)
        ordinary = replay_atomic(quotes, Window=QuoteWindow, start=10, end=90, width=20, delay=250)
        prepared = replay_atomic(quotes, Window=QuoteWindow, start=10, end=90, width=20, delay=250, prepared=True)
        sink = NativeEventBins(instrument_id=1, start_ns=10, end_ns=90, width_ns=20)
        replay_atomic(quotes, Window=frozen_quote_window(), start=10, end=90, width=20, delay=250, native_sink=sink)
        windows = result["instruments"][0]["atomic_windows"]
        self.assertEqual(len(windows), len(frozen))
        for index, window in enumerate(windows):
            for key in compare:
                self.assertEqual(window["quote"][key], frozen[index][key], key)
                self.assertEqual(ordinary[index][key], frozen[index][key], key)
                self.assertEqual(prepared[index][key], frozen[index][key], key)
        native = native_rows[1]
        for name in QUOTE_FIELDS:
            self.assertEqual([row[name] for row in native], [int(value) for value in sink.columns[name]], name)
        carry = result["measurement_continuation"]["instruments"]["1"]["quote"]
        self.assertEqual(carry, windows[-1]["quote"]["terminal_projection"])
        self.assertEqual(carry, frozen[len(frozen) - 1]["terminal_projection"])


if __name__ == "__main__":
    unittest.main()
