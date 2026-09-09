"""Attach exact F04 synthetic evidence without promoting complete source phases."""
from dataclasses import asdict
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
from trading_research.operations.artifacts import artifact_ref,code_manifest,digest
from trading_research.operations.ledger import Ledger
from trading_research.operations.scope import Scope
from trading_research.operations.trials import TrialRegistry
ROOT=Path(__file__).resolve().parents[1]
CASE_METHODS={
 'F04-01':['test_future_suffix_correction_and_restart_preserve_past_cut','test_zero_endpoint_is_expired_and_cpi_revision_preserves_past_decision_view'],
 'F04-02':['test_actual_compute_is_not_charged_twice_and_confirmation_is_not_backdated'],
 'F04-03':['test_confirmed_object_has_immutable_revision_and_no_backdating'],
 'F04-04':['test_insertion_permutations_and_future_suffix_deletion_preserve_prefix_hashes'],
 'F04-05':['test_golden_ties_and_registered_opposite_order_scenarios'],
 'F04-06':['test_equal_watermark_is_exclusive_and_receipt_is_causal','test_stalled_options_does_not_block_trade_domain_or_share_ack_cursor'],
 'F04-07':['test_repeatable_peek_reopen_before_after_ack_and_configuration_identity','test_duplicate_event_idempotence_and_id_and_source_sequence_conflicts','test_correction_uses_actual_new_receipt_and_late_rejection_is_atomic','test_acknowledgement_receipt_prevents_historical_cursor_regression_after_restart'],
 'F04-08':['test_byte_bound_exact_fit_and_failed_ack_leave_next_batch_intact','test_record_bound_counts_watermarks_and_acknowledged_history','test_oversized_tie_is_never_split_or_consumed'],
 'F04-09':['test_oi_trade_and_unused_field_propagate_to_exact_descendants'],
 'F04-10':['test_same_value_new_source_lineage_recomputes_dependent_forecast','test_evidence_only_edge_is_invalidated_by_lineage_or_optional_outage','test_mutable_source_payload_and_request_lineage_are_rejected_before_registration'],
 'F04-11':['test_missing_mandatory_exposure_allows_optional_decision_and_independent_cvd','test_stalled_options_does_not_block_trade_domain_or_share_ack_cursor'],
 'F04-12':['test_fifo_deadline_and_cost_policies_have_explicit_priority_and_endpoint_order','test_worker_poll_applies_registered_cost_policy_and_records_actual_selection'],
 'F04-13':['test_future_cost_is_excluded_and_censored_evidence_uses_registered_fallback','test_bounded_history_identity_retention_and_frozen_nearest_rank_percentiles','test_actual_timed_deterministic_work_has_exact_operations_and_unthresholded_telemetry','test_future_runtime_sample_eviction_cannot_change_an_earlier_cost_to_fallback','test_worker_uses_one_receipt_duration_for_persisted_and_restored_runtime_cost'],
 'F04-14':['test_frozen_cut_completion_latency_original_endpoint_and_restart','test_zero_endpoint_is_expired_and_cpi_revision_preserves_past_decision_view'],
 'F04-15':['test_forecast_cannot_be_published_twice_or_resurrected_after_expiry','test_worker_coalescing_is_per_producer_and_invalid_replacement_is_atomic','test_invalid_or_future_optional_admission_preserves_already_accepted_work'],
 'F04-16':['test_integrity_lanes_are_unconditional_in_both_planning_modes','test_boundary_without_next_tick_and_crash_replays_only_unacknowledged_event'],
 'F04-17':[],'F04-18':[],'F04-19':['test_future_suffix_correction_and_restart_preserve_past_cut'],
 'F04-20':[],'F04-21':[],'F04-22':[],
 'F04-23':['test_full_and_incremental_compare_every_output_lineage_and_operation_at_identical_cuts','test_full_reference_rejects_stale_derived_seed_and_current_lagged_state']}

