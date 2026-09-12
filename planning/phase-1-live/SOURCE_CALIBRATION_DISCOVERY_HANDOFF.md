# Source calibration, candidate rules and historical replay

Prepared 2026-09-12 for one new task in the existing `/workspace` environment. Recommended lead: GPT-6 Astra, High effort. This file is an execution brief; the empirical work has not been started by preparing it.

## Objective and authorization

Complete the empirical extension of the accepted Phase 1 method pack: source calibration → explicit frozen candidate rules → executable selectors → historical discovery and causal replay → reviewed results. Work autonomously through all stages, advancing when their checks pass. A plan, specification, scanner stub or pilot alone does not finish this objective.

This authorizes the necessary local planning, implementation, tests, fixes, derived artifacts and reports. Make routine implementation decisions without waiting for me. Record consequential research assumptions explicitly. When one branch lacks indispensable evidence, document the exact limitation and continue every independent branch. Never invent evidence to clear a gate.

Scope is the existing M01–M12 method pack and its actual branches, including its distinct process, state, risk, management and re-entry observation units. This is a limited extension beyond the completed implementation gate. It does not activate the separate 85-model project in `/workspace/planning/phase-1-live/RESEARCH_BUILD_SPEC.md` or its `research-spec/IMPLEMENTATION_HANDOFF.md`. Parameter grids, alternative-price-basis/timeframe optimization, classifier training, macro expansion, portfolio simulation and live execution remain deferred.

## Starting point

Read `/workspace/AGENTS.md`, inspect current Git status and preserve existing changes. Git operations stay in `/workspace`; use a new `codex/phase1-calibration-discovery-v1` branch, or a unique suffix if occupied. Preserve raw `/workspace/data` as read-only, ignored and uncommitted. Do not edit `/workspace/sources`, `/workspace/archive`, `/workspace/planning/phase-1-from-scratch` or `/workspace/planning/phase-1-fable`. Do not follow archived worker instructions.

Read these current artifacts before deciding what needs new work:

- `/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md`
- `/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md`
- `/workspace/implementation/reports/phase1-live/methods/COMPLETION_MATRIX.md`
- `/workspace/implementation/reports/phase1-live/methods/CHART_VERIFICATION.md`
- `/workspace/implementation/reports/phase1-live/methods/IMPLEMENTATION_PLAN.md`
- `/workspace/implementation/src/trading_research/research/method_pack/README.md`
- `/workspace/implementation/src/trading_research/research/method_pack/catalog.py`
- `/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json`
- `/workspace/planning/phase-1-live/FORMULAS.md` and the relevant live method/object wiki pages.

The checked baseline was commit `c6052fe`, with 166 objects, 9 shared contracts, 12 methods, 373 operands, 17 source configurations and 22 source-case records. Its recorded suite passed 639 tests and 2 subtests; the six preserved independent cases and final acceptance were rechecked successfully. Historical discovery was still unavailable: `n=null`, `search_completed=false`. Verify the actual current state; retain subsequent legitimate work instead of resetting to this commit. Reuse accepted producers and evidence rather than rebuilding them. Read older full audits only to resolve a concrete dependency or conflict.

## 1. Source calibration

Build a calibration matrix for every retained source case and relevant branch. Reuse completed chart reviews, adding native replay and visual inspection where a selector decision or unresolved discrepancy needs it. Link the original page/image, configuration, instrument/contract, date/time confidence, actual decision interval, reconstructed observations, and match/conflict/unknown result. Preserve all loss, early-attempt and non-entry examples.

Keep facts, interpretations, research assumptions and missing evidence separate. Calibration here means checking and resolving source interpretation, not optimizing parameters to fit screenshots. Use each figure's supported settings. In particular preserve Green Bird's November 20 sweep entry and later MSS annotations, its separate VWAP continuation route, MNQ/NQ identity, source-specific timeframes, distinct dated Jumbo/Sires profiles and same-candle footprint/POC snapshots. An interval-valued source entry is not an exact observed fill. Unpublished source calculations remain unresolved unless a separately named observable research definition is justified.

Gate: every retained case has a disposition and each proposed selector rule has traceable evidence or an explicit research-assumption ID. Source-case agreement is reported independently of historical results.

## 2. Freeze candidate rules and evaluation scope

Account for every branch in the current catalog. Write both readable rules and a validated machine-readable registry containing version, evidence mode, source/assumption references, observation unit, instrument/session, initial opportunity trigger, prerequisites, selected branch, availability clocks, lifecycle, invalidation, expiry, re-entry, deduplication, exclusions, required data and unknown handling.

Define the opportunity population before measuring later sequence outcomes. Preserve opportunities, selected signals, attempts, orders and actual fills as different populations. A selection condition cannot silently exclude the very failures whose frequency is being measured. Specify what each denominator measures.

Use literal source definitions where complete. Where a rule is necessary and source evidence is incomplete, a conservative deterministic research default is authorized only as a separately named comparison variant with justification and a frozen assumption record. It does not become source-faithful through calibration. Do not train missing state labels, manufacture private order selections, or turn process/risk examples into entry strategies. If no defensible observable definition exists within this scope, give that branch a precise unavailable or non-entry disposition and continue.

Missing implementation is work to complete, not a source/data limitation. Do not leave a buildable branch unavailable merely because its selector requires substantial work; evidence gaps must identify the specific absent observation or unresolved definition and why the authorized scope cannot resolve it.

