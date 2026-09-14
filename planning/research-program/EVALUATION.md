# Chronological evaluation and selection

Owner: `P15-03`, extended by `P2-02` and `P2-24`. These are registered research defaults. They define a finite experiment; they are not claims about trading edge.

## Freeze and exposure

The Phase 1 baseline is the [acquired measurement](/workspace/implementation/reports/phase1-live/historical-measurement/MEASUREMENT_REPORT.md), run `run-1.0.1`, and its immutable registry, scope, composed calendars, input manifests and accepted implementation identities. `P15-00` reads the actual receipts rather than deriving identity from a folder name. Preserve all 1,742 declared labels and each branch's eligibility; do not make every branch complete by borrowing another branch's denominator.

All existing dates have some research exposure. Record Phase 1 engineering/reconstruction/measurement and this plan's design exposure. The following are chronological out-of-sample comparisons of newly fitted rules/models, **not an untouched holdout**. Freeze candidates, search limits and scoring before running them. A result-driven amendment creates a new exploratory version and adds exposure; it never reuses the same dates as fresh confirmation.

## Outer and inner splits

Outer test blocks are calendar years 2022, 2023, 2024, 2025 and the acquired part of 2026. Earlier dates are training/lookback only. Within outer year `Y`, initial fitting data end June 30 of `Y-1`; tuning is July 1–September 30; calibration is October 1–December 31. Choose candidates/hyperparameters on fit+tune as specified below, refit chosen parameters through September 30, and calibrate only on October–December. Test year outcomes never choose that year's candidates.

Examples: for test 2022, initial fit is 2020-01-01 through 2021-06-30, tune July–September 2021, calibrate October–December 2021. For test 2025, initial fit expands through June 2024. Missing years/inputs stay missing; no random split fills them.

Purge any training row whose label interval overlaps a tune/calibration/test interval or whose label was not available before the fitting cutoff. Add one entire eligible account day between adjacent partitions; the earlier partition loses the boundary day. Group all events, variants, overlapping horizons and assets from one account day together. No row-wise shuffle split, ordinary IID standard error, or random-fold stacking.

Hyperparameter tuning uses the fixed grid in [model fitting](MODEL_FITTING.md). Rule selection uses the finite bank in the [Phase 1.5 search contract](/workspace/planning/phase-1-5/SEARCH_CONTRACT.md). Ties within 1% of the best tuning loss/score choose the simpler model, then lower candidate ID lexically. Complexity order is constant/base rule, linear, hinge basis, combination; fewer changed axes wins within an order. Never use test results to break ties.

## Causal stacking and adaptation

Generate every upstream training prediction chronologically. Use consecutive 20-eligible-day blocks; for each block, fit on prior available labels and reserve the most recent 42 eligible prior days for calibration. Minimum fit history is 126 complete days and 500 rows. Hyperparameter selection uses the 42 eligible days immediately before calibration, with training before that; if unavailable, use the declared default hyperparameters. A fold therefore may have no supported upstream predictions early on. Preserve the warm-up mask and loss of training support.

Any Phase 1.5 selected-rule role used in a historical Phase 2 row must be selected using evidence available before that row's block. Do not apply the global 2026 winning rule backward as if it had been selected in 2022. Persist `selection_manifest_id`, its cutoff and all candidate IDs for each block. Always retain the fixed source baseline features. For scarce cells, use the baseline role and mark selection unsupported.

Initial Phase 2 comparison holds parameters fixed for an outer test year. The adaptation experiment later compares: fixed annual; monthly refit at the first account-day open; weekly refit at Monday account-day open; and monthly refit plus intraday intercept updates. Refit uses a fixed trailing 756 complete eligible days (or all available if fewer), with the trailing 42 days reserved for calibration. The selected model/rule families and hyperparameters remain frozen for the outer year. Intraday updates may consume only matured, published labels, per the exact update rule in the Phase 2 adaptation contract. Every fit is versioned and becomes available at the next scheduled issue after measured fitting completion, never retrospectively at its data cutoff.

## Support and honest terminal outcomes

For a fitted continuous expert: at least 500 complete training rows on 100 account days, and 100 evaluation rows on 30 days. For a binary head: additionally at least 20 examples of each class on at least 10 distinct training days. For multiclass: apply that condition to each class; unsupported classes are pooled into an explicit `other_low_support` only if the target contract allows it, otherwise use the empirical prior and mark the head low-support. Never silently remove rare source branches.

For a Phase 1.5 upgrade: at least 100 resolved benchmark opportunities on 30 eligible test days in aggregate, represented in at least three outer blocks. A branch below the gate is `inconclusive_support`, even if all six examples succeed. It remains in the registry and downstream baseline allowlist, with low-support status. Support gates are research defaults and their counts must be shown alongside sensitivity at half/twice the gate; changing the gate cannot manufacture a claim. A disposition never deletes a candidate: `inconclusive_support`, `rejected_by_evidence`, `retained_baseline` and `unsupported_owned_input` keep the full population, parameters and diagnostics in the trial ledger and the retention set; "inactive" means not consumed by the next phase's training by default.

## Trial ledger

