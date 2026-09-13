<!-- full-phase1-measurement-current -->
# GB-VWAP — full acquired Phase 1 measurement

Implementation: accepted reconstructed setup rules, including disclosed inferred models. Historical session search: every frozen date through the owned NQ input endpoint. Setup qualification is distinct from subsequent outcomes and from actual fills.

| Branch | Scope | Searched sessions | Complete eligible sessions | Observed setups | Complete zero-setup sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- | --- |
| source_long | entry_setup | 1742 | 1666 | 499 | 1174 | 64 |

Eligible denominators require complete observed inputs for the branch and no active input limitation. Setups observed in limited sessions remain in the observed population and are excluded from the complete-session frequency numerator. Context, supplemental, personal and collection units do not enter entry-setup denominators.

Outcome tables describe all qualifying observed setups, including those in input-limited sessions. Complete future coverage is a separate requirement for excursion means; the per-setup record retains the input-eligibility flag.

## source_long

Source: GB p.33 posts 2026329904690712970/2026386393820283204; both finished session highs → close above → later contemporaneous VWAP return → long risk/continuation observation.

Setups per complete eligible session: 0.295. Observed setups per searched session: 0.286.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 258 | 56 | 56 | 2 |
| 2021 | 261 | 249 | 73 | 71 | 11 |
| 2022 | 260 | 249 | 71 | 70 | 10 |
| 2023 | 260 | 249 | 91 | 90 | 9 |
| 2024 | 262 | 248 | 88 | 86 | 12 |
| 2025 | 261 | 247 | 75 | 74 | 11 |
| 2026 | 176 | 166 | 45 | 45 | 9 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 499 | 0 | 0 | 20.301 | 22.071 |
| 15 | 499 | 0 | 0 | 32.955 | 37.870 |
| 30 | 499 | 0 | 0 | 43.410 | 52.356 |
| 60 | 496 | 3 | 0 | 55.900 | 68.904 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 49 |
| invalidation_observed | 450 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |

| Only one or neither boundary defined | n |
| --- | --- |
| expired_without_observed_boundary | 49 |
| invalidation_observed | 450 |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 450 | 206.478 | 25.889 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 478 | 1666 | 0.283 |
| NY_PM_1200_1600 | 21 | 1666 | 0.013 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 478 | 55.538 | 69.281 | expired_without_observed_boundary: 46; invalidation_observed: 432 |
| NY_PM_1200_1600 | 18 | 65.514 | 58.889 | expired_without_observed_boundary: 3; invalidation_observed: 18 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |
| earlier potential breakout close is unknown | 4 |
| session_reference_missing | 21 |

[Machine-readable results](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/MEASUREMENT_RESULTS.json) · [Coverage and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/coverage-exclusions.jsonl.gz) · [Per-setup records](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/setup-records.jsonl.gz) · [Charts](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/charts/README.md).
<!-- /full-phase1-measurement-current -->

## Preserved implementation and prior measurement history

# Green Bird — VWAP continuation

<!-- phase1-strategy-current -->
## Current reconstructed strategy

GB-VWAP: 3 setup, 0 no setup, 0 unavailable input. Personal execution requirements are excluded from qualification.

[Current method report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/GB-VWAP.md) · [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md).

| Scope and classification | Observations |
| --- | --- |
| entry_setup:setup | 3 |

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
| source_long | 2 | 2 | 0 | 1 | observed_subset_with_input_limits |

**source_long** — both finished session highs → close above → later contemporaneous VWAP return → long risk/continuation observation. Source: GB p.33 posts 2026329904690712970/2026386393820283204. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_vwap`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: session_reference_missing (1 job records).

Native market/process research is executed; author-exact verdicts and faithful disagreements remain unknown. No comparison observation is represented as a fill. [Date-level evidence for this method](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/GB-VWAP.md) · [Software acceptance and remaining external inputs](/workspace/implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md).

<!-- /phase1-native-v2-current -->

## Source definitions and retained historical comparison notes

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
