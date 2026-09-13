<!-- full-phase1-measurement-current -->
# SAINT-AMT — full acquired Phase 1 measurement

Implementation: accepted reconstructed setup rules, including disclosed inferred models. Historical session search: every frozen date through the owned NQ input endpoint. Setup qualification is distinct from subsequent outcomes and from actual fills.

| Branch | Scope | Searched sessions | Complete eligible sessions | Observed setups | Complete zero-setup sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- | --- |
| continuation_retest | entry_setup | 1742 | 1659 | 26 | 1635 | 71 |
| trapped_buyers_retest | entry_setup | 1742 | 1660 | 9 | 1651 | 70 |
| failed_auction_return | entry_setup | 1742 | 1611 | 471 | 1209 | 119 |
| poc_traversal | entry_setup | 1742 | 1623 | 279 | 1378 | 107 |

Eligible denominators require complete observed inputs for the branch and no active input limitation. Setups observed in limited sessions remain in the observed population and are excluded from the complete-session frequency numerator. Context, supplemental, personal and collection units do not enter entry-setup denominators.

Outcome tables describe all qualifying observed setups, including those in input-limited sessions. Complete future coverage is a separate requirement for excursion means; the per-setup record retains the input-eligibility flag.

## continuation_retest

Source: RTVP pp.3–11;WIC pp.7–10; fitted HTF accepted balance → actual LTF balance break → same-boundary retest → repeated directional aggression.

Setups per complete eligible session: 0.014. Observed setups per searched session: 0.015.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 255 | 8 | 7 | 5 |
| 2021 | 261 | 246 | 4 | 4 | 14 |
| 2022 | 260 | 249 | 4 | 3 | 10 |
| 2023 | 260 | 249 | 4 | 4 | 9 |
| 2024 | 262 | 247 | 2 | 2 | 13 |
| 2025 | 261 | 248 | 3 | 3 | 10 |
| 2026 | 176 | 165 | 1 | 1 | 10 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 26 | 0 | 0 | 15.933 | 11.394 |
| 15 | 26 | 0 | 0 | 25.846 | 21.029 |
| 30 | 26 | 0 | 0 | 34.760 | 25.212 |
| 60 | 26 | 0 | 0 | 44.144 | 36.519 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 8 |
| invalidation_observed | 5 |
| objective_observed | 13 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 8 |
| invalidation_observed | 5 |
| objective_observed | 13 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 5 | 1081.867 | 1194.315 |
| objective_observed | 13 | 302.387 | 95.640 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 18 | 1659 | 0.010 |
| NY_PM_1200_1600 | 8 | 1659 | 0.005 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 18 | 48.681 | 41.347 | expired_without_observed_boundary: 6; invalidation_observed: 3; objective_observed: 9 |
| NY_PM_1200_1600 | 8 | 33.938 | 25.656 | expired_without_observed_boundary: 2; invalidation_observed: 2; objective_observed: 4 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |
| earlier potential directional breakout close is unknown | 13 |

## trapped_buyers_retest

Source: TRAP pp.3–10;WIC pp.7–10; two distinct earlier upper buying failures → current LTF down break → same-boundary retest → repeated body selling.

Setups per complete eligible session: 0.005. Observed setups per searched session: 0.005.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 254 | 1 | 1 | 6 |
| 2021 | 261 | 247 | 2 | 2 | 13 |
| 2022 | 260 | 249 | 2 | 2 | 10 |
| 2023 | 260 | 249 | 2 | 2 | 9 |
| 2024 | 262 | 247 | 0 | 0 | 13 |
| 2025 | 261 | 248 | 1 | 1 | 10 |
| 2026 | 176 | 166 | 1 | 1 | 9 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 9 | 0 | 0 | 21.028 | 10.667 |
| 15 | 9 | 0 | 0 | 28.583 | 19.861 |
| 30 | 9 | 0 | 0 | 35.056 | 28.556 |
| 60 | 9 | 0 | 0 | 45.250 | 48.056 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 4 |
| invalidation_observed | 2 |
| objective_observed | 3 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 4 |
| invalidation_observed | 2 |
| objective_observed | 3 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 2 | 1443.085 | 1443.085 |
| objective_observed | 3 | 81.511 | 20.520 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 6 | 1660 | 0.004 |
| NY_PM_1200_1600 | 3 | 1660 | 0.002 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 6 | 55.042 | 52.958 | expired_without_observed_boundary: 2; invalidation_observed: 1; objective_observed: 3 |
| NY_PM_1200_1600 | 3 | 25.667 | 38.250 | expired_without_observed_boundary: 2; invalidation_observed: 1 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |
| earlier potential directional breakout close is unknown | 10 |

