"""Registered inspection of the 2026 ordering failure; no scientific acceptance."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

SOURCE = Path(__file__).with_name('run_cross_market_study.py')
BASE_SHA = '9a7023f7482cfca2a75748a5b95a3616182cc6a69ae93d985afb5c67b9fd3b4a'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError('diagnostic base changed')
spec = importlib.util.spec_from_file_location('cross_timestamp_diagnostic_base', SOURCE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.__file__ = __file__
base.OPERATIONAL_LIMITS = base.ROOT / 'validation/CROSS_MARKET_DIAGNOSTIC_LIMITS_V1.json'


def diagnose(packet, protocol, store, outputs):
    import numpy as np
    import pyarrow as pa
    import pyarrow.parquet as pq
    _, admitted = base.predecessor_actual(packet['configuration']['predecessor'], store, protocol, 'admit')
    records = []
    for item in admitted['sources']:
        source = item['source']
        if source.get('role') != 'minute_ohlcv' or source.get('year') != 2026 or source['symbol'] in ('NQ', 'ES'):
            continue
        path = Path('/workspace/data') / source['path']
        raw = base.checked(path, item['sha256'], maximum=protocol['resources']['maximum_source_file_bytes'])
        if len(raw) != source['size_bytes']:
            raise ValueError('admitted source size differs')
        table = pq.read_table(pa.BufferReader(raw))
        if len(table) != item['rows']:
            raise ValueError('admitted source rows differ')
        ts = table['t'].to_numpy(zero_copy_only=False)
        bad = np.flatnonzero(ts[1:] <= ts[:-1]) + 1
        order = np.argsort(ts, kind='stable')
        sorted_ts = ts[order]
        equal = np.flatnonzero(sorted_ts[1:] == sorted_ts[:-1]) + 1
        examples = sorted(set(int(j) for i in bad[:20] for j in (i - 1, i)))
        duplicates = sorted(set(int(order[j]) for i in equal[:20] for j in (i - 1, i)))
        record = {
            'file_id': item['file_id'], 'source': source, 'sha256': item['sha256'],
            'rows': len(table), 'timestamp_type': str(table.schema.field('t').type),
            'decreasing_adjacent': int(np.count_nonzero(ts[1:] < ts[:-1])),
            'equal_adjacent': int(np.count_nonzero(ts[1:] == ts[:-1])),
            'equal_after_stable_sort': len(equal),
            'bad_adjacent_rows': [{'row_index': i, **row} for i, row in zip(examples, table.take(pa.array(examples, type=pa.int64())).to_pylist())],
            'same_timestamp_rows': [{'row_index': i, **row} for i, row in zip(duplicates, table.take(pa.array(duplicates, type=pa.int64())).to_pylist())],
        }
        records.append(record)
    ref = outputs.json('timestamp-diagnosis.json', {
        'kind': 'cross_market_timestamp_diagnostic_v1', 'year': 2026,
        'records': records, 'source_rescan_scope': 'Only raw 2026 minute inputs implicated by full10 loading failure',
        'original_failure': '/workspace/coordination/trading-research-cursor/crossmarket10-diagnosis.json',
        'full_population_complete': False,
    }, kind='cross_market_timestamp_diagnostic_v1')
    return {'kind': 'cross_market_timestamp_diagnostic_result_v1', 'passed': True,
            'full_population_complete': False, 'diagnostic_only': True,
            'diagnosis': ref, 'output_bytes': outputs.written}


base.run_measurement = diagnose
if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        raise SystemExit(base.worker(sys.argv[2]))
    if len(sys.argv) != 2:
        raise SystemExit('usage: run_cross_market_timestamp_diagnostic.py accepted-admission-execution')
    raise SystemExit(base.parent('pilot', sys.argv[1]))
