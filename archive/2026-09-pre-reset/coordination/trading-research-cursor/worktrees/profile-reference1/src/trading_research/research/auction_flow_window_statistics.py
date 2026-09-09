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
import bisect
import json
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
COHORT_METRICS = tuple(
    f'{cohort}_{suffix}'
    for cohort in SOURCE_FILTERS if cohort != 'all'
    for suffix in ('volume_fraction', 'signed_fraction', 'true_CVD_path_range')
)
MEASUREMENT_METRICS = (
    'formationvolume_per_second', 'unknown_volume_fraction',
    'formation_price_range_ticks', 'VWAP_variance_ticks_squared',
    'standing_mean_spread_ticks', 'OFI_path_range_on_pressureeligible',
) + COHORT_METRICS
JOINED_METRICS = (
    'terminal_return_ticks', 'future_up_excursion_ticks', 'future_down_excursion_ticks',
    'future_path_range_ticks', 'future_signedflow', 'no_new_trade', 'no_priced_trade',
    'concordance_both_nonzero', 'zero_past_sign', 'zero_future_sign',
)
PAIRED_LATENCY_METRICS = (
    'terminal_return_ticks', 'future_up_excursion_ticks', 'future_down_excursion_ticks',
    'no_new_trade',
)
FORMATION_FEATURE_PAIR_METRICS = MEASUREMENT_METRICS
OPERATIONAL_CONTRACT_FIELDS = (
    'phase', 'pilot_source_paths', 'accepted_partitions', 'selected_partition_keys',
    'accepted_pilot_execution', 'accepted_pilot_worker', 'accepted_consumer_files',
    'parallel_execution', 'cash_session_table', 'event_rows',
)
_GFIELDS = (
    'group_kind', 'source_collection', 'root', 'year', 'stage', 'session',
    'formation_minutes', 'latency_ns', 'horizon_kind', 'horizon_minutes',
    'event_type', 'time_precision', 'status', 'relative_bucket', 'contrast',
)
_INT64_MIN = -(2 ** 63)
_INT64_MAX = 2 ** 63 - 1
_SHA_LEN = 64
BATCH_HINT = 65536
LINK_BATCH = 4096
JSON_LOAD_MAX = 128 * 1024 ** 2
EVENT_LOOKBACK_NS = 240 * MINUTE_NS
EVENT_LOOKAHEAD_NS = 60 * MINUTE_NS


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
    return 1.0 if value else 0.0


def directional_concordance(past_close, terminal_return):
    """Paired observed sign frequency. Not accuracy or predictive gain.

    Past and future zero flags use their own validity. A missing future price
    does not invent a past-zero observation of 0, and a missing past does not
    invent a future-zero observation.
    """
    past = signed_sign(past_close)
    future = signed_sign(terminal_return)
    zero_past = past == 0 if past is not None else False
    zero_future = future == 0 if future is not None else False
    if past is None or future is None:
        return {
            'category': 'missing', 'concordant': None,
            'zero_past': zero_past, 'zero_future': zero_future, 'both_nonzero': False,
            'past_valid': past is not None, 'future_valid': future is not None,
        }
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
        'past_valid': True,
        'future_valid': True,
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
    """Identity/stage join plus quality, completeness, clocks and no censor/roll.

    Stored feature known_at is the source-clock publication time. The helper
    scenario used by join_window_eligibility remains feature_known_at = cut +
    label.latency. Priced displacements additionally require a reference
    strictly inside the formation; that check is not a join-identity rule.
    """
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
    cut = feature.get('cut_ns')
    latency = label.get('latency_ns')
    start = label.get('event_start_ns')
    end = label.get('event_end_ns')
    known = label.get('known_at_ns')
    if cut is None or latency is None or start is None:
        return {**join, 'eligible': False, 'scientific_reason': 'label_start_not_cut_plus_latency'}
    if int(start) != _add_checked(int(cut), int(latency), what='label_start_ns'):
        return {**join, 'eligible': False, 'scientific_reason': 'label_start_not_cut_plus_latency'}
    if end is None or known is None:
        return {**join, 'eligible': False, 'scientific_reason': 'label_before_maturity'}
    if int(known) < int(end):
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


def event_clock_consistent(event):
    """Timestamp and event_date must share one economic clock. Originals are retained."""
    event = _mapping(event, what='event')
    ts = event.get('event_ts_utc_ns')
    day = event.get('event_date')
    if ts is None or type(day) is not str or not day:
        return True
    try:
        return economic_date(_py_int(ts, what='event_ts_utc_ns')) == day
    except (ContractError, IntegrityError, ValueError, OverflowError, OSError):
        return False


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


def _gkey(**kwargs):
    extra = set(kwargs).difference(_GFIELDS)
    if extra:
        raise IntegrityError(f'unknown group metadata fields {sorted(extra)}')
    return tuple(kwargs.get(name) for name in _GFIELDS)


def _gmeta(key):
    if not isinstance(key, tuple) or len(key) != len(_GFIELDS):
        raise IntegrityError('group key lost its typed metadata')
    return dict(zip(_GFIELDS, key))


def _provenance_json(value):
    return json.dumps(value if value is not None else [], separators=(',', ':'), sort_keys=True)


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


def _unit_identity_key(unit):
    ident = unit.get('source_identity') or {}
    uid = unit.get('unit_id')
    return (
        ident.get('source_path') or _unit_path(unit),
        ident.get('source_metadata_sha256'),
        ident.get('acquired_event_start_ns'),
        ident.get('acquired_event_end_ns'),
        tuple(uid) if isinstance(uid, (list, tuple)) else uid,
    )


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
        if values is None or day is None:
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
        'out_of_primary_year_rows': 0, 'source_windows': 0, 'economic_dates': set(),
        'calendar_state_counts': Counter(),
        'event_source_rows': 0, 'unique_semantic_events': 0, 'events_with_receiver': 0,
        'events_without_receiver': 0, 'events_without_window': 0, 'date_only_events': 0,
        'unknown_event_coverage_dates': 0, 'inconsistent_event_clock_rows': 0,
    }


def _metric_unit(name):
    if name in (
        'own_reference_count', 'own_alternative_count', 'common_support', 'own_support',
    ) or name.endswith('_count') or name.endswith('_support'):
        return 'count'
    if (
        'fraction' in name or name.startswith('zero_') or name.startswith('concordance')
        or name in ('no_new_trade', 'no_priced_trade')
    ):
        return 'dimensionless'
    if name.endswith('_per_second') or 'volume_per_second' in name:
        return 'contracts_per_second'
    if 'variance' in name:
        return 'ticks_squared'
    if name in (
        'OFI_path_range_on_pressureeligible', 'future_signedflow',
    ) or name.endswith('true_CVD_path_range') or 'signedflow' in name:
        return 'contracts'
    if name.endswith('_ticks') or 'excursion' in name:
        return 'quarter_point_ticks'
    return 'dimensionless'


def _undefined_metric(*, unit=None):
    return {
        'unit': unit, 'estimate': None, 'date_mean': None, 'event_mean': None,
        'eligible_observations': 0, 'eligible_independent_dates': 0,
        'missing_date_count': None, 'sample_quantiles': {str(level): None for level in QUANTILE_LEVELS},
        'sample_quantile_distribution': 'equal_weight_date_mean',
        'support': {'independent_dates': 0, 'events': 0, 'sparse': True,
                    'reasons': ['no_valid_observations']},
        'bootstrap': None, 'undefined': True,
    }


def _stores():
    return defaultdict(_DateStore)


def _group_bucket(groups, key):
    bucket = groups.get(key)
    if bucket is None:
        bucket = _stores()
        groups[key] = bucket
    return bucket


