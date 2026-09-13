<!-- full-phase1-measurement-current -->
# Phase 1 — full acquired historical measurement

The unchanged versioned scanners searched **1,742 declared session dates**, 2020-01-01 through 2026-09-03, across all 50 branches and eight additional observation units. The composed census contains **99,294 daily jobs** and **18,747 qualifying market setups**, plus three actual collection-process jobs. The independent primary run and all 90 calendar-recovery dates completed and were verified.

**The acquired observed-input census is executed. Input-limited populations remain unmeasured beyond the observed subset; the exact affected branch/session denominators are listed below.** Qualification does not establish a winning trade. All reported outcomes are subsequent observed prices; no return simulation or actual fill is claimed. Phase 2 remains the additional context layer that selects which setups to use.

[Current measurement report](/workspace/implementation/reports/phase1-live/historical-measurement/MEASUREMENT_REPORT.md) · [Charts](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/charts/README.md)

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR | full acquired historical measurement | 3912 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/JJ-TBR.md |
| GB-FAIL | full acquired historical measurement | 7589 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-FAIL.md |
| GB-VWAP | full acquired historical measurement | 499 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-VWAP.md |
| GB-SCALP | full acquired historical measurement | 3066 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-SCALP.md |
| SIRES | full acquired historical measurement | 2538 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/SIRES.md |
| SAINT-AMT | full acquired historical measurement | 785 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/SAINT-AMT.md |
| MEMBER-TWO-REASONS | full acquired historical measurement | 352 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/MEMBER-TWO-REASONS.md |
| KEANI-OPEN-ABOVE-VALUE | full acquired historical measurement | 6 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/KEANI-OPEN-ABOVE-VALUE.md |
| REFILL-STUDY | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/REFILL-STUDY.md |
| JETBUNDLE-STATES | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/JETBUNDLE-STATES.md |
| STOIC-DATA | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/STOIC-DATA.md |
| STOIC-RISK | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/STOIC-RISK.md |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| JJ-TBR | M01 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| GB-FAIL | M02 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| GB-VWAP | M03 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| GB-SCALP | M04 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| SIRES | M05 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| SAINT-AMT | M06 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| MEMBER-TWO-REASONS | M07 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| KEANI-OPEN-ABOVE-VALUE | M08 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| REFILL-STUDY | M09 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| JETBUNDLE-STATES | M10 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| STOIC-DATA | M11 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| STOIC-RISK | M12 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
<!-- /full-phase1-measurement-current -->

## Preserved implementation and prior measurement history

# Phase 1 — current status and reading guide

**Phase boundary clarified by the user (2026-09-13): Phase 1 includes both setup implementation and historical measurement. Phase 2 is the context layer that selects which setups to use.** The implementation and bounded engineering replay below are complete; they do not complete the broader Phase 1 measurement work.

The next work remains in Phase 1: use the frozen setup implementations across the declared NQ 2020+ study, measure setup frequency and subsequent outcomes with explicit denominators and coverage, and publish per-setup evidence. Source-required context already inside a setup remains part of its definition. Developing an additional context-based selector across setups belongs to Phase 2. Do not move unfinished setup measurement into Phase 2 or rerun completed implementation work merely because the phase status was corrected.

<!-- phase1-strategy-current -->
Current strategy reconstruction: **66 setups, 258 no-setup rejections and 0 unavailable market-input candidates** in the declared evaluation sample. Context and research units are separate.

Personal size, account limits and executed-order records do not gate setups. Auction states, QQQ gamma/key levels, P-zones and macro context have explicit source-inspired implementations. A no-setup rejection is not a losing trade or a software failure.

[Completion report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/COMPLETION_REPORT.md) · [Strategy results](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/STRATEGY_RESULTS.md) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) · [Charts](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/charts/README.md).

Validation: 803 passed, 36 subtests passed in 110.74s (0:01:50); 776 completed jobs across all 58 branch/extra units; 77 primary charts visually checked.

