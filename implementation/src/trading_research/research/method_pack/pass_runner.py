"""One method pass owns fixture verification, evidence scoring and complete reports."""

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shlex
import sys
import tempfile

from . import FORMULA_VERSION, HEADLINE, METHOD_IDS, SLUGS, SOURCE_WIKI_COMMIT
from .catalog import BRANCHES, EXTRA_PREDICATES, PRIMARY, METHOD_BY_ID, objects_for
from .contracts import consumed_hashes, fields_for, inventory_errors, sections, validate_output
from .discovery import discovery_audit, discovery_holes
from .evidence import CASE_BRANCHES, SchemaError
from .assembly import read_assembled_manifest, producer_coverage_matrix
from .native_resolution import NativeResolver
from .native_windows import AuditedWindowResolver
from .protocol import RECIPES, FIXTURES, jsonable, run_recipe
from .secondary import reference_outcome
from .report import counts, headline_row, implementation_identity, markdown_twin, sha256_file, utc_now, write_json, write_text, family_tables, summary_status


QUALITY_ZERO = ('fixture_failures', 'unbound_fields', 'duplicate_candidates',
                'year_reconciliation_errors', 'leakage_count', 'proxy_as_faithful_count')


def _partition(record):
    return json.dumps([record['instrument_id'], record.get('source_versions', [])], sort_keys=True)


def _summarize(records, predicate, cohort, mode, requested_years, partition=None):
    selected = [r for r in records if r['predicate'] == predicate and r['cohort_id'] == cohort and r['evidence_mode'] == mode and (partition is None or _partition(r) == partition)]
    years = {}
    for year in sorted(set(requested_years) | {str(r['year']) for r in selected}):
        years[year] = {**counts([r['verdict'] for r in selected if str(r['year']) == year]),
                       'coverage': requested_years.get(year, {}).get('status', 'supplied_record'),
                       'reason': requested_years.get(year, {}).get('reason')}
    return {'predicate': predicate, 'cohort': cohort, 'evidence_mode': mode, 'partition': partition,
            'instrument_id': selected[0]['instrument_id'] if selected else None,
            'source_versions': selected[0].get('source_versions', []) if selected else [],
            **counts([r['verdict'] for r in selected]), 'years': years}


def validate_report(doc, fixture_rows, candidates):
    errors = []
    for summary in doc['summaries']:
        if summary['n'] != summary['p'] + summary['f'] or summary['N'] != summary['n'] + summary['u']:
            errors.append('cohort arithmetic does not reconcile')
        for key in ('p', 'f', 'u', 'n', 'N'):
            if sum(y[key] for y in summary['years'].values()) != summary[key]:
                errors.append(f'{summary["predicate"]} {key} year reconciliation')
        expected = counts(['pass'] * summary['p'] + ['fail'] * summary['f'] + ['unknown'] * summary['u'])
        if any(summary[k] != expected[k] for k in ('rate', 'rate_exact', 'interval', 'interval_exact')):
            errors.append('rate or exact missingness interval does not reconcile')
        branch_counts = [c for b in [*doc['branches'].values(), *doc.get('case_branches', {}).values()] for c in b['cohorts']
                         if c['cohort'] == summary['cohort'] and c['predicate'] == summary['predicate']
                         and c['evidence_mode'] == summary['evidence_mode'] and c['partition'] == summary['partition']]
        for key in ('p', 'f', 'u', 'n', 'N'):
            if sum(c[key] for c in branch_counts) != summary[key]:
                errors.append(f'{summary["predicate"]} {key} branch reconciliation')
    expected_objects = set(objects_for(doc['identity']['method_id']))
    fixture_ids = {r['id'] for r in fixture_rows}
    method_recipe = METHOD_BY_ID[doc['identity']['method_id']]
    for number in (1, 2, 3):
        if not any(fid == f'{method_recipe}-F{number}' or fid.startswith(f'{method_recipe}-F{number}-')
                   for fid in fixture_ids):
            errors.append(f'missing printed method fixture {method_recipe}-F{number}')
    for kind in ('late', 'missing', 'identity'):
        if not any(r['id'].startswith(method_recipe + '-') and r.get('kind') == f'c08_{kind}'
                   for r in fixture_rows):
            errors.append(f'missing {method_recipe} {kind} mutation')
    for row in fixture_rows:
        if 'inputs' not in row or 'expected' not in row:
            errors.append(f'fixture {row["id"]} lacks reviewable inputs/expected values')
    for oid in expected_objects:
        if f'{oid}-F1' not in fixture_ids:
            errors.append(f'missing printed fixture {oid}-F1')
        for kind in ('late', 'missing', 'identity'):
            if not any(r.get('recipe') == oid and r.get('kind') == f'c08_{kind}' for r in fixture_rows):
                errors.append(f'missing {oid} {kind} mutation')
    for name, meta in doc['artifacts'].items():
        path = Path(meta['path'])
        if not path.is_file() or sha256_file(path) != meta['sha256']:
            errors.append(f'missing or mismatched artifact {name}')
    if set(doc['branches']) != set(BRANCHES[doc['identity']['method_id']]):
        errors.append('incomplete branch inventory')
    if len({c['candidate_id'] for c in candidates}) != len(candidates):
        errors.append('duplicate candidates')
    return errors


