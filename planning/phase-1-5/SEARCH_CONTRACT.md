# Finite breadth and refinement search

Owner `P15-08` registers the candidate bank; `P15-17` executes breadth; `P15-18` refines. Read [specification](SPEC.md), [evaluation](/workspace/planning/research-program/EVALUATION.md), [outcomes](/workspace/planning/research-program/OUTCOMES.md) and [retention](../research-program/RETENTION.md) together.

## Candidate identity and counts

Always include B0, the accepted source-inspired reconstruction. A candidate changes exactly one declared mechanism axis unless it is in the later explicit combination round. It carries a diff of stage/parameter meanings, not just a cryptic integer. Apply candidates to every eligible branch listed below; the branch IDs come from the frozen Phase 1 registry, never from a hand-maintained second branch catalog.

| Bank | Representative alternatives beyond B0 | Eligible population |
| --- | --- | --- |
| Formation | F1 trailing 60m; F2 prior-volume-completed; F3 causal balance | JJ other_session, single_extended, single_purged, internal_rotation; GB nyam_box/previous_hour; Saint balance branches; Sires microbalance. Source clocks stay fixed. |
| Profile | P1 raw tick profile b0; P2 triangular b2 | Saint and Member profile references; Keani developing value; Sires balance references. Use the same causal formation. |
| Reference | R1 account-day VWAP/band; R2 prior completed session edge | Custom siblings of GB-VWAP, GB-SCALP and Sires vwap_deviation_fade/defended_band_continuation only. Preserve original source variants separately. |
| Delta | C1 normalized5m; C2 5m half-life; C3 past-bucket robust score | Every branch that actually consumes delta/flow in Sires, GB-SCALP, Saint; confirm input use in the source adapter. A branch with no delta input is explicitly not applicable. |
| Sequence | S1 reclaim; S2 defended retest; S3 flow-supported reclaim; S4 failure-to-progress | JJ reversal/extension/other_session; GB failure/scalps; Sires reaction/continuation; Saint retests; Member reaction; Keani retest. Do not change the Judas outbound opening-entry branch into a retest without a distinct custom family. The separate Timing bank explicitly tests custom Judas reversal windows. |
| Memory | M1 require at most 1 previous completed distinct contact; M2 require previous resolved120s favorable reaction >.25S and no subsequent invalidation | Existing reference-contact candidates in Member/Sires/Saint; Refilling observations separately. Not a universal ban on old/saturated levels. |
| Timing | T1 source reversal/action window +15m; T2 window -15m using only an already complete formation; T3 condition-defined morning reversal; T4 no clock limit: the same sweep and confirmation searched from 09:30 through the account-day flatten, with expiry 60 minutes after qualification | JJ judas_reversal/other_session and GB nyam_box custom siblings. If formation is not yet available at T2, omit with a reason; never truncate a source range and call it unchanged. T4 applies to JJ judas_reversal and every GB-FAIL sweep branch as a custom sibling; source-identity output remains B0. |

This is at most 19 nonbaseline axis recipes per branch, but only applicable cells are created. `P15-08` emits a concrete expanded `candidate-bank.json` with a maximum of 160 nonbaseline branch candidates for the breadth round, plus all baseline branches. If the mechanical expansion exceeds160, apply round-robin by bank then family then branch ID, taking one candidate per applicable family/bank before second candidates; preserve deferred cells and their deterministic order. No result may affect this expansion. This cap is a first-stage breadth budget, not a claim that exactly 160 models should exist.

Separate method adapters own source constraints and construction. `P15-09` Jumbo; `P15-10` GB-FAIL; `P15-11` GB-VWAP/scalps; `P15-12` Sires; `P15-13` Saint; `P15-14` Member; `P15-15` Keani; `P15-16` research processes. Context/research/risk units never enter entry-setup denominators because their candidate bank has a row.

## Custom reversal timing recipe

T1/T2 shift the action-window start and end together by the registered offset, keeping formation already complete; source-identity output remains B0 and changed clocks use custom sibling IDs. Their expiry is the shifted window end, capped at account-day flatten. T3 uses the source-frozen overnight/range reference and a 09:30–12:00 ET custom action window. Require a strict edge sweep, then a complete trailing 15-minute balance with width<=.75 of the 60-minute scale ending before that balance and efficiency<=.35, then the S1 reclaim within 10 minutes. Entry follows that causal reclaim, structural stop is beyond the swept extreme by1 tick, objective is the still-unconsumed opposite frozen edge, and expiry is the earlier of 60 minutes after qualification or 12:00. If the objective is already consumed after the sweep, reject it. Retain all unchanged source context that can be evaluated before contact; publish the timing/balance additions as our hypothesis, not an author Judas formula. This tests condition-based reversal beyond a small clock adjustment.

T4 removes the reversal clock entirely: after the source-frozen sweep and its five-minute confirmation, the entry may occur at any time from 09:30 to the account-day flatten; structural stop and objective are unchanged; expiry is the earlier of 60 minutes after qualification or the flatten. It tests whether the source's clock limit adds value beyond the sweep-and-reclaim mechanism itself. Its refinement neighborhood in the table below is the T issue offset row, unchanged.