### PHASE lines

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR | strategy reconstruction v1 | 90 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/JJ-TBR.md |
| GB-FAIL | strategy reconstruction v1 | 84 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/GB-FAIL.md |
| GB-VWAP | strategy reconstruction v1 | 3 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/GB-VWAP.md |
| GB-SCALP | strategy reconstruction v1 | 12 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/GB-SCALP.md |
| SIRES | strategy reconstruction v1 | 96 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/SIRES.md |
| SAINT-AMT | strategy reconstruction v1 | 26 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/SAINT-AMT.md |
| MEMBER-TWO-REASONS | strategy reconstruction v1 | 7 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/MEMBER-TWO-REASONS.md |
| KEANI-OPEN-ABOVE-VALUE | strategy reconstruction v1 | 6 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/KEANI-OPEN-ABOVE-VALUE.md |
| REFILL-STUDY | strategy reconstruction v1 | 0 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/REFILL-STUDY.md |
| JETBUNDLE-STATES | strategy reconstruction v1 | 0 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/JETBUNDLE-STATES.md |
| STOIC-DATA | strategy reconstruction v1 | 0 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/STOIC-DATA.md |
| STOIC-RISK | strategy reconstruction v1 | 0 | not claimed | executed; reconstructed setup scope | implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/STOIC-RISK.md |

### Audit lines

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| JJ-TBR | M01 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| GB-FAIL | M02 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| GB-VWAP | M03 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| GB-SCALP | M04 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| SIRES | M05 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| SAINT-AMT | M06 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| MEMBER-TWO-REASONS | M07 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| KEANI-OPEN-ABOVE-VALUE | M08 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| REFILL-STUDY | M09 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| JETBUNDLE-STATES | M10 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| STOIC-DATA | M11 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
| STOIC-RISK | M12 | source logic + replay checked | pass | 0 | 0 | inferred models identified; private execution excluded; no profit claim |
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

## Historical status before the native v2 implementation

