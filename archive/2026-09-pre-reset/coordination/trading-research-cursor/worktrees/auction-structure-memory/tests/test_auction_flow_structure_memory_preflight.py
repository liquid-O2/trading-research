import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import pyarrow as pa

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries, read_json_artifact
from trading_research.research.auction_flow_structure_memory_preflight import (
    AGGREGATION_UNIT, ATOMIC_WIDTH_NS, CONTRACT_KIND, LIMITATIONS, MEMORY_DEFINITIONS,
    MEMORY_GRIDS, PIVOT_LENGTHS, PIVOT_TIES, STRUCTURE_SCALAR_PROBE, SWING_THRESHOLD_TICK_PAIRS,
    VERSION, _CPU_NAMES, _fixture_local_contract, check_structure_memory_unit,
)
from trading_research.research.auction_flow_windows import TapeWindow
from tests.test_auction_flow_prepared_trades import make_trade_table, trade_row
from tests.test_auction_flow_quotes import make_quote_table, quote_row


CONTRACT_PATH = Path(__file__).resolve().parents[1] / 'validation' / 'AUCTION_FLOW_STRUCTURE_MEMORY_PROBE_CONTRACT_V1.json'
MINUTE = ATOMIC_WIDTH_NS
START = 1_000_000_000_000
END = START + 3 * MINUTE
DELAY = 250
NQ_ID = 1
ES_ID = 2
FIXTURE_GRID = (395, 425)


def production_contract():
    return json.loads(CONTRACT_PATH.read_text())


def fixture_contract():
    return _fixture_local_contract(
        production_contract(),
        memory_grid_inclusive_by_root={'NQ': FIXTURE_GRID, 'ES': FIXTURE_GRID})


def row(t, *, source_order, size=1, side=1, price=400, instrument_id=NQ_ID, source_key='src',
        delay=DELAY, raw_flags=0, price_valid=1):
    raw_side = 'B' if side == 1 else 'A' if side == -1 else 'N'
    return trade_row(t, source_order=source_order, size=size, raw_side=raw_side, delay=delay,
                     instrument_id=instrument_id, source_key=source_key, source_row=source_order,
                     price=price, raw_flags=raw_flags, price_valid=price_valid)


def excluded_row(t, *, source_order, exclusion_bits, instrument_id=NQ_ID, size=0, flags=0,
                 action='T', source_key='src', source_row=None):
    return {
        't': t, 'action': action, 'side': 'N', 'price': 0, 'size': size,
        'bid_px': 0, 'ask_px': 0, 'bid_sz': 0, 'ask_sz': 0,
        'instrument_id': instrument_id, 'flags': flags,
        'source_row': source_order if source_row is None else source_row,
        'source_order': source_order, 'exclusion_bits': exclusion_bits,
        'source_key': source_key,
    }


def make_excluded_table(rows):
    numeric = ('t', 'price', 'size', 'bid_px', 'ask_px', 'bid_sz', 'ask_sz', 'instrument_id',
               'flags', 'source_row', 'source_order', 'exclusion_bits')
    arrays = {name: pa.array([item[name] for item in rows], type=pa.int64()) for name in numeric}
    arrays['action'] = pa.array([item['action'] for item in rows])
    arrays['side'] = pa.array([item['side'] for item in rows])
    arrays['source_key'] = pa.array([item['source_key'] for item in rows])
    return pa.table(arrays)


def write_series(outputs, name, tables):
    series = ParquetSeries(outputs, name, encoding='plain')
    for table in tables:
        if len(table):
            series.append(table)
    return series.finish()


