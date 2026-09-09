import hashlib
import tempfile
import unittest
from pathlib import Path

import pyarrow as pa

from trading_research.errors import IntegrityError
from trading_research.foundations.time import MINUTE, NS
from trading_research.research.auction_flow_observation_tables import observation_schema, observation_table
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries
from trading_research.research.auction_flow_window_population import (
    CONTRACT_KIND,
    DAY_NS,
    LOOKAHEAD_NS,
    LOOKBACK_NS,
    SOURCE_SHARDS,
    decode_window_unit_id,
    encode_window_unit_id,
    join_window_eligibility,
    plan_window_units,
    project_window_resources,
    run_window_population,
    scientific_contract_digest,
    source_path_shard,
    window_unit_cache_key,
)
from trading_research.research.auction_flow_windows import TRADE_FIELDS


PATH_A = 'quantpad/cme__nq-a/file.parquet'
PATH_B = 'quantpad/cme__nq-b/file.parquet'
DAY0 = 1577836800000000000
META = 'ab' * 32
CALENDAR = {
    'kind': 'cash_rth_calendar',
    'path': '/workspace/trading-research/configs/cash-rth-calendar-research-v1.json',
    'sha256': 'f069df0ccbb8318f1c675a05d9deed64ad681ebe1e47dd8573a6b18266665818',
    'size_bytes': 6922,
}


def _sha(tag):
    return hashlib.sha256(tag.encode()).hexdigest()


def _contract(**overrides):
    payload = {
        'kind': CONTRACT_KIND,
        'version': 1,
        'family_complete': False,
        'cut_cadence_ns': 5 * MINUTE,
        'formation_minutes': [5, 15, 60, 240],
        'latency_ns': [250_000_000, 0, 1_000_000_000],
        'forward_horizons_minutes': [5, 15, 60],
        'stage_policy': {
            'ES': {
                'calibration': ['2024-01-01', '2024-04-01'],
                'confirmation': ['2024-04-01', '2024-09-01'],
                'development': ['2023-07-01', '2024-01-01'],
                'training': ['2020-01-01', '2021-01-01'],
            },
            'NQ': {
                'calibration': ['2024-01-01', '2025-01-01'],
                'confirmation': ['2025-01-01', '2026-09-04'],
                'development': ['2023-01-01', '2024-01-01'],
                'training': ['2020-01-01', '2023-01-01'],
            },
            'other_dates': 'separate unassigned descriptive rows, not training or confirmation',
        },
        'cash_calendar': CALENDAR,
        'phase': 'pilot',
    }
    payload.update(overrides)
    return payload


def _obs_unit(path, start, *, receipt_sha, series=None, rows=1440, instruments=1, trades=4,
              status='measured'):
    return {
        'kind': 'auction_flow_observation_unit_v1',
        'root': 'NQ',
        'source_path': path,
        'source_window_start_ns': start,
        'source_window_end_ns': start + DAY_NS,
        'source_window_status': status,
        'atomic_rows': rows,
        'observation_rows': rows,
        'instruments': instruments,
        'receipt': {
            'path': f'/receipts/{receipt_sha}.json',
            'sha256': receipt_sha,
            'size_bytes': 12,
            'kind': 'auction_flow_source_window_receipt_v1',
        },
        'series': series or {'rows': rows, 'schema': 'obs', 'files': [], 'roundtrip_exact': True},
        'receipt_counts': {'trades': trades},
        'original_refs': {'receipt_sha256': receipt_sha},
    }


def _population(units):
    return {
        'kind': 'auction_flow_observation_population_v1',
        'all_population_materialized': True,
        'population_source_windows': len(units),
        'population_source_files': len({unit['source_path'] for unit in units}),
        'units': units,
        'complete_family_statistics': False,
    }


