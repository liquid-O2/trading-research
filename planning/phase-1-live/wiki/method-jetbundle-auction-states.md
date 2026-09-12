# jetbundle — participation and B–A–D–E–W states

Operating method / JETBUNDLE-STATES. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


[MATH] p.3 explicitly separates jetbundle's framework in pp.4–11 from Sires's NQ application in pp.12–14. They are not merged here.

**Instrument scope corrected 2026-09-12.** The AAPL ten-level sample is illustrative ([MATH] pp.3, 10, 16), and the framework may be applied to NQ as the user clarified. AAPL and ten levels are not universal admission requirements. Declare the native instrument and required local depth scope before observation, then check actual coverage. Missing cancellations, event identities or off-touch liquidity remain specific evidence gaps.

| Step | Source loop | Current implementation and evidence limits |
|---|---|---|
| 1 | Observe **provide, withdraw, consume** through submissions, cancellations and executions; reconcile the record with DOM/tape/footprint impressions. ([MATH] pp.4–6.) | [O001](data-coverage.md) · [O163](order-participation-events.md). NQ native events are eligible within their declared coverage. Missing order identities, off-touch events and receive/sequence fields remain data limits. |
| 2 | Measure participation and price-response efficiency, then whether opposite liquidity persists/replenishes or disappears. Efficient aggression is discovery; large executions alone are not absorption. ([MATH] pp.6–8.) | [O163](order-participation-events.md) · [O164](response-efficiency.md). Provide/withdraw/consume and effort/price-response measurements are implemented for observed native events. Their event scope is explicit; hidden/off-touch activity cannot be reconstructed from BBO alone. |
| 3 | Assign the heuristic current state: B balance, A absorption, D discovery, E exhaustion, W withdrawal. ([MATH] pp.9–10.) | [O165](auction-state.md). Supplied B–A–D–E–W state records and their definitions are validated. An automatic source classifier remains unpublished; AMT day labels cannot substitute for these states. |
| 4 | Observe the next transition conditional on current liquidity and pace; distinguish state persistence from a change. Do not fade efficient discovery or continue leaning on absorption after replenishment fails. ([MATH] pp.7–11.) | [O166](auction-state-transition.md). Adjacent dated same-identity state transitions and causal conditioning are implemented. Aggregate counts alone cannot certify a transition, and missing actual labels remain unknown. |
| 5 | Let the state evidence discipline discretion and sizing; it is not an automated entry instruction. ([MATH] pp.3, 10–11.) | [O165](auction-state.md) · [O166](auction-state-transition.md). The implemented unit is a state/transition observation. The source does not provide an entry, stop or target algorithm. |

**Not standalone:** high volume, static book imbalance, displayed resting size, or the source matrix's numerical persistence. The 20,000-event AAPL example is an illustration with its own sampling and depth, not a universal NQ transition table. “A setup cannot have a fixed win rate” is the author's argument for conditioning the analysis; it is not adopted here as a mathematical impossibility.

### Phase 1 predicate — `JETBUNDLE-STATES`

With source-defined or explicitly annotated qualitative fields:

```sql
participation_record_complete AND response_record_complete
AND participation_known_at <= state_at
AND response_known_at <= state_at
AND CASE state
  WHEN 'B' THEN two_sided_executions AND recent_revisits
                AND low_aggression_both_sides
  WHEN 'A' THEN high_aggression AND low_response_efficiency
                AND opposite_liquidity_holds_and_refills
  WHEN 'D' THEN aggression AND efficient_displacement
  WHEN 'E' THEN prior_absorption_or_effort
                AND replenishment_stops AND level_gives_way
  WHEN 'W' THEN cancellations_dominate
  ELSE NULL
END
```

A transition row additionally requires `state_at < next_state_at` and `conditioning_known_at <= state_at`. Citations: [MATH] pp.5–11. Unpublished thresholds, missing cancels or required off-touch depth make faithful automatic classification unknown. Record the actual observation scope; a complete local observation does not claim coverage of the entire book. Supplied transition counts must identify the same native instrument as the cohort. There is no trade-admission predicate beyond this observation method.

## Implementation and empirical status — 2026-09-12

The [M10 contract](../FORMULAS.md#m10) and its 20 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following branch dispositions. Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `B` | `supplied_only` | unavailable | — | — |
| `A` | `supplied_only` | unavailable | — | — |
| `D` | `supplied_only` | unavailable | — | — |
| `E` | `supplied_only` | unavailable | — | — |
| `W` | `supplied_only` | unavailable | — | — |

All declared jobs for these branches are accounted for; none remain pending. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. Separate `transition_observation` units remain supplied-only and outside the market-opportunity denominator. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Order-flow evidence.** [Executed aggressor-side trades](aggressor-trades.md) · [DOM at a planned location](dom.md) · [Absorption: effort without price reward](absorption-and-big-trades.md) · [Executed passive replenishment](passive-replenishment.md) · [Iceberg evidence and added participation](iceberg-evidence.md) · [Speed of tape](tape-speed.md) · [Bid-ask spread](spread-width.md).

**Auction-state observation.** [Provide, withdraw and consume events](order-participation-events.md) · [Aggressive effort versus price-response efficiency](response-efficiency.md) · [B–A–D–E–W auction-state alphabet](auction-state.md) · [Conditioned next-state transition](auction-state-transition.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
