# Implementation review after the research reroute

Snapshot: **2026-09-07, 19:09 UTC**. This is a review of source changes and saved execution evidence, not a new test, market-data extraction or model run. The implementation was still changing during the review.

**Assessment:** the implementation has adopted the revised scope and produced useful research infrastructure and actual observations. It still has avoidable rework around execution gates, performance estimates, data representation and reporting. No complete family study, independently evaluated Context model or Location-quality study has been delivered. Restarting the project or weakening the calculations would lose useful work; the immediate need is to complete the research path and make its findings readable.

## What changed after the handoff

I compared the current package against the reconstructible source snapshot in the [16:08 transition checkpoint](/workspace/trading-research/reports/research-scope-transition-checkpoint-v1.json), rather than attributing all recent file modification times to the reroute. The existing E0 source matches that checkpoint. The changes to previously existing source are the shared empty-path label correction and its payload propagation, with a corresponding test change. New source work is concentrated in OHLC admission and the Jumbo study.

The empty-path correction is useful: an absent observation no longer becomes a flat, zero-return observation. The separately declared process that carries a certified last observed mark retains its own semantics. See [labels.py](/workspace/trading-research/src/trading_research/research/labels.py:86).

| Work | Evidence and result | Assessment |
|---|---|---|
| Scope transition | E0 paused; previous source, failures and resource records preserved | Appropriate reuse; no evidence of continued E0 expansion after the checkpoint |
| Study definitions and cash calendar | Source range variants, source-specific mechanisms, holiday/early-close context and observation assumptions recorded | Necessary work; source hypotheses and implementation defaults need clearer separation |
| Actual price admission | All 14 NQ/ES yearly partitions, 2020 through the actual 2026-09-02 endpoint: 4,651,730 rows, of which 4,613,232 pass the declared checks | Substantive progress; valid individual rows do not certify every requested window |
| Independent data comparison | All 60 minute OHLCV observations in the retained NQ trade hour match | Useful bounded evidence; not whole-history trade reconciliation |
| Range/path extraction | Complete NQ 2020, 2021 and 2022 annual tables and statistics saved | Three of ten intended development instrument-years; NQ 2023–2024 and ES 2020–2024 remain |
| Numerical verification | Latest check: 142 selected checks pass; optimized extraction/statistics match the preserved reference on 60 actual cash dates, including saved-table and continuation comparisons | Useful verification; does not establish model quality or full-cohort runtime feasibility |
| Context preparation | A new compact model-matrix adapter is being written | No completed fitted or independently scored market model; fit/confirmation dispatch remains unavailable |
| Other families and Locations | Existing partial engineering work remains; no new completed empirical family report or Location-quality result recorded | Still outstanding, not closed by the Jumbo work |

Relevant evidence: [full admission](/workspace/trading-research/reports/jumbo-runs/168628c5d54259758b23057fba9d1c69098f6bc8ab83711c2acf625718b15fc9/execution.json), [saved annual results](/workspace/trading-research/reports/jumbo-runs/f716b22e901d4f6cc9e21a21e1ab1a9493bab62deb73b66f5b1c97721bdbf847/partial-report.md), [latest check](/workspace/trading-research/reports/jumbo-runs/4c5e09291a2ace060ed08f8dd9417ed91b19140060060f8dad18b5ace01ed66e/worker.json), [current fit/confirmation boundary](/workspace/trading-research/src/trading_research/research/jumbo_study.py:290).

## Where the 15-minute opening range came from

The supplied Pine source **IB / ORB Live Stats** sets `orb_minutes = input.int(15, ...)` and identifies its start as 09:30. See the [original source](</workspace/planning/trading-model/review/pine-extracted/Pinescript-indicators--main/IB ORB Live Stats.txt:11>). The earlier plan carried 5/15-minute opening ranges into the source benchmark catalogue while naming 06:00–09:00 NY as the Jumbo baseline: [CONTEXT.md](/workspace/planning/trading-model/components/CONTEXT.md:10). I carried that source item into the planning; I found no user instruction selecting it as the default framework.

The new implementation goes beyond merely retaining the source item:

