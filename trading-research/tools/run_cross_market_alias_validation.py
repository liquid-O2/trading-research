"""Registered regression and acquired-source check for the exact alias correction."""
from pathlib import Path
import hashlib
import importlib.util
import io
import sys
import unittest

SOURCE = Path(__file__).with_name('run_cross_market_study.py')
BASE_SHA = 'ceeda1c164092bc7434e0aa958f07922dae69edc948cdbb4488e4ba005c0986d'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError('alias validation base changed')
spec = importlib.util.spec_from_file_location('cross_alias_validation_base', SOURCE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.__file__ = __file__
base.OPERATIONAL_LIMITS = base.ROOT / 'validation/CROSS_MARKET_DIAGNOSTIC_LIMITS_V1.json'


def validate(packet, protocol, store, outputs):
    import numpy as np
    import pyarrow as pa
    import pyarrow.parquet as pq
    from trading_research.research.cross_market_alignment import parse_raw_minute_table, unit_quality_row
    spec = importlib.util.spec_from_file_location('test_cross_market_descriptive', base.ROOT / 'tests/test_cross_market_descriptive.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
    tests = {'passed': result.wasSuccessful(), 'tests': result.testsRun,
             'failures': len(result.failures), 'errors': len(result.errors), 'output': stream.getvalue()}
    outputs.json('unit-tests.json', tests, kind='cross_market_unit_tests_v1')
    if not tests['passed']:
        raise ValueError('alias correction regression failure: ' + stream.getvalue())
    _, admitted = base.predecessor_actual(packet['configuration']['predecessor'], store, protocol, 'admit')
    selected = [item for item in admitted['sources'] if item['source'].get('role') == 'minute_ohlcv'
                and item['source'].get('year') == 2026 and item['source']['symbol'] not in ('NQ', 'ES')]
    records = []
    for item in selected:
        source = item['source']
        raw = base.checked(Path('/workspace/data') / source['path'], item['sha256'],
                           maximum=protocol['resources']['maximum_source_file_bytes'])
        if len(raw) != source['size_bytes']:
            raise ValueError('admitted source bytes differ')
        table = pq.read_table(pa.BufferReader(raw))
        if len(table) != item['rows']:
            raise ValueError('admitted source row count differs')
        ts = table['t'].to_numpy(zero_copy_only=False)
        unique_ts, first_indices = np.unique(ts, return_index=True)
        unit = parse_raw_minute_table(table, symbol=source['symbol'], file_id=item['file_id'],
                                     source_sha256=item['sha256'], year=2026)
        if unit.source_row_count != len(table) or len(unit) != len(unique_ts):
            raise ValueError('original/unique row counts fail independent reconciliation')
        np.testing.assert_array_equal(unit.start_ns, unique_ts * 1_000_000)
        # Every original source field is unchanged at the retained first address.
        for source_name, result_name in [('o', 'open'), ('h', 'high'), ('l', 'low'),
                                         ('c', 'close'), ('v', 'volume')]:
            original = np.asarray(table[source_name].to_numpy(zero_copy_only=False), dtype=np.float64)
            np.testing.assert_array_equal(getattr(unit, result_name).view(np.uint64),
                                          original[first_indices].view(np.uint64))
            for repeated, first in unit.identical_source_aliases:
                if original[repeated].view(np.uint64) != original[first].view(np.uint64):
                    raise ValueError('an alias payload field differs')
        identities = table['instrument_id'].to_numpy(zero_copy_only=False)
        np.testing.assert_array_equal(unit.instrument_id, identities[first_indices])
        for repeated, first in unit.identical_source_aliases:
            if identities[repeated] != identities[first] or ts[repeated] != ts[first]:
                raise ValueError('alias instrument/timestamp differs')
        if len(unit.identical_source_aliases) != len(table) - len(unique_ts):
            raise ValueError('every duplicate original row needs an address')
        records.append({**unit_quality_row(unit), 'source_path': source['path'],
                        'independent_field_and_alias_reconciliation': True})
    ref = outputs.json('alias-validation.json', {
        'kind': 'cross_market_alias_validation_v1', 'records': records,
        'all_2026_raw_sources_validated': len(records) == len(selected) == 4,
        'prior_2020_pilot_retained': True, 'full_population_complete': False,
    }, kind='cross_market_alias_validation_v1')
    return {'kind': 'cross_market_alias_validation_v1', 'passed': True, 'tests': tests,
            'all_2026_raw_sources_validated': len(records) == len(selected) == 4,
            'base_runner_sha256': BASE_SHA, 'diagnostic_only': True,
            'full_population_complete': False, 'validation': ref, 'output_bytes': outputs.written}


base.run_measurement = validate
if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        raise SystemExit(base.worker(sys.argv[2]))
    if len(sys.argv) != 2:
        raise SystemExit('usage: run_cross_market_alias_validation.py accepted-admission-execution')
    raise SystemExit(base.parent('pilot', sys.argv[1]))