## failed_auction_return

Source: AMTL pp.8–10; original balance → distinct older value tested/rejected → original balance reacceptance → local control.

Setups per complete eligible session: 0.276. Observed setups per searched session: 0.270.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 247 | 67 | 66 | 13 |
| 2021 | 261 | 237 | 72 | 67 | 23 |
| 2022 | 260 | 238 | 68 | 66 | 21 |
| 2023 | 260 | 243 | 75 | 69 | 15 |
| 2024 | 262 | 240 | 76 | 69 | 20 |
| 2025 | 261 | 243 | 78 | 72 | 15 |
| 2026 | 176 | 163 | 35 | 35 | 12 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 470 | 1 | 0 | 18.172 | 19.388 |
| 15 | 469 | 2 | 0 | 32.022 | 31.975 |
| 30 | 469 | 2 | 0 | 47.205 | 42.558 |
| 60 | 464 | 7 | 0 | 61.345 | 56.357 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 22 |
| invalidation_observed | 155 |
| objective_observed | 294 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 22 |
| invalidation_observed | 155 |
| objective_observed | 294 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 155 | 606.801 | 373.001 |
| objective_observed | 294 | 432.811 | 176.409 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 433 | 1611 | 0.254 |
| NY_PM_1200_1600 | 38 | 1611 | 0.022 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 433 | 62.407 | 57.785 | expired_without_observed_boundary: 16; invalidation_observed: 147; objective_observed: 270 |
| NY_PM_1200_1600 | 31 | 46.508 | 36.411 | expired_without_observed_boundary: 6; invalidation_observed: 8; objective_observed: 24 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 9 |
| current input prefix has unknown intervals | 70 |
| no distinct older completed auction in current admitted prefix | 45 |

## poc_traversal

Source: RTVP pp.5–8;AMTL pp.8–11; original balance reacceptance → aggressive POC passage → source hold → far-edge objective.

Setups per complete eligible session: 0.162. Observed setups per searched session: 0.160.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 248 | 48 | 47 | 12 |
| 2021 | 261 | 238 | 29 | 27 | 22 |
| 2022 | 260 | 240 | 35 | 35 | 19 |
| 2023 | 260 | 244 | 49 | 45 | 14 |
| 2024 | 262 | 245 | 41 | 37 | 15 |
| 2025 | 261 | 245 | 42 | 39 | 13 |
| 2026 | 176 | 163 | 35 | 33 | 12 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 278 | 1 | 0 | 17.720 | 18.519 |
| 15 | 277 | 2 | 0 | 31.116 | 30.959 |
| 30 | 275 | 4 | 0 | 47.668 | 42.078 |
| 60 | 272 | 7 | 0 | 60.561 | 57.786 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 16 |
| invalidation_observed | 42 |
| objective_observed | 221 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 16 |
| invalidation_observed | 42 |
| objective_observed | 221 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 42 | 926.113 | 567.832 |
| objective_observed | 221 | 309.329 | 58.215 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 242 | 1623 | 0.142 |
| NY_PM_1200_1600 | 37 | 1623 | 0.020 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 242 | 64.595 | 60.180 | expired_without_observed_boundary: 8; invalidation_observed: 40; objective_observed: 194 |
| NY_PM_1200_1600 | 30 | 28.017 | 38.475 | expired_without_observed_boundary: 8; invalidation_observed: 2; objective_observed: 27 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 9 |
| current input prefix has unknown intervals | 70 |
| no distinct older completed auction in current admitted prefix | 45 |

