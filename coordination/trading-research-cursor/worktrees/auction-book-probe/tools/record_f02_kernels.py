"""Attach the completed fixed-kernel verification without promoting whole units."""

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path

from trading_research.operations.artifacts import artifact_ref, code_manifest, digest
from trading_research.operations.ledger import Ledger
from trading_research.operations.scope import Scope
from trading_research.operations.trials import TrialRegistry


ROOT = Path(__file__).resolve().parents[1]


def main():
    ledger = Ledger(ROOT / 'evidence')
    trials = TrialRegistry(ROOT / 'evidence/trials')
    summary = json.loads((ROOT / 'reports/f02-kernel-verification-dccbfc69d612.json').read_text())
    verification_ref = artifact_ref(summary['verification']['artifact'])
    verification = ledger.artifacts.read_json(verification_ref)
    snapshot = artifact_ref(verification['code_snapshot'])
    assert summary['success'] and verification['success'] and verification['tests_run'] == 264
    assert ledger.artifacts.read_json(snapshot)['manifest'] == code_manifest(ROOT)
    new_ids = sorted(v for v in verification['passed_assertion_ids'] if v.startswith('tests.test_payoffs_registry.'))
    assert len(new_ids) == 17
    methods = {v.rsplit('.', 1)[-1]: v for v in new_ids}
    registry_tests = sorted(v for v in new_ids if '.RegistryLifetimeTests.' in v)
    case_methods = {
        'F02-01': ['test_definition_term_conflicts_missing_support_and_public_constructor_fail_closed'],
        'F02-02': ['test_definition_term_conflicts_missing_support_and_public_constructor_fail_closed'],
        'F02-03': ['test_nq_es_tick_cash_matches_frozen_golden_and_existing_one_mini_arithmetic'],
        'F02-04': ['test_nq_es_tick_cash_matches_frozen_golden_and_existing_one_mini_arithmetic'],
        'F02-05': ['test_reused_id_retirement_delayed_knowledge_and_json_restart'],
        'F02-06': ['test_late_correction_cannot_reactivate_and_old_kernel_stays_frozen', 'test_fixed_grid_literal_compiled_parity_and_late_fixing_revision'],
        'F02-07': ['test_raw_deletion_binds_provider_lifetime_clocks_and_unused_fields'],
        'F02-08': [v.rsplit('.', 1)[-1] for v in registry_tests],
        'F02-09': ['test_immutable_contract_terms_and_explicit_exact_types'],
        'F02-10': ['test_am_pm_fixing_identity_trade_deadline_and_revised_payment_are_distinct'],
        'F02-11': [],
        'F02-12': ['test_am_pm_fixing_identity_trade_deadline_and_revised_payment_are_distinct', 'test_american_intrinsic_available_but_early_payment_schedule_is_not_invented'],
        'F02-13': ['test_premium_threshold_and_signed_or_bounded_grids'],
        'F02-14': ['test_adjusted_share_cash_basket_and_put_delivery_signs'],
        'F02-15': ['test_late_correction_cannot_reactivate_and_old_kernel_stays_frozen'],
        'F02-16': ['test_marks_are_distinct_from_fixings_and_unavailable_inputs_emit_no_result', 'test_adjusted_share_cash_basket_and_put_delivery_signs'],
        'F02-17': ['test_future_delivery_uses_exact_underlier_and_does_not_round_fixing_to_future_tick'],
        'F02-18': [],
        'F02-19': ['test_exact_inverse_conditional_mean_refusal_and_fixed_expiry_time_sign'],
        'F02-20': ['test_exact_inverse_conditional_mean_refusal_and_fixed_expiry_time_sign'],
        'F02-21': ['test_raw_deletion_binds_provider_lifetime_clocks_and_unused_fields', 'test_definition_term_conflicts_missing_support_and_public_constructor_fail_closed'],
        'F02-22': ['test_fx_units_availability_and_informational_mini_conversion'],
        'F02-23': [],
    }
    opening = json.loads((ROOT / 'reports/opening-minimum-gates.json').read_text())
    cases = []
    for case in opening['retrospective_cases']:
        key = case['case'].split()[0]
        added = [methods[m] for m in case_methods[key]]
        prior = case['assertion_ids']
        assert set(prior + added).issubset(verification['passed_assertion_ids'])
        cases.append({'case': key, 'expected': case['expected'], 'prior_assertion_ids': prior,
                      'new_partial_assertion_ids': added, 'whole_case_verified': False,
                      'basis': 'Bounded literal/synthetic cases; dated/native/all-consumer closure is separate.'})
    supervised_ref = artifact_ref(summary['artifact'])
    supervised = trials.artifacts.read_json(supervised_ref)
    retained = {}
    for name, ref in [('supervised', supervised_ref), *[(name, artifact_ref(supervised['configuration'][name]))
                       for name in ('protocol', 'golden', 'review', 'supervisor')]]:
        retained[name] = asdict(ledger.artifacts.put_bytes(trials.artifacts.read(ref), kind=ref.kind))
    script = ledger.artifacts.put_bytes(Path(__file__).read_bytes(), kind='evidence_assembly_script')
    scope = Scope.load(ROOT.parent / 'planning/trading-model')
    report = {'kind': 'f02_partial_kernel_case_evidence', 'recorded_at': datetime.now(timezone.utc).isoformat(),
              'scope_version': scope.version, 'verification': asdict(verification_ref), 'code_snapshot': asdict(snapshot),
              'artifacts': retained, 'script': asdict(script), 'cases': cases, 'new_assertion_ids': new_ids,
              'combined_tests_passed': 264, 'verification_attempts': 1, 'economic_runs': 0,
              'resources': {k: summary[k] for k in ('cpu_seconds', 'wall_seconds', 'peak_rss_bytes')},
              'whole_unit_definition_closure': False, 'historical_option_cohort_admitted': False,
              'phase_p5_consumer_integration_complete': False,
              'remaining': ['Dated/native option identities, calendar/style/deliverable joins and unsupported series.',
                            'Explicit reinstatement and overlapping lifetime-boundary correction.',
                            'Early exercise payment schedules, full model fair values and Greeks.',
                            'Original/provider/curated/compiled same-input cost and quality comparisons.',
                            'Affected O/P/X replay, eligible economics and prospective phases.']}
    ref = ledger.artifacts.put_json(report, kind='implementation_review')
    (ROOT / 'reports/f02-kernel-case-coverage.json').write_text(json.dumps({'artifact': asdict(ref), **report}, indent=2, sort_keys=True) + '\n')
    def extend(old, values):
        return list({digest(v): v for v in [*old, *values]}.values())
    state = ledger.current()
    changes = {}
    for owner in ('F02', 'F02.PAYOFF', 'B00.1', 'B01.5'):
        old = state[owner]
        changes[owner] = {'engineering_state': 'in_progress',
            'reference_and_code_artifacts': extend(old['reference_and_code_artifacts'], [asdict(snapshot), retained['protocol'], retained['golden']]),
            'verification_artifacts': extend(old['verification_artifacts'], [asdict(verification_ref)]),
            'review_artifacts': extend(old['review_artifacts'], [asdict(ref), retained['review']]),
            'assertion_ids': sorted(set(old['assertion_ids']) | set(new_ids)),
            'reason': 'Exact registry/payoff reference batch passed 17 new and 247 existing methods after one complete review and consolidated repair. Broader source, dated cohort and phase closure remains open.',
            'next_action': 'Continue opening source/case and data admission work; add separately registered curated/provider comparisons and P5 consumer integration when their prerequisites are satisfied.'}
    transaction = ledger.update(changes, reason='Attach F02 fixed-kernel evidence; preserve independent incomplete unit/phase and unrun market statuses.')
    checkpoint = json.loads((ROOT / 'reports/current-checkpoint.json').read_text())
    checkpoint.update(ledger.audit(scope))
    checkpoint.update(recorded_at=report['recorded_at'], latest_verification=asdict(verification_ref), latest_f02_kernels=asdict(ref))
    (ROOT / 'reports/current-checkpoint.json').write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + '\n')
    conformance = json.loads((ROOT / 'reports/conformance-audit.json').read_text())
    conformance.update(verification=asdict(verification_ref), code_snapshot=asdict(snapshot), f02_kernel_reference=asdict(ref))
    (ROOT / 'reports/conformance-audit.json').write_text(json.dumps(conformance, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'artifact': asdict(ref), 'transaction': transaction,
                      'engineering': checkpoint['engineering'], 'definition_reviewed': checkpoint['definition_reviewed'],
                      'evaluation': checkpoint['evaluation'], 'new_assertions': len(new_ids)}, indent=2))


if __name__ == '__main__':
    main()
