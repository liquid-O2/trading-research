# Sires × TeamVOT — The Refill Effect

Operating method / REFILL-STUDY. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


The paper is jointly credited **Sires × TeamVOT** ([REF] p.1). Its object is a **return to a previously formed aggressive-print zone**, with pre-touch memory, construction, location and flow information. It is not a separate automatic “large print = trade” system.

| Step | Source research/execution loop | Current implementation and evidence limits |
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

## Implementation and empirical status — 2026-09-12

The [M09 contract](../FORMULAS.md#m09) and its 24 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following branch dispositions. Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `touch_record` | `data_hole` | 0 / 0 / 0 | 4 / 4 | 3 |
| `supplied_selected_order` | `supplied_only` | unavailable | — | — |

All declared jobs for these branches are accounted for; none remain pending. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. Separate `selected_order_configuration` units remain supplied-only and outside the market-opportunity denominator. Only the 2023 tape search has a verified zero-zone result; the other three searches retain data holes. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

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
