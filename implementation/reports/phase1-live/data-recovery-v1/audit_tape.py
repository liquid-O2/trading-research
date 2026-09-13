"""Read-only four-window execution/clock reconciliation with physical receipts."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
EMP = OUT.parent / 'empirical'
MINUTE = 60_000_000_000
identities = {}


def identify(path):
    path = Path(path)
    key = str(path.relative_to(ROOT))
    if key not in identities:
        before = path.stat()
        h = sha256()
        with path.open('rb') as handle:
            for block in iter(lambda: handle.read(8 * 1024 * 1024), b''):
                h.update(block)
        after = path.stat()
        assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
        identities[key] = {'sha256': h.hexdigest(), 'bytes': after.st_size,
                           'mtime_ns': after.st_mtime_ns}
    return identities[key]


def native_rows(path, start, end, instrument_id, *, bars=False):
    identity = identify(path)
    file = pq.ParquetFile(path)
    columns = ['t', 'o', 'h', 'l', 'c', 'v', 'instrument_id'] if bars else ['t', 'price', 'size', 'side', 'instrument_id', 'flags']
    if 'action' in file.schema_arrow.names:
        columns.append('action')
    scale = 1_000_000 if bars else 1
    found, offset = [], 0
    for index in range(file.metadata.num_row_groups):
        group = file.metadata.row_group(index)
        stats = group.column(file.schema_arrow.names.index('t')).statistics
        if stats and (stats.max * scale < start or stats.min * scale >= end):
            offset += group.num_rows
            continue
        table = file.read_row_group(index, columns=columns)
        times = table['t'].to_numpy() * scale
        mask = (times >= start) & (times < end) & (table['instrument_id'].to_numpy() == int(instrument_id))
        if 'action' in columns:
            mask &= table['action'].to_numpy() == 'T'
        indices = np.flatnonzero(mask)
        selected = table.take(pa.array(indices)).to_pylist()
        for physical, row in zip(indices, selected):
            row['_row'] = offset + int(physical)
            row['t'] = int(row['t']) * scale
        found.extend(selected)
        offset += group.num_rows
    assert path.stat().st_size == identity['bytes'] and path.stat().st_mtime_ns == identity['mtime_ns']
    assert all(a['t'] <= b['t'] for a, b in zip(found, found[1:]))
    return found


def aggregates(frame, *, bars=False):
    result = {}
    for row in frame:
        at = row['t'] // MINUTE * MINUTE
        if bars:
            agg = result.setdefault(at, {'O': float(row['o']), 'H': float(row['h']),
                                         'L': float(row['l']), 'C': float(row['c']), 'V': 0, 'rows': 0})
            agg['H'] = max(agg['H'], float(row['h']))
            agg['L'] = min(agg['L'], float(row['l']))
            agg['C'] = float(row['c'])
            agg['V'] += int(row['v'])
        else:
            price = float(row['price'])
            agg = result.setdefault(at, {'opening_prices': set(), 'closing_prices': set(),
                                         'first_ns': row['t'], 'last_ns': row['t'],
                                         'H': price, 'L': price, 'V': 0, 'rows': 0})
            if row['t'] == agg['first_ns']:
                agg['opening_prices'].add(price)
            if row['t'] > agg['last_ns']:
                agg['closing_prices'] = set()
                agg['last_ns'] = row['t']
            agg['closing_prices'].add(price)
            agg['H'] = max(agg['H'], price)
            agg['L'] = min(agg['L'], price)
            agg['V'] += int(row['size'])
        agg['rows'] += 1
    if not bars:
        for agg in result.values():
            agg['opening_prices'] = sorted(agg['opening_prices'])
            agg['closing_prices'] = sorted(agg['closing_prices'])
    return result


def compare_minutes(trades, bars, start, end):
    mismatches = []
    for at in range(start, end, MINUTE):
        actual, expected = trades.get(at), bars.get(at)
        if actual is None or expected is None:
            mismatches.append({'minute_start': at, 'reason': 'missing_side', 'actual': actual, 'expected': expected})
            continue
        if 'opening_prices' in actual:
            match = expected['O'] in actual['opening_prices'] and expected['C'] in actual['closing_prices']
        else:
            match = actual['O'] == expected['O'] and actual['C'] == expected['C']
        match &= all(actual[k] == expected[k] for k in ['H', 'L', 'V'])
        if not match:
            mismatches.append({'minute_start': at, 'utc': datetime.fromtimestamp(at / 1e9, timezone.utc).isoformat(),
                               'actual': actual, 'expected': expected})
    return mismatches


def execution_keys(frame):
    return Counter((int(r['t']), float(r['price']), int(r['size']), str(r['side']), int(r['flags']))
                   for r in frame)


def key_digest(counter):
    h = sha256()
    for key, count in sorted(counter.items()):
        h.update(json.dumps([list(key), count], separators=(',', ':')).encode() + b'\n')
    return h.hexdigest()


def physical_ranges(frame):
    ranges = []
    for row in frame:
        at = row['_row']
        at = int(at)
        if ranges and ranges[-1][1] == at:
            ranges[-1][1] += 1
        else:
            ranges.append([at, at + 1])
    return {'row_count': len(frame), 'range_count': len(ranges),
            'row_ids_sha256': sha256(np.asarray([r['_row'] for r in frame], dtype='<i8').tobytes()).hexdigest(),
            'hash_encoding': 'ordered physical row indices as little-endian int64',
            'first_ranges': ranges[:8], 'last_ranges': ranges[-8:],
            'reproduction': 'Use exact hashed source file, instrument ID and half-open event-time window; retain all matching physical rows.'}


def main():
    probes = json.loads((OUT.parent / 'evidence-review-v1/RECOVERY_PROBES.json').read_text())
    results = []
    for checkpoint_path in sorted((EMP / 'checkpoints').glob('tape-*.json')):
        checkpoint = json.loads(checkpoint_path.read_text())
        if checkpoint['session_date'] not in ['2022-01-03', '2026-09-01']:
            continue
        identify(checkpoint_path)
        artifact_path = Path(checkpoint['artifact_path'])
        assert identify(artifact_path)['sha256'] == checkpoint['artifact_sha256']
        artifact = json.loads(artifact_path.read_text())
        for role in ['tape', 'prior_profile']:
            source = artifact[role]
            start, end, instrument_id = source['formation_start'], source['formation_end'], source['instrument_id']
            probe = next(r for r in probes['tape_alternatives'] if r['date'] == checkpoint['session_date'] and r['role'] == role)
            mbp_paths = [Path(r['path']) for r in probe['overlapping_mbp1_files'] if r['canonical_owner'] == 'owned']
            trade_paths = [ROOT / 'data' / r['path'] for r in source['source_files']]
            assert len(mbp_paths) == len(trade_paths) == 1
            print(f"Reading {checkpoint['session_date']} {role}", flush=True)
            # Keep a 1-second boundary halo to witness executions shifted across
            # the receive-clock opening or closing interval. Never move them.
            trades = native_rows(trade_paths[0], start - 1_000_000_000, end + 1_000_000_000, instrument_id)
            mbp = native_rows(mbp_paths[0], start - 1_000_000_000, end + 1_000_000_000, instrument_id)
            in_trades = [r for r in trades if start <= r['t'] < end]
            in_mbp = [r for r in mbp if start <= r['t'] < end]
            year = datetime.fromtimestamp(start / 1e9, timezone.utc).year
            bar_paths = [ROOT / f'data/quantpad/cme__nq-continuous-futures__ohlcv-{kind}/{year}.parquet' for kind in ['1m', '1s']]
            bars = [native_rows(path, start, end, instrument_id, bars=True) for path in bar_paths]
            minute_bars, second_bars = [aggregates(frame, bars=True) for frame in bars]
            ta, ma = aggregates(in_trades), aggregates(in_mbp)
            tk, mk = execution_keys(in_trades), execution_keys(in_mbp)
            tape_mismatches = compare_minutes(ta, minute_bars, start, end)
            mbp_mismatches = compare_minutes(ma, minute_bars, start, end)
            second_mismatches = compare_minutes(second_bars, minute_bars, start, end)
            boundaries = sorted({at for mismatch in tape_mismatches for at in [mismatch['minute_start'], mismatch['minute_start'] + MINUTE]})
            boundary_rows = []
            for at in boundaries:
                # Fixed 25ms diagnostic window, not a fitted timestamp offset.
                sample = [r for r in trades if at - 25_000_000 <= r['t'] < at + 25_000_000]
                boundary_rows.append({'boundary_ns': at, 'utc': datetime.fromtimestamp(at / 1e9, timezone.utc).isoformat(),
                                      'trades': [{'event_ns': int(r['t']), 'offset_ns': int(r['t']) - at,
                                                  'price': float(r['price']), 'size': int(r['size']),
                                                  'side': str(r['side']), 'flags': int(r['flags']),
                                                  'physical_row': int(r['_row'])}
                                                 for r in sample]})
            row = {'date': checkpoint['session_date'], 'role': role, 'instrument_id': instrument_id,
                   'start_ns': start, 'end_ns': end, 'minutes': (end-start)//MINUTE,
                   'standalone_rows': len(in_trades), 'mbp_execution_rows': len(in_mbp),
                   'same_execution_multiset': tk == mk,
                   'standalone_only_execution_count': sum((tk-mk).values()),
                   'mbp_only_execution_count': sum((mk-tk).values()),
                   'standalone_multiset_sha256': key_digest(tk), 'mbp_multiset_sha256': key_digest(mk),
                   'standalone_vs_1m_mismatches': tape_mismatches,
                   'mbp_vs_1m_mismatches': mbp_mismatches,
                   'aggregated_1s_vs_1m_mismatches': second_mismatches,
                   'boundary_halo_executions': boundary_rows,
                   'source_paths': {'trades': str(trade_paths[0].relative_to(ROOT)),
                                    'mbp': str(mbp_paths[0].relative_to(ROOT)),
                                    'bars': [str(p.relative_to(ROOT)) for p in bar_paths]},
                   'physical_membership': {'trades': physical_ranges(in_trades), 'mbp': physical_ranges(in_mbp)},
                   'timestamp_fields': {'trades': list(pq.ParquetFile(trade_paths[0]).schema_arrow.names),
                                        'mbp': list(pq.ParquetFile(mbp_paths[0]).schema_arrow.names)},
                   'repair_admitted': False}
            results.append(row)
            print(json.dumps({k: row[k] for k in ['date','role','standalone_rows','mbp_execution_rows','same_execution_multiset']} |
                             {'mismatch_minutes': len(tape_mismatches), 'mbp_mismatch_minutes': len(mbp_mismatches),
                              'second_bar_mismatch_minutes': len(second_mismatches)}), flush=True)
    result = {'schema': 'phase1-four-window-tape-recovery-audit-v1', 'windows': results,
              'source_files': identities,
              'clock_semantics': {'local_t': 'event timestamp per data/manifests/timestamp-conventions.json',
                                  'vendor_ohlcv': 'receive-time buckets per official Databento schema',
                                  'source_url': 'https://databento.com/docs/schemas-and-data-formats/ohlcv'},
              'admission': 'No event moved, no daily-volume cancellation, no certificate or replay change. Missing receive timestamps cannot be inferred from a matching bar.'}
    (OUT / 'TAPE_RECONCILIATION.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
