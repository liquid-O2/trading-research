# Phase 1 native implementation completion — 2026-09-13

Current registry/run v2.0.0 is accepted under identity `1ab8b9d7eb2e8aa36c053033754aac854908a2e90373457fb730671329dc5a60`. All **776 declared jobs** completed across the seven-date pilot and seven-date evaluation sample, with all **50 branches and eight additional units** retained. This is a bounded annual engineering/research sample, not a full-archive census. Pilot/evaluation overlap and prior outcome exposure are explicit; their counts are never pooled.

The implementation uses owned MBP-1 event-time executions, same-contract references and a versioned NQ session policy. Author-exact selections, actual orders/fills and account records remain separate. **Software completion does not establish full historical author-method measurement or profitability.**

[Current completion report and reproduction commands](/workspace/implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md) · [Current branch results](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/RESULTS.md) · [Authoritative branch/object/operand manifest](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/registry/coverage.json) · [Diagnostic chart index](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/charts/README.md)

## Implemented and verified

The existing discovery route now dispatches the authoritative 50-branch/eight-unit manifest into the existing method evaluator and domain producers. The manifest reconciles 166 object interfaces and 373 operand bindings. Each job retains actual operand derivations, ordered stages, domain receipts, native input membership and separate post-sequence observations. Registration and logic fixtures are not counted as native discovery evidence. Actual supplied process records enter through the existing complete causal assembly.

Owned monthly/weekly spans prevent source overlap duplication while preserving repeated executions and equal-timestamp batches. Only T events contribute volume, profile, VWAP and delta. Vendor receive-clock candles remain distinct diagnostics. The event cache is immutable and versioned under ignored data paths; source/cache hashes are revalidated on checkpoint reuse. No flat candle or full-feed claim is created from quote activity.

Native integration freshly reconciled eight current/prior tape windows, including truncated September 2021 and its prior day. All 12,420 recovered 2020+ minute keys were admitted with native-source checks; 780 August rows are equal overlaps and are not added twice. The 32 pre-2020 keys stay outside the denominator. The 829-minute event tail was independently rebuilt and matched. Vendor recovery retains its own clock and supplies separate diagnostic evidence. Method candles come from T executions. The macro path admits the existing 20-series/37,003-vintage bundles and computes available initial CPI/payroll comparisons without inventing a source C-score.

Validation: **773 passed, 36 subtests passed in 119.44s (0:01:59)**; 5 shared-contract, 1316 object and 169 method controls; 50 selected predicate controls; three actual native future-perturbation checks; 27 audit and six lifecycle regressions; the upstream reaction/HVN probe rejects reuse of the reaction period as an independent HVN; timestamp-tie and unknown-aggressor controls preserve independently computable prices and volume. Every chart in the 90-chart diagnostic set was visually inspected. Exact acceptance evidence is in [ACCEPTANCE.json](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/ACCEPTANCE.json).

Remaining external/input limits are operand-specific: dated P-zone/KG1 or gamma inputs for the branches that need them; actual account, selected-order, state/transition and management/re-entry records; unpublished scalp automatic admission and source macro cycle/C-score rules. Observable market stages and numerical macro/risk operations remain available independently. Historical NQ holiday archives could be located but CME blocked automated downloads; unverified holiday scope and same-contract history gaps remain explicit. The July 2020 two-hour interval remains unknown, and quote activity is not a feed-continuity certificate.

## Scope, exposure and preservation

Evaluation: 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-02, 2024-01-02, 2025-01-02, 2026-01-02. Pilot: 2020-01-02, 2021-09-01, 2022-01-03, 2023-01-03, 2024-01-02, 2025-01-02, 2026-09-01. All 58 units have completed dispatch evidence; collection-process units use one actual collection review per cohort. Missing records retain empty actual-record populations and exact limits. Observed sequence unknowns remain separate from population-scope uncertainty.

Research assumptions and coverage-independent dates were frozen before new outcomes. Development results and earlier stopped run attempts are disclosed in the final registry; serialization, unknown-handling, selected-branch binding, file-verification efficiency and chart corrections did not change sample dates or thresholds. This is outcome-exposed engineering verification, not an untouched holdout.

All 745 recorded historical empirical artifacts are unchanged. The accepted v1.0.0/v1.0.2 manifest remains `d80935d548abe3cafcd695ec842dc69b1d3391646c2da8fe0db9e935a6c37247`. Initial uncommitted documentation corrections are retained in the source/history sections; raw data and unrelated untracked files remain untouched. No commit or paid acquisition was performed.

The supplemental reaction/HVN regression is retained at [member-independence.json](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/validation/member-independence.json) with its executable input probe.

A supplemental [prior-month reference chart](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/diagnostics/prior-month-detail/charts/GB-FAIL--branch--prior_month_level--no_observed_candidate.png) uses the final declared pilot date to show distant reference levels while preserving local price detail; it does not change a population or verdict.

## Reproduction

Runtime: {'matplotlib': '3.11.2', 'numpy': '2.3.3', 'pyarrow': '25.0.1', 'pypdf': '6.18.1', 'pytest': '9.1.1', 'python': '3.12.3'}. The new-root chart set needs its own visual review and VISUAL_QA receipt before acceptance; a prior QA receipt must not be copied. Freeze rejects different code/tests/policy on resume.

```bash
cd /workspace
export PYTHONPATH=/workspace/implementation/src
# In a Python environment matching the recorded Python version:
python -m pip install -e './implementation[data,research,charts,test]' -r /workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/validation/replay-runtime.txt
# Verify/reprint this accepted run; selected run root is mandatory.
python implementation/tools/run_phase1_objects.py historical-replay verify --run-root /workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9
python implementation/tools/run_phase1_objects.py historical-replay report --run-root /workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9
python /workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/validation/member_independence_probe.py
python /workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/validation/resume_probe.py --run-root /workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9
# Resume the exact immutable jobs; completed jobs are revalidated.
python implementation/tools/run_phase1_objects.py historical-replay run --run-root /workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9 --cohort pilot --workers 2
python implementation/tools/run_phase1_objects.py historical-replay run --run-root /workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9 --cohort evaluation --workers 2
# A new independent replay must have a new root. Freeze before running.
python implementation/tools/run_phase1_objects.py historical-replay freeze --run-root /workspace/implementation/reports/phase1-live/implementation-v2/reproduction
python implementation/tools/run_phase1_objects.py historical-replay run --run-root /workspace/implementation/reports/phase1-live/implementation-v2/reproduction --cohort pilot --workers 2
python implementation/tools/run_phase1_objects.py historical-replay run --run-root /workspace/implementation/reports/phase1-live/implementation-v2/reproduction --cohort evaluation --workers 2
python implementation/tools/validate_phase1_native_replay.py --run-root /workspace/implementation/reports/phase1-live/implementation-v2/reproduction --part all
python implementation/tools/run_phase1_objects.py historical-replay report --run-root /workspace/implementation/reports/phase1-live/implementation-v2/reproduction
python implementation/tools/chart_phase1_native_replay.py --run-root /workspace/implementation/reports/phase1-live/implementation-v2/reproduction
# Inclusive all-year capability, with every calendar date retained:
python implementation/tools/run_phase1_objects.py historical-replay freeze --run-root /workspace/implementation/reports/phase1-live/implementation-v2/range-reproduction --date-from 2020-01-01 --date-to 2026-09-03
```

## Family reports

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