[Machine-readable results](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/MEASUREMENT_RESULTS.json) · [Coverage and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/coverage-exclusions.jsonl.gz) · [Per-setup records](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/setup-records.jsonl.gz) · [Charts](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/charts/README.md).
<!-- /full-phase1-measurement-current -->

## Preserved implementation and prior measurement history

# Saint — AMT on live markets and confirmed alignment

<!-- phase1-strategy-current -->
## Current reconstructed strategy

SAINT-AMT: 0 setup, 26 no setup, 0 unavailable input. Personal execution requirements are excluded from qualification.

[Current method report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/SAINT-AMT.md) · [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md).

| Scope and classification | Observations |
| --- | --- |
| entry_setup:no_setup | 26 |

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
| continuation_retest | 5 | 0 | 5 | 0 | observed_subset_with_input_limits |
| trapped_buyers_retest | 3 | 0 | 3 | 0 | observed_subset_with_input_limits |
| failed_auction_return | 4 | 0 | 4 | 5 | observed_subset_with_input_limits |
| poc_traversal | 5 | 0 | 5 | 4 | observed_subset_with_input_limits |

**continuation_retest** — fitted HTF accepted balance → actual LTF balance break → same-boundary retest → repeated directional aggression. Source: RTVP pp.3–11;WIC pp.7–10. Scanner: `trading_research.research.method_pack.historical_auction_scanners:scan_saint`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: no distinct confirmed LTF price balance (3 job records); no confirmed HTF price balance in observed prefix (1 job records).

**trapped_buyers_retest** — two distinct earlier upper buying failures → current LTF down break → same-boundary retest → repeated body selling. Source: TRAP pp.3–10;WIC pp.7–10. Scanner: `trading_research.research.method_pack.historical_auction_scanners:scan_saint`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: no distinct confirmed LTF price balance (3 job records); no confirmed HTF price balance in observed prefix (1 job records).

**failed_auction_return** — original balance → distinct older value tested/rejected → original balance reacceptance → local control. Source: AMTL pp.8–10. Scanner: `trading_research.research.method_pack.historical_auction_scanners:scan_saint`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (1 job records); same_contract_prior_scope_unknown (1 job records); no distinct older completed auction in current admitted prefix (1 job records); no confirmed HTF price balance in observed prefix (1 job records).

**poc_traversal** — original balance reacceptance → aggressive POC passage → source hold → far-edge objective. Source: RTVP pp.5–8;AMTL pp.8–11. Scanner: `trading_research.research.method_pack.historical_auction_scanners:scan_saint`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (1 job records); same_contract_prior_scope_unknown (1 job records); no distinct older completed auction in current admitted prefix (1 job records); no confirmed HTF price balance in observed prefix (1 job records).

Native market/process research is executed; author-exact verdicts and faithful disagreements remain unknown. No comparison observation is represented as a fill. [Date-level evidence for this method](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/SAINT-AMT.md) · [Software acceptance and remaining external inputs](/workspace/implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md).

<!-- /phase1-native-v2-current -->

## Source definitions and retained historical comparison notes

Operating method / SAINT-AMT. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


[AMTL] p.12 explicitly describes its apparent setups as the same acceptance/rejection read applied at the area being tested. [WIC] p.10 names higher/lower-timeframe alignment as the whole method. [RTVP] p.6 states his preference for continuations and relatively infrequent reversals. Keep all four Saint PDFs together, and keep his decisions separate from Sires's.