`TrialRecord`: trial_id, parent_trial_ids, family, branch, outer_fold, stage, bank, exact parameters, code/data/plan hashes, fit/tune/calibration windows, outcome-exposure cutoff, candidate population counts, score/loss, support, all test metrics, reason, disposition, runtime, artifacts, and `failure_attribution`. Write append-only JSONL; a new attempt gets a new ID and `replaces_attempt_id`, leaving the old row intact. Thresholds below are the [retention](RETENTION.md) rule 2 values, fixed before any candidate result is read.

`failure_attribution` is required for every deselected, inconclusive or not-promoted candidate. It is an ordered list drawn from `frequency` (entries below the frequency floor), `location_miss` (objective not reached while price came within 0.25 S of it, or adverse excursion beyond 0.5 S before any favorable 0.5 S), `confirmation_delay` (missed-move share above the family median), `adverse_before_target` (stop-first share above the family baseline), `cost_sensitivity` (sign reversal under the stress setting), `support` (below the support gate), `coverage` (unexplained input coverage loss). Each is computed from the diagnostics the Strategy Book already reports.

Bounded revisits: Phase 3 re-screens every retained candidate whose first attribution is `location_miss`, using its improved locations. Phase 4 re-screens every retained candidate whose first attribution is `confirmation_delay` or `adverse_before_target`, using the response and entry experts. A revisit is one registered pass over the retained set with the same folds, scores and promotion gates; it is not a new open search and adds no neighbors.

## Scores and uncertainty

Each family report contains (a) all attempted variants, (b) common complete-day paired comparisons, and (c) full candidate-specific coverage. A method's own source prerequisites remain in its eligible population. No missing feature/outcome is silently treated as no-setup. Unresolved order is an explicit excluded primary outcome with counts and pessimistic/optimistic bounds.

For setup rules the primary score is the mean daily net points in the deterministic one-contract benchmark in [outcomes](OUTCOMES.md). Compare a candidate with the unchanged baseline on common complete eligible days, including zero-entry days. Also report eligible opportunities/day, retained baseline opportunities, new opportunities, ordered target/stop rate, median net points/opportunity, drawdown from day-start, confirmation delay and missed-move counts. This benchmark measures an isolated family under a fixed scheduler; it is not a combined portfolio or a certification of the user's daily target.

For forecasts: QLIKE for variance; pinball for excursion/time quantiles; multiclass log loss and Brier for probabilities; absolute error for continuous state forecasts; censored time outcomes use the discrete survival loss specified in Phase 2. Report calibration and support for every head, horizon, session and year. Standardize multihead tuning losses by the loss of the training-only baseline, with denominator `max(abs(baseline_loss), 1e-8)` except QLIKE: use QLIKE excess `y/v - log(y/v) - 1` for positive y, and ordinary QLIKE differences for zero y. Average only supported heads with equal head weights; report the supported-head set so missing difficult heads cannot improve the aggregate silently.

Uncertainty uses a paired circular moving-block bootstrap of account days, block length 5, 2,000 draws, NumPy `Generator(PCG64(15022026))`. Draw block starts uniformly within each calendar-year segment and wrap only within that segment; concatenate blocks and truncate to its original day count. Use identical draws for baseline/candidate and all variants. Report percentile 2.5/97.5 bounds of the mean difference. Also report block lengths 1 and 10 as sensitivity, not additional selection opportunities.

For an exploratory one-sided improvement p-value use the centered bootstrap: observed mean difference `d`; each draw computes `d_b`; `p=(1 + count(d_b-d >= d))/(B+1)` under the null of no mean improvement. Family-level p-values include every candidate tested at that decision stage. Apply Holm adjustment: sort p ascending, compare `p_(i) <= .05/(m-i+1)` until the first failure, reject no later hypotheses. Publish raw p, adjusted p, candidate count and all unsuccessful trials. This dependence-aware exploratory procedure does not erase prior exposure or make adaptive search confirmatory.

Promotion requires: software/causality gates pass; support passes; paired mean improvement > 0 with the 95% lower bound > 0; Holm-adjusted p <= .05; at least three supported outer blocks and a positive difference in at least 60% of supported blocks; no cost-stress sign reversal at the declared stress setting; and no unexplained loss of input coverage. Frequency is a second objective: publish the quality–frequency Pareto set. A candidate with <50% of baseline entries cannot replace the family baseline; it may remain a separately labelled high-selectivity option if it passes all other checks. Keep the baseline whenever no candidate clears the gate.

## Economic evidence and limits

Show every eligible account day: net dollars, trades, zero-trade indicator, day-start worst marked P&L, risk-stop trigger, slippage/gap breach, and coverage. Summaries include median, mean, 5th percentile, worst day, fraction below $0/$1,000/$3,000 and fraction exceeding the $1,000 loss limit. Do not replace the user's daily floor with an average threshold, hide zero days or clip a loss to the limit.

Phase 1.5 and Phase 2 may close with retained baselines or negative/inconclusive findings. They cannot claim the final economic goal is met. Only a later combined decision replay can evaluate the integrated historical daily distribution; future realized performance remains a separate question.
