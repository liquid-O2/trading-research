# jetbundle — participation and B–A–D–E–W states

Operating method / JETBUNDLE-STATES. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


[MATH] p.3 explicitly separates jetbundle's framework in pp.4–11 from Sires's NQ application in pp.12–14. They are not merged here.

**Instrument scope corrected 2026-09-12.** The AAPL ten-level sample is illustrative ([MATH] pp.3, 10, 16), and the framework may be applied to NQ as the user clarified. AAPL and ten levels are not universal admission requirements. Declare the native instrument and required local depth scope before observation, then check actual coverage. Missing cancellations, event identities or off-touch liquidity remain specific evidence gaps.

| Step | Source loop | Attachment |
|---|---|---|
| 1 | Observe **provide, withdraw, consume** through submissions, cancellations and executions; reconcile the record with DOM/tape/footprint impressions. ([MATH] pp.4–6.) | NQ is eligible. Check the declared local event/depth scope using actual native data. The retained trade/BBO fields do not recover missing order identities or off-touch events; those are data limitations rather than an AAPL restriction. |
| 2 | Measure participation and price-response efficiency, then whether opposite liquidity persists/replenishes or disappears. Efficient aggression is discovery; large executions alone are not absorption. ([MATH] pp.6–8.) | R-F06/F07 and `aggressive_at_level/absorption_a/absorption_b` are related partial observations. Full source efficiency and replenishment measures are **missing**. |
| 3 | Assign the heuristic current state: B balance, A absorption, D discovery, E exhaustion, W withdrawal. ([MATH] pp.9–10.) | The five-state classifier is **missing** from [FORMULAS] and implementation. AMT day labels are not these states. |
| 4 | Observe the next transition conditional on current liquidity and pace; distinguish state persistence from a change. Do not fade efficient discovery or continue leaning on absorption after replenishment fails. ([MATH] pp.7–11.) | Transition/cohort machinery for this state alphabet is **missing**. Generic rate tables do not reconstruct the illustrated state definitions. |
| 5 | Let the state evidence discipline discretion and sizing; it is not an automated entry instruction. ([MATH] pp.3, 10–11.) | No source entry/stop/target algorithm exists to attach. |

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

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Order-flow evidence.** [Executed aggressor-side trades](aggressor-trades.md) · [DOM at a planned location](dom.md) · [Absorption: effort without price reward](absorption-and-big-trades.md) · [Executed passive replenishment](passive-replenishment.md) · [Iceberg evidence and added participation](iceberg-evidence.md) · [Speed of tape](tape-speed.md) · [Bid-ask spread](spread-width.md).

**Auction-state observation.** [Provide, withdraw and consume events](order-participation-events.md) · [Aggressive effort versus price-response efficiency](response-efficiency.md) · [B–A–D–E–W auction-state alphabet](auction-state.md) · [Conditioned next-state transition](auction-state-transition.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
