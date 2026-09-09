# F10 immutable object and lineage engineering protocol — preregistered engineering contract

Root has reviewed the complete design, all 34 hand-reasoned cases and source consequences. This exact contract is published by the generic registrar before dependent code or tests; source preparation and reviewed drafts remain unchanged.

## Scope and source closure

A deterministic immutable object/geometry, observation and relation registry with indexed historical projections, complete candidate denominators and atomic lineage changes.

Existing foundations/objects.py remains the legacy behavior comparator; an independently written literal append-only fold defines the new typed contract. Intentional representation/state corrections are labeled, not called legacy-output parity.

Typed frozen-candidate and target-binding adapters only. E0 VisitTracker remains unchanged; a synthetic adapter must prove stable visit/version mapping before any later E0 integration. No live generator/runtime activation.

Explicit source clauses: DRF-A07, JXA-22, JFN-04, JFN-11, CRL-19, EXT-007, EXT-085, EXT-086. All25 source cases remain, with9 additional integrity cases. No complete Location-generator or P0–P7 closure is asserted.

## Immutable data and API

**serialization.** JSON-compatible frozen records; tuples for sequences; enums for kinds; exact rational tick values encoded as canonical reduced numerator/positive-denominator pairs; maps copied then exposed read-only, including prevention of public attribute reassignment.

**identities.** Namespace-qualified nonempty strings for event_id, batch_id, source_id, anchor_id, object_id, version_id, visit_id, relation_id, cut_id. Reject endpoint namespace mismatches and duplicate IDs with changed content. SHA256 content hashes use canonical sorted-key compact UTF8 JSON with no NaN or float geometry; exact duplicate content under same key is a no-op.

**birth_key_fields.** ["generator_id", "definition_version", "exact_instrument_key", "anchor_version_ids_in_declared_order", "canonical_source_origin_ids", "generator_local_birth_discriminator"]

**birth_rule.** One canonical birth key maps to one object_id. A rename is alias metadata, not another birth. Different generator/definition/anchor/discriminator may legitimately share raw evidence and remain separate objects; expose shared-evidence relations rather than claiming statistical independence. Roles, display name, scores, current price and outcome are excluded from birth identity. Source origin IDs persist across revisions.

**revision_rule.** Per-object revision integer begins0, increases by1; exact previous version_id is supersedes. A version_id identifies immutable geometry/state/evidence snapshot and cannot be reused for other content. Mapping into another raw instrument or reanchoring uses a linked new birth unless an exact preregistered correction rule explicitly permits the anchor revision.

**instrument_and_units.** Full immutable provider,venue,raw instrument ID,definition/lifetime,raw symbol and relevant option terms. Geometry physical_support/contact_region in exact ticks of named source/execution coordinates; mapping_uncertainty,estimation_uncertainty,entry_tolerance separate nonnegative exact tick quantities. Negative prices valid; no cross-instrument point/tick arithmetic without mapping.

**time.** All clocks signed int64 UTC nanoseconds, booleans rejected. event_at may precede known time. Every published batch records decision_cut, input_known_at, actual_completion_at or named simulated-compute policy, and known_at=max(required evidence known times,confirmation time,completion). Exactly one observed-completion or modeled-compute branch; backdraw/anchor time is never publication time.

**RegistryDefinition.** Frozen lifecycle transition tables, birth-key schema, coordinate/mapping policy, visit-reset policy, expiry/archive policy, resource limits and version. Changing any semantic field changes definition ID.

**EvidenceVersion.** source_origin_id, version_id, predecessor, event_at,known_at, support enum observed/missing/invalid/tombstoned, exact instrument/units and content hash. A correction changes version/support, not original origin. External anchors reference exact evidence versions with formation interval and confirmation.

**ObjectRevision.** birth key,object_id,version_id,revision,supersedes,geometry,anchor/evidence version refs,existence,eligibility,evidence_state,role candidates,confirmation,clocks. Existence enum provisional/active/invalidated/expired/superseded; eligibility eligible/ineligible/unknown; evidence observed/missing/invalid/estimated.

