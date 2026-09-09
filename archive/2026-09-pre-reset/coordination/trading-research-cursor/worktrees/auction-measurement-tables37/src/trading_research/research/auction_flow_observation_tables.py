"""Reusable one-source/day auction and flow observation tables.

Rows are a bounded view of already-published receipt and measurement
identities. This module does not scan raw files, infer BBO recovery, pick a
POC winner, or claim family-level empirical completion.
"""
from __future__ import annotations

from fractions import Fraction
import time

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_measurements import SOURCE_FILTERS
from trading_research.research.auction_flow_production import (
    WINDOW_RECEIPT_KIND,
    source_variant,
    window_artifact_prefix,
)
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries


VERSION = 'auction-flow-observation-tables-v1'
BATCH_ROWS = 65536
_SHA_LEN = 64
_INT64_MIN = -(2**63)
_INT64_MAX = 2**63 - 1
_WEIGHTED_QUANTILES = (
    ('1/20', 'weighted_price_quantile05'),
    ('1/4', 'weighted_price_quantile25'),
    ('1/2', 'weighted_price_quantile50'),
    ('3/4', 'weighted_price_quantile75'),
    ('19/20', 'weighted_price_quantile95'),
)
_SIZE_QUANTILES = (
    ('1/4', 'print_size_quantile25'),
    ('1/2', 'print_size_quantile50'),
    ('3/4', 'print_size_quantile75'),
    ('19/20', 'print_size_quantile95'),
)
_SOURCE_QUALITY_COUNTS = (
    'raw_rows', 'non_snapshot_rows', 'gap_rows', 'snapshot_rows',
    'unknown_action_rows', 'invalid_trade_size_rows',
)
_COHORT_INTS = (
    'buy', 'sell', 'unknown', 'volume', 'prints', 'excluded_prints', 'excluded_volume',
    'open', 'high', 'low', 'close', 'observed_signed_lower', 'observed_signed_upper',
)
_COHORT_NULL_INTS = (
    'high_at_ns', 'low_at_ns', 'high_source_order', 'low_source_order',
    'true_signed_lower', 'true_signed_upper',
)
_PRICED_TRADE_FIELDS = (
    ('price_ticks', 'ticks'),
    ('event_ns', 'event_ns'),
    ('known_at_ns', 'known_at_ns'),
    ('source_order', 'source_order'),
    ('source_row', 'source_row'),
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


def _int_or_none(value, *, what):
    if value is None:
        return None
    return _int(value, what=what)


def _text(value, *, what, allow_empty=False):
    if type(value) is not str or (not value and not allow_empty):
        raise IntegrityError(f'{what} must be a concrete string')
    return value


def _mapping(value, *, what):
    if not isinstance(value, dict):
        raise IntegrityError(f'{what} must be an object')
    return value


def _as_fraction(value, *, what):
    if value is None:
        return None
    if type(value) is Fraction:
        return value
    if type(value) is bool:
        raise IntegrityError(f'{what} cannot use a boolean as an exact quantity')
    if type(value) is int:
        return Fraction(value)
    if isinstance(value, dict) and set(value) == {'$fraction'}:
        pair = value['$fraction']
        if (not isinstance(pair, (list, tuple)) or len(pair) != 2
                or type(pair[0]) is bool or type(pair[1]) is bool
                or type(pair[0]) is not int or type(pair[1]) is not int or pair[1] == 0):
            raise IntegrityError(f'{what} canonical fraction tag is invalid')
        return Fraction(pair[0], pair[1])
    raise IntegrityError(f'{what} must be an exact Fraction, integer, or {{$fraction:[n,d]}}')


def _float64_or_none(value, *, what):
    if value is None:
        return None
    if type(value) is float:
        return value
    return float(_as_fraction(value, what=what))


def _quantile_map(values, spec, *, what):
    if values is None:
        return {column: None for _, column in spec}
    if not isinstance(values, dict):
        raise IntegrityError(f'{what} must be an exact quantile object')
    out = {}
    for key, column in spec:
        item = values[key] if key in values else values.get(str(Fraction(key)))
        out[column] = _float64_or_none(item, what=f'{what}.{key}')
    return out


def _triple(value, *, what):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise IntegrityError(f'{what} must be an exact buy/sell/unknown triple')
    return tuple(_int(item, what=f'{what}[{index}]') for index, item in enumerate(value))


def _archive_contains(intervals, start, end):
    if not isinstance(intervals, (list, tuple)):
        raise IntegrityError('source_archive_intervals must be an explicit interval list')
    for item in intervals:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise IntegrityError('source archive interval must be an exact [start, end) pair')
        a, b = _int(item[0], what='source_archive_interval_start'), _int(item[1], what='source_archive_interval_end')
        if a <= start and end <= b:
            return True
    return False


def _atomic_bounds(start, end, width, number):
    a = start + number * width
    return a, min(a + width, end)


def _priced_trade(record, *, prefix):
    out = {f'{prefix}_{dest}': None for _, dest in _PRICED_TRADE_FIELDS}
    if record is None:
        return out
    rec = _mapping(record, what=prefix)
    for src, dest in _PRICED_TRADE_FIELDS:
        out[f'{prefix}_{dest}'] = _int_or_none(rec.get(src), what=f'{prefix}.{src}')
    return out


def _stream_sha256(stream, *, what):
    rec = _mapping(stream, what=what)
    return _sha256_text(rec.get('sha256'), what=f'{what}.sha256')


def _measurement_sha256(receipt):
    artifacts = _mapping(receipt.get('artifacts'), what='receipt.artifacts')
    measurement = _mapping(artifacts.get('measurement'), what='receipt.artifacts.measurement')
    raw = measurement.get('uncompressed_sha256', measurement.get('sha256'))
    return _sha256_text(raw, what='measurement_sha256')


def _canonical_raw_values_sha256(receipt, measured):
    manifest = _mapping(measured.get('source_manifest'), what='source_manifest')
    identity = receipt.get('source_manifest_identity')
    stream = manifest.get('canonical_selected_raw_stream')
    if stream is None and isinstance(identity, dict):
        stream = identity.get('canonical_selected_raw_stream')
    if stream is None:
        raise IntegrityError('canonical selected raw-value identity is required')
    sha = _stream_sha256(stream, what='canonical_selected_raw_stream')
    if isinstance(identity, dict) and identity.get('canonical_selected_raw_stream') is not None:
        other = _stream_sha256(identity['canonical_selected_raw_stream'],
                               what='receipt.source_manifest_identity.canonical_selected_raw_stream')
        if other != sha:
            raise IntegrityError('receipt and measurement canonical raw-value identities disagree')
    return sha


def _profile_summary(profile, *, coverage_complete):
    rec = _mapping(profile, what='sparse_profile')
    unpriced = _triple(rec.get('unpriced_buy_sell_unknown'), what='unpriced_buy_sell_unknown')
    rows = rec.get('rows')
    if not isinstance(rows, (list, tuple)):
        raise IntegrityError('sparse_profile.rows must be the published ordered cells')
    priced = [0, 0, 0]
    masses = []
    for index, row in enumerate(rows):
        if not isinstance(row, (list, tuple)) or len(row) != 4:
            raise IntegrityError('sparse profile cell must be [row, buy, sell, unknown]')
        price = _int(row[0], what=f'sparse_profile.rows[{index}].row')
        sides = [_int(row[j], what=f'sparse_profile.rows[{index}].side') for j in (1, 2, 3)]
        for j in range(3):
            priced[j] += sides[j]
        masses.append((price, sides[0] + sides[1] + sides[2]))
    priced_buy, priced_sell, priced_unknown = priced
    priced_volume = priced_buy + priced_sell + priced_unknown
    total = rec.get('total_volume')
    if total is not None and _int(total, what='sparse_profile.total_volume') != priced_volume + sum(unpriced):
        raise IntegrityError('sparse profile priced, unpriced and total mass do not reconcile')
    maximizers = []
    max_mass = 0
    if masses:
        max_mass = max(mass for _, mass in masses)
        if max_mass:
            maximizers = [price for price, mass in masses if mass == max_mass]
    if maximizers:
        poc_count, poc_first, poc_last = len(maximizers), maximizers[0], maximizers[-1]
    else:
        poc_count, poc_first, poc_last = 0, None, None
    _ = coverage_complete
    max_frac = Fraction(max_mass, priced_volume) if priced_volume else None
    side_conc = (Fraction(priced_buy ** 2 + priced_sell ** 2 + priced_unknown ** 2, priced_volume ** 2)
                 if priced_volume else None)
    signed_conc = Fraction(priced_buy - priced_sell, priced_volume) if priced_volume else None
    return {
        'priced_buy': priced_buy, 'priced_sell': priced_sell, 'priced_unknown': priced_unknown,
        'unpriced_buy': unpriced[0], 'unpriced_sell': unpriced[1], 'unpriced_unknown': unpriced[2],
        'occupied_price_rows': len(rows),
        'poc_maximizer_count': poc_count, 'poc_first_row': poc_first, 'poc_last_row': poc_last,
        'max_mass_fraction': None if max_frac is None else float(max_frac),
        'side_concentration': None if side_conc is None else float(side_conc),
        'signed_concentration': None if signed_conc is None else float(signed_conc),
    }


def _check_flow(flow, *, name, all_flow=None):
    rec = _mapping(flow, what=f'flows.{name}')
    if rec.get('filter') not in (None, name):
        raise IntegrityError(f'flow filter {name} changed its identity')
    values = {field: _int(rec.get(field), what=f'flows.{name}.{field}') for field in _COHORT_INTS}
    nulls = {field: _int_or_none(rec.get(field), what=f'flows.{name}.{field}') for field in _COHORT_NULL_INTS}
    coverage = _bool(rec.get('coverage_complete'), what=f'flows.{name}.coverage_complete')
    if values['volume'] != values['buy'] + values['sell'] + values['unknown']:
        raise IntegrityError(f'{name} volume is not buy+sell+unknown')
    if values['close'] != values['open'] + values['buy'] - values['sell']:
        raise IntegrityError(f'{name} close is not open+buy-sell')
    if values['high'] < max(values['open'], values['close']) or values['low'] > min(values['open'], values['close']):
        raise IntegrityError(f'{name} true OHLC extrema are inconsistent with the open/close path')
    if values['observed_signed_lower'] != values['close'] - values['unknown']:
        raise IntegrityError(f'{name} observed signed lower bound is not close-unknown')
    if values['observed_signed_upper'] != values['close'] + values['unknown']:
        raise IntegrityError(f'{name} observed signed upper bound is not close+unknown')
    if coverage:
        if nulls['true_signed_lower'] != values['observed_signed_lower'] or nulls['true_signed_upper'] != values['observed_signed_upper']:
            raise IntegrityError(f'{name} complete true signed bounds must equal the observed bounds')
    elif nulls['true_signed_lower'] is not None or nulls['true_signed_upper'] is not None:
        raise IntegrityError(f'{name} incomplete coverage cannot publish true signed bounds')
    if name == 'all' and (values['excluded_prints'] or values['excluded_volume']):
        raise IntegrityError('all-cohort excluded mass must be zero')
    if all_flow is not None:
        if values['prints'] + values['excluded_prints'] != all_flow['prints']:
            raise IntegrityError(f'{name} selected+excluded print count does not equal all')
        if values['volume'] + values['excluded_volume'] != all_flow['volume']:
            raise IntegrityError(f'{name} selected+excluded volume does not equal all')
    return {**values, **nulls, 'coverage_complete': coverage}


def _clock_uncertain_count(quality, quote):
    if 'clock_uncertain_intervals' in quality:
        return _int(quality['clock_uncertain_intervals'], what='source_quality.clock_uncertain_intervals', minimum=0)
    intervals = quote.get('source_clock_uncertain_intervals')
    if intervals is None:
        return 0
    if not isinstance(intervals, (list, tuple)):
        raise IntegrityError('quote source_clock_uncertain_intervals must be an interval list')
    return _int(len(intervals), what='quote.source_clock_uncertain_intervals', minimum=0)


def _quote_row(quote, *, source_coverage_complete, coordinate_complete):
    rec = _mapping(quote, what='quote')
    quote_complete = _bool(rec.get('coverage_complete'), what='quote.coverage_complete')
    standing = _bool(rec.get('full_standing_window_eligible'), what='full_standing_window_eligible')
    pressure = _bool(rec.get('full_pressure_transition_window_eligible'), what='full_pressure_transition_window_eligible')
    if standing and not (quote_complete and source_coverage_complete and coordinate_complete):
        raise IntegrityError('full standing eligibility cannot be inferred from a partial quote window')
    if pressure and not standing:
        raise IntegrityError('full pressure eligibility cannot be inferred from incomplete standing')
    path = rec.get('ofi_path')
    path = {} if path is None else _mapping(path, what='ofi_path')
    return {
        'quote_coverage_complete': quote_complete,
        'full_standing_window_eligible': standing,
        'full_pressure_transition_window_eligible': pressure,
        'quote_or_invalidation_rows': _int(rec.get('quote_or_invalidation_rows'), what='quote_or_invalidation_rows', minimum=0),
        'fresh_quote_updates': _int(rec.get('fresh_quote_updates'), what='fresh_quote_updates', minimum=0),
        'pressure_transitions': _int(rec.get('pressure_transitions'), what='pressure_transitions', minimum=0),
        'ofi_contracts': _int(rec.get('ofi_contracts'), what='ofi_contracts'),
        'price_change_ofi': _int(rec.get('price_change_ofi'), what='price_change_ofi'),
        'same_price_size_ofi': _int(rec.get('same_price_size_ofi'), what='same_price_size_ofi'),
        'ofi_open': _int_or_none(path.get('open'), what='ofi_path.open'),
        'ofi_high': _int_or_none(path.get('high'), what='ofi_path.high'),
        'ofi_low': _int_or_none(path.get('low'), what='ofi_path.low'),
        'ofi_close': _int_or_none(path.get('close'), what='ofi_path.close'),
        'ofi_high_at_ns': _int_or_none(path.get('high_at_ns'), what='ofi_path.high_at_ns'),
        'ofi_low_at_ns': _int_or_none(path.get('low_at_ns'), what='ofi_path.low_at_ns'),
        'ofi_high_source_order': _int_or_none(path.get('high_source_order'), what='ofi_path.high_source_order'),
        'ofi_low_source_order': _int_or_none(path.get('low_source_order'), what='ofi_path.low_source_order'),
        'invalid_book_rows': _int(rec.get('invalid_book_rows'), what='invalid_book_rows', minimum=0),
        'quote_gap_rows': _int(rec.get('gap_rows'), what='quote.gap_rows', minimum=0),
        'quote_snapshot_rows': _int(rec.get('snapshot_rows'), what='quote.snapshot_rows', minimum=0),
        'clear_rows': _int(rec.get('clear_rows'), what='clear_rows', minimum=0),
        'standing_duration_ns': _int(rec.get('observed_trusted_standing_duration_ns'),
                                     what='observed_trusted_standing_duration_ns', minimum=0),
        'duration_mean_spread_ticks': _float64_or_none(rec.get('duration_mean_spread_ticks'),
                                                       what='duration_mean_spread_ticks'),
        'duration_mean_imbalance': _float64_or_none(rec.get('duration_mean_imbalance'),
                                                    what='duration_mean_imbalance'),
        'update_mean_spread_ticks': _float64_or_none(rec.get('update_mean_spread_ticks'),
                                                     what='update_mean_spread_ticks'),
        'update_mean_imbalance': _float64_or_none(rec.get('update_mean_imbalance'),
                                                  what='update_mean_imbalance'),
        'update_mean_microprice_residual': _float64_or_none(
            rec.get('update_mean_microprice_minus_midpoint_ticks'),
            what='update_mean_microprice_minus_midpoint_ticks'),
        'sum_depth_normalized_ofi': _float64_or_none(rec.get('sum_depth_normalized_ofi'),
                                                     what='sum_depth_normalized_ofi'),
    }


def _cohort_columns(name, flow):
    return {
        f'{name}__buy': flow['buy'], f'{name}__sell': flow['sell'], f'{name}__unknown': flow['unknown'],
        f'{name}__volume': flow['volume'], f'{name}__prints': flow['prints'],
        f'{name}__excluded_prints': flow['excluded_prints'], f'{name}__excluded_volume': flow['excluded_volume'],
        f'{name}__open': flow['open'], f'{name}__high': flow['high'], f'{name}__low': flow['low'],
        f'{name}__close': flow['close'],
        f'{name}__high_at_ns': flow['high_at_ns'], f'{name}__low_at_ns': flow['low_at_ns'],
        f'{name}__high_source_order': flow['high_source_order'],
        f'{name}__low_source_order': flow['low_source_order'],
        f'{name}__coverage_complete': flow['coverage_complete'],
        f'{name}__observed_signed_lower': flow['observed_signed_lower'],
        f'{name}__observed_signed_upper': flow['observed_signed_upper'],
        f'{name}__true_signed_lower': flow['true_signed_lower'],
        f'{name}__true_signed_upper': flow['true_signed_upper'],
    }


def _empty_totals():
    return {
        'prints': 0, 'volume': 0, 'quote_rows': 0,
        'buy': 0, 'sell': 0, 'unknown': 0,
        'delta': 0,
        **{f'{name}__prints': 0 for name in SOURCE_FILTERS},
        **{f'{name}__volume': 0 for name in SOURCE_FILTERS},
        **{f'{name}__delta': 0 for name in SOURCE_FILTERS},
        **{f'{name}__buy': 0 for name in SOURCE_FILTERS},
        **{f'{name}__sell': 0 for name in SOURCE_FILTERS},
        **{f'{name}__unknown': 0 for name in SOURCE_FILTERS},
    }


def _add_flow_totals(totals, flows, *, prefix=''):
    for name, flow in flows.items():
        totals[f'{prefix}{name}__prints'] += flow['prints']
        totals[f'{prefix}{name}__volume'] += flow['volume']
        totals[f'{prefix}{name}__buy'] += flow['buy']
        totals[f'{prefix}{name}__sell'] += flow['sell']
        totals[f'{prefix}{name}__unknown'] += flow['unknown']
        totals[f'{prefix}{name}__delta'] += flow['close'] - flow['open']


def observation_column_names():
    """Stable published column order for one atomic observation row."""
    return tuple(field.name for field in observation_schema())


def observation_schema():
    """Explicit Arrow schema: nullable clocks stay null; counts and clocks are int64."""
    import pyarrow as pa

    def i64(name, nullable=False):
        return pa.field(name, pa.int64(), nullable=nullable)

    def f64(name):
        return pa.field(name, pa.float64(), nullable=True)

    def flag(name):
        return pa.field(name, pa.bool_(), nullable=False)

    def text(name, nullable=False):
        return pa.field(name, pa.string(), nullable=nullable)

    fields = [
        text('root'), text('source_path'), text('source_metadata_sha256'), text('source_variant'),
        i64('source_window_start_ns'), i64('source_window_end_ns'),
        text('receipt_sha256'), text('measurement_sha256'), text('canonical_raw_values_sha256'),
        i64('instrument_id'), text('contract_key', nullable=True),
        i64('event_start_ns'), i64('event_end_ns'), i64('known_at_ns'), i64('atomic_bin'),
        flag('coordinate_complete'), flag('supplied_raw_coordinate_stable'),
        flag('source_instrument_presence'), flag('source_coverage_complete'),
        flag('flow_history_complete'), flag('price_history_complete'),
        flag('empty_observed_window'), flag('quote_coverage_complete'),
        flag('full_standing_window_eligible'), flag('full_pressure_transition_window_eligible'),
        flag('archive_window_complete'),
        i64('raw_rows'), i64('non_snapshot_rows'), i64('gap_rows'), i64('snapshot_rows'),
        i64('unknown_action_rows'), i64('invalid_trade_size_rows'), i64('clock_uncertain_intervals'),
        i64('prints'), i64('unpriced_prints'),
        i64('first_priced_ticks', nullable=True), i64('first_priced_event_ns', nullable=True),
        i64('first_priced_known_at_ns', nullable=True), i64('first_priced_source_order', nullable=True),
        i64('first_priced_source_row', nullable=True),
        i64('last_priced_ticks', nullable=True), i64('last_priced_event_ns', nullable=True),
        i64('last_priced_known_at_ns', nullable=True), i64('last_priced_source_order', nullable=True),
        i64('last_priced_source_row', nullable=True),
        i64('observed_high_ticks', nullable=True), i64('observed_low_ticks', nullable=True),
        i64('observed_high_at_ns', nullable=True), i64('observed_low_at_ns', nullable=True),
        i64('observed_high_source_order', nullable=True), i64('observed_low_source_order', nullable=True),
        i64('observed_price_variation_ticks'), i64('observed_up_variation_ticks'),
        i64('observed_down_variation_ticks'), i64('observed_squared_price_variation_ticks_squared'),
        i64('observed_adjacent_priced_pairs'), i64('observed_maximum_same_side_run'),
        i64('same_time_adjacent_prints'), flag('terminal_run_right_censored'),
    ]
    for name in SOURCE_FILTERS:
        fields.extend([
            i64(f'{name}__buy'), i64(f'{name}__sell'), i64(f'{name}__unknown'),
            i64(f'{name}__volume'), i64(f'{name}__prints'),
            i64(f'{name}__excluded_prints'), i64(f'{name}__excluded_volume'),
            i64(f'{name}__open'), i64(f'{name}__high'), i64(f'{name}__low'), i64(f'{name}__close'),
            i64(f'{name}__high_at_ns', nullable=True), i64(f'{name}__low_at_ns', nullable=True),
            i64(f'{name}__high_source_order', nullable=True),
            i64(f'{name}__low_source_order', nullable=True),
            flag(f'{name}__coverage_complete'),
            i64(f'{name}__observed_signed_lower'), i64(f'{name}__observed_signed_upper'),
            i64(f'{name}__true_signed_lower', nullable=True),
            i64(f'{name}__true_signed_upper', nullable=True),
        ])
    fields.extend([
        i64('priced_volume'), i64('sum_price_volume'), i64('sum_price_squared_volume'),
        f64('vwap_ticks'), f64('variance_ticks_squared'),
        f64('weighted_price_quantile05'), f64('weighted_price_quantile25'),
        f64('weighted_price_quantile50'), f64('weighted_price_quantile75'),
        f64('weighted_price_quantile95'),
        f64('print_size_quantile25'), f64('print_size_quantile50'),
        f64('print_size_quantile75'), f64('print_size_quantile95'),
        f64('count_intensity_per_second'), f64('volume_intensity_per_second'),
        i64('priced_buy'), i64('priced_sell'), i64('priced_unknown'),
        i64('unpriced_buy'), i64('unpriced_sell'), i64('unpriced_unknown'),
        i64('occupied_price_rows'),
        i64('poc_maximizer_count', nullable=True), i64('poc_first_row', nullable=True),
        i64('poc_last_row', nullable=True),
        f64('max_mass_fraction'), f64('side_concentration'), f64('signed_concentration'),
        i64('quote_or_invalidation_rows'), i64('fresh_quote_updates'), i64('pressure_transitions'),
        i64('ofi_contracts'), i64('price_change_ofi'), i64('same_price_size_ofi'),
        i64('ofi_open', nullable=True), i64('ofi_high', nullable=True),
        i64('ofi_low', nullable=True), i64('ofi_close', nullable=True),
        i64('ofi_high_at_ns', nullable=True), i64('ofi_low_at_ns', nullable=True),
        i64('ofi_high_source_order', nullable=True), i64('ofi_low_source_order', nullable=True),
        i64('invalid_book_rows'), i64('quote_gap_rows'), i64('quote_snapshot_rows'), i64('clear_rows'),
        i64('standing_duration_ns'),
        f64('duration_mean_spread_ticks'), f64('duration_mean_imbalance'),
        f64('update_mean_spread_ticks'), f64('update_mean_imbalance'),
        f64('update_mean_microprice_residual'), f64('sum_depth_normalized_ofi'),
    ])
    return pa.schema(fields)


def observation_table(rows):
    """Materialize one explicit-schema table; batch slices of the same rows match."""
    import pyarrow as pa

    schema = observation_schema()
    if type(rows) is not list:
        raise ContractError('observation rows must be an ordered list')
    if any(not isinstance(row, dict) for row in rows):
        raise ContractError('each observation row must be a complete mapping')
    names = [field.name for field in schema]
    if any(set(row) != set(names) for row in rows):
        raise IntegrityError('observation row columns must match the explicit schema exactly')
    if not rows:
        return pa.table({name: pa.array([], type=schema.field(name).type) for name in names}, schema=schema)
    return pa.table({name: pa.array([row[name] for row in rows], type=schema.field(name).type) for name in names},
                    schema=schema)


def _validate_unit(receipt, measured, receipt_reference):
    rec = _mapping(receipt, what='receipt')
    payload = _mapping(measured, what='measured')
    reference = _mapping(receipt_reference, what='receipt_reference')
    if rec.get('kind') != WINDOW_RECEIPT_KIND or rec.get('success') is not True:
        raise IntegrityError('observation tables require a successful source-window receipt')
    if rec.get('status') != 'measured' or payload.get('status') != 'measured':
        raise IntegrityError('observation tables require a measured source/day status')
    unit = _mapping(rec.get('unit'), what='receipt.unit')
    identity = rec.get('unit_identity')
    identity = unit if not isinstance(identity, dict) else identity
    parameters = _mapping(rec.get('parameters'), what='receipt.parameters')
    root = _text(payload.get('root'), what='measured.root')
    start = _int(payload.get('event_start_ns'), what='measured.event_start_ns', minimum=0)
    end = _int(payload.get('event_end_ns'), what='measured.event_end_ns', minimum=1)
    known = _int(payload.get('known_at_ns'), what='measured.known_at_ns', minimum=1)
    width = _int(payload.get('atomic_width_ns'), what='measured.atomic_width_ns', minimum=1)
    if not start < end:
        raise IntegrityError('measured source window must be a half-open [start, end)')
    if (unit.get('root') != root or identity.get('root') != root
            or unit.get('event_start_ns') != start or identity.get('event_start_ns') != start
            or unit.get('event_end_ns') != end or identity.get('event_end_ns') != end):
        raise IntegrityError('receipt and measurement root/start/end identity do not join')
    source_path = _text(unit.get('source_path'), what='source_path')
    if identity.get('source_path') not in (None, source_path):
        raise IntegrityError('receipt unit source_path does not join its identity')
    source_sha = _sha256_text(unit.get('source_metadata_sha256'), what='source_metadata_sha256')
    if rec.get('source_metadata_sha256') not in (None, source_sha):
        raise IntegrityError('receipt source_metadata_sha256 does not join the unit')
    if identity.get('source_metadata_sha256') not in (None, source_sha):
        raise IntegrityError('receipt identity source_metadata_sha256 does not join the unit')
    variant = source_variant(source_path)
    if identity.get('source_variant') not in (None, variant):
        raise IntegrityError('source_variant is not the existing path digest prefix')
    latency = _int(parameters.get('latency_ns'), what='receipt.parameters.latency_ns', minimum=0, maximum=1_000_000_000)
    if known - end != latency:
        raise IntegrityError('receipt latency_ns is not measured end->known')
    if parameters.get('atomic_width_ns') not in (None, width):
        raise IntegrityError('receipt and measurement atomic_width_ns do not join')
    if rec.get('coordinate_version') not in (None, payload.get('coordinate_manifest_version')):
        raise IntegrityError('receipt and measurement coordinate versions do not join')
    if rec.get('coordinate_snapshot_version') not in (None, payload.get('coordinate_snapshot_supplement_version')):
        raise IntegrityError('receipt and measurement coordinate snapshot versions do not join')
    receipt_sha = _sha256_text(reference.get('sha256'), what='receipt_reference.sha256')
    return {
        'root': root, 'source_path': source_path, 'source_metadata_sha256': source_sha,
        'source_variant': variant, 'start': start, 'end': end, 'known': known, 'width': width,
        'latency': latency, 'receipt_sha256': receipt_sha,
        'measurement_sha256': _measurement_sha256(rec),
        'canonical_raw_values_sha256': _canonical_raw_values_sha256(rec, payload),
        'counts': _mapping(rec.get('counts'), what='receipt.counts'),
        'archive_intervals': payload.get('source_archive_intervals'),
        'instruments': payload.get('instruments'),
    }


def observation_rows(receipt, measured, *, receipt_reference):
    """Flatten one successful source/day measurement into atomic observation rows."""
    unit = _validate_unit(receipt, measured, receipt_reference)
    instruments = unit['instruments']
    if not isinstance(instruments, list) or not instruments:
        raise IntegrityError('measured source/day must retain its instrument list')
    expected_atoms = (unit['end'] - unit['start'] + unit['width'] - 1) // unit['width']
    if expected_atoms < 1 or expected_atoms > 100000:
        raise ContractError('declared atomic grid is outside the bounded source/day domain')
    column_names = {field.name for field in observation_schema()}
    seen_instruments = set()
    seen_atoms = set()
    rows = []
    atomic_totals = _empty_totals()
    whole_totals = _empty_totals()
    receipt_trades = _int(unit['counts'].get('trades'), what='receipt.counts.trades', minimum=0)
    receipt_volume = _int(unit['counts'].get('volume'), what='receipt.counts.volume', minimum=0)
    receipt_quotes = _int(unit['counts'].get('quote_rows'), what='receipt.counts.quote_rows', minimum=0)
    for instrument in instruments:
        inst = _mapping(instrument, what='instrument')
        instrument_id = _int(inst.get('instrument_id'), what='instrument_id', minimum=1)
        if instrument_id in seen_instruments:
            raise IntegrityError('measured instruments are not unique')
        seen_instruments.add(instrument_id)
        atoms = inst.get('atomic_windows')
        if not isinstance(atoms, list) or len(atoms) != expected_atoms:
            raise IntegrityError('atom count does not match the declared [start, end) grid')
        whole = _mapping(inst.get('whole_window'), what='whole_window')
        if (_int(whole.get('instrument_id'), what='whole_window.instrument_id', minimum=1) != instrument_id
                or _int(whole.get('event_start_ns'), what='whole_window.event_start_ns') != unit['start']
                or _int(whole.get('event_end_ns'), what='whole_window.event_end_ns') != unit['end']
                or _int(whole.get('known_at_ns'), what='whole_window.known_at_ns') != unit['known']):
            raise IntegrityError('whole-window instrument or clock does not join the source/day')
        whole_flows = _mapping(whole.get('flows'), what='whole_window.flows')
        if set(whole_flows) != set(SOURCE_FILTERS):
            raise IntegrityError('whole-window flows lost an exact source cohort')
        checked_whole = {}
        checked_whole['all'] = _check_flow(whole_flows['all'], name='all')
        for name in SOURCE_FILTERS:
            if name == 'all':
                continue
            checked_whole[name] = _check_flow(whole_flows[name], name=name, all_flow=checked_whole['all'])
        _add_flow_totals(whole_totals, checked_whole)
        whole_totals['prints'] += _int(whole.get('prints'), what='whole_window.prints', minimum=0)
        whole_totals['volume'] += checked_whole['all']['volume']
        instrument_atomic = _empty_totals()
        prior_bin = -1
        for atom in atoms:
            item = _mapping(atom, what='atomic_window')
            number = _int(item.get('bin'), what='atomic_bin', minimum=0)
            if number != prior_bin + 1:
                raise IntegrityError('atomic coordinates are not unique and ordered')
            prior_bin = number
            start, end = _atomic_bounds(unit['start'], unit['end'], unit['width'], number)
            known = end + unit['latency']
            if (_int(item.get('instrument_id'), what='atomic.instrument_id', minimum=1) != instrument_id
                    or _int(item.get('event_start_ns'), what='atomic.event_start_ns') != start
                    or _int(item.get('event_end_ns'), what='atomic.event_end_ns') != end
                    or _int(item.get('known_at_ns'), what='atomic.known_at_ns') != known):
                raise IntegrityError('original atom source/instrument id or known-at does not join the grid')
            key = (instrument_id, start, end)
            if key in seen_atoms:
                raise IntegrityError('atomic coordinates are not unique')
            seen_atoms.add(key)
            trade = _mapping(item.get('trade'), what='atomic.trade')
            if (_int(trade.get('instrument_id'), what='trade.instrument_id', minimum=1) != instrument_id
                    or _int(trade.get('event_start_ns'), what='trade.event_start_ns') != start
                    or _int(trade.get('event_end_ns'), what='trade.event_end_ns') != end
                    or _int(trade.get('known_at_ns'), what='trade.known_at_ns') != known):
                raise IntegrityError('trade window clocks do not join the atomic coordinate')
            coordinate = _mapping(item.get('coordinate'), what='atomic.coordinate')
            coordinate_complete = _bool(coordinate.get('complete'), what='coordinate.complete')
            if trade.get('coordinate_complete') not in (None, coordinate_complete):
                raise IntegrityError('trade and atomic coordinate completeness disagree')
            source_complete = _bool(trade.get('source_coverage_complete'), what='source_coverage_complete')
            flow_complete = _bool(trade.get('flow_history_complete'), what='flow_history_complete')
            price_complete = _bool(trade.get('price_history_complete'), what='price_history_complete')
            empty = _bool(trade.get('empty_observed_window'), what='empty_observed_window')
            if flow_complete is not source_complete:
                raise IntegrityError('flow-history completeness is not the published source-coverage flag')
            prints = _int(trade.get('prints'), what='prints', minimum=0)
            unpriced = _int(trade.get('unpriced_prints'), what='unpriced_prints', minimum=0)
            if unpriced > prints:
                raise IntegrityError('unpriced prints cannot exceed tape prints')
            if empty is not (source_complete and prints == 0):
                raise IntegrityError('empty observed window is not complete coverage with zero prints')
            if price_complete and (not (source_complete and coordinate_complete) or unpriced):
                raise IntegrityError('price history cannot be complete with incomplete coverage or unpriced prints')
            flows = _mapping(trade.get('flows'), what='trade.flows')
            if set(flows) != set(SOURCE_FILTERS):
                raise IntegrityError('atomic flows lost an exact source cohort')
            checked = {'all': _check_flow(flows['all'], name='all')}
            for name in SOURCE_FILTERS:
                if name == 'all':
                    continue
                checked[name] = _check_flow(flows[name], name=name, all_flow=checked['all'])
            if checked['all']['prints'] != prints:
                raise IntegrityError('all-cohort prints do not equal the tape print count')
            weighted = _mapping(trade.get('weighted_price'), what='weighted_price')
            priced_volume = _int(weighted.get('priced_volume'), what='priced_volume', minimum=0)
            sum_pv = _int(weighted.get('sum_price_volume'), what='sum_price_volume')
            sum_p2v = _int(weighted.get('sum_price_squared_volume'), what='sum_price_squared_volume')
            profile = _profile_summary(trade.get('sparse_profile'), coverage_complete=price_complete)
            if priced_volume != profile['priced_buy'] + profile['priced_sell'] + profile['priced_unknown']:
                raise IntegrityError('weighted priced volume does not equal sparse priced side totals')
            quality = item.get('source_quality') or {}
            if not isinstance(quality, dict):
                raise IntegrityError('source_quality must be an object')
            quote = _quote_row(item.get('quote'), source_coverage_complete=source_complete,
                               coordinate_complete=coordinate_complete)
            presence = _bool(item.get('source_instrument_presence'), what='source_instrument_presence')
            stable = _bool(item.get('supplied_raw_coordinate_stable'), what='supplied_raw_coordinate_stable')
            archive_complete = _archive_contains(unit['archive_intervals'], start, end)
            row = {
                'root': unit['root'], 'source_path': unit['source_path'],
                'source_metadata_sha256': unit['source_metadata_sha256'],
                'source_variant': unit['source_variant'],
                'source_window_start_ns': unit['start'], 'source_window_end_ns': unit['end'],
                'receipt_sha256': unit['receipt_sha256'],
                'measurement_sha256': unit['measurement_sha256'],
                'canonical_raw_values_sha256': unit['canonical_raw_values_sha256'],
                'instrument_id': instrument_id,
                'contract_key': None if coordinate.get('contract_key') is None else _text(
                    coordinate.get('contract_key'), what='contract_key'),
                'event_start_ns': start, 'event_end_ns': end, 'known_at_ns': known, 'atomic_bin': number,
                'coordinate_complete': coordinate_complete,
                'supplied_raw_coordinate_stable': stable,
                'source_instrument_presence': presence,
                'source_coverage_complete': source_complete,
                'flow_history_complete': flow_complete,
                'price_history_complete': price_complete,
                'empty_observed_window': empty,
                'archive_window_complete': archive_complete,
                **{name: _int(quality.get(name, 0), what=name, minimum=0) for name in _SOURCE_QUALITY_COUNTS},
                'clock_uncertain_intervals': _clock_uncertain_count(quality, item.get('quote') or {}),
                'prints': prints, 'unpriced_prints': unpriced,
                **_priced_trade(trade.get('first_priced_trade'), prefix='first_priced'),
                **_priced_trade(trade.get('last_priced_trade'), prefix='last_priced'),
                'observed_high_ticks': _int_or_none(trade.get('observed_high_ticks'), what='observed_high_ticks'),
                'observed_low_ticks': _int_or_none(trade.get('observed_low_ticks'), what='observed_low_ticks'),
                'observed_high_at_ns': _int_or_none(trade.get('observed_high_at_ns'), what='observed_high_at_ns'),
                'observed_low_at_ns': _int_or_none(trade.get('observed_low_at_ns'), what='observed_low_at_ns'),
                'observed_high_source_order': _int_or_none(trade.get('observed_high_source_order'),
                                                           what='observed_high_source_order'),
                'observed_low_source_order': _int_or_none(trade.get('observed_low_source_order'),
                                                          what='observed_low_source_order'),
                'observed_price_variation_ticks': _int(trade.get('observed_price_variation_ticks'),
                                                       what='observed_price_variation_ticks', minimum=0),
                'observed_up_variation_ticks': _int(trade.get('observed_up_variation_ticks'),
                                                    what='observed_up_variation_ticks', minimum=0),
                'observed_down_variation_ticks': _int(trade.get('observed_down_variation_ticks'),
                                                      what='observed_down_variation_ticks', minimum=0),
                'observed_squared_price_variation_ticks_squared': _int(
                    trade.get('observed_squared_price_variation_ticks_squared'),
                    what='observed_squared_price_variation_ticks_squared', minimum=0),
                'observed_adjacent_priced_pairs': _int(trade.get('observed_adjacent_priced_pairs'),
                                                       what='observed_adjacent_priced_pairs', minimum=0),
                'observed_maximum_same_side_run': _int(trade.get('observed_maximum_same_side_run'),
                                                       what='observed_maximum_same_side_run', minimum=0),
                'same_time_adjacent_prints': _int(trade.get('same_time_adjacent_prints'),
                                                  what='same_time_adjacent_prints', minimum=0),
                'terminal_run_right_censored': _bool(trade.get('terminal_run_right_censored'),
                                                     what='terminal_run_right_censored'),
                'priced_volume': priced_volume, 'sum_price_volume': sum_pv,
                'sum_price_squared_volume': sum_p2v,
                'vwap_ticks': _float64_or_none(weighted.get('vwap_ticks'), what='vwap_ticks'),
                'variance_ticks_squared': _float64_or_none(weighted.get('variance_ticks_squared'),
                                                           what='variance_ticks_squared'),
                **_quantile_map(weighted.get('weighted_quantile_ticks'), _WEIGHTED_QUANTILES,
                                what='weighted_quantile_ticks'),
                **_quantile_map(trade.get('count_weighted_size_quantiles'), _SIZE_QUANTILES,
                                what='count_weighted_size_quantiles'),
                'count_intensity_per_second': _float64_or_none(trade.get('count_intensity_per_second'),
                                                               what='count_intensity_per_second'),
                'volume_intensity_per_second': _float64_or_none(trade.get('volume_intensity_per_second'),
                                                                what='volume_intensity_per_second'),
                **profile,
                **quote,
            }
            for name in SOURCE_FILTERS:
                row.update(_cohort_columns(name, checked[name]))
            if set(row) != column_names:
                raise IntegrityError('constructed observation row does not match the explicit schema')
            variation = row['observed_price_variation_ticks']
            if variation != row['observed_up_variation_ticks'] + row['observed_down_variation_ticks']:
                raise IntegrityError('price variation is not up+down')
            rows.append(row)
            instrument_atomic['prints'] += prints
            instrument_atomic['volume'] += checked['all']['volume']
            instrument_atomic['quote_rows'] += row['quote_or_invalidation_rows']
            _add_flow_totals(instrument_atomic, checked)
            _add_flow_totals(atomic_totals, checked)
            atomic_totals['prints'] += prints
            atomic_totals['volume'] += checked['all']['volume']
            atomic_totals['quote_rows'] += row['quote_or_invalidation_rows']
        if instrument_atomic['prints'] != _int(whole.get('prints'), what='whole_window.prints', minimum=0):
            raise IntegrityError('per-instrument atomic prints do not equal whole_window prints')
        if instrument_atomic['volume'] != checked_whole['all']['volume']:
            raise IntegrityError('per-instrument atomic volume does not equal whole_window volume')
        for name in SOURCE_FILTERS:
            if instrument_atomic[f'{name}__prints'] != checked_whole[name]['prints']:
                raise IntegrityError(f'per-instrument {name} atomic prints do not equal the whole window')
            if instrument_atomic[f'{name}__volume'] != checked_whole[name]['volume']:
                raise IntegrityError(f'per-instrument {name} atomic volume does not equal the whole window')
            if instrument_atomic[f'{name}__buy'] != checked_whole[name]['buy']:
                raise IntegrityError(f'per-instrument {name} atomic buy mass does not equal the whole window')
            if instrument_atomic[f'{name}__sell'] != checked_whole[name]['sell']:
                raise IntegrityError(f'per-instrument {name} atomic sell mass does not equal the whole window')
            if instrument_atomic[f'{name}__unknown'] != checked_whole[name]['unknown']:
                raise IntegrityError(f'per-instrument {name} atomic unknown mass does not equal the whole window')
            if instrument_atomic[f'{name}__delta'] != checked_whole[name]['close'] - checked_whole[name]['open']:
                raise IntegrityError(f'per-instrument {name} open-relative close does not equal the whole window')
    if atomic_totals['prints'] != whole_totals['prints'] or atomic_totals['prints'] != receipt_trades:
        raise IntegrityError('atomic, whole-window and receipt trade print counts do not reconcile')
    if atomic_totals['volume'] != whole_totals['volume'] or atomic_totals['volume'] != receipt_volume:
        raise IntegrityError('atomic, whole-window and receipt trade volumes do not reconcile')
    if atomic_totals['quote_rows'] != receipt_quotes:
        raise IntegrityError('atomic quote rows do not equal receipt counts.quote_rows')
    return rows


def write_observation_unit(receipt, measured, *, receipt_reference, outputs):
    """Write one source/day observation series and a compact validation summary."""
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError('observation unit write requires bounded registered outputs')
    started = time.process_time()
    rows = observation_rows(receipt, measured, receipt_reference=receipt_reference)
    table = observation_table(rows)
    prefix = window_artifact_prefix(_mapping(receipt.get('unit'), what='receipt.unit'))
    series = ParquetSeries(outputs, f'{prefix}-observations', encoding='structural')
    offset = 0
    while offset < len(table):
        amount = min(BATCH_ROWS, len(table) - offset)
        series.append(table.slice(offset, amount))
        offset += amount
    stored = series.finish()
    cpu = time.process_time() - started
    flags = (
        'coordinate_complete', 'supplied_raw_coordinate_stable', 'source_instrument_presence',
        'source_coverage_complete', 'flow_history_complete', 'price_history_complete',
        'empty_observed_window', 'quote_coverage_complete', 'full_standing_window_eligible',
        'full_pressure_transition_window_eligible', 'archive_window_complete',
    )
    eligibility = {name: sum(1 for row in rows if row[name]) for name in flags}
    raw_rows = sum(row['raw_rows'] for row in rows)
    quote_rows = sum(row['quote_or_invalidation_rows'] for row in rows)
    prints = sum(row['prints'] for row in rows)
    volume = sum(row['all__volume'] for row in rows)
    counts = _mapping(receipt.get('counts'), what='receipt.counts')
    summary = {
        'version': VERSION,
        'kind': 'auction_flow_observation_unit_v1',
        'root': rows[0]['root'] if rows else None,
        'source_path': rows[0]['source_path'] if rows else None,
        'source_window_start_ns': rows[0]['source_window_start_ns'] if rows else None,
        'source_window_end_ns': rows[0]['source_window_end_ns'] if rows else None,
        'atomic_rows': len(rows),
        'instruments': len({row['instrument_id'] for row in rows}),
        'raw_rows': raw_rows,
        'quote_rows': quote_rows,
        'trade_prints': prints,
        'trade_volume': volume,
        'receipt_counts': {
            'trades': counts.get('trades'),
            'volume': counts.get('volume'),
            'quote_rows': counts.get('quote_rows'),
            'raw_rows': counts.get('raw_rows'),
        },
        'eligibility_counts': eligibility,
        'whole_mass_checks': {
            'atomic_prints_equal_receipt_trades': prints == counts.get('trades'),
            'atomic_volume_equal_receipt_volume': volume == counts.get('volume'),
            'atomic_quote_rows_equal_receipt_quote_rows': quote_rows == counts.get('quote_rows'),
            'source_raw_rows_not_equated_to_receipt': True,
        },
        'original_refs': {
            'receipt_sha256': rows[0]['receipt_sha256'] if rows else None,
            'measurement_sha256': rows[0]['measurement_sha256'] if rows else None,
            'canonical_raw_values_sha256': rows[0]['canonical_raw_values_sha256'] if rows else None,
            'receipt_reference': {
                'sha256': receipt_reference.get('sha256'),
                'path': receipt_reference.get('path'),
                'size_bytes': receipt_reference.get('size_bytes'),
                'kind': receipt_reference.get('kind'),
            },
        },
        'output_bytes': stored['serialized_bytes'],
        'cpu_seconds': cpu,
        'series': stored,
        'family_statistics_or_model_complete': False,
    }
    return summary
