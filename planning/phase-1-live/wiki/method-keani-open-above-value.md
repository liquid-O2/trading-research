<!-- full-phase1-measurement-current -->
# KEANI-OPEN-ABOVE-VALUE — full acquired Phase 1 measurement

Implementation: accepted reconstructed setup rules, including disclosed inferred models. Historical session search: every frozen date through the owned NQ input endpoint. Setup qualification is distinct from subsequent outcomes and from actual fills.

| Branch | Scope | Searched sessions | Complete eligible sessions | Observed setups | Complete zero-setup sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- | --- |
| source_long | entry_setup | 1742 | 1594 | 6 | 1588 | 136 |

Eligible denominators require complete observed inputs for the branch and no active input limitation. Setups observed in limited sessions remain in the observed population and are excluded from the complete-session frequency numerator. Context, supplemental, personal and collection units do not enter entry-setup denominators.

Outcome tables describe all qualifying observed setups, including those in input-limited sessions. Complete future coverage is a separate requirement for excursion means; the per-setup record retains the input-eligibility flag.

## source_long

Source: AVG pp.21–22; whole A above prior VAH → higher developing value/rejection → aggressive VAH imbalance break → defended same-imbalance retest.

Setups per complete eligible session: 0.004. Observed setups per searched session: 0.003.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-03 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 239 | 0 | 0 | 21 |
| 2021 | 261 | 239 | 2 | 2 | 21 |
| 2022 | 260 | 239 | 1 | 1 | 20 |
| 2023 | 260 | 241 | 0 | 0 | 17 |
| 2024 | 262 | 238 | 1 | 1 | 22 |
| 2025 | 261 | 238 | 1 | 1 | 20 |
| 2026 | 176 | 160 | 1 | 1 | 15 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 6 | 0 | 0 | 24.542 | 14.792 |
| 15 | 6 | 0 | 0 | 37.917 | 16.833 |
| 30 | 6 | 0 | 0 | 49.292 | 23.417 |
| 60 | 6 | 0 | 0 | 77.125 | 30.208 |

| Boundary outcome | n |
| --- | --- |
| invalidation_observed | 5 |
| objective_observed | 1 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| invalidation_observed | 5 |
| objective_observed | 1 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 5 | 115.246 | 29.437 |
| objective_observed | 1 | 742.916 | 742.916 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 6 | 1594 | 0.004 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 6 | 77.125 | 30.208 | invalidation_observed: 5; objective_observed: 1 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| A period has no observed executions | 47 |
| calendar_unverified | 65 |
| current input prefix has unknown intervals | 10 |
| same_contract_prior_scope_unknown | 37 |

[Machine-readable results](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/MEASUREMENT_RESULTS.json) · [Coverage and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/coverage-exclusions.jsonl.gz) · [Per-setup records](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/setup-records.jsonl.gz) · [Charts](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/charts/README.md).
<!-- /full-phase1-measurement-current -->

## Preserved implementation and prior measurement history

# Keani — open above value

<!-- phase1-strategy-current -->
## Current reconstructed strategy

KEANI-OPEN-ABOVE-VALUE: 0 setup, 6 no setup, 0 unavailable input. Personal execution requirements are excluded from qualification.

[Current method report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/KEANI-OPEN-ABOVE-VALUE.md) · [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md).

| Scope and classification | Observations |
| --- | --- |
| entry_setup:no_setup | 6 |

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
| source_long | 6 | 0 | 6 | 0 | observed_subset_with_input_limits |

**source_long** — whole A above prior VAH → higher developing value/rejection → aggressive VAH imbalance break → defended same-imbalance retest. Source: AVG pp.21–22. Scanner: `trading_research.research.method_pack.historical_auction_scanners:scan_keani`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (5 job records); same_contract_prior_scope_unknown (4 job records); A period has no observed executions (1 job records).

Native market/process research is executed; author-exact verdicts and faithful disagreements remain unknown. No comparison observation is represented as a fill. [Date-level evidence for this method](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/KEANI-OPEN-ABOVE-VALUE.md) · [Software acceptance and remaining external inputs](/workspace/implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md).

<!-- /phase1-native-v2-current -->

## Source definitions and retained historical comparison notes

Operating method / KEANI-OPEN-ABOVE-VALUE. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


[AVG] pp.21–22 calls this **Keani's own setup**, which Sires then validates through AMT. It is separate from the unnamed member above.

