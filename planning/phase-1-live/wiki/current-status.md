# Phase 1 implementation and empirical status

<!-- phase1-strategy-current -->
Current strategy reconstruction: **66 setups, 258 no-setup rejections and 0 unavailable market-input candidates** in the declared evaluation sample. Context and research units are separate.

Personal size, account limits and executed-order records do not gate setups. Auction states, QQQ gamma/key levels, P-zones and macro context have explicit source-inspired implementations. A no-setup rejection is not a losing trade or a software failure.

[Completion report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/COMPLETION_REPORT.md) · [Strategy results](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/STRATEGY_RESULTS.md) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) · [Charts](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/charts/README.md).

Validation: 803 passed, 36 subtests passed in 110.74s (0:01:50); 776 completed jobs across all 58 branch/extra units; 77 primary charts visually checked.
<!-- /phase1-strategy-current -->

## Preserved v2 source-audit baseline

The following section records the earlier, broader source-audit scope. Its personal-record requirements and p/f/u counts are historical comparisons; the strategy scope and current classifications above supersede them.

<!-- phase1-native-v2-current -->
## Current completion — native replay v2

Current registry/run v2.0.0 is accepted under identity `1ab8b9d7eb2e8aa36c053033754aac854908a2e90373457fb730671329dc5a60`. All **776 declared jobs** completed across the seven-date pilot and seven-date evaluation sample, with all **50 branches and eight additional units** retained. This is a bounded annual engineering/research sample, not a full-archive census. Pilot/evaluation overlap and prior outcome exposure are explicit; their counts are never pooled.

The implementation uses owned MBP-1 event-time executions, same-contract references and a versioned NQ session policy. Author-exact selections, actual orders/fills and account records remain separate. **Software completion does not establish full historical author-method measurement or profitability.**

[Current completion report and reproduction commands](/workspace/implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md) · [Current branch results](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/RESULTS.md) · [Authoritative branch/object/operand manifest](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/registry/coverage.json) · [Diagnostic chart index](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/charts/README.md)

Validation: **773 passed, 36 subtests passed in 119.44s (0:01:59)**; 5 shared-contract, 1316 object and 169 method controls; 50 selected predicate controls; three actual native future-perturbation checks; 27 audit and six lifecycle regressions; the upstream reaction/HVN probe rejects reuse of the reaction period as an independent HVN; timestamp-tie and unknown-aggressor controls preserve independently computable prices and volume. Every chart in the 90-chart diagnostic set was visually inspected. Exact acceptance evidence is in [ACCEPTANCE.json](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/ACCEPTANCE.json).

Remaining external/input limits are operand-specific: dated P-zone/KG1 or gamma inputs for the branches that need them; actual account, selected-order, state/transition and management/re-entry records; unpublished scalp automatic admission and source macro cycle/C-score rules. Observable market stages and numerical macro/risk operations remain available independently. Historical NQ holiday archives could be located but CME blocked automated downloads; unverified holiday scope and same-contract history gaps remain explicit. The July 2020 two-hour interval remains unknown, and quote activity is not a feed-continuity certificate.

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR | v2 bounded native research | 52 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/JJ-TBR.md |
| GB-FAIL | v2 bounded native research | 68 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/GB-FAIL.md |
| GB-VWAP | v2 bounded native research | 2 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/GB-VWAP.md |
| GB-SCALP | v2 bounded native research | 0 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/GB-SCALP.md |
| SIRES | v2 bounded native research | 69 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/SIRES.md |
| SAINT-AMT | v2 bounded native research | 17 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/SAINT-AMT.md |
| MEMBER-TWO-REASONS | v2 bounded native research | 2 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/MEMBER-TWO-REASONS.md |
| KEANI-OPEN-ABOVE-VALUE | v2 bounded native research | 6 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/KEANI-OPEN-ABOVE-VALUE.md |
| REFILL-STUDY | v2 bounded native research | 0 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/REFILL-STUDY.md |
| JETBUNDLE-STATES | v2 bounded native research | 0 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/JETBUNDLE-STATES.md |
| STOIC-DATA | v2 bounded native research | 1 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/STOIC-DATA.md |
| STOIC-RISK | v2 bounded native research | 0 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/STOIC-RISK.md |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| JJ-TBR | M01 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| GB-FAIL | M02 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| GB-VWAP | M03 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| GB-SCALP | M04 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| SIRES | M05 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| SAINT-AMT | M06 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| MEMBER-TWO-REASONS | M07 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| KEANI-OPEN-ABOVE-VALUE | M08 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| REFILL-STUDY | M09 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| JETBUNDLE-STATES | M10 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| STOIC-DATA | M11 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| STOIC-RISK | M12 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |

