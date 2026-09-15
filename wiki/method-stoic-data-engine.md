# Stoic — data engine / quantifying fundamentals

## Current evidence

Phase 1 setup implementation and the acquired historical census are complete. These counts describe observed setups with branch-specific input limitations; they are not fills or profitability. The source definitions below retain author-specific boundaries. Our inferred reconstruction is versioned separately.

[Full method measurements](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/STOIC-DATA.md) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) · [Research status](current-status.md).

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| STOIC-DATA | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/STOIC-DATA.md |
| STOIC-DATA | P15-16 process observation (engineering slice, not a family population) | 0 entry setups | not claimed | no entry denominator | implementation/reports/research-work/P15-16/ |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| STOIC-DATA | M11 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |

## Source definitions


Operating method / STOIC-DATA. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


This is Stoic's contribution in [DATA] pp.3–8, published in a Sires guide. Its ordered loop is:

| Step | Source operation | Source-object implementation snapshot and evidence limits |
|---|---|---|
| 1 | Pick the concept, then define a reproducible execution/research process before collecting the sample. ([DATA] p.3.) | [O137](model-definition.md). Versioned process definitions, immutable observation inventories, hashes and revision lineage are implemented. The source must still supply the actual process definition. |
| 2 | Collect every observation the same way; distinguish individual journaling from aggregate system-level data. ([DATA] pp.3–4.) | [O146](process-journal.md) · [O148](research-cohort.md). Uniform inclusion, observation clocks and process/review ledgers are implemented. Missing contemporaneous source records cannot be created from later outcomes. |
| 3 | Compare all winners and losers, identify recurring differences, refine the process and repeat. ([DATA] pp.3–4.) | [O153](outcome-metrics.md). Outcome distributions and prior-sample revision checks are implemented for supplied episodes. Stoic's general process remains a research unit with no published universal entry rule. |
| 4. Macro application | Quantify trend strength, position versus historical averages, custom C-scores, standard deviations and macro cycle. For the bubble example: identify the cycle → examine leverage/credit/housing/valuation indicators → compare with history → reach a data-based verdict. ([DATA] pp.5–6.) | [O157](macro-indicators.md) · [O158](macro-cycle.md) · [O159](c-score.md) · [O160](standardized-deviation.md) · [O161](trend-strength.md) · [O162](economic-release-vintage.md). Release-vintage admission, supplied macro/cycle/C-score/trend records and defined standardized comparisons are implemented. The guide does not publish its custom formulas, the full source series, dates or decision thresholds; their proprietary status is not established. |

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


## Source fidelity re-read, 2026-09-15

[DATA] pp.3–6 were re-read. The process is concepts, then a reproducible process, then data collection, then a comparison of all winners against all losers, then refinement; probabilities, not certainties; the macro application quantifies trend strength, position against historical averages, custom C-scores, standard deviations and the macro cycle, with the bubble case as the worked example. The implemented research-process contract matches this ordering, and no intraday entry is disclosed. Nothing to change.


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