def _feature_measurement_values(feat, i):
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
    out['VWAP_variance_ticks_squared'] = float(feat['variance'][i]) if feat['var_ok'][i] else None
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
        if cohort == 'all':
            continue
        cvol = int(feat[f'{cohort}_volume'][i]) if feat[f'{cohort}_volume_ok'][i] else None
        cbuy = int(feat[f'{cohort}_buy'][i]) if feat[f'{cohort}_buy_ok'][i] else None
        csell = int(feat[f'{cohort}_sell'][i]) if feat[f'{cohort}_sell_ok'][i] else None
        chigh = int(feat[f'{cohort}_high'][i]) if feat[f'{cohort}_high_ok'][i] else None
        clow = int(feat[f'{cohort}_low'][i]) if feat[f'{cohort}_low_ok'][i] else None
        cclose = int(feat[f'{cohort}_close'][i]) if feat[f'{cohort}_close_ok'][i] else None
        out[f'{cohort}_volume_fraction'] = cohort_volume_fraction(cvol, volume)
        out[f'{cohort}_signed_fraction'] = cohort_signed_fraction(cbuy, csell, volume)
        out[f'{cohort}_true_CVD_path_range'] = true_path_range(chigh, clow, close=cclose)
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
    start, start_ok = _i64_col(table, 'event_start_ns', np)
    end, end_ok = _i64_col(table, 'event_end_ns', np)
    cut, cut_ok = _i64_col(table, 'cut_ns', np)
    known, known_ok = _i64_col(table, 'known_at_ns', np, optional=True)
    minutes, _ = _i64_col(table, 'formation_minutes', np)
    inst, _ = _i64_col(table, 'instrument_id', np)
    acq_s, _ = _i64_col(table, 'acquired_event_start_ns', np)
    acq_e, _ = _i64_col(table, 'acquired_event_end_ns', np)
    stored_known = known_ok & cut_ok & (known == cut + np.int64(SOURCE_LATENCY_NS))
    inside = ref_at_ok & start_ok & cut_ok & (start <= ref_at) & (ref_at < cut) & ref_ok
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
        'event_start_ns': start, 'start_ok': start_ok, 'event_end_ns': end, 'end_ok': end_ok,
        'cut_ns': cut, 'cut_ok': cut_ok, 'known_at_ns': known, 'known_ok': known_ok,
        'stored_known': stored_known, 'formation_minutes': minutes,
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
    latency, lat_ok = _i64_col(table, 'latency_ns', np)
    cut, cut_ok = _i64_col(table, 'cut_ns', np)
    inst, _ = _i64_col(table, 'instrument_id', np)
    minutes, minutes_ok = _i64_col(table, 'horizon_minutes', np, optional=True)
    acq_s, _ = _i64_col(table, 'acquired_event_start_ns', np)
    acq_e, _ = _i64_col(table, 'acquired_event_end_ns', np)
    no_new = _bool_col(table, 'no_new_trade', np, optional=True, default=False)
    no_priced = _bool_col(table, 'no_priced_trade', np, optional=True, default=False)
    start_matches = start_ok & cut_ok & lat_ok & (start == cut + latency)
    matured = known_ok & end_ok & (known >= end)
    return {
        'n': len(table), 'complete': complete, 'censored': left | right | roll,
        'last': last, 'last_ok': last_ok, 'high': high, 'high_ok': high_ok,
        'low': low, 'low_ok': low_ok, 'signed_open': signed_open, 'open_ok': open_ok,
        'signed_close': signed_close, 'close_ok': close_ok, 'buy': buy, 'buy_ok': buy_ok,
        'sell': sell, 'sell_ok': sell_ok, 'known_at_ns': known, 'known_ok': known_ok,
        'event_end_ns': end, 'end_ok': end_ok, 'event_start_ns': start, 'start_ok': start_ok,
        'start_matches': start_matches, 'matured': matured,
        'latency_ns': latency, 'lat_ok': lat_ok, 'cut_ns': cut, 'cut_ok': cut_ok,
        'instrument_id': inst, 'horizon_minutes': minutes, 'horizon_minutes_ok': minutes_ok,
        'acquired_event_start_ns': acq_s, 'acquired_event_end_ns': acq_e,
        'no_new_trade': no_new, 'no_priced_trade': no_priced,
        'root': _str_list(table, 'root'), 'source_path': _str_list(table, 'source_path'),
        'source_metadata_sha256': _str_list(table, 'source_metadata_sha256'),
        'source_variant': _str_list(table, 'source_variant'),
        'contract_key': _str_list(table, 'contract_key', optional=True),
        'horizon_kind': _str_list(table, 'horizon_kind'),
        'label_id': _str_list(table, 'label_id', optional=True),
    }


def _classify_cut_clock(feat, calendar):
    """Economic date/year/session from the cut clock, stable across formations."""
    cache = {}
    dates, years, stages, sessions, states = [], [], [], [], []
    for index in range(feat['n']):
        cut = int(feat['cut_ns'][index])
        root = feat['root'][index]
        cached = cache.get((cut, root))
        if cached is None:
            known = cut + SOURCE_LATENCY_NS
            classified = classify_session(cut, cut + 1, calendar=calendar, known_at_ns=known)
            eco = classified['economic_date']
            cached = {
                'economic_date': eco,
                'year': classified['year'],
                'session': classified['session'],
                'calendar_state': classified['calendar_state'],
                'stage': stage_name(root, eco),
            }
            cache[(cut, root)] = cached
        dates.append(cached['economic_date'])
        years.append(cached['year'])
        stages.append(cached['stage'])
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


def _array_join_eligible(feat, i, lab, j, intervals):
    if not _join_identity(feat, i, lab, j):
        return False
    if not (feat['quality'][i] and not feat['censored'][i] and feat['stored_known'][i]):
        return False
    if not (lab['complete'][j] and not lab['censored'][j] and lab['start_matches'][j] and lab['matured'][j]):
        return False
    latency = int(lab['latency_ns'][j])
    feature_known = _add_checked(int(feat['cut_ns'][i]), latency, what='feature_known_at_ns')
    feature_stage = _named_interval_stage(
        feat['root'][i], int(feat['event_start_ns'][i]), feature_known, intervals)
    label_stage = _stage_of_ns(
        lab['root'][j],
        int(lab['known_at_ns'][j]) if lab['known_ok'][j] else None,
        intervals,
    )
    return feature_stage != 'unassigned' and feature_stage == label_stage


def _signed_flow(lab, j):
    if lab['open_ok'][j] and lab['close_ok'][j]:
        return int(lab['signed_close'][j]) - int(lab['signed_open'][j])
    if lab['buy_ok'][j] and lab['sell_ok'][j]:
        return int(lab['buy'][j]) - int(lab['sell'][j])
    return None


def _joined_values(feat, i, lab, j, reference):
    last = int(lab['last'][j]) if lab['last_ok'][j] else None
    high = int(lab['high'][j]) if lab['high_ok'][j] else None
    low = int(lab['low'][j]) if lab['low_ok'][j] else None
    disp = future_displacements(reference, last, high, low)
    past_close = int(feat['all_close'][i]) if feat['all_close_ok'][i] else None
    concord = directional_concordance(past_close, disp['terminal_return_ticks'])
    no_new = complete_binary_flag(bool(lab['no_new_trade'][j]), complete=True)
    no_priced = complete_binary_flag(bool(lab['no_priced_trade'][j]), complete=True)
    values = {
        **disp,
        'future_signedflow': _signed_flow(lab, j),
        'no_new_trade': no_new,
        'no_priced_trade': no_priced,
        'concordance_both_nonzero': (
            None if not concord['both_nonzero'] else (1.0 if concord['concordant'] else 0.0)
        ),
        'zero_past_sign': (
            1.0 if concord['zero_past'] else 0.0
        ) if concord['past_valid'] else None,
        'zero_future_sign': (
            1.0 if concord['zero_future'] else 0.0
        ) if concord['future_valid'] else None,
    }
    return values, concord, past_close


def _add_joined_metrics(store, day, values):
    for name in JOINED_METRICS:
        store[name].add_one(day, values.get(name))


def _receiver_payload(feat, i, lab, j, *, day, stage, session, measurements, values, concord):
    reference = int(feat['ref'][i]) if feat['inside'][i] and feat['ref_ok'][i] else None
    return {
        'day': day, 'stage': stage, 'session': session, 'root': feat['root'][i],
        'source_path': feat['source_path'][i],
        'source_metadata_sha256': feat['source_metadata_sha256'][i],
        'source_variant': feat['source_variant'][i],
        'instrument_id': int(feat['instrument_id'][i]),
        'contract_key': feat['contract_key'][i],
        'cut_ns': int(feat['cut_ns'][i]),
        'formation_minutes': int(feat['formation_minutes'][i]),
        'formation_id': feat['formation_id'][i],
        'event_start_ns': int(feat['event_start_ns'][i]),
        'latency_ns': int(lab['latency_ns'][j]),
        'horizon_kind': lab['horizon_kind'][j],
        'horizon_minutes': int(lab['horizon_minutes'][j]) if lab['horizon_minutes_ok'][j] else None,
        'label_id': lab['label_id'][j],
        'terminal': values.get('terminal_return_ticks'),
        'up': values.get('future_up_excursion_ticks'),
        'down': values.get('future_down_excursion_ticks'),
        'no_new': values.get('no_new_trade'),
        'concordant': values.get('concordance_both_nonzero'),
        'measurements': measurements,
        'ref': (
            int(feat['ref_at'][i]) if feat['ref_at_ok'][i] else None,
            int(feat['ref_ord'][i]) if feat['ref_ord_ok'][i] else None,
            reference,
        ),
        '_': concord,
    }


