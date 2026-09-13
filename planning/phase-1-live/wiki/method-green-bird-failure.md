# Green Bird — failed breakout / failed breakdown

<!-- phase1-strategy-current -->
## Current reconstructed strategy

GB-FAIL: 22 setup, 62 no setup, 0 unavailable input. Personal execution requirements are excluded from qualification.

[Current method report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/GB-FAIL.md) · [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md).

| Scope and classification | Observations |
| --- | --- |
| entry_setup:no_setup | 62 |
| entry_setup:setup | 22 |

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
| nyam_box | 7 | 3 | 4 | 1 | observed_subset_with_input_limits |
| previous_hour | 35 | 12 | 23 | 3 | observed_subset_with_input_limits |
| asia_tdo_case | 9 | 1 | 8 | 1 | observed_subset_with_input_limits |
| prior_day_level | 3 | 0 | 3 | 0 | observed_subset_with_input_limits |
| prior_week_level | 4 | 0 | 4 | 2 | observed_subset_with_input_limits |
| prior_month_level | 2 | 0 | 2 | 2 | observed_subset_with_input_limits |
| cash_open_reclaim_case | 5 | 0 | 5 | 0 | observed_subset_with_input_limits |
| mss_fvg_refinement | 3 | 0 | 3 | 0 | observed_subset_with_input_limits |

**nyam_box** — finished 09–10 box → contextual sweep → five-minute reclaim → opposing box liquidity. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

**previous_hour** — finished prior clock-hour reference → contextual sweep → reclaim → opposing hour liquidity. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

**asia_tdo_case** — completed Asia range + midnight TDO → sweep → reclaim with TDO confirmation. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

**prior_day_level** — same-contract previous actual RTH reference → sweep/reclaim → selected opposing level. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (5 job records); same_contract_prior_scope_unknown (4 job records).

**prior_week_level** — same-contract prior-week matching sessions → sweep/reclaim → selected opposing level. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: same_contract_prior_scope_unknown (11 job records); calendar_unverified (9 job records).

**prior_month_level** — same-contract prior-month matching sessions → sweep/reclaim → selected opposing level. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: same_contract_prior_scope_unknown (110 job records); calendar_unverified (11 job records).

**cash_open_reclaim_case** — 09:30 open → below-open manipulation → reclaim → retracement objective with low invalidation. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: cash_open_order_unknown (2 job records).

**mss_fvg_refinement** — completed parent reclaim → later three 2-minute candles → MSS plus actual wick FVG; annotation unit. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Native market/process research is executed; author-exact verdicts and faithful disagreements remain unknown. No comparison observation is represented as a fill. [Date-level evidence for this method](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/GB-FAIL.md) · [Software acceptance and remaining external inputs](/workspace/implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md).

<!-- /phase1-native-v2-current -->

## Source definitions and retained historical comparison notes

Operating method / GB-FAIL. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


**Source name and unification.** “Sweep → reclaim → opposing liquidity” is his own formulation ([GB] p.31). NYAM, Asia, prior hour, prior day/week/month, TDO confluence, and golden-pocket examples repeat this failure-and-reclaim mechanism. The raw golden-pocket explanation requires a failed breakdown and reclaim, or the PDL sweep followed by a five-minute close back below; the retracement band alone is not another strategy ([GB] pp.25, 31–35).

### Ordered loop and attachments

