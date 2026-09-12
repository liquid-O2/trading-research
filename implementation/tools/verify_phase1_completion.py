#!/usr/bin/env python3
"""Run the final suite or verify the complete, separately scoped evidence.

This gate cannot create manual obligation approvals. It requires the reviewed
matrix, current tests, actual native artifacts, source review and all twelve
runner reports before it writes a completion statement.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import gzip
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = ROOT / 'implementation/validation/phase1-completion'
REPORTS = ROOT / 'implementation/reports/phase1-live/methods'
sys.path.insert(0, str(ROOT / 'implementation/src'))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def ref(path):
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': digest(path)}


def read(path):
    return json.loads(Path(path).read_text())


def now():
    return datetime.now(timezone.utc).isoformat()


def test_inputs():
    paths = [*ROOT.joinpath('implementation/src').rglob('*.py'),
             *ROOT.joinpath('implementation/src').rglob('*.json'),
             *ROOT.joinpath('implementation/tests').rglob('*.py'),
             *ROOT.joinpath('implementation/tools').glob('*.py'),
             ROOT / 'implementation/pyproject.toml',
             ROOT / 'implementation/uv.lock',
             ROOT / 'planning/phase-1-live/FORMULAS.md',
             *ROOT.joinpath('planning/phase-1-live/wiki').glob('*.md')]
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)}


def run_tests():
    VALIDATION.mkdir(parents=True, exist_ok=True)
    before = test_inputs()
    command = [sys.executable, '-m', 'pytest', '-q', 'implementation/tests',
               '--junitxml=' + str(VALIDATION / 'pytest.xml')]
    started = now()
    with (VALIDATION / 'pytest.log').open('w') as log:
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    after = test_inputs()
    log = (VALIDATION / 'pytest.log').read_text()
    match = re.search(r'(\d+) passed(?:, (\d+) subtests passed)?', log)
    suites = ET.parse(VALIDATION / 'pytest.xml').getroot().iter('testsuite')
    totals = {key: 0 for key in ('tests', 'failures', 'errors', 'skipped')}
    for suite in suites:
        for key in totals:
            totals[key] += int(suite.get(key, 0))
    passed = result.returncode == 0 and before == after and totals['failures'] == totals['errors'] == 0
    document = dict(schema='phase1-final-test-run-v1', status='pass' if passed else 'fail',
        started_at=started, completed_at=now(), command=command, exit_code=result.returncode,
        source_stable_during_run=before == after, tested_source_files=after,
        python_version=sys.version,
        package_versions={name: importlib.metadata.version(name) for name in
                          ('pytest', 'pypdf', 'pyarrow', 'numpy', 'numba')},
        pytest_passed=int(match[1]) if match else None,
        subtests_passed=int(match[2] or 0) if match else None, junit=totals,
        artifacts=[ref(VALIDATION / 'pytest.log'), ref(VALIDATION / 'pytest.xml')])
    (VALIDATION / 'test-run.json').write_text(json.dumps(document, indent=2) + '\n')
    print(json.dumps({k: v for k, v in document.items() if k not in {'tested_source_files', 'command'}}), flush=True)
    return 0 if passed else 1


def verify_ref(record, *, base=None):
    path = Path(record['path'])
    if not path.is_absolute():
        root_path = ROOT / path
        path = base / path if base is not None and not root_path.is_file() else root_path
    assert path.is_file(), f'missing artifact: {path}'
    assert digest(path) == record['sha256'], f'stale artifact hash: {path}'


def verify_linked_artifacts(value, *, base=None):
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
            verify_ref(value, base=base)
        if isinstance(value.get('evidence_path'), str) and isinstance(value.get('evidence_sha256'), str):
            verify_ref({'path': value['evidence_path'], 'sha256': value['evidence_sha256']}, base=base)
        for child in value.values():
            verify_linked_artifacts(child, base=base)
    elif isinstance(value, list):
        for child in value:
            verify_linked_artifacts(child, base=base)


def final_gate():
    from trading_research.research.method_pack import METHOD_IDS, SLUGS
    from trading_research.research.method_pack.catalog import METHOD_BY_ID
    from trading_research.research.method_pack.report import implementation_identity
    from trading_research.research.method_pack.source_config import load_catalog

    tests = read(VALIDATION / 'test-run.json')
    assert tests['status'] == 'pass' and tests['exit_code'] == 0
    assert tests['tested_source_files'] == test_inputs(), 'implementation changed after final tests'
    for record in tests['artifacts']:
        verify_ref(record)
    matrix = read(VALIDATION / 'obligation-matrix.json')
    assert matrix['status'] == 'complete', matrix['status']
    for key, count in [('objects', 166), ('core_contracts', 9), ('methods', 12), ('method_fields', 373)]:
        assert len(matrix[key]) == count
        assert all(row['status'] == 'complete' for row in matrix[key]), key
    assert matrix['checks']['regression_audit']['status'] == 'pass'
    assert matrix['checks']['regression_audit']['probe_count'] == 27
    for record in matrix['native_artifacts']:
        verify_ref(record)
    for record in matrix['inputs']['ledgers']:
        verify_ref(record)
    verify_ref(matrix['inputs']['regression_audit'])
    catalog = load_catalog(verify_sources=True)
    cases = read(VALIDATION / 'source-case-review.json')
    assert cases['case_count'] == len(catalog['cases'])
    assert {r['method_id'] for r in cases['cases']} == set(METHOD_IDS)
    verify_ref(cases['source_catalog'])
    for case in cases['cases']:
        assert case['visual_review']['status'] == 'reviewed'
        assert case['historical_discovery']['n'] is None
        assert case['historical_candidate'] is False
        verify_ref(case['visual_review']['chart'])
        assembled = case.get('assembled_measurement')
        if assembled:
            verify_ref(assembled['evidence'])
            assert assembled['software_complete'] is True
            assert assembled['detected_causal_violations'] == assembled['rejected_proxy_attempts'] == 0
    for record in cases['charts']:
        verify_ref(record)
    verify_ref(cases['frozen_vwap_comparison'])
    flow = read(VALIDATION / 'native-flow.json')
    verify_ref(flow['full_artifact'])
    full_flow = json.loads(gzip.decompress((ROOT / flow['full_artifact']['path']).read_bytes()))
    full_windows = {window['date']: window for window in full_flow['windows']}
    assert {window['date'] for window in flow['windows']} == {'2026-02-24', '2026-06-12', '2026-07-23'}
    for window in flow['windows']:
        summaries = window['summary_objects']
        assert all(row['state'] != 'invalid' for row in summaries), window['date']
        for recipe_id in ('O004', 'O098', 'O108', 'O112', 'O120'):
            rows = [row for row in summaries if row['recipe_id'] == recipe_id]
            assert rows and all(row['state'] == 'computed' for row in rows), (window['date'], recipe_id)
            assert all(type(row['known_at']) is int and row['known_at'] <= window['end_ns'] for row in rows)
        results = {row['recipe_id']: row['result'] for row in full_windows[window['date']]['objects']}
        response, tape = results['O164'], results['O098']['value']
        assert response['known_at'] == window['end_ns']
        assert Decimal(response['value']['aggressive_volume']) == Decimal(tape['total'])
        if window['date'] == '2026-06-12':
            # The final native timestamp has two different prices and no
            # exchange sequence. Exact effort survives; endpoint response
            # must remain unknown instead of choosing physical row order.
            events = tape['event_records']
            last = max(row['event_key'] for row in events)
            batch = [row for row in events if row['event_key'] == last]
            assert {Decimal(row['price']) for row in batch} == {Decimal('29339.25'), Decimal('29339.0')}
            assert all(row['exchange_sequence'] is None for row in batch)
            assert response['state'] == 'hole' and response['hole_ids'] == ['HOLE:O164:response_endpoint_order']
            assert response['value']['price_response_points'] is None
            assert response['value']['price_response_ticks'] is None
            assert response['value']['response_record_complete'] is None
            assert Decimal(response['value']['aggressive_volume']) == Decimal('13338')
        else:
            assert response['state'] == 'computed' and not response['hole_ids']
        chart = window['chart_data']
        same = chart['same_candle']
        assert Decimal(same['complete_5m']['poc']) - Decimal(same['developing_2m']['poc']) == Decimal(same['poc_change'])
        assert chart['footprint_close']
        for row in chart['footprint_close']:
            assert Decimal(row['buy_volume']) + Decimal(row['sell_volume']) + Decimal(row['unknown_volume']) == Decimal(row['total_volume'])
    verify_linked_artifacts(read(VALIDATION / 'native-geometry.json'))
    for path in (REPORTS / 'reconstructions/v2').glob('*.json'):
        verify_linked_artifacts(read(path), base=path.parent)
    profile_dir = REPORTS / 'reconstructions/v2'
    profiles = read(profile_dir / 'JJ-profiles-2026-06-12.json')['profiles']
    assert {row['kind'] for row in profiles} == {'prior_rth', 'prior_eth', 'overnight', 'developing_rth', 'selected_range'}
    assert len({row['snapshot_id'] for row in profiles}) == 5
    assert sum(row['coverage_ok'] is None for row in profiles) == 4
    for profile in profiles:
        path = profile_dir / profile['payload']['path']
        payload = json.loads(gzip.decompress(path.read_bytes()))['profile']['value']
        rows = payload['rows']
        assert len(rows) == profile['native_rows'] and rows
        assert sum(Decimal(row['total_volume']) for row in rows) == Decimal(profile['total_volume'])
        assert sum(Decimal(row['unknown_volume']) for row in rows) == Decimal(profile['unknown_volume'])
        assert sum(Decimal(row['buy_volume']) - Decimal(row['sell_volume']) for row in rows) == Decimal(profile['known_delta'])
        assert payload['snapshot_id'] == profile['snapshot_id']
        assert payload['formation_start'] == profile['formation_start']
        assert payload['formation_end'] == profile['formation_end']
        assert payload['known_at'] == profile['known_at']
        peak = max(Decimal(row['total_volume']) for row in rows)
        assert Decimal(profile['poc']) in {Decimal(row['price']) for row in rows if Decimal(row['total_volume']) == peak}
    code_hash = implementation_identity(ROOT)['implementation_dirty_hash']
    method_rows = []
    for method in METHOD_IDS:
        path = REPORTS / 'completion' / (SLUGS[method] + '.json')
        document = read(path)
        assert document['identity']['implementation_dirty_hash'] == code_hash, f'stale runner: {method}'
        software = document['dimensions']['software_completeness']
        assert document['status'] == 'checks_passed'
        assert document['status_scope'] == 'implementation_checks'
        assert software['status'] == 'checks_passed'
        for key in ('fixture_failures', 'output_schema_failures', 'missing_operand_implementations'):
            assert software[key] == 0, (method, key)
        for key in ('leakage_count', 'proxy_as_faithful_count', 'assembly_implementation_failures', 'year_reconciliation_errors'):
            assert document['quality'][key] == 0, (method, key)
        historical = document['dimensions']['historical_discovery']
        assert historical['status'] == 'unavailable' and historical['candidate_count'] is None
        assert historical['search_completed'] is False
        for record in document['artifacts'].values():
            verify_ref(record)
        method_rows.append(dict(method=method, id=METHOD_BY_ID[method], software='complete',
            historical='unavailable', n=None, faithful_disagreements=None,
            fixture_checks=software['fixture_checks'], leakage=0, proxy_as_faithful=0,
            report=ref(path), report_md=str(path.with_suffix('.md'))))
    evidence_paths = ['obligation-matrix.json', 'test-run.json', 'audit-regressions.json',
        'native-boundary.json', 'native-flow.json', 'native-geometry.json',
        'native-clock-coverage.json', 'source-case-review.json', 'legacy-cache-review.json',
        'research-process-journal.json']
    outcome = dict(schema='phase1-completion-acceptance-v1', completed_at=now(), status='complete',
        scope='Implementation stages 1–7; no Stage 8 research or performance claim',
        counts=dict(objects=166, core_contracts=9, methods=12, method_operands=373,
                    source_case_records=len(catalog['cases'])),
        tests=dict(passed=tests['pytest_passed'], subtests=tests['subtests_passed']),
        software_completeness='complete', source_ambiguity='reviewed_with_limitations',
        data_coverage='per_observation_with_evidenced_gaps',
        source_case_agreement='reviewed_figures_controls_and_retained_conflicts',
        historical_discovery=dict(status='unavailable', n=None, search_completed=False),
        methods=method_rows, evidence=[ref(VALIDATION / p) for p in evidence_paths])
    (VALIDATION / 'final-acceptance.json').write_text(json.dumps(outcome, indent=2) + '\n')
    print(json.dumps({k: outcome[k] for k in ('status', 'counts', 'tests', 'historical_discovery')}), flush=True)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-tests', action='store_true')
    args = parser.parse_args()
    raise SystemExit(run_tests() if args.run_tests else final_gate())
