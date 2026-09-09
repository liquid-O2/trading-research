"""Full-population profile/reference statistics over reconstructed geometry.

Root owns registration, review, integration and registered execution. This
reducer never spawns processes. It reuses accepted partitions only after
authenticating every consumer file hash, support neighbor refs, and the
scientific identity, then retains per-partition group references in a compact manifest.
"""
from __future__ import annotations

from array import array
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
import math
import time as time_mod

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.operations.artifacts import digest, file_digest
from trading_research.research.auction_flow_core_statistics import (
    ExplicitCashSessions, FROZEN_STAGE_POLICY, REQUIRED_CASH_CALENDAR_REFERENCE,
    STAGE_ORDER, labeled_date_and_event_means,
)
from trading_research.research.auction_flow_profile_reference import (
    BAR_PROXY_VARIANTS, BASELINE_VARIANT_ID, FROZEN_CONTRACT_KIND,
    FROZEN_GEOMETRY_VARIANTS, KIND as PARTITION_KIND, LATENCY_NS, NS,
    POPULATION_KIND, ProfileCashAdapter, QUANTILE_LEVELS, VERSION,
    WINDOW_POPULATION_KIND, classify_source_collection, compute_profile_partition,
    decode_exact_int, empty_completeness, footprint_parameters, frozen_variant_ids,
    require_frozen_variants, write_series_table,
)
from trading_research.research.auction_flow_storage import BoundedOutputs, read_series_tables
from trading_research.research.auction_flow_window_statistics import intended_date_universe
from trading_research.research.date_statistics import _moving_weights, observed_date_statistics


KIND = 'auction_flow_profile_reference_statistics_result_v1'
GROUPS_MANIFEST_KIND = 'auction_flow_profile_group_manifest_v1'
PAIRED_MANIFEST_KIND = 'auction_flow_profile_paired_manifest_v1'
JSON_LOAD_MAX = 128 * 1024 ** 2
OPERATIONAL_CONTRACT_FIELDS = (
    'phase', 'pilot_source_paths', 'accepted_partitions', 'selected_partition_keys',
    'accepted_pilot_execution', 'accepted_pilot_worker', 'accepted_consumer_files',
    'parallel_execution', 'cash_session_table', 'source_collections',
)
_GFIELDS = (
    'group_kind', 'source_collection', 'root', 'year', 'stage', 'session',
    'anchor', 'variant', 'proxy', 'measurement_status', 'contrast',
    'formation_minutes', 'latency_ns', 'horizon_kind', 'horizon_minutes',
)
PAIRED_CONTRASTS = (
    ('source-one-tick-value-17/25', 'source-one-tick-value-7/10', 'fraction_68_vs_70'),
    ('value70-expansion-tie-lower', 'source-one-tick-value-7/10', 'value_tie_lower_vs_upper'),
    ('value70-expansion-tie-both', 'source-one-tick-value-7/10', 'value_tie_both_vs_upper'),
    ('value70-poc-tie-upper', 'source-one-tick-value-7/10', 'poc_tie_upper_vs_lower'),
    ('value70-width2-origin0', 'source-one-tick-value-7/10', 'width2_origin0_vs_one_tick'),
    ('value70-width2-origin1', 'source-one-tick-value-7/10', 'width2_origin1_vs_one_tick'),
    ('value70-width4-origin0', 'source-one-tick-value-7/10', 'width4_origin0_vs_one_tick'),
    ('value70-width4-origin1', 'source-one-tick-value-7/10', 'width4_origin1_vs_one_tick'),
    ('value70-width8-origin0', 'source-one-tick-value-7/10', 'width8_origin0_vs_one_tick'),
    ('value70-width8-origin1', 'source-one-tick-value-7/10', 'width8_origin1_vs_one_tick'),
    ('value70-triangular-scale1', 'source-one-tick-value-7/10', 'triangular1_vs_unsmoothed'),
    ('value70-triangular-scale2', 'source-one-tick-value-7/10', 'triangular2_vs_unsmoothed'),
    ('value70-triangular-scale4', 'source-one-tick-value-7/10', 'triangular4_vs_unsmoothed'),
)
METRIC_UNITS = {
    'scalar_poc': 'quarter_point_ticks',
    'val_row': 'grid_rows',
    'vah_row': 'grid_rows',
    'physical_poc_ticks': 'quarter_point_ticks',
    'physical_val_ticks': 'quarter_point_ticks',
    'physical_vah_ticks': 'quarter_point_ticks',
    'va_width_ticks': 'grid_rows',
    'va_width_physical_ticks': 'quarter_point_ticks',
    'poc_count': 'count',
    'overshoot_mass': 'contract_fractions',
    'priced_volume': 'contracts',
    'vwap_ticks': 'quarter_point_ticks',
    'variance_ticks_squared': 'ticks_squared',
    'sd_ticks_approx': 'quarter_point_ticks',
    'poc_touch': 'dimensionless',
    'val_touch': 'dimensionless',
    'vah_touch': 'dimensionless',
    'terminal_inside_va': 'dimensionless',
    'visit_count': 'count',
    'range_proxy_count': 'count',
    'single_print_count': 'count',
    'source_flat_bar_lost_mass': 'contracts',
    'boundary_moving': 'dimensionless',
    'price_crossing_frozen_va': 'dimensionless',
    'no_event': 'dimensionless',
    'censored': 'dimensionless',
    'missing': 'dimensionless',
    'link_rows': 'count',
    'concentration': 'dimensionless',
    'signed_delta': 'contracts',
    'absolute_delta_mass': 'contracts',
    'footprint_buy_imbalance_rows': 'count',
    'footprint_sell_imbalance_rows': 'count',
    'pin069_vwap': 'quarter_point_ticks',
    'pin069_bar_volume': 'contracts',
    'peak_count': 'count',
    'valley_count': 'count',
    'dominance_margin': 'contracts',
    'side_overlap': 'dimensionless',
    'side_total_variation': 'dimensionless',
    'side_wasserstein': 'quarter_point_ticks',
    'footprint_buy_stack_count': 'count',
    'footprint_sell_stack_count': 'count',
    'unpriced_only_atoms': 'count',
    'input_cells': 'count',
    'complete_brackets': 'count',
    'ib30_complete': 'dimensionless',
    'ib60_complete': 'dimensionless',
    'future_low_overflow_buy': 'contracts',
    'future_high_overflow_buy': 'contracts',
    'future_input_known': 'dimensionless',
    'future_coverage_complete': 'dimensionless',
    'sd_band_0_low_approx': 'quarter_point_ticks',
    'sd_band_0_high_approx': 'quarter_point_ticks',
    'sd_band_1_low_approx': 'quarter_point_ticks',
    'sd_band_1_high_approx': 'quarter_point_ticks',
    'sd_band_2_low_approx': 'quarter_point_ticks',
    'sd_band_2_high_approx': 'quarter_point_ticks',
    'sd_band_3_low_approx': 'quarter_point_ticks',
    'sd_band_3_high_approx': 'quarter_point_ticks',
    'percent_band_0_low': 'quarter_point_ticks',
    'percent_band_0_high': 'quarter_point_ticks',
    'percent_band_1_low': 'quarter_point_ticks',
    'percent_band_1_high': 'quarter_point_ticks',
    'percent_band_2_low': 'quarter_point_ticks',
    'percent_band_2_high': 'quarter_point_ticks',
    'q_1_20': 'quarter_point_ticks',
    'q_1_4': 'quarter_point_ticks',
    'q_1_2': 'quarter_point_ticks',
    'q_3_4': 'quarter_point_ticks',
    'q_19_20': 'quarter_point_ticks',
    'weighted_median': 'quarter_point_ticks',
    'mad': 'quarter_point_ticks',
    'robust_scale': 'quarter_point_ticks',
    'ib30_high': 'quarter_point_ticks',
    'ib30_low': 'quarter_point_ticks',
    'ib60_high': 'quarter_point_ticks',
    'ib60_low': 'quarter_point_ticks',
    'low_tail_count': 'count',
    'high_tail_count': 'count',
    'provisional_single_print_count': 'count',
    'final_single_print_count': 'count',
    'poc_traverse': 'dimensionless',
    'val_traverse': 'dimensionless',
    'vah_traverse': 'dimensionless',
    'terminal_outside_va': 'dimensionless',
    'terminal_at_poc': 'dimensionless',
    'future_val': 'quarter_point_ticks',
    'future_vah': 'quarter_point_ticks',
    'future_poc': 'quarter_point_ticks',
    'future_transport': 'quarter_point_ticks',
    'future_low_overflow_sell': 'contracts',
    'future_low_overflow_unknown': 'contracts',
    'future_high_overflow_sell': 'contracts',
    'future_high_overflow_unknown': 'contracts',
    'future_low_overflow_unpriced': 'contracts',
    'future_high_overflow_unpriced': 'contracts',
    'future_unpriced_buy': 'contracts',
    'future_unpriced_sell': 'contracts',
    'future_unpriced_unknown': 'contracts',
    'unpriced_buy': 'contracts',
    'unpriced_sell': 'contracts',
    'unpriced_unknown': 'contracts',
    'low_overflow_buy': 'contracts',
    'low_overflow_sell': 'contracts',
    'low_overflow_unknown': 'contracts',
    'high_overflow_buy': 'contracts',
    'high_overflow_sell': 'contracts',
    'high_overflow_unknown': 'contracts',
}


def _mapping(value, *, what):
    if not isinstance(value, dict):
        raise IntegrityError(f'{what} must be an object')
    return value


def _text(value, *, what):
    if type(value) is not str or not value:
        raise IntegrityError(f'{what} must be a concrete string')
    return value


def scientific_contract_definition(contract):
    rec = _mapping(contract, what='contract')
    return {name: value for name, value in rec.items() if name not in OPERATIONAL_CONTRACT_FIELDS}