## Breadth stage

Run the entire registered applicable bank in each outer fold with inner fit/tune separation. In inner tuning rank each candidate on primary daily net-point improvement, displaying frequency and delay. Pick at most two mechanism banks per source family that have nonnegative tuning improvement and pass inner support. Retain the best representative within each bank using the 1% simplicity rule. When none qualifies, choose no refinement and retain B0. This is a selection step; outer outcomes cannot expand the bank or choose the two banks.

Baseline comparisons use both common complete-input dates and full native coverage. Include density-matched controls for reference variants: choose the same count of bands on the same issue times, widths and expiry, with deterministic offsets `{-2S,-S,+S,+2S}` cycled by SHA256(reference_id) mod4. Reject a control that duplicates a real band within 1 tick and try the next offset; if all duplicate, mark unavailable. Controls preserve direction and stage/exit rules. They test whether concentration/placement adds value beyond the number and width of bands, not whether arbitrary shifted zones are a tradable strategy.

## Refinement stage

Refine only the two selected banks per family and only inside each fold's past fit/tune data. Use these exact one-axis neighborhoods; keep other chosen values fixed:

| Chosen mechanism | Neighbor values |
| --- | --- |
| F1 trailing duration | 30,60,90 matching minutes |
| F2 volume threshold multiplier | .75,1,1.25 times the prior 20-session median |
| F3 balance maximum width / efficiency | width .5,.75,1S with efficiency fixed.35; then efficiency .2,.35,.5 at chosen width |
| P smoothing / prominence | b0,2,4 with prominence.20; then prominence .10,.20,.30 at chosen b |
| R VWAP band | .5,1,1.5 dispersion; prior edge alternative has no numeric refinement |
| C1 window / C2 half-life / C3 history | 2,5,10 minutes / 120,300,600 seconds / 10,20,40 sessions |
| S deadline / reclaim favorable distance | 5,10,15 minutes / 1,2,4 ticks, one at a time |
| M1 touch count / M2 reaction threshold | at most 0,1,2 previous contacts / .1,.25,.5S |
| T issue offset | -30,-15,0,+15,+30 minutes; availability still required |

Maximum 12 new neighbors per selected bank per family, maximum 24 per family. After choosing the best two refined mechanisms, permit exactly one combined candidate with both changes, only if each individually beats B0 on inner tuning and all source dependencies remain causal. Compare combination against each ingredient and B0; label interaction explicitly. Maximum 25 refined/combined candidates per family per outer fold. There is one breadth round and one refinement round; no recursive “keep searching until profitable” loop.

If two families share a primitive, share cached calculations but keep their fitted/selected identities and evidence separate. Store attempted, duplicate, not-applicable, unsupported, timed-out and rejected candidate rows. Runtime failures never disappear from the trial count or become data rejections. A resumed run uses the same bank and seed.

## Trial ledger and final choice

`TrialRecord`: trial_id, parent_trial_ids, family, branch, outer_fold, stage, bank, exact parameters, code/data/plan hashes, fit/tune/calibration windows, outcome-exposure cutoff, candidate population counts, score/loss, support, all test metrics, reason, disposition, runtime, artifacts, and `failure_attribution`. Write append-only JSONL; a new attempt gets a new ID and `replaces_attempt_id`, leaving the old row intact.

`failure_attribution` is required for every deselected, inconclusive or not-promoted candidate. It is an ordered list drawn from `frequency` (entries below the frequency floor), `location_miss` (objective not reached while price came within 0.25 S of it, or adverse excursion beyond 0.5 S before any favorable 0.5 S), `confirmation_delay` (missed-move share above the family median), `adverse_before_target` (stop-first share above the family baseline), `cost_sensitivity` (sign reversal under the stress setting), `support` (below the support gate), `coverage` (unexplained input coverage loss). Each is computed from the diagnostics the Strategy Book already reports, with these thresholds fixed before any candidate result is read.

Bounded revisits: Phase 3 re-screens every retained candidate whose first attribution is `location_miss`, using its improved locations. Phase 4 re-screens every retained candidate whose first attribution is `confirmation_delay` or `adverse_before_target`, using the response and entry experts. A revisit is one registered pass over the retained set with the same folds, scores and promotion gates; it is not a new open search and adds no neighbors.

Select a final recommended research rule only by the shared promotion gates. Record the fold-specific selected rule role separately from an all-history descriptive final recommendation. Phase 2 historical training consumes the fold-specific causal role or B0, never a backward-applied final winner. Unselected alternatives remain available as research evidence, not automatically active downstream inputs. A disposition never deletes a candidate.

The exit study compares E0–E4 after entry selection is frozen. Its trials are an additional, separately counted decision family; it cannot rescue an entry candidate by replacing the primary exit during the earlier rule test. Final release includes both unchanged-entry evidence and the frozen baseline management policy for Phase 2 suitability labels.
