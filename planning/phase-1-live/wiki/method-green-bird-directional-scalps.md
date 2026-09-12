# Green Bird — directional scalps / pullbacks

Operating method / GB-SCALP. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


The September 2 post describes bearish-bias, 20–30-point short scalps with no reason to size up. September 10 describes NYAM-direction longs on pullbacks into discount, smaller size, and no compelling A+ setup ([GB] p.40, posts 2095257805242446135 / 2098075540607410229). The known loop is **directional read → favorable pullback/pop → small exposure → limited scalp/management → stop overtrading**. The entry/failure rule, impulse selection, exact invalidation, and general exit algorithm are missing. These posts cannot be silently assigned the VWAP trigger or fabricated into a “two boxes present” rule.

The implemented [directional context](directional-bias.md), [selected range geometry](premium-discount-50.md), [size](position-sizing.md) and [management](position-management.md) records support the M04 source-case scorer:

```sql
direction_recorded_before_entry AND small_size_recorded
AND source_directional_pullback_observed AND source_scalp_management_recorded
```

That is `case_description_ok`, not full entry qualification. `sequence_ok = NULL` for automatic method admission until the missing trigger is specified by evidence. The posts demonstrate that non-A+ trading occurs; they do not establish a reusable trigger or its performance.

## Implementation and empirical status — 2026-09-12

The [M04 contract](../FORMULAS.md#m04) and its 4 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following branch dispositions. Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `bearish_small_scalp` | `source_case_only` | unavailable | — | — |
| `bullish_discount_pullback` | `source_case_only` | unavailable | — | — |

All declared jobs for these branches are accounted for; none remain pending. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. Separate `automatic_admission` units remain supplied-only and outside the market-opportunity denominator. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Regime and thesis context.** [Scheduled news and changing information](news-event-context.md).

**Price references and price-action confirmation.** [Green Bird's finished session references](session-fail-boxes.md) · [Premium / discount within a selected range](premium-discount-50.md) · [Source setup quality and exposure](quality-grade.md).

**Risk, objectives and process.** [Green Bird's directional read](directional-bias.md) · [Entry-side structural invalidation](structural-risk.md) · [Exposure fitted to source risk constraints](position-sizing.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md) · [Source account and session stop](daily-loss-limit.md).

**Research, execution-study and risk records.** [Observed order lifecycle](order-lifecycle.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
