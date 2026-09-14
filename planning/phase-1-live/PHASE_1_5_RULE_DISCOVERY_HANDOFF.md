# Phase 1.5 — discover and validate stronger rule variants

This earlier high-level handoff is superseded for execution by the [Phase 1.5 implementation pack](/workspace/planning/phase-1-5/README.md) and its [copyable prompts](/workspace/planning/phase-1-5/PROMPTS.md). Phase 1's acquired historical measurement is complete. The new pack binds that accepted evidence, defines finite tasks and preserves the requirement that all Phase 1.5 work closes before Phase 2. The text below is retained scope background; use the new pack for exact formulas, budgets, gates and commands.

## Objective and phase boundary

Phase 1 defines, implements and measures the baseline setups. Phase 1.5 searches for better versions of those individual setups: alternative constructions, timing, confirmations and causal sequences. Phase 2 is the additional context layer that chooses among setups. Do not start that cross-setup selector here.

The user's examples—different Jumbo range hours, a reversal window other than 09:40–09:50, a volume-defined balance inside a formation period, or a condition-based reversal inside a broader window—illustrate the breadth of the request. They are not a fixed candidate list. Explore meaningful structural alternatives across the implemented methods, not just small numerical tweaks to Jumbo. Seek robust improvement, not a promise that some variant must win.

Work in `/workspace` and follow AGENTS.md. Preserve existing raw data, immutable sources, baseline definitions and accepted runs. New rules are research variants, not newly discovered author statements. Use separate versioned code/configuration, derived artifacts and reports. No paid acquisition, live trading or Phase 2 selection model. Preserve concurrent and unrelated working-tree changes.

## Entry gate

Read the latest PHASE.md, current method wiki, strategy source conformance and the final Phase 1 historical-measurement report/manifests. Verify that the declared full historical scope—not merely the seven-date engineering sample—has completed its jobs and reconciled its counts, coverage and outcomes. An idle task or a successful test suite alone does not prove this gate.

Finish outstanding Phase 1 measurement first if necessary. Record the exact baseline code, data, setup definitions, outcome definitions and report identities against which variants will be compared. Reuse its native data path, measured populations and efficient feature/cache infrastructure.

## Design a finite, creative search

Create one executable variant registry with stable IDs, parent baseline, rationale, parameters, required inputs, causal availability, search family, trial budget and evaluation policy. Use the existing wiki definitions and Phase 1 observations to identify plausible mechanisms, while recording that this evidence has already been inspected. Do not silently tune candidates after looking at validation outcomes.

Consider these families, selecting those relevant to each method:

1. **Formation geometry:** alternative fixed-clock windows; exchange/session/event anchors; variable-duration formation ending after a predefined volume, volatility or balance condition; nested ranges with explicitly separate parents. Test whether a meaningful formation matters more than the original clock.
2. **Auction/volume-defined boundaries:** contiguous volume value areas, a highest-volume-density price interval, identified balance nodes and low-volume boundaries, robust price quantiles, or a balance that stabilizes before the action window. Compare these with the full observed price high/low. Define price rows, volume fraction, contiguity, tie rules, minimum support and formation completion explicitly. “High/low of volume” is not a sufficient mathematical definition.
3. **Timing and event sequence:** shifted/wider/narrower action windows; first qualifying sweep or rejection inside a broad window; delayed entry until a causal flow/acceptance condition; event-count or volume-clock confirmation; expiry based on an elapsed-time cap plus a predeclared condition. Test the condition's contribution separately from simply allowing more time.
4. **Acceptance, rejection and confirmation:** excursion depth and return speed, dwell or traded volume beyond a boundary, participation without price progress, price reward after absorption, renewed same-band defense, imbalance/POC changes, failed-break/retest sequences and alternative confirmation-bar constructions.
5. **Scale and reference choice:** tick-, volatility- or range-normalized distances; appropriate prior-session, developing or composite auction references; fixed versus causally updating bands; first versus subsequent independently rearmed attempts. Keep reference identities and lifecycle rules explicit.
6. **Execution/measurement refinements:** entry after confirmation versus a defined retracement, structural invalidation, expiry and source-compatible objective alternatives. Keep these separate from signal changes so an apparent improvement can be attributed to the correct change. Model fills only with explicit defensible assumptions; a touch does not establish a queue fill.

