# Experiment and improvement protocol

## 1. What may be claimed

`implementation_correct` means contract, arithmetic, chronology, prefix-invariance and execution tests pass. `historically_promising` means the frozen candidate exceeds its registered controls in the retrospective evaluation below. `prospectively_improved` requires the later unseen-session test. These are different statuses. No strategy is called better merely because it has more features or reproduces a highlighted source example.

The 2024–2026 archive and many source examples have already been examined in this task. Do **not** call those years untouched holdout data. The new implementation can still run chronological evaluation on them, but it must call it retrospective development evaluation and disclose the exposure.

## 2. Baselines, model roles and comparisons

Every card supplies one executable default. Run it before searching a grid. Keep the old implementation's results only as a defect-regression comparison; they are not a competitive baseline when they contain leakage or malformed predicates.

For signal models compare: (a) corrected price/structure-only parent, (b) full default, (c) selected candidate, and (d) each feature ablation named in the card. Use the same qualified input/session universe, entry/exit simulator, direction convention and costs. Also report full available coverage for each model separately so common-universe filtering cannot hide attrition. An order-flow gate must face a delay-matched price-only control at the same scheduled observation deadline on **all** parent interactions, not only the interactions where its flow predicate passed.

For descriptive/context models the primary output is a distribution or calibrated forecast, not a trade win rate. Estimate class probabilities from training counts using `(count+0.5)/(N+0.5*K)` for K mutually exclusive classes. Compare conditional probabilities against the unconditional same-clock training distribution with multiclass log loss and Brier score. For numeric boundaries use empirical coverage and quantile pinball loss `L_q(y,f)=(q-I[y<f])*(y-f)`. If a context is proposed as a trading filter, test it through the explicit consumer in its card using the same parent opportunities.

For management models replay the identical filled-entry ledger and compare net outcome, drawdown and exposure time. No entry can be added, removed or shifted when comparing exits. Components such as VWAP, profile nodes, CVD and refill state are tested both for their own correctness and incremental benefit in a fixed consumer; they are not forced into 85 unrelated trading systems.

## 3. Bounded grids

The `parameters` object in each model card lists units, default and allowed values. A value not listed is prohibited until a new specification version is registered. `bindings` fixes all required engine inputs and prevents implicit defaults from changing across runs.

Use this deterministic search per model:

1. Baseline = the complete default configuration.
2. Screen one factor at a time: for each parameter in lexical name order, substitute each nondefault listed value, leaving all other defaults unchanged. Evaluate all registered candidates; do not stop when a result looks attractive.
3. Rank **parameter axes**, using their best inner-development improvement over default; ties by fewer values then lexical name. Select at most two axes with positive improvement. Evaluate their full pairwise combinations, excluding configurations already evaluated. No third-axis interaction search.
4. Total unique alpha configurations <=48 per model. If the listed one-factor screen alone would exceed 32 configurations, the specification validator must fail; reduce the grid explicitly before any performance run. The remaining budget is for pairwise combinations, visited in lexical serialized-config order, stopping at 48. Persist untested configurations and the deterministic cap reason.
5. Compare the chosen candidate with the default using the chronological protocol. If sample/stability criteria fail, keep the default as the specification baseline and record `no_supported_improvement`; do not silently take the best-looking failure.

Fixed source-comparison clocks, both sides, multiple output horizons and option scenarios are separate reported cohorts, not opportunities to select the best percentage after the fact. If one is later chosen as a preferred trading configuration, it consumes a registered candidate and an inference comparison. All attempted configurations, ablations, discarded runs, metric choices and fixes are logged in `experiments`; a failed backtest is not erased from the search record.

Quality thresholds, missing-data rules, timestamp shifts, aggressor conventions, first-visit retirement, lookahead prevention and execution ordering are **not alpha parameters**. Never tune those to improve PnL. Cost/latency sensitivity runs are robustness checks, not searches from which to choose the most favorable fill assumption.

## 4. Chronological evaluation

Freeze the data manifest and code/spec hash first. Primary archive universe begins 2020-01-02 where the necessary feed exists and ends 2026-08-31. Actual per-model eligibility begins only after its full warmup and complete input coverage. Do not fabricate earlier NQ standalone trades; the audited MBP-1 trade-action adapter may supply the earlier period. Print sample losses by reason.

Initial development uses 2020–2022 for construction/calibration and 2023 for the first chronological comparison. Subsequent retrospective outer blocks are 2024, 2025, and January–August 2026. Before each outer block, select using only the preceding 36 calendar months (or all available history if less, minimum 24 months). Within that training interval evaluate candidates over its last four nonoverlapping calendar quarters, always fitting histories/distributions only on data earlier than each scored event. Do not use future folds to fill warmup.

All events, parameter fits and labels belong to an exchange session. Keep entire sessions together. A setup spanning midnight belongs to its designated trading date. Purge any training event whose outcome horizon intersects a validation block and embargo the following five trading sessions when training samples resume after a scored block. Cross-session targets with five-session lifetimes therefore cannot leak labels across the boundary. Ordinary prior-only rolling features may carry already available training observations into validation; outcome labels may not.

Select the candidate maximizing inner-quarter mean net R0 per **eligible session**, including zero-trade days, for a signal/management card. A context card minimizes its registered proper loss. Require at least 60 completed trades on at least 30 distinct sessions for a signal and 150 sessions for a context; otherwise selection is `insufficient_sample`. A filtered cell needs at least 20 training observations before emitting an unsuppressed conditional probability; otherwise use the explicitly smoothed parent distribution and flag sparse cell. Outer-block results never tune that block's parameters.