**ObservationEvent.** event_id,object_version_at_observation,visit_id,event kind enter/contact/sweep/reclaim/exit/reset, event_at,known_at,reason, exact evidence refs, predecessor event where needed. Observation appends do not mutate stored geometry.

**Visit.** Stable object birth identity+monotonic per-object visit ordinal; open/closed/reset state derived from events, with frozen start geometry version and reset reason.

**RelationVersion.** Typed endpoints object_version/anchor_version/evidence_version/visit/action_alias; kinds parent,split_parent,merge_parent,mapped_from,shared_evidence,equivalent,shared_idea,display_group,alias. Relation known-time revision/tombstone separate from endpoint events. Directed ancestry kinds form DAG; equivalence/display relations are not ancestry.

**AtomicBatch.** batch_id,registered definition hash,global publication sequence,known_at,completion clocks,ordered immutable members,declared member count and content digest. One durable append commits all members.

**CandidateCut.** cut_id,cut time,instrument,definition,projection cursor,full applicable object version IDs,eligibility/exclusion reasons,relation closure and zero/unknown distinction. Selection/rejection annotations are separate immutable records referencing this denominator; do not silently filter loser history.

**FrozenTargetBinding.** target_id,cut_id,object_version,geometry hash,fixed horizon_end,observation process,unit. Verify version belongs to original cut and band equals that version; later supersession/expiry cannot rewrite it.

**ActionAlias.** Explicit policy-versioned key (canonical_idea_id,visit_id,side,plan_definition,horizon_end,exact instrument). Equal explicit aliases deduplicate exact action intents; geometric overlap/shared raw source alone does not deduplicate or create an equivalence assertion. Action sizing/execution absent.

## Frozen deterministic semantics

1. Formation with missing/unknown support may be recorded provisional, never eligible active; arbitrary nonempty evidence strings are insufficient. External source facts can be registered without native feed implementation but retain support/assumption scope.

2. Existence/eligibility, visit state and evidence state are independent. A supported active object may remain active after contact/sweep/reclaim under declared generator rules. No lifecycle fact can be changed by an unregistered forecast/score payload.

3. Allowed fixture existence transitions: provisional->provisional (formation revision), provisional->active, provisional->invalidated, active->active (geometry/support revision), active->invalidated, invalidated->active (new exact revision with restored support), active->expired, active->superseded. Expired/superseded never reactivate the same birth; a declared linked new birth is required.

4. Visits: enter/contact opens next ordinal when no open visit; sweep/reclaim require matching open visit; exit closes it. Same event duplicate is no-op. Revision preserves open visit unless declared reset; invalidation/expiry/supersession resets/closes once. Reactivation next visit increments ordinal, never resets historical count. Geometry correction with preserve policy binds visit start to old geometry; later observations cite their actual new supporting version. No retroactive contact invented.

5. Validate whole batch against pre-state plus staged earlier members. Explicit member ordinal resolves semantic dependencies at equal timestamps; it is registry transaction order, not inferred market/tick chronology. Unknown market order remains unknown in observations. Duplicate/conflicting revision or visit transition without a declared order rejects entire batch.

6. Every publication advances global sequence; known_at nondecreasing. Entire same-cut batch visible together. Cut token may include completed publication cursor to disambiguate equal-known-time batches; time-only query includes all completed batches with known_at<=cut. Frozen time cut prevents new publication with known_at<=cut; preexisting exact duplicate delivery remains permitted.

7. Split/merge may produce and retire intermediate objects in one batch. Parent DAG checks staged endpoints, no self/orphan/future edges or cycle. All original/intermediate versions persist and are directly retrievable; only final states enter active cut.

8. Relations carry their own known_at/revision/tombstones and obey frozen-frontier rules. Later equivalence or deletion cannot alter old relation projections or action-cut closures. Coincidence/equivalence never automatically becomes independent evidence.

9. Source drop/support tombstone creates a current unavailable/ineligible projection and targeted descendants; it is not factual object death/expiry. Lifecycle invalidation/death requires its own explicit observation/policy. When support returns, same birth and prior visits remain, unless declared lifecycle reset/new birth applies.

