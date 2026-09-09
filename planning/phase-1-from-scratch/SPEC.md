# Phase 1 measurement specification

Status: proposed implementation contract, derived from the completed wiki. No command, schema migration or application code has been implemented in this session. The [PRD](PRD.md) defines the outcome; mechanism pages own source definitions and named variants. This spec supplies only the shared seam needed to compare them.

## One interface

The proposed `phase1 measure` entry point accepts either `--slice NN` or `--all`, with `--verify`. A slice performs its definition/coverage/computation/report path. It may reuse evidence whose input, definition, code and population fingerprints still match. `--all` verifies the dependency closure and all required family/variant reports. No service, plugin framework, worker fleet or dashboard is required. Choose concrete code locations from the existing checkout during the later execution task.

The command always prints this header and one row per variant, including blocked/deferred rows:

```text
family | variant | n | faithful disagreements | experiment status | report path
```

`family` is Jumbo, day-type, auction-order-flow, CVD-SMT, volatility or options-data. `variant` includes mechanism identity and definition version. `n` is the mature eligible outcome unit specified in that report, never an unlabeled mix of days, zones and touches. `faithful disagreements` counts unexplained discrepancies against the independent expected-result evidence. `report path` identifies a real generated report for that row. Planned report location: `reports/phase-1/<slice>/<variant>.md`, with adjacent structured measured records only as needed. These report files are future execution outputs, not created by this planning task.

## Minimal records and ownership

| Record | Required fields / ownership |
|---|---|
| Definition / variant | mechanism_id, family, source path/page/post/line, source-rule or user-hypothesis or experiment, formula/parameters, units, clock/bar construction, required inputs, definition version, unresolved question IDs, disposition |
| Population | instrument/contract, calendar/day boundary, observed start/end, complete/partial/missing sessions, warmup, eligible rule, source vintage, family-native and matched-overlap membership, discovery/confirmation assignment |
| Object / version | stable object_id, parent/version, family/variant, native and optional mapped price, anchor/bounds, creation/origin time, known_at, confirmed_at, invalidated_at, supersession, state, input lineage |
| Feature snapshot | object/session ID, observation time, feature cutoff, values/units, source-known times, missing/unknown flags, definition version; all inputs must be available by cutoff |
| Event / path | event_id, object/version, approach, trigger/touch/break times, rearm state, source horizon, first-passage offsets, ordered outcomes, max excursion, censor time/reason, same-bar ambiguity and eligible denominator |
| Label | source/experimental taxonomy, label-known time, primitive evidence, unmatched/unresolved state, label version; completed-day labels remain outcomes |
| Comparison | faithful and named variant IDs, population/metric/unit, eligible sessions, event/touch n, estimates/uncertainty, paired differences, years/conditions, density/width/start-distance controls, source disagreements, experimental conclusion |
| Evidence | input and definition fingerprints, planned variant set frozen before confirmation, independent examples, measured report paths, coverage exceptions and exact command/result |

The producing slice owns its definition and records. Later slices consume them by identity and as-of time; they do not duplicate or rewrite an earlier producer’s rules. Raw rows remain immutable. A shared helper is justified only when the next slice needs it; do not build all producer layers before the first report.

## Time, source fidelity and event order

Follow [the measurement contract](wiki/measurement-contract.md) and each mechanism’s source rule. A source’s backdrawn origin is not first availability. Completed HTF values, final profile shape, future no-retest, current-day total volume and next-day OI must not become earlier features. Completed/current/developing states have separate versions. Stop using a future-informed source display as a predictor; preserve its literal formula and disagreement evidence under a diagnostic identity.

OHLC can establish that both sides traded without establishing order. Retain unknown order or explicit bounds. Trade-level ordering is used only where observed; no invented path, high-first tie default or hindsight fill. Bars formed from activity remain within the frozen clock definition, with boundary handling specified. Different data sources cannot double-count the same executions.

[Q01](QUESTIONS.md) must resolve common touch/reject/hold/acceptance/rearm meanings. Source-explicit rules keep their own thresholds/horizons. A common experimental outcome grid is frozen before comparison; it does not overwrite source semantics. Keep n for sessions, created objects, eligible triggers and mature touches separately. Nonreturning breaks, unconfirmed absorption, untouched nodes, dojis, equality and no-break sessions remain visible.

## Populations and causal inputs

