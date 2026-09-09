# Consolidated review of the current implementation

The user requested one complete review pass followed by one consolidated repair
pass. All 71 current Python implementation files (9,344 lines) were read before
any repair in this batch. Code remained frozen at
`d151aa3fa99d5fe10da0e06731b99c1cae3c79b1b63cc44e702ebedb37192dbe`.
The existing full suite passed 217 tests. This was the baseline, not evidence that
the broader B00–B10 program was implemented or validated.

`reports/batch-review-before.json` links the immutable baseline, reproduction
script, observations, and supplemental checks. Temporary synthetic journals and
fixtures were used; original data and planning documents were unchanged. No
economic evaluation or live order occurred. The supplemental model checks are
small synthetic engineering fits, not market model selection.

## Findings and required behavior, frozen before repair

| Case | Confirmed finding | Required result |
|---|---|---|
| R01 | Low Decimal precision rejects a large integral count. | Integral quantity validation is independent of caller precision. |
| R02 | `known_at` can precede a supplied computation/publication. | Relevant availability clocks cannot be bypassed by choosing another basis. |
| R03 | A valid JSON number such as `1e400` bypasses finite-payload validation. | Overflow and ambiguous duplicate keys are rejected at the common-message boundary. |
| R04 | Mutable role, candidate, reason, and lifecycle collections change immutable objects. | Versioned common inputs retain immutable collections, including nested records. |
| R05 | Compiled graph ports/edges can change under the same version. | The compiled graph is immutable. |
| R06a | Candidate selection mixes provider/venue namespaces with the same raw ID. | Candidate cuts identify the full instrument namespace. |
| R06b | An object can be admitted with an earlier availability after a candidate cut. | Publication frontiers and candidate snapshots are durable and atomic. |
| R07 | A late older bar replaces a newer observation cut. | Older bar cuts do not become the current bar. |
| R08 | Unpriced edge trades yield apparently complete, substituted opens/closes. | Edge prices remain unknown; price coverage stays incomplete while volume is retained. |
| R09 | Activity-bar boundaries disappear from the availability frontier on restart. | Both empty and nonempty boundary clocks survive restart. |
| R10 | TPO includes a boundary trade but does not count its current bracket. | The opportunity count follows the same inclusive cut as visits. |
| R11 | Another instrument's correction enters a bar through its replacement time. | Correction lineage is instrument-specific on both branches. |
| R12 | A contingent child can use another instrument or a terminal parent. | A child requires a matching active parent or actual matching position. |
| R13 | A sell limit marked `protective_stop` is counted as protection. | Protective roles require a supported stop order type. |
| R14a | Dispatch and broker updates can regress behind durable gate events. | The gate enforces a durable availability frontier. |
| R14b | A pre-dispatch flat snapshot can release a reservation. | Terminal release requires broker observations after dispatch. |
| R15a | Unsorted same-time source order changes the columnar standing quote. | Source ordering is validated before the optimized path is admitted. |
| R15b | Caller Arrow buffers can change a path under one version. | Paths own immutable buffers and include their content in identity. |
| R16 | A ready worker result bypasses an exceeded wall budget. | Ready results obey the same resource deadline. |
| R17 | Mutating fitted frequency cuts changes predictions under one model ID. | Fitted bins are immutable. |
| R17b | A contradictory fitted artifact with the same ID is silently discarded. | Conflicting fitted lineage is rejected. |
| R18 | The prior audit lacks one catalog profile; nomination fails before recording an attempt. | Missing evidence stays explicit, and preflight failure is recorded. |
| R21a | A failed compact batch leaves consumable partial state. | A failed projection requires restart and cannot publish a manifest. |
| R21b | Retrying a physical source part doubles its trade volume. | Repeated physical parts cannot enter the projection twice. |
| R22 | A correction reuses another legitimate print as replacement. | A replacement has a new source identity. |
| R23 | Online VWAP mixes contracts and ignores changed duplicate content. | Online and literal instrument/content rules agree through restart. |
| R24 | Drawdown omits the standing liquidation quote at entry. | Marked loss includes initial side-correct liquidation value. |

R17's first inspected held-out observation stayed in the same bin. The retained
supplement checks the entire fixed held-out set and demonstrates four changed
predictions; the original non-discriminating observation was not overwritten.
R02's completion-before-input example remains recorded separately from the
confirmed availability-bypass defect. The required max-input/completion/
confirmation rule remains the governing derived-availability definition.

The missing R18 profile is the normalized event calendar with `symbol: null` and
an observed microsecond timestamp field. The three prior sampled files contain
the combined, earnings, and FOMC signatures, which do not provide that profile's
golden row. A fixture for that schema is not evidence of a real acquired prefix.

Potential issues without a demonstrated violation (such as ordering arbitrary
date-group labels, explicitly unsupported retirement adapters, and future
production-scale implementations) are not relabeled as repaired defects.

## Consolidated repair and verification