def _blank_obs(**overrides):
    row = {}
    for field in observation_schema():
        if pa.types.is_boolean(field.type):
            row[field.name] = True
        elif pa.types.is_integer(field.type):
            row[field.name] = None if field.nullable else 0
        elif pa.types.is_floating(field.type):
            row[field.name] = None
        else:
            row[field.name] = None if field.nullable else ''
    row['root'] = 'NQ'
    row['source_path'] = PATH_A
    row['source_metadata_sha256'] = META
    row['source_variant'] = 'fixture'
    row['instrument_id'] = 7
    row['contract_key'] = 'NQ:NQH4:7:0:1000'
    row.update(overrides)
    return row


def _trade_row(event_ns, *, source_order, instrument_id=7):
    return {
        't': event_ns,
        'source_order': source_order,
        'instrument_id': instrument_id,
        'price': 10,
        'size': 1,
        'side': 1,
        'price_valid': 1,
        'source_row': source_order,
        'source_key': 'fixture',
        'raw_flags': 0,
        'raw_side': 'B',
        'raw_action': 'T',
        'known_at_ns': event_ns + 250_000_000,
    }


def _trade_table(rows):
    if not rows:
        arrays = {}
        for name in TRADE_FIELDS:
            arrays[name] = pa.array([], type=pa.string() if name in ('source_key', 'raw_side', 'raw_action') else pa.int64())
        return pa.table(arrays)
    data = {name: [row[name] for row in rows] for name in TRADE_FIELDS}
    arrays = {}
    for name in TRADE_FIELDS:
        arrays[name] = pa.array(
            data[name],
            type=pa.string() if name in ('source_key', 'raw_side', 'raw_action') else pa.int64(),
        )
    return pa.table(arrays)


def _store(outputs, name, table):
    series = ParquetSeries(outputs, name, encoding='plain')
    series.append(table)
    return series.finish()


def _identity(**overrides):
    payload = {
        'root': 'NQ',
        'source_path': PATH_A,
        'source_metadata_sha256': META,
        'source_variant': 'fixture12ab34',
        'acquired_event_start_ns': DAY0,
        'acquired_event_end_ns': DAY0 + 3 * DAY_NS,
    }
    payload.update(overrides)
    return payload


def _feature_label(*, cut_ns=DAY0 + 12 * 60 * MINUTE, latency_ns=250_000_000,
                   formation_start=None, known_at=None, contract_key='NQ:NQH4:7:0:1000'):
    start = DAY0 + 12 * 60 * MINUTE - 5 * MINUTE if formation_start is None else formation_start
    maturity = cut_ns + latency_ns + 5 * MINUTE if known_at is None else known_at
    feature = {
        **_identity(),
        'instrument_id': 7,
        'contract_key': contract_key,
        'cut_ns': cut_ns,
        'event_start_ns': start,
        'formation_minutes': 5,
    }
    label = {
        **_identity(),
        'instrument_id': 7,
        'contract_key': contract_key,
        'cut_ns': cut_ns,
        'latency_ns': latency_ns,
        'known_at_ns': maturity,
        'stage': 'training',
    }
    return feature, label


