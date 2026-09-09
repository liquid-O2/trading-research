"""Independent expected cases for causal window-link tables.

Expected values are derived from the scientific contract and calendar
helpers, not from the implementation's internal aggregation functions.
"""
from datetime import date, datetime, time, timezone
from pathlib import Path
import unittest

import pyarrow as pa

from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.foundations.time import MINUTE, NS, datetime_ns
from trading_research.research.auction_flow_measurements import SOURCE_FILTERS
from trading_research.research.auction_flow_observation_tables import (
    observation_schema,
    observation_table,
)
from trading_research.research.auction_flow_window_links import (
    CONTRACT_KIND,
    CUT_CADENCE_NS,
    FORMATION_MINUTES,
    LATENCY_NS,
    SOURCE_LATENCY_NS,
    VERSION,
    build_window_tables,
    feature_column_names,
    feature_schema,
    label_column_names,
    label_schema,
)
from trading_research.research.auction_flow_windows import TRADE_FIELDS


CALENDAR_PATH = Path('/workspace/trading-research/configs/cash-rth-calendar-research-v1.json')
SOURCE_PATH = 'quantpad/cme__nq-continuous-futures__mbp-1/window-link-fixture.parquet'
SOURCE_META = 'aa' * 32
SOURCE_VARIANT = 'fixture12ab34'
CONTRACT_KEY = 'NQ:NQH4:7:0:1000'


def frozen_contract():
    return {
        'kind': CONTRACT_KIND,
        'version': 1,
        'family_complete': False,
        'cut_cadence_ns': CUT_CADENCE_NS,
        'formation_minutes': [5, 15, 60, 240],
        'latency_ns': [250_000_000, 0, 1_000_000_000],
        'forward_horizons_minutes': [5, 15, 60],
        'identity': 'root+physicalsourcepath+instrument+rawcontract coordinate+formation/end',
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
    }


def source_identity(*, start, end, root='NQ'):
    return {
        'root': root,
        'source_path': SOURCE_PATH,
        'source_metadata_sha256': SOURCE_META,
        'source_variant': SOURCE_VARIANT,
        'acquired_event_start_ns': start,
        'acquired_event_end_ns': end,
    }


def research_calendar():
    return CashCalendar(CALENDAR_PATH)


def blank_observation(**overrides):
    row = {}
    for field in observation_schema():
        if field.name in overrides:
            row[field.name] = overrides[field.name]
            continue
        if pa.types.is_boolean(field.type):
            row[field.name] = field.name in (
                'coordinate_complete', 'source_instrument_presence',
                'source_coverage_complete', 'flow_history_complete',
                'price_history_complete', 'empty_observed_window',
                'quote_coverage_complete',
            ) or field.name.endswith('__coverage_complete')
        elif pa.types.is_integer(field.type):
            row[field.name] = None if field.nullable else 0
        elif pa.types.is_floating(field.type):
            row[field.name] = None
        else:
            row[field.name] = None if field.nullable else ''
    row.setdefault('root', 'NQ')
    row.setdefault('source_path', SOURCE_PATH)
    row.setdefault('source_metadata_sha256', SOURCE_META)
    row.setdefault('source_variant', SOURCE_VARIANT)
    row.setdefault('contract_key', CONTRACT_KEY)
    row.setdefault('instrument_id', 7)
    return row


def quiet_atom(*, start, end, instrument_id=7, contract_key=CONTRACT_KEY, number=0):
    row = blank_observation(
        instrument_id=instrument_id,
        contract_key=contract_key,
        event_start_ns=start,
        event_end_ns=end,
        known_at_ns=end + SOURCE_LATENCY_NS,
        atomic_bin=number,
        empty_observed_window=True,
        prints=0,
        unpriced_prints=0,
        priced_volume=0,
        sum_price_volume=0,
        sum_price_squared_volume=0,
        standing_duration_ns=0,
    )
    for name in SOURCE_FILTERS:
        row[f'{name}__buy'] = 0
        row[f'{name}__sell'] = 0
        row[f'{name}__unknown'] = 0
        row[f'{name}__volume'] = 0
        row[f'{name}__prints'] = 0
        row[f'{name}__excluded_prints'] = 0
        row[f'{name}__excluded_volume'] = 0
        row[f'{name}__open'] = 0
        row[f'{name}__high'] = 0
        row[f'{name}__low'] = 0
        row[f'{name}__close'] = 0
        row[f'{name}__coverage_complete'] = True
    return row


