#!/usr/bin/env python3
"""Prepare immutable native event inputs, without evaluating method outcomes."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from trading_research.research.method_pack.event_cache import prepare_date, transform_identity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('/workspace/implementation/reports/phase1-live/implementation-v2'))
    parser.add_argument('--date', action='append')
    parser.add_argument('--workers', type=int, default=2, choices=range(1, 5))
    args = parser.parse_args()
    scope = json.loads((args.root / 'SCOPE_POLICY.json').read_text())
    days = args.date or sorted(set(scope['evaluation_dates'] + scope['pilot_dates']))
    out = args.root / 'inputs' / transform_identity(); out.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(prepare_date, day): day for day in days}
        for future in as_completed(futures):
            result = json.loads(json.dumps(future.result(), default=str))
            path = out / (result['session_date'] + '.json')
            if path.exists() and json.loads(path.read_text()) != result:
                raise ValueError('input receipt exists with a different identity; use a new run root')
            path.write_text(json.dumps(result, indent=2) + '\n')
            print(json.dumps({'date': result['session_date'], 'executions': result['event_input']['row_count'],
                              'input_sha256': result['event_input']['input_sha256']}), flush=True)


if __name__ == '__main__':
    main()