def _accumulate_latency_pairs(arms_by_key, paired, collection, year):
    for key, arms in arms_by_key.items():
        formation, horizon_kind, horizon_minutes, session, stage, root = key[5], key[6], key[7], key[8], key[9], key[10]
        any_arm = next(iter(arms.values()))
        day = any_arm['day']
        for alt in LATENCY_ALTERNATIVES_NS:
            pkey = _gkey(
                group_kind='paired_latency', source_collection=collection, root=root,
                year=year, stage=stage, session=session, formation_minutes=formation,
                latency_ns=alt, horizon_kind=horizon_kind, horizon_minutes=horizon_minutes,
                contrast=f'{alt}_vs_{LATENCY_REFERENCE_NS}',
            )
            store = _group_bucket(paired, pkey)
            reference = arms.get(LATENCY_REFERENCE_NS)
            other = arms.get(alt)
            if reference is not None:
                store['own_reference_count'].add_one(day, 1.0)
            if other is not None:
                store['own_alternative_count'].add_one(day, 1.0)
            if (
                reference is None or other is None
                or reference['ref'] != other['ref'] or reference['ref'][2] is None
            ):
                continue
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


def _accumulate_formation_pairs(arms_by_key, paired, collection, year):
    for key, arms in arms_by_key.items():
        latency, horizon_kind, horizon_minutes, session, stage, root = key[5], key[6], key[7], key[8], key[9], key[10]
        any_arm = next(iter(arms.values()))
        day = any_arm['day']
        for minutes, row in arms.items():
            pkey = _gkey(
                group_kind='formation_own', source_collection=collection, root=root,
                year=year, stage=stage, session=session, formation_minutes=minutes,
                latency_ns=latency, horizon_kind=horizon_kind, horizon_minutes=horizon_minutes,
            )
            _group_bucket(paired, pkey)['own_support'].add_one(day, 1.0)
        minutes_list = sorted(arms)
        common_ref = None
        if minutes_list:
            refs = {arms[m]['ref'] for m in minutes_list}
            if len(refs) == 1 and next(iter(refs))[2] is not None:
                common_ref = next(iter(refs))
        if len(minutes_list) == 4 and common_ref is not None:
            pkey = _gkey(
                group_kind='formation_common4', source_collection=collection, root=root,
                year=year, stage=stage, session=session, latency_ns=latency,
                horizon_kind=horizon_kind, horizon_minutes=horizon_minutes,
            )
            _group_bucket(paired, pkey)['common_support'].add_one(day, 1.0)
        for left_i, left_m in enumerate(minutes_list):
            for right_m in minutes_list[left_i + 1:]:
                left, right = arms[left_m], arms[right_m]
                pkey = _gkey(
                    group_kind='paired_formation', source_collection=collection, root=root,
                    year=year, stage=stage, session=session, latency_ns=latency,
                    horizon_kind=horizon_kind, horizon_minutes=horizon_minutes,
                    contrast=f'{left_m}_vs_{right_m}',
                )
                store = _group_bucket(paired, pkey)
                if left['ref'] != right['ref'] or left['ref'][2] is None:
                    continue
                store['common_support'].add_one(day, 1.0)
                left_mtr, right_mtr = left['measurements'], right['measurements']
                for name in FORMATION_FEATURE_PAIR_METRICS:
                    a, b = left_mtr.get(name), right_mtr.get(name)
                    if a is None or b is None:
                        continue
                    store[name].add_one(day, float(b) - float(a))
                if left['concordant'] is not None and right['concordant'] is not None:
                    store['concordance_both_nonzero'].add_one(
                        day, float(right['concordant']) - float(left['concordant']))
                for metric, a, b in (
                    ('terminal_return_ticks', left['terminal'], right['terminal']),
                    ('future_up_excursion_ticks', left['up'], right['up']),
                    ('future_down_excursion_ticks', left['down'], right['down']),
                    ('no_new_trade', left['no_new'], right['no_new']),
                ):
                    if a is None or b is None:
                        continue
                    store[metric].add_one(day, float(b) - float(a))


def _event_link_row(event, *, cut=None, payload=None, relative_bucket, in_formation,
                    has_receiver, no_window, label_id=None, latency_ns=None,
                    horizon_kind=None, horizon_minutes=None, instrument_id=None,
                    contract_key=None, source_path=None, source_metadata_sha256=None,
                    formation_id=None, formation_minutes=None, cut_ns=None):
    src_path = source_path
    src_sha = source_metadata_sha256
    if payload is not None:
        src_path = payload['source_path']
        src_sha = payload['source_metadata_sha256']
        instrument_id = payload['instrument_id']
        contract_key = payload['contract_key']
        cut_ns = payload['cut_ns']
        formation_minutes = payload['formation_minutes']
        formation_id = payload['formation_id']
        latency_ns = payload['latency_ns']
        horizon_kind = payload['horizon_kind']
        horizon_minutes = payload['horizon_minutes']
        label_id = payload['label_id']
    elif cut is not None:
        src_path = cut.get('source_path') if src_path is None else src_path
        src_sha = cut.get('source_metadata_sha256') if src_sha is None else src_sha
        instrument_id = cut.get('instrument_id') if instrument_id is None else instrument_id
        contract_key = cut.get('contract_key') if contract_key is None else contract_key
        cut_ns = cut.get('cut_ns') if cut_ns is None else cut_ns
        formation_minutes = cut.get('formation_minutes') if formation_minutes is None else formation_minutes
        formation_id = cut.get('formation_id') if formation_id is None else formation_id
    ts = event.get('event_ts_utc_ns')
    return {
        'semantic_id': event.get('semantic_id'),
        'event_type': None if event.get('event_type') is None else str(event.get('event_type')),
        'event_date': event.get('event_date'),
        'event_ts_utc_ns': None if ts is None else int(ts),
        'time_basis': event.get('time_basis'),
        'time_precision': event.get('time_precision'),
        'status': event.get('status'),
        'source_path': src_path,
        'source_metadata_sha256': src_sha,
        'instrument_id': None if instrument_id is None else int(instrument_id),
        'contract_key': contract_key,
        'formation_id': formation_id,
        'label_id': label_id,
        'cut_ns': None if cut_ns is None else int(cut_ns),
        'formation_minutes': None if formation_minutes is None else int(formation_minutes),
        'latency_ns': None if latency_ns is None else int(latency_ns),
        'horizon_kind': horizon_kind,
        'horizon_minutes': None if horizon_minutes is None else int(horizon_minutes),
        'relative_bucket': relative_bucket,
        'in_formation': bool(in_formation),
        'has_eligible_receiver': bool(has_receiver),
        'no_window': bool(no_window),
        'known_at_ns': None,
        'causal_feature_eligible': False,
        'provenance_json': _provenance_json(event.get('provenance')),
    }


class _LinkWriter:
    def __init__(self, outputs, name, pa):
        self.series = ParquetSeries(outputs, name, encoding='plain')
        self.batch = []
        self.pa = pa
        self.rows = 0

    def add(self, row):
        self.batch.append(row)
        if len(self.batch) >= LINK_BATCH:
            self.flush()

    def flush(self):
        if not self.batch:
            return
        self.series.append(_event_table(self.batch, self.pa))
        self.rows += len(self.batch)
        self.batch.clear()

    def finish(self):
        if self.rows == 0 and not self.batch:
            self.series.append(_event_table([], self.pa))
        else:
            self.flush()
        return self.series.finish()


def _build_event_index(events):
    timed = []
    by_date = defaultdict(list)
    inconsistent = 0
    date_only = 0
    for event in events:
        day = event.get('event_date')
        if type(day) is str and day:
            by_date[day].append(event)
        timed_ok = timed_event_eligible(event)
        clock_ok = event_clock_consistent(event)
        if timed_ok and not clock_ok:
            inconsistent += 1
            date_only += 1
            continue
        if not timed_ok:
            date_only += 1
            continue
        timed.append((_py_int(event['event_ts_utc_ns'], what='event_ts_utc_ns'), event))
    timed.sort(key=lambda item: item[0])
    return {
        'all': events,
        'timed_ts': [item[0] for item in timed],
        'timed_ev': [item[1] for item in timed],
        'by_date': by_date,
        'inconsistent': inconsistent,
        'date_only': date_only,
    }


def _events_for_partition(events, *, year, intended_dates):
    intended = set(intended_dates)
    selected = []
    seen = set()
    for event in events:
        sid = event.get('semantic_id')
        day = event.get('event_date')
        take = False
        if type(day) is str and len(day) >= 4 and day[:4].isdigit() and int(day[:4]) == year:
            take = True
        elif type(day) is str and day in intended:
            take = True
        elif timed_event_eligible(event) and event_clock_consistent(event):
            eco = economic_date(_py_int(event['event_ts_utc_ns'], what='event_ts_utc_ns'))
            take = int(eco[:4]) == year or eco in intended
        if take and sid not in seen:
            seen.add(sid)
            selected.append(event)
    return selected