def build_measured(rows, *, start, end, delay, instrument_ids, atom_flags):
    width = MINUTE
    count = (end - start + width - 1) // width
    instruments = []
    for raw_id in instrument_ids:
        owned = [item for item in rows if item['instrument_id'] == raw_id]
        flags = atom_flags[raw_id]
        if len(flags) != count:
            raise IntegrityError('test atom flags must cover every measured one-minute bound')
        whole = TapeWindow(instrument_id=raw_id, start_ns=start, end_ns=end, latency_ns=delay)
        if owned:
            whole.add(make_trade_table(owned))
        atoms = []
        for number, (source_complete, coordinate_complete) in enumerate(flags):
            a = start + number * width
            b = min(a + width, end)
            tape = TapeWindow(instrument_id=raw_id, start_ns=a, end_ns=b, latency_ns=delay)
            part = [item for item in owned if a <= item['t'] < b]
            if part:
                tape.add(make_trade_table(part))
            atoms.append({
                'bin': number, 'event_start_ns': a, 'event_end_ns': b,
                'known_at_ns': b + delay, 'instrument_id': raw_id,
                'coordinate': {'complete': coordinate_complete, 'contract_key': f'TEST:{raw_id}'},
                'trade': tape.record(source_coverage_complete=source_complete,
                                     coordinate_complete=coordinate_complete),
            })
        source_complete = all(flag[0] for flag in flags)
        coordinate_complete = any(flag[1] for flag in flags)
        instruments.append({
            'instrument_id': raw_id,
            'coordinate': {'complete': coordinate_complete, 'contract_key': f'TEST:{raw_id}'},
            'whole_window': whole.record(source_coverage_complete=source_complete,
                                         coordinate_complete=coordinate_complete),
            'atomic_windows': atoms,
        })
    return {'root': 'NQ', 'event_start_ns': start, 'event_end_ns': end, 'known_at_ns': end + delay,
            'instruments': instruments}


def manifest_for(*, trades, quotes, excluded, delay=DELAY, start=START, end=END,
                 extra_invalid_size=0):
    return {
        'event_latency_scenario_ns': delay,
        'start_ns': start,
        'end_ns': end,
        'projection': {
            'counts': {
                'trades': len(trades),
                'volume': sum(item['size'] for item in trades),
                'quote_rows': len(quotes),
            },
        },
        'trade_exclusions': {
            'unique_excluded_trade_rows': len(excluded),
            'invalid_size_trade_rows': extra_invalid_size + sum(
                1 for item in excluded if item['exclusion_bits'] & 2),
            'snapshot_trade_rows': sum(1 for item in excluded if item['exclusion_bits'] & 1),
        },
    }


def ordinary_rows(*, instrument_id=NQ_ID, source_key='src'):
    specs = (
        (START + 1, 10, 1, 400),
        (START + 2, 100, -1, 416),
        (START + 3, 80, 1, 400),
        (START + 4, 75, -1, 408),
        (START + 5, 101, 1, 412),
        (START + 6, 1, 0, 404),
        (START + 20, 5, 1, 406),
        (START + 20, 5, -1, 406),
        (START + MINUTE + 8, 120, 1, 420),
        (START + 2 * MINUTE + 4, 30, -1, 410),
    )
    return [row(at, source_order=index, size=size, side=side, price=price,
                instrument_id=instrument_id, source_key=source_key)
            for index, (at, size, side, price) in enumerate(specs)]


class _Harness:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.storage = BoundedOutputs(self.folder / 'storage', maximum_total_bytes=64 * 1024 ** 2,
                                      maximum_file_bytes=32 * 1024 ** 2)
        self.outputs = BoundedOutputs(self.folder / 'check', maximum_total_bytes=64 * 1024 ** 2,
                                      maximum_file_bytes=32 * 1024 ** 2)
        self._names = 0

    def _name(self, label):
        self._names += 1
        return f'{label}-{self._names}'

    def run(self, *, trades, quotes=None, excluded=None, start=START, end=END, delay=DELAY,
            instrument_ids=(NQ_ID,), atom_flags=None, root='NQ', measured=None, contract=None,
            unit=None, manifest=None, trade_tables=None):
        quotes = [] if quotes is None else quotes
        excluded = [] if excluded is None else excluded
        flags = atom_flags or {raw_id: ((True, True), (True, True), (True, True))
                               for raw_id in instrument_ids}
        measured = measured or build_measured(trades, start=start, end=end, delay=delay,
                                              instrument_ids=instrument_ids, atom_flags=flags)
        if measured.get('root') is None:
            measured['root'] = root
        measured['source_manifest'] = manifest or manifest_for(
            trades=trades, quotes=quotes, excluded=excluded, delay=delay, start=start, end=end)
        tables = trade_tables
        if tables is None:
            tables = [make_trade_table(trades)] if trades else []
        trade_storage = write_series(self.storage, self._name(f'{root}-trades'), tables)
        quote_storage = write_series(
            self.storage, self._name(f'{root}-quotes'),
            [make_quote_table(quotes)] if quotes else [])
        excluded_storage = write_series(
            self.storage, self._name(f'{root}-excluded'),
            [make_excluded_table(excluded)] if excluded else [])
        measurement = self.outputs.json_compressed(
            f'{self._name(root)}-measurements.json.zst', measured,
            kind='auction_flow_full_window_measurements')
        current_unit = unit or {'root': root, 'cash_date': '2020-03-16', 'event_start_ns': start,
                                'event_end_ns': end, 'source_path': f'test/{root}/current.parquet',
                                'source_variant': 'fixture'}
        summary = check_structure_memory_unit(
            measured, current_unit, measurement_reference=measurement,
            trade_storage=trade_storage, quote_storage=quote_storage,
            excluded_storage=excluded_storage, outputs=self.outputs,
            contract=contract or fixture_contract())
        artifact = read_json_artifact(summary['reference'])
        return summary, artifact, measured


