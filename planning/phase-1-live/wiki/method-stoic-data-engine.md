# Stoic — data engine / quantifying fundamentals

<!-- phase1-strategy-current -->
## Current reconstructed strategy

STOIC-DATA: 0 setup, 0 no setup, 0 unavailable input. Personal execution requirements are excluded from qualification.

[Current method report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/STOIC-DATA.md) · [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md).

| Scope and classification | Observations |
| --- | --- |
| context_or_research:condition_present | 3 |

The preserved source audit below describes its original scope. An inferred level/state is identified as our model; it is not a recovered author label or evidence of an actual trade.
<!-- /phase1-strategy-current -->

## Preserved v2 source-audit baseline

The following section records the earlier, broader source-audit scope. Its personal-record requirements and p/f/u counts are historical comparisons; the strategy scope and current classifications above supersede them.

<!-- phase1-native-v2-current -->
## Current native research implementation — 2026-09-13

Every listed scanner/interface ran for its declared dates or actual collection unit. Source definitions below remain the owner of the method; frozen operational choices are in [the research policy](/workspace/implementation/reports/phase1-live/implementation-v2/RESEARCH_POLICY.json).

Evaluation dates: 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-02, 2024-01-02, 2025-01-02, 2026-01-02. No date was replaced because of missing coverage. `n=p+f`; `N observed=n+u`. A missing population scope is recorded separately from an observed zero.

| Branch/unit | n | p | f | u | Observed scope |
| --- | --- | --- | --- | --- | --- |
| process_review | 1 | 1 | 0 | 0 | bounded_observed_population_measured |
| macro_application | 0 | 0 | 0 | 1 | observed_subset_with_input_limits |
| unit: macro_application | 0 | 0 | 0 | 1 | observed_subset_with_input_limits |

**process_review** — frozen declared process → uniform inclusion → all observations → winner/loser comparison → prior-sample revision. Source: DATA pp.3–4. Scanner: `trading_research.research.method_pack.historical_process_scanners:scan_stoic_data`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

**macro_application** — actual vintage admission → selected indicator historical comparison → supplied custom cycle/C-score/trend interpretation. Source: DATA pp.5–6. Scanner: `trading_research.research.method_pack.historical_process_scanners:scan_stoic_data`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Remaining operand(s) `cycle_and_indicator_rules_recorded`: source custom indicator set/transforms, C-score/cycle/trend formula and historical interpretation. Existing 20-series/37003-vintage bundles are used directly; initial BLS clocks and specified standardized comparisons are available. Source proprietary transforms and non-initial intraday clocks are not supplied by that recovery. Source: DATA pp.5–6;O157–O161.

Inspected local evidence: ['implementation/reports/phase1-live/macro-backfill/verification.json', 'planning/phase-1-live/wiki/c-score.md'].

Recorded scope/record limits: source custom indicator set/transforms, C-score/cycle/trend formula and historical interpretation (1 job records).

**macro_application** — actual vintage admission → selected indicator historical comparison → supplied custom cycle/C-score/trend interpretation. Source: DATA pp.5–6. Scanner: `trading_research.research.method_pack.native_discovery:extra_stoic`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Remaining operand(s) `cycle_and_indicator_rules_recorded`: source custom indicator set/transforms, C-score/cycle/trend formula and historical interpretation. Existing 20-series/37003-vintage bundles are used directly; initial BLS clocks and specified standardized comparisons are available. Source proprietary transforms and non-initial intraday clocks are not supplied by that recovery. Source: DATA pp.5–6;O157–O161.

Inspected local evidence: ['implementation/reports/phase1-live/macro-backfill/verification.json', 'planning/phase-1-live/wiki/c-score.md'].

Recorded scope/record limits: source custom indicator set/transforms, C-score/cycle/trend formula and historical interpretation (1 job records).