class IdentityAndPlanTests(unittest.TestCase):
    def test_encode_decode_and_source_path_shards(self):
        key = encode_window_unit_id(PATH_A, DAY0, DAY0 + DAY_NS)
        self.assertEqual(decode_window_unit_id(key), {
            'source_path': PATH_A, 'event_start_ns': DAY0, 'event_end_ns': DAY0 + DAY_NS,
        })
        self.assertEqual(decode_window_unit_id(_sha('receipt')), {'receipt_sha256': _sha('receipt')})
        self.assertEqual(source_path_shard(PATH_A), source_path_shard(PATH_A))
        self.assertTrue(0 <= source_path_shard(PATH_A) < SOURCE_SHARDS)
        # Distinct physical files may share one of eight processing shards.
        self.assertEqual(source_path_shard(PATH_A), 1)
        self.assertEqual(source_path_shard(PATH_B), 1)

    def test_boundaries_gaps_and_no_cross_physical_file(self):
        a0 = _obs_unit(PATH_A, DAY0, receipt_sha=_sha('a0'))
        a1 = _obs_unit(PATH_A, DAY0 + DAY_NS, receipt_sha=_sha('a1'))
        a2 = _obs_unit(PATH_A, DAY0 + 2 * DAY_NS, receipt_sha=_sha('a2'))
        b1 = _obs_unit(PATH_B, DAY0 + DAY_NS, receipt_sha=_sha('b1'))
        plan = plan_window_units(_population([a0, a1, a2, b1]))
        by_id = {tuple(row['unit_id']): row for row in plan['selected']}
        first = by_id[tuple(encode_window_unit_id(PATH_A, DAY0, DAY0 + DAY_NS))]
        middle = by_id[tuple(encode_window_unit_id(PATH_A, DAY0 + DAY_NS, DAY0 + 2 * DAY_NS))]
        last = by_id[tuple(encode_window_unit_id(PATH_A, DAY0 + 2 * DAY_NS, DAY0 + 3 * DAY_NS))]
        other = by_id[tuple(encode_window_unit_id(PATH_B, DAY0 + DAY_NS, DAY0 + 2 * DAY_NS))]
        self.assertEqual(first['member_count'], 2)
        self.assertIsNone(first['members']['previous'])
        self.assertEqual(first['members']['next'], encode_window_unit_id(PATH_A, DAY0 + DAY_NS, DAY0 + 2 * DAY_NS))
        self.assertEqual(middle['member_count'], 3)
        self.assertEqual(middle['members']['previous'], encode_window_unit_id(PATH_A, DAY0, DAY0 + DAY_NS))
        self.assertEqual(middle['members']['next'], encode_window_unit_id(PATH_A, DAY0 + 2 * DAY_NS, DAY0 + 3 * DAY_NS))
        self.assertEqual(last['member_count'], 2)
        self.assertIsNone(last['members']['next'])
        self.assertEqual(other['member_count'], 1)
        self.assertIsNone(other['members']['previous'])
        self.assertIsNone(other['members']['next'])
        gapped = plan_window_units(_population([a0, a2]))
        isolated = {tuple(row['unit_id']): row for row in gapped['selected']}
        self.assertEqual(isolated[tuple(encode_window_unit_id(PATH_A, DAY0 + 2 * DAY_NS, DAY0 + 3 * DAY_NS))]['member_count'], 1)
        self.assertIsNone(isolated[tuple(encode_window_unit_id(PATH_A, DAY0 + 2 * DAY_NS, DAY0 + 3 * DAY_NS))]['members']['previous'])

    def test_unavailable_units_are_preserved_and_selected_ids_join(self):
        measured = _obs_unit(PATH_A, DAY0, receipt_sha=_sha('m'), rows=1440, instruments=1)
        empty = _obs_unit(PATH_A, DAY0 + DAY_NS, receipt_sha=_sha('u'), rows=0, instruments=0,
                          trades=0, status='unavailable_source_window')
        plan = plan_window_units(_population([measured, empty]))
        self.assertEqual(plan['selected_units'], 2)
        self.assertEqual(plan['unavailable_units'], 1)
        self.assertEqual(plan['measured_units'], 1)
        self.assertTrue(plan['selected'][1]['unavailable'])
        only = plan_window_units(_population([measured, empty]), selected_unit_ids=[_sha('u')])
        self.assertEqual(only['selected_units'], 1)
        self.assertEqual(only['selected'][0]['receipt_sha256'], _sha('u'))
        self.assertTrue(only['selected'][0]['unavailable'])
        with self.assertRaises(IntegrityError):
            plan_window_units(_population([measured]), selected_unit_ids=[_sha('missing')])

    def test_operational_source_path_filter_does_not_cross_files(self):
        a0 = _obs_unit(PATH_A, DAY0, receipt_sha=_sha('a0'))
        b0 = _obs_unit(PATH_B, DAY0, receipt_sha=_sha('b0'))
        plan = plan_window_units(_population([a0, b0]), source_paths=[PATH_A])
        self.assertEqual(plan['selected_units'], 1)
        self.assertEqual(plan['source_files'], [PATH_A])
        self.assertEqual(plan['source_unit_counts'], {PATH_A: 1})

    def test_cache_key_changes_when_neighbor_membership_or_science_changes(self):
        left = window_unit_cache_key(
            unit_id=encode_window_unit_id(PATH_A, DAY0, DAY0 + DAY_NS),
            receipt_sha256=_sha('a0'),
            observation_series={'rows': 2, 'schema': 's', 'files': [{'sha256': _sha('f'), 'rows': 2, 'row_group_values': [{'sha256': _sha('g'), 'rows': 2}]}]},
            neighbor_refs={'previous': None, 'current': {'receipt': {'sha256': _sha('a0')}}, 'next': None},
            source_identity=_identity(),
            contract_digest=scientific_contract_digest(_contract()),
        )
        changed_neighbor = window_unit_cache_key(
            unit_id=encode_window_unit_id(PATH_A, DAY0, DAY0 + DAY_NS),
            receipt_sha256=_sha('a0'),
            observation_series={'rows': 2, 'schema': 's', 'files': [{'sha256': _sha('f'), 'rows': 2, 'row_group_values': [{'sha256': _sha('g'), 'rows': 2}]}]},
            neighbor_refs={'previous': {'receipt': {'sha256': _sha('prev')}}, 'current': {'receipt': {'sha256': _sha('a0')}}, 'next': None},
            source_identity=_identity(),
            contract_digest=scientific_contract_digest(_contract()),
        )
        changed_science = window_unit_cache_key(
            unit_id=encode_window_unit_id(PATH_A, DAY0, DAY0 + DAY_NS),
            receipt_sha256=_sha('a0'),
            observation_series={'rows': 2, 'schema': 's', 'files': [{'sha256': _sha('f'), 'rows': 2, 'row_group_values': [{'sha256': _sha('g'), 'rows': 2}]}]},
            neighbor_refs={'previous': None, 'current': {'receipt': {'sha256': _sha('a0')}}, 'next': None},
            source_identity=_identity(),
            contract_digest=scientific_contract_digest(_contract(identity='changed-science')),
        )
        operational = window_unit_cache_key(
            unit_id=encode_window_unit_id(PATH_A, DAY0, DAY0 + DAY_NS),
            receipt_sha256=_sha('a0'),
            observation_series={'rows': 2, 'schema': 's', 'files': [{'sha256': _sha('f'), 'rows': 2, 'row_group_values': [{'sha256': _sha('g'), 'rows': 2}]}]},
            neighbor_refs={'previous': None, 'current': {'receipt': {'sha256': _sha('a0')}}, 'next': None},
            source_identity=_identity(),
            contract_digest=scientific_contract_digest(_contract(phase='full', selected_unit_ids=['x'])),
        )
        self.assertNotEqual(left, changed_neighbor)
        self.assertNotEqual(left, changed_science)
        self.assertEqual(left, operational)


