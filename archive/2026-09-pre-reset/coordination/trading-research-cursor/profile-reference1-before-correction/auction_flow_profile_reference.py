"""Exact profile/TPO/VWAP/footprint reconstruction from retained atoms.

This helper extracts original ``trade.sparse_profile`` cells once per source
unit, reuses observation clocks/coverage/moments, and emits compact typed
geometry. It does not fit Context, score Locations, replay tape, or spawn
workers. Root owns definitions, protocol, runner, execution and review.
"""
from __future__ import annotations

from collections import defaultdict, deque
from datetime import date, datetime, time, timedelta, timezone
from fractions import Fraction
from types import SimpleNamespace
from zoneinfo import ZoneInfo
import json
import math
import time as time_mod

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.measurements.footprint import imbalance_rows, stacked_imbalances
from trading_research.measurements.profiles import (
    FrozenGrid, ProfileCell, ProfileDefinition, bar_allocation_rows,
    profile_geometry_rows, side_geometry_rows, transform_profile_rows,
)
from trading_research.measurements.vwap import weighted_quantile
from trading_research.operations.artifacts import digest
from trading_research.research.auction_flow_anchor_tpo import (
    BRACKET_MINUTES, IB_MINUTES, AnchorTPO,
)
from trading_research.research.auction_flow_anchor_trades import AtomicTrades
from trading_research.research.auction_flow_anchors import (
    AuctionAnchor, MINUTE_NS as ANCHOR_MINUTE_NS, named_clock_anchors, rolling_anchor,
)
from trading_research.research.auction_flow_core_statistics import (
    ExplicitCashSessions, economic_date, stage_name,
)
from trading_research.research.auction_flow_measurements import SparseSideMass
from trading_research.research.auction_flow_profiles import (
    MassView, SideCell, footprint_geometry, geometry, shape_distance,
    side_geometry, transform_mass, view_sparse,
)
from trading_research.research.auction_flow_storage import (
    BoundedOutputs, ParquetSeries, read_json_artifact, read_series_tables,
)


VERSION = 'auction-flow-profile-reference-v1'
KIND = 'auction_flow_profile_reference_partition_v1'
FROZEN_CONTRACT_KIND = 'auction_flow_profile_reference_statistics_contract_v1'
POPULATION_KIND = 'auction_flow_observation_population_v1'
WINDOW_POPULATION_KIND = 'auction_flow_window_population_v1'
UNIT_KIND = 'auction_flow_observation_unit_v1'
ZONE = 'America/New_York'
NS = 1_000_000_000
MINUTE_NS = 60 * NS
CUT_STRIDE_NS = 5 * MINUTE_NS
TICK_INDEX_POINTS = 0.25
SOURCE_LATENCY_NS = 250_000_000
LATENCY_NS = (0, 250_000_000, 1_000_000_000)
FORWARD_HORIZONS_MINUTES = (5, 15, 60)
HORIZON_KINDS = ('fixed_minutes', 'remaining_session')
ROLLING_MINUTES = (5, 15, 60, 240)
QUANTILE_LEVELS = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
BATCH_HINT = 65536
JSON_LOAD_MAX = 128 * 1024 ** 2
DEFAULT_PRICE_CELLS = 250000
MAXIMUM_FIXED_ATOMS = 1_000_000
MAXIMUM_ROLLING_ATOMS = 20000
TICK_SIZE_QUARTER = Fraction(1, 4)
MAD_SCALE = Fraction(7413, 5000)
VWAP_PERCENT_BANDS = (Fraction(1, 100), Fraction(1, 40), Fraction(3, 100))
VWAP_SD_BANDS = (Fraction(1), Fraction(2), Fraction(5, 2), Fraction(3))
VWAP_QUANTILES = (
    Fraction(1, 20), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(19, 20),
)
FOOTPRINT_DEFAULTS = {
    'ratio': Fraction(3),
    'minimum_volume': 1,
    'comparison': 'diagonal',
    'zero_opponent': 'require_observed_opponent',
    'minimum_stack_rows': 2,
}
BASELINE_VARIANT_ID = 'source-one-tick-value-7/10'
DEVELOPING_VARIANTS = ('developing_cash_rth', 'developing_observed_futures_18_17')
FIXED_CLOCK_IDS = (
    'cash_rth', 'prior_cash_rth', 'observed_futures_18_17', 'overnight_18_0930',
    'morning_06_09_ny', 'source_06_09_fixed_utc_minus4',
    'source_monday_22_21_utc', 'source_tuesday_22_21_utc',
)
CIVIL_KINDS = ('week', 'month', 'quarter', 'year')
BAR_PROXY_VARIANTS = (
    'equal_inclusive_rows', 'continuous_overlap', 'pin066_source',
    'pin066_corrected', 'close', 'hlc3',
)
FROZEN_GEOMETRY_VARIANTS = (
    {
        'id': 'source-one-tick-value-17/25', 'fraction': (17, 25), 'origin': 0,
        'poc_tie': 'lower', 'smoothing_scale': 0, 'value_tie': 'upper', 'width': 1,
    },
    {
        'id': 'source-one-tick-value-7/10', 'fraction': (7, 10), 'origin': 0,
        'poc_tie': 'lower', 'smoothing_scale': 0, 'value_tie': 'upper', 'width': 1,
    },
    {
        'id': 'value70-expansion-tie-lower', 'fraction': (7, 10), 'origin': 0,
        'poc_tie': 'lower', 'smoothing_scale': 0, 'value_tie': 'lower', 'width': 1,
    },
    {
        'id': 'value70-expansion-tie-both', 'fraction': (7, 10), 'origin': 0,
        'poc_tie': 'lower', 'smoothing_scale': 0, 'value_tie': 'both', 'width': 1,
    },
    {
        'id': 'value70-poc-tie-upper', 'fraction': (7, 10), 'origin': 0,
        'poc_tie': 'upper', 'smoothing_scale': 0, 'value_tie': 'upper', 'width': 1,
    },
    {
        'id': 'value70-width2-origin0', 'fraction': (7, 10), 'origin': 0,
        'poc_tie': 'lower', 'smoothing_scale': 0, 'value_tie': 'upper', 'width': 2,
    },
    {
        'id': 'value70-width2-origin1', 'fraction': (7, 10), 'origin': 1,
        'poc_tie': 'lower', 'smoothing_scale': 0, 'value_tie': 'upper', 'width': 2,
    },
    {
        'id': 'value70-width4-origin0', 'fraction': (7, 10), 'origin': 0,
        'poc_tie': 'lower', 'smoothing_scale': 0, 'value_tie': 'upper', 'width': 4,
    },
    {
        'id': 'value70-width4-origin1', 'fraction': (7, 10), 'origin': 1,
        'poc_tie': 'lower', 'smoothing_scale': 0, 'value_tie': 'upper', 'width': 4,
    },
    {
        'id': 'value70-width8-origin0', 'fraction': (7, 10), 'origin': 0,
        'poc_tie': 'lower', 'smoothing_scale': 0, 'value_tie': 'upper', 'width': 8,
    },
    {
        'id': 'value70-width8-origin1', 'fraction': (7, 10), 'origin': 1,
        'poc_tie': 'lower', 'smoothing_scale': 0, 'value_tie': 'upper', 'width': 8,
    },
    {
        'id': 'value70-triangular-scale1', 'fraction': (7, 10), 'origin': 0,
        'poc_tie': 'lower', 'smoothing_scale': 1, 'value_tie': 'upper', 'width': 1,
    },
    {
        'id': 'value70-triangular-scale2', 'fraction': (7, 10), 'origin': 0,
        'poc_tie': 'lower', 'smoothing_scale': 2, 'value_tie': 'upper', 'width': 1,
    },
    {
        'id': 'value70-triangular-scale4', 'fraction': (7, 10), 'origin': 0,
        'poc_tie': 'lower', 'smoothing_scale': 4, 'value_tie': 'upper', 'width': 1,
    },
)
_INT64_MIN = -(2 ** 63)
_INT64_MAX = 2 ** 63 - 1
_SHA_LEN = 64
_GEOMETRY_LIST_FIELDS = (
    'poc_set', 'value_rows', 'maximum_plateau_lows', 'maximum_plateau_highs',
    'peak_lows', 'peak_highs', 'valley_lows', 'valley_highs',
    'delta_maximum_rows', 'delta_minimum_rows', 'absolute_peak_rows',
)
_TPO_LIST_FIELDS = (
    'provisional_single_print_rows', 'final_single_print_rows',
    'legacy_five_bracket_final_single_print_rows', 'low_tail_rows', 'high_tail_rows',
    'visit_rows', 'range_proxy_rows',
)


def _mapping(value, *, what):
    if not isinstance(value, dict):
        raise IntegrityError(f'{what} must be an object')
    return value


def _text(value, *, what, allow_empty=False):
    if type(value) is not str or (not value and not allow_empty):
        raise IntegrityError(f'{what} must be a concrete string')
    return value


def _py_int(value, *, what, minimum=None, maximum=None):
    if value is None:
        return None
    if type(value) is bool:
        raise IntegrityError(f'{what} must be an exact integer')
    result = int(value)
    if result != value:
        raise IntegrityError(f'{what} lost exact integer identity')
    if not _INT64_MIN <= result <= _INT64_MAX:
        raise IntegrityError(f'{what} exceeds the exact int64 domain')
    if minimum is not None and result < minimum:
        raise IntegrityError(f'{what} is below its bound')
    if maximum is not None and result > maximum:
        raise IntegrityError(f'{what} exceeds its bound')
    return result


def _bool(value, *, what):
    if type(value) is not bool:
        raise IntegrityError(f'{what} must be an explicit boolean')
    return value


def _require_numpy():
    import numpy as np
    if getattr(np, '__version__', None) != '2.3.3':
        raise ContractError('profile reference requires the pinned NumPy 2.3.3 provider')
    return np


def _require_pyarrow():
    import pyarrow as pa
    if getattr(pa, '__version__', None) != '25.0.1':
        raise ContractError('profile reference requires the pinned PyArrow 25.0.1 provider')
    return pa


def _fraction_pair(value):
    if value is None:
        return None, None
    if type(value) is Fraction:
        return int(value.numerator), int(value.denominator)
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return _py_int(value[0], what='fraction.numerator'), _py_int(value[1], what='fraction.denominator')
    raise IntegrityError('exact fraction must be a Fraction or [numerator, denominator]')


def _json_list(values):
    if values is None:
        return None
    return [int(v) if type(v) is not bool and isinstance(v, int) else v for v in values]


def variant_definition(spec):
    rec = spec if isinstance(spec, dict) else next(
        item for item in FROZEN_GEOMETRY_VARIANTS if item['id'] == spec)
    numer, denom = rec['fraction']
    return ProfileDefinition(
        rec['id'],
        value_fraction=Fraction(int(numer), int(denom)),
        poc_tie=rec['poc_tie'],
        value_tie=rec['value_tie'],
    )


def frozen_variant_ids():
    return tuple(item['id'] for item in FROZEN_GEOMETRY_VARIANTS)


def require_frozen_variants(contract):
    declared = contract.get('geometry_variants')
    if not isinstance(declared, (list, tuple)) or len(declared) != len(FROZEN_GEOMETRY_VARIANTS):
        raise IntegrityError('frozen contract requires all 14 named completed geometry variants')
    for expected, got in zip(FROZEN_GEOMETRY_VARIANTS, declared):
        if not isinstance(got, dict):
            raise IntegrityError('geometry variant must be an object')
        for key in ('id', 'origin', 'poc_tie', 'smoothing_scale', 'value_tie', 'width'):
            if got.get(key) != expected[key]:
                raise IntegrityError(f'frozen geometry variant {expected["id"]} changed {key}')
        if tuple(got.get('fraction') or ()) != expected['fraction']:
            raise IntegrityError(f'frozen geometry variant {expected["id"]} changed fraction')
    proxies = contract.get('bar_proxy_variants')
    if list(proxies or ()) != list(BAR_PROXY_VARIANTS):
        raise IntegrityError('frozen contract requires all 6 named bar-proxy variants')
    return tuple(FROZEN_GEOMETRY_VARIANTS)


def footprint_parameters(contract):
    raw = contract.get('footprint') if isinstance(contract, dict) else None
    if not raw:
        return dict(FOOTPRINT_DEFAULTS)
    rec = _mapping(raw, what='footprint')
    ratio = rec.get('ratio', FOOTPRINT_DEFAULTS['ratio'])
    if isinstance(ratio, (list, tuple)) and len(ratio) == 2:
        ratio = Fraction(int(ratio[0]), int(ratio[1]))
    elif type(ratio) is int:
        ratio = Fraction(ratio)
    if type(ratio) is not Fraction:
        raise IntegrityError('footprint.ratio must be an exact fraction')
    out = {
        'ratio': ratio,
        'minimum_volume': int(rec.get('minimum_volume', FOOTPRINT_DEFAULTS['minimum_volume'])),
        'comparison': rec.get('comparison', FOOTPRINT_DEFAULTS['comparison']),
        'zero_opponent': rec.get('zero_opponent', FOOTPRINT_DEFAULTS['zero_opponent']),
        'minimum_stack_rows': int(rec.get('minimum_stack_rows', FOOTPRINT_DEFAULTS['minimum_stack_rows'])),
    }
    if out['comparison'] not in ('diagonal', 'same_price'):
        raise IntegrityError('footprint comparison must be diagonal or same_price')
    if out['zero_opponent'] not in ('require_observed_opponent', 'infinite_if_minimum'):
        raise IntegrityError('footprint zero_opponent is not a registered rule')
    return out


