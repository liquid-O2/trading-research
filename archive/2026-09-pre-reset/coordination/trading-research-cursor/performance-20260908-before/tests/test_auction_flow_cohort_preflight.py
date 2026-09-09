from fractions import Fraction
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_cohort_preflight import (
    ADAPTIVE_RECIPES, CONTRACT_KIND, FIXED_FILTERS, PREFIX_LIMIT, PREFIX_PROBE, SOFT_KNOTS,
    VERSION, check_cohort_unit,
)
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries, read_json_artifact
from tests.test_auction_flow_prepared_trades import (
    FROZEN_MANIFEST, FROZEN_MEASUREMENTS, FROZEN_WINDOWS, make_trade_table, trade_row,
)


if FROZEN_WINDOWS is None or FROZEN_MEASUREMENTS is None or FROZEN_MANIFEST is None:
    raise IntegrityError('frozen auction-flow test reference is required')

CONTRACT_PATH = Path(__file__).resolve().parents[1] / 'validation' / 'AUCTION_FLOW_SOURCE_CHECK_EXTENSION_V4.json'
MINUTE = 60_000_000_000
START = 1_000_000_000_000
END = START + 3 * MINUTE
DELAY = 250
NQ_ID = 1
ES_ID = 2


def exact(value):
    if type(value) is dict and '$fraction' in value:
        return Fraction(*value['$fraction'])
    if type(value) is list:
        return [exact(item) for item in value]
    if type(value) is dict:
        return {key: exact(item) for key, item in value.items()}
    return value


def decode_atoms(block):
    bar_fields = tuple(block['schema']['bar'])
    channel_fields = tuple(block['schema']['channel'])
    bars = []
    for row, channels in zip(block['bars'], block['channels'], strict=True):
        bar = exact(dict(zip(bar_fields, row, strict=True)))
        bar['channels'] = [exact(dict(zip(channel_fields, channel, strict=True))) for channel in channels]
        bars.append(bar)
    return bars


def production_contract():
    return json.loads(CONTRACT_PATH.read_text())['cohort_validation']


def row(t, *, source_order, size=1, side=1, instrument_id=NQ_ID, source_key='src', delay=DELAY):
    raw_side = 'B' if side == 1 else 'A' if side == -1 else 'N'
    return trade_row(t, source_order=source_order, size=size, raw_side=raw_side, delay=delay,
                     instrument_id=instrument_id, source_key=source_key, source_row=source_order)


def write_series(outputs, name, tables):
    series = ParquetSeries(outputs, name, encoding='plain')
    for table in tables:
        if len(table):
            series.append(table)
    return series.finish()


def build_measured(rows, *, start, end, delay, instrument_ids, atom_flags):
    window = FROZEN_WINDOWS.TapeWindow
    width = MINUTE
    count = (end - start + width - 1) // width
    instruments = []
    for raw_id in instrument_ids:
        owned = [item for item in rows if item['instrument_id'] == raw_id]
        flags = atom_flags[raw_id]
        if len(flags) != count:
            raise IntegrityError('test atom flags must cover every measured one-minute bound')
        whole = window(instrument_id=raw_id, start_ns=start, end_ns=end, latency_ns=delay)
        if owned:
            whole.add(make_trade_table(owned))
        atoms = []
        for number, (source_complete, coordinate_complete) in enumerate(flags):
            a = start + number * width
            b = min(a + width, end)
            tape = window(instrument_id=raw_id, start_ns=a, end_ns=b, latency_ns=delay)
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
        coordinate_complete = all(flag[1] for flag in flags)
        instruments.append({
            'instrument_id': raw_id,
            'coordinate': {'complete': coordinate_complete, 'contract_key': f'TEST:{raw_id}'},
            'whole_window': whole.record(source_coverage_complete=source_complete,
                                         coordinate_complete=coordinate_complete),
            'atomic_windows': atoms,
        })
    return {'event_start_ns': start, 'event_end_ns': end, 'known_at_ns': end + delay,
            'instruments': instruments}