10. Corrected source versions dirty only reverse dependency descendants; dirty objects are gated until atomically repaired at actual new completion time. Derived geometry corrected at20 cannot change candidate cut15. Irrecoverable source gaps stay unavailable; no hindsight reconstruction.

11. Expired/invalidated/superseded/rejected objects remain in durable history and exact-version/target lookup. Hot-state expiry follows fixed known-time TTL/outcome-independent rules; archive is not deletion. Invalid latest version blocks current action by default. Any prior-valid fallback requires explicit policy, valid evidence and provenance with reason; unknown source cannot be bypassed.

## Public API boundary

**create_or_restore(path,definition)** — Reject journal/checkpoint definition mismatch; return registry with immutable config.

**commit_batch(batch,expected_head)** — Prevalidate schema,identity,clocks,full DAG/state/visit closure and limits; compare-and-append one durable envelope, then update indexes; duplicate identical batch/event no-op, conflict rejects. No partial write on any failure.

**get_version(version_id) / revisions(object_id)** — Retrieve exact archived immutable version or ordered all revisions; absent raises typed not_found.

**object_asof(object_id,cut,cursor=None)** — Latest completed eligible-or-ineligible fact snapshot by known cut; missing versus expired distinct.

**active_set(cut,instrument,cursor=None)** — Return factual active+eligible+supported+valid versions, output-size-aware cost; no display group filtering.

**events_asof / relations_asof / visits_asof** — Known-cut append-only projections with exact revision/tombstone policy; support object-local indexed queries.

**freeze_candidates(cut_id,cut,instrument,expected_head)** — Atomic snapshot of full applicable/excluded denominator and lineage closure at completed cursor; exact duplicate cut ID idempotent.

**bind_target(target,cut_id)** — Validate original candidate/version/geometry/horizon; return immutable binding independent of current state.

**project_action_aliases(cut_id,policy,proposals)** — Deterministic grouping on explicit full alias key; keep membership and rejected duplicates; never orders/trades.

**checkpoint() / restore(checkpoint,journal)** — Hash-bound definition,cursor,head,index state and pending-free status; verify exact journal prefix and integrity then replay suffix once. Snapshot is an accelerator, immutable journal is authority.

**archive_expired(cut)** — Evict only explicitly expired/inactive hot projections under fixed bounds; preserve all disk history. Capacity failure backpressures/gates, never evicts still-active candidates by outcome.

## Reference, indexed algorithm and measured comparison

Independent sequential fold of immutable batches and all members, rebuilding complete historical graph/state at every requested cut without using production index code or helper predicates. Preserve full event/revision/visit/source membership, not only active output.

Persist journal cursor and per-object revision/known-time index, relation/event indexes and reverse dependency adjacency. Query object-local history with binary search; dirty propagation traverses exact descendants only. Full current active-set enumeration necessarily costs O(k) returned members; avoid claiming O(log active set) for emitting k items.

Mark source-correction descendants, stage recomputed revisions and eligibility under frozen definitions, commit one current publication. Untouched object content/version remains byte-identical. Parent invalidation propagates support gating through DAG without inventing lifecycle transitions.

Same immutable history and fixed cuts fed to reference/indexed services. Exact canonical semantic outputs, candidate/target/action alias closure, failure/no-mutation behavior and restart/prefix parity. Legacy comparison only for supported existing meanings; documented corrected differences not hidden.

The toy has1002 objects:1000 independent births plus child/grandchild ofO0007. E0007 correction reevaluates exactly3 dependent object predicates versus1002 in full fold;999 unrelated versions remain unchanged. Count CPU, wall, RSS, bytes/records, edges and query/replay work separately. This ratio does not itself prove elapsed-time speedup.

## Bounds and failure behavior

{
  "batch_members_max": 128,
  "parent_edges_per_member_max": 32,
  "open_visits_per_object_max": 1,
  "hot_active_objects_max": 2048,
  "hot_relation_entries_max": 8192,
  "payload_bytes_max": 1048576,
  "identity_utf8_bytes_max": 256,
  "retained_history": "Durable append-only disk history under enclosing engineering budget; no unbounded full-history heap load in indexed service. Archive query paginates at256 rows by default.",
  "overflow_policy": "Reject batch before durable mutation and expose typed capacity_unavailable; no outcome-based truncation. Resource sizes are toy engineering scenario parameters, not calibrated production sizing.",
  "attempt_budget": "Generic registrar limits apply: maximum3 attempts/family,600 CPU seconds cumulative,180 nominal CPU/190hard,240wall,4GiB address-space per attempt. One shared full-suite identity conservatively charged as configured; no summed duplicate physical telemetry."
}

