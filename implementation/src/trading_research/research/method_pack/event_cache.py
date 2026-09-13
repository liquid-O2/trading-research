"""Immutable derived event inputs and reusable exact-date input preparation."""
from __future__ import annotations
from datetime import date, timedelta
from decimal import Decimal
from functools import lru_cache
import gzip
import errno
import json
import os
from pathlib import Path
import tempfile

from . import adapters
from .empirical_market import clock
from .empirical_protocol import content_hash
from .event_time import build_event_window, CONTRACT, EventWindow, identify_sources, VERSION
from .mbp1_views import plan_window
from .native_resolution import NativeEvidenceError, file_digest
from .protocol import jsonable

DEFAULT_CACHE = Path('/workspace/data/derived/phase1-event-time-v2')


def transform_identity():
    directory = Path(__file__).parent
    names = ['event_time.py', 'event_cache.py', 'mbp1_views.py', 'adapters.py', 'native_resolution.py', 'empirical_tape.py', 'objects/profiles.py']
    return content_hash({n: file_digest(directory / n) for n in names})


@lru_cache(maxsize=4)
def ownership(data_root):
    return adapters.ownership_manifest(data_root)


def contract_at(data_root, at):
    import pyarrow.parquet as pq
    path = Path(data_root) / 'derived/continuous-futures__instrument-and-roll-maps/nq-rolls.parquet'
    rows = pq.read_table(path).to_pylist()
    selected = [r for r in rows if r['segment_start_ms'] * 1_000_000 <= at
                and (r['segment_end_exclusive_ms'] is None or at < r['segment_end_exclusive_ms'] * 1_000_000)]
    if len(selected) != 1:
        raise NativeEvidenceError('no unique acquired continuous-contract identity for date')
    return {**selected[0], 'roll_source_path': str(path), 'roll_source_sha256': file_digest(path),
            'identity_use': 'acquired continuous membership only, not a tradable roll forecast'}


def restore(document):
    for bars in document['bars'].values():
        for bar in bars:
            for key in 'OHLC':
                if bar.get(key) is not None:
                    bar[key] = Decimal(str(bar[key]))
    for row in document['footprints']:
        row['pv'], row['p2v'] = Decimal(str(row['pv'])), Decimal(str(row['p2v']))
        row['rows'] = [[Decimal(str(p)), b, s, u] for p, b, s, u in row['rows']]
    return document


def cached_window(data_root, start, end, instrument_id, *, cache_root=DEFAULT_CACHE, seconds=(1, 60, 120, 180, 300, 1800)):
    cache_root = Path(cache_root).resolve()
    data_root = Path(data_root).resolve()
    # Only the explicitly owned new derived subtree may receive new data.
    if cache_root.is_relative_to(data_root) and not cache_root.is_relative_to(data_root / 'derived/phase1-event-time-v2'):
        raise NativeEvidenceError('event cache must use its own new derived subtree')
    plan = plan_window(data_root, start, end, ownership=ownership(str(data_root)))
    sources = identify_sources(plan)
    identity = {'transform_sha256': transform_identity(), 'contract_sha256': content_hash(CONTRACT),
                'sources': sources, 'ownership_sha256': plan['ownership_sha256'],
                'start_ns': start, 'end_ns': end, 'instrument_id': str(instrument_id), 'seconds': list(seconds)}
    key = content_hash(identity)
    directory = cache_root / key
    receipt_path = directory / 'manifest.json'
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt['cache_identity'] != identity or receipt['cache_key'] != key:
            raise NativeEvidenceError('stale event cache identity')
        path = directory / 'window.json.gz'
        if file_digest(path) != receipt['artifact_sha256']:
            raise NativeEvidenceError('damaged event cache artifact')
        document = restore(json.loads(gzip.decompress(path.read_bytes())))
        if document['input_sha256'] != receipt['input_sha256']:
            raise NativeEvidenceError('event input receipt differs')
        return document, receipt
    document = build_event_window(data_root, start, end, instrument_id,
                                  ownership=ownership(str(data_root)), frozen_inputs=sources, seconds=seconds)
    cache_root.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix='building-', dir=cache_root))
    payload = gzip.compress(json.dumps(jsonable(document), sort_keys=True, separators=(',', ':')).encode(), mtime=0)
    (temp / 'window.json.gz').write_bytes(payload)
    receipt = {'schema': 'phase1-event-cache-v2', 'cache_identity': identity, 'cache_key': key,
               'path': str(directory / 'window.json.gz'), 'artifact_sha256': file_digest(temp / 'window.json.gz'),
               'input_sha256': document['input_sha256'], 'membership_sha256': document['membership_sha256'],
               'row_count': document['row_count'], 'raw_sources_unchanged': document['raw_sources_unchanged']}
    (temp / 'manifest.json').write_text(json.dumps(receipt, indent=2) + '\n')
    try:
        temp.rename(directory)
    except OSError as error:
        if error.errno not in {errno.EEXIST,errno.ENOTEMPTY}:raise
        # Concurrent derivations must agree byte for byte; never overwrite.
        existing = json.loads(receipt_path.read_text())
        if existing != receipt or file_digest(directory/'window.json.gz')!=receipt['artifact_sha256']:
            raise NativeEvidenceError('concurrent event derivation disagrees')
        (temp / 'window.json.gz').unlink(); (temp / 'manifest.json').unlink(); temp.rmdir()
    return document, receipt


def prepare_date(day, *, data_root='/workspace/data', cache_root=DEFAULT_CACHE):
    day = date.fromisoformat(day) if isinstance(day, str) else day
    instrument = contract_at(data_root, clock(day, '09:30'))
    # Include the overnight prefix and every printed other-session clock.
    start, end = clock(day - timedelta(days=1), '18:00'), clock(day, '16:00')
    document, receipt = cached_window(data_root, start, end, instrument['instrument_id'], cache_root=cache_root)
    return {'session_date': str(day), 'instrument': jsonable(instrument), 'event_input': receipt,
            'scope': EventWindow(document).coverage(start, end)}
