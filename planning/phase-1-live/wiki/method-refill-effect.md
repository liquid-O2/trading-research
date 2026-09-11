# Sires × TeamVOT — The Refill Effect

Operating method / REFILL-STUDY. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


The paper is jointly credited **Sires × TeamVOT** ([REF] p.1). Its object is a **return to a previously formed aggressive-print zone**, with pre-touch memory, construction, location and flow information. It is not a separate automatic “large print = trade” system.

| Step | Source research/execution loop | Attachment |
|---|---|---|
| 1 | Form the zone from clustered large aggressive orders, retaining instrument, side, price span and formation time; price then leaves. ([REF] pp.5–7.) | `on_touch_refill`, `r_f17_refill_zone`; R-F17, P3 refill object. Partial. Source clustering details and NQ/MNQ threshold normalization are unpublished; the code's ≥100/2-minute/2-tick rule is a variant. |
| 2 | At each later return, create a distinct touch event. Freeze memory of **earlier** defenses, construction, auction location and incoming flow **before this touch resolves**. ([REF] pp.6–9.) | Profile/flow ingredients attach. Full zone memory, distinct touch IDs and feature-availability ledger are **missing**. The outcome of this touch cannot define its own memory. |
| 3 | Grade the already-found touch under a frozen model and aligned thesis; retain the unselected cohort too. ([REF] pp.8–9, 16; [OFM] pp.15–18.) | The published classifier, feature transformations, complete hold label and selection threshold are **missing** from [FORMULAS] and current phase1 objects. Phase 1 can audit supplied grades and freeze observations; it does not train a new model here. |
| 4 | In the documented execution study, rest a limit 12 ticks inside the selected zone, 32-tick stop, 96-tick target, 30-minute cancellation, one position at a time; modeled round-trip cost is one tick and stop slippage one tick. ([REF] p.12.) | R-F17's penetration/hold helper is not this order lifecycle. Event-linked order placement, queue/fill assumptions, cancellation, bracket and cost records are **missing**. These are this research configuration, not universal Sires risk. |
| 5 | Separate filled orders from selected touches; evaluate untouched held-out sessions, independent-engine comparisons and robustness diagnostics. Keep fill assumptions, losing quarters and causal rebuilds visible. ([REF] pp.12–22; [OFM] p.18.) | Generic statistical summaries exist. Exact study reconstruction and its source-compatible cohort/event joins are **missing**. Current daily revisit flags are not the study's per-touch hold rate. |

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