Native market/process research is executed; author-exact verdicts and faithful disagreements remain unknown. No comparison observation is represented as a fill. [Date-level evidence for this method](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/STOIC-DATA.md) · [Software acceptance and remaining external inputs](/workspace/implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md).

<!-- /phase1-native-v2-current -->

## Source definitions and retained historical comparison notes

Operating method / STOIC-DATA. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


This is Stoic's contribution in [DATA] pp.3–8, published in a Sires guide. Its ordered loop is:

| Step | Source operation | Current implementation and evidence limits |
|---|---|---|
| 1 | Pick the concept, then define a reproducible execution/research process before collecting the sample. ([DATA] p.3.) | [O137](model-definition.md). Versioned process definitions, immutable observation inventories, hashes and revision lineage are implemented. The source must still supply the actual process definition. |
| 2 | Collect every observation the same way; distinguish individual journaling from aggregate system-level data. ([DATA] pp.3–4.) | [O146](process-journal.md) · [O148](research-cohort.md). Uniform inclusion, observation clocks and process/review ledgers are implemented. Missing contemporaneous source records cannot be created from later outcomes. |
| 3 | Compare all winners and losers, identify recurring differences, refine the process and repeat. ([DATA] pp.3–4.) | [O153](outcome-metrics.md). Outcome distributions and prior-sample revision checks are implemented for supplied episodes. Stoic's general process remains a research unit with no published universal entry rule. |
| 4. Macro application | Quantify trend strength, position versus historical averages, custom C-scores, standard deviations and macro cycle. For the bubble example: identify the cycle → examine leverage/credit/housing/valuation indicators → compare with history → reach a data-based verdict. ([DATA] pp.5–6.) | [O157](macro-indicators.md) · [O158](macro-cycle.md) · [O159](c-score.md) · [O160](standardized-deviation.md) · [O161](trend-strength.md) · [O162](economic-release-vintage.md). Release-vintage admission, supplied macro/cycle/C-score/trend records and defined standardized comparisons are implemented. Proprietary formulas, the full source series and unpublished decision thresholds remain unavailable. |

The last step is an application of the data process, not a separate intraday entry. The source's historical bubble conclusion is not a current market verdict. Concepts, a macro label or one unusual release are not standalone trades.

Phase 1 — `STOIC-DATA`:

```sql
process_spec_frozen AND spec_known_at < sample_start_at
AND inclusion_rule_fixed AND uniform_schema
AND all_eligible_observations_retained
AND features_available_before_decisions
AND outcomes_separated_from_inputs
AND aggregate_winner_loser_comparison_recorded
AND revision_uses_only_prior_sample
```

For the macro application add `release_vintages_recorded AND historical_comparison_defined AND cycle_and_indicator_rules_recorded`. Citation: [DATA] pp.3–6. This measures the research process. Exact macro-model outputs remain unknown without its unpublished rules; no entry/stop/target strategy is disclosed.

## Implementation and empirical status — 2026-09-12

The [M11 contract](../FORMULAS.md#m11) and its 13 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following branch dispositions. Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `process_review` | `non_entry` | unavailable | — | — |
| `macro_application` | `non_entry` | unavailable | — | — |

All declared jobs for these branches are accounted for; none remain pending. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. Separate `macro_application` units remain supplied-only and outside the market-opportunity denominator. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md).

**Regime and thesis context.** [Scheduled news and changing information](news-event-context.md).

**Risk, objectives and process.** [Declared model and review version](model-definition.md) · [Thesis and execution journal](process-journal.md).

**Research, execution-study and risk records.** [Frozen observation cohort](research-cohort.md) · [Outcome distribution of a declared process](outcome-metrics.md) · [Stoic's macro indicator set](macro-indicators.md) · [Stoic's macro-cycle classification](macro-cycle.md) · [Stoic's custom C-score](c-score.md) · [Historical-average and standardized-deviation comparison](standardized-deviation.md) · [Stoic's trend-strength measure](trend-strength.md) · [Economic observation and release vintage](economic-release-vintage.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
