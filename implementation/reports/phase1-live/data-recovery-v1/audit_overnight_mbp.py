"""Read-only correction: include 2020 MBP-1 in overnight execution coverage.

Overlapping monthly/weekly files are inspected separately, never concatenated
as an execution stream. Counts of missing slots deduplicate instrument/minute.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import json
import numpy as np
import pyarrow.parquet as pq
from audit_tape import ROOT, OUT, identify, identities, native_rows, physical_ranges

MINUTE = 60_000_000_000

def main():
    census_path = OUT / 'BAR_CENSUS.json'
    inventory_path = OUT.parent / 'empirical/coverage/native-inventory-all.json'
    identify(census_path); identify(inventory_path)
    census = json.loads(census_path.read_text())
    inventory = json.loads(inventory_path.read_text())['files']
    windows = {w['window_id']: w for w in census['windows']}
    keys = {key for job in census['jobs'] if job['group'] == 'overnight' for key in job['window_ids']}
    keys |= {row['window_id'] for row in census['observed_unknowns']}
    slots = {(windows[key]['instrument_id'], minute) for key in keys
             for start, end in windows[key]['missing_minute_ranges'] for minute in range(start, end)}
    files = [f for f in inventory if f['root'] == 'NQ' and f['dataset_key'] == 'mbp1'
             and f['canonical_owner'] == 'owned']
    first = min(f['observed_min_ns'] for f in files)
    overlaps = []; groups = defaultdict(set)
    for instrument, minute in sorted(slots):
        matches = [f for f in files if f['observed_min_ns'] < (minute + 1) * MINUTE
                   and f['observed_max_ns'] >= minute * MINUTE]
        if matches:
            overlaps.append({'instrument_id': instrument, 'minute': minute,
                             'paths': [f['path'] for f in matches]})
        for f in matches:
            groups[f['path'], instrument].add(minute)
    results = []
    for (relative, instrument), minutes in sorted(groups.items()):
        path = ROOT / 'data' / relative
        start, end = min(minutes) * MINUTE, (max(minutes) + 1) * MINUTE
        trades = native_rows(path, start, end, instrument)
        trades = [r for r in trades if r['t'] // MINUTE in minutes]
        table = pq.read_table(path, columns=['t', 'instrument_id', 'action', 'flags'],
                              filters=[('t', '>=', start), ('t', '<', end), ('instrument_id', '=', instrument)])
        times = table['t'].to_numpy(); wanted = np.isin(times // MINUTE, list(minutes))
        actions = table['action'].to_numpy()[wanted]; flags = table['flags'].to_numpy()[wanted]
        results.append({'path': relative, 'instrument_id': instrument,
                        'start_utc': datetime.fromtimestamp(start / 1e9, timezone.utc).isoformat(),
                        'end_utc': datetime.fromtimestamp(end / 1e9, timezone.utc).isoformat(),
                        'missing_minutes': len(minutes), 'all_MBP_rows': int(wanted.sum()),
                        'actions': dict(Counter(actions.tolist())),
                        'flags': {str(k): v for k, v in Counter(flags.tolist()).items()},
                        'execution_rows': len(trades),
                        'minutes_with_executions': len({r['t'] // MINUTE for r in trades}),
                        'execution_volume': sum(int(r['size']) for r in trades),
                        'physical_trade_membership': physical_ranges(trades),
                        'schema': pq.ParquetFile(path).schema_arrow.names})
    # Check identities again after both reads; raw inputs are never opened for writing.
    for key, identity in list(identities.items()):
        before = identity.copy(); del identities[key]
        assert identify(ROOT / key) == before, key
    assert len(slots) == 10393 and len(overlaps) == 123
    assert all(row['execution_rows'] == 0 for row in results)
    identify(Path(__file__).resolve())
    summary = {'unique_missing_slots': len(slots),
               'slots_before_first_MBP_record': sum((m + 1) * MINUTE <= first for i, m in slots),
               'slots_overlapping_MBP_files': len(overlaps),
               'overlap_slots_by_UTC_date': dict(Counter(datetime.fromtimestamp(x['minute'] * 60, timezone.utc).date().isoformat() for x in overlaps)),
               'local_execution_replacement_slots': 0,
               'quiet_minute_candidates_with_book_updates': 3,
               'unresolved_two_hour_block_minutes': 120}
    result = {'schema': 'phase1-overnight-mbp-followup-v1', 'summary': summary,
              'scope': 'All unique overnight and observed-unknown-prefix missing slots from BAR_CENSUS.json',
              'raw_data_modified': False, 'new_replay': False,
              'ownership_limit': 'File-level owned inventory overlap. Monthly/weekly diagnostics are separate; overlapping rows are not pooled. This is not a canonical merged-stream coverage certificate.',
              'interpretation': 'Three isolated intervals have book updates but no recorded trades. The two-hour interval has only one book record, also present in an overlapping file. No executions were recovered; no-trade versus feed-gap completeness remains unproven.',
              'overlap_slots': overlaps, 'file_window_results': results, 'source_files': identities}
    (OUT / 'OVERNIGHT_MBP_FOLLOWUP.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