def encode_profile_partition_key(key):
    if not isinstance(key, (list, tuple)) or len(key) != 3:
        raise IntegrityError('profile partition key must be (collection, root, economic_year)')
    collection, root, year = key
    if type(collection) is not str or not collection or type(root) is not str or not root:
        raise IntegrityError('partition collection and root must be nonempty strings')
    if type(year) is bool or type(year) is not int:
        raise IntegrityError('partition economic year must be an exact integer')
    return [collection, root, int(year)]


def decode_profile_partition_key(key):
    return tuple(encode_profile_partition_key(key))


def _unit_path(unit):
    ident = unit.get('source_identity') or {}
    return ident.get('source_path') or unit.get('source_path')


def _unit_root(unit):
    ident = unit.get('source_identity') or {}
    return ident.get('root') or unit.get('root')


def _unit_window_ns(unit):
    start = unit.get('source_window_start_ns')
    end = unit.get('source_window_end_ns')
    if start is not None and end is not None:
        return int(start), int(end)
    ident = unit.get('source_identity') or {}
    if ident.get('acquired_event_start_ns') is not None:
        return int(ident['acquired_event_start_ns']), int(ident['acquired_event_end_ns'])
    raise IntegrityError('observation unit lost a positive half-open interval')


def _unit_unavailable(unit):
    if unit.get('disposition') == 'unavailable_source_window':
        return True
    if unit.get('source_window_status') == 'unavailable_source_window':
        return True
    if unit.get('atomic_rows') == 0:
        return True
    series = unit.get('series')
    if series is None or series.get('roundtrip_exact') is not True:
        return True
    return False


def _unit_identity_key(unit):
    start, end = _unit_window_ns(unit)
    return (_unit_path(unit), _unit_root(unit), start, end, unit.get('receipt', {}).get('sha256'))


def derive_source_collections(population, contract):
    """Collection map from operational injection, unit identity, or path class."""
    injected = contract.get('source_collections') if isinstance(contract, dict) else None
    injected = injected if isinstance(injected, dict) else {}
    units = population.get('units') if isinstance(population, dict) else None
    if not isinstance(units, list):
        raise IntegrityError('observation population lost its unit summaries')
    out = {}
    for unit in units:
        path = _unit_path(unit)
        out[path] = classify_source_collection(path, unit=unit, injected=injected)
    return out


def profile_partition_plan(population, contract):
    """Map observation units onto (collection, root, economic_year)."""
    rec = _mapping(population, what='population')
    if rec.get('kind') != POPULATION_KIND:
        raise IntegrityError('authenticated auction_flow_observation_population_v1 required')
    units = rec.get('units')
    if not isinstance(units, list):
        raise IntegrityError('observation population lost its unit summaries')
    collections = derive_source_collections(rec, contract)
    partitions = defaultdict(list)
    unavailable = 0
    for unit in units:
        path = _unit_path(unit)
        root = _unit_root(unit)
        if type(path) is not str or type(root) is not str:
            raise IntegrityError('observation unit lost source path or root')
        collection = collections[path]
        start, end = _unit_window_ns(unit)
        if not start < end:
            raise IntegrityError('observation unit lost a positive half-open interval')
        from trading_research.research.auction_flow_core_statistics import economic_date
        years = {int(economic_date(int(start))[:4]), int(economic_date(int(end - 1))[:4])}
        if _unit_unavailable(unit):
            unavailable += 1
        for year in sorted(years):
            partitions[(collection, root, year)].append(unit)
    members = {}
    for key in sorted(partitions):
        members[key] = sorted(
            partitions[key],
            key=lambda unit: (_unit_window_ns(unit)[0], _unit_path(unit)),
        )
    return {
        'keys': list(members),
        'members': members,
        'unavailable_units': unavailable,
        'selected_units': list(units),
        'canonical_keys': [encode_profile_partition_key(key) for key in members],
        'collections': collections,
    }


def neighbor_units(plan, key, *, collections=None):
    """Same-collection prior/next units for civil carry and 60-minute future."""
    collection, root, year = key
    members = plan['members'][key]
    selected = {_unit_identity_key(unit) for unit in members}
    year_start = local_timestamp(date(year, 1, 1), __import__('datetime').time(0), 'America/New_York')
    year_end = local_timestamp(date(year + 1, 1, 1), __import__('datetime').time(0), 'America/New_York')
    span_start = year_start - 370 * 24 * 60 * 60 * NS
    span_end = year_end + 60 * 60 * NS
    neighbors = []
    for other_key, units in plan['members'].items():
        other_collection, other_root, _other_year = other_key
        if other_collection != collection or other_root != root:
            continue
        for unit in units:
            ukey = _unit_identity_key(unit)
            if ukey in selected:
                continue
            start, end = _unit_window_ns(unit)
            if end <= span_start or start >= span_end:
                continue
            neighbors.append(unit)
    _ = collections
    return neighbors


def profile_partition_source_refs(members, *, role='selected'):
    refs = []
    for unit in members:
        series = unit.get('series') or {}
        measurement = unit.get('measurement') or (unit.get('original_refs') or {}).get('measurement') or {}
        refs.append({
            'role': role,
            'source_path': _unit_path(unit),
            'root': _unit_root(unit),
            'source_window_start_ns': _unit_window_ns(unit)[0],
            'source_window_end_ns': _unit_window_ns(unit)[1],
            'atomic_rows': unit.get('atomic_rows'),
            'series': {
                'rows': series.get('rows'),
                'schema': series.get('schema'),
                'files': [
                    {
                        'path': item.get('path'),
                        'sha256': item.get('sha256'),
                        'rows': item.get('rows'),
                    }
                    for item in series.get('files') or []
                ],
            },
            'measurement': {
                'path': measurement.get('path'),
                'sha256': measurement.get('sha256'),
                'uncompressed_sha256': measurement.get('uncompressed_sha256'),
                'size_bytes': measurement.get('size_bytes'),
            },
            'receipt': unit.get('receipt') or (unit.get('original_refs') or {}).get('receipt_reference'),
        })
    return refs


def consumer_implementation_identity():
    here = Path(__file__).resolve()
    other = here.with_name('auction_flow_profile_reference.py')
    files = []
    for path in (here, other):
        files.append({
            'name': path.name,
            'sha256': file_digest(path),
            'size_bytes': path.stat().st_size,
        })
    return files


def profile_partition_identity(contract, *, collection, root, year, source_refs, window_refs):
    return digest({
        'definition': scientific_contract_definition(contract),
        'collection': collection,
        'root': root,
        'economic_year': year,
        'source_refs': source_refs,
        'window_refs': window_refs,
        'consumer_implementation': consumer_implementation_identity(),
    })


def window_unit_refs(units, *, paths):
    refs = []
    for unit in units:
        path = (unit.get('source_identity') or {}).get('source_path') or unit.get('source_path')
        if path not in paths:
            continue
        refs.append({
            'unit_id': unit.get('unit_id'),
            'source_identity': unit.get('source_identity'),
            'features': _series_digest(unit.get('features')),
            'labels': _series_digest(unit.get('labels')),
            'feature_rows': unit.get('feature_rows'),
            'label_rows': unit.get('label_rows'),
        })
    return refs


def _series_digest(series):
    if not isinstance(series, dict):
        return None
    files = []
    for item in series.get('files') or []:
        groups = [(g.get('sha256'), g.get('rows')) for g in item.get('row_group_values') or []]
        files.append((item.get('sha256'), item.get('rows'), groups))
    return {'rows': series.get('rows'), 'schema': series.get('schema'), 'files': files}


def _require_contract(contract, *, population=None):
    rec = _mapping(contract, what='contract')
    if rec.get('kind') != FROZEN_CONTRACT_KIND:
        raise IntegrityError('frozen auction_flow_profile_reference_statistics_contract_v1 required')
    if rec.get('version') != 1:
        raise IntegrityError('profile reference contract version changed')
    if rec.get('full_family_complete') is True:
        raise IntegrityError('contract cannot certify family completion')
    require_frozen_variants(rec)
    clocks = rec.get('anchor_definitions', {}).get('fixed_clocks') if isinstance(rec.get('anchor_definitions'), dict) else rec.get('fixed_clocks')
    if clocks is not None:
        ids = [item.get('id') for item in clocks]
        expected = [
            'cash_rth', 'prior_cash_rth', 'observed_futures_18_17', 'overnight_18_0930',
            'morning_06_09_ny', 'source_06_09_fixed_utc_minus4',
            'source_monday_22_21_utc', 'source_tuesday_22_21_utc',
        ]
        if ids != expected:
            raise IntegrityError('frozen contract requires the declared eight clock identities')
    rolling = rec.get('anchor_definitions', {}).get('rolling_minutes') if isinstance(rec.get('anchor_definitions'), dict) else rec.get('rolling_minutes')
    if rolling is not None and list(rolling) != [5, 15, 60, 240]:
        raise IntegrityError('frozen rolling 5/15/60/240 minutes are required')
    latencies = rec.get('clock', {}).get('latencies_ns') if isinstance(rec.get('clock'), dict) else rec.get('latencies_ns')
    if latencies is not None and list(latencies) != list(LATENCY_NS):
        raise IntegrityError('every declared latency candidate must be retained')
    stats = rec.get('statistics') or {}
    if (stats.get('seed') != 20260908 or stats.get('block_length') != 5
            or stats.get('bootstrap_replicates') != 1000
            or float(stats.get('confidence', 0)) != 0.95):
        raise IntegrityError('frozen date-block uncertainty settings changed')
    if tuple(stats.get('quantiles') or ()) != QUANTILE_LEVELS:
        raise IntegrityError('frozen sample quantile levels changed')
    policy = rec.get('stage_policy')
    if not isinstance(policy, dict):
        raise IntegrityError('frozen stage_policy is required')
    for root, expected in FROZEN_STAGE_POLICY.items():
        got = policy.get(root)
        if not isinstance(got, dict):
            raise IntegrityError(f'frozen stage_policy.{root} is required')
        for name, bounds in expected.items():
            if tuple(got.get(name) or ()) != bounds:
                raise IntegrityError(f'frozen stage_policy.{root}.{name} changed')
    collections = derive_source_collections(population, rec) if population is not None else rec.get('source_collections') or {}
    _ = footprint_parameters(rec)
    return rec, stats, policy, collections