Add other defensible ideas when the source structure or baseline evidence suggests them. Each must have a reason stronger than “this parameter might backtest better.” Preserve recognizable setup logic and explain when a structural departure is a new experimental variant rather than a minor refinement.

Start with isolated changes and ablations. Test combinations only after component evidence justifies them, within a predeclared additional budget. Prefer a coarse, bounded search followed by training-only refinement over a huge Cartesian grid. Choose and record a finite compute/trial budget before running; batch shared features and use resumable jobs. Do not stop at writing the registry: execute the search and validation.

## Causality and native evidence

Build each candidate only from information available at its trigger. A volume-defined range must be frozen at formation completion, or versioned prospectively as it develops. Do not select the best balance, peak, final session range, turning point or reversal time using later prices. A stopping condition becomes available only when observed; action cannot begin earlier.

Use canonical owned MBP-1 executions and the established event-time conventions. Quote updates are not traded volume. Preserve genuine duplicate events, contract identities, timestamp ties, calendar rules and unknown coverage. Only independently justified order-invariant calculations may resolve ambiguous batches. Every dynamic reference and feature needs an as-of clock and source lineage.

Keep source-required context inside the setup. Testing a specific within-setup confirmation or prerequisite is allowed; training a model that allocates across different setups/regimes belongs to Phase 2.

## Compare fairly and resist overfitting

Before new trial outcomes, freeze chronological development/validation partitions and a rolling out-of-sample evaluation procedure. Fit thresholds, distributions, profile-selection models and normalization using the permitted past only. Separate overlapping formation/outcome windows at split boundaries. Record all previous Phase 1 and source-case exposure; do not call previously inspected dates an untouched holdout. Reserve genuinely uninspected or future observations where available, and state the remaining validation limits honestly.

Define “better” before searching. Use the Phase 1 outcome framework as the common baseline: objective-before-invalidation behavior, favorable/adverse excursion, time to resolution, frequency and coverage. If comparable simulated returns are available, include costs and execution sensitivity. Do not rank solely by win fraction or by favorable excursion while ignoring wider stops, more distant objectives, reduced opportunity count or longer holding time. Report both price distances and normalized outcomes where appropriate.

Account for all attempted variants and search families, including failures and abandoned trials. Use date/session-blocked comparisons and uncertainty estimates appropriate to dependent observations; control the selection bias from trying many alternatives. Compare baseline and variant on common covered dates, while also reporting each one's complete opportunity population. Do not filter the baseline to dates where the variant looks good or discard failed confirmations.

Require adequate support, stability across chronological folds/years, reasonable sensitivity to nearby parameters, and no domination by one exceptional period. Examine broad stable parameter regions rather than isolated optimum cells. Stress execution costs and sampling/coverage choices when relevant. A different rule that produces no setups in a period is not missing data. Insufficient evidence is a valid conclusion.

After choosing finalists using the development procedure, freeze them and perform the declared final validation once. Any subsequent change is a new recorded experiment; the evaluated validation slice does not become fresh again. Retain the baseline when improvement is not demonstrated.

## Deliverables and completion

Produce one current Phase 1.5 report with:

- A reproducible trial registry and results ledger for every attempted variant.
- Baseline-versus-variant comparisons, support, coverage, chronological validation, uncertainty, ablations and parameter sensitivity.
- A concise per-method shortlist: retain baseline, promising but unconfirmed, or supported improvement under the stated validation conditions.
- Exact rule definitions and configurations for finalists, with causal clocks and provenance.
- Deterministic representative charts showing what changed, including failures and counterexamples—not only successful trades.
- Tests for new features/scanners, native integration and future-perturbation checks, and exact commands to reproduce/resume the experiments.
- Separate evidence for simulation assumptions, prior exposure and any input limitation.

Update the existing current status and method pages with links to the experiment evidence; keep source definitions and historical results intact. Print both required family tables after family reports:

`family | variant | n | faithful_disagreements | status | report path`

`family | id | verdict | fixture | leakage | proxy-as-faithful | notes`

Complete the finite search, validation and reporting. Do not declare a “better rule” because it won in-sample, report only the winners, or require an improvement to exist. The useful outcome is a defensible set of improvements or a clear finding that the baseline should be retained. Stop before Phase 2 context-based setup selection.