The 27 confirmed cases were repaired together. The first complete verification
passed 245 of 247 methods and found two integration errors: competing refusal
records used an unnecessary second compare-and-swap, and a worker test read
separately published telemetry before it arrived. Both were corrected together;
the failed run is retained in [the first report](../reports/batch-review-first-verification.json).

The final [complete verification](../reports/batch-review-verification.json)
passed all 247 methods, with zero failures, errors or skips, on unchanged code.
It used 26.39 CPU seconds, 56.22 wall seconds and 156.96 MiB peak RSS. The 30
new methods below cover the 27 confirmed cases, including restart, concurrent
admission and positive counterexamples. The repair is not described as an
unbroken first-pass success.

The acquired [Arrow audit](../reports/f01-arrow-prefixes.json) completed 21 of
22 profiles: 61 rows and 686 prior-field comparisons matched with zero sampled
profile failures. Overall success remains false because the 22nd profile lacks
a prior golden row. Its actual code snapshot precedes the two integration
follow-ups; the evidence remains attached to that exact snapshot. The original
unregistered nomination failure is [recorded retrospectively](../reports/f01-arrow-preflight-failure.json),
with unknown usage charged conservatively and no claim of preregistration.

Old bar/activity/VWAP checkpoints and compact venue identities require explicit
replay after their format changes. Native decoder identity remains
`mbp-literal-v4`. Wider/native atomic admission, domain semantics, complete
source/phase review, market prediction, economics and future confirmation remain
open.

## Executed closure matrix

All names below are in `tests.test_batch_review` and occur in the passing
artifact. R18 closes error accounting; its missing data prerequisite remains.

| Case | Executed method(s) |
|---|---|

| R01 | `FoundationReviewTests.test_integral_quantities_are_independent_of_decimal_precision` |
| R02 | `FoundationReviewTests.test_availability_cannot_bypass_supplied_publication_or_computation` |
| R03 | `FoundationReviewTests.test_json_overflow_and_duplicate_members_are_rejected_recursively` |
| R04 | `FoundationReviewTests.test_versioned_common_messages_reject_mutable_collection_aliases` |
| R05 | `FoundationReviewTests.test_compiled_graph_cannot_change_ports_edges_or_versioned_attributes` |
| R06a | `ObjectReviewTests.test_candidate_cut_uses_exact_instrument_namespace` |
| R06b | `ObjectReviewTests.test_candidate_frontier_survives_restart_and_blocks_backdated_admission`; `ObjectReviewTests.test_candidate_freeze_rejects_a_concurrent_object_admission` |
| R07 | `MeasurementReviewTests.test_older_bar_cut_cannot_replace_more_current_publication` |
| R08 | `MeasurementReviewTests.test_unpriced_edge_trades_do_not_become_other_prints_or_confirm_pivots` |
| R09 | `MeasurementReviewTests.test_activity_boundaries_survive_restart_even_without_pending_trades` |
| R10 | `MeasurementReviewTests.test_tpo_boundary_visits_and_opportunities_use_the_same_cut` |
| R11 | `MeasurementReviewTests.test_correction_replacement_cannot_cross_bar_instrument_namespace` |
| R12 | `ExecutionReviewTests.test_contingent_exit_requires_matching_live_parent`; `ExecutionReviewTests.test_closed_entry_cannot_be_parent_of_a_later_position_stop` |
| R13 | `ExecutionReviewTests.test_limit_role_string_cannot_manufacture_protective_stop_coverage` |
| R14a | `GateReviewTests.test_dispatch_and_broker_availability_cannot_regress_after_restart` |
| R14b | `GateReviewTests.test_pre_dispatch_snapshot_cannot_release_reservation_but_current_truth_can` |
| R15a | `ExecutionReviewTests.test_columnar_rejects_unordered_ties_then_matches_literal_order` |
| R15b | `ExecutionReviewTests.test_versioned_columnar_path_owns_readonly_content_and_scenario` |
| R16 | `WorkerReviewTests.test_ready_worker_results_still_obey_wall_budget` |
| R17 | `LearnedIdentityReviewTests.test_fitted_frequency_bins_and_training_membership_are_immutable` |
| R17b | `LearnedIdentityReviewTests.test_contradictory_fitted_identity_is_not_silently_removed` |
| R18 | `RawProjectionReviewTests.test_missing_golden_profile_is_reported_without_inventing_a_prefix`; `RawProjectionReviewTests.test_audit_preflight_errors_are_recorded_as_failed_attempts` |
| R21a | `RawProjectionReviewTests.test_failed_projection_cannot_publish_partial_state_or_continue` |
| R21b | `RawProjectionReviewTests.test_repeated_physical_part_cannot_double_volume` |
| R22 | `MeasurementReviewTests.test_correction_requires_new_replacement_identity_and_failure_is_atomic` |
| R23 | `MeasurementReviewTests.test_online_vwap_rejects_mixed_contracts_and_changed_identity_after_restart` |
| R24 | `ExecutionReviewTests.test_marked_drawdown_includes_standing_liquidation_at_entry` |
