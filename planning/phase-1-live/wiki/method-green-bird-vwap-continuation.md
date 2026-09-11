# Green Bird — VWAP continuation

Operating method / GB-VWAP. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


This is explicitly separate. On 24 February 2026 he reports a break and close above **both London and Asia highs**, a retracement into VWAP, then a long. His reply says he consults VWAP for continuation, while normally trading reversals at time-based levels ([GB] p.33, posts 2026329904690712970 / 2026386393820283204).

| Step | Source loop | Attachment |
|---|---|---|
| 1 | Establish the London and Asia highs and the auction's continuation direction. | The GB clock/level ingredients above; source London bounds remain unresolved. R-G02/G09 provide references, not this method. |
| 2 | Price breaks and **closes above both** highs. | OHLC/close primitives exist; a joint, ordered GB continuation event is **missing** from [FORMULAS]. |
| 3 | Price subsequently retraces into the contemporaneous VWAP, the auction average. | `formulas_flow.running_vwap` and `family_value` supply VWAP ingredients. Its HLC3/bar-volume version is a declared approximation; the exact source VWAP reset is **missing**. R-F01's fade and R-F03's convergence are not this entry. |
| 4 | Enter long and manage the continuation. The post gives a 30-point stop and a 150-point result for this trade. | Source-linked entry and management are **missing**. Those numbers are one case, not a published universal stop or target-selection formula. |

**Not standalone:** a VWAP touch, one session high breaking, or an unrelated failed breakout. The source does not publish a short mirror or require Sires-style tape confirmation for this method.

### Phase 1 predicate — `GB-VWAP`

`vwap_reset_verified` is required for an author-faithful automatic check; a clearly named reset variant can be measured separately.

```sql
reference_frozen AND continuation_context AND risk_defined
AND london_known_at <= breakout_at AND asia_known_at <= breakout_at
AND breakout_close > london_high AND breakout_close > asia_high
AND breakout_at < retest_at AND retest_at <= decision_at
AND vwap_reset_verified AND vwap_known_at <= retest_at
AND retest_low <= vwap_at_retest AND retest_high >= vwap_at_retest
AND side = 'long'
```

Citation: [GB] p.33 and its chart. Score this **entry sequence** and later directional movement. General target selection is unpublished. Do not use the reported 150-point result as an entry condition or an assumed planned target.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Price references and price-action confirmation.** [Green Bird's finished session references](session-fail-boxes.md).

**Regime and thesis context.** [Session VWAP](vwap-session.md).

**Risk, objectives and process.** [Green Bird's directional read](directional-bias.md) · [Entry-side structural invalidation](structural-risk.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md).

**Research, execution-study and risk records.** [Observed order lifecycle](order-lifecycle.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