def _load_calendar(contract, load_reference):
    table = contract.get('cash_session_table')
    reference = contract.get('calendar') or contract.get('cash_calendar')
    if table is not None:
        inner = ExplicitCashSessions(table, reference={'kind': 'explicit_cash_session_table'})
        return ProfileCashAdapter(inner)
    if reference is None:
        raise ContractError(
            'profile statistics require contract.calendar equal to the admitted '
            f'cash_rth_calendar {REQUIRED_CASH_CALENDAR_REFERENCE!r}; fixtures may pass '
            'cash_session_table instead'
        )
    if (not isinstance(reference, dict) or type(reference.get('path')) is not str
            or type(reference.get('sha256')) is not str):
        raise IntegrityError('calendar must be a fully qualified path/sha256 reference')
    if (reference.get('path') != REQUIRED_CASH_CALENDAR_REFERENCE['path']
            or reference.get('sha256') != REQUIRED_CASH_CALENDAR_REFERENCE['sha256']
            or reference.get('size_bytes') != REQUIRED_CASH_CALENDAR_REFERENCE['size_bytes']):
        raise IntegrityError('production calendar identity does not match the frozen cash RTH calendar')
    if callable(load_reference):
        payload = load_reference(reference)
        if not isinstance(payload, dict) or payload.get('schema') != 'published-cash-rth-calendar-v1':
            raise IntegrityError('calendar reference is not the published cash RTH calendar')
    from trading_research.foundations.cash_calendar import CashCalendar
    inner = ExplicitCashSessions(published=CashCalendar(Path(reference['path'])), reference=reference)
    return ProfileCashAdapter(inner)


def _gkey(**kwargs):
    extra = set(kwargs).difference(_GFIELDS)
    if extra:
        raise IntegrityError(f'unknown group metadata fields {sorted(extra)}')
    return tuple(kwargs.get(name) for name in _GFIELDS)


def _gmeta(key):
    return dict(zip(_GFIELDS, key))


class _DateStore:
    __slots__ = ('date_sum', 'date_count', 'n', 'total', 'minimum', 'maximum', 'raw')

    def __init__(self):
        self.date_sum = {}
        self.date_count = {}
        self.n = 0
        self.total = 0.0
        self.minimum = None
        self.maximum = None
        self.raw = array('d')

    def add(self, day, value):
        if value is None or day is None:
            return
        number = float(value)
        if not math.isfinite(number):
            return
        self.date_sum[day] = self.date_sum.get(day, 0.0) + number
        self.date_count[day] = self.date_count.get(day, 0) + 1
        self.n += 1
        self.total += number
        self.raw.append(number)
        self.minimum = number if self.minimum is None else min(self.minimum, number)
        self.maximum = number if self.maximum is None else max(self.maximum, number)


def new_partition_accumulators():
    return {
        'groups': defaultdict(dict),
        'paired': defaultdict(dict),
        'alias_dates': defaultdict(set),
        'geometry_index': defaultdict(dict),
        'exact_index': {},
        'proxy_index': {},
        'tpo_index': defaultdict(dict),
        'emitted_variants': defaultdict(set),
        'emitted_proxies': defaultdict(set),
        'paired_done': set(),
    }


def _comparison_geometry_row(row):
    kind = row.get('anchor_kind')
    variant = row.get('anchor_variant') or ''
    if kind in ('developing', 'rolling'):
        return False
    if variant.startswith('developing_') or variant.startswith('rolling_'):
        return False
    return True


def _metric_unit(name):
    return METRIC_UNITS.get(name, 'dimensionless')


def _undefined_metric(*, unit=None):
    return {
        'unit': unit, 'estimate': None, 'date_mean': None, 'event_mean': None,
        'eligible_observations': 0, 'eligible_independent_dates': 0,
        'missing_date_count': None,
        'sample_quantiles': {str(level): None for level in QUANTILE_LEVELS},
        'raw_quantiles': {str(level): None for level in QUANTILE_LEVELS},
        'support': {'independent_dates': 0, 'events': 0, 'sparse': True,
                    'reasons': ['no_valid_observations']},
        'bootstrap': None, 'undefined': True,
    }


def _exact_quantiles(values, levels):
    if not values:
        return {str(level): None for level in levels}
    import numpy as np
    ordered = np.asarray(values, dtype=np.float64)
    quantiles = np.quantile(ordered, levels, method='linear')
    return {str(level): float(item) for level, item in zip(levels, quantiles)}


def _metric_payload(store, intended, stats_result=None, *, min_dates, min_events, unit):
    counts = store.date_count
    missing = sum(1 for day in intended if counts.get(day, 0) == 0)
    date_means = [store.date_sum[day] / counts[day] for day in sorted(counts) if counts[day]]
    event_mean = None if store.n == 0 else store.total / store.n
    date_mean_value = None if not date_means else math.fsum(date_means) / len(date_means)
    reasons = []
    if store.n == 0 or not date_means:
        reasons.append('no_valid_observations')
    if len(counts) < min_dates:
        reasons.append('fewer_than_minimum_independent_dates')
    if store.n < min_events:
        reasons.append('fewer_than_minimum_events')
    payload = {
        'unit': unit,
        'eligible_observations': store.n,
        'eligible_independent_dates': len(counts),
        'missing_date_count': missing if intended else len(intended),
        'observation_moments': {
            'count': store.n, 'mean': event_mean,
            'minimum': store.minimum, 'maximum': store.maximum, 'sum': store.total,
        },
        'sample_quantiles': _exact_quantiles(date_means, QUANTILE_LEVELS),
        'raw_quantiles': _exact_quantiles(store.raw, QUANTILE_LEVELS),
        'sample_quantile_distribution': 'equal_weight_date_mean',
        'raw_quantile_distribution': 'observation_weighted',
        'date_mean': date_mean_value,
        'event_mean': event_mean,
        'support': {
            'independent_dates': len(counts),
            'events': store.n,
            'minimum_independent_dates': min_dates,
            'minimum_events': min_events,
            'sparse': bool(reasons),
            'reasons': reasons,
        },
        'bootstrap': None,
        'undefined': store.n == 0,
    }
    if stats_result is not None:
        support = dict(stats_result.get('support') or {})
        support['events'] = store.n
        support['independent_dates'] = stats_result.get('actual_valid_date_count', len(counts))
        reasons = list(support.get('reasons') or [])
        if store.n < min_events and 'fewer_than_minimum_events' not in reasons:
            reasons.append('fewer_than_minimum_events')
        if support.get('independent_dates', 0) < min_dates and 'fewer_than_minimum_independent_dates' not in reasons:
            reasons.append('fewer_than_minimum_independent_dates')
        support['reasons'] = reasons
        support['sparse'] = bool(reasons)
        payload['date_mean'] = {
            'estimate': stats_result.get('estimate'),
            'actual_valid_date_count': stats_result.get('actual_valid_date_count'),
            'actual_valid_event_count': store.n,
            'canonical_date_event_count': stats_result.get('actual_valid_event_count'),
            'support': support,
            'bootstrap': stats_result.get('bootstrap'),
            'distribution': 'equal_weight_date_mean',
        }
        payload['estimate'] = stats_result.get('estimate')
        payload['support'] = support
        payload['bootstrap'] = stats_result.get('bootstrap')
        payload['undefined'] = stats_result.get('estimate') is None
    return payload


def _finalize_groups(groups, *, intended_by_stage, stats, np):
    seed = int(stats.get('seed', 20260908))
    block = int(stats.get('block_length', 5))
    replicates = int(stats.get('bootstrap_replicates', 1000))
    confidence = float(stats.get('confidence', 0.95))
    min_dates = int(stats.get('minimum_independent_dates', stats.get('minimum_dates', 100)))
    min_events = int(stats.get('minimum_events', 20))
    finalized = []
    by_universe = defaultdict(list)
    for key in groups:
        meta = _gmeta(key)
        by_universe[(meta['root'], meta['year'], meta['stage'])].append(key)
    for (root, year, stage), keys in by_universe.items():
        intended = list(intended_by_stage.get((root, year, stage), ()))
        if not intended:
            for key in keys:
                stores = groups[key]
                meta = _gmeta(key)
                prescribed = _prescribed_metrics(meta.get('group_kind'))
                names = tuple(dict.fromkeys((*prescribed, *stores)))
                metrics = {name: _undefined_metric(unit=_metric_unit(name)) for name in names}
                finalized.append({**_gmeta(key), 'metrics': metrics, 'intended_dates': intended,
                                 'intended_date_count': 0, 'family_complete': False})
            continue
        weights, starts = _moving_weights(
            np, len(intended), seed=seed, block_length=block, replicates=replicates)
        state = (np, weights, starts)
        for key in sorted(keys, key=lambda item: tuple(str(part) for part in item)):
            stores = groups[key]
            meta = _gmeta(key)
            prescribed = _prescribed_metrics(meta.get('group_kind'))
            for name in prescribed:
                if name not in stores:
                    stores[name] = _DateStore()
            names = tuple(dict.fromkeys((*prescribed, *stores)))
            cells = {}
            for name in names:
                store = stores[name]
                cells[name] = {
                    day: store.date_sum[day] / store.date_count[day]
                    for day in store.date_count if store.date_count[day]
                }
            if not any(cells[name] for name in names):
                metrics = {name: _undefined_metric(unit=_metric_unit(name)) for name in names}
                finalized.append({**_gmeta(key), 'metrics': metrics, 'intended_dates': intended,
                                 'intended_date_count': len(intended), 'family_complete': False})
                continue
            result = observed_date_statistics(
                cells, intended, estimator='date_mean', seed=seed,
                block_length=block, replicates=replicates, confidence=confidence,
                minimum_independent_dates=min_dates, minimum_events=1,
                _retain_replicate_estimates=False, _bootstrap_state=state,
            )
            metrics_out = {}
            for name in names:
                metrics_out[name] = _metric_payload(
                    stores[name], intended, result['metrics'][name],
                    min_dates=min_dates, min_events=min_events, unit=_metric_unit(name),
                )
            finalized.append({
                **_gmeta(key), 'metrics': metrics_out, 'intended_dates': list(intended),
                'intended_date_count': len(intended), 'family_complete': False,
            })
    return finalized