def _nearby_timed_events(index, cut_ns):
    stamps = index['timed_ts']
    if not stamps:
        return ()
    lo = bisect.bisect_left(stamps, cut_ns - EVENT_LOOKBACK_NS)
    hi = bisect.bisect_right(stamps, cut_ns + EVENT_LOOKAHEAD_NS)
    return tuple(zip(stamps[lo:hi], index['timed_ev'][lo:hi]))


def _emit_event_metrics(groups, paired_event, event, payload, *, collection, year, relative_bucket):
    day = payload['day']
    gkey = _gkey(
        group_kind='event', source_collection=collection, root=payload['root'],
        year=year, stage=payload['stage'], session=payload['session'],
        formation_minutes=payload['formation_minutes'], latency_ns=payload['latency_ns'],
        horizon_kind=payload['horizon_kind'], horizon_minutes=payload['horizon_minutes'],
        event_type=None if event.get('event_type') is None else str(event.get('event_type')),
        time_precision=event.get('time_precision'), status=event.get('status'),
        relative_bucket=relative_bucket,
    )
    store = _group_bucket(groups, gkey)
    store['terminal_return_ticks'].add_one(day, payload.get('terminal'))
    store['future_up_excursion_ticks'].add_one(day, payload.get('up'))
    store['future_down_excursion_ticks'].add_one(day, payload.get('down'))
    store['no_new_trade'].add_one(day, payload.get('no_new'))
    pair_key = (
        event.get('semantic_id'), payload['source_path'], payload['source_metadata_sha256'],
        payload['instrument_id'], payload['contract_key'], payload['cut_ns'],
        payload['formation_minutes'], payload['horizon_kind'], payload['horizon_minutes'],
    )
    bucket = paired_event[pair_key]
    bucket[payload['latency_ns']] = payload
    bucket['_event'] = event
    bucket['_meta'] = (collection, year, relative_bucket, payload['root'], payload['stage'], payload['session'])


def _flush_event_latency_pairs(paired_event, groups):
    for key, arms in paired_event.items():
        event = arms.pop('_event', None)
        meta = arms.pop('_meta', None)
        if event is None or meta is None:
            continue
        collection, year, relative_bucket, root, stage, session = meta
        formation, horizon_kind, horizon_minutes = key[6], key[7], key[8]
        reference = arms.get(LATENCY_REFERENCE_NS)
        for alt in LATENCY_ALTERNATIVES_NS:
            other = arms.get(alt)
            pkey = _gkey(
                group_kind='event_paired_latency', source_collection=collection, root=root,
                year=year, stage=stage, session=session, formation_minutes=formation,
                latency_ns=alt, horizon_kind=horizon_kind, horizon_minutes=horizon_minutes,
                event_type=None if event.get('event_type') is None else str(event.get('event_type')),
                time_precision=event.get('time_precision'), status=event.get('status'),
                relative_bucket=relative_bucket,
                contrast=f'{alt}_vs_{LATENCY_REFERENCE_NS}',
            )
            store = _group_bucket(groups, pkey)
            day = (reference or other or {}).get('day')
            if reference is not None and day:
                store['own_reference_count'].add_one(day, 1.0)
            if other is not None and day:
                store['own_alternative_count'].add_one(day, 1.0)
            if (
                reference is None or other is None or day is None
                or reference['ref'] != other['ref'] or reference['ref'][2] is None
            ):
                continue
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


def _link_unit_events(*, feat, keep, meta, receivers, event_index, expected_sids,
                      writer, groups, collection, year, window_sids, receiver_sids):
    paired_event = defaultdict(dict)
    cuts = {}
    for i in keep:
        cut_ns = int(feat['cut_ns'][i])
        cell = cuts.get(cut_ns)
        if cell is None:
            cell = {
                'cut_ns': cut_ns, 'date': meta['dates'][i], 'stage': meta['stages'][i],
                'session': meta['sessions'][i], 'features': [],
            }
            cuts[cut_ns] = cell
        cell['features'].append(i)
    linked_expected = set()
    for cut_ns, cell in cuts.items():
        nearby = _nearby_timed_events(event_index, cut_ns)
        date_events = []
        for event in event_index['by_date'].get(cell['date'], ()):
            if timed_event_eligible(event) and event_clock_consistent(event):
                continue
            date_events.append(event)
        for i in cell['features']:
            start_ns = int(feat['event_start_ns'][i])
            identity = (
                feat['source_path'][i], feat['source_metadata_sha256'][i],
                int(feat['instrument_id'][i]), feat['contract_key'][i],
                cut_ns, int(feat['formation_minutes'][i]),
            )
            labels = receivers.get(identity, ())
            cut_row = {
                'source_path': feat['source_path'][i],
                'source_metadata_sha256': feat['source_metadata_sha256'][i],
                'instrument_id': int(feat['instrument_id'][i]),
                'contract_key': feat['contract_key'][i],
                'cut_ns': cut_ns,
                'formation_minutes': int(feat['formation_minutes'][i]),
                'formation_id': feat['formation_id'][i],
            }
            for at, event in nearby:
                sid = event.get('semantic_id')
                if sid in expected_sids:
                    linked_expected.add(sid)
                    window_sids.add(sid)
                bucket = event_relative_bucket(at, cut_ns)
                inside = event_in_formation(at, start_ns, cut_ns)
                if bucket is None and not inside:
                    continue
                if labels:
                    for payload, eligible in labels:
                        writer.add(_event_link_row(
                            event, payload=payload, relative_bucket=bucket,
                            in_formation=inside, has_receiver=eligible, no_window=False,
                        ))
                        if eligible:
                            receiver_sids.add(sid)
                            _emit_event_metrics(
                                groups, paired_event, event, payload,
                                collection=collection, year=year, relative_bucket=bucket,
                            )
                else:
                    writer.add(_event_link_row(
                        event, cut=cut_row, relative_bucket=bucket, in_formation=inside,
                        has_receiver=False, no_window=False,
                    ))
            for event in date_events:
                sid = event.get('semantic_id')
                if sid in expected_sids:
                    linked_expected.add(sid)
                    window_sids.add(sid)
                if labels:
                    for payload, eligible in labels:
                        writer.add(_event_link_row(
                            event, payload=payload, relative_bucket='date_only',
                            in_formation=False, has_receiver=False, no_window=False,
                        ))
                        _ = eligible
                else:
                    writer.add(_event_link_row(
                        event, cut=cut_row, relative_bucket='date_only',
                        in_formation=False, has_receiver=False, no_window=False,
                    ))
    _flush_event_latency_pairs(paired_event, groups)
    return linked_expected