def write_training(directory, *, root, rows, start, end, delay, instrument_id, complete=True,
                   source_complete=True, atom_flags=None, mutate_measured=None, mutate_payload=None):
    outputs = BoundedOutputs(Path(directory) / f'{root}-train', maximum_total_bytes=8 * 1024**2,
                             maximum_file_bytes=4 * 1024**2)
    storage = write_series(outputs, f'{root}-train-trades', [make_trade_table(rows)] if rows else [])
    flags = atom_flags or {instrument_id: ((True, True), (True, True), (True, True))}
    measured = build_measured(rows, start=start, end=end, delay=delay, instrument_ids=(instrument_id,),
                              atom_flags=flags)
    quality_complete = complete
    if not complete:
        measured['instruments'][0]['coordinate']['complete'] = False
    if not source_complete:
        measured['instruments'][0]['whole_window']['source_coverage_complete'] = False
        measured['instruments'][0]['whole_window']['flow_history_complete'] = False
    if mutate_measured is not None:
        mutate_measured(measured)
    measurement = outputs.json_compressed(f'{root}-train-measurements.json.zst', measured,
                                          kind='auction_flow_full_window_measurements')
    payload = {
        'unit': {'root': root, 'cash_date': '2020-03-16', 'event_start_ns': start, 'event_end_ns': end,
                 'source_path': f'test/{root}/2020-03-16.parquet', 'source_variant': 'train'},
        'measurement': measurement,
        'event_storage': {'trades': storage},
        'instrument_quality': [{
            'instrument_id': instrument_id,
            'coordinate': {'complete': quality_complete, 'contract_key': f'TEST:{instrument_id}'},
            'whole_flow_complete': source_complete and quality_complete,
        }],
        'source_manifest': {'event_latency_scenario_ns': delay},
    }
    if mutate_payload is not None:
        mutate_payload(payload)
    return outputs.json(f'{root}-resource-unit.json', payload, kind='auction_flow_source_resource_unit')


def ordinary_rows(*, instrument_id=NQ_ID, source_key='src'):
    specs = (
        (START + 1, 10, 1),
        (START + 2, 20, -1),
        (START + 3, 10, 1),
        (START + 4, 29, 1),
        (START + 5, 30, 1),
        (START + 6, 60, -1),
        (START + 7, 61, 1),
        (START + 8, 74, 1),
        (START + 9, 75, -1),
        (START + 10, 99, 1),
        (START + 11, 100, 1),
        (START + 12, 1, 0),
        (START + 13, 15, 1),
        (START + 14, 45, -1),
        (START + 15, 80, 1),
        (START + 16, 120, 1),
        (START + 20, 5, 1),
        (START + 20, 5, -1),
    )
    return [row(at, source_order=index, size=size, side=side, instrument_id=instrument_id,
                source_key=source_key) for index, (at, size, side) in enumerate(specs)]


class _Harness:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.storage = BoundedOutputs(self.folder / 'storage', maximum_total_bytes=16 * 1024**2,
                                      maximum_file_bytes=8 * 1024**2)
        self.outputs = BoundedOutputs(self.folder / 'check', maximum_total_bytes=16 * 1024**2,
                                      maximum_file_bytes=8 * 1024**2)

    def contract(self, nq_ref, es_ref):
        payload = production_contract()
        payload['training_resource_units'] = {'NQ': nq_ref, 'ES': es_ref}
        return payload

    def run(self, *, current_rows, nq_rows, es_rows=None, start=START, end=END, delay=DELAY,
            instrument_ids=(NQ_ID,), atom_flags=None, root='NQ', nq_complete=True,
            nq_source_complete=True, current_tables=None, measured=None, nq_ref=None, es_ref=None,
            unit=None):
        es_rows = es_rows if es_rows is not None else [row(start + 3, source_order=0, size=7,
                                                           instrument_id=ES_ID)]
        nq_ref = nq_ref or write_training(self.folder / 'nq', root='NQ', rows=nq_rows, start=start,
                                          end=end, delay=delay, instrument_id=NQ_ID,
                                          complete=nq_complete, source_complete=nq_source_complete)
        es_ref = es_ref or write_training(self.folder / 'es', root='ES', rows=es_rows, start=start,
                                          end=end, delay=delay, instrument_id=ES_ID)
        flags = atom_flags or {raw_id: ((True, True), (True, True), (True, True)) for raw_id in instrument_ids}
        measured = measured or build_measured(current_rows, start=start, end=end, delay=delay,
                                              instrument_ids=instrument_ids, atom_flags=flags)
        tables = current_tables
        if tables is None:
            tables = [make_trade_table(current_rows)] if current_rows else []
        trades = write_series(self.storage, f'{root}-current-trades', tables)
        measurement = self.outputs.json_compressed(
            f'{root}-current-measurements.json.zst', measured, kind='auction_flow_full_window_measurements')
        current_unit = unit or {'root': root, 'cash_date': '2020-03-16', 'event_start_ns': start,
                                'event_end_ns': end, 'source_path': f'test/{root}/current.parquet',
                                'source_variant': 'fixture'}
        summary = check_cohort_unit(measured, current_unit, measurement_reference=measurement,
                                    trade_storage=trades, outputs=self.outputs,
                                    contract=self.contract(nq_ref, es_ref))
        artifact = exact(read_json_artifact(summary['reference']))
        return summary, artifact, measured