| Step | Source operation | Current implementation and evidence limits |
|---|---|---|
| 1. Establish the reference and contextual direction | Finish the selected box or use a known prior level. NYAM is 09:00–10:00 and that box cannot be traded as finished before 10:00. Previous-hour examples use the completed hour. Asia's drawn box is approximately 20:00–00:00; exact London bounds are not stated. Prior day, previous weekly candle, previous month, and an already-observed overnight reclaim can supply the context. ([GB] pp.23, 25, 27, 30–35, 38–40.) | [O003](clock-grid-and-bars.md) · [O046](session-fail-boxes.md) · [O048](prior-day-week-month-levels.md) · [O136](directional-bias.md). Completed reference windows, prior day/week/month geometry and attributed directional context are implemented. Same-contract prior coverage and exact source London bounds can remain unavailable. |
| 2. Locate the potential failure | Watch the relevant high/low or reclaimed level. Optional confluence includes PDH/PDL, Asia/London, midnight TDO, and the 50–61.8% retracement of the explicitly measured impulse. TDO is the midnight opening price; NWOG is a destination between the Friday-close and Sunday-open references. ([GB] pp.21, 25, 27, 32–39.) | [O049](true-day-open.md) · [O051](new-week-opening-gap.md) · [O052](golden-pocket.md) · [O053](premium-discount-50.md). TDO, NWOG endpoints and selected-impulse retracement geometry are implemented with parent identity and availability. The source still determines the impulse and endpoint convention. |
| 3. Wait for the sweep and its failure | Sweep above and fail back below → short; sweep below and reclaim → long. The explicit PDL and Asia/TDO examples wait for a completed five-minute close. Those cited close-confirmation variants wait for the reclaim. The November 20, 2025 figure separately shows entry at the high sweep ([GB] pp.31, 43); it must not inherit a later MSS/FVG prerequisite. ([GB] pp.21, 23, 25, 27, 30–35, 38.) | [O003](clock-grid-and-bars.md) · [O047](sweep-reclaim.md). Strict sweep/reclaim ordering and complete clock-aligned confirmations are implemented. The frozen comparison uses its declared endpoint and expiry; those parameters are not universal author rules. |
| 4. Preserve the case-specific entry and structural risk | Enter the reclaim or its retracement; the PDL reply says to wait a few points after the close and use a low-risk retracement. The November 20, 2025 MNQZ2025 two-minute figure displays a short entry at the 9–10 high sweep, at 25301.75. MSS/FVG is annotated later; exact fill time is not established. The September 1 09:30 manipulation/reclaim long is a distinct timing branch, not an early completed 9–10 box. ([GB] pp.25, 31, 40, chart p.43.) | [O054](market-structure-shift.md) · [O055](fvg-body-gaps.md) · [O139](structural-risk.md) · [O150](order-lifecycle.md). MSS/FVG geometry, linked decisions, structural invalidation and lifecycle checks are implemented. The November 2025 sweep-entry observation remains separate from subsequent annotations; exact fill time is unknown. |
| 5. Take opposing liquidity; manage the remaining position | Opposite box edge, intermediate 50%, TDO, prior/session extremes or NWOG as actually named. Take partials, move to breakeven once working, trail/leave the runner when appropriate, then stop the session. Size the quality of the setup; do not average down. ([GB] pp.25, 30–39.) | [O059](quality-grade.md) · [O140](position-sizing.md) · [O141](trade-objective.md) · [O142](position-management.md) · [O145](daily-loss-limit.md) · [O150](order-lifecycle.md). Entry-linked objectives, sizing, partials, stop changes, runners and session constraints are implemented. Historical actions remain unknown without actual source/order records. |

**Branches, not new products.**

- NYAM / completed hour / Asia failures use their own finished reference. A sweep during construction is part of the box.
- A prior-day/week/month reclaim can establish a bias for subsequent aligned pullbacks. Do not demand a fresh NYAM sweep for a separately cited prior-level trade.
- The golden pocket is `[L + 0.50(H-L), L + 0.618(H-L)]` for the illustrated retracement of a down impulse; direction and measured impulse matter. The September 1 source combines it with an actual PDL sweep and five-minute failure ([GB] p.25). The July example combines a fib pullback and hourly-low reclaim ([GB] p.35).
- The 09:30 manipulation branch is the source's below-open/reclaim long with a retracement objective and stop at the lows ([GB] p.40). Its confirmation duration is not fully specified by that reply; do not silently impose all parameters from the PDL example.
- A+ requires a relevant sweep; “no sweep = not A+” is a necessary quality condition, not proof that every sweep is A+ or that no other trade is allowed ([GB] pp.21–23, 37–40). R-G11 attaches to grading this candidate, not an OR across unrelated boxes somewhere during the day.

**November 20, 2025 source correction.** The retained [case registry](/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json), case `GB-FAIL-2025-11-20`, separates the displayed MNQ sweep entry from the subsequent MSS/FVG annotation ([GB] pp.31, 43). The predicate below describes confirmed-reclaim variants; it must not be applied retrospectively as this case's entry prerequisite. The frozen `mss_fvg_refinement` research comparison remains separately named. An NQ comparison does not establish the displayed MNQ execution or its exact fill clock.