class AuctionFlowStructureMemoryPreflightTests(unittest.TestCase):
    def test_complete_data_same_time_masses_and_pivot_equality(self):
        trades = ordinary_rows()
        with TemporaryDirectory() as folder:
            summary, artifact, measured = _Harness(folder).run(trades=trades)
            self.assertTrue(summary['passed'])
            self.assertEqual(artifact['version'], VERSION)
            self.assertEqual(artifact['kind'], CONTRACT_KIND)
            self.assertEqual(artifact['publication_status'], 'unpublished')
            self.assertFalse(artifact['admitted_for_serving'])
            self.assertFalse(artifact['f09_f10_f11_serving_admitted'])
            self.assertFalse(artifact['venue_certified'])
            self.assertEqual(artifact['limitations'], list(LIMITATIONS))
            self.assertEqual(summary['swing_definitions'], len(SWING_THRESHOLD_TICK_PAIRS))
            self.assertEqual(summary['pivot_definitions'], len(PIVOT_LENGTHS) * len(PIVOT_TIES))
            self.assertEqual(summary['definitions'], len(MEMORY_DEFINITIONS))
            self.assertGreater(summary['exact_pivot_records_compared'], 0)
            self.assertGreater(summary['exact_swing_records_compared'], 0)
            self.assertGreater(summary['exact_memory_fields_compared'], 0)
            instrument = artifact['instruments'][0]
            self.assertIsNone(instrument['continuous_unavailable'])
            self.assertIsNone(instrument['first_invalid_source_address'])
            self.assertEqual(instrument['ordinary_prints'], len(trades))
            self.assertGreater(instrument['emitted_swings'], 0)
            self.assertGreater(instrument['emitted_pivots'], 0)
            originals = measured['instruments'][0]
            all_point = next(item for item in instrument['memory'] if item['version'] == 'all_point_time_box')
            self.assertFalse(all_point['failed'])
            self.assertEqual(all_point['input_prints'], len(trades))
            ge100 = next(item for item in instrument['memory'] if item['version'] == 'ge100_triangular_time')
            gt100 = next(item for item in instrument['memory'] if item['version'] == 'gt100_triangular_time')
            ge75 = next(item for item in instrument['memory'] if item['version'] == 'ge75_triangular_box')
            self.assertGreater(ge100['selected_prints'], gt100['selected_prints'])
            self.assertGreaterEqual(ge75['selected_prints'], ge100['selected_prints'])
            self.assertEqual(ge100['selected_prints'], sum(1 for item in trades if item['size'] >= 100))
            self.assertEqual(gt100['selected_prints'], sum(1 for item in trades if item['size'] > 100))
            whole = originals['whole_window']
            self.assertEqual(all_point['input_prints'], whole['prints'])
            memory_report = read_json_artifact(all_point['reference'])
            unknown = [cluster for cluster in memory_report['clusters'] if cluster['side'] == 0]
            self.assertEqual(len(unknown), 1)
            self.assertEqual(unknown[0]['raw_count'], 1)
            same_time = [cluster for cluster in memory_report['clusters']
                         if cluster['first_at'] == START + 20]
            self.assertTrue(same_time)
            self.assertEqual(instrument['structure_scalar']['selected_count'], len(trades))
            self.assertIsNone(instrument['structure_scalar']['disposition'])
            self.assertEqual(instrument['memory_scalar']['clock_view_limitation'],
                             artifact['memory_scalar_clock_reference'])
            self.assertEqual(instrument['memory_scalar']['zero_delay_event_clock_arithmetic_view']['name'],
                             'zero_delay_event_clock_arithmetic_view')
            self.assertFalse(instrument['memory_scalar']['f05_admitted'])
            swings = read_json_artifact(artifact['artifacts']['swings'])
            self.assertGreater(len(swings['instruments'][0]['emitted']), 0)
            pivots = read_json_artifact(artifact['artifacts']['pivots'])
            for item in pivots['instruments'][0]['definitions']:
                self.assertIn(item['comparison'], ('equal', 'true_negative_comparison', 'no_emissions'))
                if item['left'] == 1 and item['ties'] == 'strict':
                    self.assertGreater(len(item['emitted']), 0)
                    for record in item['emitted']:
                        self.assertEqual(record['id'], record['reference_swing']['id'])
                        self.assertEqual(record['definition_version'],
                                         record['reference_swing']['definition_version'])
            cpu = summary['cpu_components_disjoint']
            self.assertEqual(set(cpu), set(_CPU_NAMES))
            self.assertGreaterEqual(cpu['orchestration_and_report_assembly'], 0)
            self.assertAlmostEqual(sum(cpu.values()), summary['helper_cpu_seconds'], places=9)
            self.assertEqual(cpu['serialization'], summary['serialization_cpu_seconds'])
            counts = summary['workload_counts']
            self.assertEqual(counts['trade_decoded_rows'], len(trades))
            self.assertEqual(counts['prepared_prints'], len(trades))
            self.assertGreater(counts['source_rows'], 0)
            self.assertGreater(counts['bars_assembled'], 0)
            self.assertGreater(counts['serialized_artifacts'], 1)

    def test_quote_f4_between_clean_trades_does_not_rewrite_prefix(self):
        trades = [
            row(START + 1, source_order=0, price=400, size=10, side=1),
            row(START + 2, source_order=1, price=416, size=10, side=-1),
            row(START + 4, source_order=3, price=500, size=10, side=1),
        ]
        quotes = [
            quote_row(START + 1, source_order=0, raw_action='T', raw_flags=0, delay=DELAY),
            quote_row(START + 2, source_order=1, raw_action='T', raw_flags=0, delay=DELAY),
            quote_row(START + 3, source_order=2, raw_action='M', raw_flags=4, delay=DELAY,
                      book_valid=0),
            quote_row(START + 4, source_order=3, raw_action='T', raw_flags=0, delay=DELAY),
        ]
        flags = {NQ_ID: ((False, True), (True, True), (True, True))}
        with TemporaryDirectory() as folder:
            summary, artifact, _ = _Harness(folder).run(trades=trades, quotes=quotes, atom_flags=flags)
            self.assertTrue(summary['passed'])
            first = artifact['instruments'][0]['first_invalid_source_address']
            self.assertEqual(first['source_order'], 2)
            self.assertEqual(first['reason'], 'flag4')
            swings = read_json_artifact(artifact['artifacts']['swings'])
            emitted = swings['instruments'][0]['emitted']
            high16 = [item for item in emitted if item['definition_version'] == 'fixed_16_1'
                      and item['side'] == 'high']
            self.assertEqual(len(high16), 1)
            self.assertEqual(high16[0]['price_ticks'], 416)
            self.assertEqual(high16[0]['confirmation_source_order'], 1)
            self.assertEqual(high16[0]['extreme_source_order'], 1)
            self.assertFalse(any(item['confirmation_source_order'] == 3
                                 and item['definition_version'] == 'fixed_16_1' for item in emitted))
            snapshot = swings['instruments'][0]['record']
            self.assertGreater(snapshot['reason_counts']['incomplete_segment'], 0)
            self.assertGreater(snapshot['reason_counts']['priced_complete'], 0)

    def test_invalid_size_exclusion_marks_later_trades_incomplete(self):
        trades = [
            row(START + 1, source_order=0, price=400, size=10, side=1),
            row(START + 2, source_order=1, price=416, size=10, side=-1),
            row(START + 5, source_order=4, price=500, size=10, side=1),
        ]
        excluded = [
            excluded_row(START + 3, source_order=2, exclusion_bits=1, size=0, flags=32),
            excluded_row(START + 4, source_order=3, exclusion_bits=2, size=0, flags=0),
        ]
        flags = {NQ_ID: ((False, True), (True, True), (True, True))}
        with TemporaryDirectory() as folder:
            summary, artifact, _ = _Harness(folder).run(
                trades=trades, excluded=excluded, atom_flags=flags)
            self.assertTrue(summary['passed'])
            first = artifact['instruments'][0]['first_invalid_source_address']
            self.assertEqual(first['source_order'], 3)
            self.assertEqual(first['reason'], 'invalid_size_non_snapshot')
            self.assertEqual(summary['workload_counts']['snapshot_excluded_rows'], 1)
            self.assertEqual(summary['workload_counts']['invalid_size_non_snapshot_rows'], 1)
            swings = read_json_artifact(artifact['artifacts']['swings'])
            high16 = [item for item in swings['instruments'][0]['emitted']
                      if item['definition_version'] == 'fixed_16_1' and item['side'] == 'high']
            self.assertEqual(len(high16), 1)
            self.assertEqual(high16[0]['confirmation_source_order'], 1)
            self.assertFalse(any(item['confirmation_source_order'] >= 3
                                 and item['definition_version'] == 'fixed_16_1'
                                 for item in swings['instruments'][0]['emitted']))

    def test_clear_only_is_distinct_from_a_source_gap(self):
        trades = [
            row(START + 1, source_order=0, price=400, size=10, side=1),
            row(START + 2, source_order=1, price=392, size=10, side=-1),
            row(START + 4, source_order=3, price=416, size=10, side=1),
        ]
        quotes = [
            quote_row(START + 1, source_order=0, raw_action='T', delay=DELAY),
            quote_row(START + 2, source_order=1, raw_action='T', delay=DELAY),
            quote_row(START + 3, source_order=2, raw_action='R', book_valid=0, delay=DELAY),
            quote_row(START + 4, source_order=3, raw_action='T', delay=DELAY),
        ]
        with TemporaryDirectory() as folder:
            summary, artifact, _ = _Harness(folder).run(trades=trades, quotes=quotes)
            self.assertTrue(summary['passed'])
            self.assertIsNone(artifact['instruments'][0]['first_invalid_source_address'])
            self.assertEqual(summary['workload_counts']['clear_rows'], 1)
            self.assertEqual(summary['workload_counts']['flag4_rows'], 0)
            swings = read_json_artifact(artifact['artifacts']['swings'])
            low16 = [item for item in swings['instruments'][0]['emitted']
                     if item['definition_version'] == 'fixed_16_1' and item['side'] == 'low']
            self.assertEqual(len(low16), 1)
            self.assertEqual(low16[0]['confirmation_source_order'], 3)
            self.assertEqual(low16[0]['price_ticks'], 392)
            self.assertEqual(low16[0]['extreme_source_order'], 1)

    def test_empty_source_and_quiet_minute(self):
        with TemporaryDirectory() as folder:
            summary, artifact, measured = _Harness(folder).run(trades=[])
            self.assertTrue(summary['passed'])
            instrument = artifact['instruments'][0]
            self.assertEqual(instrument['ordinary_prints'], 0)
            self.assertEqual(instrument['emitted_swings'], 0)
            self.assertEqual(instrument['bars_assembled'], 3)
            self.assertEqual(instrument['structure_scalar']['disposition'], 'absent_data')
            self.assertEqual(instrument['memory_scalar']['disposition'], 'absent_data')
            self.assertTrue(all(not item['failed'] for item in instrument['memory']))
            self.assertTrue(any(item['empty_observed_window'] for item in instrument['memory']))
            self.assertTrue(measured['instruments'][0]['atomic_windows'][1]['trade']['empty_observed_window'])
            pivots = read_json_artifact(artifact['artifacts']['pivots'])
            for item in pivots['instruments'][0]['definitions']:
                self.assertEqual(item['emitted'], [])
                self.assertIn(item['comparison'], ('true_negative_comparison', 'no_emissions'))

    def test_multiple_instruments_and_source_rejection(self):
        first = ordinary_rows(instrument_id=NQ_ID)
        second = [
            row(START + 2 * MINUTE + 4, source_order=30, size=33, side=-1, price=400,
                instrument_id=ES_ID),
            row(START + 2 * MINUTE + 5, source_order=31, size=8, side=0, price=401,
                instrument_id=ES_ID),
        ]
        flags = {
            NQ_ID: ((True, True), (False, False), (True, True)),
            ES_ID: ((False, False), (True, True), (True, True)),
        }
        with TemporaryDirectory() as folder:
            summary, artifact, measured = _Harness(folder).run(
                trades=first + second, instrument_ids=(NQ_ID, ES_ID), atom_flags=flags)
            self.assertEqual(summary['instruments'], 2)
            self.assertEqual([item['instrument_id'] for item in artifact['instruments']],
                             [NQ_ID, ES_ID])
            for report, original in zip(artifact['instruments'], measured['instruments'], strict=True):
                self.assertEqual(report['coordinate']['complete'], original['coordinate']['complete'])
                self.assertEqual(report['ordinary_prints'], original['whole_window']['prints'])
                self.assertEqual(report['bars_assembled'], 3)
        mixed = ordinary_rows()
        mixed[3] = row(mixed[3]['t'], source_order=mixed[3]['source_order'], size=mixed[3]['size'],
                       side=-1, price=mixed[3]['price'], source_key='other')
        with TemporaryDirectory() as folder:
            with self.assertRaises(IntegrityError):
                _Harness(folder).run(trades=mixed)

    def test_wrong_clocks_contract_schema_and_row_totals(self):
        trades = ordinary_rows()
        with TemporaryDirectory() as folder:
            harness = _Harness(folder)
            broken = [dict(item) for item in trades]
            broken[0]['known_at_ns'] = broken[0]['t'] + DELAY + 1
            with self.assertRaises(IntegrityError):
                harness.run(trades=broken)
        with TemporaryDirectory() as folder:
            harness = _Harness(folder)
            contract = fixture_contract()
            contract['kind'] = 'not-the-registered-contract'
            with self.assertRaises(ContractError):
                harness.run(trades=trades, contract=contract)
            contract = production_contract()
            contract['memory_grid_inclusive_by_root'] = {'NQ': [1, 2], 'ES': [3, 4]}
            with self.assertRaises(ContractError):
                harness.run(trades=trades, contract=contract)
            contract = fixture_contract()
            contract['swing_threshold_tick_pairs'] = [[4, 1], [8, 1], [16, 1], [32, 1], [6, 2]]
            with self.assertRaises(ContractError):
                harness.run(trades=trades, contract=contract)
        with TemporaryDirectory() as folder:
            harness = _Harness(folder)
            tables = [make_trade_table(trades)]
            tables[0] = tables[0].drop(['raw_action'])
            with self.assertRaises(IntegrityError):
                harness.run(trades=trades, trade_tables=tables)
        with TemporaryDirectory() as folder:
            harness = _Harness(folder)
            payload = manifest_for(trades=trades, quotes=[], excluded=[])
            payload['projection']['counts']['trades'] = len(trades) + 1
            with self.assertRaises(IntegrityError):
                harness.run(trades=trades, manifest=payload)
            payload = manifest_for(trades=trades, quotes=[], excluded=[])
            payload['projection']['counts']['volume'] = 1
            with self.assertRaises(IntegrityError):
                _Harness(Path(folder) / 'volume').run(trades=trades, manifest=payload)

    def test_structural_coordinate_unavailability_still_consumes_rows(self):
        trades = [
            row(START + 1, source_order=0, price=400, size=10, side=1),
            row(START + 2, source_order=1, price=416, size=10, side=-1),
        ]
        flags = {NQ_ID: ((True, False), (True, False), (True, False))}
        with TemporaryDirectory() as folder:
            summary, artifact, _ = _Harness(folder).run(trades=trades, atom_flags=flags)
            self.assertTrue(summary['passed'])
            instrument = artifact['instruments'][0]
            self.assertEqual(instrument['continuous_unavailable'],
                             'unavailable_structural_source_ownership_or_coordinate')
            self.assertEqual(instrument['ordinary_prints'], 2)
            self.assertEqual(instrument['emitted_swings'], 0)
            self.assertEqual(instrument['bars_assembled'], 3)
            swings = read_json_artifact(artifact['artifacts']['swings'])
            self.assertEqual(swings['instruments'][0]['record']['reason_counts']['incomplete_segment'], 2)

    def test_scalar_same_time_trim_keeps_full_main_paths(self):
        tied = [row(START + 1, source_order=index, price=400 + (index % 3), size=2, side=1)
                for index in range(STRUCTURE_SCALAR_PROBE)]
        later = [row(START + MINUTE + 4, source_order=6000, price=420, size=6, side=-1)]
        current = tied + later
        with TemporaryDirectory() as folder:
            summary, artifact, _ = _Harness(folder).run(trades=current)
            self.assertTrue(summary['passed'])
            instrument = artifact['instruments'][0]
            self.assertEqual(instrument['ordinary_prints'], len(current))
            self.assertEqual(instrument['bars_assembled'], 3)
            self.assertEqual(instrument['structure_scalar']['selected_count'], 0)
            self.assertTrue(instrument['structure_scalar']['truncated_final_timestamp_group'])
            self.assertEqual(instrument['structure_scalar']['disposition'],
                             'unavailable_empty_scalar_prefix_after_timestamp_group_trim')
            self.assertEqual(instrument['memory_scalar']['disposition'],
                             'unavailable_empty_scalar_prefix_after_timestamp_group_trim')
            self.assertEqual(instrument['memory'][0]['input_prints'], len(current))

    def test_production_contract_shape_empty_unit(self):
        contract = production_contract()
        self.assertEqual(contract['kind'], CONTRACT_KIND)
        self.assertEqual(contract['aggregation_unit'], AGGREGATION_UNIT)
        self.assertEqual(tuple(tuple(item) for item in contract['swing_threshold_tick_pairs']),
                         SWING_THRESHOLD_TICK_PAIRS)
        self.assertEqual([item['version'] for item in contract['memory_definitions']],
                         [item['version'] for item in MEMORY_DEFINITIONS])
        with TemporaryDirectory() as folder:
            summary, artifact, _ = _Harness(folder).run(trades=[], contract=contract, root='NQ')
            self.assertTrue(summary['passed'])
            self.assertEqual(artifact['memory_grid_inclusive'], list(MEMORY_GRIDS['NQ']))
            self.assertEqual(artifact['memory_grid_cell_count'],
                             MEMORY_GRIDS['NQ'][1] - MEMORY_GRIDS['NQ'][0] + 1)
            self.assertEqual(len(artifact['memory_definitions']), 5)
            self.assertEqual(len(artifact['swing_definitions']), 5)
            self.assertEqual(len(artifact['pivot_definitions']), 8)
            self.assertFalse(artifact['family_statistics_complete'])
            self.assertFalse(artifact['annual_or_model_workload_projection_complete'])
            self.assertEqual(artifact['instruments'][0]['memory'][0]['clusters'], 0)

    def test_fixture_helper_does_not_weaken_public_grids(self):
        contract = fixture_contract()
        self.assertEqual(tuple(contract['memory_grid_inclusive_by_root']['NQ']), MEMORY_GRIDS['NQ'])
        self.assertEqual(tuple(contract['memory_grid_inclusive_by_root']['ES']), MEMORY_GRIDS['ES'])
        self.assertEqual(contract['_fixture_local_memory_grid_inclusive_by_root']['NQ'], FIXTURE_GRID)
        with self.assertRaises(ContractError):
            _fixture_local_contract(production_contract(), memory_grid_inclusive_by_root={'NQ': (1, 2)})

    def test_limits_finalization_cleanup_and_closed_cpu(self):
        trades = ordinary_rows()
        with TemporaryDirectory() as folder:
            summary, _, _ = _Harness(folder).run(trades=trades)
            cpu = summary['cpu_components_disjoint']
            self.assertGreaterEqual(cpu['orchestration_and_report_assembly'], 0)
            self.assertGreaterEqual(cpu['release'], 0)
            self.assertEqual(cpu['serialization'], summary['serialization_cpu_seconds'])
            self.assertAlmostEqual(sum(cpu.values()), summary['helper_cpu_seconds'], places=9)
            self.assertGreater(summary['helper_cpu_seconds'], cpu['serialization'])
            self.assertGreater(summary['helper_wall_seconds'], 0)
            self.assertFalse(summary['annual_or_model_workload_projection_complete'])
            self.assertEqual(summary['limitations'], LIMITATIONS)
        with TemporaryDirectory() as folder:
            harness = _Harness(folder)
            with self.assertRaises(IntegrityError):
                harness.run(trades=trades, unit={'root': 'NQ', 'event_start_ns': START,
                                                 'event_end_ns': END + MINUTE,
                                                 'source_variant': 'fixture'})
            summary, _, _ = harness.run(trades=trades)
            self.assertTrue(summary['passed'])
            self.assertGreaterEqual(summary['cpu_components_disjoint']['release'], 0)
            self.assertGreater(summary['output_bytes'], 0)
