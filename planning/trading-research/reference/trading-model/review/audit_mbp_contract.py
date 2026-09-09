"""Bounded, read-only MBP-1 schema/event/flag audit; no strategy implementation.

Inspect every NQ/ES Parquet footer, reuse the existing first/middle/last file
selection for 4096-row first/last row-group prefixes, and read at most 4096
records from the first/middle/last native HG/NKD/SI files. Counts describe these
selected records, not population frequencies or certified event reconstruction.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
import time
import databento as db
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
DATA = Path('/workspace/data')
OUT = ROOT / 'review/mbp-review'
OUT.mkdir(exist_ok=True)
BITS = {f.name: int(f) for f in db.RecordFlags}
started = time.monotonic()


def summarize(rows):
    actions = Counter(str(r['action']) for r in rows)
    trades = [r for r in rows if str(r['action']) == 'T']
    return {
        'rows': len(rows), 'actions': dict(actions),
        'side_by_action': {a: dict(Counter(str(r['side']) for r in rows if str(r['action']) == a)) for a in actions},
        'flags': dict(Counter(str(int(r['flags'])) for r in rows)),
        'flag_bits': {name: sum(bool(int(r['flags']) & bit) for r in rows) for name, bit in BITS.items()},
        'trade_rows': len(trades),
        'trade_volume': sum(int(r['size']) for r in trades),
        'unknown_side_trade_volume': sum(int(r['size']) for r in trades if str(r['side']) not in ('A', 'B')),
        'trade_rows_without_last': sum(not (int(r['flags']) & BITS['F_LAST']) for r in trades),
        'trade_rows_with_maybe_bad_book': sum(bool(int(r['flags']) & BITS['F_MAYBE_BAD_BOOK']) for r in trades),
        'capture_sha256': hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
        'examples': rows[:3],
    }


footers = []
for folder in sorted((DATA / 'quantpad').glob('*__mbp-1')):
    for path in sorted(folder.glob('*.parquet')):
        pf = pq.ParquetFile(path)
        footers.append({'file': str(path.relative_to(DATA)), 'bytes': path.stat().st_size,
                        'rows': pf.metadata.num_rows, 'row_groups': pf.metadata.num_row_groups,
                        'schema': str(pf.schema_arrow), 'fields': pf.schema_arrow.names})
print('Parquet footers inspected:', len(footers), flush=True)

parquet = []
prior = json.loads((ROOT / 'review/data-audit/parquet-samples.json').read_text())
for selected in prior:
    if '__mbp-1' not in selected['dataset']:
        continue
    path = DATA / selected['file']
    before = path.stat()
    pf = pq.ParquetFile(path)
    chunks = []
    for g in sorted({0, pf.metadata.num_row_groups - 1}):
        if g < 0:
            continue
        batch = next(pf.iter_batches(batch_size=4096, row_groups=[g], use_threads=False), None)
        if batch is not None:
            rec = summarize(batch.to_pylist())
            rec['row_group'] = g
            chunks.append(rec)
    after = path.stat()
    parquet.append({'file': selected['file'], 'scope': 'up to 4096 rows from start of first and last row group',
                    'file_size_and_mtime_unchanged': (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
                    'fields': pf.schema_arrow.names, 'chunks': chunks})

native = []
keys = ['ts_recv', 'ts_event', 'publisher_id', 'instrument_id', 'rtype', 'sequence',
        'action', 'side', 'depth', 'price', 'size', 'flags', 'ts_in_delta']
for folder in sorted((DATA / 'databento').glob('*__mbp-1')):
    files = sorted(folder.glob('*.dbn.zst'))
    for i in sorted({0, len(files) // 2, len(files) - 1}):
        path = files[i]
        before = path.stat()
        store = db.DBNStore.from_file(path)
        rows = []
        for record in itertools.islice(store, 4096):
            row = {}
            for key in keys:
                value = getattr(record, key)
                row[key] = str(value) if key in ('action', 'side') else int(value)
            for key in ['bid_px', 'ask_px', 'bid_sz', 'ask_sz', 'bid_ct', 'ask_ct']:
                row[key + '_00'] = int(getattr(record.levels[0], key))
            rows.append(row)
        after = path.stat()
        native.append({'file': str(path.relative_to(DATA)), 'bytes': before.st_size,
                       'schema': str(store.metadata.schema), 'dataset_file_count': len(files),
                       'scope': 'first at most 4096 records; may include initial snapshots and multiple contracts',
                       'file_size_and_mtime_unchanged': (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
                       'fields': list(rows[0]) if rows else [], 'summary': summarize(rows)})
    print('Native family inspected:', folder.name, flush=True)

all_chunks = [c for p in parquet for c in p['chunks']] + [n['summary'] for n in native]
report = {
    'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'All NQ/ES MBP Parquet footers; selected bounded NQ/ES/HG/NKD/SI row prefixes. No complete event reconstruction, gap recovery, strategy, model, backtest, or live capture.',
    'databento_version': db.__version__, 'flag_definitions': BITS,
    'parquet_footers': footers, 'parquet_samples': parquet, 'native_samples': native,
    'totals': {'parquet_footers': len(footers), 'parquet_sample_files': len(parquet),
               'native_sample_files': len(native), 'selected_rows': sum(c['rows'] for c in all_chunks),
               'selected_trade_rows': sum(c['trade_rows'] for c in all_chunks),
               'selected_trade_rows_without_last': sum(c['trade_rows_without_last'] for c in all_chunks),
               'selected_maybe_bad_book_rows': sum(c['flag_bits']['F_MAYBE_BAD_BOOK'] for c in all_chunks)},
    'elapsed_seconds': round(time.monotonic() - started, 3),
}
(OUT / 'mbp_contract_audit.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report['totals'], indent=2), flush=True)