Reviewed against repository `f8b14ef` on 2026-09-13. **The declared empirical run and contracted episode checks are complete; historical discovery for every defined method is not.** In particular, 18 documented branches were labelled `unavailable_definition` because they were outside the registered scanner scope. See the [definition/scanner correction](wiki/current-status.md#correction-definitions-exist-18-branches-were-not-scanned). Later evidence review and data recovery are follow-on work. The event-time aggregation/validation correction has been diagnosed but has not been implemented in the production pipeline.

This is the entry point for current status and document routing. It replaces the former `method-pack-v1` implementation plan, which incorrectly remained labelled “commands not implemented” after completion. That plan remains available in Git history at `f8b14ef:planning/phase-1-live/PHASE.md`.

## Read only these first

1. **This page:** what exists, what is complete, what remains open, and which document owns each question.
2. **[Live method wiki](wiki/index.md):** the 12 readable method explanations, their source attribution, implemented objects, empirical branch observations and remaining source holes.
3. **[Accepted empirical results](../../implementation/reports/phase1-live/empirical/RESULTS.md):** measured outcomes of the frozen research comparisons, with their actual denominators and missing-data treatment.
4. **[Latest data recovery and clock correction](../../implementation/reports/phase1-live/data-recovery-v1/README.md):** the subsequent local investigations, recovered August bars, 2020 MBP-1 coverage and unresolved clock/coverage issues.

Use the deeper files below only when their question matters. “Historical” means evidence for a particular earlier run; it does not mean the evidence should be deleted or its verdict rewritten.

## Which document owns what?

| Question | Read | Role and currency |
| --- | --- | --- |
| What is the overall current state? | This `PHASE.md` | Current entry point. |
| What does each author describe, and what have we implemented/measured? | [wiki/index.md](wiki/index.md) and its 12 method pages | Current readable method explanations, reconciled after empirical acceptance. Source text and comparison assumptions remain distinct. |
| How are objects, procedures and evidence contracts defined? | [FORMULAS.md](FORMULAS.md) | Retained `method-pack-v1` object/procedure contract: C00–C08, M01–M12, O001–O166. It is not the empirical candidate-selector book or current progress log. |
| Exactly what did the empirical scanner select and score? | [CANDIDATE_REGISTRY.json](../../implementation/reports/phase1-live/empirical/registry/CANDIDATE_REGISTRY.json), with [CANDIDATE_RULES.md](../../implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md) for reading | Frozen comparison definitions, assumption IDs and unavailable-branch dispositions. The Markdown header records the original freeze; the accepted run identity is in RUN_MANIFEST, not that old header. |
| Which dates, instruments, inputs and implementation were used? | [RUN_MANIFEST.json](../../implementation/reports/phase1-live/empirical/RUN_MANIFEST.json) and its linked splits | Accepted run v1.0.2. This controls the completed sample, not a general study preference or today's available-data inventory. |
| What were the empirical results? | [RESULTS.md](../../implementation/reports/phase1-live/empirical/RESULTS.md) and [COMPLETION_REPORT.md](../../implementation/reports/phase1-live/empirical/COMPLETION_REPORT.md) | Current accepted run results. These are research observations, not author rules, actual trades or P&L. |
| What do the denominators and charts support? | [evidence-review-v1/README.md](../../implementation/reports/phase1-live/evidence-review-v1/README.md) | Completed branch/denominator/chart review. Its recovery priorities were subsequently investigated in data-recovery-v1. |
| What did the recovery investigations find? | [data-recovery-v1/README.md](../../implementation/reports/phase1-live/data-recovery-v1/README.md) | Latest findings, including the event-clock/2020 MBP-1 follow-up. Input recovery is separate from a new outcome replay. |
| Why do live wiki files differ from the frozen run? | [wiki-reconciliation/README.md](../../implementation/reports/phase1-live/wiki-reconciliation/README.md) | Historical verification bridge. FROZEN_DEFINITIONS.json identifies the exact 194 historical definition files; it is not a new assumptions book. |
| What did the earlier source-method pass establish? | [methods/index.md](../../implementation/reports/phase1-live/methods/index.md), method reports and dated audits | Historical source-method/fixture reports, including stages before repairs and empirical comparisons. Their source_hole/n=0 does not override later comparison results. |
| How was the completed work commissioned and performed? | [SOURCE_CALIBRATION_DISCOVERY_HANDOFF.md](SOURCE_CALIBRATION_DISCOVERY_HANDOFF.md), [EMPIRICAL_PROGRESS.md](EMPIRICAL_PROGRESS.md) | Executed handoff and chronological log. Earlier “working,” “not started,” and “next” statements are historical, not current instructions. |
| What about PRD, SPEC and older recipe findings? | [PRD.md](PRD.md), [SPEC.md](SPEC.md), [RULES.md](RULES.md), [FINDINGS.md](FINDINGS.md), tickets and older object-family reports | Prior requirements and earlier object/recipe experiments. Consult for provenance; do not use their progress claims, candidate populations or rates as current empirical acceptance. FORMULAS retains its specific contract role above. |
| What about the 85-model research project? | [RESEARCH_BUILD_SPEC.md](RESEARCH_BUILD_SPEC.md) and research-spec/ | Separate deferred specification. It does not authorize starting those engines or Phase 2 as part of continuing this completed Phase 1 run. |
| What does the NQ 2020 study scope mean? | [DATA_SCOPE.md](DATA_SCOPE.md) | Records the NQ/2020-onward study preference and conditional peer inputs. The accepted frozen bar sample nevertheless contains 2010–2026 dates. Keep that scope difference explicit; do not silently relabel or rerun the accepted sample. |

## What exists and what finished

- `implementation/tools/run_phase1_objects.py` exposes **check, run, report and method-pass**. The method-pass interface was implemented; the old plan's contrary statement was stale. Its source-method audit is distinct from the research-comparison scanner.
- `implementation/tools/run_phase1_empirical.py` exposes **calibrate, freeze, revise-reporting, validate, run and report**. It owns the separately frozen empirical jobs.
- The accepted sample completed **165 date jobs**: 161 monthly native-bar jobs and four annual standalone-trade jobs. All **2,274 rule/date assignments** were processed; no unscanned jobs remain.
- The observed records total **2,452**: 1,000 pass, 1,412 fail and 40 unknown, giving resolved n=2,412. These are additive audit counts across dependent, different populations; no pooled strategy rate is implied.
- There are **19 supported comparisons**, 31 other branch dispositions and eight separate observation units. Of those 31 dispositions, **18 have source definitions but no registered historical scanner**; the legacy `unavailable_definition` label conflates these facts. Complete source-method verdicts remain unknown. A supported comparison does not establish the full documented method.
- **733 assignments have missing inputs** and six have partial populations. Completion means all declared searches received the correct disposition, not that every underlying input is available.
- Accepted validation includes **736 tests and 36 subtests**. Later report/data-audit verification is separate evidence, not another full test-suite or outcome replay.

[PHASE and audit tables](../../implementation/reports/phase1-live/empirical/PHASE_AND_AUDIT_TABLES.md) retain the complete family/branch breakdown. Exact accepted manifest: `d80935d548abe3cafcd695ec842dc69b1d3391646c2da8fe0db9e935a6c37247`.

## Latest follow-on findings and remaining work

The four audited tape windows contain identical standalone-trade and MBP-1 execution multisets (946,027 executions). The code already groups these executions by event time, but its coverage check requires exact agreement with vendor bars whose documented buckets use receive time. This validation assumption is inappropriate for proving event-time tape completeness. A consistent event-time reconstruction and revised validation remain **proposed, not implemented**.

Local NQ MBP-1 begins in January 2020; the separate trade files begin in September 2021; bars extend to September 2010. Of 10,393 audited missing overnight minute slots, 10,270 predate MBP-1 and 123 overlap it. Three isolated minutes show book activity without executions; a two-hour block remains unresolved. Missing bars must not automatically be called lost executions or proven no-trade intervals.

A separately stored 780-row reconstruction from native one-second bars completes the August 2026 prior-month bar reference. It has **not** been used in a new outcome replay. Contract-roll and historical-calendar issues remain documented. See the latest recovery report for exact receipts and limitations.

Existing raw data is read-only, ignored and never committed. Any future reconstruction must use a separate derived dataset with source identity and provenance. Preserve accepted raw inputs, frozen definitions and prior results; record a new input/implementation version before a follow-on replay. Do not rerun 165 jobs merely to refresh documentation.

## Continuing from here

For the next implementation task, use [IMPLEMENTATION_FINISH_HANDOFF.md](IMPLEMENTATION_FINISH_HANDOFF.md). It consolidates the final integration review into a work order covering discovery, complete observable sequences, event-time data, existing recoveries, versioned replay and acceptance. It is not a new source-definition authority.

For documentation maintenance, use this page for status, the live wiki for the 12 method explanations, and the frozen registry for comparison assumptions. Do not copy research defaults into FORMULAS as author text or substitute RESULTS for source law. A second manually maintained ASSUMPTIONS book would duplicate the existing registry/rule guide; any future readable view should be generated from those definitions and link its exact version.

For code work, outstanding issues include consistent event-time reconstruction/validation, explicit quiet-minute versus unknown-coverage handling, and historical discovery for documented branches excluded by the current scanner. Start from their existing wiki definitions and implemented objects; identify exact remaining operational choices or inputs instead of declaring the source method unavailable. No Phase 2, 85-model expansion, parameter tuning or unpublished-engine reconstruction is active.

The historical empirical registry hashes older wiki bytes. Ordinary live validation intentionally rejects drift against today's wiki. For the completed run's archival verification, follow [wiki-reconciliation/README.md](../../implementation/reports/phase1-live/wiki-reconciliation/README.md); do not “fix” drift by rewriting the frozen registry hashes. The command lists in empirical/COMMANDS.md describe the original lifecycle, not a checklist to rerun now.
