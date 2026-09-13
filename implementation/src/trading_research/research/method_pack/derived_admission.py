"""Explicit admission of existing recovery bundles without clock mixing."""
from __future__ import annotations
from collections import defaultdict
from decimal import Decimal
import json
from pathlib import Path

from .empirical_protocol import content_hash
from .native_resolution import file_digest, NativeEvidenceError, _stat_signature
from .minute_recovery import _selected_rows

ROOT = Path('/workspace')
RECOVERY = ROOT / 'implementation/reports/phase1-live/derived-views/nq-minutes-37uhc_wa/manifest.json'
AUGUST = ROOT / 'implementation/reports/phase1-live/data-recovery-v1/RECOVERED_AUGUST_REFERENCE.json'
TAIL = ROOT / 'implementation/reports/phase1-live/derived-views/mbp1-9_5xkllu/manifest.json'
MINUTE = 60_000_000_000


def artifact(path, digest):
    path = Path(path).resolve()
    if not path.is_file() or file_digest(path) != digest:
        raise NativeEvidenceError('derived artifact identity changed: ' + str(path))
    return path


def merge_bars(native, recoveries, *, clock_basis):
    """Instrument/minute identity first, equality on overlap, never append twice."""
    index, receipts = {}, []
    for source, rows in [('native', native), *recoveries]:
        for row in rows:
            if row.get('clock_basis') != clock_basis:
                raise NativeEvidenceError('derived admission refuses mixed bar clocks')
            key = str(row['instrument_id']), row['start_ns']
            if row['end_ns'] != row['start_ns'] + MINUTE:
                raise NativeEvidenceError('recovery is not an aligned minute')
            previous = index.get(key)
            if previous is not None:
                if any(Decimal(str(previous[k])) != Decimal(str(row[k])) for k in 'OHLCV'):
                    raise NativeEvidenceError('contradictory instrument/minute recovery overlap')
                receipts.append({'instrument_id': key[0], 'start_ns': key[1], 'source': source, 'action': 'equal_overlap_not_added'})
                continue
            index[key] = dict(row, admitted_source=source)
    return list(index.values()), receipts


def admitted_recovery(*, recovery_manifest=RECOVERY, august_manifest=AUGUST, verify_transform=True):
    """Verify every selected recovered key against its actual native seconds."""
    manifest = json.loads(Path(recovery_manifest).read_text())
    source = artifact(manifest['artifact']['path'], manifest['artifact']['sha256'])
    rows = [json.loads(line) for line in source.read_text().splitlines()]
    if len(rows) != manifest['artifact']['rows']:
        raise NativeEvidenceError('recovery artifact row count differs')
    study_start = 1_577_836_800_000_000_000
    selected = [dict(r, clock_basis='vendor_receive_time') for r in rows if r['start_ns'] >= study_start]
    keys = {(int(r['t']), str(r['instrument_id'])) for r in selected}
    if len(keys) != len(selected):
        raise NativeEvidenceError('duplicate recovered minute key')
    sources = sorted({Path(s['path']) for r in selected for s in r['source_row_ranges']})
    identities = [{'path': str(p), 'sha256': file_digest(p), 'bytes': p.stat().st_size} for p in sources]
    signatures = {p: _stat_signature(p) for p in sources}
    membership = defaultdict(list)
    if verify_transform:
        accum = {}
        for path, physical, raw in _selected_rows(sources, {t for t, _ in keys}, values=True):
            key = int(raw['t']) // 60000 * 60000, str(raw['instrument_id'])
            if key not in keys:
                continue
            values = {k: Decimal(str(raw[k.lower()])) for k in 'OHLCV'}
            a = accum.setdefault(key, dict(values, first=int(raw['t']), last=int(raw['t']), V=Decimal(0), count=0))
            if int(raw['t']) < a['first']:
                a['first'], a['O'] = int(raw['t']), values['O']
            if int(raw['t']) >= a['last']:
                a['last'], a['C'] = int(raw['t']), values['C']
            a['H'], a['L'], a['V'] = max(a['H'], values['H']), min(a['L'], values['L']), a['V'] + values['V']
            a['count'] += 1
            membership[key].append([str(path), physical])
        for r in selected:
            key = r['t'], str(r['instrument_id'])
            a = accum.get(key)
            if a is None or any(a[k] != Decimal(str(r[k])) for k in 'OHLCV') or a['count'] != r['observed_second_count']:
                raise NativeEvidenceError('native-second transformation differs for ' + str(key))
            r['physical_membership_sha256'] = content_hash(membership[key])
    august = json.loads(Path(august_manifest).read_text())
    relative = august['recovered_input_path']
    path = artifact(ROOT / relative, august['source_files'][relative]['sha256'])
    import pyarrow.parquet as pq
    august_rows = []
    for r in pq.read_table(path).to_pylist():
        at = int(r['t']) * 1_000_000
        august_rows.append({**{k: r[k.lower()] for k in 'OHLCV'}, 'instrument_id': r['instrument_id'],
                           'start_ns': at, 'end_ns': at + MINUTE, 'clock_basis': 'vendor_receive_time'})
    merged, overlaps = merge_bars([], [('minute_recovery', selected), ('august_recovery', august_rows)], clock_basis='vendor_receive_time')
    for p, before in signatures.items():
        if _stat_signature(p) != before:
            raise NativeEvidenceError('native seconds changed during admission')
    receipt = {'schema': 'phase1-derived-admission-v2', 'clock_basis': 'vendor_receive_time',
               'source_manifests': [{'path': str(p), 'sha256': file_digest(Path(p))} for p in (recovery_manifest, august_manifest)],
               'source_files': identities, 'recovered_study_keys': len(selected), 'outside_study_keys': len(rows) - len(selected),
               'august_keys': len(august_rows), 'equal_overlaps_not_added': len(overlaps), 'admitted_keys': len(merged),
               'transformations_verified': verify_transform, 'membership_sha256': content_hash(merged),
               'raw_sources_unchanged': True, 'overlap_receipts': overlaps,
               'limit': 'vendor-clock recovery; no event-clock equivalence or exchange-feed continuity asserted'}
    return merged, receipt


def admitted_tail(manifest_path=TAIL):
    doc = json.loads(Path(manifest_path).read_text())
    member = doc['artifacts']['ohlcv-1m']
    path = artifact(member['path'], member['sha256'])
    rows = [dict(json.loads(line), clock_basis='event_ns') for line in path.read_text().splitlines()]
    if len(rows) != member['rows']:
        raise NativeEvidenceError('tail row count differs')
    return rows, {'schema': 'phase1-tail-admission-v2', 'manifest_sha256': file_digest(Path(manifest_path)),
                  'artifact_sha256': member['sha256'], 'rows': len(rows), 'clock_basis': 'event_ns',
                  'use': 'cross-check with fresh owned event reconstruction; never append to vendor-clock history'}
