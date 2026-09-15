# Phase 1.5 implementation specification

Implement a finite, auditable comparison of individual setup rules. Preserve the accepted Phase 1 baseline, label every departure and return either a supported upgrade, a retained baseline, or an explicit inconclusive/unsupported result for every family. Do not start Phase 2 models, a final entry integrator or a P-zone location optimizer here.

## Existing code to reuse

All existing paths in this table are under `/workspace/implementation/src/trading_research/research/method_pack/`. They were inspected while writing this pack. New signatures below are proposed, not existing APIs.

| Existing module/symbol | Use |
| --- | --- |
| `historical_features.HistoricalFeatures`; `bars`, `range`, `profile`, `vwap`, `prior`, `local`, `coverage`, `at` | Same-contract native market access and completed-window features. |
| `native_discovery.scan_branch(market, row)` | Authoritative frozen branch/scanner dispatch, including extra units and manifest binding. Prefer this to recreating the dispatch table. |
| `event_time.build_event_window`, `EventWindow`; `event_cache.cached_window`, `prepare_date` | Reuse versioned native transforms and cached event-time views. |
| `mbp1_views.plan_window`, `iter_mbp1_window`, `trade_view`, `bbo_view` | Native identities, executions and quote adapters. |
| `historical_price_scanners.scan_jumbo`, `scan_green_failure`, `scan_green_refinement`, `scan_green_vwap` | Immutable source-reconstruction baseline functions. |
| `historical_auction_scanners.scan_saint`, `scan_member`, `scan_keani`, `primary_balance` | Immutable auction-method baselines. |
| `historical_flow.batches`, `exact_contact`, `local_observations`, `flow_stages`, `scan_sires`, `scan_microbalance` | Native batch rules, local flow and source sequence baselines. |
| `historical_process_scanners.scan_refill`, `scan_scalp`, `scan_jetbundle`, `scan_stoic_data`, `scan_risk` | Research/scalp/process scope; risk is not a market-entry scanner. |
| `historical_assembly.HistoricalEpisode`, `window_result` | Read source verdict, inferred-strategy verdict, stages, geometry and omission fields without collapsing them. |
| `measurement_outcomes.interval_extrema`, `rounded_coverage`, `boundary_order` | Independent coverage/extrema conventions; preserve old output schema. |
| `strategy_pzones.inferred_pzones`; `strategy_options.gamma_at`, `key_gamma_reference`; `strategy_context.inferred_auction`, `inferred_macro` | Existing disclosed inferred inputs remain baselines. Do not relabel them source-exact. |

New code root: `implementation/src/trading_research/research/rule_discovery/`. Shared schemas, time-safe labels and execution benchmark go in `research/contracts/`. New tests mirror those namespaces under `implementation/tests/`. Accepted Phase 1 files stay unchanged; if an adapter discovers a baseline bug, write a separate discrepancy report and preserve the accepted version for comparison. A necessary new baseline repair is a separately versioned rule and exposure amendment, never a silent mutation.

### Baseline adapter details that must not be guessed

`HistoricalFeatures` enables reconstructed strategy semantics from `records['strategy_reconstruction']` **during construction**; this selects `ReconstructionSessionPolicy` and `StrategyWindow`. Build the records mapping from the bound registry's supplied records plus its `registry_sha256` and `strategy_reconstruction` fields, matching `historical_runner._records`. Do not set `market.reconstruct=True` afterward: that would leave the wrong window/calendar object. Dispatch each frozen coverage row through `native_discovery.scan_branch`, which checks the scanner module/function identity against the manifest.

The default Phase 1 `HistoricalFeatures` window ends at 16:00 ET. Preserve that exact window for baseline parity. The new `MarketView` separately covers the full matching account day through 17:00/verified early close for Phase 1.5 labels/benchmarks and Phase 2 snapshots. Build those explicit native windows with `build_event_window`/`cached_window` and split at contract/closure boundaries. Do not extend the old market object and inadvertently change baseline scanner populations. New outcome horizons can use the separate full-account-day view; keep old Phase 1 outcome records unchanged and label the new measurement policy.