def _row_int(row, name):
    return decode_exact_int(row.get(name), row.get(f'{name}_text'))


def _ratio(num, den):
    if num is None or den in (None, 0):
        return None
    return float(int(num)) / float(int(den))


def _ratio_fields(row, num_name, den_name):
    return _ratio(_row_int(row, num_name), _row_int(row, den_name))


GEOMETRY_METRIC_NAMES = (
    'scalar_poc', 'val_row', 'vah_row', 'physical_poc_ticks', 'physical_val_ticks',
    'physical_vah_ticks', 'va_width_ticks', 'va_width_physical_ticks', 'poc_count',
    'peak_count', 'valley_count', 'overshoot_mass', 'priced_volume', 'vwap_ticks',
    'variance_ticks_squared', 'sd_ticks_approx', 'source_flat_bar_lost_mass',
    'concentration', 'dominance_margin', 'signed_delta', 'absolute_delta_mass',
    'side_overlap', 'side_total_variation', 'side_wasserstein',
    'footprint_buy_imbalance_rows', 'footprint_sell_imbalance_rows',
    'footprint_buy_stack_count', 'footprint_sell_stack_count',
    'pin069_vwap', 'pin069_bar_volume', 'unpriced_only_atoms', 'input_cells',
    'sd_band_0_low_approx', 'sd_band_0_high_approx',
    'sd_band_1_low_approx', 'sd_band_1_high_approx',
    'sd_band_2_low_approx', 'sd_band_2_high_approx',
    'sd_band_3_low_approx', 'sd_band_3_high_approx',
    'percent_band_0_low', 'percent_band_0_high',
    'percent_band_1_low', 'percent_band_1_high',
    'percent_band_2_low', 'percent_band_2_high',
    'q_1_20', 'q_1_4', 'q_1_2', 'q_3_4', 'q_19_20',
    'weighted_median', 'mad', 'robust_scale',
    'unpriced_buy', 'unpriced_sell', 'unpriced_unknown',
    'low_overflow_buy', 'low_overflow_sell', 'low_overflow_unknown',
    'high_overflow_buy', 'high_overflow_sell', 'high_overflow_unknown',
)
TPO_METRIC_NAMES = (
    'visit_count', 'range_proxy_count', 'single_print_count',
    'complete_brackets', 'ib30_complete', 'ib60_complete',
    'ib30_high', 'ib30_low', 'ib60_high', 'ib60_low',
    'low_tail_count', 'high_tail_count',
    'provisional_single_print_count', 'final_single_print_count',
)
JOIN_METRIC_NAMES = (
    'poc_touch', 'val_touch', 'vah_touch', 'terminal_inside_va',
    'poc_traverse', 'val_traverse', 'vah_traverse',
    'terminal_outside_va', 'terminal_at_poc',
    'boundary_moving', 'price_crossing_frozen_va',
    'no_event', 'censored', 'missing', 'link_rows',
    'future_poc', 'future_val', 'future_vah',
    'future_low_overflow_buy', 'future_low_overflow_sell', 'future_low_overflow_unknown',
    'future_high_overflow_buy', 'future_high_overflow_sell', 'future_high_overflow_unknown',
    'future_low_overflow_unpriced', 'future_high_overflow_unpriced',
    'future_unpriced_buy', 'future_unpriced_sell', 'future_unpriced_unknown',
    'future_input_known', 'future_coverage_complete', 'future_transport',
)
PAIRED_METRIC_NAMES = (
    'physical_poc_ticks', 'physical_val_ticks', 'physical_vah_ticks',
    'va_width_physical_ticks', 'overshoot_mass', 'visit_count',
)


def _prescribed_metrics(group_kind):
    if group_kind == 'geometry':
        return GEOMETRY_METRIC_NAMES
    if group_kind == 'tpo':
        return TPO_METRIC_NAMES
    if group_kind == 'join':
        return JOIN_METRIC_NAMES
    if group_kind in ('paired_geometry', 'paired_proxy', 'paired_tpo'):
        return PAIRED_METRIC_NAMES
    return ()


def _geometry_metrics(row):
    return {
        'scalar_poc': row.get('scalar_poc'),
        'val_row': row.get('val_row'),
        'vah_row': row.get('vah_row'),
        'physical_poc_ticks': row.get('physical_poc_ticks'),
        'physical_val_ticks': row.get('physical_val_ticks'),
        'physical_vah_ticks': row.get('physical_vah_ticks'),
        'va_width_ticks': row.get('va_width_ticks'),
        'va_width_physical_ticks': row.get('va_width_physical_ticks'),
        'poc_count': row.get('poc_count'),
        'peak_count': row.get('peak_count'),
        'valley_count': row.get('valley_count'),
        'overshoot_mass': _ratio_fields(row, 'overshoot_num', 'overshoot_den'),
        'priced_volume': _row_int(row, 'priced_volume'),
        'vwap_ticks': _ratio_fields(row, 'vwap_ticks_num', 'vwap_ticks_den'),
        'variance_ticks_squared': _ratio_fields(
            row, 'variance_ticks_squared_num', 'variance_ticks_squared_den'),
        'sd_ticks_approx': row.get('sd_ticks_approx'),
        'source_flat_bar_lost_mass': _row_int(row, 'source_flat_bar_lost_mass'),
        'concentration': _ratio_fields(row, 'concentration_num', 'concentration_den'),
        'dominance_margin': _ratio_fields(row, 'dominance_margin_num', 'dominance_margin_den'),
        'signed_delta': _row_int(row, 'signed_delta'),
        'absolute_delta_mass': _ratio_fields(row, 'absolute_delta_mass_num', 'absolute_delta_mass_den'),
        'side_overlap': _ratio_fields(row, 'side_overlap_num', 'side_overlap_den'),
        'side_total_variation': _ratio_fields(
            row, 'side_total_variation_num', 'side_total_variation_den'),
        'side_wasserstein': _ratio_fields(row, 'side_wasserstein_num', 'side_wasserstein_den'),
        'footprint_buy_imbalance_rows': row.get('footprint_buy_imbalance_rows'),
        'footprint_sell_imbalance_rows': row.get('footprint_sell_imbalance_rows'),
        'footprint_buy_stack_count': row.get('footprint_buy_stack_count'),
        'footprint_sell_stack_count': row.get('footprint_sell_stack_count'),
        'pin069_vwap': _ratio_fields(row, 'pin069_vwap_num', 'pin069_vwap_den'),
        'pin069_bar_volume': _row_int(row, 'pin069_bar_volume'),
        'unpriced_only_atoms': row.get('unpriced_only_atoms'),
        'input_cells': row.get('input_cells'),
        'sd_band_0_low_approx': row.get('sd_band_0_low_approx'),
        'sd_band_0_high_approx': row.get('sd_band_0_high_approx'),
        'sd_band_1_low_approx': row.get('sd_band_1_low_approx'),
        'sd_band_1_high_approx': row.get('sd_band_1_high_approx'),
        'sd_band_2_low_approx': row.get('sd_band_2_low_approx'),
        'sd_band_2_high_approx': row.get('sd_band_2_high_approx'),
        'sd_band_3_low_approx': row.get('sd_band_3_low_approx'),
        'sd_band_3_high_approx': row.get('sd_band_3_high_approx'),
        'percent_band_0_low': _ratio_fields(row, 'percent_band_0_low_num', 'percent_band_0_low_den'),
        'percent_band_0_high': _ratio_fields(row, 'percent_band_0_high_num', 'percent_band_0_high_den'),
        'percent_band_1_low': _ratio_fields(row, 'percent_band_1_low_num', 'percent_band_1_low_den'),
        'percent_band_1_high': _ratio_fields(row, 'percent_band_1_high_num', 'percent_band_1_high_den'),
        'percent_band_2_low': _ratio_fields(row, 'percent_band_2_low_num', 'percent_band_2_low_den'),
        'percent_band_2_high': _ratio_fields(row, 'percent_band_2_high_num', 'percent_band_2_high_den'),
        'q_1_20': _ratio_fields(row, 'q_1_20_num', 'q_1_20_den'),
        'q_1_4': _ratio_fields(row, 'q_1_4_num', 'q_1_4_den'),
        'q_1_2': _ratio_fields(row, 'q_1_2_num', 'q_1_2_den'),
        'q_3_4': _ratio_fields(row, 'q_3_4_num', 'q_3_4_den'),
        'q_19_20': _ratio_fields(row, 'q_19_20_num', 'q_19_20_den'),
        'weighted_median': _ratio_fields(row, 'weighted_median_num', 'weighted_median_den'),
        'mad': _ratio_fields(row, 'mad_num', 'mad_den'),
        'robust_scale': _ratio_fields(row, 'robust_scale_num', 'robust_scale_den'),
        'unpriced_buy': _row_int(row, 'unpriced_buy'),
        'unpriced_sell': _row_int(row, 'unpriced_sell'),
        'unpriced_unknown': _row_int(row, 'unpriced_unknown'),
        'low_overflow_buy': _row_int(row, 'low_overflow_buy'),
        'low_overflow_sell': _row_int(row, 'low_overflow_sell'),
        'low_overflow_unknown': _row_int(row, 'low_overflow_unknown'),
        'high_overflow_buy': _row_int(row, 'high_overflow_buy'),
        'high_overflow_sell': _row_int(row, 'high_overflow_sell'),
        'high_overflow_unknown': _row_int(row, 'high_overflow_unknown'),
    }


def _match_key(row):
    return (
        row.get('root'), row.get('anchor_variant'), row.get('cut_ns'),
        row.get('published_known_ns'), row.get('instrument_id'),
        row.get('contract_key'), row.get('canonical_raw_values_sha256') or row.get('source_path'),
    )