class JoinAndProjectionTests(unittest.TestCase):
    def test_join_requires_same_stage_source_and_contract(self):
        feature, label = _feature_label()
        ok = join_window_eligibility(feature, label)
        self.assertTrue(ok['eligible'])
        self.assertEqual(ok['stage'], 'training')
        missing = join_window_eligibility({**feature, 'contract_key': None}, label)
        self.assertFalse(missing['eligible'])
        self.assertEqual(missing['reason'], 'absent_or_unknown_contract')
        other = join_window_eligibility({**feature, 'source_path': PATH_B}, label)
        self.assertEqual(other['reason'], 'source_identity_mismatch')
        label_stage_only = join_window_eligibility(
            feature,
            {**label, 'known_at_ns': _civil_2023(), 'stage': 'training'},
        )
        self.assertFalse(label_stage_only['eligible'])
        self.assertEqual(label_stage_only['reason'], 'label_maturity_not_same_named_stage')
        self.assertEqual(label_stage_only['feature_interval_stage'], 'training')
        crossed = join_window_eligibility(
            {**feature, 'cut_ns': _civil_2023(), 'event_start_ns': _civil_2023() - 240 * MINUTE},
            {**label, 'cut_ns': _civil_2023(), 'known_at_ns': _civil_2023() + 5 * MINUTE, 'latency_ns': 0},
        )
        self.assertEqual(crossed['reason'], 'feature_not_inside_named_stage')

    def test_projection_uses_obs_trade_envelope_and_never_divides_empty_zero(self):
        inventory = [
            {'observation_rows': 10, 'trade_rows': 10},
            {'observation_rows': 5, 'trade_rows': 5},
            {'observation_rows': 0, 'trade_rows': 0},
        ]
        measured = [
            {'cpu_seconds': 2.0, 'wall_seconds': 4.0, 'output_bytes': 40,
             'observation_input_rows': 10, 'trade_input_rows': 10},
            {'cpu_seconds': 0.5, 'wall_seconds': 1.0, 'output_bytes': 0,
             'observation_input_rows': 0, 'trade_input_rows': 0},
        ]
        result = project_window_resources(inventory, measured)
        self.assertEqual(result['population_nonempty_input_rows'], 30)
        self.assertEqual(result['cpu_seconds_with_margin'], 1.5 * (2.0 / 20 * 30 + 0.5 * 3))
        self.assertEqual(result['sequential_wall_seconds_with_margin'], 1.5 * (4.0 / 20 * 30 + 1.0 * 3))
        self.assertEqual(result['output_bytes_with_margin'], int(1.5 * (40 / 20) * 30) + 16 * 1024 ** 2)
        self.assertFalse(result['complete_feasible'])
        with self.assertRaises(IntegrityError):
            project_window_resources(inventory, [
                {'cpu_seconds': 0.1, 'output_bytes': 0, 'observation_input_rows': 0, 'trade_input_rows': 0},
            ])