The old `historical_runner.software_identity` hashes **all** tests and tools, so new task tests/tools necessarily change that whole-tree identity. Do not bypass its checks or write new jobs into a frozen Phase 1 run root. The new baseline binding verifies every accepted baseline file hash and runtime listed in the frozen manifest, then the new runner records its own current code/test identity in a new root. Direct baseline scanner parity uses the bound original inputs/configuration; release verification distinguishes preserved baseline files from added code. Historical wiki/documentation identities use their frozen snapshots, not the newly edited shared wiki.

The accepted runtime's `measurement_runner.configure_runtime` only installs the tested stable-file digest cache and bounds Arrow worker counts; the new runner may reuse that startup behavior with parity evidence. Do not monkeypatch scanner logic, thresholds or market observations to implement a variant.

## Pipeline and proposed interfaces

```python
class MarketView(Protocol):
    def executions(self, start_ns: int, end_ns: int) -> Iterable[NativeBatch]: ...
    def quotes(self, start_ns: int, end_ns: int) -> Iterable[QuoteBatch]: ...
    def coverage(self, start_ns: int, end_ns: int) -> CoverageReceipt: ...
    def completed_bars(self, start_ns: int, end_ns: int, seconds: int) -> tuple[Bar, ...]: ...

def scan_baseline(market: HistoricalFeatures, family: str, branch: str) -> BaselineResult: ...
def build_formations(market: MarketView, spec: RuleSpec, cutoff_ns: int) -> tuple[Formation, ...]: ...
def build_references(market: MarketView, formation: Formation, spec: RuleSpec) -> tuple[Reference, ...]: ...
def enumerate_contacts(market: MarketView, reference: Reference, expiry_ns: int) -> Iterable[Contact]: ...
def resolve_source_context(market: HistoricalFeatures, family: str, branch: str,
                           reference: Reference, at_ns: int) -> ContextEvidence: ...
def advance_sequence(state: SequenceState, batch: NativeBatch | None, spec: SequenceSpec,
                     *, now_ns: int, inputs: SequenceInputs) -> SequenceState: ...
def scan_variant(market: MarketView, source_market: HistoricalFeatures,
                 spec: RuleSpec) -> ScanResult: ...
def compare_rules(baseline: RunManifest, candidates: tuple[RunManifest, ...],
                  split: SplitManifest, evaluation: EvaluationPolicy) -> Comparison: ...
```

`ScanResult` contains opportunities, rejected contacts, unknown-input contacts, formations, expired sequences and coverage omissions. `Formation` contains immutable ID, asset/contract, start/end/available-at, high/low, total volume, profile identity, construction kind and source parents. `Reference` adds lower/upper, issue/expiry, side policy and formation ID. `Contact` contains native batch IDs, contact time/known-at, touch/sweep distinction, pre-touch departure evidence and all possible prices when ordering is ambiguous. `ContextEvidence` retains each source prerequisite as true/false/unknown with its derivation and clock. Never flatten unknown to false before recording coverage.

`SequenceInputs` carries the frozen reference/context, newly completed bars and already available flow/cohort features. Validate every input clock <= now_ns. The driver invokes transitions on native batches, bar-completion clocks and deadline clocks; batch=None advances time/expiry without inventing a trade. Sequence working memory contains only prior batches/partial aggregates, with explicit evidence IDs.

For an unchanged rule, `scan_variant` delegates to the original baseline function and preserves its records. For a changed rule, enumerate its own complete formation/contact population; filtering only old qualifying setups cannot discover new geometry or earlier confirmations. Source adapters provide the unchanged branch context and unchanged stages from the inspected baseline functions and wiki predicates. A changed stage is explicitly replaced by the registered delta and its hypothesis ID; all other source prerequisites stay required. No monkeypatching globals, optimistic fallback to a different branch or recursive copying of whole scanner files per variant.

At most one opportunity per distinct contact/side/rule. A contact is rearmed only after complete native prices depart by `max(4 ticks, .1*S_at_first_contact)` beyond the reference on the approach side and remain outside for a complete 60-second bar. A new reference formation is a new population. Mirror long/short inequalities exactly; both sides in one ambiguous native batch remain ambiguous.