def _process_unit_tables(features, labels, *, collection, year, calendar, intervals,
                         primary_start, primary_end, groups, paired, completeness,
                         seen_keys, event_index, expected_sids, writer, window_sids,
                         receiver_sids, np):
    feat = _extract_features(features, np)
    lab = _extract_labels(labels, np)
    meta = _classify_cut_clock(feat, calendar)
    keep = []
    for i in range(feat['n']):
        if meta['years'][i] != year:
            completeness['out_of_primary_year_rows'] += 1
            continue
        keep.append(i)
    completeness['feature_rows'] += len(keep)
    selected_label = 0
    for j in range(lab['n']):
        if lab['cut_ok'][j] and int(economic_date(int(lab['cut_ns'][j]))[:4]) == year:
            selected_label += 1
            if lab['censored'][j]:
                completeness['censored_label_rows'] += 1
    completeness['label_rows'] += selected_label
    if not keep:
        return
    feat_by_key = defaultdict(list)
    measurements = {}
    for i in keep:
        key = (
            feat['source_path'][i], feat['source_metadata_sha256'][i],
            int(feat['instrument_id'][i]), feat['contract_key'][i], int(feat['cut_ns'][i]),
        )
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
        eco = meta['dates'][i]
        if not (primary_start <= eco <= primary_end):
            completeness['out_of_primary_year_rows'] += 1
        completeness['economic_dates'].add(eco)
        completeness['calendar_state_counts'][meta['calendar_states'][i]] += 1
        span_stage = _named_interval_stage(feat['root'][i], int(feat['event_start_ns'][i]), int(feat['known_at_ns'][i]), intervals)
        same_stage = span_stage == meta['stages'][i]
        admitted = bool(feat['quality'][i] and not feat['censored'][i] and feat['stored_known'][i] and same_stage and primary_start <= eco <= primary_end)
        values = _feature_measurement_values(feat, i)
        measurements[i] = values
        if admitted:
            completeness['eligible_feature_rows'] += 1
            gkey = _gkey(
                group_kind='feature', source_collection=collection, root=feat['root'][i],
                year=year, stage=meta['stages'][i], session=meta['sessions'][i],
                formation_minutes=int(feat['formation_minutes'][i]),
            )
            store = _group_bucket(groups, gkey)
            for name, value in values.items():
                store[name].add_one(eco, value)
        if not feat['inside'][i]:
            completeness['missing_reference_rows'] += 1
    lab_by_key = defaultdict(list)
    for j in range(lab['n']):
        lab_by_key[(
            lab['source_path'][j], lab['source_metadata_sha256'][j],
            int(lab['instrument_id'][j]), lab['contract_key'][j], int(lab['cut_ns'][j]),
        )].append(j)
    latency_arms = defaultdict(dict)
    formation_arms = defaultdict(dict)
    receivers = defaultdict(list)
    for key, fis in feat_by_key.items():
        ljs = lab_by_key.get(key, ())
        for i in fis:
            day = meta['dates'][i]
            stage = meta['stages'][i]
            session = meta['sessions'][i]
            formation = int(feat['formation_minutes'][i])
            reference = int(feat['ref'][i]) if feat['inside'][i] and feat['ref_ok'][i] else None
            for j in ljs:
                eligible = _array_join_eligible(feat, i, lab, j, intervals)
                values, concord, _past = _joined_values(feat, i, lab, j, reference)
                payload = _receiver_payload(
                    feat, i, lab, j, day=day, stage=stage, session=session,
                    measurements=measurements[i], values=values, concord=concord,
                )
                identity = (
                    feat['source_path'][i], feat['source_metadata_sha256'][i],
                    int(feat['instrument_id'][i]), feat['contract_key'][i],
                    int(feat['cut_ns'][i]), formation,
                )
                receivers[identity].append((payload, eligible))
                if not eligible:
                    continue
                completeness['eligible_joined_rows'] += 1
                horizon_kind = lab['horizon_kind'][j]
                horizon_minutes = int(lab['horizon_minutes'][j]) if lab['horizon_minutes_ok'][j] else None
                latency = int(lab['latency_ns'][j])
                gkey = _gkey(
                    group_kind='joined', source_collection=collection, root=feat['root'][i],
                    year=year, stage=stage, session=session, formation_minutes=formation,
                    latency_ns=latency, horizon_kind=horizon_kind, horizon_minutes=horizon_minutes,
                )
                _add_joined_metrics(_group_bucket(groups, gkey), day, values)
                lat_key = (
                    feat['source_path'][i], feat['source_metadata_sha256'][i],
                    int(feat['instrument_id'][i]), feat['contract_key'][i],
                    int(feat['cut_ns'][i]), formation, horizon_kind, horizon_minutes,
                    session, stage, feat['root'][i],
                )
                latency_arms[lat_key][latency] = payload
                form_key = (
                    feat['source_path'][i], feat['source_metadata_sha256'][i],
                    int(feat['instrument_id'][i]), feat['contract_key'][i],
                    int(feat['cut_ns'][i]), latency, horizon_kind, horizon_minutes,
                    session, stage, feat['root'][i],
                )
                formation_arms[form_key][formation] = payload
    _accumulate_latency_pairs(latency_arms, paired, collection, year)
    _accumulate_formation_pairs(formation_arms, paired, collection, year)
    _link_unit_events(
        feat=feat, keep=keep, meta=meta, receivers=receivers, event_index=event_index,
        expected_sids=expected_sids, writer=writer, groups=groups, collection=collection,
        year=year, window_sids=window_sids, receiver_sids=receiver_sids,
    )


def _event_table(links, pa):
    names = (
        'semantic_id', 'event_type', 'event_date', 'event_ts_utc_ns', 'time_basis',
        'time_precision', 'status', 'source_path', 'source_metadata_sha256',
        'instrument_id', 'contract_key', 'formation_id', 'label_id', 'cut_ns',
        'formation_minutes', 'latency_ns', 'horizon_kind', 'horizon_minutes',
        'relative_bucket', 'in_formation', 'has_eligible_receiver', 'no_window',
        'known_at_ns', 'causal_feature_eligible', 'provenance_json',
    )
    integers = {
        'event_ts_utc_ns', 'instrument_id', 'cut_ns', 'formation_minutes', 'latency_ns',
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
        ('horizon_minutes', pa.int64()), ('event_type', pa.string()),
        ('time_precision', pa.string()), ('status', pa.string()),
        ('relative_bucket', pa.string()), ('contrast', pa.string()),
        ('metric', pa.string()), ('economic_date', pa.string()),
        ('observation_count', pa.int64()), ('sum', pa.float64()), ('mean', pa.float64()),
    ])