<!-- /phase1-native-v2-current -->

## Preserved pre-v2 status and definition corrections

The declared empirical v1 jobs finished on 2026-09-12. **That does not mean every defined method has a historical scanner or was empirically tested.** The source wiki, implemented episode checks, automated discovery and market-data coverage have different completion states. See [PHASE](../PHASE.md) for current work and the [method index](index.md) for the definitions.

## Correction: definitions exist; 18 branches were not scanned

Reviewed 2026-09-13. All 18 branches labelled `unavailable_definition` in the frozen registry have documented source sequences in this wiki: five [Jumbo branches](method-jumbo-tbr.md#definition-and-scanner-correction--2026-09-13), eleven [Sires branches](method-sires-thesis-flow.md#definition-and-scanner-correction--2026-09-13) and two [member branches](method-member-two-reasons.md#definition-and-scanner-correction--2026-09-13). Their method predicates also exist in the implementation. The legacy label is not evidence that their PDFs, raw posts or definitions are missing.

The cause is visible in [registry construction](/workspace/implementation/src/trading_research/research/method_pack/empirical_registry.py): membership in the 19-entry `SPECS` comparison map controls `supported`; most other branches default to `unavailable_definition`. Their references are reduced to a method-level FORMULAS pointer. The [runner](/workspace/implementation/src/trading_research/research/method_pack/empirical_runner.py) schedules only supported rules. The [flow sequence producers](/workspace/implementation/src/trading_research/research/method_pack/objects/flow_sequences.py) check already selected episodes and observations; those checks are not an end-to-end historical discovery pipeline. Family reporting also falls back to the same misleading label when no measured branch exists.

Read these dimensions separately:

| Dimension | What the evidence establishes |
|---|---|
| Source definition | The branch sequence is documented and cited. A missing automatic scanner must not erase it. |
| Episode evaluator | Code checks supplied or derived stages, identities and ordering. Passing fixtures establishes those checks, not discovery of historical episodes. |
| Historical discovery | These 18 branches have no scanner registered in empirical v1. Their historical populations were not searched. This is an implementation/scope limitation. |
| Operational choices | Some qualitative context, profile selection or pace criteria still need precise, cited treatment. Any research choice must be identified individually; it does not make the whole definition absent. |
| Data or external calculation | A specific depth field, platform setting, historical level or proprietary formula may be unavailable. Prove that at the affected input; do not call all order flow private or infer absence from the standalone-trade schema. Local MBP-1 includes executions and best-level book updates from 2020. |

Two particularly clear registry overstatements are corrected on the method pages: the Sires clean-squeeze sequence is published in CONT p.11; Jumbo's manual formation clocks are printed in TBR p.7. STOP pp.10, 12 and 14 also explicitly give its stages and numerical checks. P-zone generation and KG1 generation remain distinct, specifically identified calculation limitations; their documented usage sequences still exist.

This is a correction to the live explanation, not a new empirical result. Frozen registry bytes and historical reports retain their original labels for reproducibility. No new scanner has been implemented or outcome replay performed by this documentation correction. Implementation follow-up must derive observable stages from the available native data and identify only the remaining input or parameter gaps, branch by branch.

## What is complete

The [implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md), [obligation matrix](/workspace/implementation/validation/phase1-completion/obligation-matrix.json) and [post-implementation repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) cover 166 object contracts, 9 shared contracts, 12 method contracts and 373 operand bindings. Native and parent-derived producers, supplied-record admission, causal assembly and lifecycle checks exist. Each object page now links to its current contract and code. A supplied-only contract is implemented even when the actual proprietary or private record required to instantiate it is absent.

The [empirical completion report](/workspace/implementation/reports/phase1-live/empirical/COMPLETION_REPORT.md) accounts for all 165 selected date jobs and 2,274 rule/date assignments, with zero pending work in that frozen scope. It evaluates 19 explicit research-comparison definitions and records 31 other branch dispositions, covering all 50 catalog branches. Eight additional management, re-entry, state, process and risk observation units retain their own supplied-only denominators. [Readable rules](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md) distinguish assumptions from source statements.

The integrated empirical acceptance passed 736 tests, the retained baseline and repair probes, 27 independent audit cases, five quantity regressions and review of 50 selected charts. [Verification](/workspace/implementation/reports/phase1-live/empirical/validation/FINAL_VERIFICATION.json) and [independent review](/workspace/implementation/reports/phase1-live/empirical/validation/FINAL_EMPIRICAL_REVIEW.md) retain the precise tested identities and scope. The [wiki reconciliation record](/workspace/implementation/reports/phase1-live/wiki-reconciliation/README.md) documents the later documentation checks.

## What the historical run actually measured

The frozen sample selected the first eligible covered native NQ bar session in each retained month: 161 dates across 2010–2026. Four additional standalone-trade dates cover 2021, 2022, 2023 and 2026. Source/calibration dates and detected prior-inspection dates were excluded using the frozen selection rules; the 2024–2025 tape dates were already exposed. This is a coverage-selected sample, not every session in the acquired archive. Prior exposure is incompletely knowable, and reporting revisions record outcome exposure. [Coverage and splits](/workspace/implementation/reports/phase1-live/empirical/coverage/README.md) and the [run manifest](/workspace/implementation/reports/phase1-live/empirical/RUN_MANIFEST.json) identify the exact dates and inputs.

There are 2,452 recorded comparison opportunities: 1,000 pass, 1,412 fail and 40 unknown (`n = p + f = 2,412`; `N = p + f + u = 2,452`). The unknowns include 30 censored and 10 ambiguous records. Passing endpoints produce 1,000 nested comparison signals. These additive counts combine different branch populations; they are neither distinct trades nor a pooled success rate. Actual source selections, attempts, orders and fills remain unavailable. Every complete source-method verdict remains unknown, and faithful disagreements remain null. [Results by branch, year and native contract](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) retain the compatible denominators and labelled observed rates.

The [PHASE and audit tables](/workspace/implementation/reports/phase1-live/empirical/PHASE_AND_AUDIT_TABLES.md) retain all family, branch and extra-unit dispositions. The run reports zero timing violations and zero proxy-as-faithful admissions. Those checks do not establish profitability or causal trading efficacy.

## Evidence that remains unavailable

Of 2,274 rule/date assignments, 1,535 completed, six completed with population holes and 733 retained missing-data dispositions. At least one input is missing in 157 of the 165 date jobs; valid observations from those dates remain visible. The completed scope therefore correctly retains `data_hole`.

- Prior reference windows, same-contract histories, trade/profile coverage and adjacent-minute reconciliation remain incomplete in specified partitions. An unobserved search does not count as a completed zero-opportunity day.
- [Keani](method-keani-open-above-value.md) has four observed openings and four unknown opening-above-value classifications because required prior profiles are unverified. [Refill](method-refill-effect.md) has one verified zero-zone search in 2023 and three tape searches with coverage holes. The tape-dependent [Saint](method-saint-amt.md) routes preserve missing profile, reference or delta dispositions.
- Proprietary platform settings, source selectors and readouts remain unavailable where unpublished. Examples include Jumbo's EV/P-zone/Stat+ engines, source gamma/KG1 maps, the Refill classifier and the jetbundle state classifier. Implemented admission of a supplied record does not recover the underlying private calculation.
- Thesis, selection, order, fill, account and management histories require their actual linked records. NQ comparison data cannot establish an MNQ execution. The [Green Bird November 2025 sweep entry](method-green-bird-failure.md) is distinguished from its later MSS/FVG annotation; the July 23 Sires caption/attempt conflict remains explicit in [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

The [evidence review](/workspace/implementation/reports/phase1-live/evidence-review-v1/README.md) and [data recovery follow-up](/workspace/implementation/reports/phase1-live/data-recovery-v1/README.md) have since been completed within their stated scope. They identified the mixed-clock validation error, actual 2020 MBP-1 coverage and recoverable August bars. The clock correction and the absent branch scanners remain implementation work. Any broader sample or changed detector needs a separately declared version and exposure record.

## Current wiki and the frozen run

Empirical registry 1.0.0 hashes all 190 wiki pages that existed when it was frozen, alongside four executable definition files. Updating the live wiki changes that input identity. The historical registry and acceptance have been preserved; the ordinary live validator deliberately rejects the old registry against these newer pages. A future registry must be frozen explicitly against its actual current inputs.

The [definition snapshot](/workspace/implementation/reports/phase1-live/wiki-reconciliation/FROZEN_DEFINITIONS.json) preserves all 194 exact files from accepted commit `8449573`. The archival check verifies every snapshot hash, binds only the definition root to those historical bytes, and runs the original acceptance assertions against unchanged executable and market inputs:

```sh
cd /workspace
PYTHONPATH=implementation/src implementation/.venv/bin/python implementation/reports/phase1-live/wiki-reconciliation/verify_frozen_empirical.py
```

Its [verification record](/workspace/implementation/reports/phase1-live/wiki-reconciliation/VERIFICATION.json) identifies every changed or added wiki page. This verifies the historical run in its historical definition context; it does not claim that the updated wiki was part of the earlier freeze or weaken the live drift checks.

This status page is a research record, not a standalone trade. [Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source catalog and precedence](source-catalog.md) · [Ingest log](log.md)