A numerical update to a developing reference is a new immutable version within the same `reference_lifecycle_id`, not a new independent contact population. Group contact/rearm state by `(rule_id, reference_lifecycle_id, side)`; record the exact version used at contact. The lifecycle ID hashes family, branch, native contract, formation ID and reference kind, excluding the later value/version clock. A newly formed independent area creates a new lifecycle. This prevents every VWAP/profile update from resetting touch history and manufacturing opportunities.

## Numerical reconstruction work

`P15-04` produces a source-to-operator ledger for EV/expected move, P-zone, KG1/gamma, auction-state/macro and every missing numerical operand from the completed registry. Each row names the wiki object, raw source anchor, existing implementation, exact formula if printed, availability, source-exact status and downstream dependency. Recover printed formulas and unit mistakes before searching improvements.

EV has three distinct quantities: printed source expected-value/range object; conventional IV-implied horizon move; our forecast of future realized movement. For a source that explicitly supplies annualized sigma and calendar horizon T years, conventional one-standard-deviation log approximation is `move_points=spot*sigma*sqrt(T)`, labelled model-derived; T uses actual seconds/(365*86400). It is not a proprietary EV reconstruction unless the source states that formula. Example spot100,sigma.2,T=.25 gives10 points. Source bands with unpublished probabilities/conditioning stay unknown. P-zone anchors and quantiles remain the existing disclosed baseline through Phase 1.5; improving their actionable locations belongs to Phase 3. Learned intraday volatility forecasts belong to Phase 2.

The source matching budget is one ledger pass plus at most two deterministic checks per printed formula/figure with sufficient dated inputs. If the source does not supply inputs/constants, stop with `not_identifiable_from_owned_source`; implement a labelled research alternative only if it is already in this search bank. Do not ask the user to decode proprietary values or optimize a substitute to match a screenshot.

## Primitives with exact causal definitions

Time formations retain source intervals as B0. Alternative F1 is the preceding 60 matching minutes ending at a registered source issue clock. F2 is volume-completed: at each source issue clock, walk backward over complete one-minute bars until cumulative executed volume reaches the median volume of the corresponding source formation over the prior 20 complete same-contract sessions, at most 180 matching minutes; include the whole final minute and record overshoot. F3 is detected balance: inspect trailing lengths15,30,60 minutes in that order at each source issue clock, choose the first complete window with `width <= .75*S_before_window` and efficiency `abs(C-O)/max(H-L,q) <= .35`; if none, no formation. `S_before_window` uses the prior 60 matching minutes ending before formation starts. Freeze selected geometry at its availability clock; never resize it using the subsequent breakout.

Trade-volume profile: aggregate executed size into integer tick bins. Smooth with triangular kernel `w_j=max(0,b+1-|j|)` for j=-b..b normalized to sum1, using bandwidth b=0 or 2. No Gaussian fit is required. POC is highest smoothed volume, ties closest to volume-weighted mean price, then lower tick. Build 70% value area contiguously from POC by adding the larger adjacent bin, ties lower first, until cumulative **raw** included volume reaches70% of total; use smoothed values for neighbor ranking only and disclose this alternative to the source profile. HVN is a local maximum over +/-2 bins with prominence `(peak-max(left_min,right_min))/max(peak,1) >= .20`, minima taken within 8 bins. Group equal plateaus into one node at their volume-weighted tick rounded to the nearest tick, ties lower. Node band spans adjacent bins with volume >=50% of that peak until a valley or 8 bins. Reject overlap duplicates by retaining higher prominence, then volume, then lower price. LVN uses the symmetric local-minimum criterion with neighboring peaks and the same registered neighborhood. All inputs precede reference issue.

VWAP is `sum(price*executed_size)/sum(executed_size)`. Its volume-weighted price dispersion is `sqrt(sum(v*(p-VWAP)^2)/sum(v))`; it is not forecast volatility or an unweighted standard error. Reference bands use VWAP±1 dispersion for the representative bank. Reset anchors are source anchor B0 or account-day open R1; a source-imperative anchor may change only in a separately labelled custom variant. Greek-weighted centroids are not called VWAP. Prior highs/lows use completed verified same-contract session/week/month windows as the baseline does; choose no future pivot or back-adjusted cross-roll value.

