"""Full-population profile/reference statistics over reconstructed geometry.

Root owns registration, review, integration and registered execution. This
reducer never spawns processes. It reuses accepted partitions only after
authenticating every consumer file hash and the scientific identity.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import math
import time as time_mod

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import digest, file_digest
from trading_research.research.auction_flow_core_statistics import (
    ExplicitCashSessions, FROZEN_STAGE_POLICY, REQUIRED_CASH_CALENDAR_REFERENCE,
    STAGE_ORDER, labeled_date_and_event_means,
)
from trading_research.research.auction_flow_profile_reference import (
    BAR_PROXY_VARIANTS, BASELINE_VARIANT_ID, FROZEN_CONTRACT_KIND,
    FROZEN_GEOMETRY_VARIANTS, KIND as PARTITION_KIND, LATENCY_NS,
    POPULATION_KIND, ProfileCashAdapter, QUANTILE_LEVELS, VERSION,
    WINDOW_POPULATION_KIND, compute_profile_partition, empty_completeness,
    frozen_variant_ids, require_frozen_variants, write_series_table,
)
from trading_research.research.auction_flow_storage import BoundedOutputs, read_series_tables
from trading_research.research.auction_flow_window_statistics import intended_date_universe
from trading_research.research.date_statistics import _moving_weights, observed_date_statistics


KIND = 'auction_flow_profile_reference_statistics_result_v1'
JSON_LOAD_MAX = 128 * 1024 ** 2
OPERATIONAL_CONTRACT_FIELDS = (
    'phase', 'pilot_source_paths', 'accepted_partitions', 'selected_partition_keys',
    'accepted_pilot_execution', 'accepted_pilot_worker', 'accepted_consumer_files',
    'parallel_execution', 'cash_session_table',
)
_GFIELDS = (
    'group_kind', 'source_collection', 'root', 'year', 'stage', 'session',
    'anchor', 'variant', 'proxy', 'measurement_status', 'contrast',
)
PAIRED_CONTRASTS = (
    ('source-one-tick-value-17/25', 'source-one-tick-value-7/10', 'fraction_68_vs_70'),
    ('value70-expansion-tie-lower', 'source-one-tick-value-7/10', 'value_tie_lower_vs_upper'),
    ('value70-expansion-tie-both', 'source-one-tick-value-7/10', 'value_tie_both_vs_upper'),
    ('value70-poc-tie-upper', 'source-one-tick-value-7/10', 'poc_tie_upper_vs_lower'),
    ('value70-width2-origin0', 'source-one-tick-value-7/10', 'width2_origin0_vs_one_tick'),
    ('value70-width2-origin1', 'value70-width2-origin0', 'width2_origin1_vs_origin0'),
    ('value70-width4-origin0', 'source-one-tick-value-7/10', 'width4_origin0_vs_one_tick'),
    ('value70-width8-origin0', 'source-one-tick-value-7/10', 'width8_origin0_vs_one_tick'),
    ('value70-triangular-scale1', 'source-one-tick-value-7/10', 'triangular1_vs_unsmoothed'),
    ('value70-triangular-scale2', 'source-one-tick-value-7/10', 'triangular2_vs_unsmoothed'),
    ('value70-triangular-scale4', 'source-one-tick-value-7/10', 'triangular4_vs_unsmoothed'),
)
METRIC_UNITS = {
    'scalar_poc': 'quarter_point_ticks',
    'val_row': 'quarter_point_ticks',
    'vah_row': 'quarter_point_ticks',
    'va_width_ticks': 'quarter_point_ticks',
    'poc_count': 'count',
    'overshoot_mass': 'contract_fractions',
    'priced_volume': 'contracts',
    'vwap_ticks': 'quarter_point_ticks',
    'variance_ticks_squared': 'ticks_squared',
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


def profile_partition_plan(population, contract):
    """Map observation units onto (collection, root, economic_year).

    Neighbor/past support may be read later without counting those units as
    selected keys. Weekly and monthly collections stay separate.
    """
    rec = _mapping(population, what='population')
    if rec.get('kind') != POPULATION_KIND:
        raise IntegrityError('authenticated auction_flow_observation_population_v1 required')
    units = rec.get('units')
    if not isinstance(units, list):
        raise IntegrityError('observation population lost its unit summaries')
    collections = contract.get('source_collections')
    if not isinstance(collections, dict) or not collections:
        raise IntegrityError('frozen source_collections are required')
    partitions = defaultdict(list)
    unavailable = 0
    for unit in units:
        path = _unit_path(unit)
        root = _unit_root(unit)
        if type(path) is not str or type(root) is not str:
            raise IntegrityError('observation unit lost source path or root')
        if path not in collections:
            raise IntegrityError('frozen source collection map is incomplete')
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
    }


def neighbor_units(plan, key, *, collections):
    """Same-collection adjacent files for lookback/carry. Other collections stay out."""
    collection, root, year = key
    members = plan['members'][key]
    selected = {_unit_identity_key(unit) for unit in members}
    if not members:
        return []
    lookback = 240 * 60 * 1_000_000_000
    lookahead = 60 * 60 * 1_000_000_000
    span_start = min(_unit_window_ns(unit)[0] for unit in members) - lookback
    span_end = max(_unit_window_ns(unit)[1] for unit in members) + lookahead
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


def profile_partition_source_refs(members):
    refs = []
    for unit in members:
        series = unit.get('series') or {}
        measurement = unit.get('measurement') or (unit.get('original_refs') or {}).get('measurement') or {}
        refs.append({
            'source_path': _unit_path(unit),
            'root': _unit_root(unit),
            'source_window_start_ns': _unit_window_ns(unit)[0],
            'source_window_end_ns': _unit_window_ns(unit)[1],
            'atomic_rows': unit.get('atomic_rows'),
            'series': {
                'rows': series.get('rows'),
                'schema': series.get('schema'),
                'files': [
                    (item.get('sha256'), item.get('rows'))
                    for item in series.get('files') or []
                ],
            },
            'measurement': {
                'sha256': measurement.get('sha256'),
                'uncompressed_sha256': measurement.get('uncompressed_sha256'),
                'size_bytes': measurement.get('size_bytes'),
            },
            'receipt': unit.get('receipt') or (unit.get('original_refs') or {}).get('receipt_reference'),
        })
    return refs


def profile_partition_identity(contract, *, collection, root, year, source_refs, window_refs):
    return digest({
        'definition': scientific_contract_definition(contract),
        'collection': collection,
        'root': root,
        'economic_year': year,
        'source_refs': source_refs,
        'window_refs': window_refs,
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


def _require_contract(contract):
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
    collections = rec.get('source_collections')
    if not isinstance(collections, dict) or not collections:
        raise IntegrityError('frozen source_collections are required')
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
        self.raw = []

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
                metrics = {
                    name: _undefined_metric(unit=_metric_unit(name)) for name in stores
                }
                finalized.append({**_gmeta(key), 'metrics': metrics, 'intended_dates': intended,
                                 'intended_date_count': 0, 'family_complete': False})
            continue
        weights, starts = _moving_weights(
            np, len(intended), seed=seed, block_length=block, replicates=replicates)
        state = (np, weights, starts)
        for key in sorted(keys, key=lambda item: tuple(str(part) for part in item)):
            stores = groups[key]
            names = tuple(stores)
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


def _overshoot_value(row):
    num = row.get('overshoot_num')
    den = row.get('overshoot_den')
    if num is None or den in (None, 0):
        return None
    return float(num) / float(den)


def _vwap_value(row):
    num = row.get('vwap_ticks_num')
    den = row.get('vwap_ticks_den')
    if num is None or den in (None, 0):
        return None
    return float(num) / float(den)


def _variance_value(row):
    num = row.get('variance_ticks_squared_num')
    den = row.get('variance_ticks_squared_den')
    if num is None or den in (None, 0):
        return None
    return float(num) / float(den)


def _geometry_metrics(row):
    return {
        'scalar_poc': row.get('scalar_poc'),
        'val_row': row.get('val_row'),
        'vah_row': row.get('vah_row'),
        'va_width_ticks': row.get('va_width_ticks'),
        'poc_count': row.get('poc_count'),
        'overshoot_mass': _overshoot_value(row),
        'priced_volume': row.get('priced_volume'),
        'vwap_ticks': _vwap_value(row),
        'variance_ticks_squared': _variance_value(row),
        'source_flat_bar_lost_mass': row.get('source_flat_bar_lost_mass'),
    }


def _accumulate_geometry(groups, paired, rows, *, collection, year, alias_dates):
    by_pair = defaultdict(dict)
    for row in rows:
        day = row.get('economic_date')
        status = row.get('geometry_status') or 'unknown'
        key = _gkey(
            group_kind='geometry', source_collection=collection, root=row.get('root'),
            year=year, stage=row.get('stage'), session=row.get('session'),
            anchor=row.get('anchor_variant'), variant=row.get('geometry_variant'),
            proxy=row.get('proxy_variant'), measurement_status=status, contrast=None,
        )
        store = groups[key]
        metrics = _geometry_metrics(row)
        for name, value in metrics.items():
            if name not in store:
                store[name] = _DateStore()
            if value is not None:
                store[name].add(day, value)
        sha = row.get('canonical_raw_values_sha256')
        if sha and day:
            alias_dates[sha].add(day)
        pair_id = (
            row.get('root'), row.get('anchor_id'), row.get('cut_ns'),
            row.get('instrument_id'), row.get('contract_key'), row.get('source_path'),
            row.get('proxy_variant'),
        )
        by_pair[pair_id][row.get('geometry_variant')] = (day, metrics, row)
    for pair_id, variants in by_pair.items():
        for left_id, right_id, contrast in PAIRED_CONTRASTS:
            if left_id not in variants or right_id not in variants:
                continue
            day, left, left_row = variants[left_id]
            _, right, _right_row = variants[right_id]
            key = _gkey(
                group_kind='paired_geometry', source_collection=collection,
                root=left_row.get('root'), year=year, stage=left_row.get('stage'),
                session=left_row.get('session'), anchor=left_row.get('anchor_variant'),
                variant=f'{left_id}__{right_id}', proxy=left_row.get('proxy_variant'),
                measurement_status=left_row.get('geometry_status'), contrast=contrast,
            )
            store = paired[key]
            for name in ('scalar_poc', 'val_row', 'vah_row', 'va_width_ticks', 'overshoot_mass'):
                if left.get(name) is None or right.get(name) is None:
                    continue
                if name not in store:
                    store[name] = _DateStore()
                store[name].add(day, left[name] - right[name])
        baseline = variants.get(BASELINE_VARIANT_ID)
        if baseline is None:
            continue
        day, exact, exact_row = baseline
        for proxy in BAR_PROXY_VARIANTS:
            proxy_key = (
                exact_row.get('root'), exact_row.get('anchor_id'), exact_row.get('cut_ns'),
                exact_row.get('instrument_id'), exact_row.get('contract_key'),
                exact_row.get('source_path'), proxy,
            )
            if proxy_key not in by_pair or BASELINE_VARIANT_ID not in by_pair[proxy_key]:
                continue
            _, proxy_metrics, proxy_row = by_pair[proxy_key][BASELINE_VARIANT_ID]
            key = _gkey(
                group_kind='paired_proxy', source_collection=collection,
                root=exact_row.get('root'), year=year, stage=exact_row.get('stage'),
                session=exact_row.get('session'), anchor=exact_row.get('anchor_variant'),
                variant=BASELINE_VARIANT_ID, proxy=proxy,
                measurement_status=proxy_row.get('geometry_status'),
                contrast=f'exact_vs_{proxy}',
            )
            store = paired[key]
            for name in ('scalar_poc', 'val_row', 'vah_row', 'va_width_ticks'):
                if exact.get(name) is None or proxy_metrics.get(name) is None:
                    continue
                if name not in store:
                    store[name] = _DateStore()
                store[name].add(day, exact[name] - proxy_metrics[name])


def _accumulate_tpo(groups, rows, *, collection, year):
    by_pair = defaultdict(dict)
    for row in rows:
        day = row.get('economic_date')
        key = _gkey(
            group_kind='tpo', source_collection=collection, root=row.get('root'),
            year=year, stage=row.get('stage'), session=row.get('session'),
            anchor=row.get('anchor_variant'), variant=str(row.get('bracket_minutes')),
            proxy=row.get('representation'), measurement_status='observed', contrast=None,
        )
        store = groups[key]
        for name, value in (
            ('visit_count', row.get('visit_count')),
            ('range_proxy_count', row.get('range_proxy_count')),
            ('single_print_count', None if row.get('final_single_print_rows') is None
             else len(row.get('final_single_print_rows') or ())),
        ):
            if name not in store:
                store[name] = _DateStore()
            store[name].add(day, value)
        by_pair[(
            row.get('anchor_id'), row.get('cut_ns'), row.get('bracket_minutes'),
            row.get('instrument_id'),
        )][row.get('representation')] = row
    for pair, representations in by_pair.items():
        visits = representations.get('whole_trade_visits')
        proxy = representations.get('ohlc_range_proxy')
        if visits is None or proxy is None:
            continue
        key = _gkey(
            group_kind='paired_tpo', source_collection=collection, root=visits.get('root'),
            year=year, stage=visits.get('stage'), session=visits.get('session'),
            anchor=visits.get('anchor_variant'), variant=str(visits.get('bracket_minutes')),
            proxy='visit_vs_range', measurement_status='observed',
            contrast='tpo_visit_minus_range_proxy',
        )
        store = groups[key]
        if 'visit_count' not in store:
            store['visit_count'] = _DateStore()
        left = visits.get('visit_count')
        right = proxy.get('visit_count')
        if left is not None and right is not None:
            store['visit_count'].add(visits.get('economic_date'), left - right)
        _ = pair


def _accumulate_joins(groups, rows, *, collection, year):
    for row in rows:
        day = row.get('economic_date')
        key = _gkey(
            group_kind='join', source_collection=collection, root=row.get('root'),
            year=year, stage=row.get('stage'), session=row.get('session'),
            anchor=row.get('anchor_id'), variant=row.get('geometry_variant'),
            proxy=f"{row.get('latency_ns')}:{row.get('horizon_kind')}:{row.get('horizon_minutes')}",
            measurement_status=row.get('join_status'), contrast=None,
        )
        store = groups[key]
        for name in (
            'poc_touch', 'val_touch', 'vah_touch', 'terminal_inside_va',
            'boundary_moving', 'price_crossing_frozen_va',
        ):
            value = row.get(name)
            if name not in store:
                store[name] = _DateStore()
            if value is None:
                continue
            store[name].add(day, 1.0 if value else 0.0)


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
    rows = 0
    for table in read_series_tables(series):
        rows += len(table)
        del table
    if rows != int(series.get('rows') or rows):
        raise IntegrityError('accepted series row count changed')
    return rows


def authenticate_reused_partition(part, load_reference):
    if not isinstance(part, dict) or part.get('kind') != PARTITION_KIND:
        raise IntegrityError('accepted partition is not a profile reference partition')
    if part.get('passed') is not True:
        raise IntegrityError('accepted partition is not a passed profile partition')
    _authenticate_json_ref(
        part.get('completeness'), load_reference,
        kinds={'auction_flow_profile_partition_completeness_v1'},
    )
    for name in ('geometry', 'tpo', 'joins', 'cells'):
        _authenticate_series_ref(part.get(name))
    return part


def project_profile_resources(measurements, *, remaining_source_bytes, remaining_atoms,
                              remaining_geometry_rows, margin=1.5):
    """Pilot-measured envelope: source-byte + atom + geometry-row work, margin 1.5."""
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


def _group_identity_row(group):
    return {name: group.get(name) for name in _GFIELDS}


def _markdown_report(*, groups, completeness, population, cpu, output_bytes, reused,
                     recomputed, selected, all_keys, refs, measurements):
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
        meas = item
        lines.append(
            f'| {key[0]} | {key[1]} | {key[2]} | {meas.get("cpu_seconds")} | '
            f'{meas.get("atoms")} | {meas.get("geometry_rows")} | '
            f'{meas.get("source_bytes")} | {meas.get("output_bytes")} |'
        )
    lines.extend(['', '## Groups', ''])
    lines.append(
        '| collection | root | year | stage | session | anchor | variant | proxy | '
        'status | contrast | metric | unit | date_mean | event_mean | dates | events | undefined |'
    )
    lines.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for group in groups:
        metrics = group.get('metrics') or {}
        for name, payload in metrics.items():
            date_mean = payload.get('date_mean')
            if isinstance(date_mean, dict):
                date_mean = date_mean.get('estimate')
            lines.append(
                f'| {group.get("source_collection")} | {group.get("root")} | {group.get("year")} | '
                f'{group.get("stage")} | {group.get("session")} | {group.get("anchor")} | '
                f'{group.get("variant")} | {group.get("proxy")} | {group.get("measurement_status")} | '
                f'{group.get("contrast")} | {name} | {payload.get("unit")} | {date_mean} | '
                f'{payload.get("event_mean")} | {payload.get("eligible_independent_dates")} | '
                f'{payload.get("eligible_observations")} | {payload.get("undefined")} |'
            )
    lines.extend(['', '## Artifact references', ''])
    for name, value in refs.items():
        lines.append(f'- `{name}`: `{value}`')
    lines.append('')
    return '\n'.join(lines) + '\n'


def run_profile_statistics(*, population, window_population, contract, outputs, load_reference,
                           selected_partition_keys=None, accepted_partitions=None):
    """Reconstruct geometry then reduce collection/root/year groups.

    ``population`` and ``window_population`` are already-authenticated payloads.
    This helper never reloads those JSON objects and never spawns workers.
    """
    if not isinstance(outputs, BoundedOutputs) or not callable(load_reference):
        raise ContractError('bounded outputs and authenticated reference loader required')
    rec = _mapping(population, what='population')
    if rec.get('kind') != POPULATION_KIND:
        raise IntegrityError('authenticated auction_flow_observation_population_v1 required')
    windows = _mapping(window_population, what='window_population')
    if windows.get('kind') != WINDOW_POPULATION_KIND:
        raise IntegrityError('authenticated auction_flow_window_population_v1 required')
    frozen, stats, policy, collections = _require_contract(contract)
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
    completeness_refs = []
    reused, recomputed, measurements = 0, 0, []
    all_geometry = []
    all_tpo = []
    all_joins = []
    groups = defaultdict(dict)
    paired = defaultdict(dict)
    alias_dates = defaultdict(set)
    np = pa = None
    window_units = windows.get('units') or []
    if not isinstance(window_units, list):
        raise IntegrityError('window population lost its unit summaries')
    for ordinal, key in enumerate(selected_keys):
        collection, root, year = key
        members = plan['members'][key]
        neighbors = neighbor_units(plan, key, collections=collections)
        source_refs = profile_partition_source_refs(members)
        window_refs = window_unit_refs(window_units, paths={_unit_path(unit) for unit in members})
        identity = profile_partition_identity(
            frozen, collection=collection, root=root, year=year,
            source_refs=source_refs, window_refs=window_refs,
        )
        if identity in accepted and accepted[identity][1].get('passed') is True:
            ref, part = accepted[identity]
            authenticate_reused_partition(part, load_reference)
            reused += 1
            completeness_payload = _authenticate_json_ref(
                part['completeness'], load_reference,
                kinds={'auction_flow_profile_partition_completeness_v1'},
            )
            for name in ('units_scanned', 'units_unavailable', 'atoms_matched', 'geometry_emitted',
                         'geometry_complete', 'geometry_partial', 'geometry_null',
                         'tpo_emitted', 'joins_emitted', 'joins_missing', 'joins_censored'):
                total[name] += completeness_payload.get(name, 0)
        else:
            if np is None:
                np, pa = _require_numpy(), _require_pyarrow()
            ref, part, measurement, geometry_rows, tpo_rows, join_rows = compute_profile_partition(
                key=key, members=members, neighbors=neighbors, identity=identity,
                source_refs=source_refs, contract=frozen, calendar=calendar,
                policy=policy, window_units=window_units, outputs=outputs,
                ordinal=ordinal, pa=pa,
            )
            recomputed += 1
            measurements.append({**measurement, 'partition_key': encode_profile_partition_key(key)})
            all_geometry.extend(geometry_rows)
            all_tpo.extend(tpo_rows)
            all_joins.extend(join_rows)
            _accumulate_geometry(
                groups, paired, geometry_rows, collection=collection, year=year,
                alias_dates=alias_dates,
            )
            _accumulate_tpo(groups, tpo_rows, collection=collection, year=year)
            _accumulate_joins(groups, join_rows, collection=collection, year=year)
            counts = part.get('completeness_counts') or {}
            for name in total:
                if name in counts and isinstance(counts[name], int):
                    total[name] += counts[name]
        partition_refs.append(ref)
        geometry_refs.append(part['geometry'])
        tpo_refs.append(part['tpo'])
        join_refs.append(part['joins'])
        cell_refs.append(part.get('cells'))
        completeness_refs.append(part['completeness'])
    if np is None:
        np, pa = _require_numpy(), _require_pyarrow()
    primary = frozen.get('primary_population') or {}
    intended_by_stage = {}
    for key in selected_keys:
        _collection, root, year = key
        for stage in (*STAGE_ORDER, 'unassigned'):
            intended_by_stage[(root, year, stage)] = intended_date_universe(
                year, stage, root, policy,
                primary.get('start', '2020-01-01'), primary.get('end', '2026-09-04'),
            )
    finalized = _finalize_groups(groups, intended_by_stage=intended_by_stage, stats=stats, np=np)
    paired_out = _finalize_groups(paired, intended_by_stage=intended_by_stage, stats=stats, np=np)
    group_ref = outputs.json('profile-groups.json', {
        'kind': 'auction_flow_profile_group_statistics_v1',
        'groups': finalized, 'family_complete': False,
        'variant_ids': list(frozen_variant_ids()),
        'bar_proxy_variants': list(BAR_PROXY_VARIANTS),
    }, kind='auction_flow_profile_group_statistics_v1')
    paired_ref = outputs.json('profile-paired.json', {
        'kind': 'auction_flow_profile_paired_contrasts_v1',
        'groups': paired_out, 'family_complete': False,
        'contrasts': [item[2] for item in PAIRED_CONTRASTS],
    }, kind='auction_flow_profile_paired_contrasts_v1')
    completeness_out = {
        **total,
        'family_complete': False,
        'selected_partition_subset': subset,
        'declared_partitions': len(plan['keys']),
        'selected_partitions': len(selected_keys),
        'alias_independent_dates': {sha: sorted(days) for sha, days in alias_dates.items()},
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
    report_text = _markdown_report(
        groups=finalized + paired_out, completeness=total, population=rec,
        cpu=cpu, output_bytes=outputs.written, reused=reused, recomputed=recomputed,
        selected=selected_keys, all_keys=plan['keys'], refs=refs, measurements=measurements,
    )
    with outputs.create('profile-reference-statistics-report.md') as stream:
        stream.write(report_text.encode())
    report_ref = outputs.reference(
        'profile-reference-statistics-report.md', kind='auction_flow_profile_statistics_report')
    refs['report'] = report_ref
    counts = {
        'declared_partitions': len(plan['keys']),
        'selected_partitions': len(selected_keys),
        'reused_partitions': reused,
        'new_partitions': recomputed,
        'units_scanned': total.get('units_scanned', 0),
        'units_unavailable': total.get('units_unavailable', 0),
        'atoms_matched': total.get('atoms_matched', 0),
        'geometry_emitted': total.get('geometry_emitted', 0),
        'geometry_complete': total.get('geometry_complete', 0),
        'tpo_emitted': total.get('tpo_emitted', 0),
        'joins_emitted': total.get('joins_emitted', 0),
        'independent_alias_streams': len(alias_dates),
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
    return summary


__all__ = [
    'KIND', 'authenticate_reused_partition', 'decode_profile_partition_key',
    'encode_profile_partition_key', 'neighbor_units', 'profile_partition_identity',
    'profile_partition_plan', 'project_profile_resources', 'run_profile_statistics',
    'scientific_contract_definition',
]