- It defines `OR15` as 09:30–09:45 New York.
- It hardcodes `OR15` as the shared `opening` anchor for feature comparisons: [jumbo_tables.py](/workspace/trading-research/src/trading_research/research/jumbo_tables.py:448).
- It uses prior OR15 volumes to define the three activity-completed opening-range thresholds: [activity definition](/workspace/trading-research/validation/JUMBO_ANALYSIS_V1.json:2), [state update](/workspace/trading-research/src/trading_research/research/jumbo_tables.py:487).
- It includes OR15 in the four-clock headline excerpt: [report selection](/workspace/trading-research/src/trading_research/research/jumbo_study.py:457).

It is one source comparison among 69 source/corrected clocks, not the entirety of the study. However, its role as the generic opening reference is an implementation choice, not a research finding or user-selected premise. Make the anchor and activity reference explicit choices; retain the source comparison without silently granting it privileged status. A 15-minute **postformation prediction horizon** is a separate parameter.

## Findings that affect efficiency and delivery

### 1. Performance estimates created preventable interruption and rework

The first extraction measured a 30-date extraction sample, but its projection excluded annual statistics. Completed years subsequently cost about 69–70 CPU seconds each, including about 20 CPU seconds of statistics. The ten-year workload therefore did not fit the registered 480-second mode cap. The implementation interrupted the run after saving three complete years; preserving those shards was the right recovery. See the [worker log](/workspace/trading-research/reports/jumbo-runs/f716b22e901d4f6cc9e21a21e1ab1a9493bab62deb73b66f5b1c97721bdbf847/worker.log) and [interruption record](/workspace/trading-research/reports/jumbo-runs/f716b22e901d4f6cc9e21a21e1ab1a9493bab62deb73b66f5b1c97721bdbf847/interruption-review.json).

The next estimate adds the 60-date extraction and reporting costs, divides by 60, then scales by all remaining dates. Reporting has work fixed per group/annual report, so this conflates two different scaling terms. It produced a conservative estimate of **572.71 seconds**, which is not an observed full-run time. See [the calculation](/workspace/trading-research/src/trading_research/research/jumbo_parity.py:201).

The optimized 60-date extraction itself improved from 9.77 to 6.81 CPU seconds, and its statistics from 10.12 to 7.45, with no observed numerical differences in that comparison. A whole-annual projection correction is already written at [jumbo_parity.py](/workspace/trading-research/src/trading_research/research/jumbo_parity.py:221), but no executed result for that correction was present at this snapshot. Do not undertake further optimization solely to satisfy the old extrapolation. Measure the actual unit of work, including serialization, and reuse the three completed years.

### 2. Verification is coupled to the entire package instead of the work being executed

The supervisor requires the exact current whole-package code snapshot to match a successful check before every non-check mode. That snapshot contains **all source, tests, references and configurations**, including code unrelated to extraction. Adding the model adapter therefore invalidates the previous extraction check even when the extractor and its dependencies are unchanged. See [snapshot scope](/workspace/trading-research/src/trading_research/operations/artifacts.py:145) and [matching requirement](/workspace/trading-research/tools/run_jumbo_study.py:226).

Retaining a complete reproducible snapshot is valuable. Treating every unrelated change as loss of applicable verification creates unnecessary coupling between studies. Evidence reuse should depend on the exact relevant algorithm, data, schema, configuration and dependency versions. New consumers still require their own meaningful checks. Within the currently registered workflow, finish the code intended for the next snapshot and consolidate its checks instead of repeatedly adding one piece after each check.

### 3. The remaining attempts need an explicit completion allocation

Six attempts have consumed **474.034484 CPU seconds**, approximately **7.90 CPU minutes**, out of 2,400. Three were checks, two admitted data and one extraction was interrupted. Thus **60% of the attempt allowance is consumed while about 20% of the CPU allowance is consumed**. Four attempts and 1,925.965516 CPU seconds remain.

The saved worker wall times total about 8.28 minutes. These records do not measure assistant reasoning, code writing, review or coordination time, so they do not prove the rest of the elapsed time was idle. They do show that raw computation alone does not explain the delay.

