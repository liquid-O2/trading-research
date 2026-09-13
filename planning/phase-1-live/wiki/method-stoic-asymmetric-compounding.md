# Stoic — asymmetric compounding

<!-- phase1-strategy-current -->
## Current reconstructed strategy

STOIC-RISK: 0 setup, 0 no setup, 0 unavailable input. Personal execution requirements are excluded from qualification.

[Current method report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/STOIC-RISK.md) · [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md).

| Scope and classification | Observations |
| --- | --- |

The preserved source audit below describes its original scope. An inferred level/state is identified as our model; it is not a recovered author label or evidence of an actual trade.
<!-- /phase1-strategy-current -->

## Preserved v2 source-audit baseline

The following section records the earlier, broader source-audit scope. Its personal-record requirements and p/f/u counts are historical comparisons; the strategy scope and current classifications above supersede them.

<!-- phase1-native-v2-current -->
## Current native research implementation — 2026-09-13

Every listed scanner/interface ran for its declared dates or actual collection unit. Source definitions below remain the owner of the method; frozen operational choices are in [the research policy](/workspace/implementation/reports/phase1-live/implementation-v2/RESEARCH_POLICY.json).

Evaluation dates: 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-02, 2024-01-02, 2025-01-02, 2026-01-02. No date was replaced because of missing coverage. `n=p+f`; `N observed=n+u`. A missing population scope is recorded separately from an observed zero.

| Branch/unit | n | p | f | u | Observed scope |
| --- | --- | --- | --- | --- | --- |
| first | 0 | 0 | 0 | 0 | observed_subset_with_input_limits |
| second | 0 | 0 | 0 | 0 | observed_subset_with_input_limits |
| reset_after_second_win | 0 | 0 | 0 | 0 | observed_subset_with_input_limits |

**first** — prior process/100+ sample and validation → printed first stage arithmetic; no historical ledger reconstructed. Source: DATA pp.7–8. Scanner: `trading_research.research.method_pack.historical_process_scanners:scan_risk`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Remaining operand(s) `validated_process`, `prior_sample_n`, `win_rate_known`, `average_rr_known`, `mc_loss_streak_known`: actual prior validated trade sample, win/RR metrics, Monte Carlo loss-streak result and stage ledger. Printed first/second/reset arithmetic is available and executable. Neither the private prior sample nor Monte Carlo specification is present; a new simulation would not reconstruct it. Source: DATA pp.7–8;O154–O155.

Inspected local evidence: ['planning/phase-1-live/wiki/loss-streak-validation.md', 'planning/phase-1-live/wiki/asymmetric-risk-state.md'].

Remaining operand(s) `daily_r_before`, `daily_limit_allows_entry`: actual account/session closed R and active quantity/order ledger. Public market events and illustrated tickets are not a historical account ledger. The connected process interface audits supplied real records; market-stage measurement does not wait for them. Source: STOP pp.12,14;O140,O145,O150.

Inspected local evidence: ['implementation/src/trading_research/research/method_pack/objects/lifecycles.py', 'implementation/src/trading_research/research/method_pack/source_cases_v2.json'].

Recorded scope/record limits: no actual validated process and risk-stage ledger (7 job records); actual prior validated trade sample, win/RR metrics, Monte Carlo loss-streak result and stage ledger (7 job records); actual account/session closed R and active quantity/order ledger (7 job records).

**second** — prior process/100+ sample and validation → printed second stage arithmetic; no historical ledger reconstructed. Source: DATA pp.7–8. Scanner: `trading_research.research.method_pack.historical_process_scanners:scan_risk`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Remaining operand(s) `validated_process`, `prior_sample_n`, `win_rate_known`, `average_rr_known`, `mc_loss_streak_known`: actual prior validated trade sample, win/RR metrics, Monte Carlo loss-streak result and stage ledger. Printed first/second/reset arithmetic is available and executable. Neither the private prior sample nor Monte Carlo specification is present; a new simulation would not reconstruct it. Source: DATA pp.7–8;O154–O155.

Inspected local evidence: ['planning/phase-1-live/wiki/loss-streak-validation.md', 'planning/phase-1-live/wiki/asymmetric-risk-state.md'].

Remaining operand(s) `daily_r_before`, `daily_limit_allows_entry`: actual account/session closed R and active quantity/order ledger. Public market events and illustrated tickets are not a historical account ledger. The connected process interface audits supplied real records; market-stage measurement does not wait for them. Source: STOP pp.12,14;O140,O145,O150.

Inspected local evidence: ['implementation/src/trading_research/research/method_pack/objects/lifecycles.py', 'implementation/src/trading_research/research/method_pack/source_cases_v2.json'].

Recorded scope/record limits: no actual validated process and risk-stage ledger (7 job records); actual prior validated trade sample, win/RR metrics, Monte Carlo loss-streak result and stage ledger (7 job records); actual account/session closed R and active quantity/order ledger (7 job records).

**reset_after_second_win** — prior process/100+ sample and validation → printed reset_after_second_win stage arithmetic; no historical ledger reconstructed. Source: DATA pp.7–8. Scanner: `trading_research.research.method_pack.historical_process_scanners:scan_risk`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Remaining operand(s) `validated_process`, `prior_sample_n`, `win_rate_known`, `average_rr_known`, `mc_loss_streak_known`: actual prior validated trade sample, win/RR metrics, Monte Carlo loss-streak result and stage ledger. Printed first/second/reset arithmetic is available and executable. Neither the private prior sample nor Monte Carlo specification is present; a new simulation would not reconstruct it. Source: DATA pp.7–8;O154–O155.

Inspected local evidence: ['planning/phase-1-live/wiki/loss-streak-validation.md', 'planning/phase-1-live/wiki/asymmetric-risk-state.md'].

Remaining operand(s) `daily_r_before`, `daily_limit_allows_entry`: actual account/session closed R and active quantity/order ledger. Public market events and illustrated tickets are not a historical account ledger. The connected process interface audits supplied real records; market-stage measurement does not wait for them. Source: STOP pp.12,14;O140,O145,O150.

Inspected local evidence: ['implementation/src/trading_research/research/method_pack/objects/lifecycles.py', 'implementation/src/trading_research/research/method_pack/source_cases_v2.json'].

Recorded scope/record limits: no actual validated process and risk-stage ledger (7 job records); actual prior validated trade sample, win/RR metrics, Monte Carlo loss-streak result and stage ledger (7 job records); actual account/session closed R and active quantity/order ledger (7 job records).

Native market/process research is executed; author-exact verdicts and faithful disagreements remain unknown. No comparison observation is represented as a fill. [Date-level evidence for this method](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/STOIC-RISK.md) · [Software acceptance and remaining external inputs](/workspace/implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md).

<!-- /phase1-native-v2-current -->

## Source definitions and retained historical comparison notes

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