class ProfileCashAdapter:
    """Fixture/production calendar with the fields named_clock_anchors reads."""

    def __init__(self, inner):
        self.inner = inner
        self.reference = getattr(inner, 'reference', None)

    def resolve(self, day, *, cut):
        raw = self.inner.resolve(day, cut=cut)
        if getattr(raw, 'version', None) is not None and getattr(raw, 'known_at', None) is not None:
            return raw
        version = digest({
            'kind': 'profile_fixture_cash_session',
            'date': day.isoformat(),
            'state': raw.state,
            'open_at': raw.open_at,
            'close_at': raw.close_at,
        })
        return SimpleNamespace(
            state=raw.state, open_at=raw.open_at, close_at=raw.close_at,
            known_at=getattr(raw, 'known_at', cut), version=version,
        )


def extract_sparse_profile(profile):
    """Return ordered [row, buy, sell, unknown] cells plus unpriced/total."""
    rec = _mapping(profile, what='sparse_profile')
    rows = rec.get('rows')
    if not isinstance(rows, (list, tuple)):
        raise IntegrityError('sparse_profile.rows must be the published ordered cells')
    cells = []
    priced = [0, 0, 0]
    previous = None
    for index, row in enumerate(rows):
        if not isinstance(row, (list, tuple)) or len(row) != 4:
            raise IntegrityError('sparse profile cell must be [row, buy, sell, unknown]')
        price = _py_int(row[0], what=f'sparse_profile.rows[{index}].row')
        sides = [
            _py_int(row[j], what=f'sparse_profile.rows[{index}].side', minimum=0)
            for j in (1, 2, 3)
        ]
        if previous is not None and price <= previous:
            raise IntegrityError('sparse profile rows must be distinct and ordered')
        previous = price
        for j in range(3):
            priced[j] += sides[j]
        cells.append((price, sides[0], sides[1], sides[2]))
    unpriced = rec.get('unpriced_buy_sell_unknown') or (0, 0, 0)
    if not isinstance(unpriced, (list, tuple)) or len(unpriced) != 3:
        raise IntegrityError('unpriced_buy_sell_unknown must be a 3-tuple')
    unpriced = tuple(_py_int(v, what='unpriced', minimum=0) for v in unpriced)
    priced_volume = priced[0] + priced[1] + priced[2]
    total = rec.get('total_volume')
    if total is not None and _py_int(total, what='sparse_profile.total_volume') != priced_volume + sum(unpriced):
        raise IntegrityError('sparse profile priced, unpriced and total mass do not reconcile')
    return {
        'row_ticks': _py_int(rec.get('row_ticks', 1), what='row_ticks', minimum=1) or 1,
        'origin_ticks': _py_int(rec.get('origin_ticks', 0), what='origin_ticks') or 0,
        'rows': tuple(cells),
        'unpriced': unpriced,
        'priced_buy': priced[0],
        'priced_sell': priced[1],
        'priced_unknown': priced[2],
        'priced_volume': priced_volume,
        'total_volume': priced_volume + sum(unpriced),
    }


def extract_unit_cells(measured):
    """Walk one accepted measurement payload and yield compact atom cells."""
    payload = _mapping(measured, what='measured')
    status = payload.get('status')
    if status == 'unavailable_source_window':
        return {
            'status': status,
            'reason': payload.get('unavailable_reason') or 'unavailable_source_window',
            'atoms': (),
            'root': payload.get('root'),
            'event_start_ns': payload.get('event_start_ns'),
            'event_end_ns': payload.get('event_end_ns'),
        }
    if status not in (None, 'measured'):
        raise IntegrityError('measurement status is not measured or unavailable')
    instruments = payload.get('instruments')
    if not isinstance(instruments, list):
        raise IntegrityError('measured source/day must retain its instrument list')
    width = _py_int(payload.get('atomic_width_ns', MINUTE_NS), what='atomic_width_ns', minimum=1)
    atoms = []
    for instrument in instruments:
        inst = _mapping(instrument, what='instrument')
        instrument_id = _py_int(inst.get('instrument_id'), what='instrument_id', minimum=1)
        windows = inst.get('atomic_windows')
        if not isinstance(windows, list):
            raise IntegrityError('instrument lost its atomic_windows')
        for item in windows:
            atom = _mapping(item, what='atomic_window')
            trade = _mapping(atom.get('trade'), what='atomic.trade')
            coordinate = atom.get('coordinate') if isinstance(atom.get('coordinate'), dict) else {}
            profile = extract_sparse_profile(trade.get('sparse_profile'))
            start = _py_int(atom.get('event_start_ns', trade.get('event_start_ns')), what='event_start_ns')
            end = _py_int(atom.get('event_end_ns', trade.get('event_end_ns')), what='event_end_ns')
            known = _py_int(atom.get('known_at_ns', trade.get('known_at_ns')), what='known_at_ns')
            if start is None or end is None or not start < end:
                raise IntegrityError('atom lost a positive half-open interval')
            contract_key = coordinate.get('contract_key')
            if contract_key is not None:
                contract_key = _text(contract_key, what='contract_key')
            atoms.append({
                'instrument_id': instrument_id,
                'contract_key': contract_key,
                'event_start_ns': start,
                'event_end_ns': end,
                'known_at_ns': known,
                'atomic_bin': _py_int(atom.get('bin', atom.get('atomic_bin')), what='atomic_bin'),
                'width_ns': width,
                'row_ticks': profile['row_ticks'],
                'origin_ticks': profile['origin_ticks'],
                'rows': profile['rows'],
                'unpriced': profile['unpriced'],
                'priced_buy': profile['priced_buy'],
                'priced_sell': profile['priced_sell'],
                'priced_unknown': profile['priced_unknown'],
                'priced_volume': profile['priced_volume'],
                'total_volume': profile['total_volume'],
                'coordinate_complete': bool(coordinate.get('complete', True)),
                'source_coverage_complete': bool(trade.get('source_coverage_complete', True)),
                'price_history_complete': bool(trade.get('price_history_complete', True)),
                'flow_history_complete': bool(trade.get('flow_history_complete', True)),
                'prints': _py_int(trade.get('prints'), what='prints', minimum=0) or 0,
                'unpriced_prints': _py_int(trade.get('unpriced_prints'), what='unpriced_prints', minimum=0) or 0,
                'first_priced_ticks': _py_int(trade.get('first_priced_ticks') or (
                    (trade.get('first_priced_trade') or {}).get('price_ticks')
                    if isinstance(trade.get('first_priced_trade'), dict) else None
                ), what='first_priced_ticks'),
                'last_priced_ticks': _py_int(trade.get('last_priced_ticks') or (
                    (trade.get('last_priced_trade') or {}).get('price_ticks')
                    if isinstance(trade.get('last_priced_trade'), dict) else None
                ), what='last_priced_ticks'),
                'observed_high_ticks': _py_int(trade.get('observed_high_ticks'), what='observed_high_ticks'),
                'observed_low_ticks': _py_int(trade.get('observed_low_ticks'), what='observed_low_ticks'),
                'first_priced_event_ns': _py_int(trade.get('first_priced_event_ns'), what='first_priced_event_ns'),
                'last_priced_event_ns': _py_int(trade.get('last_priced_event_ns'), what='last_priced_event_ns'),
                'first_priced_source_order': _py_int(
                    trade.get('first_priced_source_order'), what='first_priced_source_order'),
                'last_priced_source_order': _py_int(
                    trade.get('last_priced_source_order'), what='last_priced_source_order'),
                'sum_price_volume': _py_int(
                    (trade.get('weighted_price') or {}).get('sum_price_volume'),
                    what='sum_price_volume',
                ),
                'sum_price_squared_volume': _py_int(
                    (trade.get('weighted_price') or {}).get('sum_price_squared_volume'),
                    what='sum_price_squared_volume',
                ),
            })
    return {
        'status': 'measured',
        'reason': None,
        'atoms': tuple(atoms),
        'root': payload.get('root'),
        'event_start_ns': payload.get('event_start_ns'),
        'event_end_ns': payload.get('event_end_ns'),
        'known_at_ns': payload.get('known_at_ns'),
        'atomic_width_ns': width,
    }


def match_atom_identity(cell, observation):
    """Require per-atom side/total identity between measurement cells and obs39."""
    if observation is None:
        raise IntegrityError('measurement atom has no matching observation row')
    for name in (
        'instrument_id', 'event_start_ns', 'event_end_ns',
        'priced_buy', 'priced_sell', 'priced_unknown',
        'unpriced_buy', 'unpriced_sell', 'unpriced_unknown',
    ):
        left = cell.get(name if not name.startswith('unpriced_') else None)
        if name == 'unpriced_buy':
            left = cell['unpriced'][0]
        elif name == 'unpriced_sell':
            left = cell['unpriced'][1]
        elif name == 'unpriced_unknown':
            left = cell['unpriced'][2]
        else:
            left = cell.get(name)
        right = observation.get(name)
        if right is None and name in ('priced_buy', 'priced_sell', 'priced_unknown'):
            continue
        if left is None or right is None:
            if left != right:
                raise IntegrityError(f'atom {name} identity is missing on one side')
            continue
        if int(left) != int(right):
            raise IntegrityError(f'atom {name} does not match observation identity')
    if observation.get('priced_volume') is not None and int(observation['priced_volume']) != int(cell['priced_volume']):
        raise IntegrityError('atom priced_volume does not match observation identity')
    if observation.get('contract_key') not in (None, cell.get('contract_key')) and cell.get('contract_key') not in (
        None, observation.get('contract_key'),
    ):
        raise IntegrityError('atom contract_key does not match observation identity')
    return True


class IntegerMass:
    """Exact integer side histogram with add/remove. No per-atom Fraction objects."""

    __slots__ = (
        'buy', 'sell', 'unknown', 'unpriced', 'sum_q', 'sum_pq', 'sum_p2q',
        'row_ticks', 'origin_ticks', 'atom_count', 'prints', 'unpriced_prints',
        'coverage_complete', 'price_history_complete', 'coordinate_complete',
        'bars', 'source_paths',
    )

    def __init__(self, *, row_ticks=1, origin_ticks=0):
        self.buy = {}
        self.sell = {}
        self.unknown = {}
        self.unpriced = [0, 0, 0]
        self.sum_q = 0
        self.sum_pq = 0
        self.sum_p2q = 0
        self.row_ticks = int(row_ticks)
        self.origin_ticks = int(origin_ticks)
        self.atom_count = 0
        self.prints = 0
        self.unpriced_prints = 0
        self.coverage_complete = True
        self.price_history_complete = True
        self.coordinate_complete = True
        self.bars = []
        self.source_paths = set()

    def _price(self, row):
        return self.origin_ticks + int(row) * self.row_ticks

    def add(self, atom, *, signed=1):
        if signed not in (1, -1):
            raise ContractError('histogram update sign must be +1 or -1')
        for row, buy, sell, unknown in atom['rows']:
            price = self._price(row) if atom.get('row_ticks', 1) == self.row_ticks else int(row)
            if atom.get('origin_ticks', 0) != self.origin_ticks or atom.get('row_ticks', 1) != self.row_ticks:
                price = int(atom.get('origin_ticks', 0)) + int(row) * int(atom.get('row_ticks', 1))
            mass = int(buy) + int(sell) + int(unknown)
            if signed == 1:
                if buy:
                    self.buy[price] = self.buy.get(price, 0) + int(buy)
                if sell:
                    self.sell[price] = self.sell.get(price, 0) + int(sell)
                if unknown:
                    self.unknown[price] = self.unknown.get(price, 0) + int(unknown)
                self.sum_q += mass
                self.sum_pq += price * mass
                self.sum_p2q += price * price * mass
            else:
                if buy:
                    next_buy = self.buy.get(price, 0) - int(buy)
                    if next_buy < 0:
                        raise IntegrityError('histogram removal exceeded buy mass')
                    if next_buy:
                        self.buy[price] = next_buy
                    else:
                        self.buy.pop(price, None)
                if sell:
                    next_sell = self.sell.get(price, 0) - int(sell)
                    if next_sell < 0:
                        raise IntegrityError('histogram removal exceeded sell mass')
                    if next_sell:
                        self.sell[price] = next_sell
                    else:
                        self.sell.pop(price, None)
                if unknown:
                    next_unk = self.unknown.get(price, 0) - int(unknown)
                    if next_unk < 0:
                        raise IntegrityError('histogram removal exceeded unknown mass')
                    if next_unk:
                        self.unknown[price] = next_unk
                    else:
                        self.unknown.pop(price, None)
                self.sum_q -= mass
                self.sum_pq -= price * mass
                self.sum_p2q -= price * price * mass
        for index, amount in enumerate(atom['unpriced']):
            self.unpriced[index] += signed * int(amount)
            if self.unpriced[index] < 0:
                raise IntegrityError('histogram removal exceeded unpriced mass')
        self.atom_count += signed
        self.prints += signed * int(atom.get('prints') or 0)
        self.unpriced_prints += signed * int(atom.get('unpriced_prints') or 0)
        if signed == 1:
            if not atom.get('source_coverage_complete', True):
                self.coverage_complete = False
            if not atom.get('price_history_complete', True):
                self.price_history_complete = False
            if not atom.get('coordinate_complete', True):
                self.coordinate_complete = False
            path = atom.get('source_path')
            if path:
                self.source_paths.add(path)
            bar = atom_bar(atom)
            if bar is not None:
                self.bars.append(bar)
        elif atom_bar(atom) is not None and self.bars:
            self.bars.pop(0)

    def remove(self, atom):
        self.add(atom, signed=-1)

    def copy_flags_from(self, atoms):
        self.coverage_complete = all(atom.get('source_coverage_complete', True) for atom in atoms)
        self.price_history_complete = all(atom.get('price_history_complete', True) for atom in atoms)
        self.coordinate_complete = all(atom.get('coordinate_complete', True) for atom in atoms)

    @property
    def priced_volume(self):
        return self.sum_q

    @property
    def unpriced_volume(self):
        return self.unpriced[0] + self.unpriced[1] + self.unpriced[2]

    def prices(self):
        return sorted(set(self.buy) | set(self.sell) | set(self.unknown))

    def sides_at(self, price):
        return (
            int(self.buy.get(price, 0)),
            int(self.sell.get(price, 0)),
            int(self.unknown.get(price, 0)),
        )

    def vwap_moments(self):
        if self.sum_q <= 0:
            return {
                'priced_volume': 0, 'sum_price_volume': 0, 'sum_price_squared_volume': 0,
                'vwap_ticks': None, 'variance_ticks_squared': None,
            }
        mean = Fraction(self.sum_pq, self.sum_q)
        second = Fraction(self.sum_p2q, self.sum_q)
        return {
            'priced_volume': self.sum_q,
            'sum_price_volume': self.sum_pq,
            'sum_price_squared_volume': self.sum_p2q,
            'vwap_ticks': mean,
            'variance_ticks_squared': second - mean * mean,
        }