| Step | Saint's ordered loop | Current implementation and evidence limits |
|---|---|---|
| 1. Fit the higher-timeframe balance to traded structure | Identify accepted value and its actual extremes; redraw the balance until it fits the market before trading it. Read the profile: balanced distribution; two shelves and their connecting LVN; P/b with a formed balance at the head/base. An unbalanced trending profile is left alone until a new balance forms. ([RTVP] pp.3–11; [TRAP] pp.3–4.) | [O060](auction-balance.md) · [O061](value-and-profiles.md) · [O066](hvn.md) · [O067](lvn.md) · [O068](profile-shelf.md) · [O071](dealing-range.md). Native profile structure and attributed balance/dealing-range admission are implemented. Choosing the source's intended HTF distribution remains a separate source observation. |
| 2. Read arrival, acceptance/rejection and the controlling side | At the extreme ask whether price accepts or rejects; inspect how price arrived, executed delta and whether aggressive effort achieves movement. Heavy buying at an upper extreme can identify trapped buyers if repeated attempts fail. ([AMTL] pp.5–10; [WIC] pp.4–6; [TRAP] pp.4–5.) | [O077](weekly-delta-profile.md) · [O113](approach-speed.md) · [O119](trapped-buyers.md) · [O164](response-efficiency.md). Local arrival, signed concentration and effort/response measurements are implemented. Unpublished classification thresholds and source interpretations remain unavailable automatically. |
| 3. Require the lower timeframe to agree | Wait through free two-sided chop. An actual intraday balance break followed by a held retest shows control; inspect the 15-minute view when the smaller chart is unclear. In the trapped-buyer example, two prior AM/PM failures support the thesis, but the current break/retest is still required. ([WIC] pp.7–10; [TRAP] pp.5–9.) | [O091](break-retest.md) · [O094](failed-auction-saint.md) · [O097](htf-ltf-alignment.md). Selected HTF/LTF parent identities and the ordered break/failed-auction/retest sequence are implemented. Distinct historical references cannot be replaced by duplicate current-session levels. |
| 4. Confirm at the retest and enter | Confirm real initiative in the intended direction; the short example has repeated aggressive selling inside candle bodies, with footprint and DOM agreement. If the retest is missed, do not chase; wait for another relevant area/test. If buyers take and defend the band instead, revise the directional read. ([TRAP] pp.6–12; [WIC] pp.8–10.) | [O004](execution-bars.md) · [O098](aggressor-trades.md) · [O119](trapped-buyers.md) · [O120](footprint.md). Native execution bars and side-specific local flow can support the selected retest. Missing aggressor, depth, platform settings or precise decision time remain evidence gaps. |
| 5. Target the actual next accepted area and manage the evidence | Initial destinations are POC/fair value, the other shelf, the far balance edge or prior balance. Repeated inability to cross and hold POC favors chop; aggressive passage, with a held retest where shown, supports travel to the far side. The TRAP ticket deliberately keeps the objective within a realistic Asia-range distance and uses normal risk. ([RTVP] pp.5–8; [AMTL] pp.8–11; [TRAP] pp.8–10.) | [O064](profile-poc.md) · [O067](lvn.md) · [O139](structural-risk.md) · [O141](trade-objective.md) · [O142](position-management.md). Fixed next-area objectives, structural invalidation and management records are implemented. Source selection and actual management require contemporaneous evidence. |

The failed-auction branch in [AMTL] pp.8–10 is **lower value tried → failure to accept → return into original value → read POC/acceptance again**. Its live example can dip deeply and take time to confirm. Do not import Sires's narrower instant rejection at an older POC as a mandatory condition for every Saint failed-auction read.

**Not standalone:** HTF bias, a large positive delta print, slow/fast arrival, P/b shape, an 80/20 claim, or a high-volume node. Saint's P/b examples start with an impulsive move, establish the new balance, then wait for its break/retest ([RTVP] pp.10–11). They do not license buying every P or selling every b. His choice to wait for rebalance on a trending profile also must not be replaced with Sires's permission to trade an established trend.

### Phase 1 predicate — `SAINT-AMT`

`alignment_ok` means the *current* HTF read and actual lower-timeframe control agree. `source_route_ok` chooses the documented path instead of pooling all profile conditions:

```sql
balance_fixed_before_use AND profile_allows_trade
AND arrival_read_recorded AND control_evidence_recorded
AND alignment_ok AND risk_defined AND objective_fixed
AND balance_known_at <= arrival_at
AND arrival_at <= control_at AND control_at <= decision_at
AND CASE branch
  WHEN 'continuation_retest' THEN
    ltf_balance_broken AND same_boundary_retest_held
    AND repeated_aggression_in_trade_direction
    AND ltf_balance_known_at < breakout_at
    AND breakout_at < retest_at AND retest_at <= confirm_at
    AND confirm_at <= decision_at
  WHEN 'trapped_buyers_retest' THEN
    prior_buying_at_upper_extreme AND two_distinct_prior_failures
    AND prior_failures_known_at < breakout_at
    AND ltf_break_down AND same_boundary_retest_held
    AND repeated_body_selling AND side = 'short'
    AND breakout_at < retest_at AND retest_at <= confirm_at
    AND confirm_at <= decision_at
  WHEN 'failed_auction_return' THEN
    older_value_tested AND older_value_rejected
    AND original_balance_reaccepted AND local_control_confirms_return
    AND older_value_known_at < older_value_touch_at
    AND older_value_touch_at < rejection_at
    AND rejection_at < reaccept_at AND reaccept_at <= decision_at
  WHEN 'poc_traversal' THEN
    original_balance_reaccepted AND aggressive_poc_passage
    AND source_poc_hold_confirmed AND target_is_far_balance_edge
    AND reaccept_at < poc_passage_at AND poc_passage_at <= decision_at
  ELSE NULL
END
```

Citations: [RTVP] pp.5–11; [AMTL] pp.8–12; [WIC] pp.7–10; [TRAP] pp.3–10. Preserve an explicitly sourced long mirror as its own side binding. A range still in “free game” with no confirmed control fails entry admission; an unobserved retest is unknown, not an assumed continuation. Measure POC chop versus passage and the subsequent source objective separately.

## Implementation and empirical status — 2026-09-12

The [M06 contract](../FORMULAS.md#m06) and its 37 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following branch dispositions. Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `continuation_retest` | `data_hole` | 31 / 75 / 0 | 161 / 161 | 54 |
| `trapped_buyers_retest` | `data_hole` | 0 / 0 / 0 | 4 / 4 | 4 |
| `failed_auction_return` | `data_hole` | 0 / 0 / 0 | 4 / 4 | 4 |
| `poc_traversal` | `data_hole` | 0 / 0 / 0 | 4 / 4 | 4 |

All declared jobs for these branches are accounted for; none remain pending. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Auction and profile structure.** [Auction balance](auction-balance.md) · [Volume profile](value-and-profiles.md) · [Profile value area](value-area.md) · [Developing profile snapshot](developing-profile.md) · [Profile point of control](profile-poc.md) · [High-volume node](hvn.md) · [Low-volume node](lvn.md) · [Profile shelf](profile-shelf.md) · [Source-selected dealing range](dealing-range.md) · [Signed volume-by-price profile](weekly-delta-profile.md) · [Developing auction day structure](day-type.md) · [Profile shape and trade permission](profile-shape.md) · [Saint's Asia-range target context](asia-range-risk-context.md).

**Auction routes inside a method.** [Rotation within accepted balance](balance-rotation.md) · [Accepted break and defended boundary retest](break-retest.md) · [Re-acceptance into value](value-reacceptance.md) · [Saint's failed auction and return to value](failed-auction-saint.md) · [POC failure versus efficient passage](poc-traversal.md) · [Higher- and lower-timeframe control alignment](htf-ltf-alignment.md).

**Order-flow evidence.** [Executed aggressor-side trades](aggressor-trades.md) · [DOM at a planned location](dom.md) · [Absorption: effort without price reward](absorption-and-big-trades.md) · [Executed passive replenishment](passive-replenishment.md) · [Local delta concentration at an extreme](delta-spike.md) · [How price arrives at the area](approach-speed.md) · [Trapped aggression at an auction extreme](trapped-buyers.md) · [Native candle footprint](footprint.md).

**Risk, objectives and process.** [Entry-side structural invalidation](structural-risk.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md).

**Research, execution-study and risk records.** [Observed order lifecycle](order-lifecycle.md).

**Auction-state observation.** [Aggressive effort versus price-response efficiency](response-efficiency.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[AMTL]: </workspace/sources/documents/discretionary/amt-on-live-markets.pdf>
[WIC]: </workspace/sources/documents/discretionary/whos-in-control.pdf>
[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