def path_atom(*, start, end, open_, high, low, close, high_at, low_at, high_order, low_order,
              buy, sell, unknown, prints, priced_volume, sum_price_volume, sum_price_squared_volume,
              first_priced, last_priced, price_high, price_low, price_high_at, price_low_at,
              instrument_id=7, contract_key=CONTRACT_KEY, number=0,
              standing_ns=0, duration_spread=None, duration_imbalance=None,
              pressure=False, ofi=None):
    row = quiet_atom(start=start, end=end, instrument_id=instrument_id,
                     contract_key=contract_key, number=number)
    row['empty_observed_window'] = False
    row['prints'] = prints
    row['priced_volume'] = priced_volume
    row['sum_price_volume'] = sum_price_volume
    row['sum_price_squared_volume'] = sum_price_squared_volume
    row['standing_duration_ns'] = standing_ns
    row['duration_mean_spread_ticks'] = duration_spread
    row['duration_mean_imbalance'] = duration_imbalance
    row['full_standing_window_eligible'] = standing_ns > 0
    row['full_pressure_transition_window_eligible'] = pressure
    volume = buy + sell + unknown
    row['all__buy'] = buy
    row['all__sell'] = sell
    row['all__unknown'] = unknown
    row['all__volume'] = volume
    row['all__prints'] = prints
    row['all__open'] = open_
    row['all__high'] = high
    row['all__low'] = low
    row['all__close'] = close
    row['all__high_at_ns'] = high_at
    row['all__low_at_ns'] = low_at
    row['all__high_source_order'] = high_order
    row['all__low_source_order'] = low_order
    for name in SOURCE_FILTERS:
        if name == 'all':
            continue
        row[f'{name}__excluded_prints'] = prints
        row[f'{name}__excluded_volume'] = volume
    row['first_priced_ticks'] = first_priced
    row['first_priced_event_ns'] = start + 1
    row['first_priced_known_at_ns'] = start + 1 + SOURCE_LATENCY_NS
    row['first_priced_source_order'] = high_order
    row['first_priced_source_row'] = high_order
    row['last_priced_ticks'] = last_priced
    row['last_priced_event_ns'] = end - 1
    row['last_priced_known_at_ns'] = end - 1 + SOURCE_LATENCY_NS
    row['last_priced_source_order'] = low_order
    row['last_priced_source_row'] = low_order
    row['observed_high_ticks'] = price_high
    row['observed_low_ticks'] = price_low
    row['observed_high_at_ns'] = price_high_at
    row['observed_low_at_ns'] = price_low_at
    row['observed_high_source_order'] = high_order
    row['observed_low_source_order'] = low_order
    if ofi is not None:
        row['ofi_open'] = ofi[0]
        row['ofi_high'] = ofi[1]
        row['ofi_low'] = ofi[2]
        row['ofi_close'] = ofi[3]
        row['ofi_high_at_ns'] = high_at
        row['ofi_low_at_ns'] = low_at
        row['ofi_high_source_order'] = high_order
        row['ofi_low_source_order'] = low_order
        row['ofi_contracts'] = ofi[3]
    return row


def observation_rows_to_table(rows):
    return observation_table(rows)


def trade_table(rows):
    if not rows:
        arrays = {}
        for name in TRADE_FIELDS:
            if name in ('source_key', 'raw_side', 'raw_action'):
                arrays[name] = pa.array([], type=pa.string())
            elif name == 'price_valid':
                arrays[name] = pa.array([], type=pa.int64())
            else:
                arrays[name] = pa.array([], type=pa.int64())
        return pa.table(arrays)
    data = {name: [row[name] for row in rows] for name in TRADE_FIELDS}
    arrays = {}
    for name in TRADE_FIELDS:
        if name in ('source_key', 'raw_side', 'raw_action'):
            arrays[name] = pa.array(data[name], type=pa.string())
        else:
            arrays[name] = pa.array(data[name], type=pa.int64())
    return pa.table(arrays)


def trade_row(event_ns, *, source_order, price=10, size=1, side=1, price_valid=1,
              instrument_id=7, raw_side=None):
    if raw_side is None:
        raw_side = 'B' if side == 1 else 'A' if side == -1 else 'N'
    return {
        't': event_ns,
        'source_order': source_order,
        'instrument_id': instrument_id,
        'price': price,
        'size': size,
        'side': side,
        'price_valid': price_valid,
        'source_row': source_order,
        'source_key': 'fixture',
        'raw_flags': 0,
        'raw_side': raw_side,
        'raw_action': 'T',
        'known_at_ns': event_ns + SOURCE_LATENCY_NS,
    }


