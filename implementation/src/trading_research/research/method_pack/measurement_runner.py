"""Resumable census wrapper over the accepted native setup scanners.

The setup implementation is reused unchanged. Only measurement, population
accounting and execution scheduling are added here.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
import argparse
import json
import os
from pathlib import Path
import time
import traceback

from . import historical_runner as hr
from .empirical_protocol import content_hash
from .historical_features import HistoricalFeatures
from .historical_outcomes import observe_outcome
from .measurement_outcomes import measure_setup
from .native_discovery import scan_branch
from .strategy_policy import observation_scope
from .event_cache import ownership
from .clocks import ns_to_et


BASE = hr.ROOT/'implementation/reports/phase1-live/historical-measurement'


def measurement_scope(method, branch):
    # This branch is explicitly a post-parent annotation in the accepted source
    # definition. Keep the legacy assessment, but never count it as an entry.
    if method == 'GB-FAIL' and branch == 'mss_fvg_refinement':
        return 'supplemental_observation'
    return observation_scope(method, branch)


def configure_runtime():
    """Reuse the already tested stable-file SHA cache, without changing bytes.

    Native event membership, transform identity and all aggregation functions
    remain unchanged. The cache invalidates on dev/inode/size/mtime/ctime and
    fully rehashes small or recently modified files, exactly as in the accepted
    runner. This avoids hashing the same monthly file for every prior window.
    """
    from . import event_cache, event_time
    event_cache.file_digest = hr.file_digest
    event_time.file_digest = hr.file_digest
    # Bound Arrow's worker multiplication when many independent dates run.
    import pyarrow as pa
    pa.set_cpu_count(1)
    pa.set_io_thread_count(1)


def freeze(root):
    root = Path(root).resolve()
    protocol = root/'protocol/MEASUREMENT_PROTOCOL_1_1.json'
    policy = hr.read(protocol)
    owned = ownership('/workspace/data')
    endpoint = max(r['end_ns'] for r in owned['owned_spans'])
    final = ns_to_et(endpoint-1).date()
    start = date.fromisoformat(policy['population']['start_session_date'])
    days = [str(start+timedelta(days=i)) for i in range((final-start).days+1)
            if (start+timedelta(days=i)).weekday() < 5]
    source_files = {}
    for row in owned['owned_spans']:
        p = Path(row['path']); st = p.stat()
        source_files[str(p)] = {'bytes': st.st_size, 'mtime_ns': st.st_mtime_ns,
                               'ctime_ns': st.st_ctime_ns, 'inode': st.st_ino}
    option_base = Path('/workspace/data/thetadata-opra')
    context_inventory = {}
    for name in ('opra__qqq-options__quote-1m__dte14__strike-range42', 'opra__qqq-options__open-interest'):
        paths = sorted((option_base/name).glob('*.parquet'))
        context_inventory[name] = [{'date': p.stem, 'path': str(p), 'bytes': p.stat().st_size,
                                    'mtime_ns': p.stat().st_mtime_ns} for p in paths]
    hr.immutable_json(root/'protocol/ACQUIRED_INPUT_POPULATION.json',
                      {'owned': owned, 'files_at_freeze': source_files,
                       'context_files_at_freeze': context_inventory,
                       'endpoint_ns_exclusive': endpoint,
                       'note': 'First/last owned bounds are input endpoints, not continuous-feed certificates.'})
    hr.immutable_json(root/'protocol/SCOPE.json', {
        'schema': 'phase1-full-history-scope-v1', 'study_start': str(start),
        'study_end': str(final), 'evaluation_dates': days, 'pilot_dates': [],
        'selection': 'all weekday session labels through acquired endpoint; closures and incomplete windows explicitly accounted',
        'sample_kind': 'full acquired historical population; no date subsampling',
        'action_scope': 'unchanged versioned scanner windows and prior lookbacks',
        'measurement_protocol': {'path': str(protocol), 'sha256': hr.file_digest(protocol)},
        'population_manifest': {'path': str(root/'protocol/ACQUIRED_INPUT_POPULATION.json'),
                               'sha256': hr.file_digest(root/'protocol/ACQUIRED_INPUT_POPULATION.json')},
        'evaluation_exposure': policy['exposure'],
    })
    registry = hr.freeze(root, scope_path=root/'protocol/SCOPE.json', strategy=True)
    hr.immutable_json(root/'protocol/EXECUTION_POLICY.json', {
        'registry_sha256': registry['registry_sha256'],
        'hash_cache': 'existing historical_runner.file_digest stable-file cache reused by event_time and event_cache; exact aggregation and canonical ownership unchanged',
        'daily_units': '57 branch/extra jobs per session; STOIC-DATA process_review is collection-scoped and evaluated after collection',
        'macro_units': 'both source macro units retain daily measured quantities; collection process qualification is evaluated separately',
        'failures': 'worker exceptions retained with traceback and retried after investigation; never changed to a zero-setup result',
        'setup_source_baseline': policy['setup_baseline'],
    })
    return {'registry_sha256': registry['registry_sha256'], 'sessions': len(days),
            'first': days[0], 'last': days[-1], 'root': str(root)}


def validate_protocol(registry):
    for key in ('measurement_protocol', 'population_manifest'):
        receipt = registry['scope'][key]
        if hr.file_digest(receipt['path']) != receipt['sha256']:
            raise ValueError('frozen measurement input changed: '+key)


def effective_omissions(market, document):
    """Keep the original limitations and explicitly identify resolved range ones."""
    active, resolved = [], []
    range_only = document['method_id'] in {'JJ-TBR', 'GB-FAIL'}
    recovered = [item for prior in market._earlier.values()
                 if prior.get('range_scope_complete') for item in prior['omissions']]
    for item in document['omissions']:
        if item.get('kind') == 'measured_selection' or (
                item.get('kind') == 'original_source_audit_requirement' and item.get('id')):
            resolved.append({'original': item, 'disposition': 'source-audit-only or completed deterministic selection'})
        elif range_only and item in recovered:
            resolved.append({'original': item, 'disposition': 'resolved by accepted continuous prior-price-range input; no volume profile substitution'})
        else:
            active.append(item)
    return active, resolved


def session_accounting(market, document):
    scope = measurement_scope(document['method_id'], document['branch'])
    active, resolved = effective_omissions(market, document)
    calendar = market.policy.rth(market.day)
    # The original scanner reports RTH coverage; retain it. Add a conservative
    # full admitted-prefix check for definitions consuming overnight structure.
    needs_overnight = document['method_id'] in {'JJ-TBR', 'SIRES', 'SAINT-AMT'} or (
        document['method_id'] == 'GB-FAIL' and document['branch'] == 'asia_tdo_case') or document['method_id'] == 'GB-VWAP'
    start = market.start if needs_overnight else market.at('06:00') if document['method_id'] == 'GB-SCALP' else market.at('09:30')
    coverage = market.coverage(start, market.end)
    assessment = [e.get('strategy_assessment', {}) for e in document['episodes']]
    unknown = sum(a.get('status') == 'data_unavailable' for a in assessment)
    closed = calendar['state'] == 'closed_rth' and not document['episodes']
    complete = coverage['observed_scope_complete'] and not active and unknown == 0 and not closed
    status = ('personal_execution_out_of_scope' if scope == 'personal_execution_out_of_scope' else
              'scheduled_closure' if closed else 'completed_search' if complete else 'observed_search_with_input_limitations')
    return {'scope': scope, 'status': status, 'searched_session': True,
            'eligible_complete_session': complete and scope == 'entry_setup',
            'completed_zero_setup_search': complete and scope == 'entry_setup' and
                not any(a.get('status') == 'setup' for a in assessment),
            'calendar': calendar, 'required_current_prefix': [start, market.end],
            'current_prefix_coverage': coverage, 'active_omissions': active,
            'original_omission_dispositions': resolved, 'unavailable_candidates': unknown,
            'note': 'Complete refers to owned observed inputs, not exchange-feed completeness. Observed setups in limited sessions remain retained separately.'}


def date_job(root, day):
    configure_runtime()
    root = Path(root)
    registry, manifest = hr.load_registry(root)
    validate_protocol(registry)
    market = HistoricalFeatures(day, records=hr._records(registry))
    receipts = []
    for row in manifest['branches']:
        if row['method_id'] == 'STOIC-DATA' and row['branch'] == 'process_review':
            continue
        path = hr._job_path(root, 'evaluation', day, row['coverage_id'])
        if path.exists():
            document = hr.verify_job(hr.read_job(path), registry, row, market)
            if document.get('measurement_protocol_sha256') != registry['scope']['measurement_protocol']['sha256']:
                raise ValueError('measurement checkpoint protocol differs')
        else:
            started = time.monotonic()
            document = scan_branch(market, row)
            ids = [e['candidate_id'] for e in document['episodes']]
            if len(ids) != len(set(ids)):
                raise ValueError('duplicate candidate opportunity within branch/session')
            document['outcomes'] = [observe_outcome(market, e) for e in document['episodes']]
            document['setup_measurements'] = [measure_setup(market, e) for e in document['episodes']
                if measurement_scope(row['method_id'], row['branch']) == 'entry_setup'
                and e['strategy_assessment']['status'] == 'setup']
            document['session_accounting'] = session_accounting(market, document)
            document.update(registry_sha256=registry['registry_sha256'],
                software_sha256=registry['software']['sha256'], cohort='evaluation',
                measurement_protocol_sha256=registry['scope']['measurement_protocol']['sha256'],
                input_receipts=list({content_hash(r): r for r in market.input_receipts}.values()),
                domain_observations=hr.domain_receipts(root, market), job_state='completed',
                native_executions=market.window.document['row_count'])
            hr.write_job(path, document)
            print(json.dumps({'event': 'branch_completed', 'date': day, 'branch': row['coverage_id'],
                              'seconds': round(time.monotonic()-started, 2)}), flush=True)
        receipts.append({'coverage_id': row['coverage_id'], 'path': str(path), 'sha256': hr.file_digest(path)})
    completion = {'schema': 'phase1-measurement-date-completion-v1', 'date': day,
                  'registry_sha256': registry['registry_sha256'], 'jobs': receipts,
                  'native_executions': market.window.document['row_count'],
                  'native_input_sha256': market.window.document['input_sha256']}
    hr.immutable_json(root/'jobs/evaluation'/day/'completion.json', completion)
    # Daily option tables are large. Their causal results are already retained
    # in this day's receipts; releasing them bounds a long-lived worker.
    from .strategy_options import option_rows, spot_rows
    from .strategy_measurements import vendor_rows
    option_rows.cache_clear()
    spot_rows.cache_clear()
    vendor_rows.cache_clear()
    return {'date': day, 'jobs': len(receipts), 'native_executions': completion['native_executions']}


def run(root, workers=16, dates=None):
    root = Path(root).resolve()
    registry, manifest = hr.load_registry(root)
    validate_protocol(registry)
    days = registry['scope']['evaluation_dates']
    if dates:
        selected = dates.split(',')
        if not set(selected) <= set(days):
            raise ValueError('date is outside frozen population')
        days = selected
    todo = [day for day in days if not (root/'jobs/evaluation'/day/'completion.json').exists()]
    print(json.dumps({'event': 'run_started', 'declared_sessions': len(days), 'pending': len(todo),
                      'workers': workers, 'registry_sha256': registry['registry_sha256']}), flush=True)
    failures = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        pending = {pool.submit(date_job, str(root), day): day for day in todo}
        for future in as_completed(pending):
            day = pending[future]
            try:
                print(json.dumps({'event': 'date_completed', **future.result()}), flush=True)
            except Exception:
                failure = {'date': day, 'registry_sha256': registry['registry_sha256'],
                           'at': datetime.now(timezone.utc).isoformat(), 'traceback': traceback.format_exc()}
                path = root/'failures'/day/(str(time.time_ns())+'.json')
                hr.immutable_json(path, failure)
                failures.append(day)
                print(json.dumps({'event': 'date_failed', 'date': day, 'evidence': str(path)}), flush=True)
    return {'sessions_requested': len(days), 'attempted': len(todo), 'failed_dates': failures}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['freeze', 'run', 'date'])
    parser.add_argument('--run-root', required=True)
    parser.add_argument('--workers', type=int, default=16)
    parser.add_argument('--dates')
    args = parser.parse_args()
    result = (freeze(args.run_root) if args.command == 'freeze' else
              date_job(args.run_root, args.dates) if args.command == 'date' else
              run(args.run_root, args.workers, args.dates))
    print(json.dumps(hr.serializable(result), indent=2), flush=True)


if __name__ == '__main__':
    main()
