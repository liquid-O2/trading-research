"""Causal rolling formation features and matured forward labels.

This helper emits the shared cut/instrument tables used by Deliverable 1
timing and distribution comparisons. It does not fit Context, score
Locations, certify family completion, join acquisitions, or invent a
winning clock. Root owns definitions, review, integration and registered
execution.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.foundations.time import MINUTE, NS, timestamp
from trading_research.research.auction_flow_measurements import SOURCE_FILTERS
from trading_research.research.auction_flow_windows import TRADE_FIELDS


VERSION = 'auction-flow-causal-window-links-v1'
CONTRACT_KIND = 'auction_flow_causal_window_links_contract_v1'
CONTRACT_VERSION = 1
SOURCE_LATENCY_NS = 250_000_000
CUT_CADENCE_NS = 5 * MINUTE
FORMATION_MINUTES = (5, 15, 60, 240)
LATENCY_NS = (250_000_000, 0, 1_000_000_000)
FORWARD_HORIZONS_MINUTES = (5, 15, 60)
HORIZON_KINDS = ('fixed_minutes', 'remaining_session')
MAX_INSTRUMENTS = 8
MAX_CUT_SPAN_NS = 24 * 60 * MINUTE
MAX_SOURCE_BUFFER_NS = 3 * 24 * 60 * MINUTE
_SHA_LEN = 64
_INT64_MIN = -(2 ** 63)
_INT64_MAX = 2 ** 63 - 1
_TRADE_REQUIRED = (
    't', 'source_order', 'instrument_id', 'price', 'size', 'side', 'price_valid',
    'source_row', 'known_at_ns',
)
_COHORT_BOUNDS = {
    'all': (1, None),
    'ny_ge100': (100, None),
    'london_ge75': (75, None),
    'inclusive30_through60': (30, 61),
}
_STAGE_NAMES = ('training', 'development', 'calibration', 'confirmation')
_FROZEN_STAGE_DATES = {
    'ES': {
        'calibration': ('2024-01-01', '2024-04-01'),
        'confirmation': ('2024-04-01', '2024-09-01'),
        'development': ('2023-07-01', '2024-01-01'),
        'training': ('2020-01-01', '2021-01-01'),
    },
    'NQ': {
        'calibration': ('2024-01-01', '2025-01-01'),
        'confirmation': ('2025-01-01', '2026-09-04'),
        'development': ('2023-01-01', '2024-01-01'),
        'training': ('2020-01-01', '2023-01-01'),
    },
}
_FEATURE_NULL_INTS = (
    'first_priced_ticks', 'first_priced_event_ns', 'first_priced_known_at_ns',
    'first_priced_source_order', 'first_priced_source_row',
    'last_priced_ticks', 'last_priced_event_ns', 'last_priced_known_at_ns',
    'last_priced_source_order', 'last_priced_source_row',
    'reference_price_ticks', 'reference_event_ns', 'reference_known_at_ns',
    'reference_source_order', 'reference_source_row',
    'observed_high_ticks', 'observed_low_ticks', 'observed_high_at_ns',
    'observed_low_at_ns', 'observed_high_source_order', 'observed_low_source_order',
    'ofi_open', 'ofi_high', 'ofi_low', 'ofi_close', 'ofi_high_at_ns', 'ofi_low_at_ns',
    'ofi_high_source_order', 'ofi_low_source_order',
    'ofi_contracts', 'price_change_ofi', 'same_price_size_ofi',
)
_LABEL_NULL_INTS = (
    'event_start_ns', 'event_end_ns', 'known_at_ns', 'horizon_minutes',
    'first_priced_ticks', 'first_priced_event_ns', 'first_priced_known_at_ns',
    'first_priced_source_order', 'first_priced_source_row',
    'last_priced_ticks', 'last_priced_event_ns', 'last_priced_known_at_ns',
    'last_priced_source_order', 'last_priced_source_row',
    'observed_high_ticks', 'observed_low_ticks', 'observed_high_at_ns',
    'observed_low_at_ns', 'observed_high_source_order', 'observed_low_source_order',
    'signed_open', 'signed_high', 'signed_low', 'signed_close',
    'signed_high_at_ns', 'signed_low_at_ns',
    'signed_high_source_order', 'signed_low_source_order',
)
_IDENTITY_KEYS = (
    'root', 'source_path', 'source_metadata_sha256', 'source_variant',
    'acquired_event_start_ns', 'acquired_event_end_ns',
)


def _sha256_text(value, *, what):
    if type(value) is not str or len(value) != _SHA_LEN or any(c not in '0123456789abcdef' for c in value):
        raise IntegrityError(f'{what} must be a lowercase 64-character hex digest')
    return value


def _bool(value, *, what):
    if type(value) is not bool:
        raise IntegrityError(f'{what} must be an explicit boolean')
    return value


def _int(value, *, what, minimum=_INT64_MIN, maximum=_INT64_MAX):
    if type(value) is bool or type(value) is not int:
        raise IntegrityError(f'{what} must be an exact integer')
    if not minimum <= value <= maximum:
        raise IntegrityError(f'{what} exceeds the exact int64 domain')
    return value


def _text(value, *, what, allow_empty=False):
    if type(value) is not str or (not value and not allow_empty):
        raise IntegrityError(f'{what} must be a concrete string')
    return value


def _mapping(value, *, what):
    if not isinstance(value, dict):
        raise IntegrityError(f'{what} must be an object')
    return value


def _py_int(value, *, what):
    if value is None:
        return None
    if type(value) is bool:
        raise IntegrityError(f'{what} must be an exact integer')
    result = int(value)
    if not _INT64_MIN <= result <= _INT64_MAX:
        raise IntegrityError(f'{what} exceeds the exact int64 domain')
    return result


def _add_checked(*values, what):
    total = 0
    for value in values:
        total += int(value)
        if not _INT64_MIN <= total <= _INT64_MAX:
            raise IntegrityError(f'{what} exceeds the exact int64 domain')
    return total


def _sub_checked(left, right, *, what):
    return _add_checked(int(left), -int(right), what=what)


def _utc_from_ns(value):
    seconds, nanos = divmod(timestamp(value), NS)
    return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)


def _civil_date_ns(iso):
    parts = iso.split('-')
    if len(parts) != 3:
        raise IntegrityError('stage date must be YYYY-MM-DD')
    year, month, day = (int(part) for part in parts)
    delta = datetime(year, month, day, tzinfo=timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return _int(delta.days * 86400 * NS, what='stage_date_ns', minimum=0)


def _minute_floor(value):
    value = int(value)
    return value - (value % MINUTE)


def _minute_ceil(value):
    value = int(value)
    remainder = value % MINUTE
    if remainder == 0:
        return value
    return _add_checked(value, MINUTE - remainder, what='minute_ceil')


def _ny_date(cut_ns, zone):
    return _utc_from_ns(cut_ns).astimezone(ZoneInfo(zone)).date()


def _frozen_stage_intervals():
    parsed = {}
    for root, spec in _FROZEN_STAGE_DATES.items():
        parsed[root] = {
            name: (_civil_date_ns(begin), _civil_date_ns(finish))
            for name, (begin, finish) in spec.items()
        }
    return parsed


def contract_definitions(contract=None):
    """Static scientific definitions copied from the frozen contract."""
    payload = {} if contract is None else _mapping(contract, what='contract')
    return {
        'version': VERSION,
        'kind': CONTRACT_KIND,
        'contract_version': CONTRACT_VERSION,
        'family_complete': False,
        'cut_clock': 'UTC five-minute boundaries; same cuts for every formation comparison',
        'cut_cadence_ns': CUT_CADENCE_NS,
        'source_latency_ns': SOURCE_LATENCY_NS,
        'formation_minutes': list(FORMATION_MINUTES),
        'formation_interval': '[end-formation_minutes, end); feature known_at = end + source 250ms',
        'latency_ns': list(LATENCY_NS),
        'forward_horizons_minutes': list(FORWARD_HORIZONS_MINUTES),
        'forward_interval': '[cut+latency, cut+latency+horizon) or [cut+latency, actual_cash_close)',
        'label_known_at': 'target_end + latency; must mature within acquired end and the same root stage',
        'price_reference': 'last priced original trade strictly before formation end and inside formation',
        'source_filters': list(SOURCE_FILTERS),
        'horizon_kinds': list(HORIZON_KINDS),
        'selection': 'all fixed candidates retained; no chosen winning clock',
        'stage_policy': payload.get('stage_policy'),
        'identity': payload.get('identity', 'root+physicalsourcepath+hash+variant+instrument+rawcontract+formation/end'),
    }


def _pa():
    import pyarrow as pa
    return pa


def _i64_field(pa, name, nullable=False):
    return pa.field(name, pa.int64(), nullable=nullable)


def _f64_field(pa, name):
    return pa.field(name, pa.float64(), nullable=True)


def _flag_field(pa, name):
    return pa.field(name, pa.bool_(), nullable=False)


def _text_field(pa, name, nullable=False):
    return pa.field(name, pa.string(), nullable=nullable)


def _feature_fields(pa):
    fields = [
        _text_field(pa, 'root'), _text_field(pa, 'source_path'),
        _text_field(pa, 'source_metadata_sha256'), _text_field(pa, 'source_variant'),
        _i64_field(pa, 'acquired_event_start_ns'), _i64_field(pa, 'acquired_event_end_ns'),
        _i64_field(pa, 'instrument_id'), _text_field(pa, 'contract_key', nullable=True),
        _i64_field(pa, 'formation_minutes'), _i64_field(pa, 'cut_ns'),
        _i64_field(pa, 'event_start_ns'), _i64_field(pa, 'event_end_ns'),
        _i64_field(pa, 'known_at_ns'),
        _text_field(pa, 'formation_id'),
        _text_field(pa, 'stage'), _flag_field(pa, 'stage_boundary'),
        _flag_field(pa, 'left_censored'), _flag_field(pa, 'right_censored'),
        _text_field(pa, 'censor_reason', nullable=True),
        _flag_field(pa, 'atoms_complete'), _flag_field(pa, 'coordinate_complete'),
        _flag_field(pa, 'supplied_raw_coordinate_stable'),
        _flag_field(pa, 'source_instrument_presence'), _flag_field(pa, 'source_coverage_complete'),
        _flag_field(pa, 'flow_history_complete'), _flag_field(pa, 'price_history_complete'),
        _flag_field(pa, 'empty_observed_window'), _flag_field(pa, 'quote_coverage_complete'),
        _flag_field(pa, 'full_standing_window_eligible'),
        _flag_field(pa, 'full_pressure_transition_window_eligible'),
        _flag_field(pa, 'contract_transition'),
        _i64_field(pa, 'prints', nullable=True), _i64_field(pa, 'unpriced_prints', nullable=True),
        _i64_field(pa, 'first_priced_ticks', nullable=True),
        _i64_field(pa, 'first_priced_event_ns', nullable=True),
        _i64_field(pa, 'first_priced_known_at_ns', nullable=True),
        _i64_field(pa, 'first_priced_source_order', nullable=True),
        _i64_field(pa, 'first_priced_source_row', nullable=True),
        _i64_field(pa, 'last_priced_ticks', nullable=True),
        _i64_field(pa, 'last_priced_event_ns', nullable=True),
        _i64_field(pa, 'last_priced_known_at_ns', nullable=True),
        _i64_field(pa, 'last_priced_source_order', nullable=True),
        _i64_field(pa, 'last_priced_source_row', nullable=True),
        _i64_field(pa, 'reference_price_ticks', nullable=True),
        _i64_field(pa, 'reference_event_ns', nullable=True),
        _i64_field(pa, 'reference_known_at_ns', nullable=True),
        _i64_field(pa, 'reference_source_order', nullable=True),
        _i64_field(pa, 'reference_source_row', nullable=True),
        _i64_field(pa, 'observed_high_ticks', nullable=True),
        _i64_field(pa, 'observed_low_ticks', nullable=True),
        _i64_field(pa, 'observed_high_at_ns', nullable=True),
        _i64_field(pa, 'observed_low_at_ns', nullable=True),
        _i64_field(pa, 'observed_high_source_order', nullable=True),
        _i64_field(pa, 'observed_low_source_order', nullable=True),
        _i64_field(pa, 'priced_volume', nullable=True),
        _i64_field(pa, 'sum_price_volume', nullable=True),
        _i64_field(pa, 'sum_price_squared_volume', nullable=True),
        _f64_field(pa, 'vwap_ticks'), _f64_field(pa, 'variance_ticks_squared'),
        _i64_field(pa, 'ofi_open', nullable=True), _i64_field(pa, 'ofi_high', nullable=True),
        _i64_field(pa, 'ofi_low', nullable=True), _i64_field(pa, 'ofi_close', nullable=True),
        _i64_field(pa, 'ofi_high_at_ns', nullable=True), _i64_field(pa, 'ofi_low_at_ns', nullable=True),
        _i64_field(pa, 'ofi_high_source_order', nullable=True),
        _i64_field(pa, 'ofi_low_source_order', nullable=True),
        _i64_field(pa, 'ofi_contracts', nullable=True),
        _i64_field(pa, 'price_change_ofi', nullable=True),
        _i64_field(pa, 'same_price_size_ofi', nullable=True),
        _i64_field(pa, 'standing_duration_ns', nullable=True),
        _f64_field(pa, 'duration_mean_spread_ticks'), _f64_field(pa, 'duration_mean_imbalance'),
    ]
    for name in SOURCE_FILTERS:
        fields.extend([
            _i64_field(pa, f'{name}__buy', nullable=True),
            _i64_field(pa, f'{name}__sell', nullable=True),
            _i64_field(pa, f'{name}__unknown', nullable=True),
            _i64_field(pa, f'{name}__volume', nullable=True),
            _i64_field(pa, f'{name}__prints', nullable=True),
            _i64_field(pa, f'{name}__excluded_prints', nullable=True),
            _i64_field(pa, f'{name}__excluded_volume', nullable=True),
            _i64_field(pa, f'{name}__open', nullable=True),
            _i64_field(pa, f'{name}__high', nullable=True),
            _i64_field(pa, f'{name}__low', nullable=True),
            _i64_field(pa, f'{name}__close', nullable=True),
            _i64_field(pa, f'{name}__high_at_ns', nullable=True),
            _i64_field(pa, f'{name}__low_at_ns', nullable=True),
            _i64_field(pa, f'{name}__high_source_order', nullable=True),
            _i64_field(pa, f'{name}__low_source_order', nullable=True),
            _flag_field(pa, f'{name}__coverage_complete'),
            _i64_field(pa, f'{name}__observed_signed_lower', nullable=True),
            _i64_field(pa, f'{name}__observed_signed_upper', nullable=True),
            _i64_field(pa, f'{name}__true_signed_lower', nullable=True),
            _i64_field(pa, f'{name}__true_signed_upper', nullable=True),
        ])
    return fields


def _label_fields(pa):
    fields = [
        _text_field(pa, 'root'), _text_field(pa, 'source_path'),
        _text_field(pa, 'source_metadata_sha256'), _text_field(pa, 'source_variant'),
        _i64_field(pa, 'acquired_event_start_ns'), _i64_field(pa, 'acquired_event_end_ns'),
        _i64_field(pa, 'instrument_id'), _text_field(pa, 'contract_key', nullable=True),
        _i64_field(pa, 'cut_ns'), _i64_field(pa, 'latency_ns'),
        _text_field(pa, 'horizon_kind'), _i64_field(pa, 'horizon_minutes', nullable=True),
        _i64_field(pa, 'event_start_ns', nullable=True), _i64_field(pa, 'event_end_ns', nullable=True),
        _i64_field(pa, 'known_at_ns', nullable=True),
        _text_field(pa, 'label_id'),
        _text_field(pa, 'stage'), _flag_field(pa, 'stage_boundary'),
        _flag_field(pa, 'remaining_session_applicable'),
        _text_field(pa, 'remaining_session_disposition', nullable=True),
        _flag_field(pa, 'left_censored'), _flag_field(pa, 'right_censored'),
        _text_field(pa, 'censor_reason', nullable=True),
        _flag_field(pa, 'complete'), _flag_field(pa, 'chronological_eligible'),
        _flag_field(pa, 'data_complete'), _flag_field(pa, 'atoms_complete'),
        _flag_field(pa, 'coordinate_complete'), _flag_field(pa, 'supplied_raw_coordinate_stable'),
        _flag_field(pa, 'source_instrument_presence'), _flag_field(pa, 'source_coverage_complete'),
        _flag_field(pa, 'flow_history_complete'), _flag_field(pa, 'price_history_complete'),
        _flag_field(pa, 'contract_transition'), _flag_field(pa, 'contract_stable'),
        _flag_field(pa, 'no_new_trade'), _flag_field(pa, 'no_priced_trade'),
        _i64_field(pa, 'buy'), _i64_field(pa, 'sell'), _i64_field(pa, 'unknown'),
        _i64_field(pa, 'volume'), _i64_field(pa, 'prints'),
        _i64_field(pa, 'priced_prints'), _i64_field(pa, 'unpriced_prints'),
        _i64_field(pa, 'first_priced_ticks', nullable=True),
        _i64_field(pa, 'first_priced_event_ns', nullable=True),
        _i64_field(pa, 'first_priced_known_at_ns', nullable=True),
        _i64_field(pa, 'first_priced_source_order', nullable=True),
        _i64_field(pa, 'first_priced_source_row', nullable=True),
        _i64_field(pa, 'last_priced_ticks', nullable=True),
        _i64_field(pa, 'last_priced_event_ns', nullable=True),
        _i64_field(pa, 'last_priced_known_at_ns', nullable=True),
        _i64_field(pa, 'last_priced_source_order', nullable=True),
        _i64_field(pa, 'last_priced_source_row', nullable=True),
        _i64_field(pa, 'observed_high_ticks', nullable=True),
        _i64_field(pa, 'observed_low_ticks', nullable=True),
        _i64_field(pa, 'observed_high_at_ns', nullable=True),
        _i64_field(pa, 'observed_low_at_ns', nullable=True),
        _i64_field(pa, 'observed_high_source_order', nullable=True),
        _i64_field(pa, 'observed_low_source_order', nullable=True),
        _i64_field(pa, 'signed_open', nullable=True), _i64_field(pa, 'signed_high', nullable=True),
        _i64_field(pa, 'signed_low', nullable=True), _i64_field(pa, 'signed_close', nullable=True),
        _i64_field(pa, 'signed_high_at_ns', nullable=True),
        _i64_field(pa, 'signed_low_at_ns', nullable=True),
        _i64_field(pa, 'signed_high_source_order', nullable=True),
        _i64_field(pa, 'signed_low_source_order', nullable=True),
    ]
    for name in SOURCE_FILTERS:
        fields.extend([
            _i64_field(pa, f'{name}__buy'), _i64_field(pa, f'{name}__sell'),
            _i64_field(pa, f'{name}__unknown'), _i64_field(pa, f'{name}__volume'),
            _i64_field(pa, f'{name}__prints'),
            _i64_field(pa, f'{name}__excluded_prints'),
            _i64_field(pa, f'{name}__excluded_volume'),
            _i64_field(pa, f'{name}__open', nullable=True),
            _i64_field(pa, f'{name}__high', nullable=True),
            _i64_field(pa, f'{name}__low', nullable=True),
            _i64_field(pa, f'{name}__close', nullable=True),
            _i64_field(pa, f'{name}__high_at_ns', nullable=True),
            _i64_field(pa, f'{name}__low_at_ns', nullable=True),
            _i64_field(pa, f'{name}__high_source_order', nullable=True),
            _i64_field(pa, f'{name}__low_source_order', nullable=True),
        ])
    return fields


def feature_schema():
    """Explicit feature Arrow schema; nullable clocks stay null."""
    pa = _pa()
    return pa.schema(_feature_fields(pa))


def label_schema():
    """Explicit label Arrow schema; formation length is not repeated."""
    pa = _pa()
    return pa.schema(_label_fields(pa))


def feature_column_names():
    return tuple(field.name for field in feature_schema())


def label_column_names():
    return tuple(field.name for field in label_schema())


def _empty_table(schema):
    pa = _pa()
    return pa.table({field.name: pa.array([], type=field.type) for field in schema}, schema=schema)


def _table_from_rows(schema, rows):
    pa = _pa()
    names = [field.name for field in schema]
    if not rows:
        return _empty_table(schema)
    if any(set(row) != set(names) for row in rows):
        raise IntegrityError('window-link row columns must match the explicit schema exactly')
    return pa.table(
        {name: pa.array([row[name] for row in rows], type=schema.field(name).type) for name in names},
        schema=schema,
    )


def _i64_values(column, *, name, nullable=False):
    import numpy as np

    combined = column.combine_chunks() if hasattr(column, 'combine_chunks') else column
    if combined.null_count and not nullable:
        raise IntegrityError(f'{name} cannot contain nulls')
    valid = ~combined.is_null().to_numpy(zero_copy_only=False) if nullable else np.ones(len(combined), dtype=bool)
    filled = combined.fill_null(0) if combined.null_count else combined
    raw = filled.to_numpy(zero_copy_only=False)
    if raw.dtype.kind == 'f':
        raise IntegrityError(f'{name} must be exact integers without float rounding')
    if raw.dtype.kind == 'u':
        if raw.itemsize >= 8 and np.any(raw.astype(np.uint64, copy=False) > np.uint64(_INT64_MAX)):
            raise IntegrityError(f'{name} exceeds the exact int64 domain')
        values = np.array(raw, dtype=np.int64, copy=True)
        return values, np.asarray(valid, dtype=bool)
    if raw.dtype.kind != 'i':
        raise IntegrityError(f'{name} must be exact integers')
    values = np.array(raw, dtype=np.int64, copy=True)
    return values, np.asarray(valid, dtype=bool)


def _bool_values(column, *, name):
    import numpy as np

    combined = column.combine_chunks() if hasattr(column, 'combine_chunks') else column
    if combined.null_count:
        raise IntegrityError(f'{name} cannot contain nulls')
    raw = combined.to_numpy(zero_copy_only=False)
    if raw.dtype != bool and raw.dtype != np.bool_:
        raise IntegrityError(f'{name} must be an explicit boolean column')
    return np.array(raw, dtype=bool, copy=True)


def _f64_values(column, *, name):
    import numpy as np

    combined = column.combine_chunks() if hasattr(column, 'combine_chunks') else column
    raw = combined.to_numpy(zero_copy_only=False)
    values = np.array(raw, dtype=np.float64, copy=True)
    if combined.null_count:
        valid = ~combined.is_null().to_numpy(zero_copy_only=False)
        values = np.where(np.asarray(valid, dtype=bool), values, np.nan)
    return values


def _string_list(column, *, name, allow_null=True):
    out = []
    for item in column.to_pylist():
        if item is None:
            if not allow_null:
                raise IntegrityError(f'{name} cannot contain nulls')
            out.append(None)
        elif type(item) is not str:
            raise IntegrityError(f'{name} must be a string column')
        else:
            out.append(item)
    return out


def _validate_contract(contract):
    rec = _mapping(contract, what='contract')
    if rec.get('kind') != CONTRACT_KIND:
        raise ContractError('window-link contract kind is not the frozen causal-window contract')
    if rec.get('version') != CONTRACT_VERSION:
        raise ContractError('window-link contract version is not the frozen v1 contract')
    if list(rec.get('formation_minutes')) != list(FORMATION_MINUTES):
        raise ContractError('every declared formation candidate must be retained')
    if list(rec.get('latency_ns')) != list(LATENCY_NS):
        raise ContractError('every declared latency candidate must be retained')
    if list(rec.get('forward_horizons_minutes')) != list(FORWARD_HORIZONS_MINUTES):
        raise ContractError('every declared forward horizon must be retained')
    if rec.get('cut_cadence_ns') != CUT_CADENCE_NS:
        raise ContractError('cut cadence must be exact UTC five minutes')
    if rec.get('family_complete') is True:
        raise ContractError('this helper cannot certify family completion')
    stages = _mapping(rec.get('stage_policy'), what='stage_policy')
    parsed = {}
    for root, spec in stages.items():
        if root == 'other_dates':
            continue
        if root not in ('NQ', 'ES') or not isinstance(spec, dict):
            raise ContractError('stage policy must declare NQ and ES intervals')
        parsed[root] = {}
        for name in _STAGE_NAMES:
            pair = spec.get(name)
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise ContractError(f'{root} {name} stage must be an exact [start, end) date pair')
            parsed[root][name] = (_civil_date_ns(pair[0]), _civil_date_ns(pair[1]))
    return rec, parsed


def _validate_source_identity(source_identity):
    rec = _mapping(source_identity, what='source_identity')
    root = _text(rec.get('root'), what='source_identity.root')
    if root not in ('NQ', 'ES'):
        raise ContractError('source_identity.root must be NQ or ES')
    path = _text(rec.get('source_path'), what='source_identity.source_path')
    if '|' in path or ';' in path or '\n' in path:
        raise IntegrityError('source_path must name a single physical file')
    sha = _sha256_text(rec.get('source_metadata_sha256'), what='source_identity.source_metadata_sha256')
    variant = _text(rec.get('source_variant'), what='source_identity.source_variant')
    start = rec.get('acquired_event_start_ns', rec.get('acquired_start_ns'))
    end = rec.get('acquired_event_end_ns', rec.get('acquired_end_ns'))
    start = _int(start, what='acquired_event_start_ns', minimum=0)
    end = _int(end, what='acquired_event_end_ns', minimum=1)
    if not start < end:
        raise IntegrityError('acquired physical file event bounds must be a half-open [start, end)')
    return {
        'root': root,
        'source_path': path,
        'source_metadata_sha256': sha,
        'source_variant': variant,
        'acquired_event_start_ns': start,
        'acquired_event_end_ns': end,
    }


def _validate_cuts(cut_start_ns, cut_end_ns, acquired):
    start = _int(cut_start_ns, what='cut_start_ns', minimum=0)
    end = _int(cut_end_ns, what='cut_end_ns', minimum=1)
    if start >= end:
        raise ContractError('cut interval must be a positive half-open [start, end)')
    if start % CUT_CADENCE_NS or end % CUT_CADENCE_NS:
        raise ContractError('cut interval must fall on exact UTC five-minute boundaries')
    if end - start > MAX_CUT_SPAN_NS:
        raise ContractError('cut interval cannot exceed one UTC day')
    day_ns = 24 * 60 * MINUTE
    padded_start = acquired['acquired_event_start_ns'] // day_ns * day_ns
    padded_end = ((acquired['acquired_event_end_ns'] - 1) // day_ns + 1) * day_ns
    if start < padded_start or end > padded_end:
        raise IntegrityError('cut interval is outside the physical file UTC-day envelope')
    import numpy as np
    n_cuts = (end - start) // CUT_CADENCE_NS
    cuts = start + np.arange(n_cuts, dtype=np.int64) * np.int64(CUT_CADENCE_NS)
    return start, end, cuts


def _stage_of(root, at_ns, stages):
    intervals = stages.get(root)
    if not intervals or at_ns is None:
        return 'unassigned'
    for name, (begin, finish) in intervals.items():
        if begin <= at_ns < finish:
            return name
    return 'unassigned'


def _stage_pair(root, start_ns, known_at_ns, stages):
    left = _stage_of(root, start_ns, stages)
    right = _stage_of(root, known_at_ns, stages)
    if left != 'unassigned' and left == right:
        return left, False
    return 'unassigned', left != right or left == 'unassigned' or right == 'unassigned'


def _named_interval_stage(root, start_ns, end_ns, stages):
    left = _stage_of(root, start_ns, stages)
    right = _stage_of(root, end_ns, stages)
    if left == 'unassigned' or left != right:
        return 'unassigned'
    return left


def _remaining_session(calendar, cut_ns):
    try:
        day = _ny_date(cut_ns, calendar.zone)
        cash = calendar.resolve(day, cut=cut_ns)
    except DependencyUnavailable:
        return {
            'applicable': False,
            'disposition': 'calendar_unavailable',
            'open_at': None,
            'close_at': None,
            'state': None,
        }
    if cash.state == 'closed' or cash.open_at is None or cash.close_at is None:
        return {
            'applicable': False,
            'disposition': 'not_applicable_closed_or_missing_cash_date',
            'open_at': None,
            'close_at': None,
            'state': cash.state,
        }
    if not cash.open_at <= cut_ns < cash.close_at:
        return {
            'applicable': False,
            'disposition': 'not_applicable_outside_cash_rth',
            'open_at': cash.open_at,
            'close_at': cash.close_at,
            'state': cash.state,
        }
    return {
        'applicable': True,
        'disposition': None,
        'open_at': cash.open_at,
        'close_at': cash.close_at,
        'state': cash.state,
    }


def _require_table(table, *, what, names):
    pa = _pa()
    if not isinstance(table, pa.Table):
        raise ContractError(f'{what} must be a PyArrow table')
    missing = [name for name in names if name not in table.schema.names]
    if missing:
        raise ContractError(f'{what} lost required columns {missing[:8]}')
    return table


def _support_width(start_values, end_values, *, what):
    import numpy as np

    if not len(start_values):
        return
    width = int(np.max(end_values)) - int(np.min(start_values))
    if width > MAX_SOURCE_BUFFER_NS:
        raise IntegrityError(f'{what} exceeds the three-UTC-day source buffer')


def _observation_arrays(observations, identity, cut_start, cut_end):
    import numpy as np

    del cut_start, cut_end
    required = [
        'root', 'source_path', 'source_metadata_sha256', 'source_variant',
        'instrument_id', 'contract_key', 'event_start_ns', 'event_end_ns', 'known_at_ns',
        'coordinate_complete', 'supplied_raw_coordinate_stable',
        'source_instrument_presence', 'source_coverage_complete',
        'flow_history_complete', 'price_history_complete', 'empty_observed_window',
        'quote_coverage_complete', 'full_standing_window_eligible',
        'full_pressure_transition_window_eligible',
        'prints', 'unpriced_prints',
        'first_priced_ticks', 'first_priced_event_ns', 'first_priced_known_at_ns',
        'first_priced_source_order', 'first_priced_source_row',
        'last_priced_ticks', 'last_priced_event_ns', 'last_priced_known_at_ns',
        'last_priced_source_order', 'last_priced_source_row',
        'observed_high_ticks', 'observed_low_ticks',
        'observed_high_at_ns', 'observed_low_at_ns',
        'observed_high_source_order', 'observed_low_source_order',
        'priced_volume', 'sum_price_volume', 'sum_price_squared_volume',
        'ofi_open', 'ofi_high', 'ofi_low', 'ofi_close',
        'ofi_high_at_ns', 'ofi_low_at_ns', 'ofi_high_source_order', 'ofi_low_source_order',
        'ofi_contracts', 'price_change_ofi', 'same_price_size_ofi',
        'standing_duration_ns', 'duration_mean_spread_ticks', 'duration_mean_imbalance',
    ]
    for name in SOURCE_FILTERS:
        required.extend([
            f'{name}__buy', f'{name}__sell', f'{name}__unknown', f'{name}__volume',
            f'{name}__prints', f'{name}__excluded_prints', f'{name}__excluded_volume',
            f'{name}__open', f'{name}__high', f'{name}__low', f'{name}__close',
            f'{name}__high_at_ns', f'{name}__low_at_ns',
            f'{name}__high_source_order', f'{name}__low_source_order',
            f'{name}__coverage_complete',
        ])
    table = _require_table(observations, what='observations', names=required)
    if not len(table):
        return {'instruments': (), 'by_instrument': {}}
    roots = set(_string_list(table['root'], name='root', allow_null=False))
    paths = set(_string_list(table['source_path'], name='source_path', allow_null=False))
    shas = set(_string_list(table['source_metadata_sha256'], name='source_metadata_sha256', allow_null=False))
    variants = set(_string_list(table['source_variant'], name='source_variant', allow_null=False))
    if roots != {identity['root']} or paths != {identity['source_path']}:
        raise IntegrityError('observations cannot join a different root or physical source file')
    if shas != {identity['source_metadata_sha256']} or variants != {identity['source_variant']}:
        raise IntegrityError('observation source identity does not join source_identity')
    event_start, _ = _i64_values(table['event_start_ns'], name='event_start_ns')
    event_end, _ = _i64_values(table['event_end_ns'], name='event_end_ns')
    if np.any(event_end <= event_start):
        raise IntegrityError('observation atoms must be positive half-open intervals')
    _support_width(event_start, event_end, what='observation support')
    day_ns = 24 * 60 * MINUTE
    padded_start = identity['acquired_event_start_ns'] // day_ns * day_ns
    padded_end = ((identity['acquired_event_end_ns'] - 1) // day_ns + 1) * day_ns
    if np.any(event_start < padded_start) or np.any(event_end > padded_end):
        raise IntegrityError('observation atoms fall outside the physical file UTC-day envelope')
    instrument_id, _ = _i64_values(table['instrument_id'], name='instrument_id')
    if np.any(instrument_id <= 0):
        raise IntegrityError('instrument_id must be a positive raw identifier')
    unique = tuple(int(v) for v in np.unique(instrument_id))
    if len(unique) > MAX_INSTRUMENTS:
        raise ContractError('window-link input cannot exceed eight instruments')
    arrays = {
        'event_start': event_start,
        'event_end': event_end,
        'known_at_ns': _i64_values(table['known_at_ns'], name='known_at_ns')[0],
        'instrument_id': instrument_id,
        'contract_key': _string_list(table['contract_key'], name='contract_key'),
        'coordinate_complete': _bool_values(table['coordinate_complete'], name='coordinate_complete'),
        'supplied_raw_coordinate_stable': _bool_values(
            table['supplied_raw_coordinate_stable'], name='supplied_raw_coordinate_stable',
        ),
        'presence': _bool_values(table['source_instrument_presence'], name='source_instrument_presence'),
        'source_coverage_complete': _bool_values(table['source_coverage_complete'], name='source_coverage_complete'),
        'flow_history_complete': _bool_values(table['flow_history_complete'], name='flow_history_complete'),
        'price_history_complete': _bool_values(table['price_history_complete'], name='price_history_complete'),
        'empty_observed_window': _bool_values(table['empty_observed_window'], name='empty_observed_window'),
        'quote_coverage_complete': _bool_values(table['quote_coverage_complete'], name='quote_coverage_complete'),
        'standing_eligible': _bool_values(table['full_standing_window_eligible'], name='full_standing_window_eligible'),
        'pressure_eligible': _bool_values(
            table['full_pressure_transition_window_eligible'],
            name='full_pressure_transition_window_eligible',
        ),
        'prints': _i64_values(table['prints'], name='prints')[0],
        'unpriced_prints': _i64_values(table['unpriced_prints'], name='unpriced_prints')[0],
        'priced_volume': _i64_values(table['priced_volume'], name='priced_volume')[0],
        'sum_price_volume': _i64_values(table['sum_price_volume'], name='sum_price_volume')[0],
        'sum_price_squared_volume': _i64_values(table['sum_price_squared_volume'], name='sum_price_squared_volume')[0],
        'standing_duration_ns': _i64_values(table['standing_duration_ns'], name='standing_duration_ns')[0],
        'duration_mean_spread_ticks': _f64_values(table['duration_mean_spread_ticks'], name='duration_mean_spread_ticks'),
        'duration_mean_imbalance': _f64_values(table['duration_mean_imbalance'], name='duration_mean_imbalance'),
    }
    for name in (
        'first_priced_ticks', 'first_priced_event_ns', 'first_priced_known_at_ns',
        'first_priced_source_order', 'first_priced_source_row',
        'last_priced_ticks', 'last_priced_event_ns', 'last_priced_known_at_ns',
        'last_priced_source_order', 'last_priced_source_row',
        'observed_high_ticks', 'observed_low_ticks',
        'observed_high_at_ns', 'observed_low_at_ns',
        'observed_high_source_order', 'observed_low_source_order',
        'ofi_open', 'ofi_high', 'ofi_low', 'ofi_close',
        'ofi_high_at_ns', 'ofi_low_at_ns', 'ofi_high_source_order', 'ofi_low_source_order',
        'ofi_contracts', 'price_change_ofi', 'same_price_size_ofi',
    ):
        values, valid = _i64_values(table[name], name=name, nullable=True)
        arrays[name] = values
        arrays[f'{name}__valid'] = valid
    for cohort in SOURCE_FILTERS:
        for suffix in (
            'buy', 'sell', 'unknown', 'volume', 'prints', 'excluded_prints', 'excluded_volume',
        ):
            arrays[f'{cohort}__{suffix}'] = _i64_values(table[f'{cohort}__{suffix}'], name=f'{cohort}__{suffix}')[0]
        for suffix in ('open', 'high', 'low', 'close'):
            arrays[f'{cohort}__{suffix}'] = _i64_values(table[f'{cohort}__{suffix}'], name=f'{cohort}__{suffix}')[0]
        for suffix in ('high_at_ns', 'low_at_ns', 'high_source_order', 'low_source_order'):
            values, valid = _i64_values(table[f'{cohort}__{suffix}'], name=f'{cohort}__{suffix}', nullable=True)
            arrays[f'{cohort}__{suffix}'] = values
            arrays[f'{cohort}__{suffix}__valid'] = valid
        arrays[f'{cohort}__coverage_complete'] = _bool_values(
            table[f'{cohort}__coverage_complete'], name=f'{cohort}__coverage_complete',
        )
    grouped = {}
    for instrument in unique:
        mask = instrument_id == instrument
        idx = np.flatnonzero(mask)
        order = np.argsort(event_start[idx], kind='stable')
        idx = idx[order]
        if np.any(event_start[idx][1:] < event_start[idx][:-1]):
            raise IntegrityError('observation atoms must be ordered by event_start_ns')
        if np.any(event_end[idx][:-1] > event_start[idx][1:]):
            raise IntegrityError('observation atoms cannot overlap for one instrument')
        grouped[instrument] = idx
    return {'instruments': unique, 'arrays': arrays, 'by_instrument': grouped}


def _trade_arrays(trades, identity, cut_start, cut_end):
    import numpy as np

    del cut_start, cut_end
    table = _require_table(trades, what='trades', names=_TRADE_REQUIRED)
    extra = [name for name in TRADE_FIELDS if name not in table.schema.names]
    _ = extra
    if not len(table):
        return {'instruments': (), 'by_instrument': {}, 'delay_ok': True, 'delays': ()}
    event_ns, _ = _i64_values(table['t'], name='t')
    source_order, _ = _i64_values(table['source_order'], name='source_order')
    instrument_id, _ = _i64_values(table['instrument_id'], name='instrument_id')
    price, _ = _i64_values(table['price'], name='price')
    size, _ = _i64_values(table['size'], name='size')
    side, _ = _i64_values(table['side'], name='side')
    price_valid, _ = _i64_values(table['price_valid'], name='price_valid')
    source_row, _ = _i64_values(table['source_row'], name='source_row')
    known_at, _ = _i64_values(table['known_at_ns'], name='known_at_ns')
    if np.any(instrument_id <= 0) or np.any(size <= 0) or np.any(size >= 2 ** 32 - 1):
        raise IntegrityError('trade instrument and size must be exact positive bounded integers')
    if len(size) and int(np.max(size)) * int(len(size)) > _INT64_MAX:
        raise IntegrityError('trade size prefix exceeds the exact int64 domain')
    if np.any(~np.isin(side, (-1, 0, 1))) or np.any(~np.isin(price_valid, (0, 1))):
        raise IntegrityError('trade side must be buy/sell/unknown and price_valid must be 0 or 1')
    if np.any(event_ns < 0) or np.any(source_order < 0) or np.any(source_row < 0):
        raise IntegrityError('trade clocks and addresses must be nonnegative')
    _support_width(event_ns, event_ns, what='trade support')
    if np.any(event_ns < identity['acquired_event_start_ns']) or np.any(event_ns >= identity['acquired_event_end_ns']):
        raise IntegrityError('trades fall outside the acquired physical file bounds')
    delays = known_at.astype(np.int64, copy=False) - event_ns
    if not bool(np.all(delays == SOURCE_LATENCY_NS)):
        raise IntegrityError('stored trade known_at_ns must equal event time plus the 250ms source latency')
    unique = tuple(int(v) for v in np.unique(instrument_id))
    if len(unique) > MAX_INSTRUMENTS:
        raise ContractError('window-link input cannot exceed eight instruments')
    grouped = {}
    for instrument in unique:
        idx = np.flatnonzero(instrument_id == instrument)
        events = event_ns[idx]
        orders = source_order[idx]
        if np.any(events[1:] < events[:-1]) or np.any(orders[1:] <= orders[:-1]):
            raise IntegrityError('trade order must be ordinary monotone in the physical source; unplanned nonmonotone trades are rejected')
        grouped[instrument] = {
            'event_ns': event_ns[idx],
            'source_order': source_order[idx],
            'price': price[idx],
            'size': size[idx],
            'side': side[idx],
            'price_valid': price_valid[idx].astype(bool),
            'source_row': source_row[idx],
            'known_at_ns': known_at[idx],
        }
    return {
        'instruments': unique,
        'by_instrument': grouped,
        'delay_ok': True,
        'delays': (SOURCE_LATENCY_NS,),
        'n': int(len(table)),
    }


def _weighted_duration_mean(means, weights):
    import numpy as np

    standing = np.asarray(weights, dtype=np.int64)
    values = np.asarray(means, dtype=np.float64)
    usable = (standing > 0) & np.isfinite(values)
    if not np.any(usable):
        return None
    denom = _add_checked(*standing[usable].tolist(), what='standing_duration_ns')
    if denom == 0:
        return None
    return float(np.sum(values[usable] * standing[usable].astype(np.float64)) / float(denom))


def _concat_offset_path(open_a, high_a, low_a, close_a, high_at, low_at, high_ord, low_ord,
                        high_at_ok, low_at_ok, high_ord_ok, low_ord_ok):
    import numpy as np

    n = len(open_a)
    if n == 0:
        return None
    rel_high = []
    rel_low = []
    offset = 0
    for i in range(n):
        opened = int(open_a[i])
        high = int(high_a[i])
        low = int(low_a[i])
        close = int(close_a[i])
        rel_high.append(_add_checked(offset, _sub_checked(high, opened, what='path_rel_high'), what='path_high_offset'))
        rel_low.append(_add_checked(offset, _sub_checked(low, opened, what='path_rel_low'), what='path_low_offset'))
        offset = _add_checked(offset, _sub_checked(close, opened, what='path_rel_close'), what='path_offset')
    high_arr = np.asarray(rel_high, dtype=np.int64)
    low_arr = np.asarray(rel_low, dtype=np.int64)
    hi = int(np.argmax(high_arr))
    lo = int(np.argmin(low_arr))
    return {
        'open': 0,
        'high': int(rel_high[hi]),
        'low': int(rel_low[lo]),
        'close': offset,
        'high_at_ns': int(high_at[hi]) if high_at_ok[hi] else None,
        'low_at_ns': int(low_at[lo]) if low_at_ok[lo] else None,
        'high_source_order': int(high_ord[hi]) if high_ord_ok[hi] else None,
        'low_source_order': int(low_ord[lo]) if low_ord_ok[lo] else None,
    }


def _first_nonnull(values, valid):
    import numpy as np

    if not np.any(valid):
        return None, None
    index = int(np.flatnonzero(valid)[0])
    return int(values[index]), index


def _last_nonnull(values, valid):
    import numpy as np

    if not np.any(valid):
        return None, None
    index = int(np.flatnonzero(valid)[-1])
    return int(values[index]), index


def _price_extrema(ticks, valid, at_ns, at_ok, orders, order_ok):
    import numpy as np

    if not np.any(valid):
        return None, None, None, None, None, None
    usable = ticks[valid]
    hi_local = int(np.argmax(usable))
    lo_local = int(np.argmin(usable))
    idx = np.flatnonzero(valid)
    hi = int(idx[hi_local])
    lo = int(idx[lo_local])
    return (
        int(ticks[hi]), int(ticks[lo]),
        int(at_ns[hi]) if at_ok[hi] else None,
        int(at_ns[lo]) if at_ok[lo] else None,
        int(orders[hi]) if order_ok[hi] else None,
        int(orders[lo]) if order_ok[lo] else None,
    )


def _formation_id(identity, instrument_id, contract_key, minutes, cut_ns):
    key = '' if contract_key is None else contract_key
    return (
        f"{identity['root']}|{identity['source_path']}|{identity['source_metadata_sha256']}"
        f"|{identity['source_variant']}|{instrument_id}|{key}|{minutes}|{cut_ns}"
    )


def _label_id(identity, instrument_id, contract_key, cut_ns, latency, horizon_kind, horizon_minutes):
    key = '' if contract_key is None else contract_key
    minutes = '' if horizon_minutes is None else horizon_minutes
    return (
        f"{identity['root']}|{identity['source_path']}|{identity['source_metadata_sha256']}"
        f"|{identity['source_variant']}|{instrument_id}|{key}|{cut_ns}|{latency}|{horizon_kind}|{minutes}"
    )


def _null_cohort_fields():
    row = {}
    for name in SOURCE_FILTERS:
        for suffix in (
            'buy', 'sell', 'unknown', 'volume', 'prints', 'excluded_prints', 'excluded_volume',
            'open', 'high', 'low', 'close', 'high_at_ns', 'low_at_ns',
            'high_source_order', 'low_source_order',
            'observed_signed_lower', 'observed_signed_upper',
            'true_signed_lower', 'true_signed_upper',
        ):
            row[f'{name}__{suffix}'] = None
        row[f'{name}__coverage_complete'] = False
    return row


def _slice_atoms(arrays, idx, left, right):
    view = {}
    take = idx[left:right]
    for key, value in arrays.items():
        if key == 'contract_key':
            view[key] = [value[int(i)] for i in take]
        else:
            view[key] = value[take]
    return view


def _vwap_moments(priced_volume, sum_pv, sum_p2v):
    if not priced_volume:
        return None, None
    numerator = int(priced_volume) * int(sum_p2v) - int(sum_pv) * int(sum_pv)
    if numerator < 0:
        raise IntegrityError('VWAP variance numerator must be nonnegative')
    denom = int(priced_volume) * int(priced_volume)
    return float(sum_pv) / float(priced_volume), float(numerator) / float(denom)


def _window_quality(view, tiled):
    import numpy as np

    if view is None or not tiled:
        return {
            'coordinate_complete': False,
            'supplied_raw_coordinate_stable': False,
            'source_instrument_presence': False,
            'source_coverage_complete': False,
            'flow_history_complete': False,
            'price_history_complete': False,
            'empty_observed_window': False,
            'quote_coverage_complete': False,
            'full_standing_window_eligible': False,
            'full_pressure_transition_window_eligible': False,
        }
    return {
        'coordinate_complete': bool(np.all(view['coordinate_complete'])),
        'supplied_raw_coordinate_stable': bool(np.all(view['supplied_raw_coordinate_stable'])),
        'source_instrument_presence': bool(np.all(view['presence'])),
        'source_coverage_complete': bool(np.all(view['source_coverage_complete'])),
        'flow_history_complete': bool(np.all(view['flow_history_complete'])),
        'price_history_complete': bool(np.all(view['price_history_complete'])),
        'empty_observed_window': bool(np.all(view['empty_observed_window'])),
        'quote_coverage_complete': bool(np.all(view['quote_coverage_complete'])),
        'full_standing_window_eligible': bool(np.all(view['standing_eligible'])),
        'full_pressure_transition_window_eligible': bool(np.all(view['pressure_eligible'])),
    }


def _feature_row(identity, instrument_id, minutes, cut_ns, arrays, idx, stages):
    import numpy as np

    start = cut_ns - minutes * MINUTE
    known = cut_ns + SOURCE_LATENCY_NS
    stage, boundary = _stage_pair(identity['root'], start, known, stages)
    starts = arrays['event_start'][idx]
    ends = arrays['event_end'][idx]
    left = int(np.searchsorted(starts, start, side='left'))
    right = int(np.searchsorted(starts, cut_ns, side='left'))
    left_censor = start < identity['acquired_event_start_ns'] or left >= right or int(starts[left]) > start
    right_censor = cut_ns > identity['acquired_event_end_ns'] or left >= right or int(ends[right - 1]) < cut_ns
    tiled = False
    if left < right:
        window_starts = starts[left:right]
        window_ends = ends[left:right]
        tiled = (
            int(window_starts[0]) == start
            and int(window_ends[-1]) == cut_ns
            and (
                len(window_starts) == 1
                or np.all(window_starts[1:] == window_ends[:-1])
            )
        )
    reasons = []
    if left_censor:
        reasons.append('missing_left_atom')
    if right_censor:
        reasons.append('missing_right_atom')
    if left < right and not tiled:
        reasons.append('incomplete_atom_coverage')
    view = _slice_atoms(arrays, idx, left, right) if left < right else None
    raw_keys = [] if view is None else list(view['contract_key'])
    distinct = set(raw_keys)
    transition = len(distinct) > 1
    contract_key = None if transition or not distinct or None in distinct else next(iter(distinct))
    if transition:
        reasons.append('contract_transition')
    if not tiled and not reasons:
        reasons.append('incomplete_atom_coverage')
    row = {
        'root': identity['root'],
        'source_path': identity['source_path'],
        'source_metadata_sha256': identity['source_metadata_sha256'],
        'source_variant': identity['source_variant'],
        'acquired_event_start_ns': identity['acquired_event_start_ns'],
        'acquired_event_end_ns': identity['acquired_event_end_ns'],
        'instrument_id': instrument_id,
        'contract_key': contract_key,
        'formation_minutes': minutes,
        'cut_ns': cut_ns,
        'event_start_ns': start,
        'event_end_ns': cut_ns,
        'known_at_ns': known,
        'formation_id': _formation_id(identity, instrument_id, contract_key, minutes, cut_ns),
        'stage': stage,
        'stage_boundary': boundary,
        'left_censored': bool(left_censor),
        'right_censored': bool(right_censor),
        'censor_reason': None if tiled and not transition else ','.join(reasons) if reasons else 'incomplete_atom_coverage',
        'atoms_complete': tiled,
        'contract_transition': transition,
        'prints': None,
        'unpriced_prints': None,
        'priced_volume': None,
        'sum_price_volume': None,
        'sum_price_squared_volume': None,
    }
    row.update(_window_quality(view, tiled and not left_censor and not right_censor))
    for name in _FEATURE_NULL_INTS:
        row[name] = None
    row['vwap_ticks'] = None
    row['variance_ticks_squared'] = None
    row['standing_duration_ns'] = None
    row['duration_mean_spread_ticks'] = None
    row['duration_mean_imbalance'] = None
    row.update(_null_cohort_fields())
    if view is None:
        return row
    row['prints'] = _add_checked(*view['prints'].tolist(), what='prints')
    row['unpriced_prints'] = _add_checked(*view['unpriced_prints'].tolist(), what='unpriced_prints')
    priced_volume = _add_checked(*view['priced_volume'].tolist(), what='priced_volume')
    sum_pv = _add_checked(*view['sum_price_volume'].tolist(), what='sum_price_volume')
    sum_p2v = _add_checked(*view['sum_price_squared_volume'].tolist(), what='sum_price_squared_volume')
    row['priced_volume'] = priced_volume
    row['sum_price_volume'] = sum_pv
    row['sum_price_squared_volume'] = sum_p2v
    row['vwap_ticks'], row['variance_ticks_squared'] = _vwap_moments(priced_volume, sum_pv, sum_p2v)
    first_ticks, first_i = _first_nonnull(view['first_priced_ticks'], view['first_priced_ticks__valid'])
    last_ticks, last_i = _last_nonnull(view['last_priced_ticks'], view['last_priced_ticks__valid'])
    if first_i is not None:
        row['first_priced_ticks'] = first_ticks
        row['first_priced_event_ns'] = int(view['first_priced_event_ns'][first_i]) if view['first_priced_event_ns__valid'][first_i] else None
        row['first_priced_known_at_ns'] = int(view['first_priced_known_at_ns'][first_i]) if view['first_priced_known_at_ns__valid'][first_i] else None
        row['first_priced_source_order'] = int(view['first_priced_source_order'][first_i]) if view['first_priced_source_order__valid'][first_i] else None
        row['first_priced_source_row'] = int(view['first_priced_source_row'][first_i]) if view['first_priced_source_row__valid'][first_i] else None
    if last_i is not None:
        row['last_priced_ticks'] = last_ticks
        row['last_priced_event_ns'] = int(view['last_priced_event_ns'][last_i]) if view['last_priced_event_ns__valid'][last_i] else None
        row['last_priced_known_at_ns'] = int(view['last_priced_known_at_ns'][last_i]) if view['last_priced_known_at_ns__valid'][last_i] else None
        row['last_priced_source_order'] = int(view['last_priced_source_order'][last_i]) if view['last_priced_source_order__valid'][last_i] else None
        row['last_priced_source_row'] = int(view['last_priced_source_row'][last_i]) if view['last_priced_source_row__valid'][last_i] else None
        row['reference_price_ticks'] = row['last_priced_ticks']
        row['reference_event_ns'] = row['last_priced_event_ns']
        row['reference_known_at_ns'] = row['last_priced_known_at_ns']
        row['reference_source_order'] = row['last_priced_source_order']
        row['reference_source_row'] = row['last_priced_source_row']
    high, low, high_at, low_at, high_ord, low_ord = _price_extrema(
        view['observed_high_ticks'], view['observed_high_ticks__valid'],
        view['observed_high_at_ns'], view['observed_high_at_ns__valid'],
        view['observed_high_source_order'], view['observed_high_source_order__valid'],
    )
    if high is not None:
        row['observed_high_ticks'] = high
        row['observed_high_at_ns'] = high_at
        row['observed_high_source_order'] = high_ord
    _low_high, low_low, _low_high_at, low_low_at, _low_high_ord, low_low_ord = _price_extrema(
        view['observed_low_ticks'], view['observed_low_ticks__valid'],
        view['observed_low_at_ns'], view['observed_low_at_ns__valid'],
        view['observed_low_source_order'], view['observed_low_source_order__valid'],
    )
    if low_low is not None:
        row['observed_low_ticks'] = low_low
        row['observed_low_at_ns'] = low_low_at
        row['observed_low_source_order'] = low_low_ord
    standing = _add_checked(*view['standing_duration_ns'].tolist(), what='standing_duration_ns')
    row['standing_duration_ns'] = standing
    row['duration_mean_spread_ticks'] = _weighted_duration_mean(
        view['duration_mean_spread_ticks'], view['standing_duration_ns'])
    row['duration_mean_imbalance'] = _weighted_duration_mean(
        view['duration_mean_imbalance'], view['standing_duration_ns'])
    for name in SOURCE_FILTERS:
        row[f'{name}__buy'] = _add_checked(*view[f'{name}__buy'].tolist(), what=f'{name}__buy')
        row[f'{name}__sell'] = _add_checked(*view[f'{name}__sell'].tolist(), what=f'{name}__sell')
        row[f'{name}__unknown'] = _add_checked(*view[f'{name}__unknown'].tolist(), what=f'{name}__unknown')
        row[f'{name}__volume'] = _add_checked(*view[f'{name}__volume'].tolist(), what=f'{name}__volume')
        row[f'{name}__prints'] = _add_checked(*view[f'{name}__prints'].tolist(), what=f'{name}__prints')
        row[f'{name}__excluded_prints'] = _add_checked(*view[f'{name}__excluded_prints'].tolist(), what=f'{name}__excluded_prints')
        row[f'{name}__excluded_volume'] = _add_checked(*view[f'{name}__excluded_volume'].tolist(), what=f'{name}__excluded_volume')
        row[f'{name}__coverage_complete'] = bool(tiled and np.all(view[f'{name}__coverage_complete']))
    if not tiled or transition:
        return row
    if (
        row['full_pressure_transition_window_eligible']
        and np.all(view['ofi_open__valid'])
        and np.all(view['ofi_high__valid'])
        and np.all(view['ofi_low__valid'])
        and np.all(view['ofi_close__valid'])
    ):
        ofi = _concat_offset_path(
            view['ofi_open'], view['ofi_high'], view['ofi_low'], view['ofi_close'],
            view['ofi_high_at_ns'], view['ofi_low_at_ns'],
            view['ofi_high_source_order'], view['ofi_low_source_order'],
            view['ofi_high_at_ns__valid'], view['ofi_low_at_ns__valid'],
            view['ofi_high_source_order__valid'], view['ofi_low_source_order__valid'],
        )
        if ofi is not None:
            row['ofi_open'] = ofi['open']
            row['ofi_high'] = ofi['high']
            row['ofi_low'] = ofi['low']
            row['ofi_close'] = ofi['close']
            row['ofi_high_at_ns'] = ofi['high_at_ns']
            row['ofi_low_at_ns'] = ofi['low_at_ns']
            row['ofi_high_source_order'] = ofi['high_source_order']
            row['ofi_low_source_order'] = ofi['low_source_order']
            row['ofi_contracts'] = _add_checked(*view['ofi_contracts'].tolist(), what='ofi_contracts')
            row['price_change_ofi'] = _add_checked(*view['price_change_ofi'].tolist(), what='price_change_ofi')
            row['same_price_size_ofi'] = _add_checked(*view['same_price_size_ofi'].tolist(), what='same_price_size_ofi')
    true_ok = (
        row['flow_history_complete']
        and row['source_instrument_presence']
        and row['coordinate_complete']
        and row['supplied_raw_coordinate_stable']
    )
    for name in SOURCE_FILTERS:
        path = _concat_offset_path(
            view[f'{name}__open'], view[f'{name}__high'], view[f'{name}__low'], view[f'{name}__close'],
            view[f'{name}__high_at_ns'], view[f'{name}__low_at_ns'],
            view[f'{name}__high_source_order'], view[f'{name}__low_source_order'],
            view[f'{name}__high_at_ns__valid'], view[f'{name}__low_at_ns__valid'],
            view[f'{name}__high_source_order__valid'], view[f'{name}__low_source_order__valid'],
        )
        if path is None:
            continue
        row[f'{name}__open'] = path['open']
        row[f'{name}__high'] = path['high']
        row[f'{name}__low'] = path['low']
        row[f'{name}__close'] = path['close']
        row[f'{name}__high_at_ns'] = path['high_at_ns']
        row[f'{name}__low_at_ns'] = path['low_at_ns']
        row[f'{name}__high_source_order'] = path['high_source_order']
        row[f'{name}__low_source_order'] = path['low_source_order']
        unknown = row[f'{name}__unknown']
        close = path['close']
        row[f'{name}__observed_signed_lower'] = close - unknown
        row[f'{name}__observed_signed_upper'] = close + unknown
        if true_ok and row[f'{name}__coverage_complete']:
            row[f'{name}__true_signed_lower'] = close - unknown
            row[f'{name}__true_signed_upper'] = close + unknown
    return row


def _prefix_side(size, side, sign):
    import numpy as np

    chosen = np.where(side == sign, size, 0).astype(np.int64, copy=False)
    return np.concatenate((np.array([0], dtype=np.int64), np.cumsum(chosen, dtype=np.int64)))


def _prefix_bool(size, mask):
    import numpy as np

    chosen = np.where(mask, size, 0).astype(np.int64, copy=False)
    return np.concatenate((np.array([0], dtype=np.int64), np.cumsum(chosen, dtype=np.int64)))


def _prefix_count(mask):
    import numpy as np

    chosen = mask.astype(np.int64)
    return np.concatenate((np.array([0], dtype=np.int64), np.cumsum(chosen, dtype=np.int64)))


def _range_sum(prefix, left, right):
    return int(prefix[right] - prefix[left])


def _signed_path(event_ns, source_order, size, side, mask, left, right):
    import numpy as np

    if left >= right or not np.any(mask[left:right]):
        return {
            'open': 0, 'high': 0, 'low': 0, 'close': 0,
            'high_at_ns': None, 'low_at_ns': None,
            'high_source_order': None, 'low_source_order': None,
        }
    signed = (size[left:right] * side[left:right] * mask[left:right].astype(np.int64)).astype(np.int64, copy=False)
    path = np.cumsum(signed, dtype=np.int64)
    high_i = int(np.argmax(path))
    low_i = int(np.argmin(path))
    high = int(path[high_i])
    low = int(path[low_i])
    close = int(path[-1])
    if high < 0:
        high, high_at, high_ord = 0, None, None
    else:
        high_at, high_ord = int(event_ns[left + high_i]), int(source_order[left + high_i])
    if low > 0:
        low, low_at, low_ord = 0, None, None
    else:
        low_at, low_ord = int(event_ns[left + low_i]), int(source_order[left + low_i])
    return {
        'open': 0, 'high': high, 'low': low, 'close': close,
        'high_at_ns': high_at, 'low_at_ns': low_at,
        'high_source_order': high_ord, 'low_source_order': low_ord,
    }


def _price_window(event_ns, source_order, source_row, price, valid, known_at, latency, left, right):
    import numpy as np

    if left >= right:
        return {}
    usable = valid[left:right]
    if not np.any(usable):
        return {'no_priced_trade': True}
    idx = np.flatnonzero(usable) + left
    first, last = int(idx[0]), int(idx[-1])
    priced = price[idx]
    hi_local = int(np.argmax(priced))
    lo_local = int(np.argmin(priced))
    hi, lo = int(idx[hi_local]), int(idx[lo_local])
    return {
        'no_priced_trade': False,
        'first_priced_ticks': int(price[first]),
        'first_priced_event_ns': int(event_ns[first]),
        'first_priced_known_at_ns': int(event_ns[first] + latency),
        'first_priced_source_order': int(source_order[first]),
        'first_priced_source_row': int(source_row[first]),
        'last_priced_ticks': int(price[last]),
        'last_priced_event_ns': int(event_ns[last]),
        'last_priced_known_at_ns': int(event_ns[last] + latency),
        'last_priced_source_order': int(source_order[last]),
        'last_priced_source_row': int(source_row[last]),
        'observed_high_ticks': int(price[hi]),
        'observed_low_ticks': int(price[lo]),
        'observed_high_at_ns': int(event_ns[hi]),
        'observed_low_at_ns': int(event_ns[lo]),
        'observed_high_source_order': int(source_order[hi]),
        'observed_low_source_order': int(source_order[lo]),
        'stored_first_known_at_ns': int(known_at[first]),
        'stored_last_known_at_ns': int(known_at[last]),
    }


def _cohort_mask(size, name):
    lower, upper = _COHORT_BOUNDS[name]
    chosen = size >= lower
    if upper is not None:
        chosen = chosen & (size < upper)
    return chosen


def _empty_label_coverage(*, reason, extra=()):
    reasons = [item for item in extra if item]
    if reason not in reasons:
        reasons.append(reason)
    return {
        'atoms_complete': False,
        'coordinate_complete': False,
        'supplied_raw_coordinate_stable': False,
        'source_instrument_presence': False,
        'source_coverage_complete': False,
        'flow_history_complete': False,
        'price_history_complete': False,
        'contract_transition': False,
        'contract_stable': False,
        'data_complete': False,
        'reasons': reasons,
        'obs_known_at_ns': None,
    }


def _label_observation_state(arrays, idx, start, end, reference_contract):
    import numpy as np

    absent = ('stale_or_absent_contract',) if reference_contract is None else ()
    if arrays is None or idx is None or len(idx) == 0:
        return _empty_label_coverage(reason='missing_future_atom', extra=absent)
    domain_start = _minute_floor(start)
    domain_end = _minute_ceil(end)
    starts = arrays['event_start'][idx]
    ends = arrays['event_end'][idx]
    overlap = (starts < domain_end) & (ends > domain_start)
    if not np.any(overlap):
        return _empty_label_coverage(reason='missing_future_atom', extra=absent)
    sel = np.flatnonzero(overlap)
    take = idx[sel]
    keys = [arrays['contract_key'][int(i)] for i in take]
    distinct = set(keys)
    transition = len(distinct) > 1
    contiguous = len(sel) == 1 or np.all(np.diff(sel) == 1)
    window_starts = starts[sel]
    window_ends = ends[sel]
    tiled = bool(
        contiguous
        and int(window_starts[0]) == domain_start
        and int(window_ends[-1]) == domain_end
        and (len(sel) == 1 or np.all(window_starts[1:] == window_ends[:-1]))
    )
    stable = (
        not transition
        and None not in distinct
        and reference_contract is not None
        and distinct == {reference_contract}
    )
    quality = {
        'coordinate_complete': bool(tiled and np.all(arrays['coordinate_complete'][take])),
        'supplied_raw_coordinate_stable': bool(tiled and np.all(arrays['supplied_raw_coordinate_stable'][take])),
        'source_instrument_presence': bool(tiled and np.all(arrays['presence'][take])),
        'source_coverage_complete': bool(tiled and np.all(arrays['source_coverage_complete'][take])),
        'flow_history_complete': bool(tiled and np.all(arrays['flow_history_complete'][take])),
        'price_history_complete': bool(tiled and np.all(arrays['price_history_complete'][take])),
    }
    reasons = []
    if not tiled:
        reasons.append('incomplete_atom_coverage' if np.any(overlap) else 'missing_future_atom')
    if reference_contract is None:
        reasons.append('stale_or_absent_contract')
    if transition:
        reasons.append('contract_transition')
    elif not stable:
        reasons.append('mixed_or_mismatched_contract')
    if tiled and not quality['source_coverage_complete']:
        reasons.append('source_coverage_incomplete')
    if tiled and not quality['flow_history_complete']:
        reasons.append('flow_history_incomplete')
    if tiled and not quality['price_history_complete']:
        reasons.append('price_history_incomplete')
    if tiled and not quality['source_instrument_presence']:
        reasons.append('presence_incomplete')
    if tiled and not quality['coordinate_complete']:
        reasons.append('coordinate_incomplete')
    if tiled and not quality['supplied_raw_coordinate_stable']:
        reasons.append('coordinate_unstable')
    data_complete = bool(
        tiled
        and stable
        and quality['source_coverage_complete']
        and quality['flow_history_complete']
        and quality['price_history_complete']
        and quality['source_instrument_presence']
        and quality['coordinate_complete']
        and quality['supplied_raw_coordinate_stable']
    )
    return {
        'atoms_complete': tiled,
        'contract_transition': transition,
        'contract_stable': stable,
        'data_complete': data_complete,
        'reasons': reasons,
        'obs_known_at_ns': int(np.max(arrays['known_at_ns'][take])),
        **quality,
    }


def _apply_signed(row, path, *, prefix):
    row[f'{prefix}open'] = path['open']
    row[f'{prefix}high'] = path['high']
    row[f'{prefix}low'] = path['low']
    row[f'{prefix}close'] = path['close']
    row[f'{prefix}high_at_ns'] = path['high_at_ns']
    row[f'{prefix}low_at_ns'] = path['low_at_ns']
    row[f'{prefix}high_source_order'] = path['high_source_order']
    row[f'{prefix}low_source_order'] = path['low_source_order']


def _label_row(identity, instrument_id, contract_key, cut_ns, latency, horizon_kind, horizon_minutes,
               start, end, acquired_end, calendar_state, trades, stages, arrays, idx):
    import numpy as np

    remaining_applicable = horizon_kind == 'remaining_session' and calendar_state['applicable']
    disposition = None
    if horizon_kind == 'remaining_session':
        disposition = None if remaining_applicable else calendar_state['disposition']
    left_censor = False
    right_censor = False
    reasons = []
    chronological = False
    coverage = _empty_label_coverage(reason='remaining_session_not_applicable')
    known = None
    if start is None or end is None:
        reasons.append(disposition or 'remaining_session_not_applicable')
        stage, boundary = 'unassigned', False
    else:
        coverage = _label_observation_state(arrays, idx, start, end, contract_key)
        scenario_known = end + latency
        known = scenario_known if coverage['obs_known_at_ns'] is None else max(scenario_known, coverage['obs_known_at_ns'])
        stage, boundary = _stage_pair(identity['root'], cut_ns, known, stages)
        if start < identity['acquired_event_start_ns']:
            left_censor = True
            reasons.append('left_of_acquired')
        if end > acquired_end or known > acquired_end:
            right_censor = True
            reasons.append('right_future_endpoint')
        chronological = (
            not left_censor
            and not right_censor
            and (horizon_kind != 'remaining_session' or remaining_applicable)
        )
        reasons.extend(coverage['reasons'])
    data_complete = bool(start is not None and end is not None and coverage['data_complete'])
    complete = bool(chronological and data_complete)
    if complete:
        reasons = []
    row = {
        'root': identity['root'],
        'source_path': identity['source_path'],
        'source_metadata_sha256': identity['source_metadata_sha256'],
        'source_variant': identity['source_variant'],
        'acquired_event_start_ns': identity['acquired_event_start_ns'],
        'acquired_event_end_ns': identity['acquired_event_end_ns'],
        'instrument_id': instrument_id,
        'contract_key': contract_key,
        'cut_ns': cut_ns,
        'latency_ns': latency,
        'horizon_kind': horizon_kind,
        'horizon_minutes': horizon_minutes,
        'event_start_ns': start,
        'event_end_ns': end,
        'known_at_ns': known,
        'label_id': _label_id(identity, instrument_id, contract_key, cut_ns, latency, horizon_kind, horizon_minutes),
        'stage': stage,
        'stage_boundary': boundary,
        'remaining_session_applicable': remaining_applicable,
        'remaining_session_disposition': disposition,
        'left_censored': left_censor,
        'right_censored': right_censor,
        'censor_reason': None if complete else ','.join(dict.fromkeys(reasons)) if reasons else 'incomplete_label',
        'complete': complete,
        'chronological_eligible': chronological,
        'data_complete': data_complete,
        'atoms_complete': coverage['atoms_complete'],
        'coordinate_complete': coverage['coordinate_complete'],
        'supplied_raw_coordinate_stable': coverage['supplied_raw_coordinate_stable'],
        'source_instrument_presence': coverage['source_instrument_presence'],
        'source_coverage_complete': coverage['source_coverage_complete'],
        'flow_history_complete': coverage['flow_history_complete'],
        'price_history_complete': coverage['price_history_complete'],
        'contract_transition': coverage['contract_transition'],
        'contract_stable': coverage['contract_stable'],
        'no_new_trade': False,
        'no_priced_trade': True,
        'buy': 0, 'sell': 0, 'unknown': 0, 'volume': 0, 'prints': 0,
        'priced_prints': 0, 'unpriced_prints': 0,
    }
    for name in _LABEL_NULL_INTS:
        if name not in row:
            row[name] = None
    for name in SOURCE_FILTERS:
        row[f'{name}__buy'] = 0
        row[f'{name}__sell'] = 0
        row[f'{name}__unknown'] = 0
        row[f'{name}__volume'] = 0
        row[f'{name}__prints'] = 0
        row[f'{name}__excluded_prints'] = 0
        row[f'{name}__excluded_volume'] = 0
        row[f'{name}__open'] = None
        row[f'{name}__high'] = None
        row[f'{name}__low'] = None
        row[f'{name}__close'] = None
        row[f'{name}__high_at_ns'] = None
        row[f'{name}__low_at_ns'] = None
        row[f'{name}__high_source_order'] = None
        row[f'{name}__low_source_order'] = None
    if start is None or end is None:
        return row
    observed_end = end if end <= acquired_end else acquired_end
    if start >= acquired_end or start >= observed_end:
        row['right_censored'] = True
        if 'right_future_endpoint' not in (row['censor_reason'] or ''):
            extra = 'right_future_endpoint'
            row['censor_reason'] = extra if not row['censor_reason'] else f"{row['censor_reason']},{extra}"
        return row
    if trades is None:
        row['no_new_trade'] = data_complete
        row['no_priced_trade'] = data_complete
        row['signed_open'] = 0
        row['signed_high'] = 0
        row['signed_low'] = 0
        row['signed_close'] = 0
        for name in SOURCE_FILTERS:
            row[f'{name}__open'] = 0
            row[f'{name}__high'] = 0
            row[f'{name}__low'] = 0
            row[f'{name}__close'] = 0
        return row
    events = trades['event_ns']
    left = int(np.searchsorted(events, start, side='left'))
    right = int(np.searchsorted(events, observed_end, side='left'))
    buy = _range_sum(trades['buy_prefix'], left, right)
    sell = _range_sum(trades['sell_prefix'], left, right)
    unknown = _range_sum(trades['unknown_prefix'], left, right)
    volume = _add_checked(buy, sell, unknown, what='volume')
    prints = _range_sum(trades['print_prefix'], left, right)
    priced_prints = _range_sum(trades['priced_prefix'], left, right)
    row['buy'] = buy
    row['sell'] = sell
    row['unknown'] = unknown
    row['volume'] = volume
    row['prints'] = prints
    row['priced_prints'] = priced_prints
    row['unpriced_prints'] = prints - priced_prints
    row['no_new_trade'] = bool(data_complete and prints == 0)
    priced = _price_window(
        events, trades['source_order'], trades['source_row'], trades['price'],
        trades['price_valid'], trades['known_at_ns'], latency, left, right,
    )
    if prints == 0:
        row['no_priced_trade'] = data_complete
    else:
        row['no_priced_trade'] = priced.get('no_priced_trade', True)
    for key in (
        'first_priced_ticks', 'first_priced_event_ns', 'first_priced_known_at_ns',
        'first_priced_source_order', 'first_priced_source_row',
        'last_priced_ticks', 'last_priced_event_ns', 'last_priced_known_at_ns',
        'last_priced_source_order', 'last_priced_source_row',
        'observed_high_ticks', 'observed_low_ticks', 'observed_high_at_ns',
        'observed_low_at_ns', 'observed_high_source_order', 'observed_low_source_order',
    ):
        if key in priced:
            row[key] = priced[key]
    all_path = None
    for name in SOURCE_FILTERS:
        mask = trades['cohort_mask'][name]
        row[f'{name}__buy'] = _range_sum(trades['cohort_buy'][name], left, right)
        row[f'{name}__sell'] = _range_sum(trades['cohort_sell'][name], left, right)
        row[f'{name}__unknown'] = _range_sum(trades['cohort_unknown'][name], left, right)
        row[f'{name}__volume'] = _add_checked(
            row[f'{name}__buy'], row[f'{name}__sell'], row[f'{name}__unknown'], what=f'{name}__volume')
        row[f'{name}__prints'] = _range_sum(trades['cohort_prints'][name], left, right)
        row[f'{name}__excluded_prints'] = prints - row[f'{name}__prints']
        row[f'{name}__excluded_volume'] = volume - row[f'{name}__volume']
        path = _signed_path(events, trades['source_order'], trades['size'], trades['side'], mask, left, right)
        _apply_signed(row, path, prefix=f'{name}__')
        if name == 'all':
            all_path = path
    if all_path is not None:
        _apply_signed(row, all_path, prefix='signed_')
    return row


def _prepare_instrument_trades(bundle):
    import numpy as np

    size = bundle['size']
    side = bundle['side']
    valid = bundle['price_valid']
    prepared = dict(bundle)
    all_mask = np.ones(len(size), dtype=bool)
    prepared['all_mask'] = all_mask
    prepared['buy_prefix'] = _prefix_side(size, side, 1)
    prepared['sell_prefix'] = _prefix_side(size, side, -1)
    prepared['unknown_prefix'] = _prefix_side(size, side, 0)
    prepared['print_prefix'] = _prefix_count(all_mask)
    prepared['priced_prefix'] = _prefix_count(valid)
    prepared['cohort_mask'] = {}
    prepared['cohort_buy'] = {}
    prepared['cohort_sell'] = {}
    prepared['cohort_unknown'] = {}
    prepared['cohort_prints'] = {}
    for name in SOURCE_FILTERS:
        mask = all_mask if name == 'all' else _cohort_mask(size, name)
        prepared['cohort_mask'][name] = mask
        prepared['cohort_buy'][name] = _prefix_bool(np.where(side == 1, size, 0), mask)
        prepared['cohort_sell'][name] = _prefix_bool(np.where(side == -1, size, 0), mask)
        prepared['cohort_unknown'][name] = _prefix_bool(np.where(side == 0, size, 0), mask)
        prepared['cohort_prints'][name] = _prefix_count(mask)
    return prepared


def _contract_at_cut(arrays, idx, cut_ns):
    import numpy as np

    if idx is None or len(idx) == 0:
        return None
    starts = arrays['event_start'][idx]
    ends = arrays['event_end'][idx]
    pos = int(np.searchsorted(starts, cut_ns, side='left')) - 1
    if pos < 0:
        return None
    start = int(starts[pos])
    end = int(ends[pos])
    if not (start < cut_ns and end == cut_ns):
        return None
    return arrays['contract_key'][int(idx[pos])]


def join_window_eligibility(feature, label):
    """Pure identity/stage join; does not infer feature-stage from the label."""
    feature = _mapping(feature, what='feature')
    label = _mapping(label, what='label')
    stages = _frozen_stage_intervals()
    same_identity = all(feature.get(name) == label.get(name) for name in _IDENTITY_KEYS)
    same_instrument = feature.get('instrument_id') == label.get('instrument_id')
    same_cut = feature.get('cut_ns') == label.get('cut_ns')
    feature_contract = feature.get('contract_key')
    label_contract = label.get('contract_key')
    same_contract = (
        type(feature_contract) is str and feature_contract
        and feature_contract == label_contract
    )
    latency = _py_int(label.get('latency_ns'), what='label.latency_ns')
    cut_ns = _py_int(feature.get('cut_ns'), what='feature.cut_ns')
    formation_start = _py_int(feature.get('event_start_ns'), what='feature.event_start_ns')
    if latency is None or cut_ns is None or formation_start is None:
        raise IntegrityError('join clocks must be exact integers')
    feature_known_at = _add_checked(cut_ns, latency, what='feature_known_at_ns')
    label_maturity = label.get('known_at_ns')
    root = feature.get('root')
    feature_stage = _named_interval_stage(root, formation_start, feature_known_at, stages)
    label_stage = _stage_of(root, label_maturity, stages)
    same_named_stage = (
        feature_stage != 'unassigned'
        and label_maturity is not None
        and feature_stage == label_stage
    )
    eligible = bool(same_identity and same_instrument and same_cut and same_contract and same_named_stage)
    reason = None
    if not eligible:
        if not same_identity:
            reason = 'source_identity_mismatch'
        elif not same_instrument:
            reason = 'instrument_mismatch'
        elif not same_cut:
            reason = 'cut_mismatch'
        elif not same_contract:
            reason = 'absent_or_unknown_contract' if not feature_contract or not label_contract else 'contract_mismatch'
        elif feature_stage == 'unassigned':
            reason = 'feature_not_inside_named_stage'
        else:
            reason = 'label_maturity_not_same_named_stage'
    return {
        'eligible': eligible,
        'reason': reason,
        'stage': feature_stage if eligible else None,
        'same_source_identity': same_identity,
        'same_instrument': same_instrument,
        'same_raw_contract': same_contract,
        'same_cut': same_cut,
        'feature_interval_stage': feature_stage,
        'label_maturity_stage': label_stage,
        'feature_known_at_ns': feature_known_at,
        'label_maturity_ns': label_maturity,
    }


def build_window_tables(observations, trades, *, contract, source_identity, cut_start_ns, cut_end_ns, calendar):
    """Build causal formation-feature and matured forward-label tables.

    Features are one row per cut, instrument and formation. Labels are one
    row per cut, instrument, latency and horizon. Latency never rewrites
    original trade times. Family completion is not claimed.
    """
    if not isinstance(calendar, CashCalendar):
        raise ContractError('calendar must be the existing CashCalendar object')
    frozen, stages = _validate_contract(contract)
    identity = _validate_source_identity(source_identity)
    cut_start, cut_end, cuts = _validate_cuts(cut_start_ns, cut_end_ns, identity)
    obs = _observation_arrays(observations, identity, cut_start, cut_end)
    trade_state = _trade_arrays(trades, identity, cut_start, cut_end)
    feature_rows = []
    label_rows = []
    instruments = obs['instruments']
    disposition = None
    if not instruments:
        disposition = 'no_observed_instrument'
    prepared_trades = {
        instrument: _prepare_instrument_trades(bundle)
        for instrument, bundle in trade_state['by_instrument'].items()
    }
    remaining_cache = {}
    for cut in (int(v) for v in cuts):
        if cut not in remaining_cache:
            remaining_cache[cut] = _remaining_session(calendar, cut)
    if instruments:
        arrays = obs['arrays']
        for instrument in instruments:
            idx = obs['by_instrument'][instrument]
            trades_i = prepared_trades.get(instrument)
            for cut in (int(v) for v in cuts):
                contract_key = _contract_at_cut(arrays, idx, cut)
                for minutes in FORMATION_MINUTES:
                    feature_rows.append(
                        _feature_row(identity, instrument, minutes, cut, arrays, idx, stages))
                cash = remaining_cache[cut]
                for latency in LATENCY_NS:
                    for horizon in FORWARD_HORIZONS_MINUTES:
                        start = cut + latency
                        end = start + horizon * MINUTE
                        label_rows.append(_label_row(
                            identity, instrument, contract_key, cut, latency,
                            'fixed_minutes', horizon, start, end,
                            identity['acquired_event_end_ns'], cash, trades_i, stages,
                            arrays, idx,
                        ))
                    if cash['applicable']:
                        start = cut + latency
                        end = cash['close_at']
                        if end <= start:
                            label_rows.append(_label_row(
                                identity, instrument, contract_key, cut, latency,
                                'remaining_session', None, None, None,
                                identity['acquired_event_end_ns'],
                                {**cash, 'applicable': False, 'disposition': 'not_applicable_empty_remaining'},
                                trades_i, stages, arrays, idx,
                            ))
                        else:
                            label_rows.append(_label_row(
                                identity, instrument, contract_key, cut, latency,
                                'remaining_session', None, start, end,
                                identity['acquired_event_end_ns'], cash, trades_i, stages,
                                arrays, idx,
                            ))
                    else:
                        label_rows.append(_label_row(
                            identity, instrument, contract_key, cut, latency,
                            'remaining_session', None, None, None,
                            identity['acquired_event_end_ns'], cash, trades_i, stages,
                            arrays, idx,
                        ))
    features = _table_from_rows(feature_schema(), feature_rows)
    labels = _table_from_rows(label_schema(), label_rows)
    validation = {
        'version': VERSION,
        'kind': CONTRACT_KIND,
        'family_complete': False,
        'source_identity': identity,
        'cut_start_ns': cut_start,
        'cut_end_ns': cut_end,
        'cut_count': int(len(cuts)),
        'instrument_ids': list(instruments),
        'instrument_count': len(instruments),
        'source_unit_disposition': disposition,
        'feature_rows': len(feature_rows),
        'label_rows': len(label_rows),
        'trade_rows': trade_state.get('n', 0),
        'stored_known_at_delay_ns': list(trade_state.get('delays', ())),
        'stored_known_at_matches_source_250ms': trade_state.get('delay_ok', True),
        'original_trade_times_unchanged': True,
        'calendar_zone': calendar.zone,
        'calendar_version': calendar.version,
        'contract_kind': frozen.get('kind'),
        'bounds': {
            'max_instruments': MAX_INSTRUMENTS,
            'max_cut_span_ns': MAX_CUT_SPAN_NS,
            'max_source_buffer_ns': MAX_SOURCE_BUFFER_NS,
        },
    }
    return {
        'features': features,
        'labels': labels,
        'validation': validation,
        'definitions': contract_definitions(frozen),
        'feature_schema': feature_schema(),
        'label_schema': label_schema(),
        'version': VERSION,
        'family_complete': False,
    }
