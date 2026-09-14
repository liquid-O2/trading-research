# Phase 2 context and expert specification

Entry gate: a verified Phase 1.5 phase receipt covering every task and family, including its limitations and fold-specific selected-rule manifests. Exception: P2-09, P2-10 and P2-03 may start from the verified P15-02 receipt (the native MarketView) instead of waiting for that phase receipt; their receipts must be re-verified under P2-00 before P2-04, P2-11 or any method expert consumes them. Do not begin any other Phase 2 implementation while any Phase 1.5 task is still in progress. This pack is written now so the next implementer can start without another planning interview.

## Result and code boundaries

Build separately fitted experts for major context mechanisms and source strategies, sharing deterministic feature calculations and common fitting code. Produce intraday forecasts, current descriptive states and conditional method plans. One jointly fitted volatility expert consumes GK, YZ, HAR and all available IV groups. A collection of hand-written state labels alone is not the required learned context system.

New root: `implementation/src/trading_research/research/experts/`. Reuse `research/contracts/` from Phase 1.5; extend schemas additively with version bumps. New reports: `implementation/reports/context-experts/<run-id>/`; large row/model caches: ignored `/workspace/data/derived/trading-research/context-experts/`. Every artifact binds the Phase 1.5 input release, plan, features, training cutoffs, labels and exact model inputs.

| Expert/artifact | Output | Required specification |
| --- | --- | --- |
| `joint_volatility` | Joint multihead future variance, intervals and converted movement scale | [Volatility](VOLATILITY.md) |
| `range_path` | Remaining up/down excursion, first-passage time distributions, break topology and post-break acceptance | [Context](CONTEXT.md) |
| `auction_session` | Current operational auction/day-state descriptors, future transitions, session opportunity quality | [Context](CONTEXT.md) |
| `flow_memory` | Rewarded aggression, failed pushes, defended persistence and transition forecasts | [Context](CONTEXT.md) |
| `cross_market` | Native related-market divergence, lead/lag, spot/IV coupling and NQ path contribution | [Context](CONTEXT.md) |
| `options_context` | Native chain exposure, flow, changes, shock scenarios and context forecast | [Options](OPTIONS.md) |
| `intraday_oi` | Weakly supervised OI change estimates, uncertainty and baseline comparison | [Options](OPTIONS.md) |
| one artifact per source entry method | Occurrence probability, conditional utility/path, session/branch/reference suitability and conditional plan | [Method experts](METHOD_EXPERTS.md) |
| research-process artifacts | Refilling memory, jetbundle transitions and macro-state contribution; risk remains a rule overlay | [Method experts](METHOD_EXPERTS.md) |

These are responsibility names, not a prescribed final model count. Unsupported heads remain explicitly unavailable. Shared input features are computed once; separately fitted experts have separate parameters, targets, validation and retirement decisions.

## Proposed APIs

```python
def build_snapshot(market, issue_at_ns: int, feature_spec, parents) -> Snapshot: ...
def build_targets(market, snapshot: Snapshot, target_spec) -> tuple[TargetRow, ...]: ...
def fit_expert(dataset: ExpertDataset, split: SplitManifest,
               config: ExpertConfig) -> ExpertArtifact: ...
def predict_expert(artifact: ExpertArtifact, snapshots: tuple[Snapshot, ...]) -> tuple[Forecast, ...]: ...
def build_conditional_plan(method_id: str, snapshot: Snapshot,
                           forecasts: tuple[Forecast, ...], rules: RuleRelease) -> ConditionalPlan: ...
def replay_context_baseline(plans, opportunities, market, policy) -> ContextReplay: ...
```

`ExpertConfig` declares expert ID, feature groups/columns, target heads/units, model recipe, hyperparameter grid, fit/calibration/adaptation schedule, minimum support, missing-input fallback, runtime budget and exact ablations. `TargetRow` stores snapshot ID, target ID, interval, value or null, event/censoring kind, coverage, label-known-at and evidence. Labels live in `experts/labels/`; the feature package may not import that package. `ExpertArtifact` includes all transformations, coefficients, calibration, target support, training/cutoff times, effective availability and parent model IDs.

Current state and future label are different records. The true final RTH day type is a future target before the close. A partial auction description may be known now. The same column name must not be used for both.

## Required feature groups

Price/auction: current and prior overnight/RTH/account-day ranges, completed source time ranges, profile POC/VAH/VAL and shape, developing and rolling/composite profiles, open location/type, initial balance once complete, value migration, prior extremes, range consumed, distance to source reference, current branch prerequisites and source objective already consumed. Retain each value's availability clock.

Activity/flow: realized variance, range and signed returns at 1/5/15/60 minutes; volume and trade-count intensity relative to prior 20 same-time buckets; CVD variants selected in Phase 1.5; buy/sell cohort markouts, unknown aggression, failed pushes, imbalance/defense persistence, touch history and reference age. Include BBO spread/depth where native coverage supports them.

Related markets: ES, QQQ, SPY, native NDX/SPX and owned YM/RTY, with per-asset clocks, standardized movement, multi-scale SMT, lagged coupling and input gaps. Source setups are NQ-only; these are context/response features, not cloned source strategies on each asset.

Options/volatility: all owned native chains and IV products, expiry/strike structure, gamma/vega/vanna/OI and flow, spot/IV/time changes, cross-expiry concentration, 0DTE plus1–7,8–30,31–90 calendar-day boards, options activity/uncertainty and updated OI. Do not limit context to one maximum-gamma strike or prior-day OI.

Macro/event: only owned dated releases/calendars with known publication and vintage; time to/from scheduled events, released surprise if a dated prior forecast is owned, and lagged macro quantities. Latest revised series cannot be used historically as though unrevised. Missing news/macro inputs produce input-limited features, not fabricated “no event” flags.

## Downstream boundary

Phase 2 may recommend side, reference identity, confirmation recipe, target ambition, time window and invalidating evidence. It may rank a source method or say support is low. It does not create Phase 3 custom actionable price zones, choose the final NQ entry or require every forecast to become a hard veto. A reference recommendation points to an already available Phase 1.5/source reference; new option/volume areas are context boards until Phase 3 validates their location role.

Compare ungated source rules, a price-context baseline, a fixed context score and the fitted method expert with identical response and execution policies. Context contribution must survive incremental/ablation tests and changed coverage. All final entry/economic claims remain reserved for the integrated phase.