Tie policy: differences in primary metric <=0.001 R0/session or <=1e-4 mean proper loss are ties. Choose fewer enabled filters, then fewer nondefault parameters, then smaller total maximum lookback, then lexical config hash. Do not use the outer test as a tiebreaker.

After retrospective comparison, freeze one candidate per model/consumer and a prospective start timestamp **later than both the freeze time and the latest inspected/acquired observation**. First scored session is the next complete scheduled session after that timestamp. No already-downloaded or source-inspected session counts as prospective. Default prospective horizon is 120 eligible trading sessions and at least 100 filled trades for a signal. If the sample threshold is not met, extend to 250 eligible sessions with the original configuration; at 250 report insufficient evidence. Do not stop early when performance looks good. This specifies a future evaluation; do not create a monitor or fetch data as part of writing the handoff.

## 5. Metrics and uncertainty

Report counts at every stage: expected sessions, quality-qualified sessions, warmup sessions, parent interactions, feature-qualified episodes, signals, submitted orders, fills, no-fills, stopped/target/time exits, censored/ambiguous cases and coverage exclusions. No-event sessions remain in the eligible denominator. A conditional reach rate uses actual eligible touches as denominator; an hourly rate uses eligible **hours**, not days with at least one success.

Signals: primary net R0 per eligible session; additionally net dollars per session for the one-contract unit, net R0 per filled trade, win fraction, payoff ratio, profit factor (undefined if zero gross loss), chronological maximum drawdown, worst 5% session mean, median holding time, turnover and exposure. Report performance per outer block, side, clock, volatility quartile and raw contract. Volatility quartile thresholds are fitted on training, never the full evaluation sample.

Contexts: empirical outcome frequencies with counts, log loss, Brier or pinball loss as registered, calibration bins, interval coverage, and the fixed consumer's incremental result. A target-reach probability is not a profit probability. Management: paired net changes on identical entries plus tail loss/drawdown and missed-target/time-exit changes.

For paired uncertainty use a circular moving-block bootstrap of the ordered **session-level paired difference series**. Block length=5 sessions, replicates=10,000, RNG=NumPy PCG64 seed=20260911. For each replicate draw start indices uniformly from 0..n-1, concatenate five-session blocks with wraparound until n observations, truncate to n, and average. Confidence interval is type-7 2.5/97.5 percentiles. The one-sided centered-null p value is `(1 + count(mean(resampled(diff-mean(diff))) >= mean(diff)))/(10001)`. For loss metrics flip the sign so positive means improvement. Also report block lengths 1 and 10 as sensitivity; they do not replace the default after looking at results.

On the frozen outer/prospective comparison list, correct the primary p values across all tested model-consumer claims with Holm's procedure: sort p ascending, compare p_(i) with 0.05/(m-i+1), reject in sequence until the first failure; later claims are not rejected. Record m including negative/insufficient comparisons (insufficient has p=1). Do not present 4,080 screened grid points as if one unselected hypothesis had been tested. Bootstrap intervals are useful uncertainty diagnostics, not a cure for historical source exposure or unrecorded experimentation.

## 6. Improvement gates

Historical signal promotion requires all of:

- All implementation/data/chronology checks pass; no silent unavailable-to-false conversion.
- Positive selected-minus-corrected-baseline net R0/session in the combined retrospective outer series, lower 95% paired-bootstrap bound >0, and Holm-adjusted primary comparison passes.
- Positive net R0/session after baseline fees/slippage, and positive selected-minus-baseline improvement in at least two of the three outer blocks (2024, 2025, 2026 partial). No single outer block may contribute >70% of aggregate positive improvement.
- Under two additional adverse ticks per fill and $10 round-trip fees, net mean remains >=0; report failures plainly. Chronological maximum drawdown and worst-5%-session loss must not worsen by more than 20% relative to the corrected baseline when that baseline quantity is nonzero. If it is zero, report the comparison undefined and require an explicit risk review before promotion.
- The candidate has a stability neighborhood: at least half of its actually evaluated one-step parameter neighbors retain positive mean improvement, minimum two neighbors. If fewer exist, call stability unmeasured; do not promote on an isolated optimum.

Context promotion uses the corresponding positive proper-loss improvement and calibrated coverage, then requires incremental benefit in its specified consumer before claiming better trading performance. A component may be retained for correct measurement and interpretability without passing an alpha claim. Rare models that fail sample gates remain implemented research hypotheses, not fabricated negatives or declared failures of the source.

Prospective promotion repeats the same registered comparison on the future frozen sample. Any change to thresholds, input conventions, targets, entry timing, costs or selected universe starts a new prospective version. Corrections to a genuine implementation bug must preserve the old result and restart the affected claim; they are not a way to reuse the same untouched label.

## 7. Reports and charts

For each family produce both workspace-required tables:

```
family | variant | n | faithful_disagreements | status | report path
family | id | verdict | fixture | leakage | proxy-as-faithful | notes
```

For these new research variants set `faithful_disagreements=not_applicable_research_definition`; audit verdict states implementation/experiment status and whether observable proxies are correctly named. Never invent a new source-faithful pass count. Before runs, n/status is `not_run`, not zero observations.

Each signal chart must show frozen formation geometry, separately ending high/low lines, profile/flow snapshot cutoff, event sequence, confirmation, order arrival/fill, original stop, target, exit, coverage gaps and timezone. Include a complete positive, negative, no-fill and censored/ambiguous example when each exists. Choose examples deterministically: earliest qualifying date per state after sorting by UTC timestamp, plus all retained historical defect-regression cases. If a state has no case, state that; never manufacture a source-positive example. Chart correctness is verified against the same event ledger used for metrics.