def _date_rows_from_groups(groups):
    rows = []
    for key, stores in groups.items():
        meta = _gmeta(key)
        formation = meta['formation_minutes']
        latency = meta['latency_ns']
        horizon_minutes = meta['horizon_minutes']
        for metric, store in stores.items():
            for day, count in store.date_count.items():
                total = store.date_sum[day]
                rows.append({
                    'group_kind': meta['group_kind'],
                    'source_collection': meta['source_collection'],
                    'root': meta['root'], 'year': int(meta['year']),
                    'stage': meta['stage'],
                    'session': None if meta['session'] is None else str(meta['session']),
                    'formation_minutes': None if formation is None else int(formation),
                    'latency_ns': None if latency is None else int(latency),
                    'horizon_kind': meta['horizon_kind'],
                    'horizon_minutes': None if horizon_minutes is None else int(horizon_minutes),
                    'event_type': meta['event_type'],
                    'time_precision': meta['time_precision'],
                    'status': meta['status'],
                    'relative_bucket': meta['relative_bucket'],
                    'contrast': meta['contrast'],
                    'metric': metric, 'economic_date': day,
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
        'sample_quantile_distribution': 'equal_weight_date_mean',
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


def _group_record(key, intended, metrics_out):
    meta = _gmeta(key)
    return {
        **meta,
        'metrics': metrics_out,
        'intended_dates': list(intended),
        'intended_date_count': len(intended),
        'family_complete': False,
    }


def _empty_group(key, intended, stores, *, min_dates, min_events):
    names = tuple(stores) or ('undefined',)
    metrics = {}
    for name in names:
        payload = _undefined_metric(unit=_metric_unit(name))
        payload['missing_date_count'] = len(intended)
        payload['support']['minimum_independent_dates'] = min_dates
        payload['support']['minimum_events'] = min_events
        metrics[name] = payload
    return _group_record(key, intended, metrics)


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
        meta = _gmeta(key)
        by_universe[(meta['root'], meta['year'], meta['stage'])].append(key)
    for (root, year, stage), keys in by_universe.items():
        intended = list(intended_by_stage.get((root, year, stage), ()))
        if not intended:
            for key in keys:
                finalized.append(_empty_group(
                    key, intended, groups[key], min_dates=min_dates, min_events=min_events))
            continue
        weights, starts = _moving_weights(
            np, len(intended), seed=seed, block_length=block, replicates=replicates)
        state = (np, weights, starts)
        for key in sorted(keys, key=lambda item: tuple(str(part) for part in item)):
            stores = groups[key]
            names = tuple(stores)
            if not names:
                finalized.append(_empty_group(
                    key, intended, stores, min_dates=min_dates, min_events=min_events))
                continue
            cells = {}
            for name in names:
                store = stores[name]
                cells[name] = {
                    day: store.date_sum[day] / store.date_count[day]
                    for day in store.date_count if store.date_count[day]
                }
            if not any(cells[name] for name in names):
                finalized.append(_empty_group(
                    key, intended, stores, min_dates=min_dates, min_events=min_events))
                continue
            result = observed_date_statistics(
                cells, intended, estimator='date_mean', seed=seed,
                block_length=block, replicates=replicates, confidence=confidence,
                minimum_independent_dates=min_dates, minimum_events=1,
                _retain_replicate_estimates=False, _bootstrap_state=state,
            )
            metrics_out = {}
            for name in names:
                payload = _metric_payload(
                    stores[name], intended, result['metrics'][name],
                    min_dates=min_dates, min_events=min_events, unit=_metric_unit(name),
                )
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


def _md(value):
    if value is None:
        text = 'undefined'
    elif isinstance(value, bool):
        text = 'true' if value else 'false'
    else:
        text = str(value)
    return text.replace('|', '\\|').replace('\n', ' ')


def _metric_estimate(metric):
    mean = metric.get('date_mean')
    if isinstance(mean, dict):
        return mean.get('estimate')
    return mean if mean is not None else metric.get('estimate')


def _ci_text(metric):
    boot = metric.get('bootstrap') or {}
    if isinstance(metric.get('date_mean'), dict):
        boot = metric['date_mean'].get('bootstrap') or boot
    if not boot:
        return 'undefined'
    lower, upper = boot.get('lower'), boot.get('upper')
    if lower is None and upper is None:
        return 'undefined'
    return f'[{lower}, {upper}]'


def _group_identity_row(group):
    support = {}
    undefined = True
    for metric in (group.get('metrics') or {}).values():
        cell = metric.get('support') or {}
        if cell.get('events', 0) or metric.get('undefined') is False:
            undefined = False
        support = cell or support
    return (
        f"| {_md(group.get('group_kind'))} | {_md(group.get('source_collection'))} | "
        f"{_md(group.get('root'))} | {_md(group.get('year'))} | {_md(group.get('stage'))} | "
        f"{_md(group.get('session'))} | {_md(group.get('formation_minutes'))} | "
        f"{_md(group.get('latency_ns'))} | {_md(group.get('horizon_kind'))}:"
        f"{_md(group.get('horizon_minutes'))} | {_md(group.get('event_type'))} | "
        f"{_md(group.get('relative_bucket'))} | {_md(group.get('contrast'))} | "
        f"{_md(support.get('independent_dates'))} | {_md(support.get('events'))} | "
        f"{_md('true' if undefined else 'false')} |"
    )


def _preset_rows(groups, kinds, names):
    lines = []
    for group in groups:
        if group.get('group_kind') not in kinds:
            continue
        metrics = group.get('metrics') or {}
        for name in names:
            if name not in metrics:
                continue
            metric = metrics[name]
            support = metric.get('support') or {}
            lines.append(
                f"| {_md(group.get('group_kind'))} | {_md(group.get('root'))} | "
                f"{_md(group.get('year'))} | {_md(group.get('stage'))} | "
                f"{_md(group.get('session'))} | {_md(group.get('formation_minutes'))} | "
                f"{_md(group.get('latency_ns'))} | {_md(group.get('horizon_minutes'))} | "
                f"{_md(group.get('event_type'))} | {_md(group.get('relative_bucket'))} | "
                f"{_md(group.get('contrast'))} | {_md(name)} | {_md(metric.get('unit'))} | "
                f"{_md(_metric_estimate(metric))} | {_md(metric.get('event_mean'))} | "
                f"{_md(support.get('independent_dates'))} | {_md(support.get('events'))} | "
                f"{_md(metric.get('missing_date_count'))} | {_md(_ci_text(metric))} |"
            )
    if not lines:
        lines.append('| undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined |')
    return lines


def _bounded_summaries(groups):
    rows = []
    for group in groups:
        metrics = {}
        for name, metric in (group.get('metrics') or {}).items():
            metrics[name] = {
                'unit': metric.get('unit'),
                'estimate': _metric_estimate(metric),
                'event_mean': metric.get('event_mean'),
                'support': metric.get('support'),
                'missing_date_count': metric.get('missing_date_count'),
                'bootstrap': None if not metric.get('bootstrap') else {
                    'lower': (metric.get('bootstrap') or {}).get('lower'),
                    'upper': (metric.get('bootstrap') or {}).get('upper'),
                },
                'undefined': metric.get('undefined', _metric_estimate(metric) is None),
            }
        rows.append({
            'group_kind': group.get('group_kind'),
            'source_collection': group.get('source_collection'),
            'root': group.get('root'), 'year': group.get('year'),
            'stage': group.get('stage'), 'session': group.get('session'),
            'formation_minutes': group.get('formation_minutes'),
            'latency_ns': group.get('latency_ns'),
            'horizon_kind': group.get('horizon_kind'),
            'horizon_minutes': group.get('horizon_minutes'),
            'event_type': group.get('event_type'),
            'time_precision': group.get('time_precision'),
            'status': group.get('status'),
            'relative_bucket': group.get('relative_bucket'),
            'contrast': group.get('contrast'),
            'intended_date_count': group.get('intended_date_count'),
            'metrics': metrics,
        })
    return rows


def _markdown_report(*, summaries, completeness, population, processed, cpu, output_bytes,
                     reused, recomputed, selected, all_keys, event_stats, refs, coverage):
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
        f'- out_of_primary_year_rows: {completeness.get("out_of_primary_year_rows", 0)}',
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
        'weekly acquisitions keep separate primary inference. Sample quantiles below are the '
        'equal-weight date-mean distribution; event mean/min/max stay separate.',
        '',
        'Price units are raw ticks (0.25 index point). Variance is ticks squared. Cohort '
        'fractions are dimensionless. Volume intensity is contracts/second. CVD, OFI and '
        'signed flow are contracts. Labels store absolute future prices; displacements are '
        'derived from each feature reference. A complete quiet window is no-new-trade = 1 '
        'with a null price, not a zero return. Missing coverage stays missing.',
        '',
        'True CVD/OFI path range uses high-low, never close extrema. Hard cohort volumes overlap '
        'and are not a partition. Standing and pressure metrics use their own eligible masks.',
        '',
        'Directional concordance is the paired observed frequency that sign(formation all-CVD close) '
        'matches sign(terminal return), only when both signs are nonzero. Zero-past and zero-future '
        'are separate denominators from their own validities. This is not model accuracy or predictive gain.',
        '',
        'Scheduled event labels are retrospective: known_at is NULL and causal_feature_eligible is '
        'false. Dates without an event record are unknown coverage. Events with no eligible '
        'receiver or no nearby window remain in the event denominator. Global no-receiver counts '
        'an event once if no selected relevant partition had a receiver.',
        '',
        '## Source, year and stage coverage',
        '',
        '| collection | root | year | stage | intended_dates | groups |',
        '|---|---|---|---|---|---|',
    ]
    if coverage:
        for row in coverage:
            lines.append(
                f"| {_md(row.get('collection'))} | {_md(row.get('root'))} | "
                f"{_md(row.get('year'))} | {_md(row.get('stage'))} | "
                f"{_md(row.get('intended_dates'))} | {_md(row.get('groups'))} |"
            )
    else:
        lines.append('| undefined | undefined | undefined | undefined | undefined | undefined |')
    lines.extend([
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
        f'- inconsistent_event_clock_rows: {completeness.get("inconsistent_event_clock_rows", 0)}',
        '',
        '## Representative feature measurements',
        '',
        '| kind | root | year | stage | session | formation | latency | horizon | event_type | bucket | contrast | metric | unit | date-mean | event-mean | dates | events | missing | 95% CI |',
        '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|',
    ])
    lines.extend(_preset_rows(summaries, ('feature',), (
        'formationvolume_per_second', 'unknown_volume_fraction', 'formation_price_range_ticks',
        'VWAP_variance_ticks_squared', 'OFI_path_range_on_pressureeligible',
        'ny_ge100_volume_fraction', 'ny_ge100_true_CVD_path_range',
    )))
    lines.extend([
        '',
        '## Representative delay contrasts',
        '',
        '| kind | root | year | stage | session | formation | latency | horizon | event_type | bucket | contrast | metric | unit | date-mean | event-mean | dates | events | missing | 95% CI |',
        '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|',
    ])
    lines.extend(_preset_rows(summaries, ('joined', 'paired_latency'), (
        'terminal_return_ticks', 'future_up_excursion_ticks', 'future_down_excursion_ticks',
        'no_new_trade', 'own_reference_count', 'own_alternative_count', 'common_support',
        'concordance_both_nonzero', 'zero_past_sign', 'zero_future_sign',
    )))
    lines.extend([
        '',
        '## Representative formation contrasts',
        '',
        '| kind | root | year | stage | session | formation | latency | horizon | event_type | bucket | contrast | metric | unit | date-mean | event-mean | dates | events | missing | 95% CI |',
        '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|',
    ])
    lines.extend(_preset_rows(summaries, ('paired_formation', 'formation_own', 'formation_common4'), (
        'formationvolume_per_second', 'ny_ge100_volume_fraction', 'ny_ge100_true_CVD_path_range',
        'OFI_path_range_on_pressureeligible', 'VWAP_variance_ticks_squared',
        'terminal_return_ticks', 'common_support', 'own_support', 'concordance_both_nonzero',
    )))
    lines.extend([
        '',
        '## Representative event outcomes',
        '',
        '| kind | root | year | stage | session | formation | latency | horizon | event_type | bucket | contrast | metric | unit | date-mean | event-mean | dates | events | missing | 95% CI |',
        '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|',
    ])
    lines.extend(_preset_rows(summaries, ('event', 'event_paired_latency'), (
        'terminal_return_ticks', 'future_up_excursion_ticks', 'future_down_excursion_ticks',
        'no_new_trade', 'own_reference_count', 'own_alternative_count', 'common_support',
    )))
    lines.extend([
        '',
        '## All retained groups',
        '',
        '| kind | collection | root | year | stage | session | formation | latency | horizon | event_type | bucket | contrast | dates | events | undefined |',
        '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|',
    ])
    if summaries:
        lines.extend(_group_identity_row(group) for group in summaries)
    else:
        lines.append('| undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | true |')
    lines.extend([
        '',
        '## Full result references',
        '',
    ])
    for name, value in refs.items():
        lines.append(f'- {name}: {_md(value)}')
    lines.extend([
        '',
        'Latency contrasts compare 0 ns and 1 s against 250 ms on the same physical '
        'source/cut/instrument/raw contract, formation, horizon and actual reference. Own '
        'supports are recorded before the intersection. Formation contrasts compare feature '
        'metrics on the common cut and reference; a zero future-target difference is a control, '
        'not evidence that formations are equivalent. A repeated forward target is not counted '
        'as independent evidence. Formation contrasts named left_vs_right report right minus left.',
        '',
    ])
    return '\n'.join(lines) + '\n'


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
    for table in read_series_tables(series):
        del table


def _authenticate_reused_partition(part, load_reference):
    if not isinstance(part, dict) or part.get('kind') != 'auction_flow_window_partition_v1':
        raise IntegrityError('accepted partition is not a window partition')
    if part.get('passed') is not True:
        raise IntegrityError('accepted partition is not a passed window partition')
    _authenticate_json_ref(
        part.get('groups'), load_reference,
        kinds={'auction_flow_window_group_statistics_v1'},
    )
    _authenticate_json_ref(
        part.get('paired'), load_reference,
        kinds={'auction_flow_window_paired_contrasts_v1'},
    )
    _authenticate_series_ref(part.get('denominators'))
    receivers, windows = set(), set()
    for table in read_series_tables(part.get('event_links')):
        ids = table.column('semantic_id').to_pylist()
        has_receiver = table.column('has_eligible_receiver').to_pylist()
        no_window = table.column('no_window').to_pylist()
        for sid, receiver, absent in zip(ids, has_receiver, no_window):
            if receiver: receivers.add(sid)
            if not absent: windows.add(sid)
    return receivers, windows


def _global_event_table(events, receiver_sids, window_sids, pa):
    rows = []
    for event in events:
        sid = event.get('semantic_id')
        timed = timed_event_eligible(event)
        clock = event_clock_consistent(event)
        rows.append({
            'semantic_id': sid,
            'event_type': None if event.get('event_type') is None else str(event.get('event_type')),
            'event_date': event.get('event_date'),
            'event_ts_utc_ns': None if event.get('event_ts_utc_ns') is None else int(event['event_ts_utc_ns']),
            'time_basis': event.get('time_basis'),
            'time_precision': event.get('time_precision'),
            'status': event.get('status'),
            'primary_population': bool(event.get('primary_population')),
            'independent_support': bool(event.get('independent_support')),
            'date_only': (not timed) or (not clock),
            'clock_consistent': clock,
            'has_eligible_receiver_any_selected': sid in receiver_sids,
            'has_window_any_selected': sid in window_sids,
            'outside_acquired_or_no_window': sid not in window_sids,
            'known_at_ns': None,
            'causal_feature_eligible': False,
            'provenance_json': _provenance_json(event.get('provenance')),
        })
    names = (
        'semantic_id', 'event_type', 'event_date', 'event_ts_utc_ns', 'time_basis',
        'time_precision', 'status', 'primary_population', 'independent_support',
        'date_only', 'clock_consistent', 'has_eligible_receiver_any_selected',
        'has_window_any_selected', 'outside_acquired_or_no_window',
        'known_at_ns', 'causal_feature_eligible', 'provenance_json',
    )
    integers = {'event_ts_utc_ns', 'known_at_ns'}
    booleans = {
        'primary_population', 'independent_support', 'date_only', 'clock_consistent',
        'has_eligible_receiver_any_selected', 'has_window_any_selected',
        'outside_acquired_or_no_window', 'causal_feature_eligible',
    }
    columns = {}
    for name in names:
        values = [row[name] for row in rows]
        if name in integers:
            columns[name] = pa.array(values, type=pa.int64())
        elif name in booleans:
            columns[name] = pa.array(values, type=pa.bool_())
        else:
            columns[name] = pa.array(values, type=pa.string())
    return pa.table(columns)


def _compute_window_partition(*, key, members, identity, source_refs, contract, stats, policy,
                              calendar, events, outputs, ordinal, np, pa, global_window_sids,
                              global_receiver_sids):
    collection, root, year = key
    began, wall_began, before = time_mod.process_time(), time_mod.monotonic(), outputs.written
    groups = {}
    paired = {}
    completeness = _empty_completeness()
    completeness['source_windows'] = len({_unit_identity_key(unit) for unit in members})
    seen_keys = set()
    intervals = _civil_stage_intervals(policy)
    primary = contract.get('primary_population') or {}
    primary_start = primary.get('start', '2020-01-01')
    primary_end = primary.get('end', '2026-09-04')
    intended_by_stage = {}
    intended_dates = []
    for stage in (*STAGE_ORDER, 'unassigned'):
        days = intended_date_universe(
            year, stage, root, policy, primary_start, primary_end)
        intended_by_stage[(root, year, stage)] = days
        intended_dates.extend(days)
    year_events = _events_for_partition(events, year=year, intended_dates=intended_dates)
    expected_sids = {event.get('semantic_id') for event in year_events}
    event_index = _build_event_index(year_events)
    completeness['date_only_events'] = event_index['date_only']
    completeness['inconsistent_event_clock_rows'] = event_index['inconsistent']
    prefix = f'window-{ordinal:03d}-{collection}-{root}-{year}'
    writer = _LinkWriter(outputs, prefix + '-event-links', pa)
    window_sids = set()
    receiver_sids = set()
    seen_units = set()
    for unit in members:
        ukey = _unit_identity_key(unit)
        if ukey not in seen_units:
            seen_units.add(ukey)
            completeness['processed_source_windows'] += 1
        start, end = _unit_window_ns(unit)
        completeness['economic_dates'].add(economic_date(int(start)))
        completeness['economic_dates'].add(economic_date(int(end - 1)))
        if _unit_unavailable(unit):
            if ukey in seen_units:
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
        _process_unit_tables(
            features, labels, collection=collection, year=year, calendar=calendar,
            intervals=intervals, primary_start=primary_start, primary_end=primary_end,
            groups=groups, paired=paired, completeness=completeness, seen_keys=seen_keys,
            event_index=event_index, expected_sids=expected_sids, writer=writer,
            window_sids=window_sids, receiver_sids=receiver_sids, np=np,
        )
        del features, labels
    for event in year_events:
        sid = event.get('semantic_id')
        if sid in window_sids:
            continue
        writer.add(_event_link_row(
            event, relative_bucket=(
                'date_only' if (not timed_event_eligible(event) or not event_clock_consistent(event)) else None
            ),
            in_formation=False, has_receiver=False, no_window=True,
        ))
    event_links = writer.finish()
    global_window_sids.update(window_sids)
    global_receiver_sids.update(receiver_sids)
    completeness['unique_semantic_events'] = len(expected_sids)
    completeness['events_with_receiver'] = len(receiver_sids)
    completeness['events_without_receiver'] = len(expected_sids - receiver_sids)
    completeness['events_without_window'] = len(expected_sids - window_sids)
    recorded_dates = {event.get('event_date') for event in year_events if event.get('event_date')}
    completeness['unknown_event_coverage_dates'] = sum(
        1 for day in intended_dates if event_coverage_state(day in recorded_dates) == 'unknown'
    )
    finalized = _finalize_groups(groups, intended_by_stage=intended_by_stage, stats=stats, np=np)
    paired_out = _finalize_groups(paired, intended_by_stage=intended_by_stage, stats=stats, np=np)
    date_rows = _date_rows_from_groups(groups) + _date_rows_from_groups(paired)
    denominators = _write_series_table(outputs, prefix + '-date-metrics', _date_table(date_rows, pa))
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
        'formation_contrast_sign': 'right_minutes_minus_left_minutes_for_left_vs_right',
    }, kind='auction_flow_window_paired_contrasts_v1')
    completeness_out = {
        **completeness,
        'economic_dates': sorted(completeness['economic_dates']),
        'calendar_state_counts': dict(completeness['calendar_state_counts']),
        'expected_semantic_events': len(expected_sids),
    }
    coverage = []
    for stage in (*STAGE_ORDER, 'unassigned'):
        coverage.append({
            'collection': collection, 'root': root, 'year': year, 'stage': stage,
            'intended_dates': len(intended_by_stage[(root, year, stage)]),
            'groups': sum(1 for group in finalized + paired_out if group.get('stage') == stage),
        })
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
    return ref, part, measurement, _bounded_summaries(finalized + paired_out), coverage