## Named fixtures and independent expected outcomes

**F10-01 — Coincident independent anchors**

Given: `{"births": [["POC0", "anchorA", 100], ["VWAP0", "anchorB", 100]], "known": 10, "relation": "display_group"}`

Expected: `{"canonical_birth_count": 2, "cut10_active": ["POC0", "VWAP0"], "display_group_count": 1, "independent_confirmation": false}`

**F10-02 — Visit preserves eligibility**

Given: `{"A0": "active10", "visitV1": [["contact", 20], ["sweep", 21], ["reclaim", 22]]}`

Expected: `{"cut15_active": ["A0"], "cut15_visit_state": "unvisited", "cut22_active": ["A0"], "cut22_visit_state": "reclaimed", "visit_event_count": 3, "visit_ids": ["V1"]}`

**F10-03 — Repeated retest and restart**

Given: `{"events": [["enterV1", 20], ["checkpoint", 21], ["exitV1", 25], ["enterV2", 30], ["duplicateEnterV2", 30]]}`

Expected: `{"open_visit": "V2", "restored_matches_uninterrupted": true, "unique_visit_event_count": 3, "visit_ordinals": [1, 2]}`

**F10-04 — Atomic split and merge**

Given: `{"batch20_order": ["A1 superseded", "B0 parent A0 active", "C0 parent A0 active", "C1 superseded", "D1 superseded", "E0 parents C0 D0 active"], "initial_active": ["A0", "D0"]}`

Expected: `{"cut19_active": ["A0", "D0"], "cut20_active": ["B0", "E0"], "failed_batch_appended_records": 0, "partial_prefix_visible": false, "retrievable_versions": ["A0", "A1", "B0", "C0", "C1", "D0", "D1", "E0"]}`

**F10-05 — Moving provisional gamma node**

Given: `{"versions": [["A0", "provisional", 100, 10], ["A1", "provisional", 102, 12], ["A2", "active", 102, 15]]}`

Expected: `{"birth_count": 1, "cut14_active": [], "cut14_latest": "A1", "cut15_active": ["A2"]}`

**F10-06 — Later geometry correction**

Given: `{"frozen_cut": 12, "source_correction_event_at": 8, "versions": [["A0", [99, 101], 10], ["A1", [102, 104], 20]]}`

Expected: `{"cut12_band": [99, 101], "cut12_geometry_unchanged_after_correction": true, "cut12_version": "A0", "cut20_version": "A1", "new_known_at": 20}`

**F10-07 — Failure and legitimate reactivation**

Given: `{"versions": [["A0", "active", 10], ["A1", "invalidated", 20], ["A2", "active", 30]]}`

Expected: `{"all_revisions": ["A0", "A1", "A2"], "cut15": ["A0"], "cut25": [], "cut35": ["A2"], "undeclared_reactivation_rejected": true}`

**F10-08 — Expired versions remain labelable**

Given: `{"bound_version": "A0", "expiry_known": 25, "target_cut": 15, "target_end": 40}`

Expected: `{"candidate_denominator_retained": 1, "cut26_active": [], "label_end": 40, "label_geometry": [99, 101], "label_version": "A0"}`

**F10-09 — Rename does not create fresh evidence**

Given: `{"A_birth_key": "K", "action_keys": ["ideaA/V1/long/plan1/end40/NQH5", "ideaA/V1/long/plan1/end40/NQH5"], "alias_B": "A", "attempt_B_birth_key": "K"}`

Expected: `{"alias_members": ["A", "B"], "canonical_birth_count": 1, "duplicate_birth_rejected": true, "loss_history_removed": false, "unique_action_count": 1}`

**F10-10 — Raw contract mapping preserves original**