def cmd_method_pass(args):
    from importlib.util import find_spec
    if args.method not in METHOD_IDS or (args.formula_version or FORMULA_VERSION) != FORMULA_VERSION or args.scope != 'acquired':
        print('invalid method, formula version or scope', file=sys.stderr)
        return 2
    data_root, report_root = Path(args.data_root).resolve(), Path(args.report_root).resolve()
    if not data_root.is_dir():
        print(f'data root does not exist: {data_root}', file=sys.stderr)
        return 2
    if report_root == data_root or data_root in report_root.parents:
        print('report root must be outside the read-only data root', file=sys.stderr)
        return 2
    if find_spec('pyarrow') is None and next(data_root.rglob('*.parquet'), None) is not None:
        print('invalid runtime: acquired Parquet requires the declared implementation[data] dependencies', file=sys.stderr)
        return 2
    method_id = args.method
    try:
        supplied, parsed, manifest_hash = (None, None, None)
        native_resolver = AuditedWindowResolver(data_root)
        if args.episodes:
            supplied, parsed, manifest_hash = read_assembled_manifest(
                args.episodes, method_id, resolver=native_resolver)
        return _run(args, data_root, report_root, supplied, parsed, manifest_hash,
                    native_window_audits=native_resolver.audit_records())
    except SchemaError as exc:
        print(f'invalid episode schema: {exc}', file=sys.stderr)
        return 2
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'implementation_fail: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 1


