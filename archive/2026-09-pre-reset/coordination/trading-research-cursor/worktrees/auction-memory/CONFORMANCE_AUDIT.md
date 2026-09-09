# Conformance audit after the sequencing concern

2026-09-06. **The implementation has not satisfied the handoff's opening
validation gates. New feature work is paused while those gaps are reconciled.**
Existing code is retained as unpromoted work. The requested B00–B10 scope remains.

## Required order

The [handoff's reading rules](../planning/trading-model/IMPLEMENTATION_HANDOFF.md#reading-and-conflict-resolution)
require the whole parent card, child/refinement, local phases, constructions and
upstream contracts before each unit is implemented. Each mechanism must be
traced to original passages, with exceptions and corrections converted to named
expected assertions.

The [validation plan](../planning/trading-model/VALIDATION_PLAN.md#1-evidence-gates-and-stopping-rules)
separates V0 specification, V1 data/semantics, V2 prediction, V3 complete
economics, V4 future/operations and V5 a later deployment decision. The
[specialist phases](../planning/trading-model/SPECIALIST_EXPERIMENT_PROGRAM.md#eight-phases-for-each-parent-and-each-named-refinement)
apply those requirements independently to every parent and child. An executed
test supports its actual assertions, not every gate.

The [master plan](../planning/trading-model/IMPLEMENTATION_PLAN.md#dependency-order-and-promotion)
puts F/V contracts and the minimum policy harness first, then deterministic
measurements and faithful Context/Location baselines, then E0. The
[backlog](../planning/trading-model/IMPLEMENTATION_BACKLOG.md#milestone-b03--e0-complete-one-mini-baseline-early)
allows E0 once its minimum dependencies pass; it need not wait for all later
specialists. Independent work may overlap, but prerequisite validation remains
required.

## Findings

| Finding | Evidence and consequence |
|---|---|
| Required reading was incomplete | Governing documents and many applicable cards were read, but full upgrade/refinement review and original-passage closure were not completed for every implemented mechanism. No unit has completed definition review in the ledger. The planning team's source-review totals do not establish this implementation's review. |
| Code grew ahead of source-case validation | B00.5 remains in progress. Many local/source compound cases lack explicit expected outputs linked to executed assertions. A nearby numerical fixture cannot discharge them. |
| Data validation remains partial | Seven nonempty paired hours reconcile, one missing ES MBP hour is recorded, and ten complete definition partitions were audited. The 111-dataset inventory is present, but field/cohort eligibility is incomplete; chain/OI and other B01 branches remain open. |
| Work spread beyond the minimum E0 path | The typed graph and independent scheduler are early requirements, and a neutral execution/risk/account harness is needed by E0. Extended broker and business-cash scenarios nevertheless received effort while minimum Context/Location validation and E0 were unfinished. Further expansion is deferred. |
| Predictive validation has not reached market data | Frequency/logistic/calibration and planted/null checks used synthetic fixtures. No real-market specialist comparison, complete E0 report or sequential economic evaluation has run. |
| Test coverage is incomplete relative to contracts | For example, B00.6 still lacks the complete incremental/macroaction reward and duplicate-OI-assimilation cases. B02 source anchors, range-path variants and comparison inventories remain incomplete. The 176 tests cannot establish their correctness. |
| Status prose lagged behind work | Historical remaining-work lists were mixed with newer test counts. STATUS and README now lead with validation state and link historical reports separately. |

Contract selection was not an invented research diversion:
[E0](../planning/trading-model/E0_REFERENCE_EXPERIMENT.md#freeze-the-manifest-before-replay)
explicitly uses preceding-session volume to select an unexpired outright. The
implemented function is a reference; it has not selected a trading policy or
proved that the supplied continuous tape contains all competing outrights.

## Gate assessment

| Gate | Current status |
|---|---|
| V0 specification | Open: original-source variants, compound cases and expected assertions incomplete. |
| V1 data/semantics/causality | Partial: named fixtures and bounded audits pass; case/cohort certification remains open. |
| V2 real-market prediction | Unrun. Synthetic positive/null controls are harness checks only. |
| V3 complete one-mini economics | Unrun. E0 is incomplete. |
| V4 frozen prospective evidence | Unrun; requires a validated/frozen policy, permitted observations and elapsed future dates. |
| V5 deployment | Not reached. |

The scope ledger retains all 4,173 IDs. Only B00.7, scope import and durable
status preservation, is verified on operational fidelity. No model or trading
policy is selected. All real-market evaluation states remain unrun.

## Corrected execution queue

1. Finish incomplete governing reading and the opening units' parent, child,
   upgrade and original-source definitions. Record each variant, exception,
   expected assertion and exact dependency. Importing an ID is not review.
2. Close applicable B00 reference/causality/lineage cases and B01 small-cohort
   gates needed by E0. Keep usable, missing and assumed observations distinct;
   retain unrelated B01 obligations independently.
3. Validate B02 measurements and faithful Context/Location objects against
   independent source-derived expectations, including range/path and anchor
   alternatives. Retain all candidates, failures and no-contact branches.
4. Freeze E0 dates, policies/models, fees/timing, metrics and budgets. Run the
   complete always-flat, source-rule, frequency and regularized-model
   comparisons; report prediction/calibration and full one-mini day/order/account
   outcomes with uncertainty.
5. Use E0 for per-family definition/information/model tests and interactions
   through B04–B09, then B10 when future-time prerequisites exist. Diagnose weak
   results through new bounded registered comparisons; do not reuse evaluation
   periods until a favored result appears.

The next work is validation of the opening implementation. No milestone advances
on test counts alone.

## First source-derived repair

The [F01 review](validation/F01_SOURCE_CASES.md) now traces the decoder's
assigned originals and records mandatory expected results before execution.
The new cases exposed truncated-native-input acceptance, content-alias identity
errors and missing schema checks. The failing artifacts remain alongside the
subsequent 191-test passing run. Later source-first tests added bounded complete
MBP Parquet admission and native physical field preservation. The latest
210-test regression and 24 native prefixes are recorded in the same review.
Wider/native admission, all-schema semantics and integration coverage remain
open; these results do not advance the program past the opening gates.

## Consolidated implementation review

Following the user's requested process, all 71 then-current implementation
files were reviewed before one consolidated repair pass. The
[27-case review](validation/BATCH_REVIEW_2026_09_06.md) preserves the frozen
reproductions, repairs, first integration failures and final 247-method passing
verification. Actual Parquet evidence now covers 21 physical profiles and 686
prior-field comparisons; the missing 22nd profile remains explicit. This
closes the named defects and error-accounting omission, while V0/V1 source,
cohort and phase prerequisites remain open. No market/economic gate advances.

## Governing reading closure

The [reading record](reports/governing-reading-progress.json) now records the
complete refinement and upgrade documents, source findings and all 712 exact
source routes, 122 conversation routes, the external routing matrix, and its
119 linked findings including the five-item third-review supplement. All direct
handoff text links are reviewed; the scope registry remains structurally
verified rather than being treated as semantic evidence.

The source-route reconciliation found 712 distinct matches, no omitted route
and no duplicate source finding. Identical route descriptions and dispositions
were compared exactly with the corresponding finding text and read once;
different clauses, source links, component anchors and required cases were read
individually. This closes the incomplete governing reading identified above.
Original-passage review for each unit and execution of its named assertions
remain separate V0/V1 requirements. The next work is the opening-unit case and
cohort validation in the corrected queue.

The subsequently completed [calendar supplement](reports/f01-calendar-field-supplement.json)
closes the single missing physical-profile prerequisite. The combined physical
coverage is 22 profiles, 64 distinct rows and 719 fixed field expectations;
the original 21-profile run and separate 103-check supplement remain distinct.
Source-specific semantics and intended-cohort gates remain open.

The subsequent [F02 kernel review](validation/F02_KERNEL_BATCH_REVIEW.md)
collected twelve findings before one consolidated repair. All 264 combined
methods passed on the first registered execution, including 17 new fixed
registry/payoff methods. The [case evidence](reports/f02-kernel-case-coverage.json)
preserves partial assertion mappings, exact code and resource observations.
Historical product admission, consumer integration and V2–V4 remain open.

The subsequent [F03 interval/timer review](validation/F03_INTERVAL_BATCH_REVIEW.md)
collected twelve findings before one consolidated repair. All 288 methods passed
on the first registered combined run, including 24 new calendar/timer methods.
The [case evidence](reports/f03-interval-case-coverage.json) retains the 74-clause
original-source review, exact code, fixed expectations and resource observations.
Restart assertions include abrupt process exit before and after a committed
internal state transition. Dated venue/account admission, complete source-specific
indicator parity, all-consumer integration and market/economic phases remain open.

## F04 availability and scheduler batch

All 321 methods passed on the first registered run after the complete ten-finding review and single consolidated repair. Exact source extent, fixed expectations, code, test IDs, resource telemetry, and the seven-cut 20-versus-12 operation comparison are retained in `reports/f04-replay-case-coverage.json`. The 58 assigned/lineage findings remain distinguished from source-specific implementation and all-consumer phases. All 4,173 economic evaluations remain unrun; no market observations were added. F05–F08 original source and definition preparation is proceeding with authorized Astra agents at low effort.

## Subsequent foundation engineering evidence

F05–F08 passed all 417 methods on its first shared run after the collected review
and consolidated repair. The subsequent [F09–F12 execution](validation/F09_F12_EXECUTION.md)
passed all 563 methods on its first shared run, with zero failures/errors/skips,
59.22 CPU seconds and 219.55 MiB peak RSS. Every frozen case, original source-case
binding, repair disposition, successful method and metric payload is retained.
These exact service assertions address the recorded foundation defects. They do
not close native/cohort, source-specific generator, complete consumer or economic
phases. The source preparation queue now proceeds to faithful C01/L01,
M12/L02/L03 and V01/V02 contracts; B00 reward/capability work and the exact-E0
data dependencies remain explicit.
