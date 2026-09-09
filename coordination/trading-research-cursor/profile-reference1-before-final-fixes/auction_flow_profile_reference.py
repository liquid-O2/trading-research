"""Exact profile/TPO/VWAP/footprint reconstruction from retained atoms.

Extract original ``trade.sparse_profile`` cells once per source unit, reuse
observation clocks/coverage/moments, and emit compact typed geometry. This
helper does not fit Context, score Locations, replay tape, or spawn workers.
Root owns definitions, protocol, runner, execution and review.
"""
from __future__ import annotations

from collections import defaultdict, deque
from datetime import date, datetime, time, timedelta, timezone
from fractions import Fraction
from types import SimpleNamespace
from zoneinfo import ZoneInfo
import hashlib
import math
import time as time_mod

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.measurements.profiles import (
    FrozenGrid, ProfileDefinition, bar_allocation_rows,
)
from trading_research.measurements.vwap import exact_sqrt, weighted_quantile
from trading_research.operations.artifacts import digest
from trading_research.research.auction_flow_anchor_profiles import PIN069BarClose
from trading_research.research.auction_flow_anchor_tpo import (
    BRACKET_MINUTES, IB_MINUTES, AnchorTPO,
)
from trading_research.research.auction_flow_anchor_trades import AtomicTrades, FlowPath
from trading_research.research.auction_flow_anchors import (
    CONTRACT_SHA256 as ANCHOR_CONTRACT_SHA256,
    DETAIL_SHA256 as ANCHOR_DETAIL_SHA256,
    AuctionAnchor, MINUTE_NS as ANCHOR_MINUTE_NS, named_clock_anchors, rolling_anchor,
)
from trading_research.research.auction_flow_core_statistics import (
    ExplicitCashSessions, economic_date, stage_name,
)
from trading_research.research.auction_flow_measurements import SparseSideMass
from trading_research.research.auction_flow_profiles import (
    MassView, footprint_geometry, geometry, side_geometry, transform_mass, view_sparse,
)
from trading_research.research.auction_flow_storage import (
    BoundedOutputs, ParquetSeries, read_json_artifact, read_series_tables,
)
from trading_research.research.auction_flow_window_links import (
    FORMATION_MINUTES as WINDOW_FORMATION_MINUTES, join_window_eligibility,
)
from trading_research.research.auction_flow_window_statistics import (
    FEATURE_QUALITY_FLAGS, IDENTITY_KEYS, scientific_join_eligibility,
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
DAY_NS = 24 * 60 * MINUTE_NS
TICK_INDEX_POINTS = 0.25
SOURCE_LATENCY_NS = 250_000_000
LATENCY_NS = (0, 250_000_000, 1_000_000_000)
FORWARD_HORIZONS_MINUTES = (5, 15, 60)
HORIZON_KINDS = ('fixed_minutes', 'remaining_session')
FORMATION_MINUTES = tuple(WINDOW_FORMATION_MINUTES)
ACTIVE_ATOM_DAYS = 8
ROLLING_MINUTES = (5, 15, 60, 240)
QUANTILE_LEVELS = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
BATCH_HINT = 4096
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
# Registered imbalance_rows / footprint_geometry call. DETAIL has no footprint
# object; authenticate_bound_contracts must bind DETAIL before this kernel is used.
REGISTERED_FOOTPRINT_KERNEL = {
    'ratio': Fraction(3),
    'minimum_volume': 1,
    'comparison': 'diagonal',
    'zero_opponent': 'require_observed_opponent',
    'minimum_stack_rows': 2,
    'authority': (
        'measurements.footprint.imbalance_rows and auction_flow_profiles.footprint_geometry; '
        'AUCTION_FLOW_ANCHOR_DETAIL_SUPPLEMENT_V1 footprint is empty after authentication'
    ),
}
KERNEL_FOOTPRINT = REGISTERED_FOOTPRINT_KERNEL
BASELINE_VARIANT_ID = 'source-one-tick-value-7/10'
DEVELOPING_VARIANTS = ('developing_cash_rth', 'developing_observed_futures_18_17')
FIXED_CLOCK_IDS = (
    'cash_rth', 'prior_cash_rth', 'observed_futures_18_17', 'overnight_18_0930',
    'morning_06_09_ny', 'source_06_09_fixed_utc_minus4',
    'source_monday_22_21_utc', 'source_tuesday_22_21_utc',
)
CIVIL_VARIANTS = ('civil_ny_week', 'civil_ny_month', 'civil_ny_quarter', 'civil_ny_year')
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
_WEEKLY_DAY_FILE = __import__('re').compile(r'^\d{4}-\d{2}-\d{2}\.parquet$')
_MONTHLY_FILE = __import__('re').compile(r'^\d{4}-\d{2}\.parquet$')
_GEOMETRY_NAMES = None
_TPO_NAMES = None
_JOIN_NAMES = None
_CELL_NAMES = None


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
        return int(value[0]), int(value[1])
    raise IntegrityError('exact fraction must be a Fraction or [numerator, denominator]')


def encode_exact_int(value):
    """int64 when it fits; decimal string otherwise. Decoder is decode_exact_int."""
    if value is None:
        return None, None
    number = int(value)
    if _INT64_MIN <= number <= _INT64_MAX:
        return number, None
    return None, format(number, 'd')


def decode_exact_int(stored, text=None):
    if type(text) is str and text:
        return int(text)
    if stored is None:
        return None
    return int(stored)


def classify_source_collection(path, *, unit=None, injected=None):
    """Derive weekly/monthly collection without requiring fixture-only maps.

    Operational ``source_collections`` may bind a path. Otherwise the unit's
    declared collection, then the retained weekly-day vs monthly-file identity,
    then an explicit weekly/monthly token in the path, is used.
    """
    if injected and path in injected:
        return injected[path]
    if unit is not None:
        declared = unit.get('source_collection')
        if declared in ('weekly_acquisitions', 'monthly_acquisitions'):
            return declared
    if type(path) is not str or not path:
        raise IntegrityError('source path is required to derive a collection')
    name = path.rsplit('/', 1)[-1]
    if _WEEKLY_DAY_FILE.match(name) or '/weekly' in path or 'weekly-' in path:
        return 'weekly_acquisitions'
    if _MONTHLY_FILE.match(name) or '/monthly' in path or 'monthly-' in path:
        return 'monthly_acquisitions'
    raise IntegrityError(f'cannot derive weekly/monthly collection from {path!r}')


def source_lineage_id(collection, root, contract_key):
    return f'{collection}/{root}/{contract_key}'


def variant_definition(spec, *, anchor_kind='day'):
    rec = spec if isinstance(spec, dict) else next(
        item for item in FROZEN_GEOMETRY_VARIANTS if item['id'] == spec)
    numer, denom = rec['fraction']
    kind = anchor_kind if anchor_kind in (
        'rth', 'prior_rth', 'overnight', 'jumbo_named_range', 'day', 'week',
        'month', 'quarter', 'year', 'rolling', 'event', 'swing', 'composite',
    ) else 'day'
    return ProfileDefinition(
        rec['id'],
        anchor_kind=kind,
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


def _parse_footprint_mapping(rec, *, authority):
    rec = _mapping(rec, what='footprint')
    ratio = rec.get('ratio')
    if ratio is None:
        raise IntegrityError('footprint.ratio is required when a footprint object is present')
    if isinstance(ratio, (list, tuple)) and len(ratio) == 2:
        ratio = Fraction(int(ratio[0]), int(ratio[1]))
    elif type(ratio) is int:
        ratio = Fraction(ratio)
    if type(ratio) is not Fraction:
        raise IntegrityError('footprint.ratio must be an exact fraction')
    if 'minimum_volume' not in rec or 'comparison' not in rec or 'zero_opponent' not in rec:
        raise IntegrityError('footprint object lost registered comparison fields')
    out = {
        'ratio': ratio,
        'minimum_volume': int(rec['minimum_volume']),
        'comparison': rec['comparison'],
        'zero_opponent': rec['zero_opponent'],
        'minimum_stack_rows': int(rec.get('minimum_stack_rows', rec.get('minimum_stack', 2))),
        'authority': authority,
    }
    if out['comparison'] not in ('diagonal', 'same_price'):
        raise IntegrityError('footprint comparison must be diagonal or same_price')
    if out['zero_opponent'] not in ('require_observed_opponent', 'infinite_if_minimum'):
        raise IntegrityError('footprint zero_opponent is not a registered rule')
    if out['minimum_stack_rows'] < 2:
        raise IntegrityError('footprint stacks require at least two rows')
    return out


def authenticate_bound_contracts(contract, load_reference):
    """Authenticate bound ANCHOR/DETAIL. Empty DETAIL footprint uses the registered kernel."""
    inputs = contract.get('input_populations') if isinstance(contract, dict) else None
    if not isinstance(inputs, dict):
        return {
            'anchor_contract': None,
            'anchor_detail': None,
            'footprint': dict(REGISTERED_FOOTPRINT_KERNEL),
            'detail_bound': False,
        }
    out = {'detail_bound': False, 'anchor_contract': None, 'anchor_detail': None}
    for name, expected_sha, expected_kind in (
        ('anchor_contract', ANCHOR_CONTRACT_SHA256, 'auction_flow_exact_anchor_measurement_contract_v1'),
        ('anchor_detail', ANCHOR_DETAIL_SHA256, 'auction_flow_anchor_detail_supplement_v1'),
    ):
        ref = inputs.get(name)
        if not isinstance(ref, dict) or type(ref.get('path')) is not str:
            if name == 'anchor_detail':
                raise IntegrityError('bound profile contract lost its DETAIL reference')
            continue
        if ref.get('sha256') != expected_sha:
            raise IntegrityError(f'{name} sha256 is not the bound frozen identity')
        if not callable(load_reference):
            raise IntegrityError(f'{name} cannot be authenticated without a reference loader')
        payload = load_reference(ref, maximum=JSON_LOAD_MAX)
        if not isinstance(payload, dict) or payload.get('kind') != expected_kind:
            raise IntegrityError(f'{name} is not the bound {expected_kind}')
        if name == 'anchor_detail' and payload.get('parent_anchor_contract', {}).get('sha256') != ANCHOR_CONTRACT_SHA256:
            raise IntegrityError('DETAIL parent ANCHOR contract identity changed')
        out[name] = payload
        if name == 'anchor_detail':
            out['detail_bound'] = True
    if not out['detail_bound']:
        raise IntegrityError('bound profile contract must authenticate DETAIL before footprint use')
    out['footprint'] = footprint_parameters(contract, detail=out.get('anchor_detail'))
    return out


def footprint_parameters(contract, detail=None):
    raw = contract.get('footprint') if isinstance(contract, dict) else None
    if isinstance(raw, dict) and raw:
        return _parse_footprint_mapping(raw, authority='contract.footprint')
    if isinstance(detail, dict):
        detail_fp = detail.get('footprint')
        if isinstance(detail_fp, dict) and detail_fp:
            return _parse_footprint_mapping(detail_fp, authority='authenticated DETAIL.footprint')
        return dict(REGISTERED_FOOTPRINT_KERNEL)
    return dict(REGISTERED_FOOTPRINT_KERNEL)


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
                'observed_high_at_ns': _py_int(trade.get('observed_high_at_ns'), what='observed_high_at_ns'),
                'observed_low_at_ns': _py_int(trade.get('observed_low_at_ns'), what='observed_low_at_ns'),
                'observed_high_source_order': _py_int(
                    trade.get('observed_high_source_order'), what='observed_high_source_order'),
                'observed_low_source_order': _py_int(
                    trade.get('observed_low_source_order'), what='observed_low_source_order'),
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


def cells_content_hash(atom):
    raw = digest({
        'rows': [list(row) for row in atom.get('rows') or ()],
        'unpriced': list(atom.get('unpriced') or (0, 0, 0)),
    })
    return raw


class IntegerMass:
    """Exact integer side histogram with add/remove. No per-atom Fraction objects."""

    __slots__ = (
        'buy', 'sell', 'unknown', 'unpriced', 'sum_q', 'sum_pq', 'sum_p2q',
        'row_ticks', 'origin_ticks', 'atom_count', 'prints', 'unpriced_prints',
        'coverage_complete', 'price_history_complete', 'coordinate_complete',
        'bars', 'source_paths', 'source_hashes', 'unpriced_only_atoms',
        'input_cells', 'first_priced_ticks', 'first_priced_known_at_ns',
        'last_priced_ticks', 'last_priced_known_at_ns',
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
        self.bars = deque()
        self.source_paths = set()
        self.source_hashes = set()
        self.unpriced_only_atoms = 0
        self.input_cells = 0
        self.first_priced_ticks = None
        self.first_priced_known_at_ns = None
        self.last_priced_ticks = None
        self.last_priced_known_at_ns = None

    def add(self, atom, *, signed=1):
        if signed not in (1, -1):
            raise ContractError('histogram update sign must be +1 or -1')
        rows = atom['rows']
        if not rows and signed == 1:
            self.unpriced_only_atoms += 1
        self.input_cells += signed * len(rows)
        for row, buy, sell, unknown in rows:
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
            sha = atom.get('measurement_sha256') or atom.get('canonical_raw_values_sha256')
            if sha:
                self.source_hashes.add(sha)
            bar = atom_bar(atom)
            if bar is not None:
                self.bars.append(bar)
            first = atom.get('first_priced_ticks')
            if first is not None and self.first_priced_ticks is None:
                self.first_priced_ticks = int(first)
                self.first_priced_known_at_ns = atom.get('known_at_ns')
            last = atom.get('last_priced_ticks')
            if last is not None:
                self.last_priced_ticks = int(last)
                self.last_priced_known_at_ns = atom.get('known_at_ns')
        else:
            if not rows:
                self.unpriced_only_atoms -= 1
            if atom_bar(atom) is not None and self.bars:
                self.bars.popleft()

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

    def rebin(self, *, width, origin):
        buy, sell, unknown = {}, {}, {}
        for price in self.prices():
            row = (int(price) - int(origin)) // int(width)
            b, s, u = self.sides_at(price)
            if b:
                buy[row] = buy.get(row, 0) + b
            if s:
                sell[row] = sell.get(row, 0) + s
            if u:
                unknown[row] = unknown.get(row, 0) + u
        return buy, sell, unknown


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


def physical_tick(row, *, width, origin):
    if row is None:
        return None
    return int(origin) + int(row) * int(width)


def integer_profile_geometry(mass, spec):
    """Integer/common-denominator geometry. Literal Fraction kernels stay for tests."""
    width = int(spec['width'])
    origin = int(spec['origin'])
    numer, denom = spec['fraction']
    if mass.sum_q <= 0:
        reason = 'no_priced_volume' if mass.unpriced_volume else 'unknown_priced_population'
        return null_geometry(reason=reason)
    buy, sell, unknown = mass.rebin(width=width, origin=origin)
    rows = sorted(set(buy) | set(sell) | set(unknown))
    start, end = rows[0], rows[-1]
    values = [0] * (end - start + 1)
    for row in rows:
        values[row - start] = (
            int(buy.get(row, 0)) + int(sell.get(row, 0)) + int(unknown.get(row, 0))
        )
    mass_total = sum(values)
    maximum = max(values) if values else 0
    modes = tuple(start + i for i, height in enumerate(values) if height == maximum) if maximum else ()
    scalar = (min(modes) if spec['poc_tie'] == 'lower' else max(modes)) if modes else None
    plateaus = []
    index = 0
    n_values = len(values)
    while index < n_values:
        height = int(values[index])
        last = index
        while last + 1 < n_values and int(values[last + 1]) == height:
            last += 1
        if height == maximum and maximum:
            plateaus.append((start + index, start + last))
        index = last + 1
    selected = []
    achieved = 0
    if scalar is not None:
        low = high = scalar
        selected = [scalar]
        achieved = int(values[scalar - start])
        target_left = mass_total * int(numer)
        while achieved * int(denom) < target_left and (low > start or high < end):
            left = int(values[low - start - 1]) if low > start else None
            right = int(values[high - start + 1]) if high < end else None
            if left is None and right is None:
                break
            if left is None:
                choices = ('right',)
            elif right is None:
                choices = ('left',)
            elif left > right:
                choices = ('left',)
            elif right > left:
                choices = ('right',)
            elif spec['value_tie'] == 'both':
                choices = ('left', 'right')
            elif spec['value_tie'] == 'lower':
                choices = ('left',)
            else:
                choices = ('right',)
            for choice in choices:
                if choice == 'left':
                    low -= 1
                    selected.append(low)
                    achieved += int(values[low - start])
                else:
                    high += 1
                    selected.append(high)
                    achieved += int(values[high - start])
    peaks, valleys = [], []
    index = 0
    while index < n_values:
        height = int(values[index])
        last = index
        while last + 1 < n_values and int(values[last + 1]) == height:
            last += 1
        a, b = start + index, start + last
        left = 0 if a == start else int(values[a - start - 1])
        right = 0 if b == end else int(values[b - start + 1])
        if height > 0 and height > left and height > right:
            peaks.append((a, b))
        if a > start and b < end and height < left and height < right:
            valleys.append((a, b))
        index = last + 1
    requested = Fraction(int(mass_total) * int(numer), int(denom))
    overshoot = max(Fraction(0), Fraction(int(achieved)) - requested)
    unique_heights = sorted({int(v) for v in values})
    second = unique_heights[-2] if len(unique_heights) > 1 else 0
    dominance = Fraction(int(maximum) - int(second))
    sq = 0
    mean_num = 0
    for offset, raw in enumerate(values):
        height = int(raw)
        sq += height * height
        mean_num += (int(start) + offset) * height
    concentration = Fraction(sq, int(mass_total) * int(mass_total)) if mass_total else None
    mean_row = Fraction(mean_num, int(mass_total)) if mass_total else None
    val = min(selected) if selected else None
    vah = max(selected) if selected else None
    compact = {
        'poc_set': modes,
        'poc_count': len(modes),
        'scalar_poc': None if scalar is None else int(scalar),
        'maximum_plateau_lows': tuple(a for a, _ in plateaus),
        'maximum_plateau_highs': tuple(b for _, b in plateaus),
        'value_rows': tuple(sorted(selected)),
        'val_row': val,
        'vah_row': vah,
        'va_width_ticks': None if val is None or vah is None else int(vah - val),
        'grid_width': width,
        'grid_origin': origin,
        'physical_poc_ticks': physical_tick(scalar, width=width, origin=origin),
        'physical_val_ticks': physical_tick(val, width=width, origin=origin),
        'physical_vah_ticks': physical_tick(vah, width=width, origin=origin),
        'va_width_physical_ticks': None if val is None or vah is None else int(vah - val) * width,
        'requested_mass_num': encode_exact_int(requested.numerator)[0],
        'requested_mass_num_text': encode_exact_int(requested.numerator)[1],
        'requested_mass_den': requested.denominator,
        'achieved_mass_num': encode_exact_int(achieved)[0],
        'achieved_mass_num_text': encode_exact_int(achieved)[1],
        'achieved_mass_den': 1,
        'overshoot_num': encode_exact_int(overshoot.numerator)[0],
        'overshoot_num_text': encode_exact_int(overshoot.numerator)[1],
        'overshoot_den': overshoot.denominator,
        'peak_lows': tuple(a for a, _ in peaks),
        'peak_highs': tuple(b for _, b in peaks),
        'peak_count': len(peaks),
        'valley_lows': tuple(a for a, _ in valleys),
        'valley_highs': tuple(b for _, b in valleys),
        'valley_count': len(valleys),
        'mean_row_num': encode_exact_int(_fraction_pair(mean_row)[0])[0],
        'mean_row_num_text': encode_exact_int(_fraction_pair(mean_row)[0])[1],
        'mean_row_den': _fraction_pair(mean_row)[1],
        'dominance_margin_num': encode_exact_int(_fraction_pair(dominance)[0])[0],
        'dominance_margin_num_text': encode_exact_int(_fraction_pair(dominance)[0])[1],
        'dominance_margin_den': _fraction_pair(dominance)[1],
        'concentration_num': encode_exact_int(_fraction_pair(concentration)[0])[0],
        'concentration_num_text': encode_exact_int(_fraction_pair(concentration)[0])[1],
        'concentration_den': _fraction_pair(concentration)[1],
        'low_overflow_buy': 0,
        'low_overflow_sell': 0,
        'low_overflow_unknown': 0,
        'high_overflow_buy': 0,
        'high_overflow_sell': 0,
        'high_overflow_unknown': 0,
        'unpriced_buy': int(mass.unpriced[0]),
        'unpriced_sell': int(mass.unpriced[1]),
        'unpriced_unknown': int(mass.unpriced[2]),
        'geometry_status': 'complete',
    }
    return compact


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
    span = max(1, (raw_high - raw_low) // int(width) + 8)
    grid = FrozenGrid(
        int(origin), int(width),
        (raw_low - int(origin)) // int(width),
        (raw_high - int(origin)) // int(width),
        f'{coordinate_identity}:w{width}:o{origin}',
        int(known_at_ns),
        max(DEFAULT_PRICE_CELLS, span),
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


def compact_geometry(result, *, view=None, width=1, origin=0):
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
    scalar = None if result.get('scalar_poc') is None else int(result['scalar_poc'])
    return {
        'poc_set': tuple(int(v) for v in poc),
        'poc_count': len(poc),
        'scalar_poc': scalar,
        'maximum_plateau_lows': tuple(int(a) for a, _ in plateaus),
        'maximum_plateau_highs': tuple(int(b) for _, b in plateaus),
        'value_rows': tuple(int(v) for v in value_rows),
        'val_row': val,
        'vah_row': vah,
        'va_width_ticks': None if val is None or vah is None else int(vah - val),
        'grid_width': int(width),
        'grid_origin': int(origin),
        'physical_poc_ticks': physical_tick(scalar, width=width, origin=origin),
        'physical_val_ticks': physical_tick(val, width=width, origin=origin),
        'physical_vah_ticks': physical_tick(vah, width=width, origin=origin),
        'va_width_physical_ticks': None if val is None or vah is None else int(vah - val) * int(width),
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
    row = {
        'poc_set': None, 'poc_count': None, 'scalar_poc': None,
        'maximum_plateau_lows': None, 'maximum_plateau_highs': None,
        'value_rows': None, 'val_row': None, 'vah_row': None, 'va_width_ticks': None,
        'grid_width': None, 'grid_origin': None,
        'physical_poc_ticks': None, 'physical_val_ticks': None, 'physical_vah_ticks': None,
        'va_width_physical_ticks': None,
        'requested_mass_num': None, 'requested_mass_den': None,
        'achieved_mass_num': None, 'achieved_mass_den': None,
        'overshoot_num': None, 'overshoot_den': None,
        'peak_lows': None, 'peak_highs': None, 'peak_count': None,
        'valley_lows': None, 'valley_highs': None, 'valley_count': None,
        'mean_row_num': None, 'mean_row_den': None,
        'dominance_margin_num': None, 'dominance_margin_den': None,
        'concentration_num': None, 'concentration_den': None,
        'low_overflow_buy': None, 'low_overflow_sell': None, 'low_overflow_unknown': None,
        'high_overflow_buy': None, 'high_overflow_sell': None, 'high_overflow_unknown': None,
        'unpriced_buy': None, 'unpriced_sell': None, 'unpriced_unknown': None,
        'geometry_status': reason,
    }
    return row


def geometry_from_mass(mass, spec, *, coordinate_identity, known_at_ns, coverage_complete,
                       verify_kernel=False, anchor_kind='day'):
    if mass.sum_q <= 0:
        reason = 'no_priced_volume' if mass.unpriced_volume else 'unknown_priced_population'
        return null_geometry(reason=reason), None
    compact = integer_profile_geometry(mass, spec)
    if int(spec.get('smoothing_scale') or 0):
        view = mass_view_from_histogram(
            mass, coordinate_identity=coordinate_identity, known_at_ns=known_at_ns,
            width=1, origin=0, coverage_complete=coverage_complete and not mass.unpriced_volume,
        )
        shaped = apply_variant_view(view, spec)
        raw = geometry(shaped, definition=variant_definition(spec, anchor_kind=anchor_kind))
        compact = compact_geometry(raw, view=shaped, width=spec['width'], origin=spec['origin'])
    compact['geometry_status'] = (
        'complete' if coverage_complete and mass.unpriced_volume == 0 and mass.coordinate_complete
        else 'observed_partial'
    )
    if mass.unpriced_volume and not coverage_complete:
        compact['geometry_status'] = 'incomplete_unpriced'
    view = None
    if verify_kernel:
        view = mass_view_from_histogram(
            mass, coordinate_identity=coordinate_identity, known_at_ns=known_at_ns,
            width=1, origin=0, coverage_complete=coverage_complete and not mass.unpriced_volume,
        )
        shaped = apply_variant_view(view, spec)
        again = geometry(shaped, definition=variant_definition(spec, anchor_kind=anchor_kind))
        kernel = compact_geometry(again, view=shaped, width=spec['width'], origin=spec['origin'])
        if tuple(kernel.get('poc_set') or ()) != tuple(compact.get('poc_set') or ()):
            raise IntegrityError('geometry kernel parity failed on POC maximizers')
        if kernel.get('value_rows') != compact.get('value_rows'):
            raise IntegrityError('geometry kernel parity failed on value rows')
        if kernel.get('scalar_poc') != compact.get('scalar_poc'):
            raise IntegrityError('geometry kernel parity failed on scalar POC')
        compact = kernel
        view = shaped
    return compact, view


def bar_proxy_from_mass(mass, variant, *, coordinate_identity, known_at_ns, coverage_complete,
                        anchor_kind='day'):
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
    raw = geometry(view, definition=variant_definition(spec, anchor_kind=anchor_kind))
    compact = compact_geometry(raw, view=view, width=1, origin=0)
    compact['source_flat_bar_lost_mass'] = int(allocation['source_flat_bar_lost_mass'])
    compact['proxy_variant'] = variant
    compact['geometry_status'] = (
        'complete' if coverage_complete and sum(allocation['unpriced']) == 0 else 'observed_partial'
    )
    return compact, view


def _same_grid_wasserstein(prices, buys, sells, buy_tot, sell_tot):
    """1-Wasserstein between buy and sell CDFs on the exact same physical ticks."""
    if not buy_tot or not sell_tot or not prices:
        return None
    cdf_buy = cdf_sell = 0
    area = 0
    previous = prices[0]
    for price, buy, sell in zip(prices, buys, sells):
        width = int(price) - int(previous)
        if width:
            area += abs(cdf_buy * sell_tot - cdf_sell * buy_tot) * width
        cdf_buy += int(buy)
        cdf_sell += int(sell)
        previous = int(price)
    return Fraction(area, int(buy_tot) * int(sell_tot))


def compact_side_geometry(mass):
    prices = mass.prices()
    buys = [mass.buy.get(p, 0) for p in prices]
    sells = [mass.sell.get(p, 0) for p in prices]
    buy_tot = sum(buys)
    sell_tot = sum(sells)
    wasserstein = None
    if not buy_tot or not sell_tot:
        overlap = None
        tv = None
    else:
        overlap = Fraction(
            sum(min(b * sell_tot, s * buy_tot) for b, s in zip(buys, sells)),
            buy_tot * sell_tot,
        )
        tv = Fraction(
            sum(abs(b * sell_tot - s * buy_tot) for b, s in zip(buys, sells)),
            2 * buy_tot * sell_tot,
        )
        wasserstein = _same_grid_wasserstein(prices, buys, sells, buy_tot, sell_tot)
    deltas = []
    abs_mass = 0
    for price in prices:
        b, s, u = mass.sides_at(price)
        delta = b - s
        deltas.append((price, delta, b + s + u))
        abs_mass += abs(delta)
    if deltas:
        max_d = max(d for _, d, _ in deltas)
        min_d = min(d for _, d, _ in deltas)
        abs_peak = max(abs(d) for _, d, _ in deltas)
        max_rows = tuple(p for p, d, _ in deltas if d == max_d)
        min_rows = tuple(p for p, d, _ in deltas if d == min_d)
        abs_rows = tuple(p for p, d, _ in deltas if abs(d) == abs_peak)
    else:
        max_rows = min_rows = abs_rows = ()
    return {
        'side_overlap_num': _fraction_pair(overlap)[0],
        'side_overlap_den': _fraction_pair(overlap)[1],
        'side_total_variation_num': _fraction_pair(tv)[0],
        'side_total_variation_den': _fraction_pair(tv)[1],
        'side_wasserstein_num': _fraction_pair(wasserstein)[0],
        'side_wasserstein_den': _fraction_pair(wasserstein)[1],
        'delta_maximum_rows': max_rows,
        'delta_minimum_rows': min_rows,
        'absolute_peak_rows': abs_rows,
        'absolute_delta_mass_num': abs_mass,
        'absolute_delta_mass_den': 1,
        'signed_delta': mass.priced_volume and (
            sum(mass.buy.get(p, 0) for p in prices) - sum(mass.sell.get(p, 0) for p in prices)
        ),
    }


def compact_side_from_view(view):
    raw = side_geometry(view)
    out = compact_side_geometry(_mass_from_view(view))
    out['side_wasserstein_num'] = _fraction_pair(raw.get('wasserstein_ticks'))[0]
    out['side_wasserstein_den'] = _fraction_pair(raw.get('wasserstein_ticks'))[1]
    out['side_overlap_num'] = _fraction_pair(raw.get('overlap'))[0]
    out['side_overlap_den'] = _fraction_pair(raw.get('overlap'))[1]
    out['side_total_variation_num'] = _fraction_pair(raw.get('total_variation'))[0]
    out['side_total_variation_den'] = _fraction_pair(raw.get('total_variation'))[1]
    return out


def compact_footprint(mass, params):
    ratio = params['ratio']
    minimum_volume = params['minimum_volume']
    comparison = params['comparison']
    zero_opponent = params['zero_opponent']
    stack_n = params['minimum_stack_rows']
    prices = mass.prices()
    sides = {p: mass.sides_at(p) for p in prices}
    buy_rows, sell_rows = [], []
    for price in prices:
        b, s, u = sides[price]
        def qualify(numer, opponent_price, opponent_is_sell):
            other = sides.get(opponent_price)
            denom = 0 if other is None else (other[1] if opponent_is_sell else other[0])
            unknown = 0 if other is None else other[2]
            worst = denom + unknown
            if numer < minimum_volume:
                return False
            if zero_opponent == 'require_observed_opponent' and denom == 0:
                return False
            if worst == 0:
                return zero_opponent == 'infinite_if_minimum'
            return Fraction(numer, worst) >= ratio
        step = 1
        buy_opp = price - step if comparison == 'diagonal' else price
        sell_opp = price + step if comparison == 'diagonal' else price
        if qualify(b, buy_opp, True):
            buy_rows.append(price)
        if qualify(s, sell_opp, False):
            sell_rows.append(price)

    def stacks(rows):
        runs, current = [], []
        for row in rows:
            if current and row != current[-1] + 1:
                if len(current) >= stack_n:
                    runs.append(tuple(current))
                current = []
            current.append(row)
        if len(current) >= stack_n:
            runs.append(tuple(current))
        return runs

    return {
        'footprint_buy_imbalance_rows': len(buy_rows),
        'footprint_sell_imbalance_rows': len(sell_rows),
        'footprint_buy_stack_count': len(stacks(buy_rows)),
        'footprint_sell_stack_count': len(stacks(sell_rows)),
        'footprint_history_complete': mass.coverage_complete and mass.unpriced_volume == 0,
        'footprint_ratio_num': ratio.numerator,
        'footprint_ratio_den': ratio.denominator,
        'footprint_authority': params.get('authority'),
    }


def labelled_sd(variance):
    """Exact variance stays rational. SD is a labelled Decimal approximation.

    ``exact_sqrt`` is a high-precision Decimal square root, not an exact
    rational radical. Irrational variances still have a defined SD.
    """
    if variance is None or variance < 0:
        return None, None, 'undefined'
    approx = exact_sqrt(variance)
    if approx is None:
        return float(variance) ** 0.5, None, 'floating_sqrt_fallback'
    return float(approx), format(approx, 'f'), 'decimal_sqrt_approximation'


def vwap_bands(moments):
    mean = moments.get('vwap_ticks')
    variance = moments.get('variance_ticks_squared')
    empty = {
        'vwap_ticks_num': None, 'vwap_ticks_den': None,
        'variance_ticks_squared_num': None, 'variance_ticks_squared_den': None,
        'sd_ticks_approx': None, 'sd_representation': 'undefined',
        'sd_ticks_num': None, 'sd_ticks_den': None,
    }
    if mean is None:
        return empty
    sd_approx, sd_text, sd_kind = labelled_sd(variance)
    bands = {
        'vwap_ticks_num': int(mean.numerator),
        'vwap_ticks_den': int(mean.denominator),
        'variance_ticks_squared_num': None if variance is None else int(variance.numerator),
        'variance_ticks_squared_den': None if variance is None else int(variance.denominator),
        'sd_ticks_approx': sd_approx,
        'sd_representation': sd_kind,
        'sd_coefficient_text': sd_text,
        'sd_ticks_num': None,
        'sd_ticks_den': None,
    }
    for index, fraction in enumerate(VWAP_PERCENT_BANDS):
        bands[f'percent_band_{index}_low_num'] = int((mean * (1 - fraction)).numerator)
        bands[f'percent_band_{index}_low_den'] = int((mean * (1 - fraction)).denominator)
        bands[f'percent_band_{index}_high_num'] = int((mean * (1 + fraction)).numerator)
        bands[f'percent_band_{index}_high_den'] = int((mean * (1 + fraction)).denominator)
    if sd_approx is not None:
        mean_f = float(mean)
        for index, mult in enumerate(VWAP_SD_BANDS):
            width = float(mult) * sd_approx
            bands[f'sd_band_{index}_low_approx'] = mean_f - width
            bands[f'sd_band_{index}_high_approx'] = mean_f + width
    return bands


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


def _source_order(atom, *, fallback_key='first_priced_source_order'):
    order = atom.get(fallback_key)
    if order is not None:
        return int(order)
    return int(atom['event_start_ns'])


def _flow_path(atom):
    unpriced = atom.get('unpriced') or (0, 0, 0)
    buy = int(atom.get('priced_buy') or 0) + int(unpriced[0])
    sell = int(atom.get('priced_sell') or 0) + int(unpriced[1])
    unknown = int(atom.get('priced_unknown') or 0) + int(unpriced[2])
    return FlowPath(
        high=0, low=0, close=int(atom.get('priced_buy') or 0) - int(atom.get('priced_sell') or 0),
        buy=buy, sell=sell, unknown=unknown,
        prints=int(atom.get('prints') or 0),
    )


def to_atomic_trades(atom, anchor):
    first = last = first_priced = last_priced = high = low = None
    first_order = _source_order(atom, fallback_key='first_priced_source_order')
    last_order = _source_order(atom, fallback_key='last_priced_source_order')
    if last_order < first_order:
        last_order = first_order
    if atom.get('first_priced_ticks') is not None:
        first_priced = (
            atom.get('first_priced_event_ns') or atom['event_start_ns'],
            first_order,
            atom['first_priced_ticks'], atom.get('source_path') or anchor.source_lineage, 0,
        )
        first = first_priced
    if atom.get('last_priced_ticks') is not None:
        last_priced = (
            atom.get('last_priced_event_ns') or atom['event_end_ns'] - 1,
            last_order,
            atom['last_priced_ticks'], atom.get('source_path') or anchor.source_lineage, 0,
        )
        last = last_priced
    if atom.get('observed_high_ticks') is not None:
        high = (
            int(atom['observed_high_ticks']),
            atom.get('observed_high_at_ns') or atom['event_start_ns'],
            atom.get('observed_high_source_order') if atom.get('observed_high_source_order') is not None else first_order,
        )
    if atom.get('observed_low_ticks') is not None:
        low = (
            int(atom['observed_low_ticks']),
            atom.get('observed_low_at_ns') or atom['event_start_ns'],
            atom.get('observed_low_source_order') if atom.get('observed_low_source_order') is not None else first_order,
        )
    rows = tuple((int(row), int(buy), int(sell), int(unknown)) for row, buy, sell, unknown in atom['rows'])
    return AtomicTrades(
        root=anchor.root,
        contract_key=anchor.contract_key,
        instrument_id=anchor.instrument_id,
        source_lineage=anchor.source_lineage,
        evidence_id=atom.get('evidence_id') or digest({
            'path': atom.get('source_path'), 'start': atom['event_start_ns'],
            'end': atom['event_end_ns'], 'instrument_id': atom['instrument_id'],
            'cells': cells_content_hash(atom),
        }),
        start_ns=int(atom['event_start_ns']),
        end_ns=int(atom['event_end_ns']),
        known_at_ns=int(atom['known_at_ns']),
        source_complete=bool(atom.get('source_coverage_complete', True)),
        coordinate_complete=bool(atom.get('coordinate_complete', True)),
        start_source_order=atom.get('start_source_order'),
        paths=(_flow_path(atom),),
        rows=rows,
        unpriced=tuple(int(v) for v in atom['unpriced']),
        unpriced_prints=int(atom.get('unpriced_prints') or 0),
        first=first, last=last, first_priced=first_priced, last_priced=last_priced,
        high=high, low=low, sum_squared_sizes=0,
    )


def compact_pin069(record):
    if not record or record.get('status', '').startswith('unavailable'):
        return {
            'pin069_active': False,
            'pin069_origin_ns': None,
            'pin069_published_ns': record.get('known_at_ns') if record else None,
            'pin069_sum_close_volume': None,
            'pin069_bar_volume': None,
            'pin069_vwap_num': None,
            'pin069_vwap_den': None,
            'pin069_high_ticks': None,
            'pin069_high_state_unresolved': True,
            'pin069_unsupported_volume': None,
            'pin069_reset': False,
        }
    vwap = record.get('observed_bar_close_vwap_ticks')
    return {
        'pin069_active': True,
        'pin069_origin_ns': record.get('origin_ns'),
        'pin069_published_ns': record.get('known_at_ns'),
        'pin069_sum_close_volume': record.get('sum_bar_close_volume'),
        'pin069_bar_volume': record.get('bar_volume'),
        'pin069_close_volume': record.get('sum_bar_close_volume'),
        'pin069_vwap_num': None if vwap is None else int(vwap.numerator),
        'pin069_vwap_den': None if vwap is None else int(vwap.denominator),
        'pin069_high_ticks': None,
        'pin069_high_state_unresolved': False,
        'pin069_unsupported_volume': record.get('unsupported_bar_volume'),
        'pin069_reset': bool(record.get('reset')),
        'pin069_history_complete': record.get('history_complete'),
    }


def pin069_reanchor(atoms, *, cut_ns, window=None):
    """PIN069BarClose first/new-high reset; accumulated close×volume from reset."""
    if window is None:
        return {
            'pin069_active': False, 'pin069_origin_ns': None, 'pin069_published_ns': None,
            'pin069_close_volume': None, 'pin069_high_ticks': None, 'pin069_window_start_ns': None,
            'pin069_sum_close_volume': None, 'pin069_bar_volume': None,
        }
    engine = PIN069BarClose(window)
    last = None
    for atom in atoms:
        if atom['event_end_ns'] > cut_ns:
            break
        last = engine.add(to_atomic_trades(atom, window))
    out = compact_pin069(last)
    out['pin069_high_ticks'] = engine.high
    out['pin069_window_start_ns'] = window.start_ns
    return out


class IncrementalPIN069:
    def __init__(self, window):
        self.window = window
        self.engine = PIN069BarClose(window)
        self.last = None
        self.last_end = None

    def add(self, atom):
        if self.last_end is not None and atom['event_start_ns'] < self.last_end:
            return
        try:
            self.last = self.engine.add(to_atomic_trades(atom, self.window))
            self.last_end = atom['event_end_ns']
            return self.last
        except (ContractError, IntegrityError) as exc:
            self.last = {'status': 'unavailable_source_high_state', 'reason': str(exc)}
            return self.last

    def snapshot(self):
        out = compact_pin069(self.last)
        out['pin069_high_ticks'] = self.engine.high
        out['pin069_window_start_ns'] = self.window.start_ns
        return out


def tpo_from_atoms(anchor, atoms, *, event_end_ns, decision_cut_ns, latency_ns,
                   bracket_minutes=30, representation='whole_trade_visits'):
    tpo = AnchorTPO(anchor, bracket_minutes=bracket_minutes, representation=representation)
    delay = None
    for atom in atoms:
        tpo.add(to_atomic_trades(atom, anchor))
        delay = int(atom['known_at_ns']) - int(atom['event_end_ns'])
    used_latency = delay if delay is not None else latency_ns
    known = tpo.known_at
    cut = decision_cut_ns if decision_cut_ns >= known else known
    return tpo.record(event_end_ns=event_end_ns, decision_cut_ns=cut, latency_ns=used_latency)


def compact_tpo(record, *, failed=False, reason=None):
    if failed:
        return {
            'tpo_status': 'failed',
            'tpo_reason': reason,
            'representation': None,
            'bracket_minutes': None,
            'complete_brackets': None,
            'observed_nonempty_brackets': None,
            'formation_final': None,
            'price_history_complete': None,
            'visit_rows': None,
            'visit_count': None,
            'provisional_single_print_rows': None,
            'final_single_print_rows': None,
            'legacy_five_bracket_final_single_print_rows': None,
            'low_tail_rows': None,
            'high_tail_rows': None,
            'ib30_complete': None,
            'ib60_complete': None,
            'ib30_high': None,
            'ib30_low': None,
            'ib60_high': None,
            'ib60_low': None,
            'known_at_ns': None,
            'quiet_brackets_retained': True,
        }
    visits = tuple(int(row) for row, _, _ in record.get('rows') or ())
    singles = record.get('provisional_single_print_rows')
    finals = record.get('final_single_print_rows')
    legacy = record.get('legacy_source_five_bracket_final_single_print_rows')
    return {
        'tpo_status': 'observed',
        'tpo_reason': None,
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
        'bracket_schedule': record.get('bracket_schedule'),
        'quiet_brackets_retained': True,
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

    return {
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
    prices = mass.prices()
    lower = min(prices) if prices else 0
    upper = max(prices) + 1 if prices else 1
    future = IntegerMass()
    low = [0, 0, 0]
    high = [0, 0, 0]
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
    else:
        row, _ = geometry_from_mass(
            future, spec, coordinate_identity=coordinate_identity,
            known_at_ns=known_at_ns, coverage_complete=coverage_complete,
        )
    row['future_low_overflow_buy'] = low[0]
    row['future_low_overflow_sell'] = low[1]
    row['future_low_overflow_unknown'] = low[2]
    row['future_high_overflow_buy'] = high[0]
    row['future_high_overflow_sell'] = high[1]
    row['future_high_overflow_unknown'] = high[2]
    row['future_grid_origin_ticks'] = 0
    row['future_grid_width_ticks'] = 1
    row['future_grid_lower_row'] = lower
    row['future_grid_upper_row'] = upper - 1
    return row, SimpleNamespace(lower_row=lower, upper_row=upper - 1, origin_ticks=0, width_ticks=1)


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
        return (int(end_ns),) if end_ns > start_ns and end_ns % stride_ns == 0 else ()
    return tuple(range(int(first), int(end_ns) + 1, int(stride_ns)))


def publication_known(*, input_known_ns, selection_known_ns, cut_ns, latency_ns):
    known = max(int(input_known_ns), int(selection_known_ns), int(cut_ns) + int(latency_ns))
    return known


def delayed_selection_blocks_origin(selection_known_ns, origin_ns):
    return int(selection_known_ns) > int(origin_ns)


def _civil_period_end(day, variant):
    nxt = day + timedelta(days=1)
    if variant == 'civil_ny_week':
        return day.weekday() == 6
    if variant == 'civil_ny_month':
        return nxt.month != day.month
    if variant == 'civil_ny_quarter':
        return nxt.month != day.month and day.month in (3, 6, 9, 12)
    if variant == 'civil_ny_year':
        return day.month == 12 and day.day == 31
    return False


def _civil_period_key(day, variant):
    if variant == 'civil_ny_week':
        return (variant, day - timedelta(days=day.weekday()))
    if variant == 'civil_ny_month':
        return (variant, day.replace(day=1))
    if variant == 'civil_ny_quarter':
        month = 1 + 3 * ((day.month - 1) // 3)
        return (variant, date(day.year, month, 1))
    if variant == 'civil_ny_year':
        return (variant, date(day.year, 1, 1))
    return (variant, day)


def _owning_atom(atoms, cut_ns, fallback=None):
    if cut_ns is None:
        return fallback
    contained = fallback
    for atom in atoms or ():
        start = atom.get('acquired_event_start_ns')
        end = atom.get('acquired_event_end_ns')
        if start is None or end is None:
            start = atom.get('event_start_ns')
            end = atom.get('event_end_ns')
        if start is None or end is None:
            continue
        start_i, end_i, cut_i = int(start), int(end), int(cut_ns)
        if start_i < end_i and end_i == cut_i:
            return atom
        if start_i <= cut_i < end_i:
            contained = atom
    return contained


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


def alias_index_key(atom):
    return (
        atom.get('source_collection'),
        atom.get('instrument_id'),
        atom.get('contract_key'),
        atom.get('event_start_ns'),
        atom.get('event_end_ns'),
    )


def content_alias_key(atom):
    return (
        atom.get('canonical_raw_values_sha256') or cells_content_hash(atom),
        atom.get('instrument_id'),
        atom.get('contract_key'),
        atom.get('event_start_ns'),
        atom.get('event_end_ns'),
        cells_content_hash(atom),
    )


class AliasIndex:
    """O(1) exact-alias collapse. Compact keys only; prune by unit watermark."""

    def __init__(self):
        self.by_slot = {}
        self.by_content = {}
        self.conflicts = []
        self.poisoned = {}
        self.retracted = []

    def _record(self, atom, content):
        return {
            'content': content,
            'event_start_ns': atom['event_start_ns'],
            'event_end_ns': atom['event_end_ns'],
            'instrument_id': atom.get('instrument_id'),
            'contract_key': atom.get('contract_key'),
            'source_path': atom.get('source_path'),
            'identity': atom_identity_key(atom),
        }

    def add(self, atom):
        slot = alias_index_key(atom)
        content = content_alias_key(atom)
        if slot in self.poisoned:
            return None
        prior = self.by_slot.get(slot)
        if prior is not None:
            if prior['content'] == content:
                return None
            self.conflicts.append({'left': atom_identity_key(atom), 'right': prior['identity']})
            self.poisoned[slot] = prior['event_end_ns']
            self.retracted.append(prior)
            self.by_slot.pop(slot, None)
            self.by_content.pop(prior['content'], None)
            return None
        other = self.by_content.get(content)
        if other is not None:
            return None
        rec = self._record(atom, content)
        self.by_slot[slot] = rec
        self.by_content[content] = rec
        return atom

    def prune(self, watermark_ns):
        if watermark_ns is None:
            return
        doomed = [
            slot for slot, rec in self.by_slot.items()
            if int(rec['event_end_ns']) <= int(watermark_ns)
        ]
        for slot in doomed:
            rec = self.by_slot.pop(slot)
            self.by_content.pop(rec['content'], None)
        expired = [slot for slot, end in self.poisoned.items() if int(end) <= int(watermark_ns)]
        for slot in expired:
            self.poisoned.pop(slot, None)


def dedup_atoms(atoms):
    index = AliasIndex()
    kept = []
    for atom in atoms:
        accepted = index.add(atom)
        if accepted is not None:
            kept.append(accepted)
    return kept, tuple(index.conflicts)


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
        del table
    return rows, counted


def window_rows_from_tables(tables):
    return observation_rows_from_tables(tables)


def load_measurement_cells(unit):
    """Read one measurement JSON, extract atoms, and drop the payload."""
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
    payload = read_json_artifact(ref)
    extracted = extract_unit_cells(payload)
    del payload
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
        merged['acquired_event_start_ns'] = merged['source_window_start_ns']
        merged['acquired_event_end_ns'] = merged['source_window_end_ns']
        if merged.get('contract_key') is None:
            merged['contract_key'] = obs.get('contract_key')
        if obs.get('sum_price_volume') is not None:
            merged['sum_price_volume'] = obs['sum_price_volume']
        if obs.get('sum_price_squared_volume') is not None:
            merged['sum_price_squared_volume'] = obs['sum_price_squared_volume']
        out.append(merged)
    return out


def _schema_names(schema_fn, cache_name):
    global _GEOMETRY_NAMES, _TPO_NAMES, _JOIN_NAMES, _CELL_NAMES
    current = {'_GEOMETRY_NAMES': _GEOMETRY_NAMES, '_TPO_NAMES': _TPO_NAMES,
               '_JOIN_NAMES': _JOIN_NAMES, '_CELL_NAMES': _CELL_NAMES}[cache_name]
    if current is None:
        current = tuple(field.name for field in schema_fn(_require_pyarrow()))
        if cache_name == '_GEOMETRY_NAMES':
            _GEOMETRY_NAMES = current
        elif cache_name == '_TPO_NAMES':
            _TPO_NAMES = current
        elif cache_name == '_JOIN_NAMES':
            _JOIN_NAMES = current
        else:
            _CELL_NAMES = current
    return current


def geometry_schema(pa):
    def i64(name, nullable=True):
        return pa.field(name, pa.int64(), nullable=nullable)

    def f64(name):
        return pa.field(name, pa.float64(), nullable=True)

    def flag(name):
        return pa.field(name, pa.bool_(), nullable=True)

    def text(name, nullable=True):
        return pa.field(name, pa.string(), nullable=nullable)

    def lst(name):
        return pa.field(name, pa.list_(pa.int64()), nullable=True)

    return pa.schema([
        text('source_collection', nullable=False), text('root', nullable=False),
        i64('year', nullable=False), text('stage'), text('session'),
        text('anchor_id'), text('anchor_variant'), text('anchor_kind'),
        text('geometry_id'), text('geometry_variant'), text('proxy_variant'),
        text('source_path'), text('source_metadata_sha256'), text('source_variant'),
        text('canonical_raw_values_sha256'), text('measurement_sha256'),
        text('contract_key'), i64('instrument_id'), i64('raw_instrument_id'),
        i64('acquired_event_start_ns'), i64('acquired_event_end_ns'),
        i64('anchor_start_ns'), i64('anchor_end_ns'), i64('anchor_span_ns'),
        i64('selection_known_ns'), i64('cut_ns'), i64('published_known_ns'),
        i64('input_known_ns'), i64('actual_known_at_ns'), i64('scenario_known_at_ns'),
        text('economic_date'), flag('coverage_complete'), flag('formation_complete'),
        flag('prefix_complete'), flag('eligible_complete'), text('geometry_status'),
        text('completed_geometry_id'),
        lst('poc_set'), i64('poc_count'), i64('scalar_poc'),
        lst('maximum_plateau_lows'), lst('maximum_plateau_highs'),
        lst('value_rows'), i64('val_row'), i64('vah_row'), i64('va_width_ticks'),
        i64('grid_width'), i64('grid_origin'),
        i64('physical_poc_ticks'), i64('physical_val_ticks'), i64('physical_vah_ticks'),
        i64('va_width_physical_ticks'),
        i64('requested_mass_num'), text('requested_mass_num_text'), i64('requested_mass_den'),
        i64('achieved_mass_num'), text('achieved_mass_num_text'), i64('achieved_mass_den'),
        i64('overshoot_num'), text('overshoot_num_text'), i64('overshoot_den'),
        lst('peak_lows'), lst('peak_highs'), i64('peak_count'),
        lst('valley_lows'), lst('valley_highs'), i64('valley_count'),
        i64('mean_row_num'), text('mean_row_num_text'), i64('mean_row_den'),
        i64('dominance_margin_num'), text('dominance_margin_num_text'), i64('dominance_margin_den'),
        i64('concentration_num'), text('concentration_num_text'), i64('concentration_den'),
        i64('low_overflow_buy'), i64('low_overflow_sell'), i64('low_overflow_unknown'),
        i64('high_overflow_buy'), i64('high_overflow_sell'), i64('high_overflow_unknown'),
        i64('unpriced_buy'), i64('unpriced_sell'), i64('unpriced_unknown'),
        i64('priced_volume'), i64('sum_price_volume'), i64('sum_price_squared_volume'),
        i64('vwap_ticks_num'), i64('vwap_ticks_den'),
        i64('variance_ticks_squared_num'), i64('variance_ticks_squared_den'),
        f64('sd_ticks_approx'), text('sd_representation'), text('sd_coefficient_text'),
        f64('sd_band_0_low_approx'), f64('sd_band_0_high_approx'),
        f64('sd_band_1_low_approx'), f64('sd_band_1_high_approx'),
        f64('sd_band_2_low_approx'), f64('sd_band_2_high_approx'),
        f64('sd_band_3_low_approx'), f64('sd_band_3_high_approx'),
        i64('percent_band_0_low_num'), i64('percent_band_0_low_den'),
        i64('percent_band_0_high_num'), i64('percent_band_0_high_den'),
        i64('percent_band_1_low_num'), i64('percent_band_1_low_den'),
        i64('percent_band_1_high_num'), i64('percent_band_1_high_den'),
        i64('percent_band_2_low_num'), i64('percent_band_2_low_den'),
        i64('percent_band_2_high_num'), i64('percent_band_2_high_den'),
        i64('q_1_20_num'), i64('q_1_20_den'), i64('q_1_4_num'), i64('q_1_4_den'),
        i64('q_1_2_num'), i64('q_1_2_den'), i64('q_3_4_num'), i64('q_3_4_den'),
        i64('q_19_20_num'), i64('q_19_20_den'),
        i64('weighted_median_num'), i64('weighted_median_den'),
        i64('mad_num'), i64('mad_den'), i64('robust_scale_num'), i64('robust_scale_den'),
        i64('source_flat_bar_lost_mass'),
        i64('side_overlap_num'), i64('side_overlap_den'),
        i64('side_total_variation_num'), i64('side_total_variation_den'),
        i64('side_wasserstein_num'), i64('side_wasserstein_den'),
        i64('absolute_delta_mass_num'), i64('absolute_delta_mass_den'), i64('signed_delta'),
        lst('delta_maximum_rows'), lst('delta_minimum_rows'), lst('absolute_peak_rows'),
        i64('footprint_buy_imbalance_rows'), i64('footprint_sell_imbalance_rows'),
        i64('footprint_buy_stack_count'), i64('footprint_sell_stack_count'),
        flag('footprint_history_complete'),
        i64('footprint_ratio_num'), i64('footprint_ratio_den'), text('footprint_authority'),
        i64('pin069_close_volume'), i64('pin069_sum_close_volume'), i64('pin069_bar_volume'),
        i64('pin069_high_ticks'), flag('pin069_active'), i64('pin069_origin_ns'),
        i64('pin069_published_ns'), i64('pin069_vwap_num'), i64('pin069_vwap_den'),
        flag('pin069_high_state_unresolved'), i64('pin069_unsupported_volume'), flag('pin069_reset'),
        flag('pin069_history_complete'), i64('pin069_window_start_ns'),
        i64('observed_open_ticks'), i64('observed_open_known_at_ns'),
        i64('observed_prior_close_ticks'), i64('observed_prior_close_known_at_ns'),
        i64('atom_count'), i64('input_cells'), i64('unpriced_only_atoms'),
        flag('selected_partition_member'),
        text('physical_contract_key'), text('source_lineage'),
        i64('formation_minutes'), text('provenance_paths'),
    ])


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
        text('anchor_id'), text('anchor_variant'), text('geometry_id'),
        text('representation'), text('tpo_status'), text('tpo_reason'),
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
        flag('quiet_brackets_retained'),
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
        text('anchor_id'), text('anchor_variant'), text('geometry_id'),
        text('geometry_variant'), text('source_path'),
        text('source_metadata_sha256'), text('source_variant'),
        i64('acquired_event_start_ns'), i64('acquired_event_end_ns'),
        text('contract_key'), i64('instrument_id'),
        i64('cut_ns'), i64('latency_ns'), text('horizon_kind'), i64('horizon_minutes'),
        i64('formation_minutes'),
        i64('actual_known_at_ns'), i64('scenario_known_at_ns'),
        i64('selection_known_ns'), i64('input_known_ns'),
        flag('formation_complete'), flag('coverage_known'), flag('prefix_complete'),
        flag('label_complete'), flag('same_stage'), flag('chronological_eligible'),
        text('join_status'), text('censor_reason'), text('scientific_reason'),
        text('join_window_reason'),
        i64('scalar_poc'), i64('val_row'), i64('vah_row'),
        i64('physical_poc_ticks'), i64('physical_val_ticks'), i64('physical_vah_ticks'),
        i64('future_high_ticks'), i64('future_low_ticks'), i64('future_last_ticks'),
        flag('poc_touch'), flag('poc_traverse'),
        flag('val_touch'), flag('val_traverse'),
        flag('vah_touch'), flag('vah_traverse'),
        flag('terminal_inside_va'), flag('terminal_outside_va'), flag('terminal_at_poc'),
        flag('touch_order_identified'),
        flag('boundary_moving'), flag('price_crossing_frozen_va'),
        i64('future_poc'), i64('future_val_row'), i64('future_vah_row'),
        i64('future_low_overflow_buy'), i64('future_low_overflow_sell'),
        i64('future_low_overflow_unknown'),
        i64('future_high_overflow_buy'), i64('future_high_overflow_sell'),
        i64('future_high_overflow_unknown'),
        flag('future_input_known'), flag('future_coverage_complete'),
        i64('future_input_known_at_ns'), text('future_mass_id'),
        i64('future_val'), i64('future_vah'),
        i64('future_low_overflow_unpriced'), i64('future_high_overflow_unpriced'),
        i64('future_unpriced_buy'), i64('future_unpriced_sell'), i64('future_unpriced_unknown'),
        flag('is_link_row'), flag('later_completed_link'),
        text('economic_date'),
        text('feature_id'), text('label_id'),
    ])


def cell_schema(pa):
    def i64(name, nullable=True):
        return pa.field(name, pa.int64(), nullable=nullable)

    def flag(name):
        return pa.field(name, pa.bool_(), nullable=True)

    def text(name, nullable=True):
        return pa.field(name, pa.string(), nullable=nullable)

    return pa.schema([
        text('source_path', nullable=False), i64('instrument_id', nullable=False),
        text('contract_key'), i64('event_start_ns', nullable=False),
        i64('event_end_ns', nullable=False), i64('known_at_ns'),
        i64('priced_buy'), i64('priced_sell'), i64('priced_unknown'),
        i64('unpriced_buy'), i64('unpriced_sell'), i64('unpriced_unknown'),
        i64('cell_count'), text('cells_sha256'),
        flag('unpriced_only'), flag('missing_cells'),
        text('measurement_sha256'), text('canonical_raw_values_sha256'),
        text('receipt_sha256'),
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


class ChunkWriter:
    """Typed Arrow chunks. Rows are released after each flush."""

    def __init__(self, outputs, name, schema, pa, *, on_row=None):
        self.series = ParquetSeries(outputs, name, encoding='plain')
        self.schema = schema
        self.pa = pa
        self.buf = []
        self.rows = 0
        self.on_row = on_row
        self._empty_written = False

    def append(self, row):
        if self.on_row is not None:
            self.on_row(row)
        self.buf.append(row)
        if len(self.buf) >= BATCH_HINT:
            self.flush()

    def flush(self):
        if not self.buf:
            return
        table = _table_from_rows(self.schema, self.buf, self.pa)
        self.series.append(table)
        self.rows += len(self.buf)
        self.buf.clear()
        del table

    def finish(self):
        self.flush()
        if self.rows == 0 and not self._empty_written:
            self.series.append(_table_from_rows(self.schema, [], self.pa))
            self._empty_written = True
        return self.series.finish()


def _empty_row(schema_fn, cache_name):
    return {name: None for name in _schema_names(schema_fn, cache_name)}


def _empty_geometry_row():
    return _empty_row(geometry_schema, '_GEOMETRY_NAMES')


def _empty_tpo_row():
    return _empty_row(tpo_schema, '_TPO_NAMES')


def _empty_join_row():
    return _empty_row(join_schema, '_JOIN_NAMES')


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


def geometry_id_for(*, anchor, variant_id, cut_ns, cells_hash, proxy=None):
    return digest({
        'anchor_id': None if anchor is None else anchor.id,
        'variant': variant_id,
        'proxy': proxy,
        'cut_ns': cut_ns,
        'cells': cells_hash,
    })


def _fill_geometry_identity(row, *, collection, root, year, stage, session, atom, anchor,
                            variant_id, proxy, cut_ns, published, economic, selected,
                            input_known, scenario_known, geometry_id, formation_minutes=None):
    row['source_collection'] = collection
    row['root'] = root
    row['year'] = year
    row['stage'] = stage
    row['session'] = session
    row['anchor_id'] = None if anchor is None else anchor.id
    row['anchor_variant'] = None if anchor is None else anchor.variant
    row['anchor_kind'] = None if anchor is None else anchor.kind
    row['geometry_id'] = geometry_id
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
    row['source_lineage'] = None if atom is None else atom.get('source_lineage')
    row['acquired_event_start_ns'] = None if atom is None else atom.get('acquired_event_start_ns')
    row['acquired_event_end_ns'] = None if atom is None else atom.get('acquired_event_end_ns')
    if anchor is not None:
        row['anchor_start_ns'] = anchor.start_ns
        row['anchor_end_ns'] = anchor.end_ns
        row['anchor_span_ns'] = anchor.end_ns - anchor.start_ns
        row['selection_known_ns'] = anchor.selection_known_at_ns
    row['cut_ns'] = cut_ns
    row['published_known_ns'] = published
    row['input_known_ns'] = input_known
    row['actual_known_at_ns'] = input_known
    row['scenario_known_at_ns'] = scenario_known
    row['economic_date'] = economic
    row['selected_partition_member'] = selected
    row['formation_minutes'] = formation_minutes


def _merge_compact(row, compact):
    for key, value in compact.items():
        row[key] = value


def emit_geometry_payload(*, mass, spec, coordinate_identity, known_at_ns,
                          coverage_complete, include_side, include_vwap, include_footprint,
                          footprint_params, verify_kernel=False, anchor_kind='day',
                          pin069=None):
    compact, view = geometry_from_mass(
        mass, spec, coordinate_identity=coordinate_identity, known_at_ns=known_at_ns,
        coverage_complete=coverage_complete, verify_kernel=verify_kernel,
        anchor_kind=anchor_kind,
    )
    extras = {}
    if include_side:
        if view is not None:
            extras.update(compact_side_from_view(view))
        else:
            extras.update(compact_side_geometry(mass))
    if include_vwap:
        extras.update(vwap_bands(mass.vwap_moments()))
        extras.update(weighted_quantiles(mass))
        if pin069 is not None:
            extras.update(pin069)
    if include_footprint:
        extras.update(compact_footprint(mass, footprint_params))
    moments = mass.vwap_moments()
    extras['priced_volume'] = mass.priced_volume
    extras['sum_price_volume'] = moments['sum_price_volume']
    extras['sum_price_squared_volume'] = moments['sum_price_squared_volume']
    extras['atom_count'] = mass.atom_count
    extras['input_cells'] = mass.input_cells
    extras['unpriced_only_atoms'] = mass.unpriced_only_atoms
    extras['observed_open_ticks'] = mass.first_priced_ticks
    extras['observed_open_known_at_ns'] = mass.first_priced_known_at_ns
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


def _latency_value(row):
    value = row.get('latency_ns')
    if value is None:
        return None
    return int(value)


def _window_identity_tuple(row, *, path=None, root=None, start=None, end=None):
    return (
        row.get('root') or root,
        row.get('source_path') or path,
        row.get('source_metadata_sha256'),
        row.get('source_variant'),
        row.get('acquired_event_start_ns', start),
        row.get('acquired_event_end_ns', end),
        row.get('instrument_id'),
        row.get('contract_key'),
        row.get('cut_ns'),
    )


class WindowUnitCache:
    """Load one window unit's feature/label arrays; release on unit change."""

    def __init__(self, window_units):
        self.units = list(window_units or [])
        self._by_path = defaultdict(list)
        for unit in self.units:
            path = (unit.get('source_identity') or {}).get('source_path') or unit.get('source_path')
            self._by_path[path].append(unit)
        self._current = None
        self.index = {}
        self.stats = {'window_units_read': 0, 'feature_rows': 0, 'label_rows': 0}

    def _load(self, unit):
        if unit.get('features') is None or unit.get('labels') is None:
            self.index = {}
            return
        features, n_feat = window_rows_from_tables(read_series_tables(unit['features']))
        labels, n_lab = window_rows_from_tables(read_series_tables(unit['labels']))
        self.stats['window_units_read'] += 1
        self.stats['feature_rows'] += n_feat
        self.stats['label_rows'] += n_lab
        ident = unit.get('source_identity') or {}
        path = ident.get('source_path') or unit.get('source_path')
        root = ident.get('root') or unit.get('root')
        start = ident.get('acquired_event_start_ns')
        end = ident.get('acquired_event_end_ns')
        labels_by = defaultdict(list)
        for label in labels:
            labels_by[_window_identity_tuple(label, path=path, root=root, start=start, end=end)].append(label)
        index = {}
        for feature in features:
            key = _window_identity_tuple(feature, path=path, root=root, start=start, end=end)
            bucket = index.get(key)
            if bucket is None:
                bucket = {'features': [], 'labels': labels_by.get(key, [])}
                index[key] = bucket
            bucket['features'].append(feature)
        self.index = index
        del features, labels

    def ensure(self, path, cut_ns):
        units = self._by_path.get(path) or []
        chosen = None
        for unit in units:
            ident = unit.get('source_identity') or {}
            start = ident.get('acquired_event_start_ns', unit.get('cut_start_ns'))
            end = ident.get('acquired_event_end_ns', unit.get('cut_end_ns'))
            if start is None or end is None:
                chosen = unit
                break
            if int(start) < int(end) and int(end) == int(cut_ns):
                chosen = unit
                break
            if int(start) <= int(cut_ns) < int(end):
                chosen = unit
                break
        if chosen is None and units:
            chosen = units[0]
        if chosen is not self._current:
            self._current = chosen
            if chosen is not None:
                self._load(chosen)
            else:
                self.index = {}
        return self.index

    def lookup(self, *, path, root, metadata, variant, acquired_start, acquired_end,
               instrument_id, contract_key, cut_ns):
        self.ensure(path, cut_ns)
        key = (root, path, metadata, variant, acquired_start, acquired_end,
               instrument_id, contract_key, cut_ns)
        found = self.index.get(key)
        if found is not None:
            return found
        for stored, payload in self.index.items():
            if (
                stored[1] == path and stored[0] == root and stored[6] == instrument_id
                and stored[7] == contract_key and stored[8] == cut_ns
                and stored[2] == metadata and stored[3] == variant
                and stored[4] == acquired_start and stored[5] == acquired_end
            ):
                return payload
        return None


def _following_atoms(atoms, *, cut_ns, horizon_ns, instrument_id, contract_key, collection):
    out = []
    for atom in atoms:
        if atom.get('instrument_id') != instrument_id or atom.get('contract_key') != contract_key:
            continue
        if atom.get('source_collection') not in (None, collection):
            continue
        if atom['event_start_ns'] >= cut_ns and atom['event_end_ns'] <= cut_ns + horizon_ns:
            out.append(atom)
    return out


def _feature_ready(feature):
    if feature is None:
        return False, 'missing_feature'
    for name in FEATURE_QUALITY_FLAGS:
        if feature.get(name) is not True:
            return False, f'missing_feature_quality:{name}'
    return True, None


def _feature_for_arm(features, formation, latency):
    chosen = None
    for feature in features:
        if feature is None:
            continue
        form = feature.get('formation_minutes')
        if form is None or int(form) != int(formation):
            continue
        feat_lat = _latency_value(feature)
        if feat_lat is not None and feat_lat != int(latency):
            continue
        chosen = feature
        if feat_lat == int(latency):
            return feature
    return chosen


def _scenario_publication(geometry_row, latency):
    source_pub = geometry_row.get('published_known_ns')
    if source_pub is None:
        return None
    scenario = int(source_pub) - SOURCE_LATENCY_NS + int(latency)
    selection = geometry_row.get('selection_known_ns')
    incoming = geometry_row.get('input_known_ns')
    if selection is not None:
        scenario = max(scenario, int(selection))
    if incoming is not None:
        scenario = max(scenario, int(incoming))
    return scenario


def _own_geometry_ready(geometry_row):
    return (
        geometry_row.get('eligible_complete') is True
        and geometry_row.get('coverage_complete') is True
        and geometry_row.get('prefix_complete') is True
        and geometry_row.get('geometry_status') == 'complete'
        and geometry_row.get('contract_key') not in (None, '')
    )


def emit_join_rows(*, writer, completeness, windows, geometry_row, feature_lookup,
                   cut_ns, collection, root, year, stage, session, economic,
                   identity_atoms, mass, motion, later_link=False, future_cache):
    sample_path = geometry_row.get('source_path')
    match = None
    if feature_lookup is not None:
        match = feature_lookup
    if match is None and windows is not None:
        match = windows.lookup(
            path=sample_path, root=root,
            metadata=geometry_row.get('source_metadata_sha256'),
            variant=geometry_row.get('source_variant'),
            acquired_start=geometry_row.get('acquired_event_start_ns'),
            acquired_end=geometry_row.get('acquired_event_end_ns'),
            instrument_id=geometry_row.get('instrument_id'),
            contract_key=geometry_row.get('contract_key'),
            cut_ns=cut_ns,
        )
    features = [] if match is None else list(
        match.get('features') or ([match['feature']] if match.get('feature') else ())
    )
    labels = [] if match is None else list(match.get('labels') or ())
    if match is None:
        completeness['joins_missing'] += 1
        features = []
    prefix_ok = geometry_row.get('prefix_complete') is True
    coverage_ok = geometry_row.get('coverage_complete') is True
    source_pub = geometry_row.get('published_known_ns')
    for formation in FORMATION_MINUTES:
        for latency in LATENCY_NS:
            feature = _feature_for_arm(features, formation, latency)
            for horizon_kind in HORIZON_KINDS:
                horizons = FORWARD_HORIZONS_MINUTES if horizon_kind == 'fixed_minutes' else (None,)
                for horizon in horizons:
                    label = None
                    for candidate in labels:
                        cand_lat = _latency_value(candidate)
                        if cand_lat is None or cand_lat != int(latency):
                            continue
                        if candidate.get('horizon_kind') != horizon_kind:
                            continue
                        if horizon_kind == 'fixed_minutes':
                            minutes = candidate.get('horizon_minutes')
                            if minutes is None or int(minutes) != int(horizon):
                                continue
                        label = candidate
                        break
                    row = _empty_join_row()
                    row.update({
                        'source_collection': collection, 'root': root, 'year': year,
                        'stage': stage, 'session': session,
                        'anchor_id': geometry_row.get('anchor_id'),
                        'anchor_variant': geometry_row.get('anchor_variant'),
                        'geometry_id': geometry_row.get('geometry_id'),
                        'geometry_variant': geometry_row.get('geometry_variant'),
                        'source_path': sample_path,
                        'source_metadata_sha256': geometry_row.get('source_metadata_sha256'),
                        'source_variant': geometry_row.get('source_variant'),
                        'acquired_event_start_ns': geometry_row.get('acquired_event_start_ns'),
                        'acquired_event_end_ns': geometry_row.get('acquired_event_end_ns'),
                        'contract_key': geometry_row.get('contract_key'),
                        'instrument_id': geometry_row.get('instrument_id'),
                        'cut_ns': cut_ns, 'latency_ns': int(latency),
                        'horizon_kind': horizon_kind, 'horizon_minutes': horizon,
                        'formation_minutes': int(formation),
                        'actual_known_at_ns': source_pub,
                        'scenario_known_at_ns': _scenario_publication(geometry_row, latency),
                        'selection_known_ns': geometry_row.get('selection_known_ns'),
                        'input_known_ns': geometry_row.get('input_known_ns'),
                        'formation_complete': prefix_ok,
                        'coverage_known': coverage_ok,
                        'prefix_complete': prefix_ok,
                        'economic_date': economic,
                        'is_link_row': True,
                        'later_completed_link': later_link,
                        'feature_id': None if feature is None else feature.get('formation_id'),
                        'label_id': None if label is None else label.get('label_id'),
                        'physical_poc_ticks': geometry_row.get('physical_poc_ticks'),
                        'physical_val_ticks': geometry_row.get('physical_val_ticks'),
                        'physical_vah_ticks': geometry_row.get('physical_vah_ticks'),
                        'scalar_poc': geometry_row.get('scalar_poc'),
                        'val_row': geometry_row.get('val_row'),
                        'vah_row': geometry_row.get('vah_row'),
                    })
                    if feature is None:
                        row['join_status'] = 'no_label'
                        row['censor_reason'] = 'missing_feature'
                        writer.append(row)
                        continue
                    if label is None:
                        row['join_status'] = 'no_label'
                        row['censor_reason'] = 'missing_label'
                        writer.append(row)
                        completeness['joins_missing'] += 1
                        continue
                    join = join_window_eligibility(feature, label)
                    scientific = scientific_join_eligibility(feature, label)
                    row['join_window_reason'] = join.get('reason')
                    row['scientific_reason'] = scientific.get('scientific_reason')
                    row['same_stage'] = join.get('eligible') is True
                    row['label_complete'] = label.get('complete') is True
                    row['chronological_eligible'] = label.get('chronological_eligible')
                    if join.get('stage'):
                        row['stage'] = join['stage']
                    feature_ok, feature_reason = _feature_ready(feature)
                    geometry_ready = _own_geometry_ready(geometry_row)
                    if not geometry_ready:
                        row['censor_reason'] = row.get('censor_reason') or 'own_geometry_incomplete'
                    own_ready = (
                        geometry_ready
                        and feature_ok
                        and join.get('eligible') is True
                        and scientific.get('eligible') is True
                        and label.get('complete') is True
                    )
                    if not own_ready:
                        row['join_status'] = (
                            'stage_leak' if scientific.get('scientific_reason') == 'label_maturity_not_same_named_stage'
                            else 'formation_incomplete' if not geometry_ready
                            else 'rejected'
                        )
                        if not feature_ok:
                            row['censor_reason'] = row.get('censor_reason') or feature_reason
                        if label.get('left_censored') or label.get('right_censored') or feature.get('stage_boundary'):
                            row['join_status'] = 'censored'
                        if label.get('no_new_trade') or label.get('no_priced_trade'):
                            row['join_status'] = 'no_event'
                        row['censor_reason'] = (
                            row.get('censor_reason') or scientific.get('scientific_reason') or join.get('reason')
                        )
                        writer.append(row)
                        completeness['joins_censored'] += 1
                        continue
                    contact = classify_future_contact(
                        poc=geometry_row.get('physical_poc_ticks', geometry_row.get('scalar_poc')),
                        val=geometry_row.get('physical_val_ticks', geometry_row.get('val_row')),
                        vah=geometry_row.get('physical_vah_ticks', geometry_row.get('vah_row')),
                        high=label.get('observed_high_ticks'),
                        low=label.get('observed_low_ticks'),
                        last=label.get('last_priced_ticks'),
                        complete=label.get('complete') is True,
                        no_new=bool(label.get('no_new_trade')),
                        no_priced=bool(label.get('no_priced_trade')),
                    )
                    row['join_status'] = contact['status']
                    row['censor_reason'] = contact.get('reason')
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
                    if horizon_kind == 'fixed_minutes' and horizon is not None:
                        cache_key = (geometry_row.get('geometry_id'), cut_ns, int(horizon))
                        if cache_key not in future_cache:
                            following = _following_atoms(
                                identity_atoms, cut_ns=cut_ns, horizon_ns=horizon * MINUTE_NS,
                                instrument_id=geometry_row.get('instrument_id'),
                                contract_key=geometry_row.get('contract_key'),
                                collection=collection,
                            )
                            intended = intended_atom_ends(cut_ns, cut_ns + horizon * MINUTE_NS)
                            present = {atom['event_end_ns'] for atom in following}
                            input_present = all(end in present for end in intended)
                            coverage_ok_future = all(
                                atom.get('source_coverage_complete', True) for atom in following
                            )
                            future_coverage = bool(input_present) and coverage_ok_future
                            future_known_at = None
                            for atom in following:
                                known = atom.get('known_at_ns')
                                if known is not None:
                                    future_known_at = int(known) if future_known_at is None else max(
                                        future_known_at, int(known)
                                    )
                            future_compact, _ = future_mass_on_frozen_grid(
                                mass, following,
                                coordinate_identity=f'{root}:{geometry_row.get("contract_key")}',
                                known_at_ns=future_known_at if future_known_at is not None else (
                                    geometry_row.get('published_known_ns') or cut_ns
                                ),
                                coverage_complete=future_coverage,
                            )
                            future_compact['future_mass_id'] = digest({
                                'geometry_id': geometry_row.get('geometry_id'),
                                'cut_ns': cut_ns, 'horizon': horizon,
                            })
                            future_cache[cache_key] = (
                                future_compact, input_present, future_coverage, future_known_at,
                            )
                        future_compact, input_present, future_coverage, future_known_at = future_cache[cache_key]
                        row['future_input_known'] = input_present
                        row['future_coverage_complete'] = future_coverage
                        row['future_input_known_at_ns'] = future_known_at
                        row['future_mass_id'] = future_compact.get('future_mass_id')
                        if future_coverage:
                            row['future_poc'] = future_compact.get('scalar_poc')
                            row['future_val_row'] = future_compact.get('val_row')
                            row['future_vah_row'] = future_compact.get('vah_row')
                            row['future_val'] = future_compact.get(
                                'physical_val_ticks', future_compact.get('val_row'))
                            row['future_vah'] = future_compact.get(
                                'physical_vah_ticks', future_compact.get('vah_row'))
                            row['future_low_overflow_buy'] = future_compact.get('future_low_overflow_buy')
                            row['future_low_overflow_sell'] = future_compact.get('future_low_overflow_sell')
                            row['future_low_overflow_unknown'] = future_compact.get('future_low_overflow_unknown')
                            row['future_high_overflow_buy'] = future_compact.get('future_high_overflow_buy')
                            row['future_high_overflow_sell'] = future_compact.get('future_high_overflow_sell')
                            row['future_high_overflow_unknown'] = future_compact.get('future_high_overflow_unknown')
                            row['future_unpriced_buy'] = future_compact.get('unpriced_buy')
                            row['future_unpriced_sell'] = future_compact.get('unpriced_sell')
                            row['future_unpriced_unknown'] = future_compact.get('unpriced_unknown')
                            row['future_low_overflow_unpriced'] = 0
                            row['future_high_overflow_unpriced'] = 0
                    writer.append(row)
                    if contact['status'] == 'observed':
                        completeness['joins_emitted'] += 1
                    else:
                        completeness['joins_censored'] += 1
    gid = geometry_row.get('geometry_id')
    for key in [item for item in future_cache if item[0] == gid and item[1] == cut_ns]:
        future_cache.pop(key, None)


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
        'link_rows': 0,
        'independent_events': 0,
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


def _ledger_row(atom):
    rows = atom.get('rows') or ()
    return {
        'source_path': atom.get('source_path'),
        'instrument_id': atom.get('instrument_id'),
        'contract_key': atom.get('contract_key'),
        'event_start_ns': atom['event_start_ns'],
        'event_end_ns': atom['event_end_ns'],
        'known_at_ns': atom.get('known_at_ns'),
        'priced_buy': atom.get('priced_buy'),
        'priced_sell': atom.get('priced_sell'),
        'priced_unknown': atom.get('priced_unknown'),
        'unpriced_buy': atom['unpriced'][0],
        'unpriced_sell': atom['unpriced'][1],
        'unpriced_unknown': atom['unpriced'][2],
        'cell_count': len(rows),
        'cells_sha256': cells_content_hash(atom),
        'unpriced_only': len(rows) == 0 and sum(atom.get('unpriced') or ()) > 0,
        'missing_cells': False,
        'measurement_sha256': atom.get('measurement_sha256'),
        'canonical_raw_values_sha256': atom.get('canonical_raw_values_sha256'),
        'receipt_sha256': atom.get('receipt_sha256'),
    }


def _write_tpo(*, writer, completeness, collection, root, year, stage, session,
               anchor, cut_ns, contract_key, instrument_id, path, economic,
               members, published, geometry_id):
    for minutes in BRACKET_MINUTES:
        for representation in ('whole_trade_visits', 'ohlc_range_proxy'):
            try:
                raw = tpo_from_atoms(
                    anchor, members, event_end_ns=min(cut_ns, anchor.end_ns),
                    decision_cut_ns=published, latency_ns=SOURCE_LATENCY_NS,
                    bracket_minutes=minutes, representation=representation,
                )
                compact = compact_tpo(raw)
                completeness['tpo_emitted'] += 1
            except (ContractError, IntegrityError) as exc:
                compact = compact_tpo({}, failed=True, reason=str(exc))
                completeness['tpo_failed'] += 1
                completeness['failed_reasons'].append({'kind': 'tpo', 'reason': str(exc)})
            tpo_row = _empty_tpo_row()
            tpo_row.update({
                'source_collection': collection, 'root': root, 'year': year,
                'stage': stage, 'session': session, 'anchor_id': anchor.id,
                'anchor_variant': anchor.variant, 'geometry_id': geometry_id,
                'cut_ns': cut_ns, 'contract_key': contract_key,
                'instrument_id': instrument_id, 'source_path': path,
                'economic_date': economic,
            })
            tpo_row.update(compact)
            if representation == 'whole_trade_visits':
                tpo_row['range_proxy_rows'] = None
                tpo_row['range_proxy_count'] = None
            else:
                tpo_row['range_proxy_rows'] = compact.get('visit_rows')
                tpo_row['range_proxy_count'] = compact.get('visit_count')
            writer.append(tpo_row)


def _unit_bounds(unit):
    start = unit.get('source_window_start_ns')
    end = unit.get('source_window_end_ns')
    if start is not None and end is not None:
        return int(start), int(end)
    ident = unit.get('source_identity') or {}
    if ident.get('acquired_event_start_ns') is not None:
        return int(ident['acquired_event_start_ns']), int(ident['acquired_event_end_ns'])
    return None, None


def _economic_session_bounds(day):
    start = local_timestamp(day - timedelta(days=1), time(18, 0), ZONE)
    end = local_timestamp(day, time(18, 0), ZONE)
    return start, end


def _atom_key(atom):
    return (atom.get('event_start_ns'), atom.get('event_end_ns'), atom.get('source_path'))


class IdentityEngine:
    """Bounded per-contract state: rolling window, civil masses, eight-day atoms."""

    def __init__(self, *, instrument_id, contract_key, collection, root, year,
                 calendar, policy, footprint_params, emit_geo, join_w, tpo_w,
                 completeness, windows, future_cache):
        self.instrument_id = instrument_id
        self.contract_key = contract_key
        self.collection = collection
        self.root = root
        self.year = year
        self.calendar = calendar
        self.policy = policy
        self.footprint_params = footprint_params
        self.emit_geo = emit_geo
        self.join_w = join_w
        self.tpo_w = tpo_w
        self.completeness = completeness
        self.windows = windows
        self.future_cache = future_cache
        self.lineage = source_lineage_id(collection, root, contract_key)
        self.pending = []
        self.flushed = set()
        self.civil_mass = {name: IntegerMass() for name in CIVIL_VARIANTS}
        self.civil_seen = {name: set() for name in CIVIL_VARIANTS}
        self.civil_present_ends = {name: set() for name in CIVIL_VARIANTS}
        self.civil_last_known = {name: None for name in CIVIL_VARIANTS}
        self.civil_emitted = set()
        self.civil_tpo = {}
        self.civil_anchor = {}
        self.civil_period = {name: None for name in CIVIL_VARIANTS}
        self.published_completed = []
        self.close_history = []
        self.pin069_history = []
        self.clock_cache = {}
        self.baseline = next(item for item in FROZEN_GEOMETRY_VARIANTS if item['id'] == BASELINE_VARIANT_ID)

    def add(self, atom):
        self.pending.append(atom)

    def reject(self, atom):
        key = _atom_key(atom)
        self.pending = [item for item in self.pending if _atom_key(item) != key]

    def _reset_civil(self, variant):
        self.civil_mass[variant] = IntegerMass()
        self.civil_seen[variant] = set()
        self.civil_present_ends[variant] = set()
        self.civil_last_known[variant] = None
        self.civil_anchor.pop(variant, None)
        for key in [item for item in self.civil_tpo if item[0] == variant]:
            self.civil_tpo.pop(key, None)

    def _latest_published(self, variant, cut_ns):
        best = None
        for item in self.published_completed:
            if item['variant'] != variant:
                continue
            if item['contract_key'] != self.contract_key:
                continue
            if item.get('instrument_id') != self.instrument_id:
                continue
            if item['published_ns'] > cut_ns:
                continue
            if best is None or item['published_ns'] > best['published_ns']:
                best = item
        return best

    def _close_at(self, deadline_ns):
        best = None
        if deadline_ns is None:
            return {'ticks': None, 'known': None}
        for item in self.close_history:
            known = item.get('known')
            if known is None or int(known) > int(deadline_ns):
                continue
            if best is None or int(known) > int(best['known']):
                best = item
        return best or {'ticks': None, 'known': None}

    def _pin_at(self, published_ns):
        best = None
        if published_ns is None:
            return None
        for item in self.pin069_history:
            known = item.get('pin069_published_ns')
            if known is None or int(known) > int(published_ns):
                continue
            if best is None or int(known) > int(best['pin069_published_ns']):
                best = item
        return best

    def _same(self):
        return [atom for atom in self.pending if atom.get('source_collection') == self.collection]

    def finish(self):
        self.flush_ready(None)
        same = self._same()
        if not same:
            return
        sample = same[-1]
        last = max(self.flushed) if self.flushed else date.fromisoformat(
            economic_date(int(same[-1]['event_end_ns'] - 1))
        )
        economic = last.isoformat()
        stage = stage_name(self.root, economic, self.policy)
        for variant in CIVIL_VARIANTS:
            key = self.civil_period.get(variant)
            if key is None or key in self.civil_emitted:
                continue
            if key[1].year != int(self.year) or variant not in self.civil_anchor:
                continue
            self._emit_completed(
                last, economic, stage, sample, self.civil_anchor[variant], same, None,
                last_year_day=last, force_civil=True,
            )

    def flush_ready(self, horizon_ns):
        if not self.pending:
            return
        days = sorted({
            date.fromisoformat(economic_date(int(atom['event_start_ns'])))
            for atom in self.pending
        } | {
            date.fromisoformat(economic_date(int(atom['event_end_ns'] - 1)))
            for atom in self.pending
        })
        for day in days:
            if day in self.flushed:
                continue
            need = _economic_session_bounds(day)[1] + 60 * MINUTE_NS
            if horizon_ns is not None and int(horizon_ns) < need:
                continue
            self.flush_day(day)
            self.flushed.add(day)
        if self.flushed:
            last = max(self.flushed)
            keep_after = _economic_session_bounds(last)[1] - ACTIVE_ATOM_DAYS * DAY_NS
            self.pending = [atom for atom in self.pending if atom['event_end_ns'] > keep_after]
            self.published_completed = [
                item for item in self.published_completed if item['published_ns'] > keep_after
            ]
            self.close_history = [
                item for item in self.close_history if (item.get('known') or 0) > keep_after
            ]
            self.pin069_history = [
                item for item in self.pin069_history
                if (item.get('pin069_published_ns') or 0) > keep_after
            ]

    def _named(self, day):
        cache_key = (day, self.instrument_id, self.contract_key)
        if cache_key not in self.clock_cache:
            cut_for_clocks = local_timestamp(day, time(17, 0), ZONE)
            self.clock_cache[cache_key] = _clock_anchors_for_day(
                day=day, cut_ns=cut_for_clocks, calendar=self.calendar, root=self.root,
                instrument_id=self.instrument_id, contract_key=self.contract_key,
                source_lineage=self.lineage,
            )
        return self.clock_cache[cache_key]

    def _day_atoms(self, day):
        return [
            atom for atom in self.pending
            if atom.get('source_collection') == self.collection
            and (
                date.fromisoformat(economic_date(int(atom['event_start_ns']))) == day
                or date.fromisoformat(economic_date(int(atom['event_end_ns'] - 1))) == day
            )
        ]

    def _cross_civil_periods(self, day, same, sample, stage, economic):
        for variant in CIVIL_VARIANTS:
            new_key = _civil_period_key(day, variant)
            old_key = self.civil_period.get(variant)
            if old_key is None:
                self.civil_period[variant] = new_key
                continue
            if old_key == new_key:
                continue
            if (
                old_key not in self.civil_emitted
                and old_key[1].year == int(self.year)
                and variant in self.civil_anchor
            ):
                self._emit_completed(
                    day, economic, stage, sample, self.civil_anchor[variant], same, None,
                    last_year_day=day, force_civil=True,
                )
            self._reset_civil(variant)
            self.civil_period[variant] = new_key

    def flush_day(self, day):
        collection, root, year = self.collection, self.root, self.year
        economic = day.isoformat()
        stage = stage_name(root, economic, self.policy)
        emit_selected = int(day.isoformat()[:4]) == int(year)
        named = self._named(day)
        same = self._same()
        day_atoms = self._day_atoms(day)
        sample = day_atoms[0] if day_atoms else (same[-1] if same else None)
        self._cross_civil_periods(day, same, sample, stage, economic)
        if emit_selected:
            for missing in named.get('unavailable') or ():
                self.completeness['unavailable_clocks'] += 1
                self.completeness['unavailable_clock_reasons'].append({
                    'economic_date': economic, 'variant': missing.get('variant'),
                    'reason': missing.get('reason'),
                })
        if not day_atoms:
            return
        cash_anchor = next((a for a in named.get('anchors') or () if a.variant == 'cash_rth'), None)
        futures_anchor = next(
            (a for a in named.get('anchors') or () if a.variant == 'observed_futures_18_17'), None)
        utc4 = next(
            (a for a in named.get('anchors') or () if a.variant == 'source_06_09_fixed_utc_minus4'), None)
        pin069_state = IncrementalPIN069(utc4) if utc4 is not None else None
        for atom in day_atoms:
            if pin069_state is not None and utc4 is not None and _wholly_inside(atom, utc4.spans):
                pin069_state.add(atom)
            for civ in named.get('anchors') or ():
                if civ.variant not in CIVIL_VARIANTS or not _wholly_inside(atom, civ.spans):
                    continue
                seen = (atom['event_start_ns'], atom['event_end_ns'])
                if seen in self.civil_seen[civ.variant]:
                    continue
                self.civil_seen[civ.variant].add(seen)
                self.civil_mass[civ.variant].add(atom)
                self.civil_present_ends[civ.variant].add(atom['event_end_ns'])
                known = atom.get('known_at_ns')
                if known is not None:
                    prior_known = self.civil_last_known[civ.variant]
                    self.civil_last_known[civ.variant] = int(known) if prior_known is None else max(prior_known, int(known))
                if civ.variant not in self.civil_anchor:
                    self.civil_anchor[civ.variant] = civ
                    for minutes in BRACKET_MINUTES:
                        for representation in ('whole_trade_visits', 'ohlc_range_proxy'):
                            try:
                                self.civil_tpo[(civ.variant, minutes, representation)] = AnchorTPO(
                                    civ, bracket_minutes=minutes, representation=representation,
                                )
                            except (ContractError, IntegrityError):
                                self.civil_tpo[(civ.variant, minutes, representation)] = None
                for minutes in BRACKET_MINUTES:
                    for representation in ('whole_trade_visits', 'ohlc_range_proxy'):
                        engine = self.civil_tpo.get((civ.variant, minutes, representation))
                        if engine is None:
                            continue
                        try:
                            engine.add(to_atomic_trades(atom, civ))
                        except (ContractError, IntegrityError) as exc:
                            self.completeness['failed_reasons'].append(
                                {'kind': 'tpo', 'reason': str(exc)})
                            self.civil_tpo[(civ.variant, minutes, representation)] = None

        pin_snap = pin069_state.snapshot() if pin069_state is not None else None
        if pin_snap is not None and pin_snap.get('pin069_published_ns') is not None:
            self.pin069_history.append(pin_snap)
        if not emit_selected:
            if cash_anchor is not None:
                members_cash = _atoms_in_spans(same, cash_anchor.spans)
                hist = IntegerMass()
                for atom in members_cash:
                    hist.add(atom)
                if hist.last_priced_ticks is not None:
                    self.close_history.append({
                        'ticks': hist.last_priced_ticks,
                        'known': hist.last_priced_known_at_ns,
                    })
            return
        self._emit_developing(
            day, economic, stage, sample, cash_anchor, futures_anchor, same,
            pin069_window=utc4,
        )
        self._emit_rolling(day, economic, stage, sample, same)
        last_year_day = date(int(year), 12, 31)
        anchors = list(named.get('anchors') or ())
        anchors.sort(key=lambda item: (item.end_ns, item.start_ns, item.variant))
        for anchor in anchors:
            self._emit_completed(
                day, economic, stage, sample, anchor, same, pin_snap,
                last_year_day=last_year_day,
            )

    def _emit_developing(self, day, economic, stage, sample, cash_anchor, futures_anchor, same,
                        pin069_window=None):
        collection, root, year = self.collection, self.root, self.year
        pin_atoms = []
        if pin069_window is not None:
            pin_atoms = [
                atom for atom in same if _wholly_inside(atom, pin069_window.spans)
            ]
            pin_atoms.sort(key=lambda item: (item['event_end_ns'], item['event_start_ns']))
        for kind, base in (
            ('developing_cash_rth', cash_anchor),
            ('developing_observed_futures_18_17', futures_anchor),
        ):
            if base is None:
                self.completeness['missing_developing_base'] += 1
                continue
            start, end = base.start_ns, min(base.end_ns, max(atom['event_end_ns'] for atom in same))
            cuts = aligned_cuts(start, end)
            hist = IntegerMass()
            members_dev = [atom for atom in same if _wholly_inside(atom, ((base.start_ns, base.end_ns),))]
            members_dev.sort(key=lambda item: item['event_end_ns'])
            cursor = 0
            pin_cursor = 0
            pin_engine = IncrementalPIN069(pin069_window) if pin069_window is not None else None
            prev_price = None
            for cut_ns in cuts:
                while cursor < len(members_dev) and members_dev[cursor]['event_end_ns'] <= cut_ns:
                    hist.add(members_dev[cursor])
                    cursor += 1
                while pin_engine is not None and pin_cursor < len(pin_atoms) and pin_atoms[pin_cursor]['event_end_ns'] <= cut_ns:
                    pin_engine.add(pin_atoms[pin_cursor])
                    pin_cursor += 1
                prefix_members = members_dev[:cursor]
                coverage = coverage_from_atoms(((start, cut_ns),), prefix_members)
                prefix_complete = coverage['coverage_complete']
                input_known = _input_known(prefix_members, cut_ns)
                published = publication_known(
                    input_known_ns=input_known, selection_known_ns=base.selection_known_at_ns,
                    cut_ns=cut_ns, latency_ns=SOURCE_LATENCY_NS,
                )
                pin_snap = pin_engine.snapshot() if pin_engine is not None else None
                if pin_snap is not None and (
                    pin_snap.get('pin069_published_ns') is None
                    or int(pin_snap['pin069_published_ns']) > int(published)
                ):
                    pin_snap = None
                compact, _view = emit_geometry_payload(
                    mass=hist, spec=self.baseline,
                    coordinate_identity=f'{root}:{self.contract_key}:{self.lineage}',
                    known_at_ns=published, coverage_complete=prefix_complete,
                    include_side=True, include_vwap=True, include_footprint=True,
                    footprint_params=self.footprint_params, verify_kernel=False,
                    anchor_kind=base.kind, pin069=pin_snap,
                )
                prior_close = self._close_at(cut_ns)
                compact['observed_prior_close_ticks'] = prior_close['ticks']
                compact['observed_prior_close_known_at_ns'] = prior_close['known']
                gid = geometry_id_for(
                    anchor=base, variant_id=BASELINE_VARIANT_ID, cut_ns=cut_ns,
                    cells_hash=digest(sorted(hist.source_hashes)),
                )
                row = _empty_geometry_row()
                _fill_geometry_identity(
                    row, collection=collection, root=root, year=year, stage=stage,
                    session=session_of(cut_ns, calendar=self.calendar, known_at_ns=published)['session'],
                    atom=_owning_atom(prefix_members or same, cut_ns, sample),
                    anchor=base, variant_id=BASELINE_VARIANT_ID, proxy=None,
                    cut_ns=cut_ns, published=published, economic=economic,
                    selected=True, input_known=input_known,
                    scenario_known=cut_ns + SOURCE_LATENCY_NS, geometry_id=gid,
                    formation_minutes=max(1, (cut_ns - start) // MINUTE_NS),
                )
                row['anchor_variant'] = kind
                row['anchor_kind'] = 'developing'
                row['coverage_complete'] = prefix_complete
                row['prefix_complete'] = prefix_complete
                row['formation_complete'] = prefix_complete
                prior = self._latest_published(base.variant, cut_ns)
                last_price = prefix_members[-1].get('last_priced_ticks') if prefix_members else None
                if prior is not None:
                    motion = compare_frozen_developing_va(
                        prior_val=prior['val'], prior_vah=prior['vah'],
                        current_val=compact.get('physical_val_ticks', compact.get('val_row')),
                        current_vah=compact.get('physical_vah_ticks', compact.get('vah_row')),
                        previous_price=prev_price, current_price=last_price,
                    )
                    row['completed_geometry_id'] = prior['geometry_id']
                else:
                    motion = {
                        'boundary_moving': False, 'price_crossing_frozen_va': False,
                        'prior_val_row': None, 'prior_vah_row': None,
                        'current_val_row': compact.get('val_row'),
                        'current_vah_row': compact.get('vah_row'),
                    }
                prev_price = last_price
                self.emit_geo(row, compact, complete=prefix_complete and hist.priced_volume > 0)
                self.completeness['baseline_emitted'] += 1
                emit_join_rows(
                    writer=self.join_w, completeness=self.completeness, windows=self.windows,
                    geometry_row=row, feature_lookup=None, cut_ns=cut_ns,
                    collection=collection, root=root, year=year, stage=stage,
                    session=row['session'], economic=economic,
                    identity_atoms=same, mass=hist, motion=motion,
                    later_link=False, future_cache=self.future_cache,
                )

    def _emit_rolling(self, day, economic, stage, sample, same):
        collection, root, year = self.collection, self.root, self.year
        session_start, session_end = _economic_session_bounds(day)
        cuts = aligned_cuts(session_start, session_end)
        for minutes in ROLLING_MINUTES:
            width = minutes * MINUTE_NS
            hist = IntegerMass()
            window = deque()
            cursor_atoms = [
                atom for atom in same
                if atom['event_end_ns'] <= session_end + 60 * MINUTE_NS
            ]
            cursor_atoms.sort(key=lambda item: (item['event_end_ns'], item['event_start_ns']))
            cursor = 0
            for cut_ns in cuts:
                eco = economic_date(int(cut_ns - 1))
                if int(eco[:4]) != int(year) or date.fromisoformat(eco) != day:
                    continue
                while cursor < len(cursor_atoms) and cursor_atoms[cursor]['event_end_ns'] <= cut_ns:
                    atom = cursor_atoms[cursor]
                    cursor += 1
                    if atom.get('source_collection') != collection:
                        continue
                    if atom['event_start_ns'] >= cut_ns - width:
                        hist.add(atom)
                        window.append(atom)
                while window and window[0]['event_start_ns'] < cut_ns - width:
                    hist.remove(window.popleft())
                members_roll = list(window)
                rolling = rolling_anchor(
                    minutes=minutes, event_end_ns=cut_ns,
                    selection_known_at_ns=cut_ns, source_versions=(self.lineage,),
                    root=root, instrument_id=self.instrument_id, contract_key=self.contract_key,
                    source_lineage=self.lineage,
                )
                coverage = coverage_from_atoms(((cut_ns - width, cut_ns),), members_roll)
                input_known = _input_known(members_roll, cut_ns)
                published = publication_known(
                    input_known_ns=input_known, selection_known_ns=cut_ns,
                    cut_ns=cut_ns, latency_ns=SOURCE_LATENCY_NS,
                )
                compact, _view = emit_geometry_payload(
                    mass=hist, spec=self.baseline,
                    coordinate_identity=f'{root}:{self.contract_key}:{self.lineage}',
                    known_at_ns=published, coverage_complete=coverage['coverage_complete'],
                    include_side=True, include_vwap=True, include_footprint=True,
                    footprint_params=self.footprint_params, verify_kernel=False,
                    anchor_kind='rolling',
                )
                gid = geometry_id_for(
                    anchor=rolling, variant_id=BASELINE_VARIANT_ID, cut_ns=cut_ns,
                    cells_hash=digest(sorted(hist.source_hashes)),
                )
                row = _empty_geometry_row()
                _fill_geometry_identity(
                    row, collection=collection, root=root, year=year,
                    stage=stage_name(root, eco, self.policy),
                    session=session_of(cut_ns, calendar=self.calendar, known_at_ns=published)['session'],
                    atom=_owning_atom(members_roll or same, cut_ns, sample),
                    anchor=rolling, variant_id=BASELINE_VARIANT_ID, proxy=None,
                    cut_ns=cut_ns, published=published, economic=eco, selected=True,
                    input_known=input_known, scenario_known=cut_ns + SOURCE_LATENCY_NS,
                    geometry_id=gid, formation_minutes=minutes,
                )
                row['coverage_complete'] = coverage['coverage_complete']
                row['prefix_complete'] = coverage['coverage_complete']
                row['formation_complete'] = coverage['coverage_complete']
                self.emit_geo(row, compact, complete=coverage['coverage_complete'] and hist.priced_volume > 0)
                self.completeness['baseline_emitted'] += 1
                emit_join_rows(
                    writer=self.join_w, completeness=self.completeness, windows=self.windows,
                    geometry_row=row, feature_lookup=None, cut_ns=cut_ns,
                    collection=collection, root=root, year=year, stage=row['stage'],
                    session=row['session'], economic=eco, identity_atoms=same,
                    mass=hist, motion={
                        'boundary_moving': False, 'price_crossing_frozen_va': False,
                        'prior_val_row': None, 'prior_vah_row': None,
                        'current_val_row': compact.get('val_row'),
                        'current_vah_row': compact.get('vah_row'),
                    }, later_link=False, future_cache=self.future_cache,
                )

    def _emit_completed(self, day, economic, stage, sample, anchor, same, pin_snap, *, last_year_day,
                        force_civil=False):
        collection, root, year = self.collection, self.root, self.year
        session = session_of(anchor.end_ns, calendar=self.calendar, known_at_ns=anchor.end_ns)['session']
        if anchor.variant in CIVIL_VARIANTS:
            civ_key = self.civil_period.get(anchor.variant) or _civil_period_key(day, anchor.variant)
            ends = _civil_period_end(day, anchor.variant)
            if civ_key in self.civil_emitted:
                return
            owned = civ_key[1].year == int(year)
            if not owned:
                return
            if not ends and day != last_year_day and not force_civil:
                return
            self.civil_emitted.add(civ_key)
            hist = self.civil_mass[anchor.variant]
            present = self.civil_present_ends[anchor.variant]
            intended_count = 0
            missing_count = 0
            for span_start, span_end in anchor.spans:
                if span_end <= span_start:
                    continue
                for end in range(span_start + MINUTE_NS, span_end + 1, MINUTE_NS):
                    intended_count += 1
                    if end not in present:
                        missing_count += 1
            civil_complete = intended_count > 0 and missing_count == 0 and hist.coverage_complete
            members_fixed = ()
            coverage = {
                'intended_spans': tuple(anchor.spans),
                'missing_spans': (),
                'missing_count': missing_count,
                'intended_count': intended_count,
                'coverage_complete': civil_complete,
                'observed_partial': bool(present) and not civil_complete,
            }
        else:
            members_fixed = _atoms_in_spans(same, anchor.spans)
            coverage = coverage_from_atoms(anchor.spans, members_fixed)
            hist = IntegerMass()
            for atom in members_fixed:
                hist.add(atom)
            hist.copy_flags_from(members_fixed)
        cut_ns = anchor.end_ns
        if anchor.variant in CIVIL_VARIANTS:
            input_known = self.civil_last_known[anchor.variant] or cut_ns
        else:
            input_known = _input_known(members_fixed, cut_ns)
        published = publication_known(
            input_known_ns=input_known, selection_known_ns=anchor.selection_known_at_ns,
            cut_ns=cut_ns, latency_ns=SOURCE_LATENCY_NS,
        )
        if delayed_selection_blocks_origin(anchor.selection_known_at_ns, anchor.start_ns):
            if published < cut_ns:
                raise IntegrityError('delayed selection cannot publish at a retrospective origin')
        complete = coverage['coverage_complete'] and hist.priced_volume > 0
        completed_id = None
        baseline_row = None
        cells_hash = digest(sorted(hist.source_hashes) + [anchor.variant, cut_ns])
        owner = _owning_atom(members_fixed or same, cut_ns, sample)
        attached_pin = pin_snap
        if attached_pin is None:
            attached_pin = self._pin_at(published)
        elif (
            attached_pin.get('pin069_published_ns') is None
            or int(attached_pin['pin069_published_ns']) > int(published)
        ):
            attached_pin = None
        prior_close = self._close_at(anchor.start_ns if anchor.selection_known_at_ns is None else min(
            int(anchor.start_ns), int(anchor.selection_known_at_ns),
        ))
        for spec in FROZEN_GEOMETRY_VARIANTS:
            include_aux = spec['id'] == BASELINE_VARIANT_ID
            compact, _view = emit_geometry_payload(
                mass=hist, spec=spec,
                coordinate_identity=f'{root}:{self.contract_key}:{self.lineage}',
                known_at_ns=published, coverage_complete=coverage['coverage_complete'],
                include_side=include_aux, include_vwap=include_aux,
                include_footprint=include_aux, footprint_params=self.footprint_params,
                verify_kernel=False, anchor_kind=anchor.kind,
                pin069=attached_pin if include_aux else None,
            )
            compact['observed_prior_close_ticks'] = prior_close['ticks']
            compact['observed_prior_close_known_at_ns'] = prior_close['known']
            gid = geometry_id_for(
                anchor=anchor, variant_id=spec['id'], cut_ns=cut_ns, cells_hash=cells_hash,
            )
            if spec['id'] == BASELINE_VARIANT_ID:
                completed_id = gid
            row = _empty_geometry_row()
            _fill_geometry_identity(
                row, collection=collection, root=root, year=year, stage=stage,
                session=session, atom=owner, anchor=anchor, variant_id=spec['id'],
                proxy=None, cut_ns=cut_ns, published=published, economic=economic,
                selected=True, input_known=input_known,
                scenario_known=cut_ns + SOURCE_LATENCY_NS, geometry_id=gid,
            )
            row['coverage_complete'] = coverage['coverage_complete']
            row['prefix_complete'] = coverage['coverage_complete']
            row['formation_complete'] = complete
            row['completed_geometry_id'] = completed_id
            row['provenance_paths'] = ','.join(sorted(hist.source_paths))
            self.emit_geo(row, compact, complete=complete)
            if spec['id'] == BASELINE_VARIANT_ID:
                baseline_row = row
        if complete:
            self.published_completed.append({
                'variant': anchor.variant,
                'contract_key': self.contract_key,
                'instrument_id': self.instrument_id,
                'published_ns': published,
                'val': baseline_row.get('physical_val_ticks', baseline_row.get('val_row')),
                'vah': baseline_row.get('physical_vah_ticks', baseline_row.get('vah_row')),
                'poc': baseline_row.get('physical_poc_ticks', baseline_row.get('scalar_poc')),
                'geometry_id': completed_id,
            })
            if anchor.variant == 'cash_rth' and hist.last_priced_ticks is not None:
                self.close_history.append({
                    'ticks': hist.last_priced_ticks,
                    'known': hist.last_priced_known_at_ns,
                })
        for proxy in BAR_PROXY_VARIANTS:
            proxy_row, _ = bar_proxy_from_mass(
                hist, proxy,
                coordinate_identity=f'{root}:{self.contract_key}:{self.lineage}',
                known_at_ns=published, coverage_complete=coverage['coverage_complete'],
                anchor_kind=anchor.kind,
            )
            row = _empty_geometry_row()
            _fill_geometry_identity(
                row, collection=collection, root=root, year=year, stage=stage,
                session=session, atom=owner, anchor=anchor,
                variant_id=BASELINE_VARIANT_ID, proxy=proxy, cut_ns=cut_ns,
                published=published, economic=economic, selected=True,
                input_known=input_known, scenario_known=cut_ns + SOURCE_LATENCY_NS,
                geometry_id=geometry_id_for(
                    anchor=anchor, variant_id=BASELINE_VARIANT_ID,
                    cut_ns=cut_ns, cells_hash=cells_hash, proxy=proxy,
                ),
            )
            row['coverage_complete'] = coverage['coverage_complete']
            row['prefix_complete'] = coverage['coverage_complete']
            row['formation_complete'] = complete
            row['completed_geometry_id'] = completed_id
            self.emit_geo(row, proxy_row, complete=complete)
            self.completeness['proxy_emitted'] += 1
        if anchor.variant in CIVIL_VARIANTS:
            for minutes in BRACKET_MINUTES:
                for representation in ('whole_trade_visits', 'ohlc_range_proxy'):
                    engine = self.civil_tpo.get((anchor.variant, minutes, representation))
                    tpo_row = _empty_tpo_row()
                    tpo_row.update({
                        'source_collection': collection, 'root': root, 'year': year,
                        'stage': stage, 'session': session, 'anchor_id': anchor.id,
                        'anchor_variant': anchor.variant, 'geometry_id': completed_id,
                        'cut_ns': cut_ns, 'contract_key': self.contract_key,
                        'instrument_id': self.instrument_id,
                        'source_path': None if owner is None else owner.get('source_path'),
                        'economic_date': economic,
                    })
                    if engine is None:
                        tpo_row.update(compact_tpo({}, failed=True, reason='tpo_engine_unavailable'))
                        self.completeness['tpo_failed'] += 1
                    else:
                        try:
                            raw = engine.record(
                                event_end_ns=min(cut_ns, anchor.end_ns),
                                decision_cut_ns=max(published, engine.known_at),
                                latency_ns=SOURCE_LATENCY_NS if engine.delay is None else engine.delay,
                            )
                            compact = compact_tpo(raw)
                            self.completeness['tpo_emitted'] += 1
                        except (ContractError, IntegrityError) as exc:
                            compact = compact_tpo({}, failed=True, reason=str(exc))
                            self.completeness['tpo_failed'] += 1
                        tpo_row.update(compact)
                    if representation == 'ohlc_range_proxy':
                        tpo_row['range_proxy_rows'] = tpo_row.get('visit_rows')
                        tpo_row['range_proxy_count'] = tpo_row.get('visit_count')
                    self.tpo_w.append(tpo_row)
        else:
            _write_tpo(
                writer=self.tpo_w, completeness=self.completeness, collection=collection,
                root=root, year=year, stage=stage, session=session, anchor=anchor,
                cut_ns=cut_ns, contract_key=self.contract_key, instrument_id=self.instrument_id,
                path=None if owner is None else owner.get('source_path'), economic=economic,
                members=members_fixed, published=published, geometry_id=completed_id,
            )
        if baseline_row is not None:
            emit_join_rows(
                writer=self.join_w, completeness=self.completeness, windows=self.windows,
                geometry_row=baseline_row, feature_lookup=None, cut_ns=cut_ns,
                collection=collection, root=root, year=year, stage=stage,
                session=session, economic=economic, identity_atoms=same,
                mass=hist, motion={
                    'boundary_moving': False, 'price_crossing_frozen_va': False,
                    'prior_val_row': None, 'prior_vah_row': None,
                    'current_val_row': baseline_row.get('val_row'),
                    'current_vah_row': baseline_row.get('vah_row'),
                }, later_link=False, future_cache=self.future_cache,
            )
            later_end = min(cut_ns + 60 * MINUTE_NS, max(atom['event_end_ns'] for atom in same))
            for later in aligned_cuts(cut_ns, later_end):
                if later <= cut_ns or published > later:
                    continue
                emit_join_rows(
                    writer=self.join_w, completeness=self.completeness, windows=self.windows,
                    geometry_row=baseline_row, feature_lookup=None, cut_ns=later,
                    collection=collection, root=root, year=year, stage=stage,
                    session=session_of(later, calendar=self.calendar, known_at_ns=published)['session'],
                    economic=economic, identity_atoms=same, mass=hist, motion={
                        'boundary_moving': False, 'price_crossing_frozen_va': False,
                        'prior_val_row': None, 'prior_vah_row': None,
                        'current_val_row': baseline_row.get('val_row'),
                        'current_vah_row': baseline_row.get('vah_row'),
                    }, later_link=True, future_cache=self.future_cache,
                )
        if anchor.variant in CIVIL_VARIANTS:
            self._reset_civil(anchor.variant)


def compute_profile_partition(*, key, members, neighbors, identity, source_refs, contract,
                              calendar, policy, window_units, outputs, ordinal, pa,
                              stats=None, load_reference=None, window_refs=None,
                              on_geometry=None, on_tpo=None, on_join=None):
    """Stream one collection/root/year. Does not retain annual rows or JSON."""
    collection, root, year = key
    began, wall_began, before = time_mod.process_time(), time_mod.monotonic(), outputs.written
    completeness = empty_completeness()
    bound = authenticate_bound_contracts(contract, load_reference)
    footprint_params = bound['footprint']
    windows = WindowUnitCache(window_units)
    prefix = f'profile-{ordinal:03d}-{collection}-{root}-{year}'
    from trading_research.research.auction_flow_profile_statistics import (
        accumulate_geometry_row, accumulate_join_row, accumulate_tpo_row,
        new_partition_accumulators, write_partition_groups,
    )
    accumulators = new_partition_accumulators()

    def _on_geo(row):
        accumulate_geometry_row(accumulators, row, collection=collection, year=year)
        if on_geometry is not None:
            on_geometry(row)

    def _on_tpo(row):
        accumulate_tpo_row(accumulators, row, collection=collection, year=year)
        if on_tpo is not None:
            on_tpo(row)

    def _on_join(row):
        accumulate_join_row(accumulators, row, collection=collection, year=year)
        if on_join is not None:
            on_join(row)

    geo_w = ChunkWriter(outputs, prefix + '-geometry', geometry_schema(pa), pa, on_row=_on_geo)
    tpo_w = ChunkWriter(outputs, prefix + '-tpo', tpo_schema(pa), pa, on_row=_on_tpo)
    join_w = ChunkWriter(outputs, prefix + '-joins', join_schema(pa), pa, on_row=_on_join)
    cell_w = ChunkWriter(outputs, prefix + '-cells', cell_schema(pa), pa)

    def emit_geo(row, compact, *, complete, partial_status=None):
        _merge_compact(row, compact)
        if complete and compact.get('geometry_status') == 'complete':
            row['eligible_complete'] = True
            completeness['geometry_complete'] += 1
        elif compact.get('geometry_status') in ('no_priced_volume', 'unknown_priced_population'):
            row['eligible_complete'] = False
            completeness['geometry_null'] += 1
        else:
            row['eligible_complete'] = False
            if partial_status:
                row['geometry_status'] = partial_status
            completeness['geometry_partial'] += 1
        geo_w.append(row)
        completeness['geometry_emitted'] += 1

    alias = AliasIndex()
    engines = {}
    future_cache = {}
    seen_units = set()
    queued = []
    for selected, group in ((True, members), (False, neighbors)):
        for unit in group:
            queued.append((selected, unit))
    queued.sort(key=lambda item: (
        _unit_bounds(item[1])[0] or 0,
        item[1].get('source_path') or '',
        item[1].get('root') or '',
    ))

    def _engine(ident):
        instrument_id, contract_key = ident
        if ident not in engines:
            engines[ident] = IdentityEngine(
                instrument_id=instrument_id, contract_key=contract_key,
                collection=collection, root=root, year=year, calendar=calendar,
                policy=policy, footprint_params=footprint_params, emit_geo=emit_geo,
                join_w=join_w, tpo_w=tpo_w, completeness=completeness,
                windows=windows, future_cache=future_cache,
            )
        return engines[ident]

    def _horizon(index):
        starts = []
        for _, unit in queued[index + 1:]:
            start, _end = _unit_bounds(unit)
            if start is not None:
                starts.append(int(start))
        return min(starts) if starts else None

    for index, (selected, unit) in enumerate(queued):
        ukey = (
            unit.get('source_path'), unit.get('source_window_start_ns'),
            unit.get('source_window_end_ns'), unit.get('root'),
        )
        if ukey in seen_units:
            continue
        seen_units.add(ukey)
        completeness['units_scanned'] += 1
        completeness['units_selected' if selected else 'units_neighbor'] += 1
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
        extracted = load_measurement_cells(unit)
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
        measured_keys = {
            (atom['instrument_id'], atom['event_start_ns'], atom['event_end_ns'])
            for atom in extracted['atoms']
        }
        for row in observations:
            key = (row.get('instrument_id'), row.get('event_start_ns'), row.get('event_end_ns'))
            if key not in measured_keys:
                completeness['atoms_missing'] += 1
                cell_w.append({
                    'source_path': row.get('source_path') or unit.get('source_path'),
                    'instrument_id': row.get('instrument_id'),
                    'contract_key': row.get('contract_key'),
                    'event_start_ns': row.get('event_start_ns'),
                    'event_end_ns': row.get('event_end_ns'),
                    'known_at_ns': row.get('known_at_ns'),
                    'priced_buy': row.get('priced_buy'),
                    'priced_sell': row.get('priced_sell'),
                    'priced_unknown': row.get('priced_unknown'),
                    'unpriced_buy': row.get('unpriced_buy'),
                    'unpriced_sell': row.get('unpriced_sell'),
                    'unpriced_unknown': row.get('unpriced_unknown'),
                    'cell_count': 0,
                    'cells_sha256': None,
                    'unpriced_only': False,
                    'missing_cells': True,
                    'measurement_sha256': row.get('measurement_sha256'),
                    'canonical_raw_values_sha256': row.get('canonical_raw_values_sha256'),
                    'receipt_sha256': row.get('receipt_sha256'),
                })
        merged = attach_observation_identity(extracted['atoms'], observations, unit=unit)
        del extracted, observations
        completeness['atoms_scanned'] += len(merged)
        unit_collection = classify_source_collection(
            unit.get('source_path'), unit=unit,
            injected=contract.get('source_collections') if isinstance(contract, dict) else None,
        )
        if unit_collection != collection and selected:
            raise IntegrityError('selected unit collection does not match the partition')
        for atom in merged:
            atom['source_collection'] = unit_collection
            atom['selected_partition_member'] = selected
            atom['source_lineage'] = source_lineage_id(
                unit_collection, root, atom.get('contract_key') or '',
            )
            accepted = alias.add(atom)
            if accepted is None:
                continue
            completeness['atoms_matched'] += 1
            cell_w.append(_ledger_row(accepted))
            contract_key = accepted.get('contract_key')
            if contract_key is None or not str(contract_key).startswith(str(root) + ':'):
                completeness['missing_contract_identity'] += 1
                continue
            _engine((accepted.get('instrument_id'), contract_key)).add(accepted)
        for prior in alias.retracted:
            ident = (prior.get('instrument_id'), prior.get('contract_key'))
            if ident in engines:
                engines[ident].reject(prior)
        del merged
        horizon = _horizon(index)
        alias.prune(horizon)
        alias.retracted.clear()
        for engine in engines.values():
            engine.flush_ready(horizon)
    for engine in engines.values():
        engine.finish()
    completeness['atoms_conflict'] += len(alias.conflicts)
    completeness['cell_rows'] = cell_w.rows + len(cell_w.buf)
    completeness.update(windows.stats)
    completeness['link_rows'] = join_w.rows + len(join_w.buf)
    geometry_ref = geo_w.finish()
    tpo_ref = tpo_w.finish()
    join_ref = join_w.finish()
    cells_ref = cell_w.finish()
    groups_ref = paired_ref = None
    if stats is not None:
        groups_ref, paired_ref = write_partition_groups(
            outputs, prefix, accumulators, stats=stats, policy=policy,
            collection=collection, root=root, year=year, contract=contract,
        )
    completeness_out = {**completeness, 'conflicts': list(alias.conflicts), 'family_complete': False}
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
        'geometry_rows': geometry_ref.get('rows', 0),
        'tpo_rows': tpo_ref.get('rows', 0),
        'join_rows': join_ref.get('rows', 0),
        'cell_rows': cells_ref.get('rows', 0),
    }
    part = {
        'kind': KIND, 'passed': True, 'identity': identity,
        'source_collection': collection, 'root': root, 'economic_year': year,
        'source_refs': source_refs, 'window_refs': window_refs,
        'geometry': geometry_ref, 'tpo': tpo_ref, 'joins': join_ref, 'cells': cells_ref,
        'completeness': completeness_ref,
        'groups': groups_ref, 'paired': paired_ref,
        'support_refs': source_refs,
        'group_count': geometry_ref.get('rows', 0),
        'measurement': measurement,
        'completeness_counts': {k: v for k, v in completeness_out.items() if k != 'conflicts'},
        'family_complete': False,
        'implementation': {
            'module': VERSION,
            'consumer_hash_fields': ('geometry', 'tpo', 'joins', 'cells'),
            'consumer_files': __import__(
                'trading_research.research.auction_flow_profile_statistics',
                fromlist=['consumer_implementation_identity'],
            ).consumer_implementation_identity(),
        },
    }
    ref = outputs.json(prefix + '-partition.json', part, kind=KIND)
    _ = ANCHOR_MINUTE_NS
    return ref, part, measurement


__all__ = [
    'BAR_PROXY_VARIANTS', 'BASELINE_VARIANT_ID', 'FROZEN_CONTRACT_KIND',
    'FROZEN_GEOMETRY_VARIANTS', 'IntegerMass', 'KIND', 'POPULATION_KIND',
    'ProfileCashAdapter', 'VERSION', 'WINDOW_POPULATION_KIND',
    'aligned_cuts', 'apply_variant_view', 'atom_bar', 'authenticate_bound_contracts',
    'bar_proxy_from_mass', 'cell_schema', 'classify_future_contact',
    'classify_source_collection', 'compact_footprint', 'compact_geometry',
    'compact_side_geometry', 'compact_tpo', 'compare_frozen_developing_va',
    'decode_exact_int', 'encode_exact_int', 'FORMATION_MINUTES', 'LATENCY_NS',
    'compute_profile_partition', 'coverage_from_atoms', 'dedup_atoms',
    'delayed_selection_blocks_origin', 'empty_completeness', 'extract_sparse_profile',
    'extract_unit_cells', 'footprint_parameters', 'frozen_variant_ids',
    'future_mass_on_frozen_grid', 'geometry_from_mass', 'geometry_schema',
    'integer_profile_geometry', 'join_schema', 'labelled_sd',
    'load_measurement_cells', 'match_atom_identity', 'mass_view_from_histogram',
    'null_geometry', 'pin069_reanchor', 'publication_known',
    'require_frozen_variants', 'source_lineage_id', 'tpo_from_atoms', 'tpo_schema',
    'to_atomic_trades', 'variant_definition', 'vwap_bands',
    'weighted_quantiles', 'write_series_table',
]