def _run(args, data_root, report_root, supplied, parsed, manifest_hash, *, native_window_audits=()):
    from .adapters import c03_raw_audit, inventory_acquired
    from .core_fixtures import run_core_fixtures
    from .methods import method_fixtures
    from .objects import run_object_fixtures

    method_id, slug = args.method, SLUGS[args.method]
    assembled = parsed or []
    scored_by_id = {episode.result['candidate_id']: episode.result for episode in assembled}
    assembly_rows = [{'candidate_id': episode.result['candidate_id'],
                      'software_complete': episode.result['software_complete'],
                      'bindings': episode.bindings, 'holes': episode.holes}
                     for episode in assembled]
    if assembled:
        indexes = ({}, {}, {}, {})
        for episode in assembled:
            for target, records in zip(indexes, episode.parsed):
                for identity, record in records.items():
                    if identity in target and target[identity] != record:
                        raise SchemaError(f'conflicting shared observation {identity}')
                    target[identity] = record
        parsed = indexes
    else:
        parsed = None
    fixture_rows = run_core_fixtures()
    fixture_rows.extend(run_object_fixtures(objects_for(method_id)))
    fixture_rows.extend(method_fixtures(method_id))
    raw_audit = c03_raw_audit(data_root)
    if raw_audit['available']:
        ok = raw_audit['matches_printed_table']
        fixture_rows.append({'id': 'C03-F1:acquired', 'recipe': 'C03', 'kind': 'raw_adapter_audit',
                             'status': 'pass' if ok else 'fail', 'failures': [] if ok else ['Acquired C03 table mismatch'],
                             'inputs': {'path': raw_audit['path'], 'rows': raw_audit['rows'], 'q': raw_audit['q']},
                             'expected': {'buy_volume': 7, 'sell_volume': 4, 'delta': 3, 'first_spread_ticks': '2'},
                             'actual_value': raw_audit, 'evidence_mode': 'raw_derived'})
    fixtures_failed = [r for r in fixture_rows if r['status'] != 'pass']
    schema_rows = []
    from copy import deepcopy
    for fixture in FIXTURES:
        if fixture['recipe'] not in objects_for(method_id):
            continue
        try:
            result = validate_output(run_recipe(fixture['recipe'], deepcopy(fixture['inputs'])))
            schema_rows.append({'fixture_id': fixture['id'], 'recipe_id': fixture['recipe'],
                                'status': 'pass', 'state': result.state,
                                'output_fields': sorted(result.value)})
        except (ValueError, TypeError, KeyError) as exc:
            schema_rows.append({'fixture_id': fixture['id'], 'recipe_id': fixture['recipe'],
                                'status': 'implementation_fail', 'reason': str(exc)})
    for error in inventory_errors(method_id):
        fixtures_failed.append({'id': 'inventory', 'failures': [error]})
    inventory = inventory_acquired(data_root, method_id)
    inventory['raw_adapter_audit'] = raw_audit
    # The retained archive includes pre-study history and future calendar rows.
    # Neither belongs in the 2020+ historical method denominator.
    requested_years = {year: row for year, row in inventory.get('years', {}).items()
                       if 2020 <= int(year) <= datetime.now(timezone.utc).year}
    selector_review = discovery_audit(method_id)
    study_scope = {'primary_instrument': 'NQ', 'start_date': '2020-01-01',
                   'end': 'actual acquired endpoint for each selected dependency',
                   'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md',
                   'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}
    holes = discovery_holes(method_id) + inventory.get('holes', [])
    if method_id == 'SIRES':
        holes.extend({'hole_id': f'HOLE:M05:{branch}:automatic_admission', 'recipe_id': 'M05',
                      'method_id': method_id, 'branch': branch, 'candidate_id': None,
                      'kind': 'source_definition', 'missing_fields': ['automatic_admission'],
                      'source_ref': f'FORMULAS M05 {branch}', 'affected_output': 'sequence',
                      'reason': 'Disclosed incomplete case only; a full automatic entry trigger is not supplied.'}
                     for branch in sorted(CASE_BRANCHES))
    candidates, object_rows, outcome_rows = [], [], []
    if parsed:
        inputs, objects, assertions, evidence = parsed
        for candidate in inputs.values():
            scored = scored_by_id[candidate['candidate_id']]
            candidates.append(scored)
            holes.extend(scored['holes'])
            if scored['predicate'] == 'sequence':
                outcome = reference_outcome(candidate, objects, evidence)
                spec = candidate.get('outcome_spec') or {}
                pending = [spec[key] for key in ('objective_id', 'invalidation_id', 'coverage_object_id') if key in spec]
                outcome_objects, outcome_evidence = set(), set()
                while pending:
                    oid = pending.pop()
                    if oid in outcome_objects or oid not in objects:
                        continue
                    outcome_objects.add(oid)
                    outcome_evidence.update(objects[oid]['evidence_ids'])
                    pending.extend(objects[oid]['parent_ids'])
                outcome['used_object_ids'] = sorted(outcome_objects)
                outcome['used_evidence_ids'] = sorted(outcome_evidence)
                outcome_rows.append(outcome)
                if outcome.get('hole'):
                    holes.append({'hole_id': outcome['hole'], 'recipe_id': 'C06', 'method_id': method_id,
                                  'branch': candidate['branch'], 'candidate_id': candidate['candidate_id'],
                                  'kind': 'ordering' if outcome.get('detected_causal_violation') else 'supplied_record_missing',
                                  'missing_fields': [outcome['hole'].split(':')[-1]],
                                  'source_ref': 'FORMULAS C06', 'affected_output': 'reference_outcome',
                                  'reason': 'The preselected reference outcome lacks its required definition, identity, availability or coverage proof.'})
        used_objects = {oid for c in candidates for oid in c['used_object_ids']}
        used_assertions = {aid for c in candidates for aid in c['used_assertion_ids']}
        used_evidence = {eid for c in candidates for eid in c['used_evidence_ids']}
        used_objects.update(oid for result in outcome_rows for oid in result['used_object_ids'])
        used_evidence.update(eid for result in outcome_rows for eid in result['used_evidence_ids'])
        object_rows = [dict(objects[oid], record_type='object') for oid in sorted(used_objects)]
        object_rows += [dict(assertions[aid], record_type='assertion') for aid in sorted(used_assertions)]
        object_rows += [dict(evidence[eid], record_type='evidence') for eid in sorted(used_evidence)]
    primary = PRIMARY[method_id]
    predicates = [primary, *EXTRA_PREDICATES.get(method_id, [])]
    summaries = [{**_summarize([], p, 'historical_discovery', 'raw_derived', requested_years),
                  'search_status': 'unavailable', 'sample_size': None,
                  'denominator_status': 'not_established',
                  'note': 'No historical search was completed. Zero ledger rows are not zero discovered candidates.'}
                 for p in predicates]
    for predicate, cohort, mode, partition in sorted({(c['predicate'], c['cohort_id'], c['evidence_mode'], _partition(c)) for c in candidates}):
        summaries.append(_summarize(candidates, predicate, cohort, mode, {}, partition))
    branches = {branch: {**counts([]), 'predicate': primary, 'cohort': 'historical_discovery',
                         'evidence_mode': 'raw_derived', 'status': 'unavailable',
                         'status_scope': 'historical_discovery', 'search_status': 'unavailable',
                         'candidate_discovery': 'hole', 'hole_ids': [h['hole_id'] for h in holes if h.get('branch') == branch],
                         'cohorts': []} for branch in BRANCHES[method_id]}
    case_branches = {branch: {**counts([]), 'predicate': 'case_description', 'cohort': 'historical_discovery',
                              'evidence_mode': 'raw_derived', 'status': 'unavailable', 'candidate_discovery': 'hole',
                              'status_scope': 'historical_discovery', 'search_status': 'unavailable',
                              'hole_ids': [f'HOLE:M05:{branch}:automatic_admission'], 'cohorts': []}
                     for branch in sorted(CASE_BRANCHES)} if method_id == 'SIRES' else {}
    for branch, row in [*branches.items(), *case_branches.items()]:
        for summary in summaries[ len(predicates): ]:
            items = [c for c in candidates if c['branch'] == branch and c['predicate'] == summary['predicate']
                     and c['cohort_id'] == summary['cohort'] and c['evidence_mode'] == summary['evidence_mode'] and _partition(c) == summary['partition']]
            if items:
                row['cohorts'].append({'predicate': summary['predicate'], 'cohort': summary['cohort'],
                                       'evidence_mode': summary['evidence_mode'], 'partition': summary['partition'],
                                       'instrument_id': summary['instrument_id'], 'source_versions': summary['source_versions'],
                                       **counts([c['verdict'] for c in items])})
    producer_matrix = producer_coverage_matrix(method_id)
    quality = {
        'fixture_failures': len(fixtures_failed),
        'unbound_fields': sum(not f.recipes for f in fields_for(method_id).values()),
        'duplicate_candidates': len(candidates) - len({c['candidate_id'] for c in candidates}),
        'year_reconciliation_errors': 0,
        'leakage_count': sum(c['verdict'] == 'pass' and c['detected_causal_violations'] > 0 for c in candidates),
        'proxy_as_faithful_count': sum(c['verdict'] == 'pass' and c['rejected_proxy_attempts'] > 0 for c in candidates),
        'detected_causal_violations': sum(c['detected_causal_violations'] for c in candidates) + sum(bool(r.get('detected_causal_violation')) for r in fixture_rows),
        'rejected_proxy_attempts': sum(c['rejected_proxy_attempts'] for c in candidates),
        'missing_operand_implementations': sum(row['binding_status'] == 'missing_implementation' for row in producer_matrix),
        'assembly_implementation_failures': sum(not c['software_complete'] for c in candidates),
        'output_schema_failures': sum(row['status'] != 'pass' for row in schema_rows),
    }
    status = 'implementation_fail' if any(quality[k] for k in QUALITY_ZERO) or any(quality[k] for k in (
        'missing_operand_implementations','assembly_implementation_failures','output_schema_failures')) else 'checks_passed'
    command = ['python', 'implementation/tools/run_phase1_objects.py', 'method-pass', '--method', method_id,
               '--scope', args.scope, '--data-root', str(args.data_root), '--report-root', str(args.report_root)]
    if args.episodes:
        command += ['--episodes', str(args.episodes)]
    if args.formula_version:
        command += ['--formula-version', args.formula_version]
    identity = {'method_id': method_id, 'formula_version': FORMULA_VERSION,
                'source_wiki_commit': SOURCE_WIKI_COMMIT, 'source_hashes': consumed_hashes(method_id),
                'discovery_audit_sha256': selector_review['audit_sha256'],
                **implementation_identity(Path(__file__).resolve().parents[5]),
                'command': shlex.join(command), 'command_argv': command, 'created_at': utc_now()}
    inclusion = {'method_id': method_id, 'formula_version': FORMULA_VERSION, 'scope': 'acquired',
                 'candidate_discovery': 'hole', 'inclusion_rule': 'Only explicitly supplied C01 episodes; automatic source selector unavailable.',
                 'historical_study_scope': study_scope, 'discovery_audit': selector_review,
                 'excluded_from_historical_sample': ['synthetic_fixture', 'chart_geometry_diagnostic', 'archive_inventory_row'],
                 'branches': BRANCHES[method_id], 'required_objects': objects_for(method_id),
                 'source_hashes': identity['source_hashes'], 'ownership': inventory.get('ownership', []),
                 'episode_manifest_sha256': manifest_hash, 'candidate_ids': [c['candidate_id'] for c in candidates]}
    inclusion_hash = hashlib.sha256(json.dumps(jsonable(inclusion), sort_keys=True).encode()).hexdigest()
    report_root.mkdir(parents=True, exist_ok=True)
    detail_root = report_root / slug
    detail_root.mkdir(exist_ok=True)
    run_root = Path(tempfile.mkdtemp(prefix='run-', dir=detail_root))
    artifacts = {}
    for name, rows in [('candidates.jsonl', candidates), ('objects.jsonl', object_rows), ('holes.jsonl', holes),
                       ('management.jsonl', [c for c in candidates if c['predicate'] == 'management']),
                       ('reference-outcomes.jsonl', outcome_rows), ('assembly.jsonl', assembly_rows),
                       ('operand-producers.jsonl', producer_matrix), ('output-contracts.jsonl', schema_rows),
                       ('native-window-audits.jsonl', native_window_audits)]:
        payload = ''.join(json.dumps(jsonable(row), sort_keys=True) + '\n' for row in rows)
        path = run_root / name
        artifacts[name] = {'path': str(path), 'sha256': write_text(path, payload), 'count': len(rows)}
    fixtures_path = run_root / 'fixtures.json'
    artifacts['fixtures.json'] = {'path': str(fixtures_path), 'sha256': write_json(fixtures_path, fixture_rows), 'count': len(fixture_rows)}
    inclusion_path = run_root / 'cohort.json'
    artifacts['cohort.json'] = {'path': str(inclusion_path), 'sha256': write_json(inclusion_path, inclusion), 'count': len(candidates)}
    coverage_path = run_root / 'coverage.json'
    artifacts['coverage.json'] = {'path': str(coverage_path), 'sha256': write_json(coverage_path, inventory), 'count': len(inventory.get('files', []))}
    if supplied is not None:
        path = run_root / 'episodes.json'
        artifacts['episodes.json'] = {'path': str(path), 'sha256': write_json(path, supplied), 'count': len(candidates)}
    section = sections()[METHOD_BY_ID[method_id]]
    limitations = [line for line in section.splitlines() if line.startswith('**Source-complete candidate discovery:**')
                   or ('**' in line and ('F3' in line or 'conflict' in line.lower() or 'causal correction' in line.lower()))]
    doc = {'identity': identity,
           'scope': {'requested': 'acquired', 'data_root': str(data_root),
                     'historical_study': study_scope,
                     'requested_date_span': inventory.get('requested_date_span'),
                     'actual_date_span': inventory.get('actual_date_span'),
                     'native_instruments': inventory.get('native_instruments', []),
                     'branch_inventory': BRANCHES[method_id], 'source_variants': sorted({e.get('source_version', '') for e in (parsed[3].values() if parsed else [])}),
                     'case_branch_inventory': list(case_branches),
                     'evidence_modes': sorted({'synthetic_fixture', *(c['evidence_mode'] for c in candidates)}),
                     'partial_endpoint_years': [y for y, r in requested_years.items() if r.get('status') == 'partial'],
                     'candidate_discovery': 'hole'},
           'ownership': inventory.get('ownership', []), 'coverage': inventory,
           'cohort': {**inclusion, 'manifest_hash': inclusion_hash,
                      'eligible_ids': [c['candidate_id'] for c in candidates], 'unselected_ids': [],
                      'historical_n': None, 'historical_search_status': 'unavailable',
                      'fixture_count': len(fixture_rows),
                      'relationships': [{'candidate_id': c['candidate_id'], 'parent_attempt_id': c.get('parent_attempt_id'),
                                         'thesis_id': c.get('thesis_id'), 'touch_id': c.get('touch_id'), 'order_id': c.get('order_id'),
                                         'fill_ids': c.get('fill_ids', [])} for c in candidates]},
           'summary': summaries[0], 'summaries': summaries, 'branches': branches, 'case_branches': case_branches,
           'years': requested_years, 'status': status, 'status_scope': 'implementation_checks', 'quality': quality,
           'dimensions': {
               'software_completeness': {'status': 'failed' if status == 'implementation_fail' else 'checks_passed',
                   'fixture_checks': len(fixture_rows), 'fixture_failures': len(fixtures_failed),
                   'output_contract_checks': len(schema_rows), 'output_schema_failures': quality['output_schema_failures'],
                   'operand_count': len(producer_matrix), 'missing_operand_implementations': quality['missing_operand_implementations'],
                   'scope': 'Report checks; full stage acceptance is recorded in the completion obligation matrix.'},
               'source_ambiguity': {'status': 'limitations_recorded',
                   'source_case_catalog': str(Path(__file__).with_name('source_cases_v2.json')),
                   'selector_review': selector_review['audit_path']},
               'data_coverage': {'status': 'per_observation',
                   'resolved_objects': sum(o.get('evidence_class') in {'resolved_native','parent_derived'} for o in object_rows),
                   'objects_with_unknown_coverage': sum(o.get('record_type') == 'object' and o.get('recipe_coverage_ok') is not True for o in object_rows),
                   'inventory_is_continuity_proof': False},
               'source_case_agreement': {'status': 'separate_chart_review',
                   'source_illustration_episodes': sum(c['evidence_mode'] == 'source_illustration' for c in candidates),
                   'performance_estimate': False},
               'historical_discovery': {'status': 'unavailable', 'search_completed': False,
                   'candidate_count': None, 'reason': 'The full branch requires unavailable source definitions or actual case/process records.'}},
           'reference_outcomes': {'unit': 'preselected reference after decision', 'N': len(outcome_rows),
                                  'counts': {label: sum(r['outcome'] == label for r in outcome_rows)
                                             for label in ('target_first', 'invalidation_first', 'same_time_unknown', 'neither_observed', 'censored', 'unknown')},
                                  'limitation': 'No inferred outcome window, stop or objective; outcomes never repair entry compliance.'},
           'source_limitations': limitations, 'artifacts': artifacts,
           'discovery_audit': selector_review,
           'operand_contract': {f: {'type': c.type, 'producer_recipes': c.recipes, 'rule': c.rule} for f, c in fields_for(method_id).items()}}
    errors = validate_report(doc, fixture_rows, candidates)
    if errors:
        quality['year_reconciliation_errors'] = sum('reconciliation' in e for e in errors)
        quality['fixture_failures'] += len(errors)
        doc['status'] = 'implementation_fail'
        doc['dimensions']['software_completeness']['status'] = 'failed'
        doc['report_errors'] = errors
    md_path, json_path = report_root / f'{slug}.md', report_root / f'{slug}.json'
    headlines = [headline_row(method_id, s['predicate'], s, summary_status(s, doc['status']), str(md_path)) for s in summaries]
    write_text(md_path, markdown_twin(doc, headlines))
    write_json(json_path, jsonable(doc))
    if not md_path.is_file() or not json_path.is_file():
        raise OSError('missing method report')
    print(HEADLINE)
    print('\n'.join(headlines))
    phase_table, audit_table = family_tables(doc, str(md_path))
    print('\n'.join(phase_table))
    print('\n'.join(audit_table))
    if doc['status'] == 'implementation_fail':
        for row in fixtures_failed:
            print(f'{row["id"]}: {row.get("failures")}', file=sys.stderr)
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0