def atom_bar(atom):
    high = atom.get('observed_high_ticks')
    low = atom.get('observed_low_ticks')
    opened = atom.get('first_priced_ticks')
    close = atom.get('last_priced_ticks')
    volume = atom.get('priced_volume') or 0
    unpriced = sum(atom.get('unpriced') or (0, 0, 0))
    if high is None or low is None or opened is None or close is None:
        return None
    return (int(opened), int(high), int(low), int(close), int(volume), int(unpriced))


def sparse_from_mass(mass):
    sparse = SparseSideMass(row_ticks=1, origin_ticks=0, maximum_cells=DEFAULT_PRICE_CELLS)
    for price in mass.prices():
        buy, sell, unknown = mass.sides_at(price)
        if buy + sell + unknown == 0:
            continue
        if len(sparse.rows) >= sparse.maximum_cells:
            raise ContractError('profile exceeds its fixed cell capacity')
        sparse.rows[int(price)] = [int(buy), int(sell), int(unknown)]
    sparse.unpriced = [int(v) for v in mass.unpriced]
    sparse.total = int(mass.sum_q + mass.unpriced_volume)
    return sparse


def mass_view_from_histogram(mass, *, coordinate_identity, known_at_ns, width=1, origin=0,
                             coverage_complete=True):
    sparse = sparse_from_mass(mass)
    prices = mass.prices()
    if not prices and mass.sum_q == 0:
        raise ContractError('mass view requires a priced grid or an explicit null geometry path')
    if prices:
        raw_low = min(prices)
        raw_high = max(prices)
    else:
        raw_low = origin
        raw_high = origin
    grid = FrozenGrid(
        int(origin), int(width),
        (raw_low - int(origin)) // int(width),
        (raw_high - int(origin)) // int(width),
        f'{coordinate_identity}:w{width}:o{origin}',
        int(known_at_ns),
        max(DEFAULT_PRICE_CELLS, (raw_high - raw_low) // int(width) + 8),
    )
    return view_sparse(
        sparse, coordinate_identity=coordinate_identity, grid=grid,
        coverage_complete=coverage_complete,
    )


def apply_variant_view(view, spec):
    width = int(spec['width'])
    origin = int(spec['origin'])
    smooth = int(spec['smoothing_scale'])
    current = view
    if origin != current.grid.origin_ticks or width != current.grid.width_ticks:
        current = mass_view_from_histogram(
            _mass_from_view(view),
            coordinate_identity=view.coordinate_identity,
            known_at_ns=view.grid.known_at,
            width=width,
            origin=origin,
            coverage_complete=view.coverage_complete,
        )
    if smooth:
        current = transform_mass(current, kind='triangular', scale=smooth)
    return current


def _mass_from_view(view):
    mass = IntegerMass(row_ticks=view.grid.width_ticks, origin_ticks=view.grid.origin_ticks)
    for row in view.rows:
        price = view.grid.origin_ticks + row.row * view.grid.width_ticks
        buy, sell, unknown = int(row.buy), int(row.sell), int(row.unknown)
        if buy:
            mass.buy[price] = buy
        if sell:
            mass.sell[price] = sell
        if unknown:
            mass.unknown[price] = unknown
        total = buy + sell + unknown
        mass.sum_q += total
        mass.sum_pq += price * total
        mass.sum_p2q += price * price * total
    mass.unpriced = [int(v) for v in view.unpriced]
    return mass


def compact_geometry(result, *, view=None):
    poc = result.get('poc_set') or ()
    plateaus = result.get('maximum_plateaus') or ()
    peaks = result.get('local_peaks') or ()
    valleys = result.get('interior_valleys') or ()
    value_rows = result.get('value_rows') or ()
    val = min(value_rows) if value_rows else None
    vah = max(value_rows) if value_rows else None
    overshoot = result.get('overshoot')
    achieved = result.get('achieved_mass')
    requested = result.get('requested_mass')
    mean_row = result.get('mean_row')
    dominance = result.get('dominance_margin')
    concentration = result.get('concentration')
    overflow = (
        tuple(int(v) for v in result.get('low_overflow', view.low_overflow if view is not None else (0, 0, 0))),
        tuple(int(v) for v in result.get('high_overflow', view.high_overflow if view is not None else (0, 0, 0))),
        tuple(int(v) for v in result.get('unpriced', view.unpriced if view is not None else (0, 0, 0))),
    )
    return {
        'poc_set': tuple(int(v) for v in poc),
        'poc_count': len(poc),
        'scalar_poc': None if result.get('scalar_poc') is None else int(result['scalar_poc']),
        'maximum_plateau_lows': tuple(int(a) for a, _ in plateaus),
        'maximum_plateau_highs': tuple(int(b) for _, b in plateaus),
        'value_rows': tuple(int(v) for v in value_rows),
        'val_row': val,
        'vah_row': vah,
        'va_width_ticks': None if val is None or vah is None else int(vah - val),
        'requested_mass_num': _fraction_pair(requested)[0],
        'requested_mass_den': _fraction_pair(requested)[1],
        'achieved_mass_num': _fraction_pair(achieved)[0],
        'achieved_mass_den': _fraction_pair(achieved)[1],
        'overshoot_num': _fraction_pair(overshoot)[0],
        'overshoot_den': _fraction_pair(overshoot)[1],
        'peak_lows': tuple(int(peak['rows'][0]) for peak in peaks),
        'peak_highs': tuple(int(peak['rows'][1]) for peak in peaks),
        'peak_count': len(peaks),
        'valley_lows': tuple(int(a) for a, _ in valleys),
        'valley_highs': tuple(int(b) for _, b in valleys),
        'valley_count': len(valleys),
        'mean_row_num': _fraction_pair(mean_row)[0],
        'mean_row_den': _fraction_pair(mean_row)[1],
        'dominance_margin_num': _fraction_pair(dominance)[0],
        'dominance_margin_den': _fraction_pair(dominance)[1],
        'concentration_num': _fraction_pair(concentration)[0],
        'concentration_den': _fraction_pair(concentration)[1],
        'low_overflow_buy': overflow[0][0],
        'low_overflow_sell': overflow[0][1],
        'low_overflow_unknown': overflow[0][2],
        'high_overflow_buy': overflow[1][0],
        'high_overflow_sell': overflow[1][1],
        'high_overflow_unknown': overflow[1][2],
        'unpriced_buy': overflow[2][0],
        'unpriced_sell': overflow[2][1],
        'unpriced_unknown': overflow[2][2],
    }


def null_geometry(*, reason):
    row = {name: None for name in (
        'poc_set', 'poc_count', 'scalar_poc', 'maximum_plateau_lows', 'maximum_plateau_highs',
        'value_rows', 'val_row', 'vah_row', 'va_width_ticks',
        'requested_mass_num', 'requested_mass_den', 'achieved_mass_num', 'achieved_mass_den',
        'overshoot_num', 'overshoot_den', 'peak_lows', 'peak_highs', 'peak_count',
        'valley_lows', 'valley_highs', 'valley_count',
        'mean_row_num', 'mean_row_den', 'dominance_margin_num', 'dominance_margin_den',
        'concentration_num', 'concentration_den',
        'low_overflow_buy', 'low_overflow_sell', 'low_overflow_unknown',
        'high_overflow_buy', 'high_overflow_sell', 'high_overflow_unknown',
        'unpriced_buy', 'unpriced_sell', 'unpriced_unknown',
    )}
    row['geometry_status'] = reason
    row['poc_set'] = None
    return row


def geometry_from_mass(mass, spec, *, coordinate_identity, known_at_ns, coverage_complete,
                       verify_kernel=False):
    if mass.sum_q <= 0:
        reason = 'no_priced_volume' if mass.unpriced_volume else 'unknown_priced_population'
        return null_geometry(reason=reason), None
    view = mass_view_from_histogram(
        mass, coordinate_identity=coordinate_identity, known_at_ns=known_at_ns,
        width=1, origin=0, coverage_complete=coverage_complete and not mass.unpriced_volume,
    )
    shaped = apply_variant_view(view, spec)
    definition = variant_definition(spec)
    raw = geometry(shaped, definition=definition)
    compact = compact_geometry(raw, view=shaped)
    compact['geometry_status'] = (
        'complete' if coverage_complete and mass.unpriced_volume == 0 and mass.coordinate_complete
        else 'observed_partial'
    )
    if mass.unpriced_volume and not coverage_complete:
        compact['geometry_status'] = 'incomplete_unpriced'
    if verify_kernel:
        again = geometry(shaped, definition=definition)
        if tuple(again.get('poc_set') or ()) != tuple(raw.get('poc_set') or ()):
            raise IntegrityError('geometry kernel parity failed on POC maximizers')
        if again.get('value_rows') != raw.get('value_rows'):
            raise IntegrityError('geometry kernel parity failed on value rows')
    return compact, shaped


def bar_proxy_from_mass(mass, variant, *, coordinate_identity, known_at_ns, coverage_complete):
    if not mass.bars:
        row = null_geometry(reason='no_bar_publication')
        row['source_flat_bar_lost_mass'] = 0
        row['proxy_variant'] = variant
        return row, None
    prices = []
    for bar in mass.bars:
        prices.extend((bar[1], bar[2]))
    low, high = min(prices), max(prices)
    grid = FrozenGrid(0, 1, low, high, f'{coordinate_identity}:bar:{variant}', int(known_at_ns),
                      max(DEFAULT_PRICE_CELLS, high - low + 8))
    allocation = bar_allocation_rows(tuple(mass.bars), grid=grid, variant=variant)
    view = MassView(
        coordinate_identity, grid, allocation['rows'],
        allocation['low_overflow'], allocation['high_overflow'], allocation['unpriced'],
        coverage_complete and not sum(allocation['unpriced']),
        (('bar_proxy', variant),),
    )
    spec = next(item for item in FROZEN_GEOMETRY_VARIANTS if item['id'] == BASELINE_VARIANT_ID)
    raw = geometry(view, definition=variant_definition(spec))
    compact = compact_geometry(raw, view=view)
    compact['source_flat_bar_lost_mass'] = int(allocation['source_flat_bar_lost_mass'])
    compact['proxy_variant'] = variant
    compact['geometry_status'] = (
        'complete' if coverage_complete and sum(allocation['unpriced']) == 0 else 'observed_partial'
    )
    return compact, view


def compact_side_geometry(view):
    raw = side_geometry(view)
    return {
        'side_overlap_num': _fraction_pair(raw.get('overlap'))[0],
        'side_overlap_den': _fraction_pair(raw.get('overlap'))[1],
        'side_total_variation_num': _fraction_pair(raw.get('total_variation'))[0],
        'side_total_variation_den': _fraction_pair(raw.get('total_variation'))[1],
        'side_wasserstein_num': _fraction_pair(raw.get('wasserstein_ticks'))[0],
        'side_wasserstein_den': _fraction_pair(raw.get('wasserstein_ticks'))[1],
        'delta_maximum_rows': tuple(int(v) for v in raw.get('maximum_rows') or ()),
        'delta_minimum_rows': tuple(int(v) for v in raw.get('minimum_rows') or ()),
        'absolute_peak_rows': tuple(int(v) for v in raw.get('absolute_peak_rows') or ()),
        'absolute_delta_mass_num': _fraction_pair(raw.get('absolute_delta_mass'))[0],
        'absolute_delta_mass_den': _fraction_pair(raw.get('absolute_delta_mass'))[1],
    }


def compact_footprint(view, params):
    raw = footprint_geometry(
        view, ratio=params['ratio'], minimum_volume=params['minimum_volume'],
        comparison=params['comparison'], zero_opponent=params['zero_opponent'],
        minimum_stack_rows=params['minimum_stack_rows'],
    )
    return {
        'footprint_buy_imbalance_rows': sum(1 for row in raw['rows'] if row['buy']['qualifying']),
        'footprint_sell_imbalance_rows': sum(1 for row in raw['rows'] if row['sell']['qualifying']),
        'footprint_buy_stack_count': len(raw['buy_stacks']),
        'footprint_sell_stack_count': len(raw['sell_stacks']),
        'footprint_history_complete': raw['geometry_history_complete'],
    }


def vwap_bands(moments):
    mean = moments.get('vwap_ticks')
    variance = moments.get('variance_ticks_squared')
    if mean is None:
        return {
            'vwap_ticks_num': None, 'vwap_ticks_den': None,
            'variance_ticks_squared_num': None, 'variance_ticks_squared_den': None,
            'sd_ticks_num': None, 'sd_ticks_den': None,
            'percent_band_low_num': None, 'percent_band_low_den': None,
            'percent_band_high_num': None, 'percent_band_high_den': None,
        }
    sd = None if variance is None or variance < 0 else exact_sqrt(variance)
    bands = {
        'vwap_ticks_num': int(mean.numerator),
        'vwap_ticks_den': int(mean.denominator),
        'variance_ticks_squared_num': None if variance is None else int(variance.numerator),
        'variance_ticks_squared_den': None if variance is None else int(variance.denominator),
        'sd_ticks_num': None if sd is None else int(sd.numerator),
        'sd_ticks_den': None if sd is None else int(sd.denominator),
    }
    for index, fraction in enumerate(VWAP_PERCENT_BANDS):
        bands[f'percent_band_{index}_low_num'] = int((mean * (1 - fraction)).numerator)
        bands[f'percent_band_{index}_low_den'] = int((mean * (1 - fraction)).denominator)
        bands[f'percent_band_{index}_high_num'] = int((mean * (1 + fraction)).numerator)
        bands[f'percent_band_{index}_high_den'] = int((mean * (1 + fraction)).denominator)
    if sd is not None:
        for index, mult in enumerate(VWAP_SD_BANDS):
            bands[f'sd_band_{index}_low_num'] = int((mean - mult * sd).numerator)
            bands[f'sd_band_{index}_low_den'] = int((mean - mult * sd).denominator)
            bands[f'sd_band_{index}_high_num'] = int((mean + mult * sd).numerator)
            bands[f'sd_band_{index}_high_den'] = int((mean + mult * sd).denominator)
    return bands


def exact_sqrt(value):
    from trading_research.measurements.vwap import exact_sqrt as _sqrt
    return _sqrt(value)


def weighted_quantiles(mass):
    weighted = tuple((price, mass.sides_at(price)[0] + mass.sides_at(price)[1] + mass.sides_at(price)[2])
                     for price in mass.prices())
    out = {}
    for q in VWAP_QUANTILES:
        value = weighted_quantile(weighted, q) if mass.sum_q else None
        num, den = _fraction_pair(value)
        key = f'q_{q.numerator}_{q.denominator}'
        out[f'{key}_num'] = num
        out[f'{key}_den'] = den
    if mass.sum_q:
        median = weighted_quantile(weighted, Fraction(1, 2))
        deviations = tuple((abs(price - median), qty) for price, qty in weighted)
        mad = weighted_quantile(deviations, Fraction(1, 2))
        out['weighted_median_num'], out['weighted_median_den'] = _fraction_pair(median)
        out['mad_num'], out['mad_den'] = _fraction_pair(mad)
        scaled = None if mad is None else mad * MAD_SCALE
        out['robust_scale_num'], out['robust_scale_den'] = _fraction_pair(scaled)
    else:
        for name in ('weighted_median', 'mad', 'robust_scale'):
            out[f'{name}_num'] = None
            out[f'{name}_den'] = None
    return out


def pin069_reanchor(atoms, *, cut_ns):
    """Bar-close-volume reanchor on a new completed-bar high inside UTC-4 06-09."""
    window_start = None
    selected = None
    high = None
    origin_ns = None
    published_ns = None
    for atom in atoms:
        start = atom['event_start_ns']
        local = datetime.fromtimestamp(start // NS, timezone.utc).astimezone(ZoneInfo('Etc/GMT+4'))
        inside = local.hour >= 6 and (local.hour < 9 or (local.hour == 9 and local.minute == 0 and local.second == 0))
        if not inside or atom['event_end_ns'] > cut_ns:
            continue
        bar_high = atom.get('observed_high_ticks')
        if bar_high is None:
            continue
        if high is None:
            high = bar_high
            selected = atom
            origin_ns = start
            published_ns = atom['known_at_ns']
            window_start = start
            continue
        if bar_high > high:
            high = bar_high
            selected = atom
            published_ns = atom['known_at_ns']
    if selected is None:
        return {
            'pin069_active': False, 'pin069_origin_ns': origin_ns, 'pin069_published_ns': published_ns,
            'pin069_close_volume': None, 'pin069_high_ticks': high, 'pin069_window_start_ns': window_start,
        }
    close = selected.get('last_priced_ticks')
    volume = selected.get('priced_volume') or 0
    return {
        'pin069_active': True,
        'pin069_origin_ns': origin_ns,
        'pin069_published_ns': published_ns,
        'pin069_close_volume': None if close is None else int(close) * int(volume),
        'pin069_high_ticks': high,
        'pin069_window_start_ns': window_start,
    }


def to_atomic_trades(atom, anchor):
    first = None
    last = None
    high = None
    low = None
    if atom.get('first_priced_ticks') is not None:
        first = (
            atom.get('first_priced_event_ns') or atom['event_start_ns'],
            atom.get('first_priced_source_order') or 0,
            atom['first_priced_ticks'], atom.get('source_path') or anchor.source_lineage, 0,
        )
    if atom.get('last_priced_ticks') is not None:
        last = (
            atom.get('last_priced_event_ns') or atom['event_end_ns'] - 1,
            atom.get('last_priced_source_order') or 0,
            atom['last_priced_ticks'], atom.get('source_path') or anchor.source_lineage, 0,
        )
    if atom.get('observed_high_ticks') is not None:
        high = (int(atom['observed_high_ticks']),)
    if atom.get('observed_low_ticks') is not None:
        low = (int(atom['observed_low_ticks']),)
    rows = tuple((int(row), int(buy), int(sell), int(unknown)) for row, buy, sell, unknown in atom['rows'])
    return AtomicTrades(
        root=anchor.root,
        contract_key=anchor.contract_key,
        instrument_id=anchor.instrument_id,
        source_lineage=anchor.source_lineage,
        evidence_id=atom.get('evidence_id') or digest({
            'path': atom.get('source_path'), 'start': atom['event_start_ns'],
            'end': atom['event_end_ns'], 'instrument_id': atom['instrument_id'],
        }),
        start_ns=int(atom['event_start_ns']),
        end_ns=int(atom['event_end_ns']),
        known_at_ns=int(atom['known_at_ns']),
        source_complete=bool(atom.get('source_coverage_complete', True)),
        coordinate_complete=bool(atom.get('coordinate_complete', True)),
        start_source_order=atom.get('start_source_order'),
        paths=(),
        rows=rows,
        unpriced=tuple(int(v) for v in atom['unpriced']),
        unpriced_prints=int(atom.get('unpriced_prints') or 0),
        first=first, last=last, first_priced=first, last_priced=last,
        high=high, low=low, sum_squared_sizes=0,
    )


def tpo_from_atoms(anchor, atoms, *, event_end_ns, decision_cut_ns, latency_ns,
                   bracket_minutes=30, representation='whole_trade_visits'):
    tpo = AnchorTPO(anchor, bracket_minutes=bracket_minutes, representation=representation)
    for atom in atoms:
        tpo.add(to_atomic_trades(atom, anchor))
    return tpo.record(event_end_ns=event_end_ns, decision_cut_ns=decision_cut_ns, latency_ns=latency_ns)


def compact_tpo(record):
    visits = tuple(int(row) for row, _, _ in record.get('rows') or ())
    singles = record.get('provisional_single_print_rows')
    finals = record.get('final_single_print_rows')
    legacy = record.get('legacy_source_five_bracket_final_single_print_rows')
    return {
        'representation': record.get('representation'),
        'bracket_minutes': record.get('bracket_minutes'),
        'complete_brackets': record.get('complete_brackets'),
        'observed_nonempty_brackets': record.get('observed_nonempty_brackets'),
        'formation_final': record.get('formation_final'),
        'price_history_complete': record.get('price_history_complete'),
        'visit_rows': visits,
        'visit_count': len(visits),
        'provisional_single_print_rows': None if singles is None else tuple(int(v) for v in singles),
        'final_single_print_rows': None if finals is None else tuple(int(v) for v in finals),
        'legacy_five_bracket_final_single_print_rows': None if legacy is None else tuple(int(v) for v in legacy),
        'low_tail_rows': tuple(int(v) for v in record.get('low_tail_rows') or ()),
        'high_tail_rows': tuple(int(v) for v in record.get('high_tail_rows') or ()),
        'ib30_complete': (record.get('initial_balance') or {}).get('30', {}).get('complete'),
        'ib60_complete': (record.get('initial_balance') or {}).get('60', {}).get('complete'),
        'ib30_high': None if not (record.get('initial_balance') or {}).get('30', {}).get('complete_high_low_ticks')
        else record['initial_balance']['30']['complete_high_low_ticks'][0],
        'ib30_low': None if not (record.get('initial_balance') or {}).get('30', {}).get('complete_high_low_ticks')
        else record['initial_balance']['30']['complete_high_low_ticks'][1],
        'ib60_high': None if not (record.get('initial_balance') or {}).get('60', {}).get('complete_high_low_ticks')
        else record['initial_balance']['60']['complete_high_low_ticks'][0],
        'ib60_low': None if not (record.get('initial_balance') or {}).get('60', {}).get('complete_high_low_ticks')
        else record['initial_balance']['60']['complete_high_low_ticks'][1],
        'known_at_ns': record.get('known_at_ns'),
    }


def classify_future_contact(*, poc, val, vah, high, low, last, complete, no_new, no_priced):
    """Touch/traverse/terminal from label extrema. Order of first touch stays unknown."""
    if no_new:
        return {'status': 'no_event', 'reason': 'no_new_trade', 'touch_order_identified': False}
    if no_priced:
        return {'status': 'no_event', 'reason': 'no_priced_trade', 'touch_order_identified': False}
    if not complete:
        return {'status': 'censored', 'reason': 'label_incomplete', 'touch_order_identified': False}
    if high is None or low is None:
        return {'status': 'missing', 'reason': 'missing_future_extrema', 'touch_order_identified': False}

    def against(level, name):
        if level is None:
            return {f'{name}_touch': None, f'{name}_traverse': None}
        return {
            f'{name}_touch': int(low) <= int(level) <= int(high),
            f'{name}_traverse': int(low) < int(level) < int(high),
        }

    out = {
        'status': 'observed',
        'reason': None,
        'touch_order_identified': False,
        **against(poc, 'poc'),
        **against(val, 'val'),
        **against(vah, 'vah'),
        'terminal_inside_va': None if last is None or val is None or vah is None
        else int(val) <= int(last) <= int(vah),
        'terminal_outside_va': None if last is None or val is None or vah is None
        else int(last) < int(val) or int(last) > int(vah),
        'terminal_at_poc': None if last is None or poc is None else int(last) == int(poc),
    }
    return out


def compare_frozen_developing_va(*, prior_val, prior_vah, current_val, current_vah,
                                 previous_price, current_price):
    """Split boundary motion from price crossing a fixed prior VA."""
    moving = (
        prior_val is not None and current_val is not None and int(prior_val) != int(current_val)
    ) or (
        prior_vah is not None and current_vah is not None and int(prior_vah) != int(current_vah)
    )
    crossing = False
    if previous_price is not None and current_price is not None and prior_val is not None and prior_vah is not None:
        was_inside = int(prior_val) <= int(previous_price) <= int(prior_vah)
        now_inside = int(prior_val) <= int(current_price) <= int(prior_vah)
        crossing = was_inside != now_inside
    return {
        'boundary_moving': moving,
        'price_crossing_frozen_va': crossing,
        'prior_val_row': prior_val,
        'prior_vah_row': prior_vah,
        'current_val_row': current_val,
        'current_vah_row': current_vah,
    }


def future_mass_on_frozen_grid(mass, following, *, coordinate_identity, known_at_ns,
                               coverage_complete):
    """Measure future POC/VA on the cut-frozen grid; overflow is explicit."""
    if mass.sum_q <= 0 and not mass.prices():
        return null_geometry(reason='no_priced_volume'), None
    view = mass_view_from_histogram(
        mass, coordinate_identity=coordinate_identity, known_at_ns=known_at_ns,
        width=1, origin=0, coverage_complete=coverage_complete,
    )
    future = IntegerMass()
    low = [0, 0, 0]
    high = [0, 0, 0]
    lower = view.grid.origin_ticks + view.grid.lower_row * view.grid.width_ticks
    upper = view.grid.origin_ticks + (view.grid.upper_row + 1) * view.grid.width_ticks
    for atom in following:
        for row, buy, sell, unknown in atom['rows']:
            price = int(atom.get('origin_ticks', 0)) + int(row) * int(atom.get('row_ticks', 1))
            if price < lower:
                low[0] += int(buy); low[1] += int(sell); low[2] += int(unknown)
            elif price >= upper:
                high[0] += int(buy); high[1] += int(sell); high[2] += int(unknown)
            else:
                future.buy[price] = future.buy.get(price, 0) + int(buy)
                future.sell[price] = future.sell.get(price, 0) + int(sell)
                future.unknown[price] = future.unknown.get(price, 0) + int(unknown)
                total = int(buy) + int(sell) + int(unknown)
                future.sum_q += total
                future.sum_pq += price * total
                future.sum_p2q += price * price * total
        for index, amount in enumerate(atom['unpriced']):
            future.unpriced[index] += int(amount)
    spec = next(item for item in FROZEN_GEOMETRY_VARIANTS if item['id'] == BASELINE_VARIANT_ID)
    if future.sum_q <= 0:
        row = null_geometry(reason='no_priced_volume')
        row['future_low_overflow_buy'] = low[0]
        row['future_low_overflow_sell'] = low[1]
        row['future_low_overflow_unknown'] = low[2]
        row['future_high_overflow_buy'] = high[0]
        row['future_high_overflow_sell'] = high[1]
        row['future_high_overflow_unknown'] = high[2]
        return row, view.grid
    compact, _ = geometry_from_mass(
        future, spec, coordinate_identity=coordinate_identity,
        known_at_ns=known_at_ns, coverage_complete=coverage_complete,
    )
    compact['future_low_overflow_buy'] = low[0]
    compact['future_low_overflow_sell'] = low[1]
    compact['future_low_overflow_unknown'] = low[2]
    compact['future_high_overflow_buy'] = high[0]
    compact['future_high_overflow_sell'] = high[1]
    compact['future_high_overflow_unknown'] = high[2]
    compact['future_grid_origin_ticks'] = view.grid.origin_ticks
    compact['future_grid_width_ticks'] = view.grid.width_ticks
    compact['future_grid_lower_row'] = view.grid.lower_row
    compact['future_grid_upper_row'] = view.grid.upper_row
    return compact, view.grid


def intended_atom_ends(start_ns, end_ns, *, width_ns=MINUTE_NS):
    if end_ns <= start_ns:
        return ()
    return tuple(range(start_ns + width_ns, end_ns + 1, width_ns))


def coverage_from_atoms(intended_spans, atoms):
    """Explicit intended versus supplied intervals. Missing atoms are not zeros."""
    supplied = tuple((atom['event_start_ns'], atom['event_end_ns']) for atom in atoms)
    missing = []
    for start, end in intended_spans:
        cursor = start
        for a, b in supplied:
            if b <= start or a >= end:
                continue
            if cursor < a:
                missing.append((cursor, min(a, end)))
            cursor = max(cursor, min(b, end))
        if cursor < end:
            missing.append((cursor, end))
    complete = not missing and all(atom.get('source_coverage_complete', True) for atom in atoms)
    return {
        'intended_spans': tuple(intended_spans),
        'missing_spans': tuple(missing),
        'coverage_complete': complete,
        'observed_partial': bool(atoms) and not complete,
    }


def aligned_cuts(start_ns, end_ns, *, stride_ns=CUT_STRIDE_NS):
    if end_ns <= start_ns:
        return ()
    first = start_ns + stride_ns
    remainder = first % stride_ns
    if remainder:
        first += stride_ns - remainder
    if first > end_ns:
        if end_ns > start_ns:
            return (int(end_ns),) if end_ns % stride_ns == 0 else ()
        return ()
    return tuple(range(int(first), int(end_ns) + 1, int(stride_ns)))


def publication_known(*, input_known_ns, selection_known_ns, cut_ns, latency_ns):
    known = max(int(input_known_ns), int(selection_known_ns), int(cut_ns) + int(latency_ns))
    return known


def delayed_selection_blocks_origin(selection_known_ns, origin_ns):
    return int(selection_known_ns) > int(origin_ns)


def atom_identity_key(atom):
    return (
        atom.get('source_path'),
        atom.get('source_metadata_sha256'),
        atom.get('canonical_raw_values_sha256'),
        atom.get('instrument_id'),
        atom.get('contract_key'),
        atom.get('event_start_ns'),
        atom.get('event_end_ns'),
    )


def alias_key(atom):
    return (
        atom.get('canonical_raw_values_sha256'),
        atom.get('instrument_id'),
        atom.get('contract_key'),
        atom.get('event_start_ns'),
        atom.get('event_end_ns'),
        tuple(atom.get('rows') or ()),
        tuple(atom.get('unpriced') or ()),
    )


def dedup_atoms(atoms):
    """Exact alias collapse, or retain a conflict. No arbitrary winner."""
    by_alias = {}
    order = []
    conflicts = []
    for atom in atoms:
        key = alias_key(atom)
        coord = (
            atom.get('instrument_id'), atom.get('contract_key'),
            atom.get('event_start_ns'), atom.get('event_end_ns'),
            atom.get('canonical_raw_values_sha256'),
        )
        if key in by_alias:
            continue
        clash = None
        for other_key, other in by_alias.items():
            other_coord = (
                other.get('instrument_id'), other.get('contract_key'),
                other.get('event_start_ns'), other.get('event_end_ns'),
                other.get('canonical_raw_values_sha256'),
            )
            if coord == other_coord and other_key != key:
                clash = other
                break
            same_slot = (
                atom.get('source_path') == other.get('source_path')
                and atom.get('instrument_id') == other.get('instrument_id')
                and atom.get('contract_key') == other.get('contract_key')
                and atom.get('event_start_ns') == other.get('event_start_ns')
                and atom.get('event_end_ns') == other.get('event_end_ns')
            )
            if same_slot and other_key != key:
                clash = other
                break
        if clash is not None:
            conflicts.append({'left': atom_identity_key(atom), 'right': atom_identity_key(clash)})
            continue
        by_alias[key] = atom
        order.append(key)
    return [by_alias[key] for key in order], tuple(conflicts)


def _col(table, name, *, optional=False):
    if name not in table.column_names:
        if optional:
            return [None] * len(table)
        raise IntegrityError(f'observation or window table lost required column {name}')
    return table.column(name).to_pylist()


def observation_rows_from_tables(tables):
    rows = []
    counted = 0
    for table in tables:
        counted += len(table)
        names = table.column_names
        columns = {name: table.column(name).to_pylist() for name in names}
        for index in range(len(table)):
            rows.append({name: columns[name][index] for name in names})
    return rows, counted


def window_rows_from_tables(tables):
    rows, counted = observation_rows_from_tables(tables)
    return rows, counted


def load_measurement_cells(unit, *, cache):
    ref = None
    if isinstance(unit.get('measurement'), dict) and unit['measurement'].get('path'):
        ref = unit['measurement']
    elif isinstance((unit.get('original_refs') or {}).get('measurement'), dict):
        ref = unit['original_refs']['measurement']
    elif isinstance(unit.get('artifacts'), dict) and isinstance(unit['artifacts'].get('measurement'), dict):
        ref = unit['artifacts']['measurement']
    if ref is None:
        if unit.get('source_window_status') == 'unavailable_source_window' or unit.get('disposition') == 'unavailable_source_window':
            return {
                'status': 'unavailable_source_window',
                'reason': unit.get('unavailable_reason') or 'unavailable_source_window',
                'atoms': (),
            }
        raise IntegrityError('observation unit lost its accepted measurement receipt')
    key = (ref.get('sha256'), ref.get('path'), ref.get('uncompressed_sha256'))
    if key in cache:
        return cache[key]
    payload = read_json_artifact(ref)
    extracted = extract_unit_cells(payload)
    cache[key] = extracted
    return extracted


def attach_observation_identity(atoms, observations, *, unit):
    by_key = {}
    for row in observations:
        key = (
            row.get('instrument_id'),
            _py_int(row.get('event_start_ns'), what='obs.event_start_ns'),
            _py_int(row.get('event_end_ns'), what='obs.event_end_ns'),
        )
        if key in by_key:
            raise IntegrityError('observation series repeats an atom coordinate')
        by_key[key] = row
    out = []
    for atom in atoms:
        key = (atom['instrument_id'], atom['event_start_ns'], atom['event_end_ns'])
        obs = by_key.get(key)
        match_atom_identity(atom, obs)
        merged = dict(atom)
        merged['source_path'] = obs.get('source_path') or unit.get('source_path')
        merged['source_metadata_sha256'] = obs.get('source_metadata_sha256') or unit.get('source_metadata_sha256')
        merged['source_variant'] = obs.get('source_variant') or unit.get('source_variant')
        merged['canonical_raw_values_sha256'] = obs.get('canonical_raw_values_sha256')
        merged['receipt_sha256'] = obs.get('receipt_sha256')
        merged['measurement_sha256'] = obs.get('measurement_sha256')
        merged['root'] = obs.get('root') or unit.get('root')
        merged['source_window_start_ns'] = obs.get('source_window_start_ns') or unit.get('source_window_start_ns')
        merged['source_window_end_ns'] = obs.get('source_window_end_ns') or unit.get('source_window_end_ns')
        if merged.get('contract_key') is None:
            merged['contract_key'] = obs.get('contract_key')
        if obs.get('sum_price_volume') is not None:
            merged['sum_price_volume'] = obs['sum_price_volume']
        if obs.get('sum_price_squared_volume') is not None:
            merged['sum_price_squared_volume'] = obs['sum_price_squared_volume']
        out.append(merged)
    return out


def geometry_schema(pa):
    def i64(name, nullable=True):
        return pa.field(name, pa.int64(), nullable=nullable)

    def flag(name):
        return pa.field(name, pa.bool_(), nullable=True)

    def text(name, nullable=True):
        return pa.field(name, pa.string(), nullable=nullable)

    def lst(name):
        return pa.field(name, pa.list_(pa.int64()), nullable=True)

    fields = [
        text('source_collection', nullable=False), text('root', nullable=False),
        i64('year', nullable=False), text('stage'), text('session'),
        text('anchor_id'), text('anchor_variant'), text('anchor_kind'),
        text('geometry_variant'), text('proxy_variant'),
        text('source_path'), text('source_metadata_sha256'), text('source_variant'),
        text('canonical_raw_values_sha256'), text('measurement_sha256'),
        text('contract_key'), i64('instrument_id'), i64('raw_instrument_id'),
        i64('anchor_start_ns'), i64('anchor_end_ns'), i64('anchor_span_ns'),
        i64('selection_known_ns'), i64('cut_ns'), i64('published_known_ns'),
        text('economic_date'), flag('coverage_complete'), flag('formation_complete'),
        flag('eligible_complete'), text('geometry_status'),
        text('completed_geometry_id'),
        lst('poc_set'), i64('poc_count'), i64('scalar_poc'),
        lst('maximum_plateau_lows'), lst('maximum_plateau_highs'),
        lst('value_rows'), i64('val_row'), i64('vah_row'), i64('va_width_ticks'),
        i64('requested_mass_num'), i64('requested_mass_den'),
        i64('achieved_mass_num'), i64('achieved_mass_den'),
        i64('overshoot_num'), i64('overshoot_den'),
        lst('peak_lows'), lst('peak_highs'), i64('peak_count'),
        lst('valley_lows'), lst('valley_highs'), i64('valley_count'),
        i64('mean_row_num'), i64('mean_row_den'),
        i64('dominance_margin_num'), i64('dominance_margin_den'),
        i64('concentration_num'), i64('concentration_den'),
        i64('low_overflow_buy'), i64('low_overflow_sell'), i64('low_overflow_unknown'),
        i64('high_overflow_buy'), i64('high_overflow_sell'), i64('high_overflow_unknown'),
        i64('unpriced_buy'), i64('unpriced_sell'), i64('unpriced_unknown'),
        i64('priced_volume'), i64('sum_price_volume'), i64('sum_price_squared_volume'),
        i64('vwap_ticks_num'), i64('vwap_ticks_den'),
        i64('variance_ticks_squared_num'), i64('variance_ticks_squared_den'),
        i64('source_flat_bar_lost_mass'),
        i64('side_overlap_num'), i64('side_overlap_den'),
        i64('side_total_variation_num'), i64('side_total_variation_den'),
        i64('absolute_delta_mass_num'), i64('absolute_delta_mass_den'),
        lst('delta_maximum_rows'), lst('delta_minimum_rows'), lst('absolute_peak_rows'),
        i64('footprint_buy_imbalance_rows'), i64('footprint_sell_imbalance_rows'),
        i64('footprint_buy_stack_count'), i64('footprint_sell_stack_count'),
        flag('footprint_history_complete'),
        i64('pin069_close_volume'), i64('pin069_high_ticks'), flag('pin069_active'),
        i64('atom_count'), i64('input_cells'),
        flag('selected_partition_member'),
        text('physical_contract_key'), text('source_lineage'),
    ]
    return pa.schema(fields)


def tpo_schema(pa):
    def i64(name, nullable=True):
        return pa.field(name, pa.int64(), nullable=nullable)

    def flag(name):
        return pa.field(name, pa.bool_(), nullable=True)

    def text(name, nullable=True):
        return pa.field(name, pa.string(), nullable=nullable)

    def lst(name):
        return pa.field(name, pa.list_(pa.int64()), nullable=True)

    return pa.schema([
        text('source_collection', nullable=False), text('root', nullable=False),
        i64('year', nullable=False), text('stage'), text('session'),
        text('anchor_id'), text('anchor_variant'), text('representation'),
        i64('bracket_minutes'), i64('cut_ns'), i64('known_at_ns'),
        text('contract_key'), i64('instrument_id'), text('source_path'),
        i64('complete_brackets'), i64('observed_nonempty_brackets'),
        flag('formation_final'), flag('price_history_complete'),
        lst('visit_rows'), i64('visit_count'),
        lst('range_proxy_rows'), i64('range_proxy_count'),
        lst('provisional_single_print_rows'), lst('final_single_print_rows'),
        lst('legacy_five_bracket_final_single_print_rows'),
        lst('low_tail_rows'), lst('high_tail_rows'),
        flag('ib30_complete'), flag('ib60_complete'),
        i64('ib30_high'), i64('ib30_low'), i64('ib60_high'), i64('ib60_low'),
        text('economic_date'),
    ])


def join_schema(pa):
    def i64(name, nullable=True):
        return pa.field(name, pa.int64(), nullable=nullable)

    def flag(name):
        return pa.field(name, pa.bool_(), nullable=True)

    def text(name, nullable=True):
        return pa.field(name, pa.string(), nullable=nullable)

    return pa.schema([
        text('source_collection', nullable=False), text('root', nullable=False),
        i64('year', nullable=False), text('stage'), text('session'),
        text('anchor_id'), text('geometry_variant'), text('source_path'),
        text('contract_key'), i64('instrument_id'),
        i64('cut_ns'), i64('latency_ns'), text('horizon_kind'), i64('horizon_minutes'),
        flag('formation_complete'), flag('coverage_known'),
        flag('label_complete'), flag('same_stage'),
        text('join_status'), text('censor_reason'),
        i64('scalar_poc'), i64('val_row'), i64('vah_row'),
        i64('future_high_ticks'), i64('future_low_ticks'), i64('future_last_ticks'),
        flag('poc_touch'), flag('poc_traverse'),
        flag('val_touch'), flag('val_traverse'),
        flag('vah_touch'), flag('vah_traverse'),
        flag('terminal_inside_va'), flag('terminal_outside_va'), flag('terminal_at_poc'),
        flag('touch_order_identified'),
        flag('boundary_moving'), flag('price_crossing_frozen_va'),
        i64('future_poc'), i64('future_val_row'), i64('future_vah_row'),
        i64('future_low_overflow_buy'), i64('future_high_overflow_buy'),
        flag('future_input_known'),
        text('economic_date'),
    ])


def cell_schema(pa):
    def i64(name, nullable=True):
        return pa.field(name, pa.int64(), nullable=nullable)

    def text(name, nullable=True):
        return pa.field(name, pa.string(), nullable=nullable)

    return pa.schema([
        text('source_path', nullable=False), i64('instrument_id', nullable=False),
        text('contract_key'), i64('event_start_ns', nullable=False),
        i64('event_end_ns', nullable=False), i64('price_ticks', nullable=False),
        i64('buy', nullable=False), i64('sell', nullable=False),
        i64('unknown', nullable=False), i64('unpriced_buy'), i64('unpriced_sell'),
        i64('unpriced_unknown'), text('measurement_sha256'),
        text('canonical_raw_values_sha256'),
    ])


def _table_from_rows(schema, rows, pa):
    names = [field.name for field in schema]
    if not rows:
        return pa.table({name: pa.array([], type=schema.field(name).type) for name in names}, schema=schema)
    columns = {}
    for field in schema:
        values = [row.get(field.name) for row in rows]
        columns[field.name] = pa.array(values, type=field.type)
    return pa.table(columns, schema=schema)


def write_series_table(outputs, name, table):
    series = ParquetSeries(outputs, name, encoding='plain')
    if not len(table):
        series.append(table)
    else:
        offset = 0
        while offset < len(table):
            amount = min(BATCH_HINT, len(table) - offset)
            series.append(table.slice(offset, amount))
            offset += amount
    return series.finish()


def _empty_geometry_row():
    return {field.name: None for field in geometry_schema(_require_pyarrow())}


def _empty_tpo_row():
    return {field.name: None for field in tpo_schema(_require_pyarrow())}


def _empty_join_row():
    return {field.name: None for field in join_schema(_require_pyarrow())}


def session_of(cut_ns, *, calendar, known_at_ns):
    from trading_research.research.auction_flow_core_statistics import classify_session
    return classify_session(cut_ns, cut_ns + MINUTE_NS, calendar=calendar, known_at_ns=known_at_ns)


def _wholly_inside(atom, spans):
    start, end = atom['event_start_ns'], atom['event_end_ns']
    return any(a <= start and end <= b for a, b in spans)


def _atoms_in_spans(atoms, spans):
    return [atom for atom in atoms if _wholly_inside(atom, spans)]


def _input_known(atoms, default):
    known = default
    for atom in atoms:
        if atom.get('known_at_ns') is not None:
            known = atom['known_at_ns'] if known is None else max(known, atom['known_at_ns'])
    return known


def _fill_geometry_identity(row, *, collection, root, year, stage, session, atom, anchor,
                            variant_id, proxy, cut_ns, published, economic, selected):
    row['source_collection'] = collection
    row['root'] = root
    row['year'] = year
    row['stage'] = stage
    row['session'] = session
    row['anchor_id'] = None if anchor is None else anchor.id
    row['anchor_variant'] = None if anchor is None else anchor.variant
    row['anchor_kind'] = None if anchor is None else anchor.kind
    row['geometry_variant'] = variant_id
    row['proxy_variant'] = proxy
    row['source_path'] = None if atom is None else atom.get('source_path')
    row['source_metadata_sha256'] = None if atom is None else atom.get('source_metadata_sha256')
    row['source_variant'] = None if atom is None else atom.get('source_variant')
    row['canonical_raw_values_sha256'] = None if atom is None else atom.get('canonical_raw_values_sha256')
    row['measurement_sha256'] = None if atom is None else atom.get('measurement_sha256')
    row['contract_key'] = None if atom is None else atom.get('contract_key')
    row['physical_contract_key'] = None if atom is None else atom.get('contract_key')
    row['instrument_id'] = None if atom is None else atom.get('instrument_id')
    row['raw_instrument_id'] = None if atom is None else atom.get('instrument_id')
    row['source_lineage'] = None if atom is None else atom.get('source_path')
    if anchor is not None:
        row['anchor_start_ns'] = anchor.start_ns
        row['anchor_end_ns'] = anchor.end_ns
        row['anchor_span_ns'] = anchor.end_ns - anchor.start_ns
        row['selection_known_ns'] = anchor.selection_known_at_ns
    row['cut_ns'] = cut_ns
    row['published_known_ns'] = published
    row['economic_date'] = economic
    row['selected_partition_member'] = selected


def _merge_compact(row, compact):
    for key, value in compact.items():
        if key in row or key in _GEOMETRY_LIST_FIELDS or key.endswith('_num') or key.endswith('_den'):
            row[key] = value
        elif key in (
            'geometry_status', 'source_flat_bar_lost_mass', 'proxy_variant',
            'priced_volume', 'pin069_active', 'pin069_close_volume', 'pin069_high_ticks',
        ):
            row[key] = value
        elif key.startswith('side_') or key.startswith('footprint_') or key.startswith('absolute_') or key.startswith('delta_'):
            row[key] = value


def emit_geometry_rows(*, mass, atoms, spec, coordinate_identity, known_at_ns,
                       coverage_complete, include_side, include_vwap, include_footprint,
                       footprint_params, verify_kernel=False):
    compact, view = geometry_from_mass(
        mass, spec, coordinate_identity=coordinate_identity, known_at_ns=known_at_ns,
        coverage_complete=coverage_complete, verify_kernel=verify_kernel,
    )
    extras = {}
    if view is not None and include_side:
        extras.update(compact_side_geometry(view))
    if include_vwap:
        extras.update(vwap_bands(mass.vwap_moments()))
        extras.update(weighted_quantiles(mass))
        extras.update(pin069_reanchor(atoms, cut_ns=known_at_ns))
    if view is not None and include_footprint:
        extras.update(compact_footprint(view, footprint_params))
    moments = mass.vwap_moments()
    extras['priced_volume'] = mass.priced_volume
    extras['sum_price_volume'] = moments['sum_price_volume']
    extras['sum_price_squared_volume'] = moments['sum_price_squared_volume']
    extras['atom_count'] = mass.atom_count
    extras['input_cells'] = sum(len(atom.get('rows') or ()) for atom in atoms)
    compact.update(extras)
    return compact, view


def _clock_anchors_for_day(*, day, cut_ns, calendar, root, instrument_id, contract_key, source_lineage):
    try:
        return named_clock_anchors(
            day=day, cut_ns=cut_ns, calendar=calendar, root=root,
            instrument_id=instrument_id, contract_key=contract_key,
            source_lineage=source_lineage,
        )
    except DependencyUnavailable as exc:
        return {'anchors': (), 'unavailable': ({'variant': 'named_clocks', 'reason': str(exc)},)}


def _join_window_rows(window_index, *, path, root, instrument_id, contract_key, cut_ns):
    return window_index.get((path, root, instrument_id, contract_key, cut_ns), [])


def build_window_index(window_units, *, wanted_paths):
    index = defaultdict(list)
    feature_rows = 0
    label_rows = 0
    scanned = 0
    for unit in window_units:
        path = (unit.get('source_identity') or {}).get('source_path') or unit.get('source_path')
        if path not in wanted_paths:
            continue
        if unit.get('features') is None or unit.get('labels') is None:
            continue
        features, n_feat = window_rows_from_tables(read_series_tables(unit['features']))
        labels, n_lab = window_rows_from_tables(read_series_tables(unit['labels']))
        feature_rows += n_feat
        label_rows += n_lab
        scanned += 1
        labels_by_cut = defaultdict(list)
        for label in labels:
            labels_by_cut[(
                label.get('source_path') or path,
                label.get('root') or unit.get('root'),
                label.get('instrument_id'),
                label.get('contract_key'),
                label.get('cut_ns'),
            )].append(label)
        for feature in features:
            key = (
                feature.get('source_path') or path,
                feature.get('root') or unit.get('root'),
                feature.get('instrument_id'),
                feature.get('contract_key'),
                feature.get('cut_ns'),
            )
            index[key].append({'feature': feature, 'labels': labels_by_cut.get(key, [])})
    return index, {'window_units_read': scanned, 'feature_rows': feature_rows, 'label_rows': label_rows}


def _following_atoms(atoms, *, cut_ns, horizon_ns, same_identity):
    out = []
    for atom in atoms:
        if not same_identity(atom):
            continue
        if atom['event_start_ns'] >= cut_ns and atom['event_end_ns'] <= cut_ns + horizon_ns:
            out.append(atom)
    return out


def compute_identity_geometry(*, atoms, collection, root, year, calendar, policy,
                              footprint_params, window_index, selected, completeness,
                              verify_completed=True):
    geometry_rows = []
    tpo_rows = []
    join_rows = []
    if not atoms:
        return geometry_rows, tpo_rows, join_rows
    sample = atoms[0]
    instrument_id = sample['instrument_id']
    contract_key = sample.get('contract_key')
    if contract_key is None or not str(contract_key).startswith(str(root) + ':'):
        completeness['missing_contract_identity'] += 1
        return geometry_rows, tpo_rows, join_rows
    source_lineage = sample.get('source_path') or collection
    atoms = sorted(atoms, key=lambda item: (item['event_start_ns'], item['event_end_ns'], item.get('source_path') or ''))
    min_start = atoms[0]['event_start_ns']
    max_end = atoms[-1]['event_end_ns']
    days = sorted({
        date.fromisoformat(economic_date(int(atom['event_start_ns'])))
        for atom in atoms
    } | {
        date.fromisoformat(economic_date(int(atom['event_end_ns'] - 1)))
        for atom in atoms
    })
    completed_cache = {}
    prior_completed_va = {}
    previous_developing = {}

    def same_identity(atom):
        return (
            atom.get('instrument_id') == instrument_id
            and atom.get('contract_key') == contract_key
            and atom.get('source_path') == sample.get('source_path')
        )

    identity_atoms = [atom for atom in atoms if same_identity(atom)]
    for day in days:
        economic = day.isoformat()
        if int(economic[:4]) != int(year):
            continue
        stage = stage_name(root, economic, policy)
        cut_for_clocks = local_timestamp(day, time(17, 0), ZONE)
        named = _clock_anchors_for_day(
            day=day, cut_ns=cut_for_clocks, calendar=calendar, root=root,
            instrument_id=instrument_id, contract_key=contract_key,
            source_lineage=source_lineage,
        )
        for missing in named.get('unavailable') or ():
            completeness['unavailable_clocks'] += 1
            completeness['unavailable_clock_reasons'].append({
                'economic_date': economic, 'variant': missing.get('variant'),
                'reason': missing.get('reason'),
            })
        session_info = session_of(cut_for_clocks, calendar=calendar, known_at_ns=cut_for_clocks)
        session = session_info['session']

        for anchor in named.get('anchors') or ():
            members = _atoms_in_spans(identity_atoms, anchor.spans)
            coverage = coverage_from_atoms(anchor.spans, members)
            cut_ns = anchor.end_ns
            input_known = _input_known(members, cut_ns)
            if delayed_selection_blocks_origin(anchor.selection_known_at_ns, anchor.start_ns):
                published = publication_known(
                    input_known_ns=input_known, selection_known_ns=anchor.selection_known_at_ns,
                    cut_ns=cut_ns, latency_ns=SOURCE_LATENCY_NS,
                )
                if published < cut_ns:
                    raise IntegrityError('delayed selection cannot publish at a retrospective origin')
            published = publication_known(
                input_known_ns=input_known, selection_known_ns=anchor.selection_known_at_ns,
                cut_ns=cut_ns, latency_ns=SOURCE_LATENCY_NS,
            )
            hist = IntegerMass()
            for atom in members:
                hist.add(atom)
            hist.copy_flags_from(members)
            complete = coverage['coverage_complete'] and hist.priced_volume > 0
            variants = FROZEN_GEOMETRY_VARIANTS if complete else (
                next(item for item in FROZEN_GEOMETRY_VARIANTS if item['id'] == BASELINE_VARIANT_ID),
            )
            completed_id = None
            first_view = None
            for spec in variants:
                include_aux = spec['id'] == BASELINE_VARIANT_ID
                compact, view = emit_geometry_rows(
                    mass=hist, atoms=members, spec=spec,
                    coordinate_identity=f'{root}:{contract_key}:{source_lineage}',
                    known_at_ns=published, coverage_complete=coverage['coverage_complete'],
                    include_side=include_aux, include_vwap=include_aux,
                    include_footprint=include_aux, footprint_params=footprint_params,
                    verify_kernel=verify_completed and complete,
                )
                if view is not None and spec['id'] == BASELINE_VARIANT_ID:
                    first_view = view
                row = _empty_geometry_row()
                _fill_geometry_identity(
                    row, collection=collection, root=root, year=year, stage=stage,
                    session=session, atom=sample, anchor=anchor, variant_id=spec['id'],
                    proxy=None, cut_ns=cut_ns, published=published, economic=economic,
                    selected=selected,
                )
                row['coverage_complete'] = coverage['coverage_complete']
                row['formation_complete'] = complete
                row['eligible_complete'] = complete
                _merge_compact(row, compact)
                if completed_id is None:
                    completed_id = digest({
                        'anchor_id': anchor.id, 'variant': spec['id'], 'cut_ns': cut_ns,
                        'cells': [atom.get('measurement_sha256') for atom in members],
                    })
                row['completed_geometry_id'] = completed_id
                geometry_rows.append(row)
                completeness['geometry_emitted'] += 1
                if complete:
                    completeness['geometry_complete'] += 1
                elif compact.get('geometry_status', '').startswith('null') or compact.get('geometry_status') in (
                    'no_priced_volume', 'unknown_priced_population',
                ):
                    completeness['geometry_null'] += 1
                else:
                    completeness['geometry_partial'] += 1
            if complete:
                baseline = next(
                    item for item in reversed(geometry_rows)
                    if item.get('geometry_variant') == BASELINE_VARIANT_ID
                    and item.get('anchor_id') == anchor.id
                )
                completed_cache[(anchor.variant, economic)] = {
                    'id': completed_id,
                    'val': baseline.get('val_row'),
                    'vah': baseline.get('vah_row'),
                    'poc': baseline.get('scalar_poc'),
                    'view': first_view,
                }
                prior_completed_va[anchor.variant] = (
                    baseline.get('val_row'), baseline.get('vah_row'), baseline.get('scalar_poc'),
                )
                for proxy in BAR_PROXY_VARIANTS:
                    proxy_row, _ = bar_proxy_from_mass(
                        hist, proxy,
                        coordinate_identity=f'{root}:{contract_key}:{source_lineage}',
                        known_at_ns=published, coverage_complete=coverage['coverage_complete'],
                    )
                    row = _empty_geometry_row()
                    _fill_geometry_identity(
                        row, collection=collection, root=root, year=year, stage=stage,
                        session=session, atom=sample, anchor=anchor, variant_id=BASELINE_VARIANT_ID,
                        proxy=proxy, cut_ns=cut_ns, published=published, economic=economic,
                        selected=selected,
                    )
                    row['coverage_complete'] = coverage['coverage_complete']
                    row['formation_complete'] = complete
                    row['eligible_complete'] = complete
                    row['completed_geometry_id'] = completed_id
                    _merge_compact(row, proxy_row)
                    geometry_rows.append(row)
                    completeness['geometry_emitted'] += 1
                    completeness['proxy_emitted'] += 1
                for minutes in BRACKET_MINUTES:
                    for representation in ('whole_trade_visits', 'ohlc_range_proxy'):
                        try:
                            raw = tpo_from_atoms(
                                anchor, members, event_end_ns=min(cut_ns, anchor.end_ns),
                                decision_cut_ns=published, latency_ns=SOURCE_LATENCY_NS,
                                bracket_minutes=minutes, representation=representation,
                            )
                        except (ContractError, IntegrityError) as exc:
                            completeness['tpo_failed'] += 1
                            completeness['failed_reasons'].append({'kind': 'tpo', 'reason': str(exc)})
                            continue
                        compact = compact_tpo(raw)
                        tpo_row = _empty_tpo_row()
                        tpo_row.update({
                            'source_collection': collection, 'root': root, 'year': year,
                            'stage': stage, 'session': session, 'anchor_id': anchor.id,
                            'anchor_variant': anchor.variant, 'cut_ns': cut_ns,
                            'contract_key': contract_key, 'instrument_id': instrument_id,
                            'source_path': sample.get('source_path'), 'economic_date': economic,
                        })
                        tpo_row.update(compact)
                        if representation == 'whole_trade_visits':
                            tpo_row['range_proxy_rows'] = None
                            tpo_row['range_proxy_count'] = None
                        else:
                            tpo_row['range_proxy_rows'] = compact.get('visit_rows')
                            tpo_row['range_proxy_count'] = compact.get('visit_count')
                        tpo_rows.append(tpo_row)
                        completeness['tpo_emitted'] += 1

        cash_anchor = next((a for a in named.get('anchors') or () if a.variant == 'cash_rth'), None)
        futures_anchor = next(
            (a for a in named.get('anchors') or () if a.variant == 'observed_futures_18_17'), None)
        developing = (
            ('developing_cash_rth', cash_anchor),
            ('developing_observed_futures_18_17', futures_anchor),
        )
        spec = next(item for item in FROZEN_GEOMETRY_VARIANTS if item['id'] == BASELINE_VARIANT_ID)
        for kind, base in developing:
            if base is None:
                completeness['missing_developing_base'] += 1
                continue
            start, end = base.start_ns, min(base.end_ns, max_end)
            cuts = aligned_cuts(start, end)
            hist = IntegerMass()
            pending = [atom for atom in identity_atoms if _wholly_inside(atom, ((start, end),))]
            pending.sort(key=lambda item: item['event_end_ns'])
            cursor = 0
            prev_cut = start
            for cut_ns in cuts:
                while cursor < len(pending) and pending[cursor]['event_end_ns'] <= cut_ns:
                    hist.add(pending[cursor])
                    cursor += 1
                members = [atom for atom in pending[:cursor] if atom['event_start_ns'] >= start]
                coverage = coverage_from_atoms(((start, cut_ns),), members)
                input_known = _input_known(members, cut_ns)
                published = publication_known(
                    input_known_ns=input_known, selection_known_ns=base.selection_known_at_ns,
                    cut_ns=cut_ns, latency_ns=SOURCE_LATENCY_NS,
                )
                compact, view = emit_geometry_rows(
                    mass=hist, atoms=members, spec=spec,
                    coordinate_identity=f'{root}:{contract_key}:{source_lineage}',
                    known_at_ns=published, coverage_complete=coverage['coverage_complete'],
                    include_side=True, include_vwap=True, include_footprint=True,
                    footprint_params=footprint_params,
                )
                row = _empty_geometry_row()
                _fill_geometry_identity(
                    row, collection=collection, root=root, year=year, stage=stage,
                    session=session_of(cut_ns, calendar=calendar, known_at_ns=published)['session'],
                    atom=sample, anchor=base, variant_id=BASELINE_VARIANT_ID, proxy=None,
                    cut_ns=cut_ns, published=published, economic=economic, selected=selected,
                )
                row['anchor_variant'] = kind
                row['anchor_kind'] = 'developing'
                row['coverage_complete'] = coverage['coverage_complete']
                row['formation_complete'] = coverage['coverage_complete'] and cut_ns >= base.end_ns
                row['eligible_complete'] = False
                cached = completed_cache.get((base.variant, economic))
                row['completed_geometry_id'] = None if cached is None else cached['id']
                _merge_compact(row, compact)
                geometry_rows.append(row)
                completeness['geometry_emitted'] += 1
                completeness['baseline_emitted'] += 1
                prior = prior_completed_va.get(base.variant)
                last_price = members[-1].get('last_priced_ticks') if members else None
                prev_price = previous_developing.get((kind, 'price'))
                if prior is not None:
                    motion = compare_frozen_developing_va(
                        prior_val=prior[0], prior_vah=prior[1],
                        current_val=row.get('val_row'), current_vah=row.get('vah_row'),
                        previous_price=prev_price, current_price=last_price,
                    )
                else:
                    motion = {
                        'boundary_moving': False, 'price_crossing_frozen_va': False,
                        'prior_val_row': None, 'prior_vah_row': None,
                        'current_val_row': row.get('val_row'), 'current_vah_row': row.get('vah_row'),
                    }
                previous_developing[(kind, 'price')] = last_price
                previous_developing[(kind, 'va')] = (row.get('val_row'), row.get('vah_row'))
                _emit_joins(
                    join_rows, completeness, window_index=window_index, sample=sample,
                    root=root, collection=collection, year=year, stage=stage,
                    session=row['session'], economic=economic, anchor_id=base.id,
                    cut_ns=cut_ns, geometry_row=row, identity_atoms=identity_atoms,
                    view=view, motion=motion, calendar=calendar,
                )
                prev_cut = cut_ns
                _ = prev_cut

        for minutes in ROLLING_MINUTES:
            width = minutes * MINUTE_NS
            cuts = aligned_cuts(min_start, max_end)
            hist = IntegerMass()
            window = deque()
            pending = list(identity_atoms)
            cursor = 0
            for cut_ns in cuts:
                if date.fromisoformat(economic_date(int(cut_ns - 1))) != day and date.fromisoformat(economic_date(int(cut_ns))) != day:
                    continue
                if int(economic_date(int(cut_ns - 1))[:4]) != int(year) and int(economic_date(int(cut_ns))[:4]) != int(year):
                    continue
                while cursor < len(pending) and pending[cursor]['event_end_ns'] <= cut_ns:
                    atom = pending[cursor]
                    cursor += 1
                    if atom['event_start_ns'] >= cut_ns - width:
                        hist.add(atom)
                        window.append(atom)
                while window and window[0]['event_start_ns'] < cut_ns - width:
                    hist.remove(window.popleft())
                members = list(window)
                other = [atom for atom in members if atom.get('source_path') != sample.get('source_path')
                         and atom.get('source_collection') not in (None, collection)]
                if other:
                    raise IntegrityError('rolling window mixed a foreign source collection')
                rolling = rolling_anchor(
                    minutes=minutes, event_end_ns=cut_ns,
                    selection_known_at_ns=cut_ns, source_versions=(source_lineage,),
                    root=root, instrument_id=instrument_id, contract_key=contract_key,
                    source_lineage=source_lineage,
                )
                coverage = coverage_from_atoms(((cut_ns - width, cut_ns),), members)
                input_known = _input_known(members, cut_ns)
                published = publication_known(
                    input_known_ns=input_known, selection_known_ns=cut_ns,
                    cut_ns=cut_ns, latency_ns=SOURCE_LATENCY_NS,
                )
                eco = economic_date(int(cut_ns - 1))
                if int(eco[:4]) != int(year):
                    continue
                compact, view = emit_geometry_rows(
                    mass=hist, atoms=members, spec=spec,
                    coordinate_identity=f'{root}:{contract_key}:{source_lineage}',
                    known_at_ns=published, coverage_complete=coverage['coverage_complete'],
                    include_side=True, include_vwap=True, include_footprint=True,
                    footprint_params=footprint_params,
                )
                row = _empty_geometry_row()
                _fill_geometry_identity(
                    row, collection=collection, root=root, year=year,
                    stage=stage_name(root, eco, policy),
                    session=session_of(cut_ns, calendar=calendar, known_at_ns=published)['session'],
                    atom=sample, anchor=rolling, variant_id=BASELINE_VARIANT_ID, proxy=None,
                    cut_ns=cut_ns, published=published, economic=eco, selected=selected,
                )
                row['coverage_complete'] = coverage['coverage_complete']
                row['formation_complete'] = coverage['coverage_complete']
                row['eligible_complete'] = coverage['coverage_complete'] and hist.priced_volume > 0
                _merge_compact(row, compact)
                geometry_rows.append(row)
                completeness['geometry_emitted'] += 1
                completeness['baseline_emitted'] += 1
                _emit_joins(
                    join_rows, completeness, window_index=window_index, sample=sample,
                    root=root, collection=collection, year=year, stage=row['stage'],
                    session=row['session'], economic=eco, anchor_id=rolling.id,
                    cut_ns=cut_ns, geometry_row=row, identity_atoms=identity_atoms,
                    view=view, motion={
                        'boundary_moving': False, 'price_crossing_frozen_va': False,
                        'prior_val_row': None, 'prior_vah_row': None,
                        'current_val_row': row.get('val_row'), 'current_vah_row': row.get('vah_row'),
                    }, calendar=calendar,
                )
    return geometry_rows, tpo_rows, join_rows


def _emit_joins(join_rows, completeness, *, window_index, sample, root, collection, year,
                stage, session, economic, anchor_id, cut_ns, geometry_row, identity_atoms,
                view, motion, calendar):
    matches = _join_window_rows(
        window_index, path=sample.get('source_path'), root=root,
        instrument_id=sample.get('instrument_id'), contract_key=sample.get('contract_key'),
        cut_ns=cut_ns,
    )
    if not matches:
        completeness['joins_missing'] += 1
        return
    for match in matches:
        feature = match['feature']
        feature_complete = bool(feature.get('atoms_complete', feature.get('source_coverage_complete')))
        coverage_known = feature.get('source_coverage_complete') is not None
        feature_stage = feature.get('stage') or stage
        for latency in LATENCY_NS:
            for horizon_kind in HORIZON_KINDS:
                horizons = FORWARD_HORIZONS_MINUTES if horizon_kind == 'fixed_minutes' else (None,)
                for horizon in horizons:
                    label = None
                    for candidate in match['labels']:
                        if int(candidate.get('latency_ns') or -1) != int(latency):
                            continue
                        if candidate.get('horizon_kind') != horizon_kind:
                            continue
                        if horizon_kind == 'fixed_minutes' and int(candidate.get('horizon_minutes') or -1) != int(horizon):
                            continue
                        label = candidate
                        break
                    row = _empty_join_row()
                    row.update({
                        'source_collection': collection, 'root': root, 'year': year,
                        'stage': feature_stage, 'session': session, 'anchor_id': anchor_id,
                        'geometry_variant': geometry_row.get('geometry_variant'),
                        'source_path': sample.get('source_path'),
                        'contract_key': sample.get('contract_key'),
                        'instrument_id': sample.get('instrument_id'),
                        'cut_ns': cut_ns, 'latency_ns': latency,
                        'horizon_kind': horizon_kind, 'horizon_minutes': horizon,
                        'formation_complete': feature_complete,
                        'coverage_known': coverage_known,
                        'economic_date': economic,
                    })
                    if label is None:
                        row['join_status'] = 'no_label'
                        row['censor_reason'] = 'missing_label'
                        join_rows.append(row)
                        completeness['joins_missing'] += 1
                        continue
                    label_stage = label.get('stage') or feature_stage
                    same_stage = label_stage == feature_stage
                    row['same_stage'] = same_stage
                    row['label_complete'] = bool(label.get('complete'))
                    if not same_stage:
                        row['join_status'] = 'stage_leak'
                        row['censor_reason'] = 'feature_label_stage_disagree'
                        join_rows.append(row)
                        completeness['joins_censored'] += 1
                        continue
                    if not feature_complete or not coverage_known:
                        row['join_status'] = 'formation_incomplete'
                        row['censor_reason'] = 'feature_incomplete'
                        join_rows.append(row)
                        completeness['joins_censored'] += 1
                        continue
                    contact = classify_future_contact(
                        poc=geometry_row.get('scalar_poc'),
                        val=geometry_row.get('val_row'),
                        vah=geometry_row.get('vah_row'),
                        high=label.get('observed_high_ticks'),
                        low=label.get('observed_low_ticks'),
                        last=label.get('last_priced_ticks'),
                        complete=bool(label.get('complete')),
                        no_new=bool(label.get('no_new_trade')),
                        no_priced=bool(label.get('no_priced_trade')),
                    )
                    row['join_status'] = contact['status']
                    row['censor_reason'] = contact.get('reason')
                    row['scalar_poc'] = geometry_row.get('scalar_poc')
                    row['val_row'] = geometry_row.get('val_row')
                    row['vah_row'] = geometry_row.get('vah_row')
                    row['future_high_ticks'] = label.get('observed_high_ticks')
                    row['future_low_ticks'] = label.get('observed_low_ticks')
                    row['future_last_ticks'] = label.get('last_priced_ticks')
                    for name in (
                        'poc_touch', 'poc_traverse', 'val_touch', 'val_traverse',
                        'vah_touch', 'vah_traverse', 'terminal_inside_va',
                        'terminal_outside_va', 'terminal_at_poc', 'touch_order_identified',
                    ):
                        row[name] = contact.get(name)
                    row['boundary_moving'] = motion.get('boundary_moving')
                    row['price_crossing_frozen_va'] = motion.get('price_crossing_frozen_va')
                    if horizon_kind == 'fixed_minutes' and horizon is not None and view is not None:
                        following = _following_atoms(
                            identity_atoms, cut_ns=cut_ns, horizon_ns=horizon * MINUTE_NS,
                            same_identity=lambda atom: (
                                atom.get('instrument_id') == sample.get('instrument_id')
                                and atom.get('contract_key') == sample.get('contract_key')
                                and atom.get('source_path') == sample.get('source_path')
                            ),
                        )
                        intended = intended_atom_ends(cut_ns, cut_ns + horizon * MINUTE_NS)
                        present = {atom['event_end_ns'] for atom in following}
                        future_known = all(end in present for end in intended) and all(
                            atom.get('source_coverage_complete', True) for atom in following
                        )
                        future_compact, _ = future_mass_on_frozen_grid(
                            _mass_from_view(view) if view is not None else IntegerMass(),
                            following,
                            coordinate_identity=f'{root}:{sample.get("contract_key")}',
                            known_at_ns=geometry_row.get('published_known_ns') or cut_ns,
                            coverage_complete=future_known,
                        )
                        row['future_poc'] = future_compact.get('scalar_poc')
                        row['future_val_row'] = future_compact.get('val_row')
                        row['future_vah_row'] = future_compact.get('vah_row')
                        row['future_low_overflow_buy'] = future_compact.get('future_low_overflow_buy')
                        row['future_high_overflow_buy'] = future_compact.get('future_high_overflow_buy')
                        row['future_input_known'] = future_known
                    else:
                        row['future_input_known'] = None
                    join_rows.append(row)
                    if contact['status'] == 'observed':
                        completeness['joins_emitted'] += 1
                    elif contact['status'] in ('no_event', 'censored', 'missing'):
                        completeness['joins_censored'] += 1
                    else:
                        completeness['joins_emitted'] += 1
    _ = calendar


def empty_completeness():
    return {
        'units_scanned': 0,
        'units_selected': 0,
        'units_neighbor': 0,
        'units_unavailable': 0,
        'atoms_scanned': 0,
        'atoms_matched': 0,
        'atoms_missing': 0,
        'atoms_conflict': 0,
        'geometry_emitted': 0,
        'geometry_complete': 0,
        'geometry_partial': 0,
        'geometry_null': 0,
        'baseline_emitted': 0,
        'proxy_emitted': 0,
        'tpo_emitted': 0,
        'tpo_failed': 0,
        'joins_emitted': 0,
        'joins_missing': 0,
        'joins_censored': 0,
        'missing_contract_identity': 0,
        'missing_developing_base': 0,
        'unavailable_clocks': 0,
        'unavailable_clock_reasons': [],
        'failed_reasons': [],
        'unavailable_units': [],
        'measurement_bytes': 0,
        'observation_rows': 0,
        'window_units_read': 0,
        'feature_rows': 0,
        'label_rows': 0,
        'cell_rows': 0,
    }


def compute_profile_partition(*, key, members, neighbors, identity, source_refs, contract,
                              calendar, policy, window_units, outputs, ordinal, pa):
    collection, root, year = key
    began, wall_began, before = time_mod.process_time(), time_mod.monotonic(), outputs.written
    completeness = empty_completeness()
    cache = {}
    selected_paths = {unit.get('source_path') for unit in members}
    wanted_paths = selected_paths | {unit.get('source_path') for unit in neighbors}
    window_index, window_counts = build_window_index(window_units, wanted_paths=wanted_paths)
    completeness.update(window_counts)
    all_atoms = []
    cell_rows = []
    seen_units = set()
    for role, group, selected in (('selected', members, True), ('neighbor', neighbors, False)):
        for unit in group:
            ukey = (
                unit.get('source_path'), unit.get('source_window_start_ns'),
                unit.get('source_window_end_ns'), unit.get('root'),
            )
            if ukey in seen_units:
                continue
            seen_units.add(ukey)
            completeness['units_scanned'] += 1
            if selected:
                completeness['units_selected'] += 1
            else:
                completeness['units_neighbor'] += 1
            if (
                unit.get('source_window_status') == 'unavailable_source_window'
                or unit.get('disposition') == 'unavailable_source_window'
                or unit.get('atomic_rows') == 0
            ):
                completeness['units_unavailable'] += 1
                completeness['unavailable_units'].append({
                    'source_path': unit.get('source_path'),
                    'root': unit.get('root'),
                    'source_window_start_ns': unit.get('source_window_start_ns'),
                    'source_window_end_ns': unit.get('source_window_end_ns'),
                    'reason': unit.get('unavailable_reason') or 'unavailable_source_window',
                })
                continue
            extracted = load_measurement_cells(unit, cache=cache)
            if extracted.get('status') == 'unavailable_source_window':
                completeness['units_unavailable'] += 1
                completeness['unavailable_units'].append({
                    'source_path': unit.get('source_path'),
                    'root': unit.get('root'),
                    'reason': extracted.get('reason'),
                })
                continue
            measurement_ref = unit.get('measurement') or (unit.get('original_refs') or {}).get('measurement')
            if isinstance(measurement_ref, dict):
                completeness['measurement_bytes'] += int(
                    measurement_ref.get('uncompressed_size_bytes') or measurement_ref.get('size_bytes') or 0
                )
            series = unit.get('series')
            if series is None:
                raise IntegrityError('observation unit lost its verified Parquet series')
            observations, counted = observation_rows_from_tables(read_series_tables(series))
            completeness['observation_rows'] += counted
            if counted != int(unit.get('atomic_rows') or counted):
                raise IntegrityError('read_series_tables row count does not match the unit receipt')
            merged = attach_observation_identity(extracted['atoms'], observations, unit=unit)
            completeness['atoms_scanned'] += len(merged)
            completeness['atoms_matched'] += len(merged)
            for atom in merged:
                atom['source_collection'] = collection if selected else (
                    atom.get('source_collection') or collection
                )
                atom['selected_partition_member'] = selected
                all_atoms.append(atom)
                for price, buy, sell, unknown in atom['rows']:
                    cell_rows.append({
                        'source_path': atom.get('source_path'),
                        'instrument_id': atom.get('instrument_id'),
                        'contract_key': atom.get('contract_key'),
                        'event_start_ns': atom['event_start_ns'],
                        'event_end_ns': atom['event_end_ns'],
                        'price_ticks': price,
                        'buy': buy, 'sell': sell, 'unknown': unknown,
                        'unpriced_buy': atom['unpriced'][0],
                        'unpriced_sell': atom['unpriced'][1],
                        'unpriced_unknown': atom['unpriced'][2],
                        'measurement_sha256': atom.get('measurement_sha256'),
                        'canonical_raw_values_sha256': atom.get('canonical_raw_values_sha256'),
                    })
    deduped, conflicts = dedup_atoms(all_atoms)
    completeness['atoms_conflict'] += len(conflicts)
    completeness['cell_rows'] = len(cell_rows)
    groups = defaultdict(list)
    for atom in deduped:
        groups[(atom.get('instrument_id'), atom.get('contract_key'), atom.get('source_path'))].append(atom)
    geometry_rows = []
    tpo_rows = []
    join_rows = []
    footprint_params = footprint_parameters(contract)
    for key_ident in sorted(groups, key=lambda item: (item[0] or 0, str(item[1]), str(item[2]))):
        geo, tpo, joins = compute_identity_geometry(
            atoms=groups[key_ident], collection=collection, root=root, year=year,
            calendar=calendar, policy=policy, footprint_params=footprint_params,
            window_index=window_index, selected=True, completeness=completeness,
        )
        geometry_rows.extend(geo)
        tpo_rows.extend(tpo)
        join_rows.extend(joins)
    prefix = f'profile-{ordinal:03d}-{collection}-{root}-{year}'
    geometry_ref = write_series_table(outputs, prefix + '-geometry', _table_from_rows(geometry_schema(pa), geometry_rows, pa))
    tpo_ref = write_series_table(outputs, prefix + '-tpo', _table_from_rows(tpo_schema(pa), tpo_rows, pa))
    join_ref = write_series_table(outputs, prefix + '-joins', _table_from_rows(join_schema(pa), join_rows, pa))
    cells_ref = write_series_table(outputs, prefix + '-cells', _table_from_rows(cell_schema(pa), cell_rows, pa))
    completeness_out = {
        **completeness,
        'conflicts': list(conflicts),
        'family_complete': False,
    }
    completeness_ref = outputs.json(
        prefix + '-completeness.json', completeness_out,
        kind='auction_flow_profile_partition_completeness_v1',
    )
    measurement = {
        'cpu_seconds': time_mod.process_time() - began,
        'wall_seconds': time_mod.monotonic() - wall_began,
        'output_bytes': outputs.written - before,
        'source_bytes': completeness['measurement_bytes'],
        'atoms': completeness['atoms_matched'],
        'geometry_rows': len(geometry_rows),
        'tpo_rows': len(tpo_rows),
        'join_rows': len(join_rows),
        'cell_rows': len(cell_rows),
    }
    part = {
        'kind': KIND, 'passed': True, 'identity': identity,
        'source_collection': collection, 'root': root, 'economic_year': year,
        'source_refs': source_refs,
        'geometry': geometry_ref, 'tpo': tpo_ref, 'joins': join_ref, 'cells': cells_ref,
        'completeness': completeness_ref,
        'group_count': len(geometry_rows),
        'measurement': measurement,
        'completeness_counts': {k: v for k, v in completeness_out.items() if k != 'conflicts'},
        'family_complete': False,
    }
    ref = outputs.json(prefix + '-partition.json', part, kind=KIND)
    return ref, part, measurement, geometry_rows, tpo_rows, join_rows


__all__ = [
    'BAR_PROXY_VARIANTS', 'BASELINE_VARIANT_ID', 'FROZEN_CONTRACT_KIND',
    'FROZEN_GEOMETRY_VARIANTS', 'IntegerMass', 'KIND', 'POPULATION_KIND',
    'ProfileCashAdapter', 'VERSION', 'WINDOW_POPULATION_KIND',
    'aligned_cuts', 'apply_variant_view', 'atom_bar', 'bar_proxy_from_mass',
    'cell_schema', 'classify_future_contact', 'compact_footprint',
    'compact_geometry', 'compact_side_geometry', 'compact_tpo',
    'compare_frozen_developing_va', 'compute_profile_partition',
    'coverage_from_atoms', 'dedup_atoms', 'delayed_selection_blocks_origin',
    'empty_completeness', 'extract_sparse_profile', 'extract_unit_cells',
    'footprint_parameters', 'frozen_variant_ids', 'future_mass_on_frozen_grid',
    'geometry_from_mass', 'geometry_schema', 'join_schema',
    'load_measurement_cells', 'match_atom_identity', 'mass_view_from_histogram',
    'null_geometry', 'pin069_reanchor', 'publication_known',
    'require_frozen_variants', 'tpo_from_atoms', 'tpo_schema',
    'to_atomic_trades', 'variant_definition', 'vwap_bands',
    'weighted_quantiles', 'write_series_table',
]