### Phase 1 predicate — `GB-FAIL`

`reference_px` is the swept boundary; `opposite_bound` is the other edge when the reference is a box. `box_return_ok` means the confirmation is back inside that finished box, or true for a single-level reclaim. `source_hold_confirmed` records the actual reclaim/hold observation when a five-minute rule was not stated. `tdo_required` is true only in the selected source variant.

```sql
reference_frozen AND bias_recorded AND risk_defined AND objective_fixed
AND reference_known_at <= sweep_at
AND context_at <= sweep_at AND sweep_at < confirm_at
AND confirm_at <= decision_at AND source_session_allowed
AND (
  (side = 'short' AND sweep_high > reference_px
                  AND confirm_close < reference_px)
  OR
  (side = 'long' AND sweep_low < reference_px
                 AND confirm_close > reference_px)
)
AND box_return_ok
AND CASE confirmation_mode
  WHEN 'five_minute_close' THEN complete_clock_five_minute_bar
  WHEN 'reclaim_and_hold' THEN source_hold_confirmed
  ELSE NULL
END
AND (NOT tdo_required OR source_tdo_close_confirmed)
AND (NOT pocket_required OR impulse_known_at <= touch_at
                            AND touch_in_measured_pocket)
AND (NOT retracement_entry OR confirm_at <= retest_at
                              AND retest_at <= decision_at)
```

Sequence citations: [GB] pp.21, 23, 25, 27, 30–35, 38–40. Outcome: the preselected opposing-liquidity objective after this entry, with source stop/management recorded separately. Examples that sweep and remain accepted outside fail this predicate. A 09:45 candidate using a final 09:00–10:00 box fails availability. A pocket touch without failure fails. Missing London bounds, prior-week/month data, or an unspecified reclaim detector leave the corresponding automatic check unknown.

## Implementation and empirical status — 2026-09-12

The [M02 contract](../FORMULAS.md#m02) and its 27 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following branch dispositions. Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `nyam_box` | `data_hole` | 99 / 123 / 1 | 161 / 161 | 2 |
| `previous_hour` | `completed_with_population_holes` | 487 / 631 / 6 | 161 / 161 | 0 |
| `asia_tdo_case` | `data_hole` | 3 / 114 / 0 | 161 / 161 | 95 |
| `prior_day_level` | `data_hole` | 33 / 75 / 1 | 161 / 161 | 54 |
| `prior_week_level` | `data_hole` | 12 / 46 / 0 | 161 / 161 | 69 |
| `prior_month_level` | `data_hole` | 5 / 6 / 0 | 161 / 161 | 138 |
| `cash_open_reclaim_case` | `measured` | 53 / 89 / 0 | 161 / 161 | 0 |
| `mss_fvg_refinement` | `data_hole` | 52 / 47 / 0 | 161 / 161 | 2 |

All declared jobs for these branches are accounted for; none remain pending. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Regime and thesis context.** [Scheduled news and changing information](news-event-context.md).

**Price references and price-action confirmation.** [Green Bird's finished session references](session-fail-boxes.md) · [Sweep, failure and reclaim](sweep-reclaim.md) · [Prior day, week and month extremes](prior-day-week-month-levels.md) · [Green Bird's midnight true-day open](true-day-open.md) · [09:30 cash-open price](cash-open-reference.md) · [New-week opening gap](new-week-opening-gap.md) · [Measured 50–61.8% retracement](golden-pocket.md) · [Premium / discount within a selected range](premium-discount-50.md) · [Market-structure shift after failure](market-structure-shift.md) · [Fair-value gaps and higher-timeframe imbalances](fvg-body-gaps.md) · [Source setup quality and exposure](quality-grade.md).

**Auction and profile structure.** [Prior-session auction landmarks](prior-session-reference-levels.md) · [Remaining auction objectives](unfinished-business.md).

**Risk, objectives and process.** [Green Bird's directional read](directional-bias.md) · [Entry-side structural invalidation](structural-risk.md) · [Exposure fitted to source risk constraints](position-sizing.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md) · [Source account and session stop](daily-loss-limit.md).

**Research, execution-study and risk records.** [Observed order lifecycle](order-lifecycle.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