def accumulate_geometry_row(acc, row, *, collection, year):
    day = row.get('economic_date')
    complete = row.get('eligible_complete') is True
    status = 'eligible_complete' if complete else (row.get('geometry_status') or 'observed_partial')
    key = _gkey(
        group_kind='geometry', source_collection=collection, root=row.get('root'),
        year=year, stage=row.get('stage'), session=row.get('session'),
        anchor=row.get('anchor_variant'), variant=row.get('geometry_variant'),
        proxy=row.get('proxy_variant'), measurement_status=status, contrast=None,
        formation_minutes=row.get('formation_minutes'), latency_ns=None,
        horizon_kind=None, horizon_minutes=None,
    )
    store = acc['groups'][key]
    metrics = _geometry_metrics(row)
    for name, value in metrics.items():
        if name not in store:
            store[name] = _DateStore()
        store[name].add(day, value)
    sha = row.get('canonical_raw_values_sha256')
    if sha and day:
        acc['alias_dates'][sha].add(day)
    if row.get('selected_partition_member') is False or not _comparison_geometry_row(row):
        return
    match = _match_key(row)
    if row.get('proxy_variant') is None:
        acc['emitted_variants'][match].add(row.get('geometry_variant'))
        if complete:
            acc['geometry_index'][match][row.get('geometry_variant')] = (day, metrics, row)
            if row.get('geometry_variant') == BASELINE_VARIANT_ID:
                acc['exact_index'][match] = (day, metrics, row)
    else:
        acc['emitted_proxies'][match].add(row.get('proxy_variant'))
        if complete:
            acc['proxy_index'][(match, row.get('proxy_variant'))] = (day, metrics, row)
    _release_geometry_group(acc, collection, year, match)


def _pair_variants(acc, collection, year, match):
    variants = acc['geometry_index'].get(match) or {}
    for left_id, right_id, contrast in PAIRED_CONTRASTS:
        if left_id not in variants or right_id not in variants:
            continue
        day, left, left_row = variants[left_id]
        _, right, _right = variants[right_id]
        if left_row.get('eligible_complete') is not True:
            continue
        key = _gkey(
            group_kind='paired_geometry', source_collection=collection,
            root=left_row.get('root'), year=year, stage=left_row.get('stage'),
            session=left_row.get('session'), anchor=left_row.get('anchor_variant'),
            variant=f'{left_id}__{right_id}', proxy=None,
            measurement_status='eligible_complete', contrast=contrast,
            formation_minutes=left_row.get('formation_minutes'), latency_ns=None,
            horizon_kind=None, horizon_minutes=None,
        )
        store = acc['paired'][key]
        for name in (
            'physical_poc_ticks', 'physical_val_ticks', 'physical_vah_ticks',
            'va_width_physical_ticks', 'overshoot_mass',
        ):
            if left.get(name) is None or right.get(name) is None:
                continue
            if name not in store:
                store[name] = _DateStore()
            store[name].add(day, left[name] - right[name])


def _pair_exact_proxy(acc, collection, year, match, proxy, day, proxy_metrics, proxy_row):
    exact = acc['exact_index'].get(match)
    if exact is None or proxy is None:
        return
    _day, exact_metrics, exact_row = exact
    if proxy == exact_row.get('proxy_variant') or proxy == exact_row.get('geometry_variant'):
        return
    key = _gkey(
        group_kind='paired_proxy', source_collection=collection,
        root=exact_row.get('root'), year=year, stage=exact_row.get('stage'),
        session=exact_row.get('session'), anchor=exact_row.get('anchor_variant'),
        variant=BASELINE_VARIANT_ID, proxy=proxy,
        measurement_status='eligible_complete', contrast=f'exact_vs_{proxy}',
        formation_minutes=exact_row.get('formation_minutes'), latency_ns=None,
        horizon_kind=None, horizon_minutes=None,
    )
    store = acc['paired'][key]
    for name in ('physical_poc_ticks', 'physical_val_ticks', 'physical_vah_ticks', 'va_width_physical_ticks'):
        if exact_metrics.get(name) is None or proxy_metrics.get(name) is None:
            continue
        if name not in store:
            store[name] = _DateStore()
        store[name].add(day, exact_metrics[name] - proxy_metrics[name])


def _clear_geometry_indexes(acc, match):
    for key in [item for item in acc['proxy_index'] if item[0] == match]:
        acc['proxy_index'].pop(key, None)
    acc['geometry_index'].pop(match, None)
    acc['exact_index'].pop(match, None)
    acc['emitted_variants'].pop(match, None)
    acc['emitted_proxies'].pop(match, None)


def _pair_geometry_proxies(acc, collection, year, match):
    exact = acc['exact_index'].get(match)
    if exact is None:
        return
    day, _metrics, _row = exact
    for proxy in BAR_PROXY_VARIANTS:
        item = acc['proxy_index'].get((match, proxy))
        if item is None:
            continue
        _pair_exact_proxy(acc, collection, year, match, proxy, item[0], item[1], item[2])


def _release_geometry_group(acc, collection, year, match):
    if match in acc['paired_done']:
        _clear_geometry_indexes(acc, match)
        return
    variants_seen = acc['emitted_variants'].get(match) or set()
    proxies_seen = acc['emitted_proxies'].get(match) or set()
    if len(variants_seen) < len(FROZEN_GEOMETRY_VARIANTS):
        return
    if len(proxies_seen) < len(BAR_PROXY_VARIANTS):
        return
    _pair_variants(acc, collection, year, match)
    _pair_geometry_proxies(acc, collection, year, match)
    acc['paired_done'].add(match)
    _clear_geometry_indexes(acc, match)


def accumulate_tpo_row(acc, row, *, collection, year):
    day = row.get('economic_date')
    key = _gkey(
        group_kind='tpo', source_collection=collection, root=row.get('root'),
        year=year, stage=row.get('stage'), session=row.get('session'),
        anchor=row.get('anchor_variant'), variant=str(row.get('bracket_minutes')),
        proxy=row.get('representation'), measurement_status=row.get('tpo_status') or 'observed',
        contrast=None, formation_minutes=None, latency_ns=None,
        horizon_kind=None, horizon_minutes=None,
    )
    store = acc['groups'][key]
    for name, value in (
        ('visit_count', row.get('visit_count')),
        ('range_proxy_count', row.get('range_proxy_count')),
        ('single_print_count', None if row.get('final_single_print_rows') is None
         else len(row.get('final_single_print_rows') or ())),
        ('complete_brackets', row.get('complete_brackets')),
        ('ib30_complete', None if row.get('ib30_complete') is None else (1.0 if row.get('ib30_complete') else 0.0)),
        ('ib60_complete', None if row.get('ib60_complete') is None else (1.0 if row.get('ib60_complete') else 0.0)),
        ('ib30_high', row.get('ib30_high')),
        ('ib30_low', row.get('ib30_low')),
        ('ib60_high', row.get('ib60_high')),
        ('ib60_low', row.get('ib60_low')),
        ('low_tail_count', None if row.get('low_tail_rows') is None else len(row.get('low_tail_rows') or ())),
        ('high_tail_count', None if row.get('high_tail_rows') is None else len(row.get('high_tail_rows') or ())),
        ('provisional_single_print_count', None if row.get('provisional_single_print_rows') is None
         else len(row.get('provisional_single_print_rows') or ())),
        ('final_single_print_count', None if row.get('final_single_print_rows') is None
         else len(row.get('final_single_print_rows') or ())),
    ):
        if name not in store:
            store[name] = _DateStore()
        store[name].add(day, value)
    pair = (
        row.get('anchor_id'), row.get('cut_ns'), row.get('bracket_minutes'),
        row.get('instrument_id'),
    )
    acc['tpo_index'][pair][row.get('representation')] = row
    reps = acc['tpo_index'][pair]
    visits = reps.get('whole_trade_visits')
    proxy = reps.get('ohlc_range_proxy')
    if visits is None or proxy is None:
        return
    pkey = _gkey(
        group_kind='paired_tpo', source_collection=collection, root=visits.get('root'),
        year=year, stage=visits.get('stage'), session=visits.get('session'),
        anchor=visits.get('anchor_variant'), variant=str(visits.get('bracket_minutes')),
        proxy='visit_vs_range', measurement_status='observed',
        contrast='tpo_visit_minus_range_proxy',
        formation_minutes=None, latency_ns=None, horizon_kind=None, horizon_minutes=None,
    )
    store = acc['paired'][pkey]
    if 'visit_count' not in store:
        store['visit_count'] = _DateStore()
    left, right = visits.get('visit_count'), proxy.get('visit_count')
    if left is not None and right is not None:
        store['visit_count'].add(visits.get('economic_date'), left - right)
    acc['tpo_index'].pop(pair, None)