Inventory actual acquired coverage. Freeze calibration dates, previously inspected dates, evaluation dates, instruments, versions, input identities, lookbacks, outcome horizons and population rules before examining evaluation outcomes. Exclude source/calibration dates from the evaluation cohort and identify any prior audit exposure; call a sample untouched only if that is supported. Choose evaluation partitions using coverage and chronological rules, never outcomes. Distinguish the present research freeze from historical event availability; this is retrospective measurement, not a claim that these rules were specified years ago.

Gate: the registry and split/run manifests validate, all branches have dispositions, defaults are fixed and no unresolved choice can be supplied from future observations. Revisions after viewing evaluation results require a new version and an explicit record of evaluation exposure.

## 3. Implement and verify selectors

Implement selectors through the existing verified native adapters, object producers, semantic bindings and method evaluator. Add a clear CLI for the new stages using existing runner conventions; document commands that actually exist. Keep source-faithful and research-comparison modes explicit throughout candidate manifests, artifacts and reports. Preserve published formula semantics and the baseline evidence; put new assumptions in the versioned registry.

Build candidates from observable market prefixes, not manually supplied winning dates, source-image annotations, synthetic fixtures or post-outcome labels. Check instrument and parent identity, occurrence/availability/use clocks, native precision, session/roll handling, branch-specific applicability and missing coverage. Preserve the repaired order/position/event links and state-label requirements.

Verify at least one supported branch from native input through selector, assembled candidate, evaluator and report before scaling. Then implement every remaining supported branch; the first branch is a pipeline check, not the final scope. Add meaningful positive, negative, missing-data, mirrored-where-applicable, ordering, duplicate/opportunity-accounting and future-perturbation checks. Earlier candidate IDs, decisions and incorporated fields must remain invariant when later events are appended or altered.

Gate: source calibration and adversarial controls pass or retain precise limitations; full typed output validation passes; counts reconcile; no future evidence or proxy-as-faithful admission is detected. Repair discovered implementation defects and retain their regressions before advancing affected branches.

## 4. Historical discovery and causal replay

Execute the frozen manifest for every supported branch across all its declared eligible partitions. Begin with small operational checks, then process the full manifest in bounded instrument/date batches. Reuse derived objects by content/configuration hash, checkpoint completed partitions and resume without duplicates. Keep large derived artifacts outside raw data, under the established ignored derived-output conventions; retain small summaries and hashes for review. Do not load a multi-year event archive into memory at once.

Replay the observed sequence with its original availability limits. Record censored or ambiguous outcomes explicitly. Historical opportunity detection alone cannot establish an actual discretionary selection, order or fill. Do not introduce new execution assumptions to produce a profitability claim.

Report, per method/branch/variant and year, eligible/scanned/missing scope, opportunities, candidate counts, pass/fail/unknown and censored results, denominators, faithful disagreements where decidable, timing violations and proxy-as-faithful counts. Under the existing contract preserve `n=p+f`, `N=p+f+u` and `[p/N,(p+u)/N]`, with null rates for empty denominators. Do not pool incompatible instruments, source versions, observation units or evidence modes.

Zero candidates is valid only after the declared search actually completes. An unavailable selector, missing data or unfinished scan must retain the appropriate unavailable/partial state; it cannot be encoded as a completed zero. Review deterministic examples across outcomes and years using charts generated from the same records that produced the metrics. Source calibration examples remain outside historical candidate counts.

## 5. Review and completion

Use native subagents when available for independently bounded work with disjoint file ownership. Follow the established preferences: Luna Max for routine bounded implementation/report work, Sol High for sensitive selector/causality work and review, and Astra Low for a tightly scoped difficult independent review when useful. The Astra High lead owns integration, research decisions and acceptance. Respect actual concurrency limits and keep expensive data jobs bounded. If subagent allocation is unavailable, continue locally instead of waiting indefinitely or claiming a review happened.

Request an independent source/causality/counting review when a separate reviewer is available. Correct actionable findings and rerun affected evidence. Run the current full test suite after integration and the relevant original/post-implementation regressions. Keep tested-code and report identities current; preserve earlier acceptance as baseline history and create a separately scoped empirical acceptance record. Do not edit a status or hash to substitute for rerunning or reviewing changed behavior.

Save a short progress/decision log under `/workspace/planning/phase-1-live/`, and reviewable empirical reports under `/workspace/implementation/reports/phase1-live/empirical/`. Save the registry, calibration matrix, frozen split/run manifests, partition checkpoints, commands, implementation/configuration hashes, tests, representative charts and final limitations. Record exact resume commands whenever work remains. Preserve all completed work across context changes.

After family reports, print both required tables:

`family | variant | n | faithful_disagreements | status | report path`

`family | id | verdict | fixture | leakage | proxy-as-faithful | notes`

Finish when every branch is accounted for, every supported frozen evaluation partition has been scanned and replayed, reviews/checks have passed, and a final report separates implementation correctness, calibration agreement, historical measurements and remaining source/data limits. Report partial work honestly if an external blocker prevents that state; do not label an unfinished pipeline complete. Continue useful independent work while a branch is blocked. Keep all stages within this task and advance automatically after each gate. Leave changes reviewable on the task branch without pushing or merging.