A further narrow check followed by another round of model implementation could exhaust attempts before confirmation. A check/extract/fit/confirm sequence fits four attempts only if the remaining implementation and applicable specifications are ready for that sequence and its measured costs fit. Establish that before another run; do not reset budgets, discard failures, weaken tests or rename the same study to evade its limits.

### 4. The report remains too narrow for the research deliverable

The current design expands 69 source clocks into 81 formation clocks and **433 clock/horizon combinations**. The saved 2020 statistics contain **17,320 path metric summaries plus 232 special-mechanism metric summaries**. Preserving source breadth and uncertainty is useful; those counts are not, by themselves, evidence of waste or research completion.

The human-readable report generator still exposes only four clocks and one statistic: both strict breaches in the following 180 minutes. The rest is largely inside approximately 15 MB of JSON per year. Even after extraction completes, that template will not explain which source claims were supported, how ordering and censoring affect them, what changes by session/year, or what timing comparisons can actually conclude. See [the report template](/workspace/trading-research/src/trading_research/research/jumbo_study.py:486).

Turn the retained calculations into a report organized by research question, with named definitions, denominators, uncertainty, conditional results and unresolved conclusions. Preserve the complete machine-readable tables. Descriptive differences across differently sized ranges and different forecast origins cannot select a better clock; complete the already planned matched-target comparison before claiming timing superiority.

### 5. The model adapter is repairing avoidable loss of representation

The extracted feature table retains a normalized last-known-close position but omits the corresponding exact price and observation timestamp. The model adapter now reconstructs the price through floating-point error bounds and a ratio round-trip test: [exact_known_anchor](/workspace/trading-research/src/trading_research/research/jumbo_matrix.py:32).

The numerical safeguards have a purpose, but this complexity arises because an available exact input was not retained directly. Keep the exact anchor price/time in future table versions. For existing frozen shards, an exact join to the admitted canonical minute or formation close can recover it without weakening precision or rerunning all outcomes. Preserve the original shards and make any supplement explicit.

## Quality issues to carry through completion

- **NQ 2024 metadata:** 33,241 excluded minutes are attributed to conflicting activation/lifetime definitions for the same NQZ4 raw ID/symbol/expiry/tick combination. This is not evidence that all those price values are corrupt. The implementation has preserved the conflict, which is appropriate. Resolve it against actual update/supersession semantics and source values, retaining the original evidence; otherwise report its effect on the late-2024 selection population. See [lineage review](/workspace/trading-research/reports/jumbo-nq2024-definition-lineage-review-v1.json). Other eligible studies can continue.
- **Source clocks versus availability:** the registered OHLC scenario makes a bar available one minute after its end. A completed 06:00–09:00 range therefore normally starts its causal forecast at 09:01; the 180-minute forecast ends at 12:01. That is different from a literal 09:00–12:00 source window. Both definitions need explicit labels; the latency scenario is not measured historical receipt evidence. See [availability](/workspace/trading-research/src/trading_research/data/ohlc.py:712) and [forecast construction](/workspace/trading-research/src/trading_research/research/jumbo_tables.py:444).
- **OHLC observation limits:** retain ambiguous intraminute order, compatible versus definite contact, roll exclusions and censored/no-event populations. Exact trade-order questions still need the appropriate ordered observations. A passing OHLC comparison cannot close those dependencies.

## Recommended continuation

1. Keep the admitted data, completed annual shards, meaningful source cases and corrections. Make OR15's benchmark status and the chosen shared anchors explicit.
2. Consolidate the remaining current-study implementation and verification before consuming another attempt. Verify the annual performance calculation and allocate a feasible completion sequence under the existing bounds.
3. Resume the seven missing development instrument-years from the retained state, then produce a readable question-based Jumbo report and the declared independent model/confirmation results. Preserve unresolved conclusions when evidence is insufficient.
4. Reuse the admitted-table, label and evaluation path for the other families. Advance eligible independent work when a particular formula/feed is unavailable; keep every required Context specialist and Location family visible in the delivery table.

This review changes no implementation source, frozen study protocol, accepted result or consumed budget. It identifies a correction order; it does not certify unexecuted changes or claim that another task has received these findings.
