"""Complete-population descriptive core measurement statistics.

This reducer answers the frozen core-statistics questions from retained
atomic observation tables.  It does not complete the auction/flow family,
choose a source winner, or invent cash RTH on unpublished or closed dates.

The admitted cash calendar is an explicit contract input.  Production must
supply the same fully qualified reference already used by the auction-flow
study protocol; fixtures may pass an explicit session table instead.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo
import math
import time as time_mod

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.research.auction_flow_measurements import SOURCE_FILTERS
from trading_research.research.auction_flow_production import source_variant
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries, read_series_tables
from trading_research.research.date_statistics import (
    _batch_bootstrap_components,
    _metric_result,
    _moving_weights,
    _numpy,
)


VERSION = 'auction-flow-core-statistics-v1'
KIND = 'auction_flow_core_statistics_result_v1'
FROZEN_CONTRACT_KIND = 'auction_flow_core_statistics_contract_v1'
POPULATION_KIND = 'auction_flow_observation_population_v1'
ZONE = 'America/New_York'
FUTURES_ROLL_HOUR = 18
NS = 1_000_000_000
MAXIMUM_JSON_BYTES = 512 * 1024 ** 2
BATCH_HINT = 65536

# Exact admitted study-protocol calendar. Codex must freeze this on the
# statistics contract before a production run; this module will not invent
# regular 09:30-16:00 on holidays or unpublished dates.
REQUIRED_CASH_CALENDAR_REFERENCE = {
    'kind': 'cash_rth_calendar',
    'path': '/workspace/trading-research/configs/cash-rth-calendar-research-v1.json',
    'sha256': 'f069df0ccbb8318f1c675a05d9deed64ad681ebe1e47dd8573a6b18266665818',
    'size_bytes': 6922,
}

FROZEN_STAGE_POLICY = {
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
STAGE_ORDER = ('training', 'development', 'calibration', 'confirmation')
QUANTILE_LEVELS = (0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99)
SESSIONS = ('cash_rth', 'pre_rth', 'futures_wallclock_18_17', 'off_session')

PROVENANCE_FIELDS = (
    'root', 'source_path', 'source_metadata_sha256', 'source_variant',
    'source_window_start_ns', 'source_window_end_ns',
    'receipt_sha256', 'measurement_sha256', 'canonical_raw_values_sha256',
)
HISTORICAL_STATE_FIELDS = (
    'coordinate_complete', 'supplied_raw_coordinate_stable', 'source_instrument_presence',
    'source_coverage_complete', 'flow_history_complete', 'price_history_complete',
    'empty_observed_window', 'quote_coverage_complete',
    'full_standing_window_eligible', 'full_pressure_transition_window_eligible',
    'archive_window_complete',
    'raw_rows', 'non_snapshot_rows', 'gap_rows', 'snapshot_rows',
    'unknown_action_rows', 'invalid_trade_size_rows', 'clock_uncertain_intervals',
)
JOIN_FIELDS = ('root', 'instrument_id', 'event_start_ns', 'event_end_ns')
_COHORT_STATE_SUFFIXES = (
    'coverage_complete', 'true_signed_lower', 'true_signed_upper',
    'high_at_ns', 'low_at_ns', 'high_source_order', 'low_source_order',
)


def iter_observation_tables(series):
    """Yield logical observation tables from a retained verified Parquet series."""
    yield from read_series_tables(series)


def path_true_ohlc(path):
    """True OHLC and close-only information loss of an ordered CVD path."""
    if not isinstance(path, (list, tuple)) or len(path) < 1:
        raise ContractError('CVD path must be a nonempty ordered sequence')
    values = []
    for item in path:
        if isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(item):
            raise ContractError('CVD path values must be finite numbers')
        values.append(item)
    return information_loss_terms(values[0], max(values), min(values), values[-1])


def information_loss_terms(open_value, high, low, close):
    """True excursion, close excursion, and their nonnegative difference."""
    for name, value in (('open', open_value), ('high', high), ('low', low), ('close', close)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ContractError(f'{name} must be a finite number')
    if high < max(open_value, close) or low > min(open_value, close):
        raise ContractError('true OHLC extrema are inconsistent with the open/close path')
    excursion = high - low
    close_excursion = abs(close - open_value)
    loss = excursion - close_excursion
    return {
        'open': open_value, 'high': high, 'low': low, 'close': close,
        'true_cvd_excursion': excursion,
        'close_excursion': close_excursion,
        'information_loss': loss,
        'information_loss_positive': loss > 0,
    }


def signed_close_open(*, buy, sell, unknown):
    """Known-side signed close-open. Unknown mass is retained and never signed."""
    for name, value in (('buy', buy), ('sell', sell), ('unknown', unknown)):
        if type(value) is bool or type(value) is not int:
            raise ContractError(f'{name} must be an exact integer')
    _ = unknown
    return buy - sell


def occupancy_fractions(*, all_prints, all_volume, cohorts):
    """Count and size occupancy. Overlapping hard cohorts are not a partition."""
    if type(all_prints) is bool or type(all_prints) is not int or all_prints < 0:
        raise ContractError('all_prints must be a nonnegative integer')
    if type(all_volume) is bool or type(all_volume) is not int or all_volume < 0:
        raise ContractError('all_volume must be a nonnegative integer')
    if not isinstance(cohorts, dict) or not cohorts:
        raise ContractError('cohort occupancy requires an explicit cohort mapping')
    out = {}
    for name, pair in cohorts.items():
        if not isinstance(name, str) or not name:
            raise ContractError('cohort names must be nonempty strings')
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ContractError('each cohort must supply (prints, volume)')
        prints, volume = pair
        if type(prints) is bool or type(prints) is not int or prints < 0:
            raise ContractError(f'{name} prints must be a nonnegative integer')
        if type(volume) is bool or type(volume) is not int or volume < 0:
            raise ContractError(f'{name} volume must be a nonnegative integer')
        out[name] = {
            'count': None if all_prints == 0 else prints / all_prints,
            'size': None if all_volume == 0 else volume / all_volume,
        }
    return out


def observe_metric(value, *, eligible, reason):
    """Record an eligible value, including true zero. Missing stays excluded."""
    if type(eligible) is not bool:
        raise ContractError('metric eligibility must be an explicit boolean')
    if type(reason) is not str or not reason:
        raise ContractError('exclusion reason must be a concrete string')
    if not eligible:
        return None, reason
    if value is None:
        return None, 'missing_value'
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ContractError('eligible metric values must be finite numbers or missing')
    return float(value), None


def economic_date(event_start_ns, *, zone=ZONE):
    """NY futures-clock date: local 18:00 onward moves to the next civil date."""
    if type(event_start_ns) is bool or type(event_start_ns) is not int:
        raise ContractError('event_start_ns must be an exact integer nanosecond')
    local = datetime.fromtimestamp(event_start_ns // NS, timezone.utc).astimezone(ZoneInfo(zone))
    day = local.date()
    if local.hour >= FUTURES_ROLL_HOUR:
        day = day + timedelta(days=1)
    return day.isoformat()


def stage_name(root, economic_iso, stage_policy=None):
    """Half-open frozen stage interval; other dates stay unassigned."""
    if type(root) is not str or not root:
        raise ContractError('stage assignment requires a concrete root')
    if type(economic_iso) is not str:
        raise ContractError('stage assignment requires an ISO economic date')
    policy = FROZEN_STAGE_POLICY if stage_policy is None else stage_policy
    if root not in policy:
        return 'unassigned'
    row = policy[root]
    for name in STAGE_ORDER:
        bounds = row.get(name)
        if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
            raise IntegrityError(f'stage_policy.{root}.{name} must be a half-open [start, end) pair')
        start, end = bounds
        if start <= economic_iso < end:
            return name
    return 'unassigned'


class ExplicitCashSessions:
    """Fixture/production adapter: published resolver or an explicit date table.

    A missing table date is missing calendar, not regular 09:30-16:00. Closed
    rows expose no open interval. Production uses CashCalendar.resolve.
    """

    def __init__(self, table=None, *, published=None, zone=ZONE, reference=None):
        if (table is None) == (published is None):
            raise ContractError('exactly one of an explicit session table or a published calendar is required')
        if table is not None and not isinstance(table, dict):
            raise ContractError('cash_session_table must be an object keyed by ISO date')
        self.table = None if table is None else dict(table)
        self.published = published
        self.zone = zone
        self.reference = reference

    def resolve(self, day, *, cut):
        if type(day) is not date:
            raise ContractError('cash session resolve requires a civil date')
        if type(cut) is bool or type(cut) is not int:
            raise ContractError('cash session resolve requires an integer known-at cut')
        if self.published is not None:
            return self.published.resolve(day, cut=cut)
        row = self.table.get(day.isoformat())
        if row is None:
            raise DependencyUnavailable(
                f'cash-calendar date {day.isoformat()} is not published or supplied at this cut'
            )
        if not isinstance(row, dict) or row.get('state') not in ('closed', 'regular', 'early_close'):
            raise ContractError(f'cash session {day.isoformat()} must declare closed, regular, or early_close')
        if row['state'] == 'closed':
            if row.get('open') is not None or row.get('close') is not None:
                raise ContractError('closed cash date cannot expose an open interval')
            return SimpleNamespace(state='closed', open_at=None, close_at=None)
        opened, closed = row.get('open'), row.get('close')
        if type(opened) is not str or type(closed) is not str:
            raise ContractError(
                f'open cash date {day.isoformat()} must declare explicit open and close wall times; '
                'regular 09:30-16:00 is not invented'
            )
        return SimpleNamespace(
            state=row['state'],
            open_at=local_timestamp(day, time.fromisoformat(opened), self.zone),
            close_at=local_timestamp(day, time.fromisoformat(closed), self.zone),
        )


def classify_session(event_start_ns, event_end_ns, *, calendar, known_at_ns, zone=ZONE):
    """Assign session from the half-open event start; known_at stays separate.

    cash_rth uses the admitted calendar open/close only. pre_rth is the named
    06:00-09:30 wall window. futures_wallclock_18_17 is observed, not a
    certified exchange calendar. Closed or missing calendar never becomes
    cash_rth.
    """
    if type(event_start_ns) is bool or type(event_start_ns) is not int:
        raise ContractError('event_start_ns must be an exact integer nanosecond')
    if type(event_end_ns) is bool or type(event_end_ns) is not int or event_end_ns <= event_start_ns:
        raise ContractError('event interval must be a positive half-open [start, end)')
    if type(known_at_ns) is bool or type(known_at_ns) is not int:
        raise ContractError('known_at_ns must be an exact integer nanosecond')
    eco = economic_date(event_start_ns, zone=zone)
    day = date.fromisoformat(eco)
    calendar_state = 'missing'
    open_at = close_at = None
    try:
        cash = calendar.resolve(day, cut=known_at_ns)
        calendar_state = cash.state
        open_at, close_at = cash.open_at, cash.close_at
    except DependencyUnavailable:
        calendar_state = 'missing'
    in_cash = (
        calendar_state in ('regular', 'early_close')
        and open_at is not None and close_at is not None
        and open_at <= event_start_ns < close_at
    )
    in_pre = (
        local_timestamp(day, time(6, 0), zone)
        <= event_start_ns
        < local_timestamp(day, time(9, 30), zone)
    )
    in_futures = (
        local_timestamp(day - timedelta(days=1), time(18, 0), zone)
        <= event_start_ns
        < local_timestamp(day, time(17, 0), zone)
    )
    if in_cash:
        session = 'cash_rth'
    elif in_pre:
        session = 'pre_rth'
    elif in_futures:
        session = 'futures_wallclock_18_17'
    else:
        session = 'off_session'
    return {
        'economic_date': eco,
        'year': day.year,
        'session': session,
        'calendar_state': calendar_state,
        'in_cash_rth': in_cash,
        'in_pre_rth': in_pre,
        'in_futures_wallclock': in_futures,
        'known_at_ns': known_at_ns,
        'event_end_ns': event_end_ns,
    }


def labeled_date_and_event_means(date_sums, date_counts):
    """Equal-date mean versus event-weighted mean. Missing dates are absent keys."""
    if not isinstance(date_sums, dict) or not isinstance(date_counts, dict):
        raise ContractError('date sums and counts must be objects')
    if set(date_sums) != set(date_counts):
        raise ContractError('date sums and counts must cover the same dates')
    date_means = []
    total = 0.0
    events = 0
    for day, count in date_counts.items():
        if type(count) is bool or type(count) is not int or count < 0:
            raise ContractError('date counts must be nonnegative integers')
        if count == 0:
            raise ContractError('zero-count dates must be omitted rather than converted to zero')
        value = date_sums[day]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ContractError('date sums must be finite numbers')
        date_means.append(value / count)
        total += value
        events += count
    if not date_means:
        return {'date_mean': None, 'event_mean': None, 'independent_dates': 0, 'events': 0}
    return {
        'date_mean': math.fsum(date_means) / len(date_means),
        'event_mean': total / events,
        'independent_dates': len(date_means),
        'events': events,
    }


def shared_moving_block_intervals(date_sums, date_counts, *, seed, block_length, replicates,
                                  confidence, minimum_independent_dates, minimum_events,
                                  return_weights=False, intended_dates=None):
    """Date-mean and event-mean intervals with one shared weight matrix."""
    if not isinstance(date_sums, dict) or not date_sums:
        raise ContractError('at least one named metric date-sum mapping is required')
    if set(date_sums) != set(date_counts):
        raise ContractError('bootstrap metrics must share names between sums and counts')
    dates = sorted(set(intended_dates) if intended_dates is not None
                   else {day for cells in date_sums.values() for day in cells})
    if not dates:
        raise ContractError('bootstrap requires at least one economic date')
    np = _numpy()
    names = tuple(date_sums)
    normalised = {}
    for name in names:
        if not isinstance(date_sums[name], dict) or not isinstance(date_counts[name], dict):
            raise ContractError(f'{name} sums and counts must be date mappings')
        extras = set(date_sums[name]).union(date_counts[name]).difference(dates)
        if extras:
            raise ContractError(f'{name} contains dates outside the shared economic-date order')
        sums = []
        counts = []
        for day in dates:
            count = date_counts[name].get(day, 0)
            if type(count) is bool or type(count) is not int or count < 0:
                raise ContractError(f'{name} date counts must be nonnegative integers')
            if count == 0:
                if day in date_sums[name]:
                    raise ContractError(f'{name} cannot publish a sum for a zero-count date')
                sums.append(0.0)
                counts.append(0)
                continue
            value = date_sums[name][day]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ContractError(f'{name} date sums must be finite')
            sums.append(float(value))
            counts.append(count)
        normalised[name] = {
            'name': name, 'cells': (), 'sums': tuple(sums), 'counts': tuple(counts),
            'valid_dates': sum(c > 0 for c in counts),
            'valid_events': sum(counts),
        }
    weights, starts = _moving_weights(
        np, len(dates), seed=seed, block_length=block_length, replicates=replicates,
    )
    metrics = {}
    for estimator in ('date_mean', 'event_mean'):
        numerators, denominators = _batch_bootstrap_components(
            np, normalised, names, estimator=estimator, weights=weights, replicates=replicates,
        )
        for index, name in enumerate(names):
            result, _, _ = _metric_result(
                np, normalised[name], tuple(dates), weights, starts,
                estimator=estimator, seed=seed, block_length=block_length,
                replicates=replicates, confidence=float(confidence),
                minimum_dates=minimum_independent_dates, minimum_events=minimum_events,
                bootstrap_numerator=numerators[:, index],
                bootstrap_denominator=denominators[:, index],
                retain_replicate_estimates=False,
            )
            metrics.setdefault(name, {})[estimator] = result
    payload = {
        'intended_dates': list(dates),
        'intended_date_count': len(dates),
        'metrics': metrics,
        'shared_weights': True,
        'seed': int(seed),
        'block_length': int(block_length),
        'replicates': int(replicates),
        'confidence': float(confidence),
    }
    if return_weights:
        payload['bootstrap_weights'] = {
            'date_order': list(dates),
            'weights': weights.tolist(),
            'block_starts': [list(starts_row) for starts_row in starts],
            'circular_end_wrap': False,
        }
    return payload


def alias_independent_dates(rows):
    """Unique economic dates per raw-stream hash. Aliases are not extra support."""
    if not isinstance(rows, (list, tuple)):
        raise ContractError('alias rows must be a sequence')
    by_sha = {}
    variants = {}
    windows = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ContractError('each alias row must be an object')
        sha = row.get('canonical_raw_values_sha256')
        day = row.get('economic_date')
        variant = row.get('source_variant')
        if type(sha) is not str or len(sha) != 64:
            raise ContractError('canonical_raw_values_sha256 must be a 64-character hex digest')
        if type(day) is not str or type(variant) is not str or not variant:
            raise ContractError('alias rows require economic_date and source_variant')
        by_sha.setdefault(sha, set()).add(day)
        variants.setdefault(sha, set()).add(variant)
        windows.setdefault(sha, 0)
        windows[sha] += 1
    return {
        sha: {
            'canonical_raw_values_sha256': sha,
            'source_variants': sorted(variants[sha]),
            'alias_source_variant_count': len(variants[sha]),
            'source_window_rows': windows[sha],
            'independent_economic_dates': sorted(by_sha[sha]),
            'independent_economic_date_count': len(by_sha[sha]),
        }
        for sha in sorted(by_sha)
    }


def _value_fields(names, *, extra_excluded=()):
    excluded = set(PROVENANCE_FIELDS)
    excluded.update(JOIN_FIELDS)
    excluded.update(HISTORICAL_STATE_FIELDS)
    excluded.update(extra_excluded)
    excluded.add('atomic_bin')
    excluded.add('contract_key')
    for name in SOURCE_FILTERS:
        for suffix in _COHORT_STATE_SUFFIXES:
            excluded.add(f'{name}__{suffix}')
    return tuple(name for name in names if name not in excluded)


def join_observations(left_rows, right_rows, *, value_fields=None):
    """Match root/instrument/event interval only when raw coordinates are compatible.

    Distinct contract keys are not joined. Provenance and historical-state
    columns are not required to be equal.
    """
    if not isinstance(left_rows, (list, tuple)) or not isinstance(right_rows, (list, tuple)):
        raise ContractError('join inputs must be row sequences')
    fields = value_fields
    if fields is None and left_rows:
        fields = _value_fields(left_rows[0])
    if fields is None:
        fields = ()
    left_map, right_map = {}, {}
    mismatched_contract = 0
    incompatible = 0

    def place(store, row, side):
        nonlocal incompatible
        if not isinstance(row, dict):
            raise ContractError(f'{side} join row must be an object')
        try:
            key = tuple(row[name] for name in JOIN_FIELDS)
        except KeyError as exc:
            raise ContractError(f'{side} join row lost {exc.args[0]}') from exc
        if not row.get('coordinate_complete') or not row.get('contract_key'):
            incompatible += 1
            return None
        store.setdefault(key, []).append(row)
        return key

    for row in left_rows:
        place(left_map, row, 'left')
    for row in right_rows:
        place(right_map, row, 'right')
    matched_equal = matched_different = 0
    disagreements = Counter()
    magnitudes = defaultdict(list)
    unmatched_left = 0
    unmatched_right = 0
    seen_right = set()
    for key, lefts in left_map.items():
        rights = right_map.get(key)
        if not rights:
            unmatched_left += len(lefts)
            continue
        seen_right.add(key)
        for left in lefts:
            partner = None
            for right in rights:
                if left.get('contract_key') != right.get('contract_key'):
                    continue
                partner = right
                break
            if partner is None:
                mismatched_contract += 1
                continue
            different = False
            for field in fields:
                lv, rv = left.get(field, None), partner.get(field, None)
                if lv != rv:
                    different = True
                    disagreements[field] += 1
                    if isinstance(lv, (int, float)) and isinstance(rv, (int, float)) and not isinstance(lv, bool) and not isinstance(rv, bool):
                        magnitudes[field].append(abs(float(lv) - float(rv)))
            if different:
                matched_different += 1
            else:
                matched_equal += 1
    for key, rights in right_map.items():
        if key not in left_map:
            unmatched_right += len(rights)
    summary = {}
    for field, values in magnitudes.items():
        summary[field] = {
            'count': len(values),
            'mean_abs_difference': None if not values else math.fsum(values) / len(values),
            'maximum_abs_difference': None if not values else max(values),
        }
    return {
        'matched_equal': matched_equal,
        'matched_different': matched_different,
        'unmatched_left': unmatched_left,
        'unmatched_right': unmatched_right,
        'incompatible_coordinates': incompatible,
        'mismatched_contract': mismatched_contract,
        'metric_disagreements': dict(disagreements),
        'magnitude_summaries': summary,
    }


def _require_numpy():
    np = _numpy()
    return np


def _require_pyarrow():
    import pyarrow as pa
    if getattr(pa, '__version__', None) != '25.0.1':
        raise ContractError('core statistics require the pinned PyArrow 25.0.1 provider')
    return pa


def _require_contract(contract):
    if not isinstance(contract, dict) or contract.get('kind') != FROZEN_CONTRACT_KIND:
        raise IntegrityError('frozen auction_flow_core_statistics_contract_v1 required')
    if contract.get('version') not in (1, 2):
        raise IntegrityError('core statistics contract version changed')
    if contract.get('family_statistics_complete') is not False:
        raise IntegrityError('contract must retain family_statistics_complete=false')
    clock = contract.get('clock')
    if not isinstance(clock, dict) or clock.get('atomic_width_ns') != 60_000_000_000:
        raise IntegrityError('frozen atomic width is 60000000000 ns')
    if clock.get('interval') != 'half-open original event interval; known_at retained separately':
        raise IntegrityError('frozen half-open event interval changed')
    estimands = contract.get('statistical_estimands')
    if not isinstance(estimands, dict):
        raise IntegrityError('frozen statistical estimands are required')
    if (estimands.get('seed') != 20260908 or estimands.get('block_length') != 5
            or estimands.get('bootstrap_replicates') != 1000
            or float(estimands.get('confidence')) != 0.95):
        raise IntegrityError('frozen date-block uncertainty settings changed')
    if tuple(estimands.get('quantiles') or ()) != QUANTILE_LEVELS:
        raise IntegrityError('frozen sample quantile levels changed')
    if (estimands.get('minimum_events') != 20 or estimands.get('minimum_independent_dates') != 100):
        raise IntegrityError('frozen support minima changed')
    policy = contract.get('stage_policy')
    if not isinstance(policy, dict):
        raise IntegrityError('frozen stage_policy is required')
    for root, expected in FROZEN_STAGE_POLICY.items():
        got = policy.get(root)
        if not isinstance(got, dict):
            raise IntegrityError(f'frozen stage_policy.{root} is required')
        for name, bounds in expected.items():
            if tuple(got.get(name) or ()) != bounds:
                raise IntegrityError(f'frozen stage_policy.{root}.{name} changed')
    return estimands, policy


def _load_calendar(contract, load_reference):
    table = contract.get('cash_session_table')
    reference = contract.get('cash_calendar')
    if table is not None:
        return ExplicitCashSessions(table, reference={'kind': 'explicit_cash_session_table'})
    if reference is None:
        raise ContractError(
            'core statistics require contract.cash_calendar equal to the admitted '
            f'AUCTION_FLOW_STUDY_V1 cash_rth_calendar {REQUIRED_CASH_CALENDAR_REFERENCE!r} '
            'so it can be frozen before execution; regular 09:30-16:00 is not invented '
            'on holidays or unpublished dates. Fixtures may pass cash_session_table instead.'
        )
    if (not isinstance(reference, dict) or type(reference.get('path')) is not str
            or type(reference.get('sha256')) is not str):
        raise IntegrityError('cash_calendar must be a fully qualified path/sha256 reference')
    if callable(load_reference):
        payload = load_reference(reference)
        if not isinstance(payload, dict) or payload.get('schema') != 'published-cash-rth-calendar-v1':
            raise IntegrityError('cash_calendar reference is not the published cash RTH calendar')
    from pathlib import Path
    from trading_research.foundations.cash_calendar import CashCalendar
    return ExplicitCashSessions(published=CashCalendar(Path(reference['path'])), reference=reference)


def _optional_numeric(table, name, np, *, kind):
    col = table.column(name).combine_chunks()
    length = len(col)
    if col.null_count == length:
        return np.zeros(length, dtype=np.float64), np.zeros(length, dtype=bool)
    valid = (np.ones(length, dtype=bool) if col.null_count == 0
             else col.is_valid().to_numpy(zero_copy_only=False))
    if col.null_count:
        import pyarrow.compute as pc
        filled = pc.fill_null(col, 0)
        values = filled.to_numpy(zero_copy_only=False).astype(np.float64, copy=False)
    else:
        values = col.to_numpy(zero_copy_only=False).astype(np.float64, copy=False)
    if kind == 'float':
        valid = valid & np.isfinite(values)
    return values, valid


def _bool_col(table, name, np):
    return table.column(name).combine_chunks().to_numpy(zero_copy_only=False).astype(bool, copy=False)


def _int_col(table, name, np):
    return table.column(name).combine_chunks().to_numpy(zero_copy_only=False).astype(np.int64, copy=False)


class _MetricStore:
    def __init__(self, np):
        self.np = np
        self.parts = []
        self.n = 0
        self.total = 0.0
        self.total_sq = 0.0
        self.minimum = None
        self.maximum = None
        self.date_sum = {}
        self.date_count = {}

    def extend(self, values, dates):
        if values.size == 0:
            return
        self.n += int(values.size)
        self.total += float(values.sum(dtype=self.np.float64))
        self.total_sq += float(self.np.square(values, dtype=self.np.float64).sum(dtype=self.np.float64))
        lo, hi = float(values.min()), float(values.max())
        self.minimum = lo if self.minimum is None else min(self.minimum, lo)
        self.maximum = hi if self.maximum is None else max(self.maximum, hi)
        if type(dates) is not str:
            raise ContractError('metric batch must belong to one economic date')
        self.date_sum[dates] = self.date_sum.get(dates, 0.0) + float(values.sum())
        self.date_count[dates] = self.date_count.get(dates, 0) + int(values.size)
        self.parts.append(values.copy())

    def array(self):
        if not self.parts:
            return self.np.empty(0, dtype=self.np.float64)
        values = self.np.concatenate(self.parts)
        self.parts = []
        return values


def _exact_quantiles(np, values, levels):
    if values.size == 0:
        return {str(level): None for level in levels}
    quantiles = np.quantile(values, levels, method='linear')
    return {str(level): float(item) for level, item in zip(levels, quantiles)}


def metric_unit(name):
    if name.endswith('information_loss_positive'):
        return 'binary indicator'
    if name.endswith('occupancy') or 'fraction' in name or 'concentration' in name or 'imbalance' in name:
        return 'dimensionless'
    if name.endswith('_ns'):
        return 'nanoseconds'
    if 'variance' in name:
        return 'ticks squared'
    if 'ticks' in name or 'microprice' in name:
        return 'quarter-point ticks'
    if name.endswith('prints'):
        return 'trade prints'
    if name in ('occupied_price_rows', 'complete_occupied_price_rows', 'poc_maximizer_count', 'complete_poc_maximizer_count'):
        return 'price rows'
    return 'contracts'


def _moments(store, values):
    count = int(values.size)
    if count == 0:
        return {
            'count': 0, 'mean': None, 'variance': None, 'standard_deviation': None,
            'minimum': None, 'maximum': None, 'sum': 0.0,
        }
    mean = float(store.total / count)
    variance = None if count < 2 else float(store.np.var(values, ddof=1))
    return {
        'count': count,
        'mean': mean,
        'variance': variance,
        'standard_deviation': None if variance is None else math.sqrt(variance),
        'minimum': store.minimum,
        'maximum': store.maximum,
        'sum': float(store.total),
    }


def _table_metric_columns(table, np):
    """Vectorized declared metrics. Null/ineligible stays masked, never zero-filled."""
    n = len(table)
    columns = []
    all_prints = _int_col(table, 'all__prints', np)
    all_volume = _int_col(table, 'all__volume', np)
    flow_ok = _bool_col(table, 'flow_history_complete', np)
    price_ok = _bool_col(table, 'price_history_complete', np)
    coord_ok = _bool_col(table, 'coordinate_complete', np)
    quote_ok = _bool_col(table, 'quote_coverage_complete', np)
    standing_ok = _bool_col(table, 'full_standing_window_eligible', np)
    pressure_ok = _bool_col(table, 'full_pressure_transition_window_eligible', np)
    observed_presence = (_bool_col(table, 'source_instrument_presence', np)
                         | (_int_col(table, 'raw_rows', np) > 0))
    starts = _int_col(table, 'event_start_ns', np)
    ends = _int_col(table, 'event_end_ns', np)
    width = (ends - starts).astype(np.float64)

    def add(name, values, valid, reason):
        columns.append((name, values.astype(np.float64, copy=False), valid.astype(bool, copy=False), reason))

    for cohort in SOURCE_FILTERS:
        buy = _int_col(table, f'{cohort}__buy', np)
        sell = _int_col(table, f'{cohort}__sell', np)
        unknown = _int_col(table, f'{cohort}__unknown', np)
        open_ = _int_col(table, f'{cohort}__open', np)
        high = _int_col(table, f'{cohort}__high', np)
        low = _int_col(table, f'{cohort}__low', np)
        close = _int_col(table, f'{cohort}__close', np)
        volume = _int_col(table, f'{cohort}__volume', np)
        prints = _int_col(table, f'{cohort}__prints', np)
        cohort_ok = _bool_col(table, f'{cohort}__coverage_complete', np)
        signed = (buy - sell).astype(np.float64)
        rng = (high - low).astype(np.float64)
        close_exc = np.abs(close - open_).astype(np.float64)
        loss = rng - close_exc
        always = observed_presence
        complete = flow_ok & cohort_ok & observed_presence
        count_valid = (all_prints > 0) & observed_presence
        size_valid = (all_volume > 0) & observed_presence
        count_occ = np.divide(prints.astype(np.float64), all_prints.astype(np.float64),
                              out=np.full(n, np.nan, dtype=np.float64), where=count_valid)
        size_occ = np.divide(volume.astype(np.float64), all_volume.astype(np.float64),
                             out=np.full(n, np.nan, dtype=np.float64), where=size_valid)
        observed = {
            f'{cohort}_buy': buy, f'{cohort}_sell': sell, f'{cohort}_unknown': unknown,
            f'{cohort}_signed_close_open': signed, f'{cohort}_volume': volume, f'{cohort}_prints': prints,
            f'{cohort}_true_cvd_excursion': rng, f'{cohort}_close_excursion': close_exc,
            f'{cohort}_information_loss': loss,
            f'{cohort}_information_loss_positive': (loss > 0).astype(np.float64),
        }
        for name, values in observed.items():
            add(name, values, always, 'no_observed_instrument')
            add(f'complete_{name}', values, complete, 'incomplete_flow_or_cohort_coverage')
        add(f'{cohort}_count_occupancy', count_occ, count_valid, 'undefined_zero_all_prints')
        add(f'{cohort}_size_occupancy', size_occ, size_valid, 'undefined_zero_all_volume')
        add(f'complete_{cohort}_count_occupancy', count_occ, count_valid & complete,
            'incomplete_or_undefined_count_occupancy')
        add(f'complete_{cohort}_size_occupancy', size_occ, size_valid & complete,
            'incomplete_or_undefined_size_occupancy')

    ofi_open, ofi_open_ok = _optional_numeric(table, 'ofi_open', np, kind='int')
    ofi_high, ofi_high_ok = _optional_numeric(table, 'ofi_high', np, kind='int')
    ofi_low, ofi_low_ok = _optional_numeric(table, 'ofi_low', np, kind='int')
    ofi_close, ofi_close_ok = _optional_numeric(table, 'ofi_close', np, kind='int')
    ofi_path = ofi_open_ok & ofi_high_ok & ofi_low_ok & ofi_close_ok
    ofi_signed = (ofi_close - ofi_open).astype(np.float64)
    ofi_rng = (ofi_high - ofi_low).astype(np.float64)
    ofi_close_exc = np.abs(ofi_close - ofi_open).astype(np.float64)
    ofi_loss = ofi_rng - ofi_close_exc
    ofi_observed = ofi_path
    ofi_eligible = ofi_path & pressure_ok
    add('ofi_observed_signed_close_open', ofi_signed, ofi_observed, 'missing_ofi_path')
    add('ofi_observed_true_excursion', ofi_rng, ofi_observed, 'missing_ofi_path')
    add('ofi_observed_close_excursion', ofi_close_exc, ofi_observed, 'missing_ofi_path')
    add('ofi_observed_information_loss', ofi_loss, ofi_observed, 'missing_ofi_path')
    add('ofi_signed_close_open', ofi_signed, ofi_eligible, 'not_full_pressure_eligible')
    add('ofi_true_excursion', ofi_rng, ofi_eligible, 'not_full_pressure_eligible')
    add('ofi_close_excursion', ofi_close_exc, ofi_eligible, 'not_full_pressure_eligible')
    add('ofi_information_loss', ofi_loss, ofi_eligible, 'not_full_pressure_eligible')
    add('ofi_information_loss_positive', (ofi_loss > 0).astype(np.float64), ofi_eligible,
        'not_full_pressure_eligible')
    add('ofi_contracts', _int_col(table, 'ofi_contracts', np), ofi_eligible, 'not_full_pressure_eligible')
    add('price_change_ofi', _int_col(table, 'price_change_ofi', np), ofi_eligible, 'not_full_pressure_eligible')
    add('same_price_size_ofi', _int_col(table, 'same_price_size_ofi', np), ofi_eligible,
        'not_full_pressure_eligible')

    duration = _int_col(table, 'standing_duration_ns', np).astype(np.float64)
    fraction = np.divide(duration, width, out=np.full(n, np.nan, dtype=np.float64), where=width > 0)
    add('quote_standing_fraction', fraction, standing_ok & (width > 0), 'not_full_standing_eligible')
    add('quote_observed_standing_fraction', fraction, observed_presence & (width > 0), 'no_observed_instrument')
    add('quote_trusted_duration_ns', duration, standing_ok, 'not_full_standing_eligible')
    add('quote_observed_trusted_duration_ns', duration, quote_ok, 'incomplete_quote_coverage')
    for column, dest, eligible, reason in (
        ('duration_mean_spread_ticks', 'duration_mean_spread_ticks', standing_ok, 'not_full_standing_eligible'),
        ('duration_mean_imbalance', 'duration_mean_imbalance', standing_ok, 'not_full_standing_eligible'),
        ('update_mean_spread_ticks', 'update_mean_spread_ticks', quote_ok, 'incomplete_quote_coverage'),
        ('update_mean_imbalance', 'update_mean_imbalance', quote_ok, 'incomplete_quote_coverage'),
        ('update_mean_microprice_residual', 'update_mean_microprice_residual', quote_ok,
         'incomplete_quote_coverage'),
    ):
        values, present = _optional_numeric(table, column, np, kind='float')
        add(dest, values, eligible & present, reason)

    high_px, high_ok = _optional_numeric(table, 'observed_high_ticks', np, kind='int')
    low_px, low_ok = _optional_numeric(table, 'observed_low_ticks', np, kind='int')
    first_px, first_ok = _optional_numeric(table, 'first_priced_ticks', np, kind='int')
    last_px, last_ok = _optional_numeric(table, 'last_priced_ticks', np, kind='int')
    variation = _int_col(table, 'observed_price_variation_ticks', np).astype(np.float64)
    rng_px = (high_px - low_px).astype(np.float64)
    displacement = (last_px - first_px).astype(np.float64)
    extrema = high_ok & low_ok
    ends_ok = first_ok & last_ok
    price_complete = price_ok & coord_ok & observed_presence
    add('observed_price_variation_ticks', variation, observed_presence, 'no_observed_instrument')
    add('complete_price_variation_ticks', variation, price_complete, 'incomplete_price_or_coordinate')
    add('observed_price_range_ticks', rng_px, extrema, 'missing_price_extrema')
    add('complete_price_range_ticks', rng_px, extrema & price_complete, 'incomplete_price_or_coordinate')
    add('observed_price_net_displacement_ticks', displacement, ends_ok, 'missing_priced_endpoints')
    add('complete_price_net_displacement_ticks', displacement, ends_ok & price_complete,
        'incomplete_price_or_coordinate')

    priced_volume = _int_col(table, 'priced_volume', np)
    vwap_ok = priced_volume > 0
    variance, var_ok = _optional_numeric(table, 'variance_ticks_squared', np, kind='float')
    conc, conc_ok = _optional_numeric(table, 'side_concentration', np, kind='float')
    mass, mass_ok = _optional_numeric(table, 'max_mass_fraction', np, kind='float')
    occupied = _int_col(table, 'occupied_price_rows', np).astype(np.float64)
    poc, poc_ok = _optional_numeric(table, 'poc_maximizer_count', np, kind='int')
    add('vwap_variance_ticks_squared', variance, vwap_ok & var_ok, 'missing_vwap_dispersion')
    add('side_concentration', conc, vwap_ok & conc_ok, 'missing_side_concentration')
    add('max_mass_fraction', mass, vwap_ok & mass_ok, 'missing_max_mass_fraction')
    add('occupied_price_rows', occupied, vwap_ok, 'missing_priced_volume')
    add('poc_maximizer_count', poc.astype(np.float64), vwap_ok & poc_ok, 'missing_poc_ties')
    add('complete_vwap_variance_ticks_squared', variance, vwap_ok & var_ok & price_complete, 'incomplete_price_or_vwap')
    add('complete_side_concentration', conc, vwap_ok & conc_ok & price_complete, 'incomplete_price_or_vwap')
    add('complete_occupied_price_rows', occupied, vwap_ok & price_complete, 'incomplete_price_or_vwap')
    add('complete_poc_maximizer_count', poc.astype(np.float64), vwap_ok & poc_ok & price_complete,
        'incomplete_price_or_vwap')
    return columns, {
        'archive_window_complete': _bool_col(table, 'archive_window_complete', np),
        'source_coverage_complete': _bool_col(table, 'source_coverage_complete', np),
        'flow_history_complete': flow_ok,
        'price_history_complete': price_ok,
        'quote_coverage_complete': quote_ok,
        'coordinate_complete': coord_ok,
    }


def _classify_rows(table, calendar, np):
    starts = _int_col(table, 'event_start_ns', np)
    ends = _int_col(table, 'event_end_ns', np)
    known = _int_col(table, 'known_at_ns', np)
    variants = table.column('source_variant').to_pylist()
    roots = table.column('root').to_pylist()
    raw_sha = table.column('canonical_raw_values_sha256').to_pylist()
    cache = {}
    keys = []
    dates = []
    years = []
    stages = []
    sessions = []
    calendar_states = []
    for index in range(len(table)):
        start = int(starts[index])
        cached = cache.get(start)
        if cached is None:
            cached = classify_session(start, int(ends[index]), calendar=calendar, known_at_ns=int(known[index]))
            cache[start] = cached
        eco = cached['economic_date']
        stage = stage_name(roots[index], eco)
        keys.append((variants[index], roots[index], str(cached['year']), stage, cached['session']))
        dates.append(eco)
        years.append(cached['year'])
        stages.append(stage)
        sessions.append(cached['session'])
        calendar_states.append(cached['calendar_state'])
    return {
        'keys': keys, 'dates': dates, 'years': years, 'stages': stages,
        'sessions': sessions, 'calendar_states': calendar_states,
        'variants': variants, 'roots': roots, 'raw_sha': raw_sha,
    }


def _add_exclusions(target, metric, reason, count):
    if count:
        bucket = target[metric]
        bucket[reason] = bucket.get(reason, 0) + int(count)


def _process_table(table, *, calendar, np, groups, exclusions, completeness,
                   dates_by_variant, dates_by_sha, calendar_counts, collection=None, year=None):
    meta = _classify_rows(table, calendar, np)
    if year is not None:
        indexes = [i for i, value in enumerate(meta['years']) if value == year]
        if not indexes:
            return
        if len(indexes) != len(table):
            table = table.take(_require_pyarrow().array(indexes, type=_require_pyarrow().int64()))
            meta = {name: [values[i] for i in indexes] for name, values in meta.items()}
    if collection is not None:
        meta['keys'] = [(collection, *key[1:]) for key in meta['keys']]
    columns, flags = _table_metric_columns(table, np)
    n = len(table)
    completeness['observations'] += n
    for name, mask in flags.items():
        completeness[name] += int(np.count_nonzero(mask))
    completeness['economic_dates'].update(meta['dates'])
    for day, variant, sha, state in zip(meta['dates'], meta['variants'], meta['raw_sha'], meta['calendar_states']):
        dates_by_variant[variant].add(day)
        dates_by_sha[sha].add(day)
        calendar_counts[state] += 1
    index_groups = defaultdict(list)
    for index, key in enumerate(meta['keys']):
        index_groups[(key, meta['dates'][index])].append(index)
    for (key, day), indexes in index_groups.items():
        ix = np.asarray(indexes, dtype=np.int64)
        store = groups[key]
        exclusions[key]['__intended_dates__'][day] = 1
        for metric, values, valid, reason in columns:
            selected = valid[ix]
            taken = values[ix][selected]
            metric_store = store[metric]
            metric_store.extend(taken, day)
            missing = int(selected.size - taken.size)
            if missing and reason != 'not_used':
                _add_exclusions(exclusions[key], metric, reason, missing)


def _finalize_groups(groups, exclusions, estimands):
    settings = {
        'seed': estimands['seed'],
        'block_length': estimands['block_length'],
        'replicates': estimands['bootstrap_replicates'],
        'confidence': float(estimands['confidence']),
        'minimum_independent_dates': estimands['minimum_independent_dates'],
        'minimum_events': estimands['minimum_events'],
    }
    finalized = []
    date_rows = []
    np = _require_numpy()
    for key in sorted(groups):
        variant, root, year, stage, session = key
        intended_dates = sorted(exclusions[key]['__intended_dates__'])
        metrics_out = {}
        date_sums = {}
        date_counts = {}
        for metric, store in sorted(groups[key].items()):
            values = store.array()
            moments = _moments(store, values)
            metrics_out[metric] = {
                'unit': metric_unit(metric),
                'observation_moments': moments,
                'sample_quantiles': _exact_quantiles(np, values, QUANTILE_LEVELS),
                'eligible_observations': moments['count'],
                'eligible_independent_dates': len(store.date_count),
                'excluded_reason_counts': dict(exclusions[key].get(metric, {})),
            }
            if metric.endswith('information_loss_positive'):
                positives = int(np.count_nonzero(values))
                metrics_out[metric].update(positive_observations=positives,
                    negative_observations=len(values)-positives,
                    sparse_minority_event_support=min(positives, len(values)-positives)<estimands['minimum_events'])
            date_sums[metric] = dict(store.date_sum)
            date_counts[metric] = dict(store.date_count)
            for day in intended_dates:
                count = store.date_count.get(day, 0)
                date_rows.append({
                    'source_collection': variant, 'root': root, 'year': int(year),
                    'stage': stage, 'session': session, 'economic_date': day,
                    'metric': metric, 'observation_count': int(count),
                    'sum': None if count == 0 else float(store.date_sum[day]),
                    'mean': None if count == 0 else float(store.date_sum[day] / count),
                })
        intervals = None
        if date_sums:
            intervals = shared_moving_block_intervals(date_sums, date_counts,
                                                     intended_dates=intended_dates, **settings)
            for metric, payload in intervals['metrics'].items():
                metrics_out[metric]['date_mean'] = payload['date_mean']
                metrics_out[metric]['event_mean'] = payload['event_mean']
        finalized.append({
            'source_collection': variant, 'root': root, 'year': int(year),
            'stage': stage, 'session': session,
            'metrics': metrics_out,
            'intended_dates': None if intervals is None else intervals['intended_dates'],
            'intended_date_count': 0 if intervals is None else intervals['intended_date_count'],
        })
    return finalized, date_rows


def _compare_overlapping_units(unit_lists):
    declared = (
        'all__close', 'all__high', 'all__low', 'all__open', 'all__buy', 'all__sell', 'all__unknown',
        'all__volume', 'all__prints',
    )
    needed = (*JOIN_FIELDS, 'contract_key', 'coordinate_complete', 'source_variant', *declared)
    totals = Counter()
    disagreements = Counter()
    magnitudes = defaultdict(list)
    unmatched_coverage = 0
    mismatched_contract = 0
    incompatible = 0
    for units in unit_lists:
        if len(units) < 2:
            continue
        by_join = defaultdict(list)
        for unit in units:
            variant = unit.get('source_variant') or source_variant(unit['source_path'])
            for table in iter_observation_tables(unit['series']):
                present = set(table.schema.names)
                cols = {name: table.column(name).to_pylist() for name in needed if name in present}
                fields = tuple(cols)
                for index in range(len(table)):
                    row = {name: cols[name][index] for name in fields}
                    row['source_variant'] = variant
                    key = tuple(row[name] for name in JOIN_FIELDS)
                    by_join[key].append(row)
        for rows in by_join.values():
            variants = {}
            for row in rows:
                variants.setdefault(row['source_variant'], []).append(row)
            names = sorted(variants)
            if len(names) < 2:
                unmatched_coverage += 1
                continue
            for i, left_name in enumerate(names):
                for right_name in names[i + 1:]:
                    result = join_observations(variants[left_name], variants[right_name],
                                               value_fields=declared)
                    totals['matched_equal'] += result['matched_equal']
                    totals['matched_different'] += result['matched_different']
                    totals['unmatched_left'] += result['unmatched_left']
                    totals['unmatched_right'] += result['unmatched_right']
                    incompatible += result['incompatible_coordinates']
                    mismatched_contract += result['mismatched_contract']
                    disagreements.update(result['metric_disagreements'])
                    for field, payload in result['magnitude_summaries'].items():
                        if payload['count']:
                            magnitudes[field].append(payload)
    magnitude_out = {}
    for field, items in magnitudes.items():
        count = sum(item['count'] for item in items)
        if not count:
            continue
        mean = math.fsum(item['mean_abs_difference'] * item['count'] for item in items) / count
        magnitude_out[field] = {
            'count': count,
            'mean_abs_difference': mean,
            'maximum_abs_difference': max(item['maximum_abs_difference'] for item in items),
        }
    return {
        'matched_equal': int(totals['matched_equal']),
        'matched_different': int(totals['matched_different']),
        'unmatched_left': int(totals['unmatched_left']),
        'unmatched_right': int(totals['unmatched_right']),
        'unmatched_coverage_keys': unmatched_coverage,
        'incompatible_coordinates': incompatible,
        'mismatched_contract': mismatched_contract,
        'metric_disagreements': dict(disagreements),
        'magnitude_summaries': magnitude_out,
        'no_source_winner_selected': True,
    }


def _true_ohlc_effect(finalized):
    rows = []
    for group in finalized:
        for cohort in (*SOURCE_FILTERS, 'ofi'):
            prefix = 'ofi' if cohort == 'ofi' else 'complete_' + cohort
            loss = group['metrics'].get(prefix + '_information_loss')
            close = group['metrics'].get(prefix + '_close_excursion')
            if loss is None or close is None:
                continue
            def summary(metric):
                mean = metric.get('date_mean')
                return {'observation_mean': metric['observation_moments']['mean'],
                        'date_mean': None if mean is None else mean['estimate'],
                        'date_mean_interval': None if mean is None else mean['bootstrap'],
                        'support': None if mean is None else mean['support'],
                        'eligible_observations': metric['eligible_observations'],
                        'eligible_independent_dates': metric['eligible_independent_dates']}
            rows.append({'source_collection': group['source_collection'], 'root': group['root'],
                         'year': group['year'], 'stage': group['stage'], 'session': group['session'],
                         'cohort': cohort, 'information_loss': summary(loss), 'close_excursion': summary(close),
                         'paired_shared_weights': 'date_mean' in loss and 'date_mean' in close})
    return {'kind': 'matched_true_ohlc_vs_close_information_loss_v1',
            'scope': 'Complete covered ordered excursion minus abs(close-open), each hard cohort and OFI separately.',
            'groups': rows}


def _alias_payload(inventory, dates_by_sha, dates_by_variant):
    if not isinstance(inventory, list):
        return {'alias_groups': [], 'source_window_count': 0}
    rows = []
    for item in inventory:
        raw = item.get('canonical_raw_values')
        unit = item.get('unit') or {}
        if not isinstance(raw, dict) or type(raw.get('sha256')) is not str:
            raise IntegrityError('population inventory lost canonical_raw_values.sha256')
        variant = unit.get('source_variant')
        if not variant:
            path = unit.get('source_path')
            if type(path) is not str:
                raise IntegrityError('inventory unit lost source_variant and source_path')
            variant = source_variant(path)
        rows.append({
            'canonical_raw_values_sha256': raw['sha256'],
            'source_variant': variant,
            'economic_date': None,
            'root': unit.get('root'),
            'event_start_ns': unit.get('event_start_ns'),
            'event_end_ns': unit.get('event_end_ns'),
            'source_path': unit.get('source_path'),
        })
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row['root'], row['event_start_ns'], row['event_end_ns'], row['canonical_raw_values_sha256'])].append(row)
    groups = []
    for (root, start, end, sha), members in sorted(grouped.items()):
        variants = sorted({row['source_variant'] for row in members})
        windows = {(row['root'], row['event_start_ns'], row['event_end_ns'], row['source_variant'])
                   for row in members}
        window_dates = {economic_date(start), economic_date(end - 1)}
        observed = sorted(set(dates_by_sha.get(sha, ())) & window_dates)
        groups.append({
            'canonical_raw_values_sha256': sha,
            'root': root, 'event_start_ns': start, 'event_end_ns': end,
            'alias_source_variants': variants,
            'alias_source_variant_count': len(variants),
            'source_window_count': len(windows),
            'independent_economic_dates': observed,
            'independent_economic_date_count': len(observed),
            'variant_date_counts': {name: len(dates_by_variant.get(name, ())) for name in variants},
            'aliases_are_not_extra_independent_support': True,
        })
    return {
        'kind': 'auction_flow_source_alias_report_v1',
        'alias_groups': groups,
        'source_window_count': len(rows),
        'no_source_winner_selected': True,
    }


def _write_json_or_split(outputs, name, payload, *, kind, by_source=None):
    from trading_research.operations.artifacts import canonical_json
    blob = canonical_json(payload) + b'\n'
    if len(blob) <= MAXIMUM_JSON_BYTES:
        return [outputs.json(name, payload, kind=kind)]
    if not by_source:
        raise ContractError('core statistics JSON exceeds 512MiB and has no source split')
    refs = []
    for index, (variant, part) in enumerate(sorted(by_source.items())):
        safe = ''.join(ch if ch.isalnum() or ch in '-_' else '_' for ch in variant)
        refs.append(outputs.json(f'{name[:-5] if name.endswith(".json") else name}-{safe}.json',
                                 part, kind=kind))
        _ = index
    return refs


def _markdown_report(*, finalized, completeness, aliases, matched, effect, population,
                     no_instrument, processed, cpu, output_bytes, calendar_ref, calendar_counts):
    lines = [
        '# Auction/flow core measurement statistics',
        '',
        'Descriptive complete-population core measurements only. '
        'This does not complete the auction/flow family, adaptive cohorts, '
        'anchor geometry, causal structure, or Context/Location.',
        '',
        f'- complete_family_statistics: false',
        f'- population_source_windows: {population.get("population_source_windows")}',
        f'- processed_source_windows: {processed}',
        f'- processed_observations: {completeness["observations"]}',
        f'- independent_economic_dates: {len(completeness["economic_dates"])}',
        f'- no_instrument_source_windows: {no_instrument}',
        f'- cpu_seconds: {cpu}',
        f'- output_bytes: {output_bytes}',
        f'- cash_calendar: {calendar_ref}',
        '',
        '## Completeness',
        '',
        f'- archive_window_complete observations: {completeness["archive_window_complete"]}',
        f'- source_coverage_complete observations: {completeness["source_coverage_complete"]}',
        f'- flow_history_complete observations: {completeness["flow_history_complete"]}',
        f'- price_history_complete observations: {completeness["price_history_complete"]}',
        f'- quote_coverage_complete observations: {completeness["quote_coverage_complete"]}',
        f'- coordinate_complete observations: {completeness["coordinate_complete"]}',
        f'- calendar_state_counts: {dict(calendar_counts)}',
        '',
        'True zero complete flow is retained. Missing or partial coverage is excluded, not replaced with zero.',
        '',
        '## True OHLC versus close-only',
        '',
    ]
    if not effect['groups']:
        lines.append('No complete-flow information-loss groups were eligible in this run.')
    else:
        lines.append('| source collection | root | year | stage | session | cohort | loss date-mean | close date-mean | dates | obs |')
        lines.append('|---|---|---|---|---|---|---|---|---|---|')
        for row in effect['groups']:
            loss = row['information_loss']
            close = row['close_excursion']
            lines.append(
                f"| {row['source_collection']} | {row['root']} | {row['year']} | {row['stage']} | "
                f"{row['session']} | {row['cohort']} | {loss['date_mean']} | {close['date_mean']} | "
                f"{loss['eligible_independent_dates']} | {loss['eligible_observations']} |"
            )
    lines.extend([
        '',
        '## Source aliases and disagreement',
        '',
        f"- alias groups: {len(aliases.get('alias_groups', []))}",
        f"- matched equal measurements: {matched.get('matched_equal')}",
        f"- matched different measurements: {matched.get('matched_different')}",
        f"- mismatched contracts not joined: {matched.get('mismatched_contract')}",
        f"- incompatible coordinates: {matched.get('incompatible_coordinates')}",
        '- no source winner is selected from these descriptive counts.',
        '',
        '## Groups',
        '',
        f'- root/source/year/stage/session groups: {len(finalized)}',
        '',
        'Overlapping hard cohorts are occupancy fractions, not a partition. '
        'OFI analogs use only full pressure-eligible windows; the observed OFI subset is separate. '
        'Futures 18:00-17:00 is an observed wall clock, not a certified venue calendar.',
        '',
    ])
    return '\n'.join(lines) + '\n'


def _empty_completeness():
    return {**{name: 0 for name in ('observations', 'archive_window_complete',
        'source_coverage_complete', 'flow_history_complete', 'price_history_complete',
        'quote_coverage_complete', 'coordinate_complete')}, 'economic_dates': set()}


def _date_denominator_table(rows, pa):
    fields = [('source_collection', pa.string()), ('root', pa.string()), ('year', pa.int64()),
              ('stage', pa.string()), ('session', pa.string()), ('economic_date', pa.string()),
              ('metric', pa.string()), ('observation_count', pa.int64()), ('sum', pa.float64()),
              ('mean', pa.float64())]
    return pa.table({name: pa.array([row[name] for row in rows], type=kind) for name, kind in fields})


def _merge_evidence(total, part, dates_by_variant, dates_by_sha, calendar_counts):
    for name in total:
        if name == 'economic_dates':
            total[name].update(part['completeness'][name])
        else:
            total[name] += part['completeness'][name]
    for name, days in part['dates_by_variant'].items():
        dates_by_variant[name].update(days)
    for name, days in part['dates_by_sha'].items():
        dates_by_sha[name].update(days)
    calendar_counts.update(part['calendar_counts'])


def run_core_statistics(*, population, contract, outputs, load_reference):
    """Reduce one collection/root/economic-year at a time, retaining exact samples."""
    from trading_research.operations.artifacts import digest
    if not isinstance(outputs, BoundedOutputs) or not callable(load_reference):
        raise ContractError('bounded outputs and authenticated reference loader required')
    if not isinstance(population, dict) or population.get('kind') != POPULATION_KIND:
        raise IntegrityError('authenticated observation population required')
    phase = contract.get('phase', 'full')
    if phase not in ('pilot', 'full'):
        raise IntegrityError('unregistered core-statistics phase')
    if population.get('all_population_materialized') is not True:
        raise IntegrityError('all_population_materialized=true required for the input catalog; pilot selection stays explicit')
    estimands, _policy = _require_contract(contract)
    calendar = _load_calendar(contract, load_reference)
    started, wall_started = time_mod.process_time(), time_mod.monotonic()
    np, pa = _require_numpy(), _require_pyarrow()
    all_units = population.get('units')
    if not isinstance(all_units, list):
        raise IntegrityError('observation population lost its unit summaries')
    collections = contract.get('source_collections', {})
    selected_paths = contract.get('pilot_source_paths') if phase == 'pilot' else None
    if phase == 'pilot' and (not isinstance(selected_paths, list) or not selected_paths):
        raise IntegrityError('pilot needs explicit physical source-path selection')
    units = [u for u in all_units if selected_paths is None or u['source_path'] in selected_paths]
    if selected_paths is not None and set(selected_paths) != {u['source_path'] for u in units}:
        raise IntegrityError('pilot source paths do not join the materialized population')
    if collections and any(u['source_path'] not in collections for u in all_units):
        raise IntegrityError('frozen source collection map is incomplete')
    partitions, overlap = defaultdict(list), defaultdict(list)
    no_instrument = 0
    intended_rows = 0
    for unit in units:
        rows = unit.get('atomic_rows', unit.get('observation_rows'))
        if type(rows) is not int or rows < 0:
            raise IntegrityError('observation unit row count invalid')
        intended_rows += rows
        if rows == 0:
            no_instrument += 1
            continue
        if unit.get('series', {}).get('roundtrip_exact') is not True:
            raise IntegrityError('complete verified observation series required')
        root, path = unit['root'], unit['source_path']
        start, end = unit['source_window_start_ns'], unit['source_window_end_ns']
        overlap[(root, start, end)].append(unit)
        collection = collections.get(path, unit.get('source_variant') or source_variant(path))
        years = {int(economic_date(start)[:4]), int(economic_date(end - 1)[:4])}
        for year in sorted(years):
            partitions[(collection, root, year)].append(unit)
    total = _empty_completeness()
    dates_by_variant, dates_by_sha = defaultdict(set), defaultdict(set)
    calendar_counts = Counter()
    partition_refs, group_refs, denominator_refs, effects = [], [], [], []
    reused, recomputed, measurements = 0, 0, []
    accepted = {}
    for ref in contract.get('accepted_partitions', []):
        row = load_reference(ref, maximum=128 * 1024**2)
        accepted[row['identity']] = (ref, row)
    definition = {name: value for name, value in contract.items()
                  if name not in ('phase', 'pilot_source_paths', 'accepted_partitions',
                                  'accepted_pilot_execution', 'accepted_pilot_worker', 'accepted_consumer_files')}
    for ordinal, (key, members) in enumerate(sorted(partitions.items())):
        collection, root, year = key
        members = sorted(members, key=lambda u: (u['source_window_start_ns'], u['source_path']))
        source_refs = [u.get('receipt', {'source_path': u['source_path'],
            'start': u['source_window_start_ns'], 'rows': u['atomic_rows']}) for u in members]
        identity = digest({'definition': definition, 'collection': collection, 'root': root,
                           'economic_year': year, 'source_refs': source_refs})
        if identity in accepted:
            ref, part = accepted[identity]
            if part.get('passed') is not True:
                raise IntegrityError('retained core partition was not successful')
            reused += 1
        else:
            began, wall_began, before = time_mod.process_time(), time_mod.monotonic(), outputs.written
            groups = defaultdict(lambda: defaultdict(lambda: _MetricStore(np)))
            exclusions = defaultdict(lambda: defaultdict(dict))
            complete = _empty_completeness()
            variant_dates, raw_dates, calendar_local = defaultdict(set), defaultdict(set), Counter()
            # Same-collection overlapping physical windows would duplicate observations.
            seen_windows = set()
            for unit in members:
                unit_key = (unit['source_window_start_ns'], unit['source_window_end_ns'])
                if unit_key in seen_windows:
                    raise IntegrityError('source collection contains overlapping duplicate physical windows')
                seen_windows.add(unit_key)
                for table in iter_observation_tables(unit['series']):
                    _process_table(table, calendar=calendar, np=np, groups=groups, exclusions=exclusions,
                        completeness=complete, dates_by_variant=variant_dates, dates_by_sha=raw_dates,
                        calendar_counts=calendar_local, collection=collection, year=year)
            finalized, date_rows = _finalize_groups(groups, exclusions, estimands)
            del groups, exclusions
            name = f'core-{ordinal:03d}-{root}-{year}'
            denominators = ParquetSeries(outputs, name + '-date-metrics', encoding='plain')
            for at in range(0, len(date_rows), BATCH_HINT):
                denominators.append(_date_denominator_table(date_rows[at:at+BATCH_HINT], pa))
            if not date_rows:
                denominators.append(_date_denominator_table([], pa))
            denominator = denominators.finish()
            del date_rows
            group = outputs.json(name + '-groups.json', {'kind': 'auction_flow_core_group_statistics_v1',
                'groups': finalized, 'source_refs': source_refs, 'source_collection': collection,
                'root': root, 'economic_year': year}, kind='auction_flow_core_group_statistics_v1')
            effect = _true_ohlc_effect(finalized)
            group_count = len(finalized)
            del finalized
            complete['economic_dates'] = sorted(complete['economic_dates'])
            measurement = {'cpu_seconds': time_mod.process_time()-began,
                'wall_seconds': time_mod.monotonic()-wall_began,
                'observations': complete['observations'], 'output_bytes': outputs.written-before}
            part = {'kind': 'auction_flow_core_partition_v1', 'passed': True, 'identity': identity,
                'source_collection': collection, 'root': root, 'economic_year': year,
                'source_refs': source_refs, 'groups': group, 'denominators': denominator,
                'effect': effect, 'group_count': group_count, 'measurement': measurement,
                'completeness': complete, 'dates_by_variant': {k: sorted(v) for k,v in variant_dates.items()},
                'dates_by_sha': {k: sorted(v) for k,v in raw_dates.items()}, 'calendar_counts': dict(calendar_local)}
            ref = outputs.json(name + '-partition.json', part, kind='auction_flow_core_partition_v1')
            recomputed += 1
            measurements.append(measurement)
        partition_refs.append(ref)
        group_refs.append(part['groups'])
        denominator_refs.append(part['denominators'])
        effects.extend(part['effect']['groups'])
        _merge_evidence(total, part, dates_by_variant, dates_by_sha, calendar_counts)
        print(f'core statistics {ordinal+1}/{len(partitions)} {key} observations={part["completeness"]["observations"]}', flush=True)
    if total['observations'] != intended_rows:
        raise IntegrityError('core reducer lost or repeated an intended atomic observation')
    aliases = _alias_payload(population.get('inventory') or [], dates_by_sha, dates_by_variant)
    matched = _compare_overlapping_units([items for items in overlap.values() if len(items) > 1])
    effect = {'kind': 'matched_true_ohlc_vs_close_information_loss_v1', 'groups': effects}
    alias_ref = outputs.json('core-statistics-aliases.json', aliases, kind='auction_flow_source_alias_report')
    matched_ref = outputs.json('core-statistics-matched-true-ohlc.json',
        {'true_ohlc_vs_close': effect, 'source_disagreement': matched}, kind='auction_flow_core_matched_true_ohlc')
    completeness_out = {**total, 'economic_dates': sorted(total['economic_dates']),
        'independent_economic_dates': len(total['economic_dates']), 'calendar_state_counts': dict(calendar_counts),
        'no_instrument_source_windows': no_instrument, 'physical_observation_count_includes_separate_acquisitions': True,
        'date_inference_is_separate_by_source_collection': True}
    completeness_ref = outputs.json('core-statistics-completeness.json', completeness_out,
                                   kind='auction_flow_core_completeness')
    cpu = time_mod.process_time()-started
    report_text = _markdown_report(finalized=group_refs, completeness=total, aliases=aliases,
        matched=matched, effect=effect, population=population, no_instrument=no_instrument,
        processed=len(units), cpu=cpu, output_bytes=outputs.written,
        calendar_ref=calendar.reference, calendar_counts=calendar_counts)
    report_text = report_text.replace('Descriptive complete-population core measurements only.',
        f'Descriptive {phase} core measurements. Source collections pool only nonoverlapping physical windows; acquisition alternatives stay separate.')
    with outputs.create('core-measurement-statistics-report.md') as stream:
        stream.write(report_text.encode())
    report_ref = outputs.reference('core-measurement-statistics-report.md', kind='auction_flow_core_statistics_report')
    summary = {'kind': KIND, 'version': VERSION, 'phase': phase, 'passed': True,
        'complete_family_statistics': False, 'all_family_validation_complete': False,
        'all_core_population_reduced': phase == 'full' and len(units) == len(all_units),
        'population_source_windows': population['population_source_windows'],
        'population_source_files': population['population_source_files'],
        'processed_source_windows': len(units), 'processed_observations': total['observations'],
        'independent_economic_dates': len(total['economic_dates']), 'no_instrument_source_windows': no_instrument,
        'cpu_seconds': time_mod.process_time()-started, 'wall_seconds': time_mod.monotonic()-wall_started,
        'output_bytes': outputs.written, 'reused_partitions': reused, 'new_partitions': recomputed,
        'partition_measurements': measurements,
        'refs': {'partitions': partition_refs, 'denominators': denominator_refs, 'groups': group_refs,
                 'aliases': alias_ref, 'matched_true_ohlc': matched_ref, 'completeness': completeness_ref,
                 'report': report_ref, 'source_catalog': population.get('source_catalog'),
                 'cash_calendar': calendar.reference}}
    summary_ref = outputs.json('core-statistics-summary.json', summary, kind=KIND)
    summary['refs']['summary'] = summary_ref
    return summary


__all__ = [
    'ExplicitCashSessions',
    'FROZEN_CONTRACT_KIND',
    'FROZEN_STAGE_POLICY',
    'KIND',
    'REQUIRED_CASH_CALENDAR_REFERENCE',
    'VERSION',
    'alias_independent_dates',
    'classify_session',
    'economic_date',
    'information_loss_terms',
    'iter_observation_tables',
    'join_observations',
    'labeled_date_and_event_means',
    'observe_metric',
    'occupancy_fractions',
    'path_true_ohlc',
    'run_core_statistics',
    'shared_moving_block_intervals',
    'signed_close_open',
    'stage_name',
]
