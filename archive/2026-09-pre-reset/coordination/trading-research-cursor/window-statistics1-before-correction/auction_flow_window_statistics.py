"""Formation, availability-delay, forward-label and event-timing statistics.

This consumer answers the frozen window-statistics contract from retained
feature/label tables. It does not fit Context, score Locations, run core
atomic statistics, or certify family completion. Root owns registration,
review, integration and registered execution.
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
    ExplicitCashSessions,
    FROZEN_STAGE_POLICY,
    REQUIRED_CASH_CALENDAR_REFERENCE,
    STAGE_ORDER,
    classify_session,
    economic_date,
    labeled_date_and_event_means,
    stage_name,
)
from trading_research.research.auction_flow_measurements import SOURCE_FILTERS
from trading_research.research.auction_flow_production import source_variant
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries, read_series_tables
from trading_research.research.auction_flow_window_links import join_window_eligibility
from trading_research.research.date_statistics import _moving_weights, observed_date_statistics


VERSION = 'auction-flow-window-statistics-v1'
KIND = 'auction_flow_window_statistics_result_v1'
FROZEN_CONTRACT_KIND = 'auction_flow_window_statistics_contract_v1'
POPULATION_KIND = 'auction_flow_window_population_v1'
UNIT_KIND = 'auction_flow_window_unit_v1'
ZONE = 'America/New_York'
NS = 1_000_000_000
MINUTE_NS = 60 * NS
TICK_INDEX_POINTS = 0.25
SOURCE_LATENCY_NS = 250_000_000
FORMATION_MINUTES = (5, 15, 60, 240)
LATENCY_NS = (250_000_000, 0, 1_000_000_000)
LATENCY_REFERENCE_NS = 250_000_000
LATENCY_ALTERNATIVES_NS = (0, 1_000_000_000)
FORWARD_HORIZONS_MINUTES = (5, 15, 60)
HORIZON_KINDS = ('fixed_minutes', 'remaining_session')
QUANTILE_LEVELS = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
SESSIONS = ('cash_rth', 'pre_rth', 'futures_wallclock_18_17', 'off_session')
RELATIVE_BUCKETS = (
    (-60, -15, '[-60,-15)'),
    (-15, 0, '[-15,0)'),
    (0, 15, '[0,15)'),
    (15, 60, '[15,60)'),
)
FEATURE_QUALITY_FLAGS = (
    'atoms_complete', 'coordinate_complete', 'supplied_raw_coordinate_stable',
    'source_instrument_presence', 'source_coverage_complete',
    'flow_history_complete', 'price_history_complete',
)
IDENTITY_KEYS = (
    'root', 'source_path', 'source_metadata_sha256', 'source_variant',
    'acquired_event_start_ns', 'acquired_event_end_ns',
)
MEASUREMENT_METRICS = (
    'formationvolume_per_second', 'unknown_volume_fraction',
    'formation_price_range_ticks', 'VWAP_variance_ticks_squared',
    'standing_mean_spread_ticks', 'OFI_path_range_on_pressureeligible',
)
JOINED_METRICS = (
    'terminal_return_ticks', 'future_up_excursion_ticks', 'future_down_excursion_ticks',
    'future_path_range_ticks', 'future_signedflow', 'no_new_trade', 'no_priced_trade',
    'concordance_both_nonzero', 'zero_past_sign', 'zero_future_sign',
)
PAIRED_LATENCY_METRICS = (
    'terminal_return_ticks', 'future_up_excursion_ticks', 'future_down_excursion_ticks',
    'no_new_trade',
)
OPERATIONAL_CONTRACT_FIELDS = (
    'phase', 'pilot_source_paths', 'accepted_partitions', 'selected_partition_keys',
    'accepted_pilot_execution', 'accepted_pilot_worker', 'accepted_consumer_files',
    'parallel_execution', 'cash_session_table', 'event_rows',
)
_INT64_MIN = -(2 ** 63)
_INT64_MAX = 2 ** 63 - 1
_SHA_LEN = 64
BATCH_HINT = 65536
STAT_BATCH = 12


def _mapping(value, *, what):
    if not isinstance(value, dict):
        raise IntegrityError(f'{what} must be an object')
    return value


def _text(value, *, what, allow_empty=False):
    if type(value) is not str or (not value and not allow_empty):
        raise IntegrityError(f'{what} must be a concrete string')
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


def _civil_date_ns(iso):
    parts = iso.split('-')
    if len(parts) != 3:
        raise IntegrityError('stage date must be YYYY-MM-DD')
    year, month, day = (int(part) for part in parts)
    delta = datetime(year, month, day, tzinfo=timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return _add_checked(delta.days * 86400 * NS, what='civil_date_ns')


def _civil_stage_intervals(policy):
    parsed = {}
    for root, spec in policy.items():
        if root == 'other_dates' or not isinstance(spec, dict):
            continue
        parsed[root] = {
            name: (_civil_date_ns(bounds[0]), _civil_date_ns(bounds[1]))
            for name, bounds in spec.items()
            if isinstance(bounds, (list, tuple)) and len(bounds) == 2
        }
    return parsed


def _stage_of_ns(root, at_ns, intervals):
    if at_ns is None or root not in intervals:
        return 'unassigned'
    at_ns = int(at_ns)
    for name in STAGE_ORDER:
        bounds = intervals[root].get(name)
        if bounds is None:
            continue
        begin, finish = bounds
        if begin <= at_ns < finish:
            return name
    return 'unassigned'


def _named_interval_stage(root, start_ns, end_ns, intervals):
    left = _stage_of_ns(root, start_ns, intervals)
    right = _stage_of_ns(root, end_ns, intervals)
    if left == 'unassigned' or left != right:
        return 'unassigned'
    return left


def signed_sign(value):
    """Exact integer sign; zero stays zero and is never a direction."""
    if value is None:
        return None
    if type(value) is bool or not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ContractError('sign inputs must be finite numbers or missing')
    if isinstance(value, float) and not math.isfinite(value):
        raise ContractError('sign inputs must be finite numbers or missing')
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def future_displacements(reference_ticks, future_last, future_high, future_low):
    """Formation-relative displacements. Missing prices stay missing, not zero."""
    if reference_ticks is None:
        return {
            'terminal_return_ticks': None, 'future_up_excursion_ticks': None,
            'future_down_excursion_ticks': None, 'future_path_range_ticks': None,
        }
    reference = _py_int(reference_ticks, what='reference_ticks')
    last = None if future_last is None else _py_int(future_last, what='future_last')
    high = None if future_high is None else _py_int(future_high, what='future_high')
    low = None if future_low is None else _py_int(future_low, what='future_low')
    up = None if high is None else max(0, high - reference)
    down = None if low is None else max(0, reference - low)
    return {
        'terminal_return_ticks': None if last is None else last - reference,
        'future_up_excursion_ticks': up,
        'future_down_excursion_ticks': down,
        'future_path_range_ticks': None if high is None or low is None else high - low,
    }


def true_path_range(high, low, close=None):
    """True path range is high-low. Close extrema are never a substitute."""
    _ = close
    if high is None or low is None:
        return None
    return _py_int(high, what='high') - _py_int(low, what='low')


def formation_volume_per_second(volume, start_ns, end_ns):
    start = _py_int(start_ns, what='event_start_ns')
    end = _py_int(end_ns, what='event_end_ns')
    if start is None or end is None or end <= start:
        return None
    if volume is None:
        return None
    width = (end - start) / NS
    return float(_py_int(volume, what='volume')) / width


def unknown_volume_fraction(unknown, volume):
    if unknown is None or volume is None:
        return None
    vol = _py_int(volume, what='volume')
    if vol == 0:
        return None
    return float(_py_int(unknown, what='unknown')) / vol


def cohort_volume_fraction(cohort_volume, all_volume):
    if cohort_volume is None or all_volume is None:
        return None
    total = _py_int(all_volume, what='all_volume')
    if total == 0:
        return None
    return float(_py_int(cohort_volume, what='cohort_volume')) / total


def cohort_signed_fraction(buy, sell, all_volume):
    if buy is None or sell is None or all_volume is None:
        return None
    total = _py_int(all_volume, what='all_volume')
    if total == 0:
        return None
    return float(_py_int(buy, what='buy') - _py_int(sell, what='sell')) / total


def complete_binary_flag(value, *, complete):
    """Zero/one only on complete coverage. Incomplete stays missing, not zero."""
    if complete is not True:
        return None
    if value is None:
        return None
    if type(value) is bool:
        return 1.0 if value else 0.0
    return 1.0 if value else 0.0


def directional_concordance(past_close, terminal_return):
    """Paired observed sign frequency. Not accuracy or predictive gain."""
    past = signed_sign(past_close)
    future = signed_sign(terminal_return)
    if past is None or future is None:
        return {
            'category': 'missing', 'concordant': None,
            'zero_past': False, 'zero_future': False, 'both_nonzero': False,
        }
    zero_past = past == 0
    zero_future = future == 0
    if zero_past and zero_future:
        category = 'zero_past_and_future'
    elif zero_past:
        category = 'zero_past'
    elif zero_future:
        category = 'zero_future'
    else:
        category = 'both_nonzero'
    return {
        'category': category,
        'concordant': None if past == 0 or future == 0 else past == future,
        'zero_past': zero_past,
        'zero_future': zero_future,
        'both_nonzero': category == 'both_nonzero',
    }


def reference_inside_formation(reference_event_ns, start_ns, cut_ns):
    """Last priced event must be strictly inside [start, cut)."""
    if reference_event_ns is None or start_ns is None or cut_ns is None:
        return False
    start = _py_int(start_ns, what='event_start_ns')
    cut = _py_int(cut_ns, what='cut_ns')
    ref = _py_int(reference_event_ns, what='reference_event_ns')
    return start <= ref < cut


def known_at_available_at_cut(known_at_ns, cut_ns):
    """Causal availability at the cut. After-cut or unknown is not available."""
    if known_at_ns is None or cut_ns is None:
        return False
    return _py_int(known_at_ns, what='known_at_ns') <= _py_int(cut_ns, what='cut_ns')


def feature_quality_eligible(feature):
    feature = _mapping(feature, what='feature')
    for name in FEATURE_QUALITY_FLAGS:
        if feature.get(name) is not True:
            return False, f'missing_feature_quality:{name}'
    return True, None


def feature_censored_or_roll(feature):
    return (
        feature.get('left_censored') is True
        or feature.get('right_censored') is True
        or feature.get('contract_transition') is True
    )


def label_censored_or_roll(label):
    return (
        label.get('left_censored') is True
        or label.get('right_censored') is True
        or label.get('contract_transition') is True
    )


def scientific_join_eligibility(feature, label):
    """Identity/stage join plus quality, completeness and no censor/roll."""
    join = join_window_eligibility(feature, label)
    if join.get('eligible') is not True:
        return {**join, 'eligible': False, 'scientific_reason': join.get('reason')}
    ok, reason = feature_quality_eligible(feature)
    if not ok:
        return {**join, 'eligible': False, 'scientific_reason': reason}
    if feature_censored_or_roll(feature):
        return {**join, 'eligible': False, 'scientific_reason': 'feature_censored_or_roll'}
    if label.get('complete') is not True:
        return {**join, 'eligible': False, 'scientific_reason': 'label_incomplete'}
    if label.get('known_at_ns') is None:
        return {**join, 'eligible': False, 'scientific_reason': 'label_before_maturity'}
    end = label.get('event_end_ns')
    known = label.get('known_at_ns')
    if end is not None and known is not None and int(known) < int(end):
        return {**join, 'eligible': False, 'scientific_reason': 'label_before_maturity'}
    if label_censored_or_roll(label):
        return {**join, 'eligible': False, 'scientific_reason': 'label_censored_or_roll'}
    return {**join, 'eligible': True, 'scientific_reason': None}


def same_actual_reference(left, right):
    if left is None or right is None:
        return False
    return (
        left.get('reference_event_ns') is not None
        and left.get('reference_event_ns') == right.get('reference_event_ns')
        and left.get('reference_source_order') is not None
        and left.get('reference_source_order') == right.get('reference_source_order')
        and left.get('reference_price_ticks') is not None
        and left.get('reference_price_ticks') == right.get('reference_price_ticks')
    )


def formation_pair_eligible(left_feature, right_feature, label):
    """Same cut/target and the same actual reference. Distinct priors are not paired."""
    if left_feature.get('cut_ns') != right_feature.get('cut_ns'):
        return False
    if left_feature.get('instrument_id') != right_feature.get('instrument_id'):
        return False
    if left_feature.get('contract_key') != right_feature.get('contract_key'):
        return False
    if not same_actual_reference(left_feature, right_feature):
        return False
    return (
        scientific_join_eligibility(left_feature, label)['eligible']
        and scientific_join_eligibility(right_feature, label)['eligible']
    )


def latency_pair_eligible(feature, left_label, right_label):
    """0/1s versus 250ms on the same cut, formation, horizon and reference."""
    if left_label.get('cut_ns') != right_label.get('cut_ns') or left_label.get('cut_ns') != feature.get('cut_ns'):
        return False
    if left_label.get('horizon_kind') != right_label.get('horizon_kind'):
        return False
    if left_label.get('horizon_minutes') != right_label.get('horizon_minutes'):
        return False
    if left_label.get('instrument_id') != right_label.get('instrument_id'):
        return False
    if left_label.get('contract_key') != right_label.get('contract_key'):
        return False
    return (
        scientific_join_eligibility(feature, left_label)['eligible']
        and scientific_join_eligibility(feature, right_label)['eligible']
    )


def event_in_formation(event_ts_ns, start_ns, cut_ns):
    """Half-open [start, cut). An event at the cut is excluded."""
    if event_ts_ns is None or start_ns is None or cut_ns is None:
        return False
    start = _py_int(start_ns, what='event_start_ns')
    cut = _py_int(cut_ns, what='cut_ns')
    at = _py_int(event_ts_ns, what='event_ts_ns')
    return start <= at < cut


def timed_event_eligible(event):
    """Date-only rows cannot enter timed proximity buckets."""
    event = _mapping(event, what='event')
    if event.get('time_basis') == 'date_only':
        return False
    if event.get('time_precision') == 'date_only':
        return False
    if event.get('intraday_functions_defined') is False:
        return False
    return event.get('event_ts_utc_ns') is not None


def event_relative_bucket(event_ts_ns, cut_ns):
    """Half-open minute buckets relative to the cut. Date-only stays out."""
    if event_ts_ns is None or cut_ns is None:
        return None
    delta = _py_int(event_ts_ns, what='event_ts_ns') - _py_int(cut_ns, what='cut_ns')
    if delta % MINUTE_NS == 0:
        minutes = delta // MINUTE_NS
    elif delta >= 0:
        minutes = delta // MINUTE_NS
    else:
        minutes = -((-delta + MINUTE_NS - 1) // MINUTE_NS)
    for low, high, name in RELATIVE_BUCKETS:
        if low <= minutes < high:
            return name
    return None


def event_coverage_state(has_record):
    """No calendar record is unknown coverage, not a certified ordinary day."""
    return 'recorded' if has_record else 'unknown'


def equal_date_mean(date_cells):
    """One weight per date. Duplicate cuts on one date do not add date support."""
    if not isinstance(date_cells, dict):
        raise ContractError('equal-date cells must be a date mapping')
    sums, counts = {}, {}
    for day, values in date_cells.items():
        if values is None:
            continue
        if isinstance(values, (int, float)) and not isinstance(values, bool):
            seq = (float(values),)
        else:
            seq = tuple(float(item) for item in values if item is not None)
        if not seq:
            continue
        sums[day] = math.fsum(seq)
        counts[day] = len(seq)
    return labeled_date_and_event_means(sums, counts)


def alias_collection_dates(rows):
    """Monthly/weekly aliases of the same date are not extra independent support."""
    if not isinstance(rows, (list, tuple)):
        raise ContractError('alias rows must be a sequence')
    by_key = defaultdict(lambda: {'dates': set(), 'collections': set(), 'rows': 0})
    for row in rows:
        row = _mapping(row, what='alias_row')
        root = _text(row.get('root'), what='root')
        day = _text(row.get('economic_date'), what='economic_date')
        collection = _text(row.get('collection'), what='collection')
        key = (root, row.get('year'), row.get('identity') or day)
        cell = by_key[key]
        cell['dates'].add(day)
        cell['collections'].add(collection)
        cell['rows'] += 1
    out = {}
    for key, cell in by_key.items():
        out[str(key)] = {
            'independent_economic_dates': sorted(cell['dates']),
            'independent_economic_date_count': len(cell['dates']),
            'collections': sorted(cell['collections']),
            'source_window_rows': cell['rows'],
            'aliases_are_not_extra_independent_support': True,
        }
    return out


def intended_date_universe(year, stage, root, stage_policy=None, primary_start='2020-01-01',
                           primary_end='2026-09-04'):
    """Year/stage civil dates inside the primary population. Gaps stay missing."""
    if type(year) is bool or type(year) is not int:
        raise ContractError('economic year must be an exact integer')
    policy = FROZEN_STAGE_POLICY if stage_policy is None else stage_policy
    start = date(year, 1, 1)
    finish = date(year + 1, 1, 1)
    days = []
    cursor = start
    while cursor < finish:
        iso = cursor.isoformat()
        if primary_start <= iso <= primary_end:
            assigned = stage_name(root, iso, policy)
            if assigned == stage:
                days.append(iso)
        cursor = cursor + timedelta(days=1)
    return tuple(days)


def encode_window_partition_key(key):
    if not isinstance(key, (list, tuple)) or len(key) != 3:
        raise IntegrityError('window partition key must be (collection, root, economic_year)')
    collection, root, year = key
    if type(collection) is not str or not collection or type(root) is not str or not root:
        raise IntegrityError('partition collection and root must be nonempty strings')
    if type(year) is bool or type(year) is not int:
        raise IntegrityError('partition economic year must be an exact integer')
    return [collection, root, int(year)]


def decode_window_partition_key(key):
    return tuple(encode_window_partition_key(key))


def scientific_contract_definition(contract):
    rec = _mapping(contract, what='contract')
    return {name: value for name, value in rec.items() if name not in OPERATIONAL_CONTRACT_FIELDS}


def window_partition_source_refs(members):
    refs = []
    for unit in members:
        refs.append({
            'unit_id': unit.get('unit_id'),
            'source_identity': unit.get('source_identity'),
            'features': _series_digest(unit.get('features')),
            'labels': _series_digest(unit.get('labels')),
            'feature_rows': unit.get('feature_rows'),
            'label_rows': unit.get('label_rows'),
        })
    return refs


def window_partition_identity(contract, *, collection, root, year, source_refs):
    return digest({
        'definition': scientific_contract_definition(contract),
        'collection': collection,
        'root': root,
        'economic_year': year,
        'source_refs': source_refs,
    })


def _series_digest(series):
    if not isinstance(series, dict):
        return None
    files = []
    for item in series.get('files') or []:
        groups = [(g.get('sha256'), g.get('rows')) for g in item.get('row_group_values') or []]
        files.append((item.get('sha256'), item.get('rows'), groups))
    return {'rows': series.get('rows'), 'schema': series.get('schema'), 'files': files}


def _iso_dates(start_iso, end_exclusive_iso):
    cursor = date.fromisoformat(start_iso)
    finish = date.fromisoformat(end_exclusive_iso)
    out = []
    while cursor < finish:
        out.append(cursor.isoformat())
        cursor = cursor + timedelta(days=1)
    return out


def _require_contract(contract):
    rec = _mapping(contract, what='contract')
    if rec.get('kind') != FROZEN_CONTRACT_KIND:
        raise IntegrityError('frozen auction_flow_window_statistics_contract_v1 required')
    if rec.get('version') != 1:
        raise IntegrityError('window statistics contract version changed')
    if rec.get('family_complete') is True:
        raise IntegrityError('contract cannot certify family completion')
    if list(rec.get('formation_minutes') or ()) != list(FORMATION_MINUTES):
        raise IntegrityError('every declared formation candidate must be retained')
    if list(rec.get('latency_ns') or ()) != list(LATENCY_NS):
        raise IntegrityError('every declared latency candidate must be retained')
    stats = rec.get('statistics') or {}
    if (stats.get('seed') != 20260908 or stats.get('block_length_dates') != 5
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
    reference = contract.get('cash_calendar')
    if table is not None:
        return ExplicitCashSessions(table, reference={'kind': 'explicit_cash_session_table'})
    if reference is None:
        raise ContractError(
            'window statistics require contract.cash_calendar equal to the admitted '
            f'cash_rth_calendar {REQUIRED_CASH_CALENDAR_REFERENCE!r}; fixtures may pass '
            'cash_session_table instead'
        )
    if (not isinstance(reference, dict) or type(reference.get('path')) is not str
            or type(reference.get('sha256')) is not str):
        raise IntegrityError('cash_calendar must be a fully qualified path/sha256 reference')
    if callable(load_reference):
        payload = load_reference(reference)
        if not isinstance(payload, dict) or payload.get('schema') != 'published-cash-rth-calendar-v1':
            raise IntegrityError('cash_calendar reference is not the published cash RTH calendar')
    from trading_research.foundations.cash_calendar import CashCalendar
    return ExplicitCashSessions(published=CashCalendar(Path(reference['path'])), reference=reference)


def _load_events(contract):
    if 'event_rows' in contract:
        rows = contract['event_rows']
        if not isinstance(rows, list):
            raise IntegrityError('event_rows must be a list')
        return [dict(row) for row in rows], {'kind': 'inline_event_rows', 'rows': len(rows)}
    source = (contract.get('event_source') or {}).get('events')
    if not source:
        return [], {'kind': 'no_event_source', 'rows': 0, 'coverage': 'unknown'}
    path = Path(source['path'])
    if (type(source.get('size_bytes')) is not int or path.stat().st_size != source['size_bytes']
            or file_digest(path) != source['sha256']):
        raise IntegrityError('scheduled observed-source-events parquet changed or exceeded its bound')
    import pyarrow.parquet as pq
    table = pq.read_table(path)
    rows = []
    names = table.column_names
    columns = {name: table.column(name).to_pylist() for name in names}
    for index in range(len(table)):
        row = {name: columns[name][index] for name in names}
        if row.get('event_ts_utc_ns') is not None:
            row['event_ts_utc_ns'] = _py_int(row['event_ts_utc_ns'], what='event_ts_utc_ns')
        if row.get('known_at_ns') is not None:
            row['known_at_ns'] = _py_int(row['known_at_ns'], what='event_known_at_ns')
        rows.append(row)
    return rows, {'kind': source.get('kind'), 'path': source['path'], 'sha256': source['sha256'],
                  'rows': len(rows)}


def dedup_scheduled_events(events):
    """primary_population + independent_support; retain every source provenance."""
    selected = []
    skipped = 0
    for event in events:
        if event.get('primary_population') is True and event.get('independent_support') is True:
            selected.append(event)
        else:
            skipped += 1
    by_id = {}
    order = []
    for event in selected:
        sid = event.get('semantic_id')
        if sid is None:
            sid = f'anonymous:{len(order)}'
        if sid not in by_id:
            row = dict(event)
            row['known_at_ns'] = None
            row['causal_feature_eligible'] = False
            row['event_labels_retrospective'] = True
            row['provenance'] = []
            by_id[sid] = row
            order.append(sid)
        by_id[sid]['provenance'].append({
            'source_path': event.get('source_path'),
            'source_sha256': event.get('source_sha256'),
            'physical_row': event.get('physical_row'),
            'source': event.get('source'),
        })
    return [by_id[sid] for sid in order], {
        'source_event_rows': len(events),
        'selected_primary_independent': len(selected),
        'unique_semantic_events': len(order),
        'nonselected_source_rows': skipped,
    }


def _unit_unavailable(unit):
    if unit.get('disposition') == 'unavailable_source_window':
        return True
    if unit.get('source_window_status') == 'unavailable_source_window':
        return True
    if unit.get('instrument_count') == 0:
        return True
    features = unit.get('features')
    if features is None or features.get('roundtrip_exact') is not True:
        return True
    return False


def _unit_window_ns(unit):
    if unit.get('cut_start_ns') is not None and unit.get('cut_end_ns') is not None:
        return _py_int(unit['cut_start_ns'], what='cut_start_ns'), _py_int(unit['cut_end_ns'], what='cut_end_ns')
    uid = unit.get('unit_id')
    if isinstance(uid, (list, tuple)) and len(uid) == 3:
        return _py_int(uid[1], what='unit_id.start'), _py_int(uid[2], what='unit_id.end')
    ident = _mapping(unit.get('source_identity'), what='source_identity')
    return (
        _py_int(ident.get('acquired_event_start_ns'), what='acquired_event_start_ns'),
        _py_int(ident.get('acquired_event_end_ns'), what='acquired_event_end_ns'),
    )


def _unit_path(unit):
    ident = unit.get('source_identity') or {}
    if ident.get('source_path'):
        return ident['source_path']
    uid = unit.get('unit_id')
    if isinstance(uid, (list, tuple)) and uid:
        return uid[0]
    return unit.get('source_path')


def _unit_root(unit):
    ident = unit.get('source_identity') or {}
    return ident.get('root') or unit.get('root')


def window_partition_plan(units, *, collections):
    """Map window units onto (collection, root, economic_year). Collections stay separate."""
    if not isinstance(units, list):
        raise IntegrityError('window population lost its unit summaries')
    partitions = defaultdict(list)
    unavailable = 0
    for unit in units:
        path = _unit_path(unit)
        root = _unit_root(unit)
        if type(path) is not str or type(root) is not str:
            raise IntegrityError('window unit lost source path or root')
        if path not in collections:
            raise IntegrityError('frozen source collection map is incomplete')
        collection = collections[path]
        start, end = _unit_window_ns(unit)
        if start is None or end is None or not start < end:
            raise IntegrityError('window unit lost a positive half-open interval')
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
    }


def _require_numpy():
    import numpy as np
    if getattr(np, '__version__', None) != '2.3.3':
        raise ContractError('window statistics require the pinned NumPy 2.3.3 provider')
    return np


def _require_pyarrow():
    import pyarrow as pa
    if getattr(pa, '__version__', None) != '25.0.1':
        raise ContractError('window statistics require the pinned PyArrow 25.0.1 provider')
    return pa


def _i64_col(table, name, np, *, optional=False):
    if name not in table.column_names:
        if optional:
            n = len(table)
            return np.zeros(n, dtype=np.int64), np.zeros(n, dtype=bool)
        raise IntegrityError(f'window table lost required integer column {name}')
    combined = table.column(name).combine_chunks()
    valid = (~combined.is_null().to_numpy(zero_copy_only=False)
             if combined.null_count else np.ones(len(combined), dtype=bool))
    filled = combined.fill_null(0) if combined.null_count else combined
    raw = filled.to_numpy(zero_copy_only=False)
    if raw.dtype.kind == 'f':
        raise IntegrityError(f'{name} must be exact integers without float rounding')
    if raw.dtype.kind == 'u':
        if raw.itemsize >= 8 and np.any(raw.astype(np.uint64, copy=False) > np.uint64(_INT64_MAX)):
            raise IntegrityError(f'{name} exceeds the exact int64 domain')
        return np.array(raw, dtype=np.int64, copy=True), np.asarray(valid, dtype=bool)
    if raw.dtype.kind != 'i':
        raise IntegrityError(f'{name} must be exact integers')
    return np.array(raw, dtype=np.int64, copy=True), np.asarray(valid, dtype=bool)


def _bool_col(table, name, np, *, optional=False, default=False):
    if name not in table.column_names:
        if optional:
            return np.full(len(table), default, dtype=bool)
        raise IntegrityError(f'window table lost required boolean column {name}')
    raw = table.column(name).combine_chunks().to_numpy(zero_copy_only=False)
    return np.asarray(raw, dtype=bool)


def _f64_col(table, name, np, *, optional=False):
    if name not in table.column_names:
        if optional:
            n = len(table)
            return np.full(n, np.nan, dtype=np.float64), np.zeros(n, dtype=bool)
        raise IntegrityError(f'window table lost required float column {name}')
    combined = table.column(name).combine_chunks()
    raw = combined.to_numpy(zero_copy_only=False)
    values = np.array(raw, dtype=np.float64, copy=True)
    valid = ~combined.is_null().to_numpy(zero_copy_only=False) if combined.null_count else np.isfinite(values)
    valid = np.asarray(valid, dtype=bool) & np.isfinite(values)
    return values, valid


def _str_list(table, name, *, optional=False):
    if name not in table.column_names:
        if optional:
            return [None] * len(table)
        raise IntegrityError(f'window table lost required string column {name}')
    return table.column(name).to_pylist()


def _concat_tables(tables, pa):
    if not tables:
        return None
    if len(tables) == 1:
        return tables[0]
    return pa.concat_tables(tables, promote_options='default')


class _DateStore:
    __slots__ = ('date_sum', 'date_count', 'n', 'total', 'minimum', 'maximum')

    def __init__(self):
        self.date_sum = {}
        self.date_count = {}
        self.n = 0
        self.total = 0.0
        self.minimum = None
        self.maximum = None

    def add(self, day, values):
        if values is None:
            return
        if hasattr(values, 'size'):
            if values.size == 0:
                return
            data = [float(v) for v in values.tolist()] if hasattr(values, 'tolist') else [float(v) for v in values]
        elif isinstance(values, (list, tuple)):
            data = [float(v) for v in values]
        else:
            data = [float(values)]
        if not data:
            return
        total = math.fsum(data)
        self.date_sum[day] = self.date_sum.get(day, 0.0) + total
        self.date_count[day] = self.date_count.get(day, 0) + len(data)
        self.n += len(data)
        self.total += total
        lo, hi = min(data), max(data)
        self.minimum = lo if self.minimum is None else min(self.minimum, lo)
        self.maximum = hi if self.maximum is None else max(self.maximum, hi)

    def add_one(self, day, value):
        if value is None:
            return
        self.add(day, (float(value),))


def _empty_completeness():
    return {
        'feature_rows': 0, 'label_rows': 0, 'eligible_feature_rows': 0, 'eligible_joined_rows': 0,
        'censored_feature_rows': 0, 'censored_label_rows': 0, 'unavailable_source_windows': 0,
        'processed_source_windows': 0, 'missing_reference_rows': 0, 'unassigned_stage_rows': 0,
        'source_windows': 0, 'economic_dates': set(), 'calendar_state_counts': Counter(),
        'event_source_rows': 0, 'unique_semantic_events': 0, 'events_with_receiver': 0,
        'events_without_receiver': 0, 'events_without_window': 0, 'date_only_events': 0,
        'unknown_event_coverage_dates': 0,
    }


def _metric_unit(name):
    if 'fraction' in name or name.startswith('zero_') or name.startswith('concordance') or name in (
            'no_new_trade', 'no_priced_trade'):
        return 'dimensionless'
    if name.endswith('_per_second'):
        return 'contracts_per_second'
    if 'variance' in name:
        return 'ticks squared'
    if 'ticks' in name or 'range' in name or 'excursion' in name or 'signedflow' in name:
        return 'quarter-point ticks'
    return 'dimensionless'


def _undefined_metric():
    return {
        'unit': None, 'estimate': None, 'date_mean': None, 'event_mean': None,
        'eligible_observations': 0, 'eligible_independent_dates': 0,
        'missing_date_count': None, 'sample_quantiles': {str(level): None for level in QUANTILE_LEVELS},
        'support': {'independent_dates': 0, 'events': 0, 'sparse': True,
                    'reasons': ['no_valid_observations']},
        'bootstrap': None,
    }


def _stores():
    return defaultdict(_DateStore)


def _group_bucket(groups, key):
    bucket = groups.get(key)
    if bucket is None:
        bucket = _stores()
        groups[key] = bucket
    return bucket


def _feature_measurement_values(feat, i, np):
    start = int(feat['event_start_ns'][i])
    end = int(feat['event_end_ns'][i])
    out = {}
    volume = int(feat['all_volume'][i]) if feat['all_volume_ok'][i] else None
    unknown = int(feat['all_unknown'][i]) if feat['all_unknown_ok'][i] else None
    out['formationvolume_per_second'] = formation_volume_per_second(volume, start, end)
    out['unknown_volume_fraction'] = unknown_volume_fraction(unknown, volume)
    high = int(feat['obs_high'][i]) if feat['obs_high_ok'][i] else None
    low = int(feat['obs_low'][i]) if feat['obs_low_ok'][i] else None
    out['formation_price_range_ticks'] = true_path_range(high, low)
    if feat['var_ok'][i]:
        out['VWAP_variance_ticks_squared'] = float(feat['variance'][i])
    else:
        out['VWAP_variance_ticks_squared'] = None
    if feat['standing'][i] and feat['spread_ok'][i]:
        out['standing_mean_spread_ticks'] = float(feat['spread'][i])
    else:
        out['standing_mean_spread_ticks'] = None
    if feat['pressure'][i] and feat['ofi_high_ok'][i] and feat['ofi_low_ok'][i]:
        out['OFI_path_range_on_pressureeligible'] = true_path_range(
            int(feat['ofi_high'][i]), int(feat['ofi_low'][i]))
    else:
        out['OFI_path_range_on_pressureeligible'] = None
    for cohort in SOURCE_FILTERS:
        cvol = int(feat[f'{cohort}_volume'][i]) if feat[f'{cohort}_volume_ok'][i] else None
        cbuy = int(feat[f'{cohort}_buy'][i]) if feat[f'{cohort}_buy_ok'][i] else None
        csell = int(feat[f'{cohort}_sell'][i]) if feat[f'{cohort}_sell_ok'][i] else None
        chigh = int(feat[f'{cohort}_high'][i]) if feat[f'{cohort}_high_ok'][i] else None
        clow = int(feat[f'{cohort}_low'][i]) if feat[f'{cohort}_low_ok'][i] else None
        cclose = int(feat[f'{cohort}_close'][i]) if feat[f'{cohort}_close_ok'][i] else None
        out[f'{cohort}_volume_fraction'] = cohort_volume_fraction(cvol, volume)
        out[f'{cohort}_signed_fraction'] = cohort_signed_fraction(cbuy, csell, volume)
        out[f'{cohort}_true_CVD_path_range'] = true_path_range(chigh, clow, close=cclose)
    _ = np
    return out


def _extract_features(table, np):
    n = len(table)
    quality = np.ones(n, dtype=bool)
    for name in FEATURE_QUALITY_FLAGS:
        quality &= _bool_col(table, name, np, optional=True, default=False)
    left = _bool_col(table, 'left_censored', np, optional=True, default=False)
    right = _bool_col(table, 'right_censored', np, optional=True, default=False)
    roll = _bool_col(table, 'contract_transition', np, optional=True, default=False)
    ref, ref_ok = _i64_col(table, 'reference_price_ticks', np, optional=True)
    ref_at, ref_at_ok = _i64_col(table, 'reference_event_ns', np, optional=True)
    ref_ord, ref_ord_ok = _i64_col(table, 'reference_source_order', np, optional=True)
    start, _ = _i64_col(table, 'event_start_ns', np)
    end, _ = _i64_col(table, 'event_end_ns', np)
    cut, _ = _i64_col(table, 'cut_ns', np)
    known, known_ok = _i64_col(table, 'known_at_ns', np, optional=True)
    minutes, _ = _i64_col(table, 'formation_minutes', np)
    inst, _ = _i64_col(table, 'instrument_id', np)
    acq_s, _ = _i64_col(table, 'acquired_event_start_ns', np)
    acq_e, _ = _i64_col(table, 'acquired_event_end_ns', np)
    inside = ref_at_ok & (start <= ref_at) & (ref_at < cut) & ref_ok
    all_volume, all_volume_ok = _i64_col(table, 'all__volume', np, optional=True)
    all_unknown, all_unknown_ok = _i64_col(table, 'all__unknown', np, optional=True)
    all_close, all_close_ok = _i64_col(table, 'all__close', np, optional=True)
    obs_high, obs_high_ok = _i64_col(table, 'observed_high_ticks', np, optional=True)
    obs_low, obs_low_ok = _i64_col(table, 'observed_low_ticks', np, optional=True)
    variance, var_ok = _f64_col(table, 'variance_ticks_squared', np, optional=True)
    spread, spread_ok = _f64_col(table, 'duration_mean_spread_ticks', np, optional=True)
    ofi_high, ofi_high_ok = _i64_col(table, 'ofi_high', np, optional=True)
    ofi_low, ofi_low_ok = _i64_col(table, 'ofi_low', np, optional=True)
    standing = _bool_col(table, 'full_standing_window_eligible', np, optional=True, default=False)
    pressure = _bool_col(table, 'full_pressure_transition_window_eligible', np, optional=True, default=False)
    payload = {
        'n': n, 'quality': quality, 'censored': left | right | roll,
        'ref': ref, 'ref_ok': ref_ok, 'ref_at': ref_at, 'ref_at_ok': ref_at_ok,
        'ref_ord': ref_ord, 'ref_ord_ok': ref_ord_ok, 'inside': inside,
        'event_start_ns': start, 'event_end_ns': end, 'cut_ns': cut,
        'known_at_ns': known, 'known_ok': known_ok, 'formation_minutes': minutes,
        'instrument_id': inst, 'acquired_event_start_ns': acq_s, 'acquired_event_end_ns': acq_e,
        'all_volume': all_volume, 'all_volume_ok': all_volume_ok,
        'all_unknown': all_unknown, 'all_unknown_ok': all_unknown_ok,
        'all_close': all_close, 'all_close_ok': all_close_ok,
        'obs_high': obs_high, 'obs_high_ok': obs_high_ok, 'obs_low': obs_low, 'obs_low_ok': obs_low_ok,
        'variance': variance, 'var_ok': var_ok, 'spread': spread, 'spread_ok': spread_ok,
        'ofi_high': ofi_high, 'ofi_high_ok': ofi_high_ok, 'ofi_low': ofi_low, 'ofi_low_ok': ofi_low_ok,
        'standing': standing, 'pressure': pressure,
        'root': _str_list(table, 'root'), 'source_path': _str_list(table, 'source_path'),
        'source_metadata_sha256': _str_list(table, 'source_metadata_sha256'),
        'source_variant': _str_list(table, 'source_variant'),
        'contract_key': _str_list(table, 'contract_key', optional=True),
        'formation_id': _str_list(table, 'formation_id', optional=True),
    }
    for cohort in SOURCE_FILTERS:
        for field in ('volume', 'buy', 'sell', 'high', 'low', 'close'):
            values, ok = _i64_col(table, f'{cohort}__{field}', np, optional=True)
            payload[f'{cohort}_{field}'] = values
            payload[f'{cohort}_{field}_ok'] = ok
    return payload


def _extract_labels(table, np):
    complete = _bool_col(table, 'complete', np, optional=True, default=False)
    left = _bool_col(table, 'left_censored', np, optional=True, default=False)
    right = _bool_col(table, 'right_censored', np, optional=True, default=False)
    roll = _bool_col(table, 'contract_transition', np, optional=True, default=False)
    last, last_ok = _i64_col(table, 'last_priced_ticks', np, optional=True)
    high, high_ok = _i64_col(table, 'observed_high_ticks', np, optional=True)
    low, low_ok = _i64_col(table, 'observed_low_ticks', np, optional=True)
    signed_open, open_ok = _i64_col(table, 'signed_open', np, optional=True)
    signed_close, close_ok = _i64_col(table, 'signed_close', np, optional=True)
    buy, buy_ok = _i64_col(table, 'buy', np, optional=True)
    sell, sell_ok = _i64_col(table, 'sell', np, optional=True)
    known, known_ok = _i64_col(table, 'known_at_ns', np, optional=True)
    end, end_ok = _i64_col(table, 'event_end_ns', np, optional=True)
    start, start_ok = _i64_col(table, 'event_start_ns', np, optional=True)
    latency, _ = _i64_col(table, 'latency_ns', np)
    cut, _ = _i64_col(table, 'cut_ns', np)
    inst, _ = _i64_col(table, 'instrument_id', np)
    minutes, minutes_ok = _i64_col(table, 'horizon_minutes', np, optional=True)
    acq_s, _ = _i64_col(table, 'acquired_event_start_ns', np)
    acq_e, _ = _i64_col(table, 'acquired_event_end_ns', np)
    no_new = _bool_col(table, 'no_new_trade', np, optional=True, default=False)
    no_priced = _bool_col(table, 'no_priced_trade', np, optional=True, default=False)
    before = known_ok & end_ok & (known < end)
    return {
        'n': len(table), 'complete': complete, 'censored': left | right | roll | before,
        'last': last, 'last_ok': last_ok, 'high': high, 'high_ok': high_ok,
        'low': low, 'low_ok': low_ok, 'signed_open': signed_open, 'open_ok': open_ok,
        'signed_close': signed_close, 'close_ok': close_ok, 'buy': buy, 'buy_ok': buy_ok,
        'sell': sell, 'sell_ok': sell_ok, 'known_at_ns': known, 'known_ok': known_ok,
        'event_end_ns': end, 'event_start_ns': start, 'start_ok': start_ok,
        'latency_ns': latency, 'cut_ns': cut, 'instrument_id': inst,
        'horizon_minutes': minutes, 'horizon_minutes_ok': minutes_ok,
        'acquired_event_start_ns': acq_s, 'acquired_event_end_ns': acq_e,
        'no_new_trade': no_new, 'no_priced_trade': no_priced,
        'root': _str_list(table, 'root'), 'source_path': _str_list(table, 'source_path'),
        'source_metadata_sha256': _str_list(table, 'source_metadata_sha256'),
        'source_variant': _str_list(table, 'source_variant'),
        'contract_key': _str_list(table, 'contract_key', optional=True),
        'horizon_kind': _str_list(table, 'horizon_kind'),
        'label_id': _str_list(table, 'label_id', optional=True),
    }


def _classify_feature_rows(feat, calendar, np):
    cache = {}
    dates, years, stages, sessions, states = [], [], [], [], []
    for index in range(feat['n']):
        start = int(feat['event_start_ns'][index])
        cached = cache.get(start)
        if cached is None:
            end = int(feat['event_end_ns'][index])
            known = int(feat['known_at_ns'][index]) if feat['known_ok'][index] else start
            cached = classify_session(start, end, calendar=calendar, known_at_ns=known)
            cache[start] = cached
        eco = cached['economic_date']
        dates.append(eco)
        years.append(cached['year'])
        stages.append(stage_name(feat['root'][index], eco))
        sessions.append(cached['session'])
        states.append(cached['calendar_state'])
    return {
        'dates': dates, 'years': years, 'stages': stages,
        'sessions': sessions, 'calendar_states': states,
    }


def _join_identity(feat, i, lab, j):
    return (
        feat['root'][i] == lab['root'][j]
        and feat['source_path'][i] == lab['source_path'][j]
        and feat['source_metadata_sha256'][i] == lab['source_metadata_sha256'][j]
        and feat['source_variant'][i] == lab['source_variant'][j]
        and int(feat['acquired_event_start_ns'][i]) == int(lab['acquired_event_start_ns'][j])
        and int(feat['acquired_event_end_ns'][i]) == int(lab['acquired_event_end_ns'][j])
        and int(feat['instrument_id'][i]) == int(lab['instrument_id'][j])
        and int(feat['cut_ns'][i]) == int(lab['cut_ns'][j])
        and type(feat['contract_key'][i]) is str and feat['contract_key'][i]
        and feat['contract_key'][i] == lab['contract_key'][j]
    )


def _process_unit_tables(features, labels, *, collection, year, calendar, intervals, np,
                         groups, paired, event_acc, completeness, seen_keys, cuts_acc):
    feat = _extract_features(features, np)
    lab = _extract_labels(labels, np)
    meta = _classify_feature_rows(feat, calendar, np)
    completeness['feature_rows'] += feat['n']
    completeness['label_rows'] += lab['n']
    keep = [i for i, value in enumerate(meta['years']) if value == year]
    if not keep:
        return
    feat_by_key = defaultdict(list)
    for i in keep:
        key = (int(feat['instrument_id'][i]), int(feat['cut_ns'][i]), feat['contract_key'][i])
        dup = (
            feat['root'][i], int(feat['instrument_id'][i]),
            int(feat['cut_ns'][i]), int(feat['formation_minutes'][i]),
        )
        if dup in seen_keys:
            raise IntegrityError('duplicate root/instrument/cut/formation inside a collection')
        seen_keys.add(dup)
        feat_by_key[key].append(i)
        if feat['censored'][i]:
            completeness['censored_feature_rows'] += 1
        if meta['stages'][i] == 'unassigned':
            completeness['unassigned_stage_rows'] += 1
        completeness['economic_dates'].add(meta['dates'][i])
        completeness['calendar_state_counts'][meta['calendar_states'][i]] += 1
        cuts_acc.append({
            'cut_ns': int(feat['cut_ns'][i]),
            'event_start_ns': int(feat['event_start_ns'][i]),
            'formation_minutes': int(feat['formation_minutes'][i]),
            'instrument_id': int(feat['instrument_id'][i]),
            'contract_key': feat['contract_key'][i],
            'source_path': feat['source_path'][i],
            'source_metadata_sha256': feat['source_metadata_sha256'][i],
            'formation_id': feat['formation_id'][i],
            'index': i,
            'date': meta['dates'][i],
            'stage': meta['stages'][i],
            'session': meta['sessions'][i],
        })
        measurement_ok = bool(feat['quality'][i] and not feat['censored'][i])
        if measurement_ok:
            completeness['eligible_feature_rows'] += 1
            values = _feature_measurement_values(feat, i, np)
            gkey = (
                'feature', collection, feat['root'][i], year, meta['stages'][i],
                meta['sessions'][i], int(feat['formation_minutes'][i]), None, None, None,
            )
            store = _group_bucket(groups, gkey)
            day = meta['dates'][i]
            for name, value in values.items():
                store[name].add_one(day, value)
        elif not feat['inside'][i]:
            completeness['missing_reference_rows'] += 1
    lab_by_key = defaultdict(list)
    for j in range(lab['n']):
        if lab['censored'][j]:
            completeness['censored_label_rows'] += 1
        lab_by_key[(int(lab['instrument_id'][j]), int(lab['cut_ns'][j]), lab['contract_key'][j])].append(j)
    latency_buckets = defaultdict(dict)
    formation_buckets = defaultdict(dict)
    for key, fis in feat_by_key.items():
        ljs = lab_by_key.get(key)
        if not ljs:
            continue
        for i in fis:
            if not (feat['quality'][i] and not feat['censored'][i]):
                continue
            day = meta['dates'][i]
            stage = meta['stages'][i]
            session = meta['sessions'][i]
            formation = int(feat['formation_minutes'][i])
            ref_ok = bool(feat['inside'][i] and feat['ref_ok'][i])
            reference = int(feat['ref'][i]) if ref_ok else None
            past_close = int(feat['all_close'][i]) if feat['all_close_ok'][i] else None
            for j in ljs:
                if not lab['complete'][j] or lab['censored'][j]:
                    continue
                if not _join_identity(feat, i, lab, j):
                    continue
                latency = int(lab['latency_ns'][j])
                feature_known = _add_checked(int(feat['cut_ns'][i]), latency, what='feature_known_at_ns')
                feature_stage = _named_interval_stage(
                    feat['root'][i], int(feat['event_start_ns'][i]), feature_known, intervals)
                label_stage = _stage_of_ns(
                    lab['root'][j],
                    int(lab['known_at_ns'][j]) if lab['known_ok'][j] else None,
                    intervals,
                )
                if feature_stage == 'unassigned' or not lab['known_ok'][j] or feature_stage != label_stage:
                    continue
                completeness['eligible_joined_rows'] += 1
                last = int(lab['last'][j]) if lab['last_ok'][j] else None
                high = int(lab['high'][j]) if lab['high_ok'][j] else None
                low = int(lab['low'][j]) if lab['low_ok'][j] else None
                disp = future_displacements(reference, last, high, low)
                if lab['open_ok'][j] and lab['close_ok'][j]:
                    signed = int(lab['signed_close'][j]) - int(lab['signed_open'][j])
                elif lab['buy_ok'][j] and lab['sell_ok'][j]:
                    signed = int(lab['buy'][j]) - int(lab['sell'][j])
                else:
                    signed = None
                no_new = complete_binary_flag(bool(lab['no_new_trade'][j]), complete=True)
                no_priced = complete_binary_flag(bool(lab['no_priced_trade'][j]), complete=True)
                concord = directional_concordance(past_close, disp['terminal_return_ticks'])
                horizon_kind = lab['horizon_kind'][j]
                horizon_minutes = int(lab['horizon_minutes'][j]) if lab['horizon_minutes_ok'][j] else None
                gkey = (
                    'joined', collection, feat['root'][i], year, stage, session,
                    formation, latency, horizon_kind, horizon_minutes,
                )
                store = _group_bucket(groups, gkey)
                for name in JOINED_METRICS:
                    if name == 'future_signedflow':
                        store[name].add_one(day, signed)
                    elif name == 'no_new_trade':
                        store[name].add_one(day, no_new)
                    elif name == 'no_priced_trade':
                        store[name].add_one(day, no_priced)
                    elif name == 'concordance_both_nonzero':
                        if concord['both_nonzero']:
                            store[name].add_one(day, 1.0 if concord['concordant'] else 0.0)
                    elif name == 'zero_past_sign':
                        if past_close is not None:
                            store[name].add_one(day, 1.0 if concord['zero_past'] else 0.0)
                    elif name == 'zero_future_sign':
                        if disp['terminal_return_ticks'] is not None:
                            store[name].add_one(day, 1.0 if concord['zero_future'] else 0.0)
                    else:
                        store[name].add_one(day, disp.get(name))
                ref_tuple = (
                    int(feat['ref_at'][i]) if feat['ref_at_ok'][i] else None,
                    int(feat['ref_ord'][i]) if feat['ref_ord_ok'][i] else None,
                    reference,
                )
                payload = {
                    'day': day, 'stage': stage, 'session': session, 'root': feat['root'][i],
                    'terminal': disp['terminal_return_ticks'],
                    'up': disp['future_up_excursion_ticks'],
                    'down': disp['future_down_excursion_ticks'],
                    'no_new': no_new, 'ref': ref_tuple,
                    'formation_id': feat['formation_id'][i],
                    'label_id': lab['label_id'][j],
                    'cut_ns': int(feat['cut_ns'][i]),
                    'instrument_id': int(feat['instrument_id'][i]),
                    'contract_key': feat['contract_key'][i],
                }
                lat_key = (
                    int(feat['instrument_id'][i]), int(feat['cut_ns'][i]), feat['contract_key'][i],
                    formation, horizon_kind, horizon_minutes, session, stage,
                )
                latency_buckets[lat_key][latency] = payload
                form_key = (
                    int(feat['instrument_id'][i]), int(feat['cut_ns'][i]), feat['contract_key'][i],
                    latency, horizon_kind, horizon_minutes, session, stage,
                )
                formation_buckets[form_key][formation] = payload
    _accumulate_latency_pairs(latency_buckets, paired, collection, year)
    _accumulate_formation_pairs(formation_buckets, paired, collection, year)
    event_acc['latency_buckets'].append(latency_buckets)
    event_acc['cuts'].extend(cuts_acc[-len(keep):] if False else [])
    _ = cuts_acc


def _accumulate_latency_pairs(buckets, paired, collection, year):
    for key, arms in buckets.items():
        instrument, cut, contract, formation, horizon_kind, horizon_minutes, session, stage = key
        _ = instrument, cut, contract
        reference = arms.get(LATENCY_REFERENCE_NS)
        if reference is None:
            continue
        for alt in LATENCY_ALTERNATIVES_NS:
            other = arms.get(alt)
            if other is None or other['ref'] != reference['ref'] or other['ref'][2] is None:
                continue
            pkey = (
                'paired_latency', collection, reference['root'], year, stage, session,
                formation, alt, horizon_kind, horizon_minutes,
            )
            store = _group_bucket(paired, pkey)
            day = reference['day']
            store['own_reference_count'].add_one(day, 1.0)
            store['own_alternative_count'].add_one(day, 1.0)
            store['common_support'].add_one(day, 1.0)
            for metric, left, right in (
                ('terminal_return_ticks', other['terminal'], reference['terminal']),
                ('future_up_excursion_ticks', other['up'], reference['up']),
                ('future_down_excursion_ticks', other['down'], reference['down']),
                ('no_new_trade', other['no_new'], reference['no_new']),
            ):
                if left is None or right is None:
                    continue
                store[metric].add_one(day, float(left) - float(right))


def _accumulate_formation_pairs(buckets, paired, collection, year):
    for key, arms in buckets.items():
        instrument, cut, contract, latency, horizon_kind, horizon_minutes, session, stage = key
        _ = instrument, cut, contract
        own = {minutes: row for minutes, row in arms.items() if row['ref'][2] is not None}
        if not own:
            continue
        root = next(iter(own.values()))['root']
        day = next(iter(own.values()))['day']
        stage = next(iter(own.values()))['stage']
        session = next(iter(own.values()))['session']
        for minutes, row in own.items():
            pkey = (
                'formation_own', collection, root, year, stage, session,
                minutes, latency, horizon_kind, horizon_minutes,
            )
            _group_bucket(paired, pkey)['own_support'].add_one(day, 1.0)
        minutes_list = sorted(own)
        refs = {own[m]['ref'] for m in minutes_list}
        if len(minutes_list) == 4 and len(refs) == 1:
            pkey = (
                'formation_common4', collection, root, year, stage, session,
                None, latency, horizon_kind, horizon_minutes,
            )
            _group_bucket(paired, pkey)['common_support'].add_one(day, 1.0)
        for left_i, left_m in enumerate(minutes_list):
            for right_m in minutes_list[left_i + 1:]:
                left, right = own[left_m], own[right_m]
                if left['ref'] != right['ref']:
                    continue
                pkey = (
                    'paired_formation', collection, root, year, stage, session,
                    (left_m, right_m), latency, horizon_kind, horizon_minutes,
                )
                store = _group_bucket(paired, pkey)
                store['common_support'].add_one(day, 1.0)
                for metric, a, b in (
                    ('terminal_return_ticks', right['terminal'], left['terminal']),
                    ('future_up_excursion_ticks', right['up'], left['up']),
                    ('future_down_excursion_ticks', right['down'], left['down']),
                    ('no_new_trade', right['no_new'], left['no_new']),
                ):
                    if a is None or b is None:
                        continue
                    store[metric].add_one(day, float(a) - float(b))


def _event_link_row(event, cut, *, relative_bucket, in_formation, has_receiver, no_window):
    return {
        'semantic_id': event.get('semantic_id'),
        'event_type': event.get('event_type'),
        'event_date': event.get('event_date'),
        'event_ts_utc_ns': None if event.get('event_ts_utc_ns') is None else int(event['event_ts_utc_ns']),
        'time_basis': event.get('time_basis'),
        'time_precision': event.get('time_precision'),
        'status': event.get('status'),
        'source_path': None if cut is None else cut.get('source_path'),
        'source_metadata_sha256': None if cut is None else cut.get('source_metadata_sha256'),
        'formation_id': None if cut is None else cut.get('formation_id'),
        'label_id': None,
        'cut_ns': None if cut is None else int(cut['cut_ns']),
        'formation_minutes': None if cut is None else int(cut['formation_minutes']),
        'latency_ns': None,
        'horizon_kind': None,
        'horizon_minutes': None,
        'relative_bucket': relative_bucket,
        'in_formation': bool(in_formation),
        'has_eligible_receiver': bool(has_receiver),
        'no_window': bool(no_window),
        'known_at_ns': None,
        'causal_feature_eligible': False,
        'provenance_json': repr(event.get('provenance') or []),
    }


def _link_events(events, cuts, *, completeness):
    recorded_dates = set()
    links = []
    cut_index = defaultdict(list)
    for cut in cuts:
        cut_index[int(cut['cut_ns'])].append(cut)
    unique_cuts = sorted(cut_index)
    for event in events:
        event_date = event.get('event_date')
        if event_date:
            recorded_dates.add(event_date)
        timed = timed_event_eligible(event)
        if event.get('time_basis') == 'date_only' or not timed:
            completeness['date_only_events'] += 1
            linked = False
            for cut in cuts:
                if cut['date'] != event_date:
                    continue
                linked = True
                links.append(_event_link_row(
                    event, cut, relative_bucket='date_only', in_formation=False,
                    has_receiver=False, no_window=False,
                ))
            if not linked:
                completeness['events_without_window'] += 1
                links.append(_event_link_row(
                    event, None, relative_bucket='date_only', in_formation=False,
                    has_receiver=False, no_window=True,
                ))
            continue
        at = _py_int(event.get('event_ts_utc_ns'), what='event_ts_utc_ns')
        matched = False
        if unique_cuts:
            import numpy as np
            cuts_arr = np.asarray(unique_cuts, dtype=np.int64)
            lo = at - 60 * MINUTE_NS
            hi = at + 240 * MINUTE_NS
            left = int(np.searchsorted(cuts_arr, lo, side='left'))
            right = int(np.searchsorted(cuts_arr, hi, side='right'))
            for cut_ns in unique_cuts[left:right]:
                bucket = event_relative_bucket(at, cut_ns)
                for cut in cut_index[cut_ns]:
                    inside = event_in_formation(at, cut['event_start_ns'], cut['cut_ns'])
                    if bucket is None and not inside:
                        continue
                    matched = True
                    links.append(_event_link_row(
                        event, cut, relative_bucket=bucket, in_formation=inside,
                        has_receiver=False, no_window=False,
                    ))
        if not matched:
            completeness['events_without_window'] += 1
            links.append(_event_link_row(
                event, None, relative_bucket=None, in_formation=False,
                has_receiver=False, no_window=True,
            ))
    return links, recorded_dates


def _attach_event_receivers(links, latency_buckets, groups, collection, year):
    receivers = 0
    seen = set()
    for link in links:
        if link['cut_ns'] is None or link['formation_minutes'] is None:
            continue
        found = False
        day = link.get('event_date')
        etype = link.get('event_type') or 'unknown'
        bucket = link.get('relative_bucket') or 'unbucketed'
        for buckets in latency_buckets:
            for key, arms in buckets.items():
                instrument, cut, contract, formation, horizon_kind, horizon_minutes, session, stage = key
                _ = instrument, contract, session
                if cut != link['cut_ns'] or formation != link['formation_minutes']:
                    continue
                ref = arms.get(LATENCY_REFERENCE_NS)
                if ref is None:
                    continue
                found = True
                link['has_eligible_receiver'] = True
                link['label_id'] = ref.get('label_id')
                link['latency_ns'] = LATENCY_REFERENCE_NS
                link['horizon_kind'] = horizon_kind
                link['horizon_minutes'] = horizon_minutes
                gkey = (
                    'event', collection, ref['root'], year, stage, bucket,
                    etype, None, None, None,
                )
                store = _group_bucket(groups, gkey)
                if day:
                    store['terminal_return_ticks'].add_one(day, ref.get('terminal'))
                    store['future_up_excursion_ticks'].add_one(day, ref.get('up'))
                    store['future_down_excursion_ticks'].add_one(day, ref.get('down'))
                    store['no_new_trade'].add_one(day, ref.get('no_new'))
                for alt_ns in LATENCY_ALTERNATIVES_NS:
                    alt = arms.get(alt_ns)
                    if alt is None or alt.get('ref') != ref.get('ref'):
                        continue
                    if day and alt.get('terminal') is not None and ref.get('terminal') is not None:
                        pkey = (
                            'event_paired_latency', collection, ref['root'], year, stage, bucket,
                            etype, alt_ns, horizon_kind, horizon_minutes,
                        )
                        _group_bucket(groups, pkey)['terminal_return_ticks'].add_one(
                            day, float(alt['terminal']) - float(ref['terminal']))
                break
            if found:
                break
        if found and link.get('semantic_id') not in seen:
            seen.add(link.get('semantic_id'))
            receivers += 1
    return receivers


def _event_table(links, pa):
    names = (
        'semantic_id', 'event_type', 'event_date', 'event_ts_utc_ns', 'time_basis',
        'time_precision', 'status', 'source_path', 'source_metadata_sha256',
        'formation_id', 'label_id', 'cut_ns', 'formation_minutes', 'latency_ns',
        'horizon_kind', 'horizon_minutes', 'relative_bucket', 'in_formation',
        'has_eligible_receiver', 'no_window', 'known_at_ns', 'causal_feature_eligible',
        'provenance_json',
    )
    integers = {
        'event_ts_utc_ns', 'cut_ns', 'formation_minutes', 'latency_ns',
        'horizon_minutes', 'known_at_ns',
    }
    booleans = {'in_formation', 'has_eligible_receiver', 'no_window', 'causal_feature_eligible'}
    columns = {}
    for name in names:
        values = [row.get(name) for row in links]
        if name in integers:
            columns[name] = pa.array(values, type=pa.int64())
        elif name in booleans:
            columns[name] = pa.array(values, type=pa.bool_())
        else:
            columns[name] = pa.array(values, type=pa.string())
    return pa.table(columns)


def _date_aggregate_schema(pa):
    return pa.schema([
        ('group_kind', pa.string()), ('source_collection', pa.string()),
        ('root', pa.string()), ('year', pa.int64()), ('stage', pa.string()),
        ('session', pa.string()), ('formation_minutes', pa.int64()),
        ('latency_ns', pa.int64()), ('horizon_kind', pa.string()),
        ('horizon_minutes', pa.int64()), ('contrast', pa.string()),
        ('metric', pa.string()), ('economic_date', pa.string()),
        ('observation_count', pa.int64()), ('sum', pa.float64()), ('mean', pa.float64()),
    ])


def _date_rows_from_groups(groups):
    rows = []
    for key, stores in groups.items():
        kind, collection, root, year, stage, session, formation, latency, horizon_kind, horizon_minutes = key
        contrast = None
        formation_out = formation
        if isinstance(formation, tuple):
            contrast = f'{formation[0]}_vs_{formation[1]}'
            formation_out = None
        elif kind == 'paired_latency':
            contrast = f'{latency}_vs_{LATENCY_REFERENCE_NS}'
        for metric, store in stores.items():
            for day, count in store.date_count.items():
                total = store.date_sum[day]
                rows.append({
                    'group_kind': kind, 'source_collection': collection, 'root': root,
                    'year': int(year), 'stage': stage,
                    'session': None if session is None else str(session),
                    'formation_minutes': None if formation_out is None else int(formation_out),
                    'latency_ns': None if latency is None else int(latency),
                    'horizon_kind': horizon_kind,
                    'horizon_minutes': None if horizon_minutes is None else int(horizon_minutes),
                    'contrast': contrast, 'metric': metric, 'economic_date': day,
                    'observation_count': int(count), 'sum': float(total),
                    'mean': float(total / count) if count else None,
                })
    return rows


def _date_table(rows, pa):
    schema = _date_aggregate_schema(pa)
    if not rows:
        return pa.table({field.name: pa.array([], type=field.type) for field in schema}, schema=schema)
    return pa.table(
        {field.name: pa.array([row[field.name] for row in rows], type=field.type) for field in schema},
        schema=schema,
    )


def _exact_quantiles(values, levels):
    if not values:
        return {str(level): None for level in levels}
    import numpy as np
    ordered = np.asarray(values, dtype=np.float64)
    quantiles = np.quantile(ordered, levels, method='linear')
    return {str(level): float(item) for level, item in zip(levels, quantiles)}


def _metric_payload(store, intended, stats_result=None):
    counts = store.date_count
    missing = sum(1 for day in intended if counts.get(day, 0) == 0)
    date_means = [store.date_sum[day] / counts[day] for day in sorted(counts) if counts[day]]
    payload = {
        'unit': None,
        'eligible_observations': store.n,
        'eligible_independent_dates': len(counts),
        'missing_date_count': missing,
        'observation_moments': {
            'count': store.n,
            'mean': None if store.n == 0 else store.total / store.n,
            'minimum': store.minimum,
            'maximum': store.maximum,
            'sum': store.total,
        },
        'sample_quantiles': _exact_quantiles(date_means, QUANTILE_LEVELS),
        'date_mean': None,
        'event_mean': None,
        'support': {
            'independent_dates': len(counts),
            'events': store.n,
            'sparse': store.n == 0 or len(counts) == 0,
            'reasons': [] if store.n else ['no_valid_observations'],
        },
        'bootstrap': None,
    }
    if stats_result is not None:
        payload['date_mean'] = {
            'estimate': stats_result.get('estimate'),
            'actual_valid_date_count': stats_result.get('actual_valid_date_count'),
            'actual_valid_event_count': stats_result.get('actual_valid_event_count'),
            'support': stats_result.get('support'),
            'bootstrap': stats_result.get('bootstrap'),
        }
        payload['support'] = stats_result.get('support') or payload['support']
        payload['bootstrap'] = stats_result.get('bootstrap')
    return payload


def _group_record(key, intended, metrics_out):
    kind, collection, root, year, stage, session, formation, latency, horizon_kind, horizon_minutes = key
    contrast = None
    formation_out = formation
    if isinstance(formation, tuple):
        contrast = f'{formation[0]}_vs_{formation[1]}'
        formation_out = None
    return {
        'group_kind': kind, 'source_collection': collection, 'root': root,
        'year': int(year), 'stage': stage, 'session': session,
        'formation_minutes': formation_out, 'latency_ns': latency,
        'horizon_kind': horizon_kind, 'horizon_minutes': horizon_minutes,
        'contrast': contrast, 'metrics': metrics_out,
        'intended_dates': list(intended), 'intended_date_count': len(intended),
        'family_complete': False,
    }


def _empty_group(key, intended, stores):
    metrics = {name: {**_undefined_metric(), 'unit': _metric_unit(name)} for name in stores}
    if not metrics:
        metrics = {'undefined': _undefined_metric()}
    record = _group_record(key, intended, metrics)
    for payload in record['metrics'].values():
        payload['missing_date_count'] = len(intended)
    return record


def _finalize_groups(groups, *, intended_by_stage, stats, np):
    seed = int(stats.get('seed', 20260908))
    block = int(stats.get('block_length_dates', 5))
    replicates = int(stats.get('bootstrap_replicates', 1000))
    confidence = float(stats.get('confidence', 0.95))
    min_dates = int(stats.get('minimum_dates', 100))
    min_events = int(stats.get('minimum_events', 20))
    finalized = []
    by_universe = defaultdict(list)
    for key in groups:
        by_universe[(key[2], key[3], key[4])].append(key)
    for (root, year, stage), keys in by_universe.items():
        intended = list(intended_by_stage.get((root, year, stage), ()))
        if not intended:
            intended = sorted({
                day for key in keys for store in groups[key].values() for day in store.date_count
            })
        if not intended:
            for key in keys:
                finalized.append(_empty_group(key, intended, groups[key]))
            continue
        weights, starts = _moving_weights(
            np, len(intended), seed=seed, block_length=block, replicates=replicates)
        state = (np, weights, starts)
        for key in sorted(keys, key=lambda item: tuple(str(part) for part in item)):
            stores = groups[key]
            names = tuple(stores)
            if not names:
                finalized.append(_empty_group(key, intended, stores))
                continue
            metrics_out = {}
            for offset in range(0, len(names), STAT_BATCH):
                batch = names[offset:offset + STAT_BATCH]
                cells = {}
                for name in batch:
                    store = stores[name]
                    cells[name] = {
                        day: store.date_sum[day] / store.date_count[day]
                        for day in store.date_count if store.date_count[day]
                    }
                result = observed_date_statistics(
                    cells, intended, estimator='date_mean', seed=seed,
                    block_length=block, replicates=replicates, confidence=confidence,
                    minimum_independent_dates=min_dates, minimum_events=min_events,
                    _retain_replicate_estimates=False, _bootstrap_state=state,
                )
                for name in batch:
                    payload = _metric_payload(stores[name], intended, result['metrics'][name])
                    payload['unit'] = _metric_unit(name)
                    metrics_out[name] = payload
            finalized.append(_group_record(key, intended, metrics_out))
    return finalized


def _write_series_table(outputs, name, table):
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


def _markdown_report(*, groups, paired, completeness, population, processed, cpu, output_bytes,
                     reused, recomputed, selected, all_keys, event_stats):
    lines = [
        '# Auction/flow window, formation and event-timing statistics',
        '',
        'Descriptive formation-length, availability-delay, forward-label and scheduled-event '
        'timing measurements. This does not complete the auction/flow family, select a source '
        'or clock winner, or claim causal news impact.',
        '',
        f'- family_complete: false',
        f'- complete_family_statistics: false',
        f'- population_source_windows: {population.get("population_source_windows")}',
        f'- processed_source_windows: {processed}',
        f'- unavailable_source_windows: {completeness["unavailable_source_windows"]}',
        f'- feature_rows: {completeness["feature_rows"]}',
        f'- label_rows: {completeness["label_rows"]}',
        f'- eligible_feature_rows: {completeness["eligible_feature_rows"]}',
        f'- eligible_joined_rows: {completeness["eligible_joined_rows"]}',
        f'- censored_feature_rows: {completeness["censored_feature_rows"]}',
        f'- unassigned_stage_rows: {completeness["unassigned_stage_rows"]}',
        f'- independent_economic_dates: {len(completeness["economic_dates"])}',
        f'- reused_partitions: {reused}',
        f'- new_partitions: {recomputed}',
        f'- selected_partitions: {len(selected)}',
        f'- declared_partitions: {len(all_keys)}',
        f'- cpu_seconds: {cpu}',
        f'- output_bytes: {output_bytes}',
        '',
        'Date means give one weight per economic date. Multiple cuts or overlapping windows '
        'on the same date are dependent observations, not extra independent dates. Monthly and '
        'weekly acquisitions keep separate primary inference.',
        '',
        'Price units are raw ticks (0.25 index point). Labels store absolute future prices; '
        'displacements are derived from each feature reference. A complete quiet window is '
        'no-new-trade = 1 with a null price, not a zero return. Missing coverage stays missing.',
        '',
        'True CVD/OFI path range uses high-low, never close extrema. Hard cohort volumes overlap '
        'and are not a partition. Standing and pressure metrics use their own eligible masks.',
        '',
        'Directional concordance is the paired observed frequency that sign(formation all-CVD close) '
        'matches sign(terminal return), only when both signs are nonzero. Zero-past and zero-future '
        'are separate denominators. This is not model accuracy or predictive gain.',
        '',
        'Scheduled event labels are retrospective: known_at is NULL and causal_feature_eligible is '
        'false. Dates without an event record are unknown coverage. Events with no eligible '
        'receiver or no nearby window remain in the event denominator.',
        '',
        '## Event coverage',
        '',
        f'- source_event_rows: {event_stats.get("source_event_rows", completeness["event_source_rows"])}',
        f'- unique_semantic_events: {event_stats.get("unique_semantic_events", completeness["unique_semantic_events"])}',
        f'- events_with_receiver: {completeness["events_with_receiver"]}',
        f'- events_without_receiver: {completeness["events_without_receiver"]}',
        f'- events_without_window: {completeness["events_without_window"]}',
        f'- date_only_events: {completeness["date_only_events"]}',
        f'- unknown_event_coverage_dates: {completeness["unknown_event_coverage_dates"]}',
        '',
        '## Groups',
        '',
        '| kind | collection | root | year | stage | session | formation | latency | horizon | metric | date-mean | dates | events | missing |',
        '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|',
    ]
    shown = 0
    for group in groups:
        for name, metric in sorted(group.get('metrics', {}).items()):
            mean = metric.get('date_mean') or {}
            estimate = mean.get('estimate') if isinstance(mean, dict) else None
            support = metric.get('support') or {}
            lines.append(
                f"| {group.get('group_kind')} | {group.get('source_collection')} | "
                f"{group.get('root')} | {group.get('year')} | {group.get('stage')} | "
                f"{group.get('session')} | {group.get('formation_minutes')} | "
                f"{group.get('latency_ns')} | {group.get('horizon_kind')}:{group.get('horizon_minutes')} | "
                f"{name} | {estimate} | {support.get('independent_dates')} | "
                f"{support.get('events')} | {metric.get('missing_date_count')} |"
            )
            shown += 1
            if shown >= 80:
                break
        if shown >= 80:
            lines.append('')
            lines.append(f'Showing the first {shown} metric rows of {len(groups)} groups.')
            break
    if not groups:
        lines.append('No eligible groups were observed in the selected partitions.')
    lines.extend([
        '',
        '## Paired contrasts',
        '',
        f'- paired contrast groups: {len(paired)}',
        '',
        'Latency contrasts compare 0 ns and 1 s against 250 ms on the same physical '
        'source/cut/instrument/raw contract, formation, horizon and actual reference. '
        'Formation contrasts compare 5/15/60/240 on the same cut, target and actual '
        'reference, with separate own-support and common-support counts. A repeated '
        'forward target is not counted as independent evidence. Primary eligible-group '
        'statistics stay in the group tables above.',
        '',
    ])
    return '\n'.join(lines) + '\n'


def _merge_completeness(total, part):
    for name, value in part.items():
        if name == 'economic_dates':
            total[name].update(value)
        elif name == 'calendar_state_counts':
            total[name].update(value)
        elif name in total and isinstance(value, (int, float)):
            total[name] += value


def _compute_window_partition(*, key, members, identity, source_refs, contract, stats, policy,
                              calendar, events, outputs, ordinal, np, pa):
    collection, root, year = key
    began, wall_began, before = time_mod.process_time(), time_mod.monotonic(), outputs.written
    groups = {}
    paired = {}
    completeness = _empty_completeness()
    completeness['source_windows'] = len(members)
    seen_keys = set()
    cuts = []
    latency_bucket_sets = []
    intervals = _civil_stage_intervals(policy)
    primary = contract.get('primary_population') or {}
    intended_by_stage = {}
    for stage in (*STAGE_ORDER, 'unassigned'):
        intended_by_stage[(root, year, stage)] = intended_date_universe(
            year, stage, root, policy,
            primary.get('start', '2020-01-01'), primary.get('end', '2026-09-04'),
        )
    for unit in members:
        completeness['processed_source_windows'] += 1
        start, end = _unit_window_ns(unit)
        completeness['economic_dates'].add(economic_date(int(start)))
        completeness['economic_dates'].add(economic_date(int(end - 1)))
        if _unit_unavailable(unit):
            completeness['unavailable_source_windows'] += 1
            continue
        feature_tables = list(read_series_tables(unit['features']))
        label_tables = list(read_series_tables(unit['labels']))
        features = _concat_tables(feature_tables, pa)
        labels = _concat_tables(label_tables, pa)
        del feature_tables, label_tables
        if features is None or labels is None:
            completeness['unavailable_source_windows'] += 1
            continue
        event_acc = {'latency_buckets': [], 'cuts': []}
        unit_cuts = []
        _process_unit_tables(
            features, labels, collection=collection, year=year, calendar=calendar,
            intervals=intervals, np=np, groups=groups, paired=paired,
            event_acc=event_acc, completeness=completeness, seen_keys=seen_keys,
            cuts_acc=unit_cuts,
        )
        cuts.extend(unit_cuts)
        latency_bucket_sets.extend(event_acc['latency_buckets'])
        del features, labels, unit_cuts
    links, recorded_dates = _link_events(events, cuts, completeness=completeness)
    receivers = _attach_event_receivers(links, latency_bucket_sets, groups, collection, year)
    completeness['events_with_receiver'] += receivers
    unique_events = {link.get('semantic_id') for link in links}
    completeness['unique_semantic_events'] += len(unique_events)
    completeness['events_without_receiver'] += max(0, len(unique_events) - receivers)
    intended_dates = []
    for stage in (*STAGE_ORDER, 'unassigned'):
        intended_dates.extend(intended_by_stage[(root, year, stage)])
    unknown = sum(1 for day in intended_dates if event_coverage_state(day in recorded_dates) == 'unknown')
    completeness['unknown_event_coverage_dates'] += unknown
    finalized = _finalize_groups(groups, intended_by_stage=intended_by_stage, stats=stats, np=np)
    paired_out = _finalize_groups(paired, intended_by_stage=intended_by_stage, stats=stats, np=np)
    date_rows = _date_rows_from_groups(groups) + _date_rows_from_groups(paired)
    prefix = f'window-{ordinal:03d}-{collection}-{root}-{year}'
    denominators = _write_series_table(outputs, prefix + '-date-metrics', _date_table(date_rows, pa))
    event_links = _write_series_table(outputs, prefix + '-event-links', _event_table(links, pa))
    group_ref = outputs.json(prefix + '-groups.json', {
        'kind': 'auction_flow_window_group_statistics_v1',
        'groups': finalized, 'source_refs': source_refs, 'source_collection': collection,
        'root': root, 'economic_year': year, 'family_complete': False,
    }, kind='auction_flow_window_group_statistics_v1')
    paired_ref = outputs.json(prefix + '-paired.json', {
        'kind': 'auction_flow_window_paired_contrasts_v1',
        'groups': paired_out, 'source_collection': collection, 'root': root,
        'economic_year': year, 'family_complete': False,
        'latency_reference_ns': LATENCY_REFERENCE_NS,
        'latency_alternatives_ns': list(LATENCY_ALTERNATIVES_NS),
        'formation_minutes': list(FORMATION_MINUTES),
    }, kind='auction_flow_window_paired_contrasts_v1')
    completeness_out = {
        **completeness,
        'economic_dates': sorted(completeness['economic_dates']),
        'calendar_state_counts': dict(completeness['calendar_state_counts']),
    }
    measurement = {
        'cpu_seconds': time_mod.process_time() - began,
        'wall_seconds': time_mod.monotonic() - wall_began,
        'output_bytes': outputs.written - before,
        'feature_rows': completeness['feature_rows'],
        'label_rows': completeness['label_rows'],
        'observations': completeness['feature_rows'] + completeness['label_rows'],
    }
    part = {
        'kind': 'auction_flow_window_partition_v1', 'passed': True, 'identity': identity,
        'source_collection': collection, 'root': root, 'economic_year': year,
        'source_refs': source_refs, 'groups': group_ref, 'denominators': denominators,
        'paired': paired_ref, 'event_links': event_links, 'group_count': len(finalized),
        'measurement': measurement, 'completeness': completeness_out, 'family_complete': False,
    }
    ref = outputs.json(prefix + '-partition.json', part, kind='auction_flow_window_partition_v1')
    return ref, part, measurement


def run_window_statistics(*, population, contract, outputs, load_reference,
                          selected_partition_keys=None):
    """Reduce one collection/root/economic-year at a time from window unit tables."""
    if not isinstance(outputs, BoundedOutputs) or not callable(load_reference):
        raise ContractError('bounded outputs and authenticated reference loader required')
    rec = _mapping(population, what='population')
    if rec.get('kind') != POPULATION_KIND:
        raise IntegrityError('authenticated auction_flow_window_population_v1 required')
    frozen, stats, policy, collections = _require_contract(contract)
    calendar = _load_calendar(frozen, load_reference)
    raw_events, event_ref = _load_events(frozen)
    events, event_stats = dedup_scheduled_events(raw_events)
    started, wall_started = time_mod.process_time(), time_mod.monotonic()
    units = rec.get('units')
    if not isinstance(units, list) or not units:
        raise IntegrityError('window population lost its unit summaries')
    plan = window_partition_plan(units, collections=collections)
    if selected_partition_keys is None:
        selected_keys = list(plan['keys'])
        subset = False
    else:
        if not isinstance(selected_partition_keys, list):
            raise IntegrityError('selected_partition_keys must be a list of partition keys')
        selected_keys = [decode_window_partition_key(key) for key in selected_partition_keys]
        known = set(plan['keys'])
        if any(key not in known for key in selected_keys):
            raise IntegrityError('selected_partition_keys are not members of the authenticated population')
        if len(set(selected_keys)) != len(selected_keys):
            raise IntegrityError('selected_partition_keys contain a duplicate')
        subset = selected_keys != list(plan['keys'])
    accepted = {}
    for ref in frozen.get('accepted_partitions', []) or []:
        row = load_reference(ref, maximum=128 * 1024 ** 2)
        accepted[row['identity']] = (ref, row)
    total = _empty_completeness()
    total['event_source_rows'] = event_stats['source_event_rows']
    partition_refs, group_refs, denominator_refs, paired_refs, event_link_refs = [], [], [], [], []
    reused, recomputed, measurements = 0, 0, []
    finalized_groups, finalized_paired = [], []
    np = pa = None
    for ordinal, key in enumerate(selected_keys):
        collection, root, year = key
        members = plan['members'][key]
        source_refs = window_partition_source_refs(members)
        identity = window_partition_identity(
            frozen, collection=collection, root=root, year=year, source_refs=source_refs)
        if identity in accepted and accepted[identity][1].get('passed') is True:
            ref, part = accepted[identity]
            reused += 1
        else:
            if np is None:
                np, pa = _require_numpy(), _require_pyarrow()
            ref, part, measurement = _compute_window_partition(
                key=key, members=members, identity=identity, source_refs=source_refs,
                contract=frozen, stats=stats, policy=policy, calendar=calendar,
                events=events, outputs=outputs, ordinal=ordinal, np=np, pa=pa,
            )
            recomputed += 1
            measurements.append({**measurement, 'partition_key': encode_window_partition_key(key)})
        partition_refs.append(ref)
        group_refs.append(part['groups'])
        denominator_refs.append(part['denominators'])
        paired_refs.append(part.get('paired'))
        event_link_refs.append(part.get('event_links'))
        _merge_completeness(total, part['completeness'])
    cpu = time_mod.process_time() - started
    wall = time_mod.monotonic() - wall_started
    for ref in group_refs:
        if isinstance(ref, dict) and ref.get('path'):
            import json
            payload = json.loads(Path(ref['path']).read_bytes())
            finalized_groups.extend(payload.get('groups') or [])
    for ref in paired_refs:
        if isinstance(ref, dict) and ref.get('path'):
            import json
            payload = json.loads(Path(ref['path']).read_bytes())
            finalized_paired.extend(payload.get('groups') or [])
    completeness_out = {
        **total,
        'economic_dates': sorted(total['economic_dates']),
        'independent_economic_dates': len(total['economic_dates']),
        'calendar_state_counts': dict(total['calendar_state_counts']),
        'date_inference_is_separate_by_source_collection': True,
        'full_111_source_intersection_not_required': True,
        'family_complete': False,
        'selected_partition_subset': subset,
        'event_source': event_ref,
        'event_selection': event_stats,
    }
    completeness_ref = outputs.json(
        'window-statistics-completeness.json', completeness_out,
        kind='auction_flow_window_completeness_v1')
    report_text = _markdown_report(
        groups=finalized_groups, paired=finalized_paired, completeness=total,
        population=rec, processed=total['processed_source_windows'], cpu=cpu,
        output_bytes=outputs.written, reused=reused, recomputed=recomputed,
        selected=selected_keys, all_keys=plan['keys'], event_stats=event_stats,
    )
    with outputs.create('window-measurement-statistics-report.md') as stream:
        stream.write(report_text.encode())
    report_ref = outputs.reference(
        'window-measurement-statistics-report.md', kind='auction_flow_window_statistics_report')
    counts = {
        'population_source_windows': rec.get('population_source_windows', len(units)),
        'processed_source_windows': total['processed_source_windows'],
        'unavailable_source_windows': total['unavailable_source_windows'],
        'feature_rows': total['feature_rows'],
        'label_rows': total['label_rows'],
        'eligible_feature_rows': total['eligible_feature_rows'],
        'eligible_joined_rows': total['eligible_joined_rows'],
        'censored_feature_rows': total['censored_feature_rows'],
        'unassigned_stage_rows': total['unassigned_stage_rows'],
        'independent_economic_dates': len(total['economic_dates']),
        'unique_semantic_events': total['unique_semantic_events'],
        'events_without_receiver': total['events_without_receiver'],
        'events_without_window': total['events_without_window'],
        'declared_partitions': len(plan['keys']),
        'selected_partitions': len(selected_keys),
        'reused_partitions': reused,
        'new_partitions': recomputed,
    }
    summary = {
        'kind': KIND, 'version': VERSION, 'passed': True, 'family_complete': False,
        'complete_family_statistics': False, 'all_family_validation_complete': False,
        'full_window_population_reduced': (not subset) and len(selected_keys) == len(plan['keys']),
        'selected_partition_subset': subset, 'counts': counts,
        'partition_measurements': measurements, 'cpu_seconds': cpu, 'wall_seconds': wall,
        'output_bytes': outputs.written, 'reused_partitions': reused, 'new_partitions': recomputed,
        'partition_keys': [encode_window_partition_key(key) for key in selected_keys],
        'refs': {
            'partitions': partition_refs, 'groups': group_refs, 'denominators': denominator_refs,
            'paired': paired_refs, 'event_links': event_link_refs,
            'completeness': completeness_ref, 'report': report_ref,
            'event_source': event_ref, 'cash_calendar': getattr(calendar, 'reference', None),
        },
    }
    summary_ref = outputs.json('window-statistics-summary.json', summary, kind=KIND)
    summary['refs']['summary'] = summary_ref
    return summary


__all__ = [
    'FEATURE_QUALITY_FLAGS', 'FROZEN_CONTRACT_KIND', 'KIND', 'POPULATION_KIND', 'VERSION',
    'alias_collection_dates', 'cohort_signed_fraction', 'cohort_volume_fraction',
    'complete_binary_flag', 'decode_window_partition_key', 'dedup_scheduled_events',
    'directional_concordance', 'encode_window_partition_key', 'equal_date_mean',
    'event_coverage_state', 'event_in_formation', 'event_relative_bucket',
    'feature_quality_eligible', 'formation_pair_eligible', 'formation_volume_per_second',
    'future_displacements', 'intended_date_universe', 'known_at_available_at_cut',
    'latency_pair_eligible', 'reference_inside_formation', 'run_window_statistics',
    'same_actual_reference', 'scientific_contract_definition', 'scientific_join_eligibility',
    'timed_event_eligible', 'true_path_range', 'unknown_volume_fraction',
    'window_partition_identity', 'window_partition_plan',
]