def feature_at(table, *, cut_ns, minutes, instrument_id=7):
    for row in table.to_pylist():
        if row['cut_ns'] == cut_ns and row['formation_minutes'] == minutes and row['instrument_id'] == instrument_id:
            return row
    raise AssertionError('missing feature row')


def labels_for(table, *, cut_ns, instrument_id=7):
    return [row for row in table.to_pylist()
            if row['cut_ns'] == cut_ns and row['instrument_id'] == instrument_id]


def label_at(table, *, cut_ns, latency_ns, horizon_kind, horizon_minutes=None, instrument_id=7):
    for row in labels_for(table, cut_ns=cut_ns, instrument_id=instrument_id):
        if (row['latency_ns'] == latency_ns and row['horizon_kind'] == horizon_kind
                and row['horizon_minutes'] == horizon_minutes):
            return row
    raise AssertionError('missing label row')


class AuctionFlowWindowLinkTests(unittest.TestCase):
    def setUp(self):
        self.cut = 10 * CUT_CADENCE_NS
        self.cut_end = self.cut + CUT_CADENCE_NS
        self.acquired_start = 0
        self.acquired_end = self.cut_end + 60 * MINUTE
        self.calendar = research_calendar()
        self.contract = frozen_contract()
        self.identity = source_identity(start=self.acquired_start, end=self.acquired_end)

    def five_minute_atoms(self, last_two):
        start = self.cut - 5 * MINUTE
        rows = []
        for i in range(3):
            a = start + i * MINUTE
            rows.append(quiet_atom(start=a, end=a + MINUTE, number=i))
        rows.extend(last_two)
        return rows

    def build(self, observations, trades, *, identity=None, cut_start=None, cut_end=None):
        return build_window_tables(
            observations, trades,
            contract=self.contract,
            source_identity=self.identity if identity is None else identity,
            cut_start_ns=self.cut if cut_start is None else cut_start,
            cut_end_ns=self.cut_end if cut_end is None else cut_end,
            calendar=self.calendar,
        )

    def test_schema_and_static_definitions_retain_every_candidate(self):
        self.assertEqual(VERSION, 'auction-flow-causal-window-links-v1')
        self.assertEqual(FORMATION_MINUTES, (5, 15, 60, 240))
        self.assertEqual(LATENCY_NS, (250_000_000, 0, 1_000_000_000))
        self.assertFalse(feature_schema().equals(label_schema()))
        self.assertIn('formation_id', feature_column_names())
        self.assertIn('reference_price_ticks', feature_column_names())
        self.assertIn('horizon_kind', label_column_names())
        self.assertNotIn('formation_minutes', label_column_names())
        empty = observation_table([])
        result = self.build(empty, trade_table([]))
        self.assertFalse(result['family_complete'])
        self.assertFalse(result['definitions']['family_complete'])
        self.assertEqual(result['validation']['source_unit_disposition'], 'no_observed_instrument')
        self.assertEqual(result['features'].num_rows, 0)
        self.assertEqual(result['labels'].num_rows, 0)
        self.assertEqual(result['definitions']['formation_minutes'], [5, 15, 60, 240])
        self.assertEqual(result['definitions']['latency_ns'], [250_000_000, 0, 1_000_000_000])

    def test_concatenated_cvd_ohlc_uses_offset_path_not_close_extrema(self):
        # Independent path reconstruction:
        # atom A local path 0,5,-2,1 => O=0 H=5 L=-2 C=1
        # atom B local path 0,-4,2 => O=0 H=2 L=-4 C=2
        # offset B by A's close 1 => 1, -3, 3
        # concatenated OHLC 0, 5, -3, 3. Extrema times are the original
        # path stamps, not the atom close stamps.
        a_start = self.cut - 2 * MINUTE
        b_start = self.cut - MINUTE
        high_at_a = a_start + 10
        low_at_a = a_start + 20
        close_at_a = a_start + MINUTE - 1
        high_at_b = b_start + 30
        low_at_b = b_start + 15
        close_at_b = b_start + MINUTE - 1
        atom_a = path_atom(
            start=a_start, end=a_start + MINUTE, number=3,
            open_=0, high=5, low=-2, close=1,
            high_at=high_at_a, low_at=low_at_a, high_order=10, low_order=11,
            buy=5, sell=4, unknown=0, prints=4,
            priced_volume=1, sum_price_volume=10, sum_price_squared_volume=100,
            first_priced=10, last_priced=10, price_high=10, price_low=10,
            price_high_at=high_at_a, price_low_at=low_at_a,
        )
        atom_b = path_atom(
            start=b_start, end=b_start + MINUTE, number=4,
            open_=0, high=2, low=-4, close=2,
            high_at=high_at_b, low_at=low_at_b, high_order=20, low_order=19,
            buy=6, sell=4, unknown=0, prints=3,
            priced_volume=3, sum_price_volume=42, sum_price_squared_volume=588,
            first_priced=14, last_priced=14, price_high=14, price_low=14,
            price_high_at=high_at_b, price_low_at=low_at_b,
        )
        observations = observation_rows_to_table(self.five_minute_atoms([atom_a, atom_b]))
        result = self.build(observations, trade_table([]))
        row = feature_at(result['features'], cut_ns=self.cut, minutes=5)
        self.assertTrue(row['atoms_complete'])
        self.assertEqual((row['all__open'], row['all__high'], row['all__low'], row['all__close']), (0, 5, -3, 3))
        self.assertEqual(row['all__high_at_ns'], high_at_a)
        self.assertEqual(row['all__low_at_ns'], low_at_b)
        self.assertNotEqual(row['all__high_at_ns'], close_at_a)
        self.assertNotEqual(row['all__low_at_ns'], close_at_b)
        naive_close_high = max(1, 2)
        naive_unoffset_low = min(-2, -4)
        self.assertNotEqual(row['all__high'], naive_close_high)
        self.assertNotEqual(row['all__low'], naive_unoffset_low)
        self.assertEqual(row['known_at_ns'], self.cut + SOURCE_LATENCY_NS)
        self.assertEqual(row['event_start_ns'], self.cut - 5 * MINUTE)
        self.assertEqual(row['event_end_ns'], self.cut)

    def test_vwap_uses_summed_moments_not_average_of_prices(self):
        # q1@10 and q3@14: (1*10 + 3*14) / 4 = 13, not (10+14)/2 = 12.
        a_start = self.cut - 2 * MINUTE
        b_start = self.cut - MINUTE
        atom_a = path_atom(
            start=a_start, end=a_start + MINUTE, number=3,
            open_=0, high=0, low=0, close=0,
            high_at=a_start + 1, low_at=a_start + 1, high_order=1, low_order=1,
            buy=1, sell=0, unknown=0, prints=1,
            priced_volume=1, sum_price_volume=10, sum_price_squared_volume=100,
            first_priced=10, last_priced=10, price_high=10, price_low=10,
            price_high_at=a_start + 1, price_low_at=a_start + 1,
        )
        atom_b = path_atom(
            start=b_start, end=b_start + MINUTE, number=4,
            open_=0, high=0, low=0, close=0,
            high_at=b_start + 1, low_at=b_start + 1, high_order=2, low_order=2,
            buy=3, sell=0, unknown=0, prints=3,
            priced_volume=3, sum_price_volume=42, sum_price_squared_volume=588,
            first_priced=14, last_priced=14, price_high=14, price_low=14,
            price_high_at=b_start + 1, price_low_at=b_start + 1,
        )
        observations = observation_rows_to_table(self.five_minute_atoms([atom_a, atom_b]))
        result = self.build(observations, trade_table([]))
        row = feature_at(result['features'], cut_ns=self.cut, minutes=5)
        self.assertEqual(row['priced_volume'], 4)
        self.assertEqual(row['sum_price_volume'], 52)
        self.assertEqual(row['sum_price_squared_volume'], 688)
        self.assertEqual(row['vwap_ticks'], 13.0)
        self.assertNotEqual(row['vwap_ticks'], 12.0)
        self.assertEqual(row['variance_ticks_squared'], 3.0)
        self.assertEqual(row['reference_price_ticks'], 14)

    def test_label_half_open_membership_and_latency_starts(self):
        atoms = [quiet_atom(start=self.cut - (5 - i) * MINUTE, end=self.cut - (4 - i) * MINUTE, number=i)
                 for i in range(5)]
        trades = trade_table([
            trade_row(self.cut - 1, source_order=1, price=9, size=1, side=1),
            trade_row(self.cut, source_order=2, price=11, size=2, side=1),
            trade_row(self.cut + SOURCE_LATENCY_NS, source_order=3, price=12, size=2, side=-1),
            trade_row(self.cut + 1_000_000_000, source_order=4, price=13, size=3, side=0, raw_side='N'),
            trade_row(self.cut + 5 * MINUTE, source_order=5, price=99, size=8, side=1),
        ])
        original = trades['known_at_ns'].to_pylist()
        original_events = trades['t'].to_pylist()
        result = self.build(observation_rows_to_table(atoms), trades)
        self.assertEqual(trades['known_at_ns'].to_pylist(), original)
        self.assertEqual(trades['t'].to_pylist(), original_events)
        feature = feature_at(result['features'], cut_ns=self.cut, minutes=5)
        self.assertEqual(feature['event_end_ns'], self.cut)
        self.assertTrue(feature['empty_observed_window'])
        zero = label_at(result['labels'], cut_ns=self.cut, latency_ns=0,
                        horizon_kind='fixed_minutes', horizon_minutes=5)
        mid = label_at(result['labels'], cut_ns=self.cut, latency_ns=SOURCE_LATENCY_NS,
                       horizon_kind='fixed_minutes', horizon_minutes=5)
        late = label_at(result['labels'], cut_ns=self.cut, latency_ns=1_000_000_000,
                        horizon_kind='fixed_minutes', horizon_minutes=5)
        self.assertEqual(zero['event_start_ns'], self.cut)
        self.assertEqual(mid['event_start_ns'], self.cut + SOURCE_LATENCY_NS)
        self.assertEqual(late['event_start_ns'], self.cut + 1_000_000_000)
        self.assertEqual(zero['event_end_ns'], self.cut + 5 * MINUTE)
        # Independent membership: [start, end) on event time.
        # 0ms includes event==cut and event==cut+250ms and event==cut+1s; excludes cut-1 and end.
        self.assertEqual(zero['prints'], 3)
        self.assertEqual(zero['first_priced_ticks'], 11)
        self.assertEqual(zero['last_priced_ticks'], 13)
        self.assertEqual(zero['first_priced_known_at_ns'], self.cut + 0)
        self.assertEqual(zero['unknown'], 3)
        self.assertEqual(zero['buy'], 2)
        self.assertEqual(zero['sell'], 2)
        self.assertFalse(zero['no_new_trade'])
        # 250ms excludes event==cut; includes 250ms and 1s.
        self.assertEqual(mid['prints'], 2)
        self.assertEqual(mid['first_priced_ticks'], 12)
        self.assertEqual(mid['first_priced_known_at_ns'], self.cut + SOURCE_LATENCY_NS + SOURCE_LATENCY_NS)
        # 1000ms includes only the 1s trade.
        self.assertEqual(late['prints'], 1)
        self.assertEqual(late['first_priced_ticks'], 13)
        self.assertEqual(late['unknown'], 3)
        self.assertEqual(late['buy'], 0)
        self.assertEqual(late['sell'], 0)
        self.assertEqual(result['validation']['stored_known_at_matches_source_250ms'], True)
        self.assertTrue(result['validation']['original_trade_times_unchanged'])

    def test_unknown_side_is_not_classified_as_buy_or_sell(self):
        atoms = [quiet_atom(start=self.cut - (5 - i) * MINUTE, end=self.cut - (4 - i) * MINUTE, number=i)
                 for i in range(5)]
        trades = trade_table([
            trade_row(self.cut + 5, source_order=1, price=10, size=7, side=0, raw_side='N'),
        ])
        result = self.build(observation_rows_to_table(atoms), trades)
        row = label_at(result['labels'], cut_ns=self.cut, latency_ns=0,
                       horizon_kind='fixed_minutes', horizon_minutes=5)
        self.assertEqual(row['unknown'], 7)
        self.assertEqual(row['buy'], 0)
        self.assertEqual(row['sell'], 0)
        self.assertEqual(row['signed_close'], 0)
        self.assertEqual(row['all__unknown'], 7)
        self.assertEqual(row['all__close'], 0)

    def test_missing_atom_is_null_not_zero_and_quiet_is_zero(self):
        missing = [quiet_atom(start=self.cut - (5 - i) * MINUTE, end=self.cut - (4 - i) * MINUTE, number=i)
                   for i in (0, 1, 2, 4)]
        result = self.build(observation_rows_to_table(missing), trade_table([]))
        incomplete = feature_at(result['features'], cut_ns=self.cut, minutes=5)
        self.assertFalse(incomplete['atoms_complete'])
        self.assertIsNone(incomplete['prints'])
        self.assertIsNone(incomplete['all__buy'])
        self.assertIsNone(incomplete['vwap_ticks'])
        self.assertTrue(incomplete['left_censored'] or incomplete['right_censored']
                        or incomplete['censor_reason'])
        quiet = [quiet_atom(start=self.cut - (5 - i) * MINUTE, end=self.cut - (4 - i) * MINUTE, number=i)
                 for i in range(5)]
        covered = self.build(observation_rows_to_table(quiet), trade_table([]))
        row = feature_at(covered['features'], cut_ns=self.cut, minutes=5)
        self.assertTrue(row['atoms_complete'])
        self.assertTrue(row['empty_observed_window'])
        self.assertEqual(row['prints'], 0)
        self.assertEqual(row['all__buy'], 0)
        self.assertEqual(row['all__close'], 0)
        self.assertIsNone(row['reference_price_ticks'])
        self.assertIsNone(row['vwap_ticks'])

    def test_right_future_endpoint_returns_observed_fields_but_incomplete(self):
        atoms = [quiet_atom(start=self.cut - (5 - i) * MINUTE, end=self.cut - (4 - i) * MINUTE, number=i)
                 for i in range(5)]
        identity = source_identity(start=0, end=self.cut + 2 * MINUTE)
        trades = trade_table([
            trade_row(self.cut + 10, source_order=1, price=21, size=4, side=1),
        ])
        result = self.build(observation_rows_to_table(atoms), trades, identity=identity)
        row = label_at(result['labels'], cut_ns=self.cut, latency_ns=0,
                       horizon_kind='fixed_minutes', horizon_minutes=5)
        self.assertFalse(row['complete'])
        self.assertTrue(row['right_censored'])
        self.assertEqual(row['prints'], 1)
        self.assertEqual(row['first_priced_ticks'], 21)
        self.assertIn('right_future_endpoint', row['censor_reason'])

    def test_mixed_instrument_is_not_joined(self):
        start = self.cut - 5 * MINUTE
        rows = []
        for instrument_id, close in ((7, 3), (8, -9)):
            for i in range(4):
                a = start + i * MINUTE
                rows.append(quiet_atom(start=a, end=a + MINUTE, number=i, instrument_id=instrument_id))
            rows.append(path_atom(
                start=self.cut - MINUTE, end=self.cut, number=4, instrument_id=instrument_id,
                open_=0, high=close, low=close, close=close,
                high_at=self.cut - 10, low_at=self.cut - 10, high_order=instrument_id, low_order=instrument_id,
                buy=instrument_id, sell=0, unknown=0, prints=1,
                priced_volume=1, sum_price_volume=instrument_id, sum_price_squared_volume=instrument_id * instrument_id,
                first_priced=instrument_id, last_priced=instrument_id, price_high=instrument_id, price_low=instrument_id,
                price_high_at=self.cut - 10, price_low_at=self.cut - 10,
            ))
        trades = trade_table([
            trade_row(self.cut + 1, source_order=1, price=70, size=2, side=1, instrument_id=7),
            trade_row(self.cut + 2, source_order=2, price=80, size=5, side=-1, instrument_id=8),
        ])
        result = self.build(observation_rows_to_table(rows), trades)
        seven = feature_at(result['features'], cut_ns=self.cut, minutes=5, instrument_id=7)
        eight = feature_at(result['features'], cut_ns=self.cut, minutes=5, instrument_id=8)
        self.assertEqual(seven['all__close'], 3)
        self.assertEqual(eight['all__close'], -9)
        self.assertNotEqual(seven['all__close'], eight['all__close'])
        self.assertEqual(seven['all__buy'], 7)
        self.assertEqual(eight['all__buy'], 8)
        label7 = label_at(result['labels'], cut_ns=self.cut, latency_ns=0,
                          horizon_kind='fixed_minutes', horizon_minutes=5, instrument_id=7)
        label8 = label_at(result['labels'], cut_ns=self.cut, latency_ns=0,
                          horizon_kind='fixed_minutes', horizon_minutes=5, instrument_id=8)
        self.assertEqual(label7['prints'], 1)
        self.assertEqual(label7['first_priced_ticks'], 70)
        self.assertEqual(label7['buy'], 2)
        self.assertEqual(label8['prints'], 1)
        self.assertEqual(label8['first_priced_ticks'], 80)
        self.assertEqual(label8['sell'], 5)

    def test_mixed_contract_is_not_joined(self):
        start = self.cut - 5 * MINUTE
        rows = []
        for i in range(4):
            a = start + i * MINUTE
            rows.append(quiet_atom(start=a, end=a + MINUTE, number=i, contract_key=CONTRACT_KEY))
        rows.append(quiet_atom(
            start=self.cut - MINUTE, end=self.cut, number=4, contract_key='NQ:NQM4:7:0:1000'))
        result = self.build(observation_rows_to_table(rows), trade_table([]))
        row = feature_at(result['features'], cut_ns=self.cut, minutes=5)
        self.assertTrue(row['contract_transition'])
        self.assertFalse(row['atoms_complete'])
        self.assertIsNone(row['all__close'])
        self.assertIsNone(row['prints'])

    def test_clocks_are_int64_and_not_float(self):
        atoms = [quiet_atom(start=self.cut - (5 - i) * MINUTE, end=self.cut - (4 - i) * MINUTE, number=i)
                 for i in range(5)]
        result = self.build(observation_rows_to_table(atoms), trade_table([]))
        row = feature_at(result['features'], cut_ns=self.cut, minutes=5)
        for name in ('cut_ns', 'event_start_ns', 'event_end_ns', 'known_at_ns'):
            self.assertIsInstance(row[name], int)
            self.assertNotIsInstance(row[name], float)
        self.assertEqual(row['known_at_ns'] - row['event_end_ns'], SOURCE_LATENCY_NS)
        for field in feature_schema():
            if field.name.endswith('_ns'):
                self.assertEqual(str(field.type), 'int64')

    def test_stage_boundary_is_unassigned_not_a_chosen_stage(self):
        cut = datetime_ns(datetime(2024, 1, 1, 0, 5, tzinfo=timezone.utc))
        self.assertEqual(cut % CUT_CADENCE_NS, 0)
        identity = source_identity(start=cut - 240 * MINUTE, end=cut + 60 * MINUTE)
        atoms = [quiet_atom(start=cut - (5 - i) * MINUTE, end=cut - (4 - i) * MINUTE, number=i)
                 for i in range(5)]
        result = self.build(
            observation_rows_to_table(atoms), trade_table([]),
            identity=identity, cut_start=cut, cut_end=cut + CUT_CADENCE_NS,
        )
        long_feature = feature_at(result['features'], cut_ns=cut, minutes=240)
        self.assertEqual(long_feature['stage'], 'unassigned')
        self.assertTrue(long_feature['stage_boundary'])
        self.assertEqual(long_feature['event_start_ns'], cut - 240 * MINUTE)
        five = feature_at(result['features'], cut_ns=cut, minutes=5)
        self.assertEqual(five['event_start_ns'], datetime_ns(datetime(2024, 1, 1, tzinfo=timezone.utc)))
        self.assertEqual(five['stage'], 'calibration')
        self.assertFalse(five['stage_boundary'])

    def test_ny_dst_and_early_close_use_actual_calendar(self):
        calendar = self.calendar
        winter_open = local_timestamp(date(2024, 1, 8), time(9, 30), calendar.zone)
        winter_close = local_timestamp(date(2024, 1, 8), time(16, 0), calendar.zone)
        dst_open = local_timestamp(date(2024, 3, 11), time(9, 30), calendar.zone)
        dst_close = local_timestamp(date(2024, 3, 11), time(16, 0), calendar.zone)
        early_close = local_timestamp(date(2024, 11, 29), time(13, 0), calendar.zone)
        early_open = local_timestamp(date(2024, 11, 29), time(9, 30), calendar.zone)
        self.assertEqual(winter_open - winter_close, dst_open - dst_close)
        self.assertNotEqual(winter_open, dst_open)
        self.assertEqual(early_close - early_open, 3 * 60 * MINUTE)
        winter_cut = winter_open + 30 * MINUTE
        self.assertEqual(winter_cut % CUT_CADENCE_NS, 0)
        dst_cut = dst_open + 30 * MINUTE
        early_cut = early_open + 30 * MINUTE
        after_early = early_close + 30 * MINUTE
        thanksgiving = local_timestamp(date(2024, 11, 28), time(12, 0), calendar.zone)
        for cut, expected_end, applicable in (
            (winter_cut, winter_close, True),
            (dst_cut, dst_close, True),
            (early_cut, early_close, True),
        ):
            identity = source_identity(start=cut - 240 * MINUTE, end=cut + 8 * 60 * MINUTE)
            atoms = [quiet_atom(start=cut - (5 - i) * MINUTE, end=cut - (4 - i) * MINUTE, number=i)
                     for i in range(5)]
            result = self.build(
                observation_rows_to_table(atoms), trade_table([]),
                identity=identity, cut_start=cut, cut_end=cut + CUT_CADENCE_NS,
            )
            row = label_at(result['labels'], cut_ns=cut, latency_ns=0,
                           horizon_kind='remaining_session')
            self.assertTrue(row['remaining_session_applicable'])
            self.assertIsNone(row['remaining_session_disposition'])
            self.assertEqual(row['event_end_ns'], expected_end)
            self.assertEqual(row['event_start_ns'], cut)
            self.assertEqual(row['known_at_ns'], expected_end)
        for cut in (after_early, thanksgiving):
            aligned = cut - (cut % CUT_CADENCE_NS)
            identity = source_identity(start=aligned - 240 * MINUTE, end=aligned + 8 * 60 * MINUTE)
            atoms = [quiet_atom(start=aligned - (5 - i) * MINUTE,
                                end=aligned - (4 - i) * MINUTE, number=i)
                     for i in range(5)]
            result = self.build(
                observation_rows_to_table(atoms), trade_table([]),
                identity=identity, cut_start=aligned, cut_end=aligned + CUT_CADENCE_NS,
            )
            row = label_at(result['labels'], cut_ns=aligned, latency_ns=0,
                           horizon_kind='remaining_session')
            self.assertFalse(row['remaining_session_applicable'])
            self.assertIsNotNone(row['remaining_session_disposition'])
            self.assertIsNone(row['event_end_ns'])
            self.assertNotEqual(row['remaining_session_disposition'], 'regular')

    def test_duration_means_are_standing_weighted_not_atom_averaged(self):
        a_start = self.cut - 2 * MINUTE
        b_start = self.cut - MINUTE
        atom_a = path_atom(
            start=a_start, end=a_start + MINUTE, number=3,
            open_=0, high=0, low=0, close=0,
            high_at=a_start + 1, low_at=a_start + 1, high_order=1, low_order=1,
            buy=0, sell=0, unknown=0, prints=0,
            priced_volume=0, sum_price_volume=0, sum_price_squared_volume=0,
            first_priced=10, last_priced=10, price_high=10, price_low=10,
            price_high_at=a_start + 1, price_low_at=a_start + 1,
            standing_ns=10, duration_spread=2.0, duration_imbalance=0.1,
            pressure=True, ofi=(0, 1, -1, 0),
        )
        atom_a['empty_observed_window'] = True
        atom_b = path_atom(
            start=b_start, end=b_start + MINUTE, number=4,
            open_=0, high=0, low=0, close=0,
            high_at=b_start + 1, low_at=b_start + 1, high_order=2, low_order=2,
            buy=0, sell=0, unknown=0, prints=0,
            priced_volume=0, sum_price_volume=0, sum_price_squared_volume=0,
            first_priced=10, last_priced=10, price_high=10, price_low=10,
            price_high_at=b_start + 1, price_low_at=b_start + 1,
            standing_ns=30, duration_spread=4.0, duration_imbalance=0.5,
            pressure=True, ofi=(0, 2, -3, 1),
        )
        atom_b['empty_observed_window'] = True
        rows = self.five_minute_atoms([atom_a, atom_b])
        for row in rows:
            row['full_pressure_transition_window_eligible'] = True
            row['full_standing_window_eligible'] = True
            if row['ofi_open'] is None:
                row['ofi_open'] = 0
                row['ofi_high'] = 0
                row['ofi_low'] = 0
                row['ofi_close'] = 0
        observations = observation_rows_to_table(rows)
        result = self.build(observations, trade_table([]))
        row = feature_at(result['features'], cut_ns=self.cut, minutes=5)
        # (2*10 + 4*30) / 40 = 3.5, not (2+4)/2 = 3.
        self.assertEqual(row['duration_mean_spread_ticks'], 3.5)
        self.assertEqual(row['duration_mean_imbalance'], (0.1 * 10 + 0.5 * 30) / 40)
        self.assertNotEqual(row['duration_mean_spread_ticks'], 3.0)
        # Independent OFI concat: 0-path atoms, then (0,1,-1,0), then (0,2,-3,1).
        self.assertEqual((row['ofi_open'], row['ofi_high'], row['ofi_low'], row['ofi_close']), (0, 2, -3, 1))

    def test_no_future_trades_sets_no_new_trade_and_null_prices(self):
        atoms = [quiet_atom(start=self.cut - (5 - i) * MINUTE, end=self.cut - (4 - i) * MINUTE, number=i)
                 for i in range(5)]
        result = self.build(observation_rows_to_table(atoms), trade_table([]))
        row = label_at(result['labels'], cut_ns=self.cut, latency_ns=0,
                       horizon_kind='fixed_minutes', horizon_minutes=5)
        self.assertTrue(row['no_new_trade'])
        self.assertTrue(row['no_priced_trade'])
        self.assertIsNone(row['first_priced_ticks'])
        self.assertIsNone(row['observed_high_ticks'])
        self.assertEqual(row['prints'], 0)
        self.assertTrue(row['complete'])


if __name__ == '__main__':
    unittest.main()