def main():
 summary=json.loads(Path(sys.argv[1]).read_text());ledger=Ledger(ROOT/'evidence');trials=TrialRegistry(ROOT/'evidence/trials')
 verification_ref=artifact_ref(summary['verification']['artifact']);verification=ledger.artifacts.read_json(verification_ref)
 snapshot=artifact_ref(verification['code_snapshot'])
 assert summary['success'] and verification['success']
 assert ledger.artifacts.read_json(snapshot)['manifest']==code_manifest(ROOT)
 ids=verification['passed_assertion_ids'];new_ids=sorted(i for i in ids if i.startswith(('tests.test_replay_merge.','tests.test_scheduling.','tests.test_f04_contracts.')))
 assert verification['tests_run']==321 and len(new_ids)==33
 def find(method):
  found=[i for i in ids if i.rsplit('.',1)[-1]==method];assert len(found)==1,(method,found);return found[0]
 source=json.loads((ROOT/'reports/f04-source-cases.json').read_text())
 cases=[{**c,'partial_assertion_ids':[find(m) for m in CASE_METHODS[c['id']]],'whole_case_verified':False,
         'basis':'Fixed generic clock/replay/planning assertions only; every source indicator and consumer is a separate closure.'} for c in source['cases']]
 seen=set()
 def retain(ref):
  ref=artifact_ref(ref) if isinstance(ref,dict) else ref
  if ref.sha256 in seen:return asdict(ref)
  try:raw=trials.artifacts.read(ref)
  except FileNotFoundError:raw=ledger.artifacts.read(ref)
  copied=ledger.artifacts.put_bytes(raw,kind=ref.kind);assert copied==ref;seen.add(ref.sha256)
  if raw[:1] in (b'{',b'['):
   try:value=json.loads(raw)
   except (ValueError,UnicodeError):return asdict(ref)
   def walk(v):
    if type(v)is dict:
     if set(v)=={'sha256','size_bytes','kind'}:retain(v)
     else:
      for c in v.values():walk(c)
    elif type(v)is list:
     for c in v:walk(c)
   walk(value)
  return asdict(ref)
 supervised=trials.artifacts.read_json(artifact_ref(summary['artifact']))
 retained={'supervised':retain(summary['artifact'])}
 for name in ('protocol','golden','review','supervisor','source_cases'):retained[name]=retain(supervised['configuration'][name])
 toy={}
 for line in supervised['stdout'].splitlines():
  for marker,key in [('F04_TOY_COMPARISON ','state_comparison'),('F04_ACTUAL_TOY_TIMING ','actual_toy_timing')]:
   if line.startswith(marker):toy[key]=json.loads(line[len(marker):])
 assert set(toy)=={'state_comparison','actual_toy_timing'}
 scope=Scope.load(ROOT.parent/'planning/trading-model')
 report={'kind':'f04_partial_availability_scheduler_evidence','recorded_at':datetime.now(timezone.utc).isoformat(),
  'scope_version':scope.version,'verification':asdict(verification_ref),'code_snapshot':asdict(snapshot),'artifacts':retained,
  'cases':cases,'new_assertion_ids':new_ids,'combined_tests_passed':321,'new_tests_passed':33,
  'verification_attempts':1,'review_findings_collected':10,'consolidated_repair_passes':1,
  'source_findings_reviewed':58,'static_original_files':28,'new_pdf_pages_text_and_visual':6,'reused_pdf_pages':6,
  'script':asdict(ledger.artifacts.put_bytes(Path(__file__).read_bytes(),kind='evidence_assembly_script')),
  'comparisons':toy,'resources':{k:summary[k] for k in ('cpu_seconds','wall_seconds','peak_rss_bytes')},
  'economic_runs':0,'market_tape_reads':0,'whole_unit_definition_closure':False,'phase_p5_consumer_integration_complete':False,
  'remaining':['Full source-specific indicator variants and confirmation rules.','Live receipt distributions and complete historical field/cohort admission.',
   'Shared live incremental payload caching and all-consumer decision/latency comparisons.',
   'Registered economic comparisons and future observations.','Domain consumer idempotent state and external side-effect integration remain separate.']}
 ref=ledger.artifacts.put_json(report,kind='implementation_review')
 (ROOT/'reports/f04-replay-case-coverage.json').write_text(json.dumps({'artifact':asdict(ref),**report},indent=2)+'\n')
 def extend(old,values):return list({digest(v):v for v in [*old,*values]}.values())
 state=ledger.current();changes={}
 for owner in ('F04','F04.SCHEDULER','B00.1'):
  old=state[owner];changes[owner]={'engineering_state':'in_progress',
   'reference_and_code_artifacts':extend(old['reference_and_code_artifacts'],[asdict(snapshot),retained['protocol'],retained['golden']]),
   'verification_artifacts':extend(old['verification_artifacts'],[asdict(verification_ref)]),
   'review_artifacts':extend(old['review_artifacts'],[asdict(ref),retained['review'],retained['source_cases']]),
   'assertion_ids':sorted(set(old['assertion_ids'])|set(new_ids)),
   'reason':'F04 bounded merge and optional scheduling passed 33 new and 288 existing methods after full review and one repair; same-cut toy state parity retained. Whole source, data and consumer phases remain open.',
   'next_action':'Continue canonical transaction, source quality and joined-age work with separately registered source/consumer cases and exact data dependencies.'}
 transaction=ledger.update(changes,reason='Attach F04 exact synthetic replay/scheduling evidence without claiming full source, data, consumer or economic closure.')
 checkpoint=json.loads((ROOT/'reports/current-checkpoint.json').read_text());checkpoint.update(ledger.audit(scope))
 checkpoint.update(recorded_at=report['recorded_at'],latest_verification=asdict(verification_ref),latest_f04_replay=asdict(ref))
 (ROOT/'reports/current-checkpoint.json').write_text(json.dumps(checkpoint,indent=2,sort_keys=True)+'\n')
 conformance=json.loads((ROOT/'reports/conformance-audit.json').read_text());conformance.update(verification=asdict(verification_ref),code_snapshot=asdict(snapshot),f04_replay_reference=asdict(ref))
 (ROOT/'reports/conformance-audit.json').write_text(json.dumps(conformance,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'artifact':asdict(ref),'transaction':transaction,'retained_artifacts':len(seen),
  'engineering':checkpoint['engineering'],'definition_reviewed':checkpoint['definition_reviewed'],'evaluation':checkpoint['evaluation'],'new_assertions':len(new_ids)},indent=2))

if __name__=='__main__':main()