Given: `{"X0_source_ticks": 100, "Y0_execution_ticks": 103, "mappingM_known": 20, "mapping_relation": "X0->Y0"}`

Expected: `{"cut19_mapped_active": [], "cut20_mapped_active": ["Y0"], "mapping_version": "M", "native_equivalence_certified": false, "original_X0_ticks": 100}`

**F10-11 — Relation correction respects knowledge cut**

Given: `{"endpoints_known": 10, "relationR0_known": 30, "relationR1_tombstone_known": 40, "relation_event_at": 12}`

Expected: `{"cut20_equivalent": false, "cut35_equivalent": true, "cut45_equivalent": false, "retrievable_relations": ["R0", "R1"]}`

**F10-12 — Orphan and unknown source closure**

Given: `{"attempts": [["A", "missing_parent", 10], ["A", "E_known11", 10], ["A", "E_known11", 12]]}`

Expected: `{"accepted": [false, false, true], "commits": 1, "rejection_mutates_state": false}`

**F10-13 — Independent immutable state dimensions**

Given: `{"bad_evidence_state": "calibrated_by_UI", "bad_visit_state": "whatever", "legitimate_contact": "active+eligible+observed"}`

Expected: `{"bad_states_rejected": [true, true], "contact_active": true, "contact_eligibility": "eligible", "contact_evidence": "observed"}`

**F10-14 — Exact version and candidate cut retrieval**

Given: `{"A_superseded20": "A1", "B_expired25": "B1", "annotations": {"rejected": ["B0"], "selected": ["A0"]}, "cut15_versions": ["A0", "B0"]}`

Expected: `{"annotations_unchanged": true, "candidate_count": 2, "lookup_old_versions": ["A0", "B0"], "restored_cut15": ["A0", "B0"]}`

**F10-15 — Reference/indexed projection parity**

Given: `{"A": ["A0@10", "A1@20"], "B": ["B0@15", "B1_expired@25"], "queries": [9, 10, 15, 19, 20, 25], "unrelated_future_suffix": 1000}`

Expected: `{"active_at_cuts": [[], ["A0"], ["A0", "B0"], ["A0", "B0"], ["A1", "B0"], ["A1"]], "prefix_deletion_equal": true, "reference_indexed_equal": true, "restart_equal": true}`

**F10-16 — Frozen lifecycle contract**

Given: `{"attempt_reassignment": true, "checkpoint_definition": "different", "registered_tradable": ["active", "contacted", "reclaimed"]}`

Expected: `{"config_reassignment_rejected": true, "existing_contacted_active_unchanged": true, "restore_definition_mismatch_rejected": true}`

**F10-17 — Scores are downstream typed outputs**

Given: `{"calibration_provenance": null, "probability_claim": "0.71", "rank": 82, "rank_scale": 100}`

Expected: `{"factual_lifecycle_changed": false, "probability_from_rank": null, "unsupported_probability_eligible": false}`

**F10-18 — In-between location has explicit origin**

Given: `{"negative_weight_variant": [-1, 1], "parent_prices": [100, 104], "positive_weights": [1, 1], "proposal_rule": "weighted_midpoint"}`

Expected: `{"negative_weight_ordinary_density_accepted": false, "new_geometry_ticks": 102, "new_parent_count": 2, "original_births_retained": 2}`

**F10-19 — Invalid latest version fallback is explicit**

Given: `{"A0_active": 10, "A1_invalid": 20, "fallback_policy_default": "block"}`

Expected: `{"cut21_current_action_eligible": false, "explicit_fallback_requires_valid_old_support": true, "silent_A0_fallback": false}`

**F10-20 — Bounded retention is not hindsight deletion**

Given: `{"TTL_ns": 30, "archive_cut": 40, "births": {"A": 10, "B": 10}, "outcomes": {"A": "failure20", "B": "success25"}}`

Expected: `{"archived_ids": ["A", "B"], "history_deleted": false, "hot_active": [], "outcome_dependent_expiry": false}`

**F10-21 — Mutable preset cannot rewrite prior geometry**

Given: `{"A_color_changed": true, "A_preset": "P_v1", "B_preset": "P_v2", "ratios_v1": ["0", "1/2", "1"], "ratios_v2": ["0", "309/500", "1"]}`

