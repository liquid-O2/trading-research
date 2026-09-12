# Stoic — asymmetric compounding

Operating method / STOIC-RISK. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


The risk overlay has different inputs and a different loop, so it stays separate:

1. **Establish eligibility.** An existing trading process must have at least 100 observations, known win rate and average R:R, and a Monte Carlo estimate of maximum loss streak; base risk must not exceed 1% ([DATA] p.8).
2. **First trade.** In the printed illustration, risk one baseline unit (1% of initial account units) for 3R. A win banks three baseline units ([DATA] p.7).
3. **Second trade.** Risk the original one plus the three just banked, four units total. A 3R win earns twelve more units; a loss leaves the two-trade sequence down one unit ([DATA] p.7).
4. **Reset after the second win.** Return to base risk and repeat. Retain the source's stated volatility and validation constraints ([DATA] pp.7–8).

**Not standalone:** a win streak does not generate a trade; this overlay consumes trades admitted by an already validated process. The [printed risk-state ladder](asymmetric-risk-state.md) and [prior loss-streak validation](loss-streak-validation.md) now have implemented contracts. Actual prior process, account and Monte Carlo records remain required; generic bootstrap output does not establish the source validation.

The page heading says the overlay activates on a “two trade winning streak,” while its explicit ladder increases risk **after the first 3R win**. Preserve that discrepancy. The following Phase 1 predicate checks the **printed ladder**, not an invented resolution of the heading:

```sql
validated_process AND prior_sample_n >= 100
AND win_rate_known AND average_rr_known AND mc_loss_streak_known
AND base_risk_fraction <= 0.01 AND base_risk_fraction > 0
AND CASE risk_stage
  WHEN 'first' THEN risk_units = 1 AND planned_reward_r = 3
  WHEN 'second' THEN first_trade_closed AND first_trade_result_units = 3
                     AND risk_units = 4 AND planned_reward_r = 3
                     AND first_trade_close_at < decision_at
  WHEN 'reset_after_second_win' THEN second_trade_result_units = 12
                                     AND next_risk_units = 1
  ELSE NULL
END
```

Citation: [DATA] pp.7–8. Units use the initial baseline of the printed illustration, so `3 - 4 = -1` and `3 + 12 = 15`; silently rebasing every percentage on the changed equity produces different arithmetic. Handling after other outcomes, the sizing denominator in a general implementation, and the heading's alternative activation rule are not fully specified. The generic overlay is therefore only partially reconstructable. This is a rule/arithmetic audit, not a new simulation or a profitability claim.

## Implementation and empirical status — 2026-09-12

The [M12 contract](../FORMULAS.md#m12) and its 15 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following branch dispositions. Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `first` | `supplied_only` | unavailable | — | — |
| `second` | `supplied_only` | unavailable | — | — |
| `reset_after_second_win` | `supplied_only` | unavailable | — | — |

All declared jobs for these branches are accounted for; none remain pending. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md).

**Risk, objectives and process.** [Exposure fitted to source risk constraints](position-sizing.md).

**Research, execution-study and risk records.** [Frozen observation cohort](research-cohort.md) · [Outcome distribution of a declared process](outcome-metrics.md) · [Prior loss-streak validation for Stoic's overlay](loss-streak-validation.md) · [Stoic's printed asymmetric risk ladder](asymmetric-risk-state.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
