"""Idempotently attach a successful shared run to its exact registered family cases."""
from dataclasses import asdict
import json
from pathlib import Path
import sys

from trading_research.operations.artifacts import artifact_ref, code_manifest, digest
from trading_research.operations.ledger import Ledger
from trading_research.operations.scope import Scope
from trading_research.operations.trials import TrialRegistry
from trading_research.verify import validate_engineering_metrics
from verify_engineering_batch import atomic_json, validate_successful_completion
from engineering_batch_contract import (
    ROOT, RESOLVED, baseline_assertions, case_contract, package_path, validate_batch,
    validate_coverage, validate_registrations, validate_review_support, retain_mapping_inputs, final_resource_error,
    batch_resources, validate_resource_binding,
)

LIST_FIELDS = ('reference_and_code_artifacts', 'verification_artifacts', 'review_artifacts', 'assertion_ids')
REASON = 'Attach exact registered family engineering evidence from one physical supervised execution.'


def main():
    summary = json.loads(Path(sys.argv[1]).read_bytes())
    ledger, trials = Ledger(ROOT / 'evidence'), TrialRegistry(ROOT / 'evidence/trials')
    supervised_ref = artifact_ref(summary['artifact'])
    supervised = trials.artifacts.read_json(supervised_ref)
    for key in ('success', 'shared_execution_id', 'members', 'reason', 'cpu_seconds', 'wall_seconds', 'peak_rss_bytes'):
        if summary[key] != supervised[key]:
            raise ValueError(f'mutable summary differs from immutable {key}')
    if summary['verification'] != supervised['result'] or not supervised['success'] or supervised['status'] != 'succeeded':
        raise ValueError('only the exact successful supervised result can be attached')
    configuration = supervised['configuration']
    error=final_resource_error(supervised['cpu_seconds'],supervised['wall_seconds'],supervised['peak_rss_bytes'],configuration)
    if error is not None: raise ValueError(error)
    if configuration['shared_execution_id'] != supervised['shared_execution_id']:
        raise ValueError('shared configuration identity differs')
    validate_successful_completion(trials, {
        **{key: supervised[key] for key in ('shared_execution_id', 'configuration', 'members', 'code_snapshot')},
        'worker_start_identity': supervised.get('worker_start_identity'),
        'worker_resource_acknowledgement': supervised.get('worker_resource_acknowledgement'),
        'completion': supervised,
    })
    batch_raw = trials.artifacts.read(artifact_ref(configuration['batch_contract']))
    batch = validate_batch(json.loads(batch_raw))
    validate_resource_binding(batch, configuration, supervised.get('worker_resource_acknowledgement'))
    acknowledgement = supervised.get('worker_resource_acknowledgement')
    if acknowledgement is not None:
        start = supervised.get('worker_start_identity')
        if (start is None or acknowledgement.get('start_identity') != start
                or acknowledgement.get('pid') != start['pid'] or acknowledgement.get('pgid') != start['pgid']
                or start['pid'] != start['pgid'] or acknowledgement.get('worker_source') != configuration['supervisor_path']):
            raise ValueError('successful resources do not identify the retained worker process')
    cpu_limit, _, _, _ = batch_resources(batch)
    batch_path = configuration['batch_path']
    if package_path(batch_path).read_bytes() != batch_raw or batch['id'] != configuration['batch_id']:
        raise ValueError('local batch contract or retained batch identity differs')
    specs = batch['families']
    registrations = configuration['registrations']
    validate_registrations(trials, registrations, batch)
    members = supervised['members']
    if (len(members) != len(specs) or {m['family'] for m in members} != {s['family'] for s in specs}
            or len({m['attempt_id'] for m in members}) != len(members)
            or len({m['trial_id'] for m in members}) != len(members)):
        raise ValueError('duplicate, missing or extra participating members')
    preflight = configuration['preflight']
    for role, relative in batch['tools'].items():
        if package_path(relative).read_bytes() != trials.artifacts.read(artifact_ref(preflight[role])):
            raise ValueError('reviewed orchestration source changed after execution')
    if preflight['supervisor'] != configuration['supervisor']:
        raise ValueError('supervisor source references disagree')

    seen = set()
    def retain(value):
        ref = artifact_ref(value) if isinstance(value, dict) else value
        key = (ref.sha256, ref.size_bytes, ref.kind)
        if key in seen:
            return asdict(ref)
        try:
            raw = trials.artifacts.read(ref)
        except FileNotFoundError:
            raw = ledger.artifacts.read(ref)
        if ledger.artifacts.put_bytes(raw, kind=ref.kind) != ref:
            raise ValueError('retained artifact identity differs')
        seen.add(key)
        if raw[:1] in (b'{', b'['):
            try:
                decoded = json.loads(raw)
            except (ValueError, UnicodeError):
                return asdict(ref)
            def walk(item):
                if type(item) is dict:
                    if set(item) == {'sha256', 'size_bytes', 'kind'}:
                        retain(item)
                    else:
                        for child in item.values():
                            walk(child)
                elif type(item) is list:
                    for child in item:
                        walk(child)
            walk(decoded)
        return asdict(ref)

    retain(supervised_ref)
    verification_ref = artifact_ref(supervised['result']['artifact'])
    verification = ledger.artifacts.read_json(verification_ref)
    snapshot = artifact_ref(supervised['code_snapshot'])
    snapshot_body = ledger.artifacts.read_json(snapshot)
    if (not verification['success'] or verification['errors'] or verification['failures'] or verification['skipped']
            or verification['code_snapshot'] != asdict(snapshot)
            or supervised['result']['code_snapshot'] != asdict(snapshot)
            or snapshot_body['manifest'] != code_manifest(ROOT)):
        raise ValueError('verification failed, its snapshot differs, or code changed')
    passed = verification['passed_assertion_ids']
    if len(passed) != len(set(passed)) or len(passed) != verification['tests_run']:
        raise ValueError('every executed assertion needs a unique successful identity')
    review_ref = artifact_ref(preflight['batch_review'])
    review = ledger.artifacts.read_json(review_ref)
    if (review['review_complete_before_repair'] is not True or review['repair_status'] != 'complete_static_verification_ready_for_shared_run'
            or review['repaired_code_manifest_sha256'] != digest(snapshot_body['manifest'])):
        raise ValueError('pre-execution review/repair record does not bind the verified code')
    validate_review_support(review, trials.artifacts, batch)
    if (sorted(passed) != preflight['expected_assertion_ids']
            or preflight['required_existing_assertion_ids'] != baseline_assertions(trials.artifacts, batch)
            or not set(preflight['required_existing_assertion_ids']) <= set(passed)
            or verification['engineering_metric_errors']):
        raise ValueError('complete prior/new assertion population or metric validation differs')
    for module_name, metrics in verification['engineering_metrics'].items():
        validate_engineering_metrics(module_name, metrics, passed)
    state = trials.state()
    by_family = {r['family']: r for r in registrations}
    by_member = {m['family']: m for m in members}
    for member in members:
        attempt, trial = state['attempts'][member['attempt_id']], state['trials'][member['trial_id']]
        registration = by_family[member['family']]
        if (attempt['status'] != 'succeeded' or attempt['trial_id'] != member['trial_id']
                or attempt['family'] != member['family'] or trial['family'] != member['family']
                or trial['configuration'] != configuration or trial['code_hash'] != digest(snapshot_body['manifest'])
                or trial['data_hashes'] != {'independent_golden': registration['golden']['sha256']}
                or trial['stage'] != 'engineering' or trial['fold_version'] != 'no-market-fit'
                or trial['target_version'] != batch['id'] or attempt['cpu_reservation_seconds'] != cpu_limit
                or attempt['resource_basis'] != 'observed' or asdict(supervised_ref) not in attempt['result_artifacts']
                or any(attempt[k] != supervised[k] for k in ('cpu_seconds', 'wall_seconds', 'peak_rss_bytes'))):
            raise ValueError('trial membership, successful finalization, resource charge or output evidence differs')

    # Validate presentation inputs and scope before committing any evidence.
    scope = Scope.load(ROOT.parent / 'planning/trading-model')
    ledger.audit(scope)
    checkpoint_path, conformance_path = ROOT / 'reports/current-checkpoint.json', ROOT / 'reports/conformance-audit.json'
    checkpoint, conformance = json.loads(checkpoint_path.read_bytes()), json.loads(conformance_path.read_bytes())
    if type(checkpoint) is not dict or type(conformance) is not dict:
        raise ValueError('checkpoint and conformance presentation inputs must be JSON objects')
    reports, report_payloads, owner_updates = {}, {}, {}
    for spec in specs:
        prefix, family, approved_modules = spec['prefix'], spec['family'], spec['test_modules']
        registration = by_family[family]
        source_ref = artifact_ref(registration['source_cases'])
        original_by_id, literals, bindings, clauses = case_contract(ledger.artifacts, registration, spec)
        mapping = preflight['coverage'][prefix]
        coverage_ref = artifact_ref(mapping['artifact'])
        coverage = ledger.artifacts.read_json(coverage_ref)
        if mapping['approved_modules'] != list(approved_modules):
            raise ValueError('immutable case or approved module mapping differs')
        modules = tuple(m + '.' for m in approved_modules)
        family_assertions = sorted(a for a in passed if a.startswith(modules))
        if family_assertions != mapping['static_assertion_ids'] or not family_assertions:
            raise ValueError('all and only the predeclared family methods must actually pass')
        validate_coverage(coverage, spec, original_by_id, literals, bindings, clauses, family_assertions)
        retained_inputs = retain_mapping_inputs(trials.artifacts, coverage, registration, spec, batch, batch_path)
        if any(mapping[k] != retained_inputs[k] for k in retained_inputs):
            raise ValueError('retained mapping source artifacts differ at attachment')
        cases = []
        for case in coverage['cases']:
            cases.append({'case_id': case['case_id'], 'frozen_literal_case': literals[case['case_id']],
                          'source_cases_as_prepared': [original_by_id[source] for source in case['source_case_ids']],
                          'partial_assertion_ids': sorted(case['assertion_ids']), 'remaining': case['remaining'],
                          'frozen_vector_assertions_passed': True, 'whole_source_or_phase_closure': False})
        report = {
            'kind': 'partial_engineering_family_evidence', 'family': family, 'batch_id': batch['id'],
            'recorded_at': verification['started_at'], 'scope_version': scope.version,
            'shared_execution_id': supervised['shared_execution_id'], 'member': by_member[family],
            'verification': asdict(verification_ref), 'code_snapshot': asdict(snapshot),
            'supervised': asdict(supervised_ref), 'registration': registration,
            'case_mapping': asdict(coverage_ref), 'batch_review': asdict(review_ref),
            'script': preflight['recorder'], 'cases': cases, 'assertion_ids': family_assertions,
            'source_case_mapping': coverage['source_case_mapping'],
            'source_dispositions': coverage['source_dispositions'], 'extra_requirements': coverage['extra_requirements'],
            'additional_assertion_ids': coverage['additional_assertion_ids'],
            'engineering_metrics': {module: verification['engineering_metrics'][module] for module in approved_modules
                                    if module in verification['engineering_metrics']},
            'tests_passed': len(family_assertions), 'combined_tests_passed': verification['tests_run'],
            'resources': {k: supervised[k] for k in ('cpu_seconds', 'wall_seconds', 'peak_rss_bytes')},
            'resource_accounting': registration['shared_verification'], 'remaining': coverage['remaining'],
            'whole_unit_definition_closure': False, 'phase_p5_consumer_integration_complete': False,
            'market_tape_reads': 0, 'economic_runs': 0,
        }
        report_ref = ledger.artifacts.put_json(report, kind='implementation_review')
        reports[prefix] = asdict(report_ref)
        report_payloads[prefix] = {'artifact': asdict(report_ref), **report}
        for owner in registration['scope_ids']:
            current = owner_updates.setdefault(owner, {field: [] for field in LIST_FIELDS})
            additions = {
                'reference_and_code_artifacts': [asdict(snapshot), registration['protocol'], registration['golden']],
                'verification_artifacts': [asdict(verification_ref)],
                'review_artifacts': [asdict(report_ref), asdict(review_ref), asdict(source_ref)],
                'assertion_ids': family_assertions,
            }
            for field, values in additions.items():
                current[field] = list({digest(v): v for v in [*current[field], *values]}.values())
            current.update(engineering_state='in_progress',
                reason='Registered finite engineering assertions passed in one shared supervised execution after the full review and one consolidated repair pass; source, data, consumer and economic closure remains open.',
                next_action='Continue remaining source and consumer work, retaining missing-data and future-time dependencies.')
    attachment_key = 'engineering-batch:' + batch['id'] + ':' + supervised['shared_execution_id']
    # This append-only event is the durable attachment receipt. Identical retries
    # return its existing hash; a different payload under the same key fails.
    transaction = ledger.update(owner_updates, reason=REASON, append_fields=LIST_FIELDS, attachment_key=attachment_key)
    receipt = {'attachment_key': attachment_key, 'transaction': transaction, 'reports': reports,
               'supervised': asdict(supervised_ref), 'verification': asdict(verification_ref)}
    try:
        atomic_json(ROOT / f'reports/engineering-attachment-{supervised["shared_execution_id"]}.json', receipt)
        for spec in specs:
            atomic_json(package_path(spec['case_report_path']), report_payloads[spec['prefix']])
        checkpoint.update(ledger.audit(scope))
        checkpoint.update(recorded_at=verification['started_at'], latest_verification=asdict(verification_ref),
                          latest_engineering_batch={'batch_id': batch['id'], 'families': reports})
        conformance.update(verification=asdict(verification_ref), code_snapshot=asdict(snapshot),
                           engineering_batch_references={**conformance.get('engineering_batch_references', {}), batch['id']: reports})
        atomic_json(checkpoint_path, checkpoint)
        atomic_json(conformance_path, conformance)
    except Exception as exc:
        print(json.dumps({**receipt, 'attachment_committed': True, 'presentation_error': f'{type(exc).__name__}: {exc}',
                          'recovery': 'Rerun this recorder with the same immutable summary; no tests are rerun.'}, indent=2))
        return 2
    print(json.dumps({**receipt, 'retained_artifacts': len(seen), 'combined_tests_passed': verification['tests_run'],
                      'engineering': checkpoint['engineering'], 'definition_reviewed': checkpoint['definition_reviewed'],
                      'evaluation': checkpoint['evaluation']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
