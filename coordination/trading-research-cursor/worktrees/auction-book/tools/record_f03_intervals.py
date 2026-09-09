"""Attach the completed F03 reference batch without promoting whole-unit closure."""

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
    summary = json.loads((ROOT / 'reports/f03-interval-verification-731dc74edd41.json').read_text())
    verification_ref = artifact_ref(summary['verification']['artifact'])
    verification = ledger.artifacts.read_json(verification_ref)
    snapshot = artifact_ref(verification['code_snapshot'])
    assert summary['success'] and verification['success'] and verification['tests_run'] == 288
    assert ledger.artifacts.read_json(snapshot)['manifest'] == code_manifest(ROOT)
    new_ids = sorted(v for v in verification['passed_assertion_ids'] if
                     v.startswith(('tests.test_interval_graph.', 'tests.test_timer_journal.')))
    assert len(new_ids) == 24
    methods = {v.rsplit('.', 1)[-1]: v for v in new_ids}
    case_methods = {
        'F03-01': ['test_calendar_rows_have_stable_identity_and_frozen_known_time_queries',
                   'test_public_cash_source_views_cannot_mutate_frozen_versions', 'test_malformed_published_cash_rows_fail_at_ingestion'],
        'F03-02': ['test_summer_ny_fixed_est_and_nine_vs_nine_thirty_match_frozen_utc', 'test_dst_gap_fold_and_non_24_hour_calendar_days'],
        'F03-03': ['test_sunday_midnight_interval_keeps_declared_trading_date_and_last_nanosecond'],
        'F03-04': ['test_compiled_intersections_match_literal_and_preserve_inactive_gaps', 'test_literal_source_clock_variants_and_all_endpoint_queries'],
        'F03-05': ['test_weekly_dated_union_keeps_a_holiday_and_short_session', 'test_dst_gap_fold_and_non_24_hour_calendar_days'],
        'F03-06': ['test_session_cutoff_and_eligibility_do_not_depend_on_opening_prints', 'test_cash_and_venue_clocks_reject_invalid_types_and_margins'],
        'F03-07': ['test_no_market_tick_is_needed_and_boundary_order_is_deterministic', 'test_boundary_order_empty_intersections_and_duplicate_reset_owners',
                   'test_separate_owners_share_clock_but_not_state_or_logical_identity'],
        'F03-08': ['test_abrupt_process_exit_before_and_after_commit_is_restart_safe', 'test_reducer_failure_rolls_back_state_application_and_clock_together',
                   'test_initial_late_install_catches_up_at_available_cut_and_duplicate_is_inert'],
        'F03-09': ['test_future_calendar_change_replaces_pending_timer_and_keeps_old_history', 'test_removed_unapplied_action_can_be_explicitly_reintroduced'],
        'F03-10': ['test_past_revision_reconciles_at_installation_without_retroactive_reset',
                   'test_calendar_revision_never_repeats_an_already_committed_logical_reset'],
        'F03-11': ['test_session_cutoff_and_eligibility_do_not_depend_on_opening_prints', 'test_no_market_tick_is_needed_and_boundary_order_is_deterministic'],
        'F03-12': ['test_summer_ny_fixed_est_and_nine_vs_nine_thirty_match_frozen_utc', 'test_literal_source_clock_variants_and_all_endpoint_queries'],
        'F03-13': ['test_summer_ny_fixed_est_and_nine_vs_nine_thirty_match_frozen_utc', 'test_invalid_public_clock_types_and_unknown_timezone_bytes_fail'],
        'F03-14': ['test_literal_source_clock_variants_and_all_endpoint_queries'],
        'F03-15': ['test_literal_source_clock_variants_and_all_endpoint_queries', 'test_dst_gap_fold_and_non_24_hour_calendar_days'],
        'F03-16': ['test_boundary_order_empty_intersections_and_duplicate_reset_owners', 'test_no_market_tick_is_needed_and_boundary_order_is_deterministic'],
        'F03-17': [],
        'F03-18': ['test_literal_source_clock_variants_and_all_endpoint_queries'],
        'F03-19': [], 'F03-20': [], 'F03-21': [],
        'F03-22': ['test_summer_ny_fixed_est_and_nine_vs_nine_thirty_match_frozen_utc'],
        'F03-23': ['test_compiled_intersections_match_literal_and_preserve_inactive_gaps',
                   'test_literal_source_clock_variants_and_all_endpoint_queries', 'test_graph_intervals_and_source_dependencies_are_immutable'],
        'F03-24': [],
    }
    source_report = json.loads((ROOT / 'reports/f03-source-cases.json').read_text())
    cases = [{**case, 'new_partial_assertion_ids': [methods[m] for m in case_methods[case['id']]],
              'whole_case_verified': False,
              'basis': 'Fixed calendar/reference state cases only; indicator, dated-data and all-consumer closure remains separate.'}
             for case in source_report['cases']]
    seen = set()
    def retain(ref):
        ref = artifact_ref(ref) if isinstance(ref, dict) else ref
        if ref.sha256 in seen:
            return asdict(ref)
        payload = trials.artifacts.read(ref)
        copied = ledger.artifacts.put_bytes(payload, kind=ref.kind)
        assert copied == ref
        seen.add(ref.sha256)
        if payload[:1] in (b'{', b'['):
            try:
                value = json.loads(payload)
            except (ValueError, UnicodeError):
                return asdict(ref)
            def walk(v):
                if type(v) is dict:
                    if set(v) == {'sha256', 'size_bytes', 'kind'}:
                        retain(v)
                    else:
                        for child in v.values():
                            walk(child)
                elif type(v) is list:
                    for child in v:
                        walk(child)
            walk(value)
        return asdict(ref)
    supervised_ref = artifact_ref(summary['artifact'])
    supervised = trials.artifacts.read_json(supervised_ref)
    retained = {'supervised': retain(supervised_ref)}
    for name in ('protocol', 'golden', 'review', 'supervisor', 'source_cases'):
        retained[name] = retain(supervised['configuration'][name])
    script = ledger.artifacts.put_bytes(Path(__file__).read_bytes(), kind='evidence_assembly_script')
    scope = Scope.load(ROOT.parent / 'planning/trading-model')
    report = {'kind': 'f03_partial_interval_timer_evidence', 'recorded_at': datetime.now(timezone.utc).isoformat(),
              'scope_version': scope.version, 'verification': asdict(verification_ref), 'code_snapshot': asdict(snapshot),
              'artifacts': retained, 'script': asdict(script), 'cases': cases, 'new_assertion_ids': new_ids,
              'combined_tests_passed': 288, 'new_tests_passed': 24, 'verification_attempts': 1,
              'review_findings_collected': 12, 'consolidated_repair_passes': 1,
              'economic_runs': 0, 'market_tape_reads': 0, 'source_findings_reviewed': 74,
              'static_original_files': 47, 'visually_inspected_pdf_pages': 41,
              'resources': {k: summary[k] for k in ('cpu_seconds', 'wall_seconds', 'peak_rss_bytes')},
              'whole_unit_definition_closure': False, 'historical_venue_cohort_admitted': False,
              'phase_p5_consumer_integration_complete': False,
              'remaining': ['Every source-specific indicator variant and unresolved imported/private source definition.',
                            'Dated futures venue, firm and platform boundaries and eligibility joins.',
                            'Actual print coverage, formation data and prior-session/weekly/monthly reconciliation.',
                            'Measured original/provider/compiled cost comparisons on equivalent eligible inputs.',
                            'Complete runtime and C/L/R/P consumer integration; external action delivery remains its own contract.',
                            'Eligible economic comparisons and prospective phases.']}
    ref = ledger.artifacts.put_json(report, kind='implementation_review')
    (ROOT / 'reports/f03-interval-case-coverage.json').write_text(json.dumps({'artifact': asdict(ref), **report}, indent=2, sort_keys=True) + '\n')
    def extend(old, values):
        return list({digest(v): v for v in [*old, *values]}.values())
    state = ledger.current()
    changes = {}
    for owner in ('F03', 'F03.SESSION_CASES', 'B00.1'):
        old = state[owner]
        changes[owner] = {'engineering_state': 'in_progress',
            'reference_and_code_artifacts': extend(old['reference_and_code_artifacts'], [asdict(snapshot), retained['protocol'], retained['golden']]),
            'verification_artifacts': extend(old['verification_artifacts'], [asdict(verification_ref)]),
            'review_artifacts': extend(old['review_artifacts'], [asdict(ref), retained['review'], retained['source_cases']]),
            'assertion_ids': sorted(set(old['assertion_ids']) | set(new_ids)),
            'reason': 'F03 fixed interval/timer reference batch passed 24 new and 264 existing methods after one complete review and consolidated repair. Broader source, dated cohort and all-consumer closure remains open.',
            'next_action': 'Continue independent reference/admission work and separately registered source/consumer integration; preserve historical venue/account and exact E0 parent dependencies.'}
    transaction = ledger.update(changes, reason='Attach F03 frozen interval/durable internal timer evidence; preserve incomplete whole-unit phases and unrun market evaluations.')
    checkpoint = json.loads((ROOT / 'reports/current-checkpoint.json').read_text())
    checkpoint.update(ledger.audit(scope))
    checkpoint.update(recorded_at=report['recorded_at'], latest_verification=asdict(verification_ref), latest_f03_intervals=asdict(ref))
    (ROOT / 'reports/current-checkpoint.json').write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + '\n')
    conformance = json.loads((ROOT / 'reports/conformance-audit.json').read_text())
    conformance.update(verification=asdict(verification_ref), code_snapshot=asdict(snapshot), f03_interval_reference=asdict(ref))
    (ROOT / 'reports/conformance-audit.json').write_text(json.dumps(conformance, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'artifact': asdict(ref), 'transaction': transaction, 'retained_artifacts': len(seen),
                      'engineering': checkpoint['engineering'], 'definition_reviewed': checkpoint['definition_reviewed'],
                      'evaluation': checkpoint['evaluation'], 'new_assertions': len(new_ids)}, indent=2))


if __name__ == '__main__':
    main()