def _civil_2023():
    return int((datetime_utc(2023, 1, 1) - datetime_utc(1970, 1, 1)).total_seconds() * NS)


def datetime_utc(year, month, day):
    from datetime import datetime, timezone
    return datetime(year, month, day, tzinfo=timezone.utc)


class DriverRunTests(unittest.TestCase):
    def test_fake_build_sees_literal_member_and_filter_counts(self):
        calls = []

        def fake_build(observations, trades, *, contract, source_identity, cut_start_ns, cut_end_ns, calendar):
            days = sorted({int(value) // DAY_NS for value in observations['event_start_ns'].to_pylist()})
            calls.append({
                'observation_rows': len(observations),
                'trade_rows': len(trades),
                'observation_columns': observations.num_columns,
                'instrument_ids': sorted({int(value) for value in observations['instrument_id'].to_pylist()}),
                'trade_instrument_ids': sorted({int(value) for value in trades['instrument_id'].to_pylist()}),
                'member_days': len(days),
                'cut_start_ns': cut_start_ns,
                'cut_end_ns': cut_end_ns,
                'acquired_start': source_identity['acquired_event_start_ns'],
                'acquired_end': source_identity['acquired_event_end_ns'],
                'support_ok': (
                    min(observations['event_start_ns'].to_pylist()) >= cut_start_ns - LOOKBACK_NS
                    and max(observations['event_end_ns'].to_pylist()) <= cut_end_ns + LOOKAHEAD_NS
                ),
            })
            features = pa.table({
                'cut_ns': [cut_start_ns],
                'instrument_id': [7],
                'atoms_complete': [True],
                'left_censored': [False],
                'right_censored': [False],
            })
            labels = pa.table({
                'cut_ns': [cut_start_ns],
                'instrument_id': [7],
                'complete': [True],
                'left_censored': [False],
                'right_censored': [False],
                'latency_ns': [250_000_000],
                'horizon_minutes': [5],
            })
            return {
                'features': features,
                'labels': labels,
                'validation': {
                    'feature_rows': 1, 'label_rows': 1, 'instrument_count': 1,
                    'instrument_ids': [7], 'cut_count': 288, 'source_unit_disposition': None,
                },
            }

        cut = DAY0 + DAY_NS
        with tempfile.TemporaryDirectory() as folder:
            inputs = BoundedOutputs(Path(folder) / 'in', maximum_total_bytes=8 * 1024 ** 2,
                                    maximum_file_bytes=4 * 1024 ** 2)
            prev_obs = observation_table([
                _blank_obs(event_start_ns=cut - 300 * MINUTE, event_end_ns=cut - 299 * MINUTE,
                           instrument_id=7, atomic_bin=0),
                _blank_obs(event_start_ns=cut - 60 * MINUTE, event_end_ns=cut - 59 * MINUTE,
                           instrument_id=7, atomic_bin=1),
                _blank_obs(event_start_ns=cut - 60 * MINUTE, event_end_ns=cut - 59 * MINUTE,
                           instrument_id=99, atomic_bin=2),
            ])
            current_obs = observation_table([
                _blank_obs(event_start_ns=cut, event_end_ns=cut + MINUTE, instrument_id=7, atomic_bin=3),
            ])
            next_obs = observation_table([
                _blank_obs(event_start_ns=cut + DAY_NS + 10 * MINUTE, event_end_ns=cut + DAY_NS + 11 * MINUTE,
                           instrument_id=7, atomic_bin=4),
                _blank_obs(event_start_ns=cut + DAY_NS + 10 * MINUTE, event_end_ns=cut + DAY_NS + 11 * MINUTE,
                           instrument_id=99, atomic_bin=5),
            ])
            prev_tr = _trade_table([
                _trade_row(cut - 300 * MINUTE, source_order=1, instrument_id=99),
                _trade_row(cut - 30 * MINUTE, source_order=2, instrument_id=7),
            ])
            current_tr = _trade_table([_trade_row(cut + 5 * MINUTE, source_order=3, instrument_id=7)])
            next_tr = _trade_table([
                _trade_row(cut + DAY_NS + 5 * MINUTE, source_order=4, instrument_id=7),
                _trade_row(cut + DAY_NS + 5 * MINUTE, source_order=5, instrument_id=99),
            ])
            series = {
                'prev': _store(inputs, 'obs-prev', prev_obs),
                'curr': _store(inputs, 'obs-curr', current_obs),
                'nxt': _store(inputs, 'obs-next', next_obs),
                'tprev': _store(inputs, 'tr-prev', prev_tr),
                'tcurr': _store(inputs, 'tr-curr', current_tr),
                'tnxt': _store(inputs, 'tr-next', next_tr),
            }
            empty_obs = observation_table([])
            empty_tr = _trade_table([])
            series['empty_obs'] = _store(inputs, 'obs-empty', empty_obs)
            series['empty_tr'] = _store(inputs, 'tr-empty', empty_tr)
            receipts = {}

            def put_receipt(tag, start, obs_series, trade_series, *, file_end=None, rows=1):
                sha = _sha(tag)
                receipts[sha] = {
                    'kind': 'auction_flow_source_window_receipt_v1',
                    'success': True,
                    'status': 'measured' if rows else 'unavailable_source_window',
                    'source_metadata_sha256': META,
                    'unit': {
                        'root': 'NQ',
                        'source_path': PATH_A,
                        'source_metadata_sha256': META,
                        'event_start_ns': start,
                        'event_end_ns': start + DAY_NS,
                        'observed_file_start_ns': DAY0,
                        'observed_file_end_ns': (DAY0 + 4 * DAY_NS - 1) if file_end is None else file_end,
                    },
                    'event_storage': {'trades': trade_series},
                    'artifacts': {'trades': trade_series},
                    'counts': {'trades': trade_series['rows']},
                }
                return sha

            sha_prev = put_receipt('prev', DAY0, series['prev'], series['tprev'])
            sha_curr = put_receipt('curr', cut, series['curr'], series['tcurr'])
            sha_next = put_receipt('next', cut + DAY_NS, series['nxt'], series['tnxt'])
            sha_empty = put_receipt('empty', cut + 2 * DAY_NS, series['empty_obs'], series['empty_tr'], rows=0)
            units = [
                _obs_unit(PATH_A, DAY0, receipt_sha=sha_prev, series=series['prev'], rows=3, instruments=2, trades=2),
                _obs_unit(PATH_A, cut, receipt_sha=sha_curr, series=series['curr'], rows=1, instruments=1, trades=1),
                _obs_unit(PATH_A, cut + DAY_NS, receipt_sha=sha_next, series=series['nxt'], rows=2, instruments=2, trades=2),
                _obs_unit(PATH_A, cut + 2 * DAY_NS, receipt_sha=sha_empty, series=series['empty_obs'],
                          rows=0, instruments=0, trades=0, status='unavailable_source_window'),
            ]
            outputs = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=8 * 1024 ** 2,
                                     maximum_file_bytes=4 * 1024 ** 2)

            def load_reference(reference, **_):
                return receipts[reference['sha256']]

            result = run_window_population(
                population=_population(units),
                contract=_contract(selected_unit_ids=[sha_curr, sha_empty]),
                outputs=outputs,
                load_reference=load_reference,
                finalize=False,
                build_tables=fake_build,
            )
            self.assertFalse(result['finalize'])
            self.assertEqual(result['processed_source_windows'], 2)
            self.assertEqual(result['unavailable_source_windows'], 1)
            self.assertNotIn('window-population.json', outputs.names)
            self.assertEqual(len(calls), 1)
            seen = calls[0]
            self.assertEqual(seen['observation_columns'], len(observation_schema()))
            self.assertEqual(seen['instrument_ids'], [7])
            self.assertEqual(seen['trade_instrument_ids'], [7])
            self.assertEqual(seen['observation_rows'], 3)
            self.assertEqual(seen['trade_rows'], 3)
            self.assertEqual(seen['member_days'], 3)
            self.assertTrue(seen['support_ok'])
            self.assertEqual(seen['acquired_start'], DAY0)
            self.assertEqual(seen['acquired_end'], DAY0 + 4 * DAY_NS)
            empty_unit = [row for row in result['units'] if row['receipt_sha256'] == sha_empty][0]
            self.assertEqual(empty_unit['feature_rows'], 0)
            self.assertEqual(empty_unit['label_rows'], 0)
            self.assertEqual(empty_unit['disposition'], 'no_observed_instrument')
            current_unit = [row for row in result['units'] if row['receipt_sha256'] == sha_curr][0]
            self.assertEqual(current_unit['neighbor_member_refs']['previous']['receipt']['sha256'], sha_prev)
            self.assertEqual(current_unit['neighbor_member_refs']['next']['receipt']['sha256'], sha_next)
            self.assertEqual(current_unit['feature_rows'], 1)
            self.assertGreaterEqual(result['data_reads'], 1)
            finalized = run_window_population(
                population=_population(units),
                contract=_contract(
                    selected_unit_ids=[sha_curr],
                    accepted_window_units=[current_unit],
                ),
                outputs=BoundedOutputs(Path(folder) / 'out2', maximum_total_bytes=8 * 1024 ** 2,
                                       maximum_file_bytes=4 * 1024 ** 2),
                load_reference=load_reference,
                finalize=True,
                build_tables=fake_build,
            )
            self.assertEqual(len(calls), 1)
            self.assertEqual(finalized['reused_units'], 1)
            self.assertTrue(finalized['refs']['population']['path'].endswith('window-population.json'))
            self.assertFalse(finalized['family_complete'])
            self.assertFalse(finalized['complete_feasible'])
            self.assertFalse(finalized['resource_projection']['complete_feasible'])