def _unique_population_counts(plan, selected_keys):
    seen = set()
    processed = 0
    unavailable = 0
    feature_rows = 0
    label_rows = 0
    for key in selected_keys:
        for unit in plan['members'][key]:
            ukey = _unit_identity_key(unit)
            if ukey in seen:
                continue
            seen.add(ukey)
            processed += 1
            if _unit_unavailable(unit):
                unavailable += 1
                continue
            feature_rows += int(unit.get('feature_rows') or 0)
            label_rows += int(unit.get('label_rows') or 0)
    return {
        'processed_source_windows': processed,
        'unavailable_source_windows': unavailable,
        'feature_rows': feature_rows,
        'label_rows': label_rows,
        'unique_source_units': len(seen),
    }


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
        row = load_reference(ref, maximum=JSON_LOAD_MAX)
        accepted[row['identity']] = (ref, row)
    total = _empty_completeness()
    total['event_source_rows'] = event_stats['source_event_rows']
    partition_refs, group_refs, denominator_refs, paired_refs, event_link_refs = [], [], [], [], []
    reused, recomputed, measurements = 0, 0, []
    summaries = []
    coverage_rows = []
    global_window_sids = set()
    global_receiver_sids = set()
    np = pa = None
    for ordinal, key in enumerate(selected_keys):
        collection, root, year = key
        members = plan['members'][key]
        source_refs = window_partition_source_refs(members)
        identity = window_partition_identity(
            frozen, collection=collection, root=root, year=year, source_refs=source_refs)
        if identity in accepted and accepted[identity][1].get('passed') is True:
            ref, part = accepted[identity]
            reused_receivers, reused_windows = _authenticate_reused_partition(part, load_reference)
            global_receiver_sids.update(reused_receivers)
            global_window_sids.update(reused_windows)
            for stage in (*STAGE_ORDER, 'unassigned'):
                coverage_rows.append({'collection':collection,'root':root,'year':year,'stage':stage,'intended_dates':len(intended_date_universe(year,stage,root,policy)), 'groups':None})
            reused += 1
            groups_payload = _authenticate_json_ref(
                part['groups'], load_reference,
                kinds={'auction_flow_window_group_statistics_v1'},
            )
            paired_payload = _authenticate_json_ref(
                part['paired'], load_reference,
                kinds={'auction_flow_window_paired_contrasts_v1'},
            )
            summaries.extend(_bounded_summaries(
                (groups_payload.get('groups') or []) + (paired_payload.get('groups') or [])))
            del groups_payload, paired_payload
        else:
            if np is None:
                np, pa = _require_numpy(), _require_pyarrow()
            ref, part, measurement, part_summary, part_coverage = _compute_window_partition(
                key=key, members=members, identity=identity, source_refs=source_refs,
                contract=frozen, stats=stats, policy=policy, calendar=calendar,
                events=events, outputs=outputs, ordinal=ordinal, np=np, pa=pa,
                global_window_sids=global_window_sids, global_receiver_sids=global_receiver_sids,
            )
            recomputed += 1
            measurements.append({**measurement, 'partition_key': encode_window_partition_key(key)})
            summaries.extend(part_summary)
            coverage_rows.extend(part_coverage)
        partition_refs.append(ref)
        group_refs.append(part['groups'])
        denominator_refs.append(part['denominators'])
        paired_refs.append(part.get('paired'))
        event_link_refs.append(part.get('event_links'))
        part_complete = part['completeness']
        total['eligible_feature_rows'] += part_complete.get('eligible_feature_rows', 0)
        total['eligible_joined_rows'] += part_complete.get('eligible_joined_rows', 0)
        total['censored_feature_rows'] += part_complete.get('censored_feature_rows', 0)
        total['censored_label_rows'] += part_complete.get('censored_label_rows', 0)
        total['missing_reference_rows'] += part_complete.get('missing_reference_rows', 0)
        total['unassigned_stage_rows'] += part_complete.get('unassigned_stage_rows', 0)
        total['out_of_primary_year_rows'] += part_complete.get('out_of_primary_year_rows', 0)
        total['unknown_event_coverage_dates'] += part_complete.get('unknown_event_coverage_dates', 0)
        total['inconsistent_event_clock_rows'] += part_complete.get('inconsistent_event_clock_rows', 0)
        total['date_only_events'] += part_complete.get('date_only_events', 0)
        total['economic_dates'].update(part_complete.get('economic_dates') or ())
        total['calendar_state_counts'].update(part_complete.get('calendar_state_counts') or {})
    unique = _unique_population_counts(plan, selected_keys)
    total['processed_source_windows'] = unique['processed_source_windows']
    total['unavailable_source_windows'] = unique['unavailable_source_windows']
    total['feature_rows'] = unique['feature_rows']
    total['label_rows'] = unique['label_rows']
    all_sids = {event.get('semantic_id') for event in events}
    total['unique_semantic_events'] = len(all_sids)
    total['date_only_events'] = sum(not timed_event_eligible(e) or not event_clock_consistent(e) for e in events)
    total['inconsistent_event_clock_rows'] = sum(timed_event_eligible(e) and not event_clock_consistent(e) for e in events)
    total['events_with_receiver'] = len(global_receiver_sids)
    total['events_without_receiver'] = len(all_sids - global_receiver_sids)
    total['events_without_window'] = len(all_sids - global_window_sids)
    if pa is None:
        pa = _require_pyarrow()
    event_denominators = _write_series_table(
        outputs, 'window-event-denominators',
        _global_event_table(events, global_receiver_sids, global_window_sids, pa),
    )
    cpu = time_mod.process_time() - started
    wall = time_mod.monotonic() - wall_started
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
        'unique_source_units': unique['unique_source_units'],
    }
    completeness_ref = outputs.json(
        'window-statistics-completeness.json', completeness_out,
        kind='auction_flow_window_completeness_v1')
    refs = {
        'partitions': partition_refs, 'groups': group_refs, 'denominators': denominator_refs,
        'paired': paired_refs, 'event_links': event_link_refs,
        'event_denominators': event_denominators,
        'completeness': completeness_ref,
        'event_source': event_ref, 'cash_calendar': getattr(calendar, 'reference', None),
    }
    report_text = _markdown_report(
        summaries=summaries, completeness=total, population=rec,
        processed=total['processed_source_windows'], cpu=cpu, output_bytes=outputs.written,
        reused=reused, recomputed=recomputed, selected=selected_keys, all_keys=plan['keys'],
        event_stats=event_stats, refs=refs, coverage=coverage_rows,
    )
    with outputs.create('window-measurement-statistics-report.md') as stream:
        stream.write(report_text.encode())
    report_ref = outputs.reference(
        'window-measurement-statistics-report.md', kind='auction_flow_window_statistics_report')
    refs['report'] = report_ref
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
        'unique_source_units': unique['unique_source_units'],
    }
    summary = {
        'kind': KIND, 'version': VERSION, 'passed': True, 'family_complete': False,
        'complete_family_statistics': False, 'all_family_validation_complete': False,
        'full_window_population_reduced': (not subset) and len(selected_keys) == len(plan['keys']),
        'selected_partition_subset': subset, 'counts': counts,
        'partition_measurements': measurements, 'cpu_seconds': cpu, 'wall_seconds': wall,
        'output_bytes': outputs.written, 'reused_partitions': reused, 'new_partitions': recomputed,
        'partition_keys': [encode_window_partition_key(key) for key in selected_keys],
        'refs': refs,
    }
    summary_ref = outputs.json('window-statistics-summary.json', summary, kind=KIND)
    summary['refs']['summary'] = summary_ref
    return summary


__all__ = [
    'FEATURE_QUALITY_FLAGS', 'FROZEN_CONTRACT_KIND', 'KIND', 'POPULATION_KIND', 'VERSION',
    'alias_collection_dates', 'cohort_signed_fraction', 'cohort_volume_fraction',
    'complete_binary_flag', 'decode_window_partition_key', 'dedup_scheduled_events',
    'directional_concordance', 'encode_window_partition_key', 'equal_date_mean',
    'event_clock_consistent', 'event_coverage_state', 'event_in_formation',
    'event_relative_bucket', 'feature_quality_eligible', 'formation_pair_eligible',
    'formation_volume_per_second', 'future_displacements', 'intended_date_universe',
    'known_at_available_at_cut', 'latency_pair_eligible', 'reference_inside_formation',
    'run_window_statistics', 'same_actual_reference', 'scientific_contract_definition',
    'scientific_join_eligibility', 'timed_event_eligible', 'true_path_range',
    'unknown_volume_fraction', 'window_partition_identity', 'window_partition_plan',
]
