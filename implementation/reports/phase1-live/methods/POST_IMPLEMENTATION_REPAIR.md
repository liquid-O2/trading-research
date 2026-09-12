# Phase 1 post-implementation correctness repair

**The Phase 1 correctness gate is closed for the reviewed implementation scope.** The final acceptance passed after the unchanged independent diagnostic, the full test suite, all 27 original counterexamples with schema checks, five separate quantity controls, and all 12 method reports. No remaining defect was identified in the repaired paths under these checks. Historical discovery remains unavailable.

The reviewed commit was `662463b545394e663937be2d83e0677f50492dc3`. Its 475 passing tests and two subtests did not expose the independent diagnostic's four invalid cases. The [original negative review](../../../validation/phase1-post-implementation-check/original-check/POST_IMPLEMENTATION_CHECK.md), [original six inputs and results](../../../validation/phase1-post-implementation-check/original-check/lifecycle-probes.json), [preservation manifest](../../../validation/phase1-post-implementation-check/original-check/preservation.json), and [previous acceptance](../../../validation/phase1-post-implementation-check/previous-acceptance/final-acceptance.json) retain that history.

## Repairs and review

O150 checks each event's order, position, instrument and supplied candidate relationship before applying it. Working-order mutations require order/instrument links; fills also require position; exits require position/instrument and may occur after entry-order cancellation. Explicit reopen generations remain supported. Pending or unavailable reopens cannot activate a new order generation. A caller's policy flags cannot bypass these checks, and a later explicit cancellation cannot suppress an earlier policy deadline.

Occurrence, availability, snapshot and use retain their original timestamps. Contradictory clocks reject; correctly timed future records remain pending. Explicit unknown availability remains unknown. Unverifiable events remain unapplied and cannot certify final quantities; separately named `known_prefix_*` fields retain observed prefix arithmetic.

O151 preserves individual actual fill-report identities, occurrence, availability and quantity through the parent adapter. An early partial fill is visible even when a later report is still pending. O166 requires both B/A/D/E/W labels, actual adjacency and cohort/reset identity, and causal conditioning. Missing labels produce explicit holes and unknown validity; invalid labels or clocks reject. No automatic classifier was introduced.

Supplied-source dependency and operand audits rerun these domains with the actual outer instrument, method and snapshot. Real source-audited parent outputs exercise the native adapter, including foreign identity, future/unknown availability, linked reopens and post-cancellation exits. [The parent review](../../../validation/phase1-post-implementation-check/repair-review.json) records the changed obligations and why unaffected native calculations and source figures retain their earlier review.

The [comparison of all twelve refreshed reports](../../../validation/phase1-post-implementation-check/report-invariance.json) confirms unchanged measurement, assembly, outcome and missing-evidence values, with the same historical and source limits.

Full schema replay also exposed four legacy partial-result defects: O001 and O056 guards omitted required unknown fields, O006 returned the wrong recipe identity with an incomplete clock/range payload, and O015 rejected its own unknown bands under a nonnullable schema. These now preserve complete typed unknown results. Native measurements, literal inputs and source limitations remain unchanged; computed and invalid-identity controls still behave correctly.

## Exact independent cases

| Preserved case | Current result | Observed invariant | Supplied-source audit |
| --- | --- | --- | --- |
| `order_control` | `computed` | `filled=1; position=1; lifecycle_valid=True` | accepted |
| `foreign_order_fill` | `invalid` | `filled=None; position=None; lifecycle_valid=False` | rejected |
| `future_fill_backdated` | `invalid` | `filled=None; position=None; lifecycle_valid=False` | rejected |
| `transition_control` | `computed` | `D → A; transition_valid=True` | covered separately by admission tests |
| `transition_missing_labels` | `hole` | `None → None; transition_valid=None` | covered separately by admission tests |
| `transition_backdated` | `invalid` | `D → A; transition_valid=False` | covered separately by admission tests |

The [repair checker](../../../tools/validate_phase1_post_implementation_regressions.py) records exact original-input fingerprints, current implementation hashes, full output-schema checks and supplied-source admission outcomes in [repair-regressions.json](../../../validation/phase1-post-implementation-check/repair-regressions.json). The original diagnostic script was rerun unchanged: **6 passed, 0 failed**.

## Final validation

- **639 tests and 2 subtests passed**, with zero failures, errors or skips; [the final test record](../../../validation/phase1-completion/test-run.json) confirms unchanged tested inputs across the run.
- **6/6 preserved independent cases passed**, including both positive controls and all four invalid/missing-evidence cases.
- **27/27 original counterexamples passed their behavior and full schema checks**, with **5/5 additional identified O150 quantity controls**. Original inputs remain unchanged in [the paired audit](../../../validation/phase1-completion/audit-regressions.json).
- **12/12 method reports passed implementation checks** using the locked environment and recorded commands; [runner evidence](../../../validation/phase1-completion/runner-checks.json) and both family tables are in [the completion report](COMPLETION_REPORT.md#required-family-tables).
- The [matrix](COMPLETION_MATRIX.md) and [final gate](../../../validation/phase1-completion/final-acceptance.json) resolve **166 objects, 9 shared contracts, 12 methods and 373 operands**. Shared executable evidence includes **5 printed fixtures and 22 verified regression groups**.

The gate now rejects missing or stale regression evidence, changed original inputs, failed schema/quantity controls and falsely marked passing lifecycle results. Manual reviews were updated after re-examining behavior and passing stable checks; hashes alone did not grant closure.

Historical candidate count remains unavailable and `search_completed=false`. No parameter searches, new classifiers, macro collection or performance research were added. Raw data and protected source/archive/old-plan directories were preserved. No commit or push was performed for this repair.