def accumulate_join_row(acc, row, *, collection, year):
    day = row.get('economic_date')
    status = row.get('join_status') or 'unknown'
    key = _gkey(
        group_kind='join', source_collection=collection, root=row.get('root'),
        year=year, stage=row.get('stage'), session=row.get('session'),
        anchor=row.get('anchor_variant'), variant=row.get('geometry_variant'),
        proxy=None, measurement_status=status, contrast=None,
        formation_minutes=row.get('formation_minutes'),
        latency_ns=row.get('latency_ns'),
        horizon_kind=row.get('horizon_kind'),
        horizon_minutes=row.get('horizon_minutes'),
    )
    intended_key = _gkey(
        group_kind='join', source_collection=collection, root=row.get('root'),
        year=year, stage=row.get('stage'), session=row.get('session'),
        anchor=row.get('anchor_variant'), variant=row.get('geometry_variant'),
        proxy=None, measurement_status='intended_link', contrast=None,
        formation_minutes=row.get('formation_minutes'),
        latency_ns=row.get('latency_ns'),
        horizon_kind=row.get('horizon_kind'),
        horizon_minutes=row.get('horizon_minutes'),
    )
    for group_key in (key, intended_key):
        store = acc['groups'][group_key]
        for name in (
            'poc_touch', 'val_touch', 'vah_touch', 'terminal_inside_va',
            'poc_traverse', 'val_traverse', 'vah_traverse',
            'terminal_outside_va', 'terminal_at_poc',
            'boundary_moving', 'price_crossing_frozen_va',
        ):
            value = row.get(name)
            if name not in store:
                store[name] = _DateStore()
            if value is None:
                continue
            store[name].add(day, 1.0 if value else 0.0)
        for name, flag in (
            ('no_event', status == 'no_event'),
            ('censored', status == 'censored'),
            ('missing', status in ('missing', 'no_label')),
            ('link_rows', True),
        ):
            if name not in store:
                store[name] = _DateStore()
            store[name].add(day, 1.0 if flag else 0.0)
        if 'future_input_known' not in store:
            store['future_input_known'] = _DateStore()
        if row.get('future_input_known') is not None:
            store['future_input_known'].add(day, 1.0 if row.get('future_input_known') else 0.0)
        if 'future_coverage_complete' not in store:
            store['future_coverage_complete'] = _DateStore()
        if row.get('future_coverage_complete') is not None:
            store['future_coverage_complete'].add(
                day, 1.0 if row.get('future_coverage_complete') else 0.0)
        future_metrics = {
            'future_poc': row.get('future_poc'),
            'future_val': row.get('future_val'),
            'future_vah': row.get('future_vah'),
            'future_low_overflow_buy': row.get('future_low_overflow_buy'),
            'future_low_overflow_sell': row.get('future_low_overflow_sell'),
            'future_low_overflow_unknown': row.get('future_low_overflow_unknown'),
            'future_high_overflow_buy': row.get('future_high_overflow_buy'),
            'future_high_overflow_sell': row.get('future_high_overflow_sell'),
            'future_high_overflow_unknown': row.get('future_high_overflow_unknown'),
            'future_low_overflow_unpriced': None,
            'future_high_overflow_unpriced': None,
            'future_unpriced_buy': row.get('future_unpriced_buy'),
            'future_unpriced_sell': row.get('future_unpriced_sell'),
            'future_unpriced_unknown': row.get('future_unpriced_unknown'),
            'future_transport': None if row.get('future_transport_overflow_unidentified') is True
            else _ratio_fields(row, 'future_transport_num', 'future_transport_den'),
        }
        if row.get('future_coverage_complete') is True:
            for name, value in future_metrics.items():
                if name not in store:
                    store[name] = _DateStore()
                store[name].add(day, value)
    future_partial = (
        row.get('future_coverage_complete') is not True
        and (
            row.get('future_input_known') is True
            or row.get('future_poc') is not None
            or row.get('future_val') is not None
        )
    )
    if future_partial:
        partial_key = _gkey(
            group_kind='join', source_collection=collection, root=row.get('root'),
            year=year, stage=row.get('stage'), session=row.get('session'),
            anchor=row.get('anchor_variant'), variant=row.get('geometry_variant'),
            proxy=None, measurement_status='future_observed_partial', contrast=None,
            formation_minutes=row.get('formation_minutes'),
            latency_ns=row.get('latency_ns'),
            horizon_kind=row.get('horizon_kind'),
            horizon_minutes=row.get('horizon_minutes'),
        )
        partial_store = acc['groups'][partial_key]
        for name, value in (
            ('future_poc', row.get('future_poc')),
            ('future_val', row.get('future_val')),
            ('future_vah', row.get('future_vah')),
            ('future_low_overflow_buy', row.get('future_low_overflow_buy')),
            ('future_low_overflow_sell', row.get('future_low_overflow_sell')),
            ('future_low_overflow_unknown', row.get('future_low_overflow_unknown')),
            ('future_high_overflow_buy', row.get('future_high_overflow_buy')),
            ('future_high_overflow_sell', row.get('future_high_overflow_sell')),
            ('future_high_overflow_unknown', row.get('future_high_overflow_unknown')),
            ('future_unpriced_buy', row.get('future_unpriced_buy')),
            ('future_unpriced_sell', row.get('future_unpriced_sell')),
            ('future_unpriced_unknown', row.get('future_unpriced_unknown')),
            (
                'future_transport',
                None if row.get('future_transport_overflow_unidentified') is True
                else _ratio_fields(row, 'future_transport_num', 'future_transport_den'),
            ),
        ):
            if name not in partial_store:
                partial_store[name] = _DateStore()
            partial_store[name].add(day, value)


def write_partition_groups(outputs, prefix, acc, *, stats, policy, collection, root, year, contract):
    leftover = [match for match in list(acc['geometry_index']) if match not in acc['paired_done']]
    for match in leftover:
        _pair_variants(acc, collection, year, match)
        _pair_geometry_proxies(acc, collection, year, match)
        acc['paired_done'].add(match)
        _clear_geometry_indexes(acc, match)
    np = _require_numpy()
    primary = (contract or {}).get('primary_population') or {}
    intended_by_stage = {}
    for stage in (*STAGE_ORDER, 'unassigned'):
        intended_by_stage[(root, year, stage)] = intended_date_universe(
            year, stage, root, policy,
            primary.get('start', '2020-01-01'), primary.get('end', '2026-09-04'),
        )
    finalized = _finalize_groups(acc['groups'], intended_by_stage=intended_by_stage, stats=stats, np=np)
    paired_out = _finalize_groups(acc['paired'], intended_by_stage=intended_by_stage, stats=stats, np=np)
    groups_ref = outputs.json(prefix + '-groups.json', {
        'kind': 'auction_flow_profile_group_statistics_v1',
        'groups': finalized, 'family_complete': False,
        'source_collection': collection, 'root': root, 'economic_year': year,
        'variant_ids': list(frozen_variant_ids()),
        'bar_proxy_variants': list(BAR_PROXY_VARIANTS),
    }, kind='auction_flow_profile_group_statistics_v1')
    paired_ref = outputs.json(prefix + '-paired.json', {
        'kind': 'auction_flow_profile_paired_contrasts_v1',
        'groups': paired_out, 'family_complete': False,
        'source_collection': collection, 'root': root, 'economic_year': year,
        'contrasts': [item[2] for item in PAIRED_CONTRASTS],
    }, kind='auction_flow_profile_paired_contrasts_v1')
    return groups_ref, paired_ref


def _authenticate_json_ref(reference, load_reference, *, kinds):
    if not isinstance(reference, dict) or type(reference.get('path')) is not str:
        raise IntegrityError('accepted partition lost a JSON reference')
    payload = load_reference(reference, maximum=JSON_LOAD_MAX)
    if not isinstance(payload, dict) or payload.get('kind') not in kinds:
        raise IntegrityError('accepted JSON reference failed authentication')
    path = Path(reference['path'])
    if (type(reference.get('size_bytes')) is not int or path.stat().st_size != reference['size_bytes']
            or file_digest(path) != reference['sha256']):
        raise IntegrityError('accepted JSON reference hash or size changed')
    return payload


def _authenticate_series_ref(series):
    if not isinstance(series, dict):
        raise IntegrityError('accepted partition lost a Parquet series reference')
    if series.get('roundtrip_exact') is not True:
        raise IntegrityError('accepted series lost its roundtrip certificate')
    if type(series.get('rows')) is not int or series['rows'] < 0:
        raise IntegrityError('accepted series lost its row-count certificate')
    files = series.get('files')
    if not isinstance(files, list):
        raise IntegrityError('accepted series lost its file certificates')
    counted = 0
    sizes = 0
    for reference in files:
        if not isinstance(reference, dict) or type(reference.get('path')) is not str:
            raise IntegrityError('accepted series file lost its path certificate')
        path = Path(reference['path'])
        if type(reference.get('size_bytes')) is not int or path.stat().st_size != reference['size_bytes']:
            raise IntegrityError('accepted series file size certificate changed')
        if type(reference.get('sha256')) is not str or file_digest(path) != reference['sha256']:
            raise IntegrityError('accepted series file hash certificate changed')
        if type(reference.get('rows')) is int:
            counted += reference['rows']
        sizes += int(reference['size_bytes'])
    if type(series.get('serialized_bytes')) is int and series['serialized_bytes'] != sizes:
        raise IntegrityError('accepted series serialized-byte certificate changed')
    if counted and counted != series['rows']:
        raise IntegrityError('accepted series row-count certificate does not match file rows')
    if type(series.get('schema')) is not str and series.get('schema') is not None:
        raise IntegrityError('accepted series schema certificate is not text')
    return series['rows']


def authenticate_reused_partition(part, load_reference):
    if not isinstance(part, dict) or part.get('kind') != PARTITION_KIND:
        raise IntegrityError('accepted partition is not a profile reference partition')
    if part.get('passed') is not True:
        raise IntegrityError('accepted partition is not a passed profile partition')
    completeness = _authenticate_json_ref(
        part.get('completeness'), load_reference,
        kinds={'auction_flow_profile_partition_completeness_v1'},
    )
    if part.get('groups') is None or part.get('paired') is None:
        raise IntegrityError('accepted partition lost finalized group payloads')
    expected_impl = consumer_implementation_identity()
    got_impl = (part.get('implementation') or {}).get('consumer_files')
    if got_impl != expected_impl:
        raise IntegrityError('accepted partition consumer implementation hash changed')
    groups = _authenticate_json_ref(
        part.get('groups'), load_reference,
        kinds={'auction_flow_profile_group_statistics_v1'},
    )
    paired = _authenticate_json_ref(
        part.get('paired'), load_reference,
        kinds={'auction_flow_profile_paired_contrasts_v1'},
    )
    del groups
    del paired
    for name in ('geometry', 'tpo', 'joins', 'cells'):
        _authenticate_series_ref(part.get(name))
    for ref in part.get('support_refs') or part.get('source_refs') or ():
        measurement = ref.get('measurement') if isinstance(ref, dict) else None
        if isinstance(measurement, dict) and measurement.get('sha256'):
            path = measurement.get('path')
            if type(path) is not str or not path:
                raise IntegrityError('accepted partition neighbor or member measurement lost its path')
            if file_digest(Path(path)) != measurement['sha256']:
                raise IntegrityError('accepted partition neighbor or member measurement hash changed')
        series = ref.get('series') if isinstance(ref, dict) else None
        files = (series or {}).get('files') or []
        for item in files:
            if isinstance(item, dict) and item.get('path') and item.get('sha256'):
                if file_digest(Path(item['path'])) != item['sha256']:
                    raise IntegrityError('accepted partition neighbor series hash changed')
    return {
        'part': part, 'completeness': completeness,
        'groups_ref': part.get('groups'), 'paired_ref': part.get('paired'),
    }