class AuctionFlowCohortPreflightTests(unittest.TestCase):
    def test_ordinary_signed_unknown_empty_minutes_and_reference_equality(self):
        rows = ordinary_rows()
        flags = {NQ_ID: ((True, True), (True, True), (False, True))}
        with TemporaryDirectory() as folder:
            summary, artifact, measured = _Harness(folder).run(
                current_rows=rows, nq_rows=rows, atom_flags=flags)
            self.assertTrue(summary['passed'])
            self.assertEqual(summary['definitions'], 8)
            self.assertEqual(summary['instruments'], 1)
            self.assertGreater(summary['exact_original_source_fields_compared'], 0)
            self.assertGreater(summary['exact_original_source_channels_compared'], 0)
            self.assertGreater(summary['exact_original_source_fields_compared'],
                               summary['exact_original_source_channels_compared'])
            self.assertEqual(summary['training_prefix_prints'], len(rows))
            self.assertEqual(artifact['version'], VERSION)
            self.assertEqual(artifact['publication_status'], 'unpublished')
            self.assertFalse(artifact['admitted_for_serving'])
            self.assertEqual(artifact['training']['member']['selected_count'], len(rows))
            self.assertIsNone(artifact['training']['unavailable'])
            instrument = artifact['instruments'][0]
            self.assertEqual(len(instrument['definitions']), 8)
            names = [item['name'] for item in instrument['definitions']]
            self.assertEqual(names, [*FIXED_FILTERS, 'soft_benchmark_knots',
                                     *(name for name, _, _ in ADAPTIVE_RECIPES)])
            original = measured['instruments'][0]
            for item in instrument['definitions']:
                if item['kind'] == 'fixed_source':
                    atoms = decode_atoms(item['atomic'])
                    self.assertEqual(len(atoms), 3)
                    self.assertEqual([bar['bin'] for bar in atoms], [0, 1, 2])
                    self.assertTrue(atoms[1]['empty_observed_window'])
                    self.assertFalse(atoms[2]['empty_observed_window'])
                    self.assertFalse(atoms[2]['source_coverage_complete'])
                    included = next(channel for channel in item['whole']['channels']
                                    if channel['role'] == 'included')
                    flow = original['whole_window']['flows'][item['name']]
                    self.assertEqual(included['close'], flow['close'])
                    self.assertEqual(included['high'], flow['high'])
                    self.assertEqual(included['low'], flow['low'])
                    self.assertEqual(included['high_at_ns'], flow['high_at_ns'])
                    self.assertEqual(included['low_source_order'], flow['low_source_order'])
                    self.assertEqual(included['buy'], flow['buy'])
                    self.assertEqual(included['unknown'], flow['unknown'])
                    if item['name'] == 'all':
                        self.assertNotEqual(included['high'], included['low'])
                        self.assertGreater(included['high'], 0)
                        self.assertLess(included['low'], 0)
                else:
                    atoms = decode_atoms(item['atomic'])
                    self.assertGreaterEqual(item['supported_start_ns'],
                                            artifact['training']['fits'][item['name']]['available_at']
                                            if item['kind'] == 'adaptive' else START)
                    self.assertEqual(sum(bar['prints'] for bar in atoms), item['whole']['prints'])
                    self.assertEqual(len(item['atomic']['schema']['bar']), len(item['atomic']['bars'][0]))
                    self.assertEqual(len(item['atomic']['schema']['channel']),
                                     len(item['atomic']['channels'][0][0]))
            counts = summary['workload_counts']
            self.assertGreaterEqual(counts['decoded_rows'], len(rows))
            self.assertGreater(counts['prepared_prints'], 0)
            self.assertGreater(counts['report_bars'], 8)
            self.assertGreater(counts['report_channels'], 0)
            self.assertGreater(counts['serialized_bytes'], 0)
            cpu = summary['cpu_components_disjoint']
            self.assertEqual(set(cpu), {
                'training_cache_validation_and_selection',
                'histogram_accumulation_fit_and_reference_arithmetic',
                'current_cache_decoding', 'preparation_and_filtering', 'whole_path_updates',
                'atomic_path_updates', 'whole_atomic_finalization', 'original_source_comparisons',
                'full_atom_composition', 'bounded_scalar_reference', 'serialization',
                'orchestration_and_report_assembly'})
            self.assertGreaterEqual(cpu['orchestration_and_report_assembly'], 0)
            self.assertEqual(cpu['serialization'], summary['serialization_cpu_seconds'])
            self.assertAlmostEqual(sum(cpu.values()), summary['helper_cpu_seconds'], places=9)
            self.assertGreaterEqual(counts['training_decoded_rows'], 0)
            self.assertGreaterEqual(counts['current_decoded_rows'], len(rows))
            self.assertEqual(counts['decoded_rows'],
                             counts['training_decoded_rows'] + counts['current_decoded_rows'])
            all_flow = next(item for item in instrument['definitions'] if item['name'] == 'all')
            self.assertEqual(all_flow['scalar_reference']['selected_count'], len(rows))
            self.assertFalse(all_flow['scalar_reference']['truncated_final_timestamp_group'])
            self.assertIsNone(all_flow['scalar_reference']['disposition'])

    def test_reader_cuts_same_time_ties_and_cutoff_neighbors(self):
        rows = ordinary_rows()
        first = make_trade_table(rows[:17])
        second = make_trade_table(rows[17:])
        self.assertEqual(rows[16]['t'], rows[17]['t'])
        flags = {NQ_ID: ((True, True), (True, True), (True, True))}
        with TemporaryDirectory() as folder:
            summary, artifact, measured = _Harness(folder).run(
                current_rows=rows, nq_rows=rows, current_tables=(first, second), atom_flags=flags)
            self.assertTrue(summary['passed'])
            whole = next(item for item in artifact['instruments'][0]['definitions'] if item['name'] == 'all')
            included = whole['whole']['channels'][0]
            flow = measured['instruments'][0]['whole_window']['flows']['all']
            self.assertEqual(included['high_source_order'], flow['high_source_order'])
            self.assertEqual(included['low_source_order'], flow['low_source_order'])
            ge100 = next(item for item in artifact['instruments'][0]['definitions'] if item['name'] == 'ny_ge100')
            included = next(channel for channel in ge100['whole']['channels'] if channel['role'] == 'included')
            self.assertEqual(included['volume'], 220)
            mid = next(item for item in artifact['instruments'][0]['definitions']
                       if item['name'] == 'inclusive30_through60')
            included = next(channel for channel in mid['whole']['channels'] if channel['role'] == 'included')
            self.assertEqual(included['volume'], 135)
            soft = next(item for item in artifact['instruments'][0]['definitions']
                        if item['name'] == 'soft_benchmark_knots')
            self.assertEqual(len(soft['whole']['channels']), len(SOFT_KNOTS))
            self.assertEqual(sum((channel['volume'] for channel in soft['whole']['channels']), Fraction(0)),
                             soft['whole']['volume'])

    def test_training_group_truncation_and_quantile_ties(self):
        early = [row(START + 1, source_order=index, size=1 + (index % 4), side=1 if index % 2 else -1)
                 for index in range(4095)]
        tied = [row(START + 2, source_order=4095 + index, size=8, side=1) for index in range(10)]
        training = early + tied
        later = [row(START + MINUTE + 10, source_order=5000, size=50, side=-1)]
        current = training + later
        flags = {NQ_ID: ((True, True), (True, True), (True, True))}
        with TemporaryDirectory() as folder:
            summary, artifact, _ = _Harness(folder).run(
                current_rows=current, nq_rows=training, atom_flags=flags)
            self.assertTrue(summary['passed'])
            self.assertEqual(artifact['training']['member']['selected_count'], 4095)
            self.assertEqual(artifact['training']['eligible_prints_seen'], 4105)
            self.assertFalse(artifact['training']['entire_unit_at_or_under_prefix_limit'])
            fits = artifact['training']['fits']
            self.assertEqual(set(fits), {name for name, _, _ in ADAPTIVE_RECIPES})
            sizes = [item['size'] for item in early]
            total_count = len(sizes)
            total_volume = sum(sizes)
            count_thresholds = fits['count_quartiles']['requested_thresholds']
            self.assertEqual(count_thresholds, fits['count_quartiles']['literal_requested_thresholds'])
            self.assertEqual(sum(fits['count_quartiles']['realized_count']), total_count)
            self.assertEqual(sum(fits['volume_quartiles']['realized_volume']), total_volume)
            self.assertEqual(fits['source_top35_count_quantile']['requested_thresholds'],
                             fits['source_top35_count_quantile']['literal_requested_thresholds'])
            occupancy = fits['source_top35_count_quantile']['realized_count_occupancy']
            self.assertEqual(len(occupancy), 2)
            self.assertEqual(sum(occupancy), 1)
            adaptive = next(item for item in artifact['instruments'][0]['definitions']
                            if item['name'] == 'count_quartiles')
            self.assertGreaterEqual(adaptive['supported_start_ns'], fits['count_quartiles']['available_at'])
            atoms = decode_atoms(adaptive['atomic'])
            self.assertEqual(sum(bar['prints'] for bar in atoms), 1)
            self.assertTrue(any(bar['clipped'] for bar in atoms) or adaptive['atomic_unavailable'])
            fixed = next(item for item in artifact['instruments'][0]['definitions'] if item['name'] == 'all')
            self.assertEqual(fixed['whole']['prints'], len(current))
            self.assertEqual(len(decode_atoms(fixed['atomic'])), 3)
            self.assertEqual(fixed['scalar_reference']['selected_count'], 4095)
            self.assertTrue(fixed['scalar_reference']['truncated_final_timestamp_group'])
            self.assertIsNone(fixed['scalar_reference']['disposition'])
            self.assertEqual(artifact['training']['member']['truncated_final_timestamp_group'], True)

    def test_adaptive_suffix_starts_at_availability_including_partial_first_minute(self):
        training = [row(START + 1 + index, source_order=index, size=4 + index, side=1 if index % 2 else -1)
                    for index in range(6)]
        training.append(row(START + MINUTE - 1, source_order=6, size=9, side=1))
        suffix = [
            row(START + MINUTE + DELAY + 5, source_order=7, size=40, side=-1),
            row(START + 2 * MINUTE + 8, source_order=8, size=12, side=1),
        ]
        current = training + suffix
        flags = {NQ_ID: ((True, True), (True, True), (True, True))}
        with TemporaryDirectory() as folder:
            _, artifact, _ = _Harness(folder).run(
                current_rows=current, nq_rows=training, atom_flags=flags)
            available = artifact['training']['fits']['count_quartiles']['available_at']
            self.assertEqual(available, (START + MINUTE - 1) + 1 + DELAY)
            adaptive = next(item for item in artifact['instruments'][0]['definitions']
                            if item['name'] == 'count_quartiles')
            self.assertEqual(adaptive['supported_start_ns'], available)
            self.assertEqual(adaptive['atomic_unavailable'][0]['disposition'],
                             'unavailable_before_training_availability')
            self.assertEqual(adaptive['atomic_unavailable'][0]['bin'], 0)
            atoms = decode_atoms(adaptive['atomic'])
            self.assertEqual([bar['bin'] for bar in atoms], [1, 2])
            self.assertTrue(atoms[0]['clipped'])
            self.assertEqual(atoms[0]['supported_start_ns'], available)
            self.assertEqual(sum(bar['prints'] for bar in atoms), 2)
            self.assertEqual(adaptive['whole']['prints'], 2)
            self.assertEqual(adaptive['whole']['event_start_ns'], available)
            fixed = next(item for item in artifact['instruments'][0]['definitions'] if item['name'] == 'all')
            self.assertEqual(fixed['whole']['prints'], len(current))
            self.assertEqual(fixed['supported_start_ns'], START)

    def test_two_raw_instruments_with_local_coverage(self):
        first = ordinary_rows(instrument_id=NQ_ID)
        second = [
            row(START + 2 * MINUTE + 4, source_order=30, size=33, side=-1, instrument_id=ES_ID),
            row(START + 2 * MINUTE + 5, source_order=31, size=8, side=0, instrument_id=ES_ID),
        ]
        flags = {
            NQ_ID: ((True, True), (False, False), (True, True)),
            ES_ID: ((False, False), (True, True), (True, True)),
        }
        with TemporaryDirectory() as folder:
            summary, artifact, measured = _Harness(folder).run(
                current_rows=first + second, nq_rows=first, instrument_ids=(NQ_ID, ES_ID),
                atom_flags=flags)
            self.assertEqual(summary['instruments'], 2)
            self.assertEqual([item['instrument_id'] for item in artifact['instruments']], [NQ_ID, ES_ID])
            for report, original in zip(artifact['instruments'], measured['instruments'], strict=True):
                self.assertEqual(report['coordinate']['complete'], original['coordinate']['complete'])
                all_flow = next(item for item in report['definitions'] if item['name'] == 'all')
                atoms = decode_atoms(all_flow['atomic'])
                self.assertEqual(len(atoms), 3)
                self.assertEqual(all_flow['whole']['prints'], original['whole_window']['prints'])
                self.assertEqual([bar['prints'] for bar in atoms],
                                 [atom['trade']['prints'] for atom in original['atomic_windows']])

    def test_rejects_changed_training_root_hash_and_size(self):
        rows = ordinary_rows()
        with TemporaryDirectory() as folder:
            harness = _Harness(folder)
            nq_ref = write_training(folder + '/nq', root='NQ', rows=rows, start=START, end=END,
                                    delay=DELAY, instrument_id=NQ_ID)
            es_ref = write_training(folder + '/es', root='ES', rows=[row(START + 3, source_order=0, size=7,
                                                                        instrument_id=ES_ID)],
                                    start=START, end=END, delay=DELAY, instrument_id=ES_ID)
            measured = build_measured(rows, start=START, end=END, delay=DELAY, instrument_ids=(NQ_ID,),
                                      atom_flags={NQ_ID: ((True, True), (True, True), (True, True))})
            trades = write_series(harness.storage, 'NQ-current-trades', [make_trade_table(rows)])
            measurement = harness.outputs.json_compressed('NQ-current-measurements.json.zst', measured,
                                                          kind='auction_flow_full_window_measurements')
            unit = {'root': 'NQ', 'cash_date': '2020-03-16', 'event_start_ns': START,
                    'event_end_ns': END, 'source_path': 'test/NQ/current.parquet',
                    'source_variant': 'fixture'}
            with self.assertRaises(IntegrityError):
                check_cohort_unit(measured, unit, measurement_reference=measurement,
                                  trade_storage=trades, outputs=harness.outputs,
                                  contract=harness.contract(es_ref, es_ref))
            broken_hash = dict(nq_ref)
            broken_hash['sha256'] = '0' * 64
            with self.assertRaises(IntegrityError):
                check_cohort_unit(measured, unit, measurement_reference=measurement,
                                  trade_storage=trades, outputs=harness.outputs,
                                  contract=harness.contract(broken_hash, es_ref))
            broken_size = dict(nq_ref)
            broken_size['size_bytes'] = nq_ref['size_bytes'] + 1
            with self.assertRaises(IntegrityError):
                check_cohort_unit(measured, unit, measurement_reference=measurement,
                                  trade_storage=trades, outputs=harness.outputs,
                                  contract=harness.contract(broken_size, es_ref))

    def test_rejects_incompatible_source_key(self):
        rows = ordinary_rows()
        rows[5] = row(rows[5]['t'], source_order=rows[5]['source_order'], size=rows[5]['size'],
                      side=1 if rows[5]['side'] == 1 else -1 if rows[5]['side'] == -1 else 0,
                      source_key='other')
        with TemporaryDirectory() as folder:
            with self.assertRaises(IntegrityError):
                _Harness(folder).run(current_rows=rows, nq_rows=ordinary_rows())

    def test_rejects_incomplete_training(self):
        rows = ordinary_rows()
        with TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaises(IntegrityError):
                _Harness(root / 'incomplete-coordinate').run(
                    current_rows=rows, nq_rows=rows, nq_complete=False)
            with self.assertRaises(IntegrityError):
                _Harness(root / 'incomplete-source').run(
                    current_rows=rows, nq_rows=rows, nq_source_complete=False)

    def test_rejects_tampered_expected_measurement(self):
        rows = ordinary_rows()
        flags = {NQ_ID: ((True, True), (True, True), (True, True))}
        measured = build_measured(rows, start=START, end=END, delay=DELAY, instrument_ids=(NQ_ID,),
                                  atom_flags=flags)
        measured['instruments'][0]['whole_window']['flows']['all']['close'] += 1
        with TemporaryDirectory() as folder:
            with self.assertRaises(IntegrityError):
                _Harness(folder).run(current_rows=rows, nq_rows=rows, measured=measured, atom_flags=flags)

    def test_rejects_changed_contract_kind_filters_and_recipes(self):
        rows = ordinary_rows()
        with TemporaryDirectory() as folder:
            harness = _Harness(folder)
            nq_ref = write_training(folder + '/nq', root='NQ', rows=rows, start=START, end=END,
                                    delay=DELAY, instrument_id=NQ_ID)
            es_ref = write_training(folder + '/es', root='ES',
                                    rows=[row(START + 3, source_order=0, size=7, instrument_id=ES_ID)],
                                    start=START, end=END, delay=DELAY, instrument_id=ES_ID)
            measured = build_measured(rows, start=START, end=END, delay=DELAY, instrument_ids=(NQ_ID,),
                                      atom_flags={NQ_ID: ((True, True), (True, True), (True, True))})
            trades = write_series(harness.storage, 'NQ-current-trades', [make_trade_table(rows)])
            measurement = harness.outputs.json_compressed('NQ-current-measurements.json.zst', measured,
                                                          kind='auction_flow_full_window_measurements')
            unit = {'root': 'NQ', 'cash_date': '2020-03-16', 'event_start_ns': START,
                    'event_end_ns': END, 'source_path': 'test/NQ/current.parquet',
                    'source_variant': 'fixture'}
            contract = harness.contract(nq_ref, es_ref)
            contract['kind'] = 'not-the-registered-contract'
            with self.assertRaises(ContractError):
                check_cohort_unit(measured, unit, measurement_reference=measurement,
                                  trade_storage=trades, outputs=harness.outputs, contract=contract)
            contract = harness.contract(nq_ref, es_ref)
            contract['fixed_soft_knots'] = [1, 30, 61, 75, 101]
            with self.assertRaises(ContractError):
                check_cohort_unit(measured, unit, measurement_reference=measurement,
                                  trade_storage=trades, outputs=harness.outputs, contract=contract)
            contract = harness.contract(nq_ref, es_ref)
            contract['fixed_soft_knots'] = [1, 30, 61, 75, True]
            with self.assertRaises(ContractError):
                check_cohort_unit(measured, unit, measurement_reference=measurement,
                                  trade_storage=trades, outputs=harness.outputs, contract=contract)
            contract = harness.contract(nq_ref, es_ref)
            contract['adaptive_definitions'][0]['probabilities'] = [[True, 4], [1, 2], [3, 4]]
            with self.assertRaises(ContractError):
                check_cohort_unit(measured, unit, measurement_reference=measurement,
                                  trade_storage=trades, outputs=harness.outputs, contract=contract)
            contract = harness.contract(nq_ref, es_ref)
            contract['adaptive_definitions'][0]['probabilities'] = [[Fraction(1, 1), 4], [1, 2], [3, 4]]
            with self.assertRaises(ContractError):
                check_cohort_unit(measured, unit, measurement_reference=measurement,
                                  trade_storage=trades, outputs=harness.outputs, contract=contract)
            self.assertEqual(CONTRACT_KIND, production_contract()['kind'])
            self.assertEqual(production_contract()['maximum_training_prefix_prints'], PREFIX_LIMIT)

    def test_scalar_timestamp_trim_keeps_full_main_paths(self):
        early = [row(START + 1, source_order=index, size=2, side=1) for index in range(4095)]
        tied = [row(START + 2, source_order=4095 + index, size=3, side=-1) for index in range(10)]
        later = [row(START + MINUTE + 3, source_order=5000, size=11, side=1)]
        current = early + tied + later
        training = ordinary_rows()
        flags = {NQ_ID: ((True, True), (True, True), (True, True))}
        with TemporaryDirectory() as folder:
            summary, artifact, _ = _Harness(folder).run(
                current_rows=current, nq_rows=training, atom_flags=flags)
            fixed = next(item for item in artifact['instruments'][0]['definitions'] if item['name'] == 'all')
            atoms = decode_atoms(fixed['atomic'])
            self.assertEqual(fixed['whole']['prints'], len(current))
            self.assertEqual(len(atoms), 3)
            self.assertEqual(sum(bar['prints'] for bar in atoms), len(current))
            self.assertEqual(fixed['scalar_reference']['selected_count'], 4095)
            self.assertTrue(fixed['scalar_reference']['truncated_final_timestamp_group'])
            self.assertIsNone(fixed['scalar_reference']['disposition'])
            self.assertEqual(fixed['scalar_reference']['first']['source_order'], 0)
            self.assertEqual(fixed['scalar_reference']['last']['source_order'], 4094)
            self.assertEqual(summary['workload_counts']['scalar_reference_sliced_prints'], 5 * 4095 + 3)

    def test_scalar_all_probe_prints_one_timestamp_are_unavailable(self):
        tied = [row(START + 1, source_order=index, size=2, side=1) for index in range(PREFIX_PROBE)]
        later = [row(START + MINUTE + 4, source_order=6000, size=6, side=-1)]
        current = tied + later
        flags = {NQ_ID: ((True, True), (True, True), (True, True))}
        with TemporaryDirectory() as folder:
            _, artifact, _ = _Harness(folder).run(
                current_rows=current, nq_rows=ordinary_rows(), atom_flags=flags)
            fixed = next(item for item in artifact['instruments'][0]['definitions'] if item['name'] == 'all')
            self.assertEqual(fixed['whole']['prints'], len(current))
            self.assertEqual(sum(bar['prints'] for bar in decode_atoms(fixed['atomic'])), len(current))
            self.assertEqual(fixed['scalar_reference']['selected_count'], 0)
            self.assertTrue(fixed['scalar_reference']['truncated_final_timestamp_group'])
            self.assertEqual(fixed['scalar_reference']['disposition'],
                             'unavailable_empty_scalar_prefix_after_timestamp_group_trim')
            self.assertIsNone(fixed['scalar_reference']['first'])
            self.assertEqual(fixed['scalar_reference_prints'], 0)

    def test_flagged_prefix_keeps_original_source_evidence(self):
        rows = ordinary_rows()
        rows[0] = trade_row(rows[0]['t'], source_order=rows[0]['source_order'], size=rows[0]['size'],
                            raw_side='B', delay=DELAY, instrument_id=NQ_ID, source_key='src',
                            source_row=rows[0]['source_row'], raw_flags=1, raw_action='T')
        flags = {NQ_ID: ((True, True), (True, True), (True, True))}
        with TemporaryDirectory() as folder:
            _, artifact, _ = _Harness(folder).run(current_rows=rows, nq_rows=rows, atom_flags=flags)
            fixed = next(item for item in artifact['instruments'][0]['definitions'] if item['name'] == 'all')
            self.assertEqual(fixed['scalar_reference']['first']['raw_flags'], 1)
            self.assertEqual(fixed['scalar_reference']['first']['raw_action'], 'T')
            self.assertEqual(fixed['scalar_reference']['first']['raw_side'], 'B')
            self.assertEqual(fixed['scalar_reference']['first']['raw_flags'], rows[0]['raw_flags'])
            self.assertTrue(fixed['scalar_reference']['prefix_digest'])

    def test_rejects_missing_or_changed_training_delay_and_window(self):
        rows = ordinary_rows()
        with TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaises(IntegrityError):
                nq = write_training(root / 'delay-missing', root='NQ', rows=rows, start=START, end=END,
                                    delay=DELAY, instrument_id=NQ_ID,
                                    mutate_payload=lambda payload: payload['source_manifest'].pop(
                                        'event_latency_scenario_ns'))
                _Harness(root / 'delay-missing-run').run(current_rows=rows, nq_rows=rows, nq_ref=nq)
            with self.assertRaises(IntegrityError):
                nq = write_training(root / 'delay-changed', root='NQ', rows=rows, start=START, end=END,
                                    delay=DELAY, instrument_id=NQ_ID,
                                    mutate_payload=lambda payload: payload['source_manifest'].__setitem__(
                                        'event_latency_scenario_ns', DELAY + 1))
                _Harness(root / 'delay-changed-run').run(current_rows=rows, nq_rows=rows, nq_ref=nq)
            with self.assertRaises(IntegrityError):
                nq = write_training(root / 'window-changed', root='NQ', rows=rows, start=START, end=END,
                                    delay=DELAY, instrument_id=NQ_ID,
                                    mutate_payload=lambda payload: payload['unit'].__setitem__(
                                        'event_end_ns', END + 1))
                _Harness(root / 'window-changed-run').run(current_rows=rows, nq_rows=rows, nq_ref=nq)
            with self.assertRaises(IntegrityError):
                nq = write_training(root / 'known-missing', root='NQ', rows=rows, start=START, end=END,
                                    delay=DELAY, instrument_id=NQ_ID,
                                    mutate_measured=lambda measured: measured.pop('known_at_ns'))
                _Harness(root / 'known-missing-run').run(current_rows=rows, nq_rows=rows, nq_ref=nq)

    def test_rejects_duplicate_and_unknown_current_instrument_ids(self):
        rows = ordinary_rows()
        flags = {NQ_ID: ((True, True), (True, True), (True, True))}
        measured = build_measured(rows, start=START, end=END, delay=DELAY, instrument_ids=(NQ_ID,),
                                  atom_flags=flags)
        measured['instruments'].append(dict(measured['instruments'][0]))
        with TemporaryDirectory() as folder:
            with self.assertRaises(IntegrityError):
                _Harness(Path(folder) / 'duplicate').run(
                    current_rows=rows, nq_rows=rows, measured=measured, atom_flags=flags)
        extra = rows + [row(START + MINUTE + 7, source_order=80, size=4, side=1, instrument_id=99)]
        with TemporaryDirectory() as folder:
            with self.assertRaises(IntegrityError):
                _Harness(Path(folder) / 'unknown').run(
                    current_rows=extra, nq_rows=rows, instrument_ids=(NQ_ID,), atom_flags=flags)

    def test_cpu_total_closes_against_disjoint_stages(self):
        rows = ordinary_rows()
        with TemporaryDirectory() as folder:
            summary, _, _ = _Harness(folder).run(current_rows=rows, nq_rows=rows)
            cpu = summary['cpu_components_disjoint']
            self.assertGreaterEqual(cpu['orchestration_and_report_assembly'], 0)
            self.assertEqual(cpu['serialization'], summary['serialization_cpu_seconds'])
            self.assertAlmostEqual(sum(cpu.values()), summary['helper_cpu_seconds'], places=9)
            self.assertGreater(summary['helper_cpu_seconds'], cpu['serialization'])