| Family/input | Honest starting evidence, subject to actual later coverage query |
|---|---|
| Minute price/range | NQ/ES/YM from 2010-09; RTY observed2017-07. Do not trust earlier partition labels. |
| NQ order flow/BBO | NQ MBP-1 observed2020-01-01T23:00 onward. Separate NQ tape starts2021-09; use each schema’s own real coverage. |
| Sister futures | ES/YM/RTY trades from 2020; ES MBP-1 is partial. Keep contract/roll identity and missingness. |
| Options | CME futures-options definitions/stats/trades/OHLC from 2020; no acquired option MBP-1 established. Theta daily2016/NDXP2018, scoped intraday2020; exact DTE/strike limits remain in the wiki. |
| Cash/ETF/volatility | QQQ/SPY minute from 2018; NDX/SPX cash daily. Volatility indices and VX curve are daily unless acquisition proves otherwise. |

The [inventory page](wiki/inventory-and-availability.md) and [option scope](wiki/options-chain-availability.md) own exact dates and limits. Source extrema are not a gap-free audit. Later slices run the cheapest decisive real-data query for their coverage. Requested pulls, empty September markers and superseded vendor overlaps do not establish data. Roll maps/release times must be valid as of use; do not select a pre-open contract from that day’s completed volume.

## Discovery, experiments and confirmation

Use the longest honest sample per family. Pre2024 history is discovery where available. Reserve2024 through each family’s last complete2026 observation for frozen confirmation. A family starting later cannot invent earlier training history; use source-fixed definitions or an explicitly reserved chronological split and report that limitation. Never force all families onto the narrowest common options sample.

Before confirmation, freeze source variants, named experiments, finite parameter grids, outcome definitions, population rules and uncertainty method in the report’s evidence record. Fixed-grid clock experiments use the wiki’s proposed15-minute neighbors within60minutes, with an explicit distance penalty toward the source clock; preserve the published clock as the benchmark. The exact penalty strength is a discovery-only comparison parameter, not a daily learned box. Activity-bar thresholds use past information. Test named changes and a small predeclared set of combinations, not an unbounded Cartesian search.

Compute descriptive means/quantiles, event rates, time-to-event and conditional tables. HAR means lagged1/5/22 RV inputs; no forecast is trained. Experimental day/state labelers are deterministic definitions. No fitted Context classifier, learned location/reversal selector, HMM, touch grader, performance-selected supertrend, or trade/P&L optimization runs in Phase 1.

Report full native samples and matched overlaps. Use session-clustered95% intervals and paired session differences where applicable; show each year and support, dependence and multiple-comparison limits. Small/nonsignificant/worse results are measured results. A winner claim requires the frozen metric comparison and stability evidence; it cannot use confirmation to retune. Density/width/age/starting distance accompany level and node comparisons.

## Verification and pass semantics

Each ticket starts with an independent expected example, then computes real discovery data and a report. Include decisive cases for its named risk: ambiguous order, no event, incomplete horizon, unreleased input, invalidated object or source-formula discrepancy. Do not write broad tests that merely mirror code. Before the confirmation pass, show the frozen choices and independent expected results. Reuse accepted results while their fingerprints remain valid.

Status values distinguish `measured-better`, `measured-null`, `measured-worse`, `measured-inconclusive-support`, `blocked-definition`, `blocked-data`, `deferred-P2`, `deferred-P3`, and `unidentifiable-MBP1`. Faithful rows identify their benchmark status separately. Reports never label a planned or skipped computation as measured.

Successful verification requires complete mandatory rows, valid inputs/time/denominators, no unexplained faithful disagreement and all named in-scope comparisons measured on their declared sample. It does not require an improvement or matching a source claim percentage. Explicit wiki deferrals for later models and unidentifiable all-depth/identity claims are valid dispositions. An unsupported auxiliary source such as VOLI may retain a documented unavailable benchmark and a named available proxy; it cannot silently satisfy a required acquired-input comparison. Unresolved required P-zone/CVD/node definitions and missing mandatory family evidence prevent global success.

The all-family command must exit nonzero for required blocked rows, stale evidence, omission, leakage or unresolved fidelity error. On failure, preserve the exact exception/result, input identities and evidence; reassess before another repair. No automatic retry/repair loop. There is no wall-clock kill. The accepted pass command is the scientific stop rule, with the source/raw-data/archive invariants intact.

## Explicit exclusions

No application code is written now. No raw sources/data/archive changes, bundled-code execution, workers, trades, purchases or excluded-product/contradiction-lint review. Later implementation uses Grok through Cursor under the selected project model and execution rules, one smallest complete slice at a time. Phase 2/3 scope remains solely [the one-page handoff](wiki/deferred-context-location.md).