def iter_authenticated_profile_groups(manifest, load_reference, *, role='groups'):
    """Yield one partition's groups at a time from a compact group/paired manifest."""
    payload_kind = (
        'auction_flow_profile_group_statistics_v1' if role == 'groups'
        else 'auction_flow_profile_paired_contrasts_v1'
    )
    refs = None
    if isinstance(manifest, dict):
        if role == 'groups':
            refs = manifest.get('partition_groups')
        else:
            refs = manifest.get('partition_paired')
        if refs is None and manifest.get('kind') == payload_kind:
            for group in manifest.get('groups') or ():
                yield group
            return
    for ref in refs or ():
        payload = _authenticate_json_ref(ref, load_reference, kinds={payload_kind})
        try:
            for group in payload.get('groups') or ():
                yield group
        finally:
            del payload


def reconstruct_profile_groups(manifest, load_reference, *, role='groups'):
    return list(iter_authenticated_profile_groups(manifest, load_reference, role=role))


def project_profile_resources(measurements, *, remaining_source_bytes, remaining_atoms,
                              remaining_geometry_rows, margin=1.5):
    if not measurements:
        raise IntegrityError('resource projection requires a measured partition')
    if any(
        item.get('source_bytes', 0) < 0 or item.get('atoms', 0) < 0 or item.get('geometry_rows', 0) < 0
        for item in measurements
    ):
        raise IntegrityError('resource projection requires complete measured work')
    nonempty = [item for item in measurements if item.get('atoms', 0) > 0]
    if not nonempty:
        raise IntegrityError('resource projection needs at least one observed atom partition')
    cpu_per_byte = max(
        item['cpu_seconds'] / item['source_bytes'] for item in nonempty if item.get('source_bytes')
    ) if any(item.get('source_bytes') for item in nonempty) else 0.0
    cpu_per_atom = max(item['cpu_seconds'] / item['atoms'] for item in nonempty)
    cpu_per_geo = max(
        item['cpu_seconds'] / item['geometry_rows'] for item in nonempty if item.get('geometry_rows')
    ) if any(item.get('geometry_rows') for item in nonempty) else cpu_per_atom
    out_per_atom = max(item['output_bytes'] / max(item['atoms'], 1) for item in nonempty)
    cpu = margin * max(
        cpu_per_byte * remaining_source_bytes,
        cpu_per_atom * remaining_atoms,
        cpu_per_geo * remaining_geometry_rows,
    )
    output = int(margin * out_per_atom * remaining_atoms) + 16 * 1024 ** 2
    return {
        'method': (
            'maximum measured CPU per source byte, per atom and per geometry row; '
            'larger estimate; margin 1.5. Not a per-trade-only fantasy.'
        ),
        'margin': margin,
        'cpu_seconds_with_margin': cpu,
        'output_bytes_with_margin': output,
        'remaining_source_bytes': remaining_source_bytes,
        'remaining_atoms': remaining_atoms,
        'remaining_geometry_rows': remaining_geometry_rows,
    }


def _require_numpy():
    import numpy as np
    if getattr(np, '__version__', None) != '2.3.3':
        raise ContractError('profile statistics require the pinned NumPy 2.3.3 provider')
    return np


def _require_pyarrow():
    import pyarrow as pa
    if getattr(pa, '__version__', None) != '25.0.1':
        raise ContractError('profile statistics require the pinned PyArrow 25.0.1 provider')
    return pa


def _readable_mean(value):
    if isinstance(value, dict):
        return value.get('estimate')
    return value


def _append_report_metric_rows(lines, group):
    metrics = group.get('metrics') or {}
    prefix = (
        f'| {group.get("source_collection")} | {group.get("root")} | {group.get("year")} | '
        f'{group.get("stage")} | {group.get("session")} | {group.get("anchor")} | '
        f'{group.get("variant")} | {group.get("proxy")} | {group.get("measurement_status")} | '
        f'{group.get("contrast")} | {group.get("formation_minutes")} | {group.get("latency_ns")} | '
        f'{group.get("horizon_kind")}/{group.get("horizon_minutes")}'
    )
    if not metrics:
        lines.append(f'{prefix} |  |  |  |  |  |  |  |')
        return
    for name, payload in metrics.items():
        payload = payload or {}
        support = payload.get('support') or {}
        lines.append(
            f'{prefix} | {name} | {payload.get("unit")} | {_readable_mean(payload.get("date_mean"))} | '
            f'{payload.get("event_mean")} | {payload.get("eligible_independent_dates")} | '
            f'{payload.get("eligible_observations")} | {payload.get("undefined")} | '
            f'{support.get("reasons") or payload.get("undefined")} | '
            f'{json.dumps(payload.get("bootstrap"), sort_keys=True)} | '
            f'{json.dumps(payload.get("raw_quantiles"), sort_keys=True)} |'
        )


def _markdown_report(*, completeness, population, cpu, output_bytes, reused,
                     recomputed, selected, all_keys, refs, measurements,
                     load_reference=None, group_manifest=None, paired_manifest=None, stream):
    lines = [
        '# Auction/flow profile reference statistics',
        '',
        'This report is descriptive reconstruction and comparison evidence. It does not',
        'complete the family, fit Context, or score Location quality.',
        '',
        f'- Population kind: `{population.get("kind")}`',
        f'- Processed partitions: {len(selected)} of {len(all_keys)} declared',
        f'- Reused authenticated partitions: {reused}',
        f'- Newly computed partitions: {recomputed}',
        f'- CPU seconds (this reducer): {cpu:.6f}',
        f'- Output bytes (this reducer): {output_bytes}',
        f'- Units scanned: {completeness.get("units_scanned")}',
        f'- Units unavailable (retained): {completeness.get("units_unavailable")}',
        f'- Atoms matched: {completeness.get("atoms_matched")}',
        f'- Geometry emitted: {completeness.get("geometry_emitted")}',
        f'- Geometry complete / partial / null: '
        f'{completeness.get("geometry_complete")} / {completeness.get("geometry_partial")} / {completeness.get("geometry_null")}',
        f'- TPO emitted / failed: {completeness.get("tpo_emitted")} / {completeness.get("tpo_failed")}',
        f'- Joins emitted / missing / censored: '
        f'{completeness.get("joins_emitted")} / {completeness.get("joins_missing")} / {completeness.get("joins_censored")}',
        '',
        '## Frozen variant set',
        '',
        'Completed anchors emit all 14 named geometry variants and all 6 bar proxies.',
        'Developing RTH / 18-17 and rolling 5/15/60/240 emit the one-tick 70 percent baseline.',
        '',
    ]
    for spec in FROZEN_GEOMETRY_VARIANTS:
        lines.append(
            f'- `{spec["id"]}`: fraction {spec["fraction"][0]}/{spec["fraction"][1]}, '
            f'width {spec["width"]}, origin {spec["origin"]}, '
            f'poc_tie {spec["poc_tie"]}, value_tie {spec["value_tie"]}, '
            f'smooth {spec["smoothing_scale"]}'
        )
    lines.extend(['', '## Bar proxies', ''])
    for name in BAR_PROXY_VARIANTS:
        lines.append(f'- `{name}`')
    lines.extend(['', '## Partition measurements', ''])
    lines.append('| collection | root | year | cpu | atoms | geometry | source_bytes | output |')
    lines.append('|---|---|---|---|---|---|---|---|')
    for item in measurements:
        key = item.get('partition_key') or [None, None, None]
        lines.append(
            f'| {key[0]} | {key[1]} | {key[2]} | {item.get("cpu_seconds")} | '
            f'{item.get("atoms")} | {item.get("geometry_rows")} | '
            f'{item.get("source_bytes")} | {item.get("output_bytes")} |'
        )
    lines.extend(['', '## Group metrics', ''])
    lines.append(
        '`refs.groups` is an `auction_flow_profile_group_manifest_v1` of per-partition '
        'group references. Reconstruct with `iter_authenticated_profile_groups`.'
    )
    lines.append('')
    lines.append(
        '| collection | root | year | stage | session | anchor | variant | proxy | '
        'status | contrast | formation | latency | horizon | metric | unit | '
        'date_mean | event_mean | dates | events | undefined | support | bootstrap | raw quantiles |'
    )
    lines.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    stream.write(('\n'.join(lines) + '\n').encode())
    lines.clear()
    if group_manifest is not None and load_reference is not None:
        for group in iter_authenticated_profile_groups(group_manifest, load_reference, role='groups'):
            _append_report_metric_rows(lines, group)
            stream.write(('\n'.join(lines) + '\n').encode())
            lines.clear()
        for group in iter_authenticated_profile_groups(paired_manifest or {}, load_reference, role='paired'):
            _append_report_metric_rows(lines, group)
            stream.write(('\n'.join(lines) + '\n').encode())
            lines.clear()
    lines.extend(['', '## Artifact references', ''])
    for name, value in refs.items():
        lines.append(f'- `{name}`: `{value}`')
    lines.append('')
    stream.write(('\n'.join(lines) + '\n').encode())