Expected: `{"A_geometry_preset": "P_v1", "B_geometry_preset": "P_v2", "color_mutates_geometry": false, "preset_name_alone_sufficient": false}`

**F10-22 — Universe changes are not object death**

Given: `{"A_visible": [true, false], "view10": "Current", "view20": "first3expiries"}`

Expected: `{"A_factual_death": false, "A_history_retained": true, "universe_definition_changed": true}`

**F10-23 — Visual clamp does not widen physical band**

Given: `{"clamp_percent": [4, 8], "opacity_percent": [35, 60], "support": [99, 101]}`

Expected: `{"confidence_inferred": false, "geometry_version_changed": false, "presentation_version_changed": true, "support": [99, 101]}`

**F10-24 — Derived overlay disappearance is support loss**

Given: `{"mapped_birth": "A", "source_support": [[10, "observed"], [20, "missing"], [30, "observed"]]}`

Expected: `{"action_eligible_at": [true, false, true], "canonical_birth_count": 1, "factual_death_events": 0, "mapping_formula_certified": false}`

**F10-25 — Historical display requires original cut**

Given: `{"after_version": "A1", "before_version": "A0", "correction_known": 30, "selected_replay_cut": 20}`

Expected: `{"current_version": "A1", "replay_version": "A0", "visual_replay_button_certifies_asof": false}`

**F10-26 — Completion controls publication, not drawing anchor**

Given: `{"actual_completion": 12, "anchor_end": 5, "anchor_start": 1, "confirmation": 9, "input_known_at": 8, "simulated_delay_also_supplied": false}`

Expected: `{"actual_completion_plus_simulated_delay_rejected": true, "cut11_active": [], "cut12_active": ["A0"], "known_at": 12}`

**F10-27 — Parent DAG and staged identity conflict rollback**

Given: `{"cycle": ["A0->B0", "B0->A0"], "duplicate_id_different_payload": "A0", "orphan": "missing0", "valid_existing_prefix_records": 3}`

Expected: `{"conflicting_identity_rejected": true, "cycle_rejected": true, "orphan_rejected": true, "records_after_each_rejection": 3}`

**F10-28 — Targeted source invalidation equals full fold**

Given: `{"correction": "E0007v1@20", "edges": ["E0007->O0007", "O0007->C0007", "C0007->G0007"], "extra_children": ["C0007", "G0007"], "independent_objects": 1000}`

Expected: `{"dirty_ids": ["O0007", "C0007", "G0007"], "full_object_evaluations": 1002, "pending_dirty_objects_action_eligible": false, "semantic_outputs_equal": true, "targeted_object_evaluations": 3, "unaffected_object_versions_unchanged": 999}`

**F10-29 — Checkpoint cursor, hash and exact suffix integrity**

Given: `{"faults": ["wrong_definition", "wrong_head", "payload_tamper", "cursor_beyond_end", "partial_batch_snapshot"], "journal": "B1,B2,B3", "snapshot_cursor": 2, "snapshot_head": "H2"}`

Expected: `{"all_faults_rejected": true, "duplicate_B3_no_second_visit": true, "restored_projection_equals_fresh": true, "valid_prefix_replayed": [], "valid_suffix_replayed": ["B3"]}`

**F10-30 — Capacity rejects atomically without forgetting active objects**

Given: `{"active_before": 2048, "active_limit": 2048, "attempt_new_active": 1, "batch_limit": 128, "members_attempted": 129}`

Expected: `{"active_overflow_rejected": true, "batch_overflow_rejected": true, "history_deleted": 0, "new_journal_records": 0, "old_active_count": 2048}`

**F10-31 — Frozen time cut and equal-time batch ordering**

Given: `{"B1_known": 20, "B1_members": ["A0", "A1"], "exact_duplicate_B1": true, "freeze_cut": 20, "later_B2_known": 20}`

Expected: `{"exact_duplicate_B1_noop": true, "frozen_latest": "A1", "intermediate_A0_visible_in_active_cut": false, "late_new_B2_rejected": true, "two_independent_unfrozen_same_time_batches_use_global_sequence": true}`

