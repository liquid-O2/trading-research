"""Idempotently attach one immutable shared run to exact partial foundation cases."""
from dataclasses import asdict
import json
from pathlib import Path
import sys

from trading_research.operations.artifacts import artifact_ref, code_manifest, digest
from trading_research.operations.ledger import Ledger
from trading_research.operations.scope import Scope
from trading_research.operations.trials import TrialRegistry
from trading_research.verify import validate_engineering_metrics
from verify_f09_f12 import (
    ROOT, SPECS, atomic_json, case_contract, validate_coverage, validate_registrations,
    validate_review_support, retain_mapping_inputs,
)

LIST_FIELDS = ('reference_and_code_artifacts', 'verification_artifacts', 'review_artifacts', 'assertion_ids')
REASON = 'Attach exact F09–F12 partial engineering evidence from one physical supervised execution.'


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
    if configuration['shared_execution_id'] != supervised['shared_execution_id']:
        raise ValueError('shared configuration identity differs')
    registrations = configuration['registrations']
    validate_registrations(trials, registrations)
    members = supervised['members']
    if (len(members) != len(SPECS) or {m['family'] for m in members} != {s[1] for s in SPECS}
            or len({m['attempt_id'] for m in members}) != len(members)
            or len({m['trial_id'] for m in members}) != len(members)):
        raise ValueError('duplicate, missing or extra participating members')
    preflight = configuration['preflight']
    for path, ref in ((Path(__file__), preflight['recorder']),
                      (ROOT / 'tools/verify_f09_f12.py', configuration['supervisor']),
                      (ROOT / 'tools/map_f09_f12.py', preflight['normalizer'])):
        if path.read_bytes() != trials.artifacts.read(artifact_ref(ref)):
            raise ValueError('reviewed orchestration source changed after execution')

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
    if (review['review_complete_before_repair'] is not True or review['consolidated_repair_passes'] != 1
            or review['repair_status'] != 'complete_static_verification_ready_for_shared_run'
            or review['repaired_code_manifest_sha256'] != digest(snapshot_body['manifest'])):
        raise ValueError('pre-execution review/repair record does not bind the verified code')
    validate_review_support(review, trials.artifacts)
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
                or trial['stage'] != 'engineering' or attempt['cpu_reservation_seconds'] != 180
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
    for spec in SPECS:
        prefix, family, *_, approved_modules = spec
        registration = by_family[family]
        source_ref = artifact_ref(registration['source_cases'])
        original_by_id, literals, bindings = case_contract(ledger.artifacts, registration, spec)
        mapping = preflight['coverage'][prefix]
        coverage_ref = artifact_ref(mapping['artifact'])
        coverage = ledger.artifacts.read_json(coverage_ref)
        if mapping['approved_modules'] != list(approved_modules):
            raise ValueError('immutable case or approved module mapping differs')
        modules = tuple(m + '.' for m in approved_modules)
        family_assertions = sorted(a for a in passed if a.startswith(modules))
        if family_assertions != mapping['static_assertion_ids'] or not family_assertions:
            raise ValueError('all and only the predeclared family methods must actually pass')
        validate_coverage(coverage, spec, original_by_id, literals, bindings, family_assertions)
        retained_inputs = retain_mapping_inputs(trials.artifacts, coverage, registration, spec)
        if any(mapping[k] != retained_inputs[k] for k in retained_inputs):
            raise ValueError('retained mapping source artifacts differ at attachment')
        for module_name in approved_modules:
            validate_engineering_metrics(module_name, verification['engineering_metrics'][module_name], passed)
        cases = []
        for case in coverage['cases']:
            cases.append({'case_id': case['case_id'], 'frozen_literal_case': literals[case['case_id']],
                          'source_cases_as_prepared': [original_by_id[source] for source in case['source_case_ids']],
                          'partial_assertion_ids': sorted(case['assertion_ids']), 'remaining': case['remaining'],
                          'whole_case_verified': False})
        report = {
            'kind': 'partial_foundation_reference_evidence', 'family': family,
            'recorded_at': verification['started_at'], 'scope_version': scope.version,
            'shared_execution_id': supervised['shared_execution_id'], 'member': by_member[family],
            'verification': asdict(verification_ref), 'code_snapshot': asdict(snapshot),
            'supervised': asdict(supervised_ref), 'registration': registration,
            'case_mapping': asdict(coverage_ref), 'batch_review': asdict(review_ref),
            'script': preflight['recorder'], 'cases': cases, 'assertion_ids': family_assertions,
            'source_case_mapping': coverage['source_case_mapping'],
            'additional_assertion_ids': coverage['additional_assertion_ids'],
            'engineering_metrics': {module: verification['engineering_metrics'][module] for module in approved_modules},
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
                reason='Registered partial foundation assertions passed in one shared supervised execution after the full review and one consolidated repair pass; source, data, consumer and economic closure remains open.',
                next_action='Continue remaining source and consumer work, retaining missing-data and future-time dependencies.')
    attachment_key = 'foundation-f09-f12:' + supervised['shared_execution_id']
    # This append-only event is the durable attachment receipt. Identical retries
    # return its existing hash; a different payload under the same key fails.
    transaction = ledger.update(owner_updates, reason=REASON, append_fields=LIST_FIELDS, attachment_key=attachment_key)
    receipt = {'attachment_key': attachment_key, 'transaction': transaction, 'reports': reports,
               'supervised': asdict(supervised_ref), 'verification': asdict(verification_ref)}
    try:
        atomic_json(ROOT / f'reports/foundation-attachment-{supervised["shared_execution_id"]}.json', receipt)
        for prefix, report in report_payloads.items():
            atomic_json(ROOT / f'reports/{prefix}-case-coverage.json', report)
        checkpoint.update(ledger.audit(scope))
        checkpoint.update(recorded_at=verification['started_at'], latest_verification=asdict(verification_ref),
                          latest_foundation_extensions=reports)
        conformance.update(verification=asdict(verification_ref), code_snapshot=asdict(snapshot),
                           foundation_extension_references=reports)
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