R1 computes its account-day VWAP/dispersion from the account-day anchor through the registered source issue time and freezes that band until the registered expiry. It is explicitly a frozen reference snapshot; do not silently reissue it every minute. Source developing-VWAP behavior remains its own baseline. Developing-profile alternatives that the source stage requires retain immutable value versions and the shared lifecycle/rearm rule above.

## CVD and cohort memory

For batch b, `D_b=sum(q_i*s_i)` over known aggressor signs s=+1 buy,-1 sell; `V_b=sum(q_i)` over all executions; `U_b=sum(q_i*1[sign unknown])`. Unknown volume remains separate. C0 is source/raw session-reset CVD `sum D_b`; C1 normalized delta=`sum D_b/max(sum(V_b-U_b),1)` over trailing 5 matching minutes; C2 exponentially decayed delta `Z_t=exp(-ln2*dt/300s)*Z_prev+D_t`, normalized by similarly decayed known volume; C3 price-level delta z-score: current 5-minute delta minus prior 20-session same-time-bucket median, divided by `max(1,1.4826*MAD)` from those past sessions. If required histories or >20% aggressor volume is unknown, C1–C3 are unavailable. Raw price/volume remain usable where independently known.

Fixture batches signed sizes +10,-4,unknown6: known delta6, total20, unknown6, raw CVD6, known-volume delta ratio6/14. Because unknown share=.30, the ratio is numerically observable but fails the .20 admission gate; retain both value and support flag. Never silently classify unknown6 as selling.

Cohort markout at resolved horizon h=30,120,300 seconds: `M_h=sum(q_i*s_i*(mid_(i+h)-trade_price_i))/sum(q_i)` for known-sign trades whose full horizon and future midpoint are available by the snapshot. Bid/ask midpoint is not a fill. Store buy and sell cohorts separately, median markout, positive fraction, volume and unresolved cohort count. “Rewarded buyers” means positive buy markouts, not high CVD alone. A current unresolved cohort cannot borrow later markouts. For Refilling memory also retain distinct touch count, time since formation/last contact, pre-touch departure, signed volume at the band and previous resolved contact reactions.

## Response state machines

All response alternatives start after a causally issued reference and an admissible distinct contact. Source confirmation B0 remains exact to its disclosed reconstruction. S1 is price reclaim: after a strict edge sweep by >=1 tick, first complete 60-second bar closes back inside; decision is that close's known-at. S2 is reclaim+defended retest: after S1, first later contact within 1 tick of the reclaimed edge, followed by a complete 60-second bar closing at least 2 ticks in the favorable direction without an intervening complete close beyond the swept extreme. S3 is flow-supported reclaim: S1 plus C1 signed in trade direction >.20 and at least one resolved prior 120-second cohort with mean signed favorable markout >0; all cohort resolutions must be known by the S1 decision. S4 is failure-to-progress: within 120 seconds after contact, known opposing aggressive volume exceeds its prior 20-session same-bucket .75 quantile, adverse extension is <=max(2 ticks,.1S), then a complete 60-second favorable close exceeds contact batch favorable extreme by1 tick. Unknown aggression cannot qualify S3/S4.

Sequence states: `issued -> contacted -> swept -> reclaimed -> retested -> confirmed`, with explicit optional stages selected by the recipe. `expired`, `invalidated`, `input_unknown` are terminal for that contact. Default deadline is10 minutes from contact, bounded by source expiry. S4 follows `contacted -> pressure_observed -> stalled -> confirmed`. Store stage times, dependencies and rejected alternatives. No event may satisfy two ordered stages in the same ambiguous batch. Absorption, continuation, stop-run, failure, imbalance and microbalance remain distinct source mechanisms; S1–S4 are representative alternatives, not a universal absorption classifier.

## Completion boundary

The final pack contains the entire baseline registry, all attempted candidates and deltas, construction/coverage evidence, nested selected-rule manifests, rule-level and daily diagnostics, unchanged-entry exit comparisons, and a Phase 2 dependency allowlist. Every source family and every search mechanism has a disposition. Negative results close a correctly executed experiment; missing code does not. All important active definitions and evidence pointers are added to the shared wiki.
