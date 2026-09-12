# Green Bird — VWAP continuation

Operating method / GB-VWAP. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


This is explicitly separate. On 24 February 2026 he reports a break and close above **both London and Asia highs**, a retracement into VWAP, then a long. His reply says he consults VWAP for continuation, while normally trading reversals at time-based levels ([GB] p.33, posts 2026329904690712970 / 2026386393820283204).

| Step | Source loop | Current implementation and evidence limits |
|---|---|---|
| 1 | Establish the London and Asia highs and the auction's continuation direction. | [O003](clock-grid-and-bars.md) · [O046](session-fail-boxes.md). Complete session-reference geometry is implemented. The comparison registry declares London/Asia clocks; unresolved source London bounds do not become author-exact. |
| 2 | Price breaks and **closes above both** highs. | [O046](session-fail-boxes.md) · [O136](directional-bias.md). The M03 assembler checks ordered closes above both references before the later return; missing or incomplete reference windows remain holes. |
| 3 | Price subsequently retraces into the contemporaneous VWAP, the auction average. | [O030](vwap-session.md). Native price-times-quantity VWAP and clocked snapshots are implemented. The frozen minute-bar comparison uses its explicitly declared estimator and reset; it does not establish the chart platform's settings. |
| 4 | Enter long and manage the continuation. The post gives a 30-point stop and a 150-point result for this trade. | [O139](structural-risk.md) · [O141](trade-objective.md) · [O142](position-management.md) · [O150](order-lifecycle.md). Source-linked risk, objectives and lifecycle admission are implemented. This example's size and points do not supply a universal target or an actual historical fill. |

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

## Implementation and empirical status — 2026-09-12

The [M03 contract](../FORMULAS.md#m03) and its 17 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following branch dispositions. Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `source_long` | `data_hole` | 36 / 12 / 8 | 161 / 161 | 91 |

All declared jobs for these branches are accounted for; none remain pending. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

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
