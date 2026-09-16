# Phase deliverables and definition of done

Receipts, matrices and gate reviews prove that software ran and that checks passed. This contract defines what the user receives at the end of each phase and the exact artifact that marks a phase finished. It adds reporting requirements; it changes no formula, budget, gate or date.

## Phase 1.5 outcome: Strategy Book, version 1

One entry per family and per branch in the frozen Phase 1 registry, including research, process and risk units, with entry setups distinguished from observations. Every number carries a pointer to the immutable artifact it was computed from. Sections per branch:

1. **Definition.** Source method, branch, ordered stages, reference, confirmation, structural stop and objective, expiry, session clock, and for every operand whether it is source-exact, printed-but-different, inferred or not identifiable, linking the source-reconstruction ledger row. For every source stage of the branch, one status: evaluated, evaluated_with_inferred_substitute, structural_not_required, unevaluated, scheduled_build, or personal_record_excluded, with the ledger row or code reference that justifies it. Where a literal operand is kept by construction or by declared assumption, the entry names it and the assumption ID.
2. **Population.** Eligible account days, opportunities, opportunities per day and per week, by year; unknown-input, ambiguous-order and missing-coverage counts; the stage-rejection funnel (how many contacts fail at which prerequisite).
3. **Base rates, baseline B0, fixed one-contract benchmark.** Ordered outcome rates (target first, stop first, neither, ambiguous) on the rule's structural geometry and on the diagnostic grid; net points per opportunity (mean, median, 5th and 95th percentiles); win rate and payoff ratio; expectancy per eligible day; daily P&L distribution (median, mean, 5th percentile, worst day, fraction of days below zero); maximum drawdown from day start; time to resolution; MFE and MAE quantiles at each horizon; confirmation delay; missed-move counts. Every rate carries the contract's block-bootstrap 95% interval and its support count.
4. **Conditional rates by pre-registered regime dimension.** One-way cuts only, no interactions, each cell with count, rate and interval, cells under 30 opportunities marked low-support. Dimensions are frozen in `REGIME_DIMENSIONS.json` before any candidate result is read, each computed causally from owned data as of the decision time: calendar year and outer fold; session bucket (Asia, London, New York morning, New York afternoon); day of week; realized-volatility tercile from the prior 20 sessions' daily ranges; overnight range relative to its prior-20-session median, in terciles; prior-close VIX bucket (below 15, 15 to 20, 20 to 30, above 30); inferred aggregate gamma sign at 09:32 (positive, negative, unknown; labelled inferred); prior-day type by the registered trend-or-balance rule; scheduled macro release day (CPI, payrolls, FOMC) where the calendar is owned. This section is descriptive. It never selects candidates, and it is disclosed in the exposure ledger.
5. **Upgrades.** Every attempted candidate for the family with bank, axis, parameters and disposition (attempted, duplicate, not applicable, unsupported, timed out, rejected, selected). For the selected candidate per outer fold: sections 2 to 4 recomputed and paired against B0 with differences, intervals, raw and Holm-adjusted p, fraction of positive blocks, cost-stress result, and the quality-frequency Pareto set. The exit study E0 to E4 on the frozen entries.
6. **Verdict.** Promoted, retained baseline, inconclusive support or not applicable, with the reason, the fold-specific selected-rule manifest IDs, and the all-history descriptive recommendation kept separate from the causal fold roles.
7. **Limitations.** Coverage gaps, inferred inputs, unknown operands, exposure notes, and what the branch's numbers cannot claim.

**Formats.** `STRATEGY_BOOK.md` (one section per family, one subsection per branch), `STRATEGY_BOOK.json` (the same numbers under a versioned schema) and one CSV per branch for sections 3 to 5. Produced by P15-20 from the immutable trial ledgers. A **B0-only edition** covering sections 1 to 4 and 7 is produced as soon as the outcome machinery exists, so base rates are readable before any search result; it is regenerated, never edited, when the full edition is built.

**Definition of done for Phase 1.5.** The release receipt verifies; every registry branch has a book entry with a verdict; the B0-only and full editions render from artifacts with no hand-typed number; all attempted candidates appear; the Phase 2 allowlist and selected-rule manifests are frozen.

## Phase 2 outcome: Strategy Book, version 2, plus context experts

Per strategy, adding to version 1: fitted conditional probability of target-first, expected net points and suitability (session, reference, confirmation, timing, target ambition) as functions of the context state; calibration by year and session (reliability tables, Brier and log loss); a context-sensitivity ranking from group ablations (volatility forecast, options and gamma exposure, auction and day state, cross-market coupling, flow); the immutable conditional plan; and the adaptation comparison (fixed annual, monthly, weekly, monthly with intraday updates). Per expert (joint volatility, remaining range and passage time, auction and day quality, options flow and repricing, intraday OI estimate): scores against the registered baselines by horizon, session and year, ablations, support and lineage.

**Definition of done for Phase 2.** The release receipt verifies; every strategy has a version 2 entry and every expert has a scorecard; the chronological replay, ablations and lineage are complete; the Phase 3 handoff lists which context outputs are admissible inputs for location work.

## Subphase outcomes, what the user can inspect at each boundary

| Subphase | User-facing outcome |
| --- | --- |
| 1.5 / 00 | The verifier and the baseline binding. Nothing to read about strategies yet. |
| 1.5 / 01 | Native full-account-day market view with byte-identical baseline parity on the stratified sample; outcome and benchmark machinery; throughput measurement; the fit-period baseline diagnostics. |
| 1.5 / 02 | The source-reconstruction ledger, the printed-figure replay result, versioned source-exact amendments. The B0-only Strategy Book edition. |
| 1.5 / 03 | The primitive library with literal fixtures and the registered candidate bank. |
| 1.5 / 04 | Every family adapter run on full history: first candidate populations and coverage per branch. |
| 1.5 / 05 | Breadth and refinement trial ledgers with every disposition. |
| 1.5 / 06 | The exit study. |
| 1.5 / 07 | Strategy Book version 1 and the release. |
| 2 / 00–08 | Expert scorecards as each is fitted; Strategy Book version 2 at release. |

## Result card, every task (added 2026-09-16)

Receipts prove that software ran and that checks passed; the result card says whether the task reached what it was for, in a shape a person can judge in a minute. Every task writes `RESULT_CARD.json` (schema `research-result-card-v1`) beside its receipt and repeats it as the last section of `REPORT.md`:

- `question`: the one question the task answers, in plain words.
- `headline`: at most five numbers, each with its unit, its interval or support count, and the pointer to the artifact it was read from.
- `target`: the gate or target the task was held to, from the contract, and `met`: yes, no, partial or not_applicable.
- `verdict`: one of `done_well`, `needs_upgrade`, `not_reaching_target`, `not_applicable`, with one sentence of reason.
- `lever`: if the verdict is not `done_well`, the single smallest change that would most plausibly improve the result, and what evidence would show it did.
- `limits`: what the numbers cannot claim.

A subphase receipt lists its tasks' verdicts; a phase release rolls them into the wiki results ledger. A task whose result is honestly `not_reaching_target` still closes with a verified receipt; the ledger is where the program decides what to upgrade next, in small parts.