| Step | Source loop | Current implementation and evidence limits |
|---|---|---|
| 1 | Current TPO opens fully above yesterday's value: the entire A period is clear of prior VAH. Observe the developing profile around 10:00. | [O050](cash-open-reference.md) · [O061](value-and-profiles.md) · [O062](value-area.md) · [O078](tpo-ib-auction.md). The complete A period is checked against the available prior profile, with native profile and time-period identities. All four frozen empirical openings remain unclassified because prior profiles are unverified. |
| 2 | Value builds higher; observe rejection at POC or previous VAH within that bullish auction. | [O063](developing-profile.md). Developing snapshots and ordered value-build/rejection evidence are implemented; later profile values cannot rewrite an earlier observation. |
| 3 | Price breaks the current developing VAH with aggressive buying imbalances. Freeze the actual imbalance prices and their known time. | [O063](developing-profile.md) · [O109](footprint-imbalance-zones.md). The developing-VAH breakout and actual imbalance band retain separate identities and clocks. The source's aggressive breakout interpretation remains distinct from literal price measurements. |
| 4 | Price returns to those imbalance prices; buyers defend them, with the DOM and time of day supporting the trade. | [O100](dom.md) · [O109](footprint-imbalance-zones.md) · [O120](footprint.md). The later retest must join the same imbalance and its local defense. Missing DOM/source confirmation remains an explicit hole. |
| 5 | Enter long toward a worthwhile, preselected HTF objective, with defined risk. | [O139](structural-risk.md) · [O141](trade-objective.md) · [O142](position-management.md) · [O150](order-lifecycle.md). Preselected risk, objective and subsequent management/lifecycle admission are implemented. They remain unavailable for a historical candidate without the source records. |

All steps: [AVG] pp.21–22. **Not standalone:** an opening gap, `open > current VAH`, an eventual bullish day, or a break without defense on return. Around 10:00 is an observation point, not access to the finished day type. The displayed dashboard results and the document's data-collection discussion do not establish this setup's entry edge.

### Phase 1 predicate — `KEANI-OPEN-ABOVE-VALUE`

```sql
prior_value_fixed AND a_period_complete
AND a_low > prior_vah
AND developing_value_builds_higher AND source_rejection_observed
AND dev_vah_known_at <= breakout_at
AND breakout_close > dev_vah_at_break
AND aggressive_buy_imbalance_break
AND imbalance_band_known_at <= retest_at
AND breakout_at < retest_at AND retest_at <= defense_at
AND buyers_defend_same_imbalance_band AND dom_supports_long
AND time_of_day_allowed AND objective_fixed AND risk_defined
AND a_end_at <= observation_at AND observation_at <= breakout_at
AND defense_at <= decision_at AND side = 'long'
```

Citation: [AVG] pp.21–22. The source's near-10:00 observation does not define an exact universal minute tolerance. Missing that convention is an explicitly named timing variant. A developing-VAL short is not claimed as Keani's published mirror.

## Implementation and empirical status — 2026-09-12

The [M08 contract](../FORMULAS.md#m08) and its 23 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following branch dispositions. Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `source_long` | `measured` | 0 / 0 / 4 | 4 / 4 | 0 |

All declared jobs for these branches are accounted for; none remain pending. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. All four observed openings are unknown because the required prior profiles are unverified. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Session and range geometry.** [Opening location and participation](open-location-switch.md).

**Price references and price-action confirmation.** [09:30 cash-open price](cash-open-reference.md).

**Auction and profile structure.** [Auction balance](auction-balance.md) · [Volume profile](value-and-profiles.md) · [Profile value area](value-area.md) · [Developing profile snapshot](developing-profile.md) · [Profile point of control](profile-poc.md) · [Time-price-opportunity profile](tpo-ib-auction.md) · [Prior-session auction landmarks](prior-session-reference-levels.md) · [Remaining auction objectives](unfinished-business.md).

**Auction routes inside a method.** [Accepted break and defended boundary retest](break-retest.md) · [Higher- and lower-timeframe control alignment](htf-ltf-alignment.md).

**Order-flow evidence.** [Executed aggressor-side trades](aggressor-trades.md) · [DOM at a planned location](dom.md) · [Diagonal footprint imbalance stacks](footprint-imbalance-zones.md) · [Native candle footprint](footprint.md).

**Risk, objectives and process.** [Entry-side structural invalidation](structural-risk.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md).

**Research, execution-study and risk records.** [Observed order lifecycle](order-lifecycle.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
