# Sires × TeamVOT — The Refill Effect

## Current evidence

Phase 1 setup implementation and the acquired historical census are complete. These counts describe observed setups with branch-specific input limitations; they are not fills or profitability. The source definitions below retain author-specific boundaries. Our inferred reconstruction is versioned separately.

[Full method measurements](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/REFILL-STUDY.md) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) · [Research status](current-status.md).

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| REFILL-STUDY | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/REFILL-STUDY.md |
| REFILL-STUDY | engineering slice (9 dates, not a family population) | labelled population_scale_unreconciled | not claimed | F-REFILL-POP path (ii): pre-registration ordering cannot be established; 260-session printed-figure replay not re-run; 9-date slice is not the registered window | implementation/reports/research-work/P15-16/ |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| REFILL-STUDY | M09 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |

## Source definitions


Operating method / REFILL-STUDY. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


The paper is jointly credited **Sires × TeamVOT** ([REF] p.1). Its object is a **return to a previously formed aggressive-print zone**, with pre-touch memory, construction, location and flow information. It is not a separate automatic “large print = trade” system.

| Step | Source research/execution loop | Source-object implementation snapshot and evidence limits |
|---|---|---|
| 1 | Form the zone from clustered large aggressive orders, retaining instrument, side, price span and formation time; price then leaves. ([REF] pp.5–7.) | [O098](aggressor-trades.md) · [O099](big-trades.md) · [O116](refill-zone.md). Native refill events, completed formation and later distinct returns are implemented. The frozen study comparison declares its own clustering/threshold rules; unpublished source normalization remains unresolved. |
| 2 | At each later return, create a distinct touch event. Freeze memory of **earlier** defenses, construction, auction location and incoming flow **before this touch resolves**. ([REF] pp.6–9.) | [O072](prior-reaction-area.md) · [O116](refill-zone.md) · [O117](zone-touch-memory.md). Zone identity, distinct touches and pre-touch memory are implemented. Features from the current touch's future outcome cannot enter its own selection record. |
| 3 | Grade the already-found touch under a frozen model and aligned thesis; retain the unselected cohort too. ([REF] pp.8–9, 16; [OFM] pp.15–18.) | [O149](touch-grader.md). Supplied-grade admission checks the cited classifier, model version, features and availability. The source classifier, transformations and general selection threshold remain unpublished. |
| 4 | In the documented execution study, rest a limit 12 ticks inside the selected zone, 32-tick stop, 96-tick target, 30-minute cancellation, one position at a time; modeled round-trip cost is one tick and stop slippage one tick. ([REF] p.12.) | [O150](order-lifecycle.md) · [O151](fill-model.md) · [O152](cost-model.md). Placement, amendment, cancellation, bracket, fill-assumption and cost reconciliation are implemented. Only actual reports establish fills; the study's execution convention remains scoped to this configuration. |
| 5 | Separate filled orders from selected touches; evaluate untouched held-out sessions, independent-engine comparisons and robustness diagnostics. Keep fill assumptions, losing quarters and causal rebuilds visible. ([REF] pp.12–22; [OFM] p.18.) | [O148](research-cohort.md) · [O153](outcome-metrics.md) · [O156](evaluation-risk-scenarios.md). Causal cohort, outcome and evaluation-risk records are implemented. Exact source replication still needs its original classifier and execution records. One 2023 comparison search completed with zero zones; three tape searches remain unavailable. |

**What survives the source's own correction.** [OFM] p.18 says the fully causal mechanical entry rebuild was negative, approximately −0.16R to −0.54R out of sample, and that the earlier positive selection used later-day information. It retains touch grading and the passive-side execution lesson. Do not certify an automatic positive entry edge by quoting [REF]'s earlier replay alone. The independent limit/market cohorts have different fill counts; they are not paired returns on identical filled trades. Reverse splits and rotating folds are diagnostic experiments, not forward-deployable estimates. Touch-or-trade-through fill assumptions do not prove real queue fills.

### Phase 1 predicates — `REFILL-STUDY`

The primary check is a causal zone-touch record:

```sql
zone_definition_recorded AND zone_frozen AND departure_observed
AND zone_known_at < departure_at AND departure_at < touch_at
AND distinct_touch_id AND thesis_recorded
AND feature_max_known_at <= touch_at
AND memory_uses_only_prior_resolved_touches
AND label_uses_only_post_touch_observations
AND instrument_and_threshold_preserved
```

