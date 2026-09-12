"""Select immutable native windows and independently reconcile tape coverage.

A tape's extrema/row count do not establish completeness. For supported QuantPad
trade windows, every complete native minute must reconcile executed volume,
price range and feasible opening/closing prices with independent OHLCV records.
No absent minute is silently converted into an empty interval.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, replace
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from . import adapters
from .clocks import minute_starts, aligned_bar_bounds
from .native_resolution import NativeEvidenceError, NativeResolver, ResolvedMembers, ns, _selected_source_rows, _stat_signature

MINUTE = 60_000_000_000


@dataclass(frozen=True)
class NativeWindow:
    dataset_id: str
    instrument_id: int | str | None
    start_ns: int
    end_ns: int
    rows: tuple[Mapping, ...]
    locators: tuple[Mapping, ...]
    coverage_ok: bool | None
    missing_intervals: tuple[tuple[int, int], ...]
    mismatches: tuple[Mapping, ...]
    coverage_evidence: Mapping
    resolver: NativeResolver
    resolved: ResolvedMembers | None

    @property
    def raw_member_locators(self):
        return [dict(locator) for locator in self.locators]

    @property
    def instrument_definition(self):
        return None if self.resolved is None else self.resolved.instrument_definition


def _group_ranges(path, dataset, start, end):
    """Locate candidate physical row groups using exact native timestamp units."""
    if path.suffix != '.parquet':
        # Small JSON/CSV fixtures: scan once to obtain the finite physical bound.
        count = sum(1 for _ in adapters.iter_source_rows(path, dataset_id=dataset))
        return [] if not count else [(0, count)]
    import pyarrow.parquet as pq
    parquet = pq.ParquetFile(path)
    names = parquet.schema_arrow.names
    key = 't' if 't' in names else 'ts_event' if 'ts_event' in names else None
    if key is None:
        return []
    column = names.index(key)
    unit = adapters.native_timestamp_unit(dataset, key)
    if unit is None:
        raise NativeEvidenceError('unknown native timestamp unit')
    result, offset = [], 0
    for i in range(parquet.num_row_groups):
        group = parquet.metadata.row_group(i)
        count = group.num_rows
        stat = group.column(column).statistics
        include = True
        if stat is not None and stat.has_min_max:
            low = adapters.timestamp_ns(stat.min, unit)
            high = adapters.timestamp_ns(stat.max, unit)
            include = low < end and high >= start
        if include:
            result.append((offset, offset + count))
        offset += count
    return result


def _normalizer(dataset):
    if 'ohlcv-' in dataset:
        return adapters.normalize_ohlcv_row
    if 'mbp-1' in dataset:
        return adapters.normalize_mbp1_row
    if 'trades' in dataset:
        return adapters.normalize_trade_row
    raise NativeEvidenceError('window collector supports native QuantPad trades/MBP-1/OHLCV only')


def _collect(resolver, dataset, start, end, instrument_id):
    directory = (resolver.root / dataset).resolve()
    if not directory.is_relative_to(resolver.root):
        raise NativeEvidenceError('dataset escapes data root')
    if not directory.is_dir():
        return [], [], []
    normalize = _normalizer(dataset)
    rows, locators, conflicts = [], [], []
    for path in sorted(directory.iterdir()):
        if path.suffix not in {'.parquet', '.json', '.jsonl', '.csv', '.tsv'}:
            continue
        ranges = _group_ranges(path, dataset, start, end)
        if not ranges:
            continue
        # Hash only files whose row groups could contain the requested window.
        signature, digest = resolver._digest(path)
        indices = []
        for index, raw in _selected_source_rows(path, dataset, ranges):
            row = normalize(raw, dataset_id=dataset, source_file=str(path), source_row=index)
            at = row.get('start', row.get('event_ns'))
            until = row.get('end', at + 1)
            if at < start or until > end:
                continue
            if instrument_id is not None and str(row['instrument_id']) != str(instrument_id):
                continue
            if not resolver._owned(path, dataset, at, until):
                conflicts.append({'source_file': str(path), 'source_row': index, 'event_ns': at, 'reason': 'unowned_member'})
                continue
            row['dataset_id'] = dataset
            for key in ('price','O','H','L','C','V'):
                value = row.get(key)
                if value is not None and isinstance(value, Decimal) and not value.is_finite():
                    raise NativeEvidenceError('nonfinite native window measurement')
            rows.append(row)
            indices.append(index)
        if _stat_signature(path) != signature:
            raise NativeEvidenceError('native file changed while collecting window')
        # Consecutive physical rows compress into exact half-open locators.
        # Filtering by instrument never renumbers a row inside its source file.
        runs = []
        for index in indices:
            if runs and runs[-1][1] == index:
                runs[-1][1] += 1
            else:
                runs.append([index, index + 1])
        locators.extend({'source_file': str(path), 'dataset_id': dataset, 'sha256': digest,
                         'row_start': first, 'row_end': last} for first, last in runs)
    rows.sort(key=lambda row: row.get('start', row.get('event_ns')))
    return rows, locators, conflicts


def _minute_coverage(rows, start, end):
    expected = minute_starts(start, end)
    missing, mismatch, index = [], [], {}
    if start % MINUTE or end % MINUTE:
        mismatch.append({'reason': 'partial_minute_window_not_independently_verifiable'})
    for row in rows:
        at = row['start']
        if at in index:
            mismatch.append({'minute_start': at, 'reason': 'duplicate_native_minute'})
            continue
        index[at] = row
    for at in expected:
        row = index.get(at)
        if row is None:
            missing.append((at, at + MINUTE))
        elif row['end'] != at + MINUTE or row.get('complete') is not True:
            missing.append((at, at + MINUTE))
            mismatch.append({'minute_start': at, 'reason': 'incomplete_native_minute'})
        elif row['V'] < 0 or row['H'] < max(row['O'], row['L'], row['C']) or row['L'] > min(row['O'], row['H'], row['C']):
            mismatch.append({'minute_start': at, 'reason': 'invalid_native_ohlcv'})
    return index, missing, mismatch


def _reconcile(rows, minute_index, expected):
    by_minute = defaultdict(list)
    for row in rows:
        if row.get('action') == 'T':
            by_minute[(row['event_ns'] // MINUTE) * MINUTE].append(row)
    mismatches, reconciled = [], []
    for at in expected:
        bar = minute_index.get(at)
        if bar is None or bar.get('complete') is not True:
            continue
        trades = by_minute.get(at, [])
        if any(row.get('price') is None or row.get('size') is None or row['size'] < 0 for row in trades):
            mismatches.append({'minute_start': at, 'reason': 'missing_trade_price_or_size'})
            continue
        volume = sum((Decimal(row['size']) for row in trades), Decimal(0))
        check = {'minute_start': at, 'bar_id': bar['bar_id'], 'executed_volume': str(volume),
                 'ohlcv_volume': str(bar['V']), 'trade_count': len(trades)}
        reasons = []
        if volume != bar['V']:
            reasons.append('executed_volume_mismatch')
        if trades:
            high, low = max(t['price'] for t in trades), min(t['price'] for t in trades)
            if high != bar['H'] or low != bar['L']:
                reasons.append('trade_high_low_mismatch')
            first, last = trades[0]['event_ns'], trades[-1]['event_ns']
            opening = {t['price'] for t in trades if t['event_ns'] == first}
            closing = {t['price'] for t in trades if t['event_ns'] == last}
            if bar['O'] not in opening or bar['C'] not in closing:
                reasons.append('trade_open_close_mismatch')
            check['endpoint_order'] = 'unique_timestamp' if sum(t['event_ns'] == first for t in trades) == 1 and sum(t['event_ns'] == last for t in trades) == 1 else 'unknown_order'
        elif bar['V'] != 0:
            reasons.append('no_executed_trades_for_active_minute')
        else:
            # A source may publish a zero-volume minute with carried OHLC.
            # It corroborates zero executions, not a fabricated trade price.
            check['endpoint_order'] = 'no_executions'
        check['matched'] = not reasons
        reconciled.append(check)
        if reasons:
            mismatches.append({**check, 'reason': ','.join(reasons)})
    return mismatches, reconciled


def collect_window(data_root, dataset_id, start_ns, end_ns, instrument_id=None, required='trades'):
    """Return actual rows, immutable locators, coverage evidence and resolver.

    ``required='trades'`` independently reconciles all complete same-instrument
    OHLCV minutes. ``required='ohlcv'`` requires every exact one-minute member.
    Rolls/mixed native identities require an explicit instrument selection;
    neither a filename nor a source's displayed continuous symbol is a fill ID.
    """
    start, end = ns(start_ns, 'window start'), ns(end_ns, 'window end')
    if end <= start or required not in {'trades', 'ohlcv'}:
        raise NativeEvidenceError('positive window and supported required observation needed')
    if required == 'ohlcv' and not dataset_id.endswith('ohlcv-1m'):
        raise NativeEvidenceError('clock-complete minute coverage requires native ohlcv-1m')
    if required == 'trades' and not (dataset_id.endswith('trades') or dataset_id.endswith('mbp-1')):
        raise NativeEvidenceError('executed coverage requires native trades or MBP-1')
    resolver = NativeResolver(data_root)
    rows, locators, conflicts = _collect(resolver, dataset_id, start, end, instrument_id)
    identities = {str(row['instrument_id']) for row in rows}
    if instrument_id is None:
        if len(identities) > 1:
            raise NativeEvidenceError('window contains a native contract change; select an actual instrument')
        instrument_id = rows[0]['instrument_id'] if rows else None
    if required == 'ohlcv':
        minute_rows, minute_locators = rows, locators
    else:
        minute_dataset = dataset_id.rsplit('__', 1)[0] + '__ohlcv-1m'
        minute_rows, minute_locators, minute_conflicts = _collect(resolver, minute_dataset, start, end, instrument_id)
        conflicts += minute_conflicts
    minute_index, missing, mismatches = _minute_coverage(minute_rows, start, end)
    if required == 'trades':
        differences, reconciled = _reconcile(rows, minute_index, minute_starts(start, end))
        mismatches += differences
    else:
        reconciled = []
    # Unowned fallback rows may duplicate a valid monthly owner; canonical
    # ownership resolves those without treating the skipped duplicate as a gap.
    # Actual missing owned observations are witnessed by independent minute gaps
    # or reconciliation mismatches, not by a source file min/max.
    complete = bool(minute_index) and not missing and not mismatches
    coverage = True if complete else None
    volume_checks = [r for r in reconciled if 'executed_volume' in r and 'ohlcv_volume' in r]
    native_volume = sum((Decimal(r['executed_volume']) for r in volume_checks), Decimal(0))
    reference_volume = sum((Decimal(r['ohlcv_volume']) for r in volume_checks), Decimal(0))
    reconciliation_summary = {
        'checked_minute_count': len(volume_checks), 'mismatch_count': len(mismatches),
        'native_executed_volume': str(native_volume), 'reference_ohlcv_volume': str(reference_volume),
        'net_volume_difference': str(native_volume-reference_volume),
        'window_volume_matches': native_volume == reference_volume if volume_checks else None,
        'all_minute_allocations_match': not mismatches if volume_checks else None,
        'interpretation': 'Cross-source allocation discrepancies are observed mismatches; they do not by themselves establish missing tape or a verified bar clock.'}
    evidence = {'schema': 'phase1-native-window-coverage-v1', 'dataset_id': dataset_id,
                'instrument_id': instrument_id, 'start_ns': start, 'end_ns': end,
                'required': required, 'coverage_ok': coverage,
                'coverage_reason': 'verified' if coverage is True else 'missing_native_intervals' if missing else 'cross_source_reconciliation_mismatch' if mismatches else 'no_native_minute_reference',
                'reconciliation_summary': reconciliation_summary,
                'missing_intervals': [list(interval) for interval in missing], 'mismatches': mismatches,
                'member_locators': locators,
                'sources': [{'source_file': l['source_file'], 'sha256': l['sha256']} for l in locators],
                'corroborating_member_locators': minute_locators, 'minute_reconciliation': reconciled,
                'native_row_count': len(rows), 'native_minute_count': len(minute_index),
                'excluded_unowned_rows': len(conflicts),
                'method': 'exact_native_minutes' if required == 'ohlcv' else 'all_native_rows_plus_independent_minute_volume_ohlc_reconciliation'}
    resolver.coverage_records = (evidence,)
    frozen_rows = tuple(MappingProxyType(row) for row in rows)
    frozen_locators = tuple(MappingProxyType(l) for l in locators)
    resolved = None
    if locators and instrument_id is not None:
        # _collect has already verified immutable bytes, physical membership,
        # normalization and canonical ownership. Reuse those same immutable rows
        # instead of decoding a million-event session a second time.
        times = [row.get('known_at') for row in rows]
        known = max(times) if times and all(t is not None for t in times) else None
        definition = resolver._definition(instrument_id, [dataset_id], None)
        resolved = ResolvedMembers(frozen_rows, instrument_id, start, end, known, coverage,
                                   frozen_locators, tuple(missing), definition)
    return NativeWindow(dataset_id, instrument_id, start, end,
        frozen_rows, frozen_locators, coverage,
        tuple(missing), tuple(MappingProxyType(row) for row in mismatches), MappingProxyType(evidence), resolver, resolved)


class AuditedWindowResolver(NativeResolver):
    """Resolve a manifest and independently audit its complete selected window.

    Coverage is recomputed from the application's immutable inventory. A
    manifest subset cannot borrow the audit of a larger native window, and a
    caller's coverage Boolean or artifact locator is never the proof.
    """
    def __init__(self, data_root='/workspace/data'):
        super().__init__(data_root)
        self.window_audits = {}

    def resolve(self, locators, **kwargs):
        resolved = super().resolve(locators, **kwargs)
        datasets = {row['dataset_id'] for row in resolved.members}
        if len(datasets) != 1:
            return resolved
        dataset = next(iter(datasets))
        required = 'ohlcv' if dataset.endswith('ohlcv-1m') else 'trades' if dataset.endswith(('trades','mbp-1')) else None
        if required is None:
            return resolved
        # Include the content identities validated during this resolution.
        signatures = tuple(sorted((str(row['source_file']), row['sha256']) for row in locators))
        key = dataset, str(resolved.instrument_id), resolved.start_ns, resolved.end_ns, signatures
        cached = self.window_audits.get(key)
        if cached is not None and any(_stat_signature(path) != signature
                for path, (signature, digest) in cached.resolver._digests.items()):
            del self.window_audits[key]
        if key not in self.window_audits:
            window = collect_window(self.root, dataset, resolved.start_ns, resolved.end_ns,
                                    resolved.instrument_id, required=required)
            self.window_audits[key] = window
        window = self.window_audits[key]
        actual = {(row['source_file'], row['source_row']) for row in resolved.members}
        complete = {(row['source_file'], row['source_row']) for row in window.rows}
        coverage = window.coverage_ok if actual == complete and len(actual) == len(resolved.members) else None
        return replace(resolved, coverage_ok=coverage, missing_intervals=window.missing_intervals)

    def audit_records(self):
        return [dict(window.coverage_evidence) for window in self.window_audits.values()]