def run_profile_statistics(*, population, window_population, contract, outputs, load_reference,
                           selected_partition_keys=None, accepted_partitions=None):
    """Reconstruct geometry then reduce collection/root/year groups.

    ``population`` and ``window_population`` are already-authenticated payloads.
    This helper never reloads those JSON objects and never spawns workers.
    ``refs['groups']`` is an ``auction_flow_profile_group_manifest_v1`` of
    per-partition group references. Reconstruct with
    ``iter_authenticated_profile_groups`` / ``reconstruct_profile_groups``.
    """
    if not isinstance(outputs, BoundedOutputs) or not callable(load_reference):
        raise ContractError('bounded outputs and authenticated reference loader required')
    rec = _mapping(population, what='population')
    if rec.get('kind') != POPULATION_KIND:
        raise IntegrityError('authenticated auction_flow_observation_population_v1 required')
    windows = _mapping(window_population, what='window_population')
    if windows.get('kind') != WINDOW_POPULATION_KIND:
        raise IntegrityError('authenticated auction_flow_window_population_v1 required')
    frozen, stats, policy, collections = _require_contract(contract, population=rec)
    calendar = _load_calendar(frozen, load_reference)
    started, wall_started = time_mod.process_time(), time_mod.monotonic()
    plan = profile_partition_plan(rec, frozen)
    if selected_partition_keys is None:
        selected_keys = list(plan['keys'])
        subset = False
    else:
        if not isinstance(selected_partition_keys, list):
            raise IntegrityError('selected_partition_keys must be a list of partition keys')
        selected_keys = [decode_profile_partition_key(key) for key in selected_partition_keys]
        known = set(plan['keys'])
        if any(key not in known for key in selected_keys):
            raise IntegrityError('selected_partition_keys are not members of the authenticated population')
        if len(set(selected_keys)) != len(selected_keys):
            raise IntegrityError('selected_partition_keys contain a duplicate')
        subset = selected_keys != list(plan['keys'])
    accepted = {}
    incoming = list(frozen.get('accepted_partitions') or [])
    if accepted_partitions:
        incoming.extend(accepted_partitions)
    for ref in incoming:
        row = load_reference(ref, maximum=JSON_LOAD_MAX)
        accepted[row['identity']] = (ref, row)
    total = empty_completeness()
    partition_refs, geometry_refs, tpo_refs, join_refs, cell_refs = [], [], [], [], []
    completeness_refs, group_refs, paired_refs = [], [], []
    reused, recomputed, measurements = 0, 0, []
    np = pa = None
    window_units = windows.get('units') or []
    if not isinstance(window_units, list):
        raise IntegrityError('window population lost its unit summaries')
    for ordinal, key in enumerate(selected_keys):
        collection, root, year = key
        members = plan['members'][key]
        neighbors = neighbor_units(plan, key, collections=collections)
        source_refs = (
            profile_partition_source_refs(members, role='selected')
            + profile_partition_source_refs(neighbors, role='support')
        )
        paths = {_unit_path(unit) for unit in members} | {_unit_path(unit) for unit in neighbors}
        window_refs = window_unit_refs(window_units, paths=paths)
        identity = profile_partition_identity(
            frozen, collection=collection, root=root, year=year,
            source_refs=source_refs, window_refs=window_refs,
        )
        if identity in accepted and accepted[identity][1].get('passed') is True:
            ref, part = accepted[identity]
            reused_payload = authenticate_reused_partition(part, load_reference)
            reused += 1
            completeness_payload = reused_payload['completeness']
            group_refs.append(part['groups'])
            paired_refs.append(part['paired'])
            for name, value in completeness_payload.items():
                if name in total and isinstance(total[name], int) and isinstance(value, int):
                    total[name] += value
            if completeness_payload.get('unavailable_units'):
                total['unavailable_units'].extend(completeness_payload['unavailable_units'])
            del reused_payload
        else:
            if np is None:
                np, pa = _require_numpy(), _require_pyarrow()
            ref, part, measurement = compute_profile_partition(
                key=key, members=members, neighbors=neighbors, identity=identity,
                source_refs=source_refs, contract=frozen, calendar=calendar,
                policy=policy, window_units=window_units, outputs=outputs,
                ordinal=ordinal, pa=pa, stats=stats, load_reference=load_reference,
                window_refs=window_refs,
            )
            recomputed += 1
            measurements.append({**measurement, 'partition_key': encode_profile_partition_key(key)})
            if part.get('groups') is None or part.get('paired') is None:
                raise IntegrityError('computed partition did not store finalized group payloads')
            groups_payload = _authenticate_json_ref(
                part['groups'], load_reference,
                kinds={'auction_flow_profile_group_statistics_v1'},
            )
            paired_payload = _authenticate_json_ref(
                part['paired'], load_reference,
                kinds={'auction_flow_profile_paired_contrasts_v1'},
            )
            del groups_payload
            del paired_payload
            group_refs.append(part['groups'])
            paired_refs.append(part['paired'])
            counts = part.get('completeness_counts') or {}
            for name in total:
                if name in counts and isinstance(counts[name], int):
                    total[name] += counts[name]
            if counts.get('unavailable_units'):
                total['unavailable_units'].extend(counts['unavailable_units'])
        partition_refs.append(ref)
        geometry_refs.append(part['geometry'])
        tpo_refs.append(part['tpo'])
        join_refs.append(part['joins'])
        cell_refs.append(part.get('cells'))
        completeness_refs.append(part['completeness'])
    if np is None:
        np, pa = _require_numpy(), _require_pyarrow()
    group_manifest = {
        'kind': GROUPS_MANIFEST_KIND,
        'partition_groups': group_refs,
        'family_complete': False,
        'manifest_kind': 'per_partition_group_refs',
        'variant_ids': list(frozen_variant_ids()),
        'bar_proxy_variants': list(BAR_PROXY_VARIANTS),
    }
    paired_manifest = {
        'kind': PAIRED_MANIFEST_KIND,
        'partition_paired': paired_refs,
        'family_complete': False,
        'manifest_kind': 'per_partition_paired_refs',
        'contrasts': [item[2] for item in PAIRED_CONTRASTS],
    }
    group_ref = outputs.json('profile-groups.json', group_manifest, kind=GROUPS_MANIFEST_KIND)
    paired_ref = outputs.json('profile-paired.json', paired_manifest, kind=PAIRED_MANIFEST_KIND)
    completeness_out = {
        **total,
        'family_complete': False,
        'selected_partition_subset': subset,
        'declared_partitions': len(plan['keys']),
        'selected_partitions': len(selected_keys),
        'unavailable_units': total.get('unavailable_units') or [],
    }
    completeness_ref = outputs.json(
        'profile-statistics-completeness.json', completeness_out,
        kind='auction_flow_profile_completeness_v1',
    )
    refs = {
        'partitions': partition_refs, 'geometry': geometry_refs, 'tpo': tpo_refs,
        'joins': join_refs, 'cells': cell_refs, 'partition_completeness': completeness_refs,
        'groups': group_ref, 'paired': paired_ref, 'completeness': completeness_ref,
    }
    cpu = time_mod.process_time() - started
    wall = time_mod.monotonic() - wall_started
    with outputs.create('profile-reference-statistics-report.md') as stream:
        _markdown_report(
            completeness=total, population=rec,
            cpu=cpu, output_bytes=outputs.written, reused=reused, recomputed=recomputed,
            selected=selected_keys, all_keys=plan['keys'], refs=refs, measurements=measurements,
            load_reference=load_reference, group_manifest=group_manifest,
            paired_manifest=paired_manifest, stream=stream,
        )
    cpu = time_mod.process_time() - started
    wall = time_mod.monotonic() - wall_started
    report_ref = outputs.reference(
        'profile-reference-statistics-report.md', kind='auction_flow_profile_statistics_report')
    refs['report'] = report_ref
    counts = {
        'declared_partitions': len(plan['keys']),
        'selected_partitions': len(selected_keys),
        'reused_partitions': reused,
        'new_partitions': recomputed,
        'units_scanned': total.get('units_scanned', 0),
        'units_selected': total.get('units_selected', 0),
        'units_neighbor': total.get('units_neighbor', 0),
        'units_unavailable': total.get('units_unavailable', 0),
        'atoms_scanned': total.get('atoms_scanned', 0),
        'atoms_matched': total.get('atoms_matched', 0),
        'geometry_emitted': total.get('geometry_emitted', 0),
        'geometry_complete': total.get('geometry_complete', 0),
        'geometry_partial': total.get('geometry_partial', 0),
        'geometry_null': total.get('geometry_null', 0),
        'tpo_emitted': total.get('tpo_emitted', 0),
        'tpo_failed': total.get('tpo_failed', 0),
        'joins_emitted': total.get('joins_emitted', 0),
        'joins_missing': total.get('joins_missing', 0),
        'joins_censored': total.get('joins_censored', 0),
        'link_rows': total.get('link_rows', 0),
        'cell_rows': total.get('cell_rows', 0),
    }
    summary = {
        'kind': KIND, 'version': VERSION, 'passed': True, 'family_complete': False,
        'complete_family_statistics': False, 'all_family_validation_complete': False,
        'full_profile_population_reduced': (not subset) and len(selected_keys) == len(plan['keys']),
        'selected_partition_subset': subset, 'counts': counts,
        'partition_measurements': measurements, 'cpu_seconds': cpu, 'wall_seconds': wall,
        'output_bytes': outputs.written, 'reused_partitions': reused, 'new_partitions': recomputed,
        'partition_keys': [encode_profile_partition_key(key) for key in selected_keys],
        'refs': refs,
    }
    summary_ref = outputs.json('profile-statistics-summary.json', summary, kind=KIND)
    summary['refs']['summary'] = summary_ref
    _ = labeled_date_and_event_means
    _ = write_series_table
    _ = timedelta
    return summary


__all__ = [
    'KIND', 'accumulate_geometry_row', 'accumulate_join_row', 'accumulate_tpo_row',
    'authenticate_reused_partition', 'decode_profile_partition_key',
    'derive_source_collections', 'encode_profile_partition_key',
    'GROUPS_MANIFEST_KIND', 'iter_authenticated_profile_groups',
    'neighbor_units', 'new_partition_accumulators', 'PAIRED_MANIFEST_KIND',
    'profile_partition_identity',
    'profile_partition_plan', 'profile_partition_source_refs',
    'project_profile_resources', 'reconstruct_profile_groups',
    'run_profile_statistics',
    'scientific_contract_definition', 'write_partition_groups',
]