If auditing a **supplied** selected-order record, additionally check:

```sql
grade_model_frozen_before_touch AND grade_available_at <= order_at
AND touch_selected_without_future_information
AND order_inside_ticks = 12 AND stop_ticks = 32 AND target_ticks = 96
AND cancel_minutes = 30 AND one_position_policy
AND round_trip_cost_ticks = 1 AND stop_slippage_ticks = 1
AND fill_assumption_recorded
```

Citations: [REF] pp.5–12, 16, 22; [OFM] pp.15–18. This second predicate verifies the documented configuration, not its profitability. If the grade/model or side/zone construction is unavailable, it is unknown. The default full mechanical-entry claim remains unsupported by the supplied sources.


## Source fidelity re-read, 2026-09-15

[REF] was re-read in full with its tables and charts. The zone is a price area where a burst of large aggressive orders traded (sixty, eighty, a hundred contracts within seconds); a touch is a later return; features known before the touch fall into memory, construction, location and flow ([REF] pp.2–8). The data are 199 million ticks of NQ and MNQ from December 2024 to November 2025, 235 regular sessions and 41,152 zone-touch events, about 175 touches per session ([REF] p.8). Baseline: 42% of touches hold and fading every touch loses −0.285R after costs; the graded selection reaches AUC 0.63 out of sample against 0.51 for a placebo, with the top decile holding 63% and the bottom 25%; memory and location carry the signal, flow alone reaches AUC 0.54 ([REF] pp.8–9). Execution: the median eventual winner dips 18 ticks past the touch; a resting limit inside the zone gives PF 1.80 (64 trades, 68.8%) against PF 0.81 (312 trades, 27.2%) for a market order at the touch on an independent engine ([REF] pp.10–11). The deployed configuration is the 12/32/96-tick bracket with a 30-minute cancel and one position at a time ([REF] p.12); out of sample 79 sessions, 542 trades, +0.143R, PF 1.19, about 6.8 trades a day, 30% win rate ([REF] pp.12–13); the independent-engine year shows 223 trades, 58.7%, PF 1.45, +$3,803 with a losing Q4 ([REF] p.14); a −4R daily stop adds about 14 points of pass rate ([REF] p.21).

Against the implementation: the zone construction (print clusters with size thresholds and width) is the source's and the adapter's ≥40 prints in 5 seconds with ≥80 size is an operational stand-in; the touch definition, the 30-minute horizon and the bracket are literal; the "hold" label boundary is not printed and must be registered as an operational choice; the population target for reconciliation is about 175 touches per session. The correction in [OFM] p.18 stands: the fully causal mechanical rebuild was negative, so no automatic positive entry edge is claimed.


## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Auction and profile structure.** [Auction balance](auction-balance.md) · [Volume profile](value-and-profiles.md) · [Profile value area](value-area.md) · [Profile point of control](profile-poc.md) · [Prior defended reaction area](prior-reaction-area.md).

**Order-flow evidence.** [Executed aggressor-side trades](aggressor-trades.md) · [BigTrades aggression markers](big-trades.md) · [DOM at a planned location](dom.md) · [Speed of tape](tape-speed.md) · [How price arrives at the area](approach-speed.md) · [Zone formed by aggressive prints](refill-zone.md) · [Memory of earlier zone tests](zone-touch-memory.md).

**Risk, objectives and process.** [Thesis, validity band and death condition](thesis-lifecycle.md) · [Exposure fitted to source risk constraints](position-sizing.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md).

**Research, execution-study and risk records.** [Frozen observation cohort](research-cohort.md) · [Supplied refill-touch grade](touch-grader.md) · [Observed order lifecycle](order-lifecycle.md) · [Refill-study fill assumption](fill-model.md) · [Trading and account costs](cost-model.md) · [Outcome distribution of a declared process](outcome-metrics.md) · [Refill-study evaluation-risk scenarios](evaluation-risk-scenarios.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[OFM]: </workspace/sources/documents/discretionary/origin-of-the-move.pdf>
[REF]: </workspace/sources/documents/discretionary/refill-effect.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