**F10-32 — Invalidation resets visit while reactivation retains ordinal**

Given: `{"events": ["A0 active10", "V1 enter12", "A1 invalid20", "A2 restored30", "V2 enter32"]}`

Expected: `{"V1_reset_at": 20, "V1_state": "reset", "V2_ordinal": 2, "open_visits": 1, "visit_history_ordinals": [1, 2]}`

**F10-33 — Target cannot substitute corrected geometry**

Given: `{"A0_band": [99, 101], "attempt_member": "A1_known20", "attempt_target_band": [102, 104], "cut15_member": "A0", "fixed_end": 40}`

Expected: `{"fixed_end": 40, "future_version_rejected": true, "valid_target_geometry": [99, 101], "wrong_band_rejected": true}`

**F10-34 — Geometry correction preserves visit under declared policy**

Given: `{"events": ["A0 band99..101 known10", "V1 enter12 bindsA0", "A1 band102..104 known20", "V1 exit25 citesA1"]}`

Expected: `{"exit_observation_geometry": "A1", "retroactive_contact_at_new_band": false, "visit_birth_geometry": "A0", "visit_count": 1}`

## Acceptance and execution accounting

After approval/registration, one consolidated test implementation must assert all34 named cases against independent literals, compare reference/indexed projections and complete candidate/relation/visit/target/action-alias closure, test atomic failure with unchanged durable prefix, and compare uninterrupted/restarted/suffix-deleted histories. No skips or unexplained ambiguity. Rational geometry, identity, counts, masks, clocks and graph/state outputs compare exactly; hashes are recomputed independently from canonical bytes. Native latency and empirical probabilities remain outside this deterministic contract.

Instrument per-object update counts, adjacency visits, full-history reads and query cursor work as defined above. Record actual CPU/wall/RSS and bytes; do not infer a speedup from asymptotic labels. Do not iterate until a favorable benchmark appears. Consolidate findings, make at most one coordinated repair pass per review cycle, respect preregistered attempt/CPU limits and retain every attempt.

The generic registrar records baseline code, protocol, golden, source and design hashes before dependent code. It must retain temporary preparation evidence. Root performs publication; this draft script does not invoke project code or registrar.

## Remaining gates

{
  "source": "Resolved supplied and direct external F10 originals complete via recorded fresh reading or exact permitted/shared reuse; downstream generator and private-formula gates remain separate.",
  "deterministic": "All25 proposed cases unexecuted; listed static gaps unresolved. No F10 P0\u2013P7 completion implied.",
  "native": "Actual provider receipt clocks, mapping revisions, correction messages, checkpoint/replay and captures require authorized data and parity evidence; no market tape read.",
  "calibration": "Any learned lifecycle/role/reach/rank/action output needs frozen target/cohort/OOF and chronological calibration; no sample percentages admitted.",
  "economic": "P4 increment/interactions, P5 rerun attribution, P6 full one-account/one-mini costs/risk/fill confirmation and P7 future monitoring remain planned.",
  "private": "No reconstruction of undisclosed source formulas, participant identities or hidden inventory."
}

Private source formulas, all downstream generator integration, native receipts/roll mappings/corrections, chronological learned calibration, economic confirmation and future operational evidence remain explicit gates. Deterministic registry correctness is neither alpha nor trading authorization.

## Exact added runtime declaration

{
  "id": "F10.LINEAGE",
  "component": "F10",
  "stage": 0,
  "schema": "ImmutableLineage.v1",
  "fields": [
    "objects",
    "versions",
    "geometry",
    "observations",
    "visits",
    "relations",
    "candidate_cut",
    "targets",
    "action_aliases",
    "known_time",
    "history_cursor"
  ],
  "dependencies": [],
  "lane": "offline",
  "learned": false,
  "target": null,
  "capabilities": []
}

This offline declaration names the implemented service and has no automatic consumer activation. Its actual binding must retain verified implementation, definition, parameters, input schema and this family verification artifact. Existing runtime declarations retain their contracts. A port declaration alone does not supply external inputs, completed full-system integration, source certification or economic evidence.
