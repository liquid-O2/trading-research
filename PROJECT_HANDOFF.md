# Project handoff — adaptive NQ trading research

Snapshot: **2026-09-15**. Repository: `/workspace`, `liquid-O2/trading-research`.

This file is the starting context for a new session with no knowledge of the previous conversation. It records the objective, accepted decisions, work completed, implementation state, known defects and where to continue. Detailed formulas and task requirements remain in the linked canonical specifications. This handoff is a dated snapshot, not a replacement for those contracts or a claim that later work has been verified.

## 1. Start here

- **The goal:** build an adaptive NQ decision process with independently testable context, location, response, entry and risk/management components. Source methods provide baselines and mechanisms. There is no agreed fixed number of models.
- **Phase 1 is complete** for the acquired observed-input population. Its census contains 18,747 observed setups. These are opportunities and subsequent price observations, not independent executed trades or proven profits.
- **Phase 1.5 and Phase 2 are fully specified:** 46 task cards in 17 subphases. Most of that implementation does not exist yet.
- **Phase 1.5 `00-foundation`, `01-native-and-outcomes`, `02-source-reconstruction`, `03-primitives` and `04-family-adapters` are closed** under assurance `research-assurance-2026-09-14-v3`. Foundation identities are P15-00 `ea9693217cb577cb`, P15-01 `a4c95ab43aef1038`, subphase `72c6541ece1cfab0` and matching GATE_REVIEW. Native/outcomes identities are P15-02 `c9669fa98ba72c43`, P15-03 `b957ec04d76e9c71`, subphase `207db9ec1a196b8c` and matching GATE_REVIEW. Source-reconstruction identities are P15-04 `0d0a57cc4de997b4`, subphase `c8a2842644f906d6` and matching GATE_REVIEW. Primitive identities are P15-05 `8e1ea422bfc8678d`, P15-06 `50d64d506299dc8d` attempt-0002, P15-07 `ac09070f5aeb604b`, P15-08 `9728f9ee0bbbdfd5`, subphase `c1511ed5a468005d` and matching GATE_REVIEW. Family-adapter identities are P15-09 `72323a6d8f65b77d`, P15-10 `a856814fe11b24ac`, P15-11 `a3f84244bc9239c3`, P15-12 `2488a221f5843c26`, P15-13 `79e50a6a3faf8be2`, P15-14 `31841425087b5507`, P15-15 `f7df59d81e058166`, P15-16 `316dc53caf8bdfac`, subphase `924c9a35552250ab` and matching GATE_REVIEW. The first 04 close `9f9109f9b6350a8d` … `b7ed375d0b2721ee` is preserved and is not this gate. The first 03 close `40442820ef920707` / `f8d351d8b47b4583` / `7aa938605dc472a6` / `4d3a6dd40b39d3b2` / `1d3586803dd9688b` is preserved and is not this gate. Earlier closed attempts `3df87f26477a4205` / `89ba731db83660ab` / `1d17f7f63296a745`, `c9756fc1e534b240` / `babe7a991b6b3dc1` / `50587897e824ede8`, `cac8165617b72e9f` / `6986d93967e3eaea` / `ceb48321823736a3`, `40ffb49bc037e3cc` / `ee71900e26791e89` / `6824d15fbda635ce` and `ebb1b8270700be4d` / `53e8f17617f39a87` / `95522aebaedfa3ed` are preserved. The [2026-09-14 v2 review](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/REVIEW.md) rejected attempt `240838146c38c484`; that attempt is preserved and is not that gate.
- **Do not start `05-finite-search` until a later user-dispatched coordinator prompt.** All of Phase 1.5 must subsequently finish before Phase 2 implementation. Phase 3 and Phase 4 have agreed scope but no detailed implementation packs yet.
- **Immediate engineering work:** execute `05-finite-search` from the closed 04 receipts in section 8 (`72323a6d8f65b77d` / `a856814fe11b24ac` / `a3f84244bc9239c3` / `2488a221f5843c26` / `79e50a6a3faf8be2` / `31841425087b5507` / `f7df59d81e058166` / `316dc53caf8bdfac` / `924c9a35552250ab`), which themselves require the closed 03 receipts (`8e1ea422bfc8678d` / `50d64d506299dc8d` attempt-0002 / `ac09070f5aeb604b` / `9728f9ee0bbbdfd5` / `c1511ed5a468005d`). Known baseline discrepancies: [phase1-code-review-2026-09-14](/workspace/planning/research-program/reviews/phase1-code-review-2026-09-14/). This 04 run did not start 05.
- **User constraint:** usage available for this assistant is limited. The user has been using Grok for implementation and wants bounded, self-contained handoffs, practical progress and honest verification. Do not restart a planning interview or expand the specifications by default.

The wiki now records the closed v3 identities. The root README and some planning reports may still retain documentation-only wording; task cards and TASK_GRAPH retain `planned` authoring status. Use dated execution evidence to determine actual progress. Neither a stale README sentence nor a `planned` card header establishes runtime status.

The rejected v2 identities remain those in the review's [INPUT_IDENTITIES.json](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/INPUT_IDENTITIES.json). Current admission uses the receipts named in section 8.

## 2. The project objective and settled decisions

The intended system should recognize market context, locate useful areas, understand the response there, decide whether and when to trade NQ, and manage account-level risk. Each responsibility needs independent diagnostics before the components are combined. We are researching whether this can work; no completed component currently certifies the eventual economic objective.

The user has already settled the following. Do not ask these questions again unless a new request changes the scope.

| Topic | Agreed decision |
| --- | --- |
| Execution | NQ is the execution asset. The fixed research benchmark uses one NQ mini; it does not invent fractional partial contracts. |
| Study period | Study 2020 onward on owned data. Earlier observations may supply causal lookbacks. The currently accepted acquired census ends at the September 2026 endpoint described below. |
| Sessions | Include all verified matching sessions within an account day, not only RTH. Source branches keep their particular clocks. No position crosses the account-day boundary. |
| Economics | Jointly optimize profit and downside. The user's ambition is $3,000 per trading day; less than $1,000/day is unacceptable for the eventual system. The daily loss limit is $1,000 measured from day-start. Report every eligible day, including zero-trade days; an average cannot stand in for the daily requirement. These are objectives and evaluation constraints, not established achievable returns. |
| Source fidelity | Preserve source facts, disclosed inferred reconstructions and our research alternatives as distinct identities. Proprietary constants that were not supplied remain unknown. The user is not expected to decode them. |
| Search | Start with a small representative bank across different mechanisms, then refine evidence-supported mechanisms within a finite budget. Opportunity frequency, missed moves, confirmation delay and remaining reward matter alongside quality. No family must produce a winner. |
| Cross-market reasoning | A location on asset A and a response on asset B may justify an NQ trade without an NQ local touch for a separately named custom candidate. Source-linked NQ methods still require their original NQ stages. |
| Other assets | Do not clone Jumbo, Green Bird or Sires onto other instruments. Permitted custom areas include gamma, vega, vanna, OI, rolling-volume improvements, VWAP/bands and prior highs/lows. Other assets may also supply context, flow and response. |
| Native scope | Cover owned native NDX/NDXP, SPX/SPXW, QQQ, SPY, NQ, ES and option chains, with availability verified by product and interval. YM/RTY and volatility products are contextual inputs where owned. A futures conversion cannot be labelled native cash-index data. |
| Volatility architecture | GK, YZ, HAR-RV and available IV inputs feed **one jointly fitted volatility expert with multiple heads**. They are not four separate fitted experts. Other major mechanisms and source methods have separately fitted artifacts and diagnostics while sharing calculations. |
| Context scope | Phase 2 includes intraday forward volatility/range forecasts, intraday options/OI/IV updates and method-specific context/day/setup classification and conditional plans. It is substantially more than a global regime label. |
| Data spending | Use owned data only. Missing inputs get explicit scope/availability dispositions. No paid acquisition proposals or external account actions are part of the plan. |
| Gates | Complete all Phase 1.5 work before implementing Phase 2. Stop each dispatched run at its subphase boundary. |

The accepted answer ledger is [NEXT_PHASES_DISCUSSION.md](/workspace/planning/phase-1-live/NEXT_PHASES_DISCUSSION.md). The [scope audit](/workspace/planning/research-program/SCOPE_AUDIT.md) maps the original conversation requirements to tasks and reserved later phases. Old conversation exports contain superseded assistant proposals, model counts and economic targets; those are not current instructions.

## 3. What we did in the previous work

1. **Established the Phase 1 baseline.** Existing source-object and method implementations were reconstructed, audited and measured by the Phase 1 work. We checked its completed evidence and used that accepted baseline for the next-phase plan; this planning/review work did not rerun the full census.
2. **Reconciled the user's goals.** We reviewed the active project, source-linked wiki, relevant code and earlier conversation material, then resolved a 16-area questionnaire. The attached early phase map was treated as examples, not an exhaustive task list. The answer ledger and scope audit preserve the resulting decisions.
3. **Reviewed workflow methods.** The requested Matt Pocock and pstack material informed bounded task cards, progressive reading, code-grounded work, sensitive tests, one writer per checkout and separate review. The [method review](/workspace/planning/research-program/METHOD_REVIEW.md) and [pinned inventory](/workspace/planning/research-program/METHOD_REVIEW_INVENTORY.tsv) record what was inspected. This was not permission to import old Cursor/mill execution instructions.
4. **Created the shared wiki.** The former phase-local wiki was moved to `/workspace/wiki`, preserving source definitions and old links through the `planning/phase-1-live/wiki` symlink. Generated historical report sediment was replaced with links to immutable evidence. The [migration audit](/workspace/planning/research-program/WIKI_MIGRATION_AUDIT.json) records the 191 original pages and preservation checks. Active definitions now live in the shared wiki rather than duplicated phase wikis.
5. **Wrote the full Phase 1.5 and Phase 2 packs.** These include formulas, units, proposed APIs/types, finite candidate/model recipes, chronological evaluation, task ownership/dependencies, output requirements, worked vectors and generated prompts/runbooks. Documentation generation and structural checks were added under `/workspace/tools`. Authoring a proposed command or class did not implement it.
6. **Adapted prompts to the user's Grok build.** The user already has pstack available there. Prompts use `/poteto-mode new task`, the installed router and parent-Grok inheritance for every role. The user sends **one coordinator prompt per subphase**. The generated total of 72 blocks includes 46 worker prompts, 17 coordinator prompts, eight support templates and one repair prompt; it does not mean 72 user-dispatched jobs.
7. **Reviewed the first foundation implementation.** Grok's first completion had 25 passing tests, but the fixed independent 27-case checker exposed 18 invalid acceptances. We preserved those artifacts, wrote reproducible checks and explicitly amended acceptance to `research-assurance-2026-09-14-v2` across all 46 tasks and all 17 subphases. The amendment strengthened verification, not research formulas, budgets or goals.
8. **Reviewed the repaired v2 foundation.** Grok produced new receipts, 45 passing targeted tests and 27/27 passing fixed checks. We independently reproduced those successes. Additional review found ten more invalid acceptances in the review, matrix, identity, artifact-schema and lineage validators. The current stopping point is this unresolved review, detailed below.
9. **Kept the next action bounded.** The user expressed frustration with repeated bad implementation and limited remaining assistant usage. The last recommendation was one focused repair against existing reproductions, followed by a stop if it cannot pass; another broad rewrite or planning expansion was not recommended. No further implementation was performed while creating this handoff.

See [PLANNING_REPORT.md](/workspace/planning/research-program/PLANNING_REPORT.md) for the original documentation deliverables, [AMENDMENTS.json](/workspace/planning/research-program/AMENDMENTS.json) for the assurance change and the two review packs for the actual implementation history. Their dated claims must be read in that order.

## 4. Phase 1 — completed baseline and its limits

The accepted [measurement report](/workspace/implementation/reports/phase1-live/historical-measurement/MEASUREMENT_REPORT.md) covers:

- **1,742 declared session dates**, 2020-01-01 through 2026-09-03.
- **99,294 daily jobs**, plus three collection-process jobs.
- **18,747 observed qualifying setups** across 50 branches and eight additional units.
- **591,714,592 native execution references** reconciled from session receipts to branch jobs; shared consumption by several branches is not double-counted in that native total.
- 58 units partitioned into 37 entry setups, 10 context/research units, seven personal-execution exclusions and four supplemental observations.

The native acquired endpoint is **2026-09-03T06:09:59.901114+00:00, exclusive**. September 3 is partial. Required current/prior inputs and matching calendars differ by branch. Unknown intervals, same-contract lookback gaps, ambiguous order, missing context and out-of-scope personal records remain explicit. Exchange-feed completeness is not established by `complete_observed_scope`.

The 12 method identifiers are `JJ-TBR`, `GB-FAIL`, `GB-VWAP`, `GB-SCALP`, `SIRES`, `SAINT-AMT`, `MEMBER-TWO-REASONS`, `KEANI-OPEN-ABOVE-VALUE`, `REFILL-STUDY`, `JETBUNDLE-STATES`, `STOIC-DATA` and `STOIC-RISK`. Research/process/risk observations must not be turned into invented market entries.

The accepted run is under [historical-measurement/run-1.0.1](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1). Its [registry](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/registry/registry.json), protocol directory, composed calendar, dependency/recovery runs and validation artifacts bind the baseline. Use the report's actual paths, not a guessed newest folder or current wiki hash.

[PHASE.md](/workspace/planning/phase-1-live/PHASE.md) contains completion and family/audit tables. [STRATEGY_SOURCE_CONFORMANCE.md](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) explains which operational P-zone, gamma, auction and macro definitions are disclosed reconstructions rather than recovered author formulas. The accepted report records its own larger test, native-input, restart and chart verification; these are historical receipts, not checks rerun for this handoff.

Do not reinterpret overlapping setups as independent portfolio trades, subsequent observed prices as fills, or this exposed research history as an untouched holdout. Preserve the accepted baseline even when building a separately versioned improvement.

## 5. What each remaining phase entails

| Phase | Responsibility | Completion boundary and current state |
| --- | --- | --- |
| 1.5 | Reconstruct remaining numerical definitions; improve and compare individual formations, references, CVD, sequences, confirmations and setup rules; compare exits with entries fixed. | All tasks/families/candidates have verified dispositions, baseline and selected rules are frozen, and the release includes limitations and causal selection records. Fully specified; foundation exists but remains blocked; later subphases unimplemented. |
| 2 | Fit context and intraday forecast experts, native options and OI updates, source-method suitability and conditional plans. | Reproducible chronological predictions, uncertainty, ablations, model/input lineage, adaptation comparisons and a complete context release. Fully specified; unimplemented and gated on all of 1.5. |
| 3 | Fit actionable location experts: P-zone improvements, forecast-volatility-derived areas, native options/volume/VWAP/prior-extreme areas, arrival, conditional reaction and competition between areas. | Detailed pack must be written from actual Phase 2 outputs. Reserved scope only; no execution or fixed model count. |
| 4 | Fit response/entry experts and integrate context, location and response into NQ decisions, combined historical replay, account-level risk and daily economics. | Validate the combined decision process and every eligible day's economic distribution. Prospective evidence remains separate. Reserved scope only. |
| Later management work | Learned exits, thesis changes, management and re-entry after fixed-entry controls. | A recommendation, not a user-approved numbered Phase 5. Position-size changes or partial-contract assumptions are not silently authorized. |

### Phase 1.5 — 21 tasks, eight subphases

Canonical [specification](/workspace/planning/phase-1-5/SPEC.md), [finite search contract](/workspace/planning/phase-1-5/SEARCH_CONTRACT.md), [phase README](/workspace/planning/phase-1-5/README.md) and [coordinator prompts](/workspace/planning/phase-1-5/PROMPTS.md).

| Order / runbook | Tasks | What the work produces |
| --- | --- | --- |
| [00-foundation](/workspace/planning/phase-1-5/subphases/00-foundation/RUNBOOK.md) | P15-00, P15-01 | Baseline/input binding, typed causal records and identities; task/subphase/phase/lineage verification. **Closed on v3 receipts `72c6541ece1cfab0`.** |
| [01-native-and-outcomes](/workspace/planning/phase-1-5/subphases/01-native-and-outcomes/RUNBOOK.md) | P15-02, P15-03 | Native MarketView and baseline parity/restart slice; ordered outcomes, coverage-aware labels, costed replay and chronological comparisons. **Closed on v3 receipts `207db9ec1a196b8c`.** |
| [02-source-reconstruction](/workspace/planning/phase-1-5/subphases/02-source-reconstruction/RUNBOOK.md) | P15-04 | Source-reconstruction ledger, B0.1 operand overrides, printed-figure refill replay, B0 Strategy Book. **Closed on v3 receipts `c8a2842644f906d6`.** |
| [03-primitives](/workspace/planning/phase-1-5/subphases/03-primitives/RUNBOOK.md) | P15-05–08 | 05: causal time/activity/balance formations and profiles. 06: CVD and resolved cohort memory. 07: explicit response state machines. 08: reference, memory and timing recipes plus the finite candidate bank. **Closed on v3 receipts `c1511ed5a468005d`.** |
| [04-family-adapters](/workspace/planning/phase-1-5/subphases/04-family-adapters/RUNBOOK.md) | P15-09–16 | 09: Jumbo. 10: Green Bird failure. 11: Green Bird VWAP/scalps. 12: Sires. 13: Saint. 14: Member. 15: Keani. 16: Refilling/jetbundle/Stoic process and risk observations. Unchanged variants delegate to the baseline; changed variants enumerate their own population. **Closed on v3 receipts `924c9a35552250ab`.** First close `b7ed375d0b2721ee` preserved. |
| [05-finite-search](/workspace/planning/phase-1-5/subphases/05-finite-search/RUNBOOK.md) | P15-17, P15-18 | Reconciled breadth screen, then one bounded refinement and honest per-family dispositions. All attempted, rejected, duplicate, deferred and unsuccessful candidates remain in the ledger. |
| [06-exit-controls](/workspace/planning/phase-1-5/subphases/06-exit-controls/RUNBOOK.md) | P15-19 | E0–E4 exit comparisons with the selected entries, source deadlines and initial risk fixed. This does not select an ex-post best exit for each trade. |
| [07-release](/workspace/planning/phase-1-5/subphases/07-release/RUNBOOK.md) | P15-20 | Complete family/task/candidate reconciliation, selected-rule manifests, release inputs and Phase 2 allowlist; coordinator finalizes the phase release and matching review. |

The breadth cap is 160 nonbaseline applicable branch candidates, plus baselines, using the specified deterministic allocation. Refinement permits at most 24 neighbors and one combination per family/outer fold. These are registered experiment budgets, not desired model counts. The precise recipes and promotion/support rules are already written; do not invent another open-ended search.

Important boundaries: CVD improvements belong here; source EV reconstruction belongs here; learned forward movement belongs to Phase 2; optimizing actionable P-zone/volatility-derived locations belongs to Phase 3. A changed geometry or earlier confirmation must enumerate its own eligible population rather than filter only old successful setups.

### Phase 2 — 25 tasks, nine subphases

Canonical [specification](/workspace/planning/phase-2/SPEC.md), [phase README](/workspace/planning/phase-2/README.md) and [coordinator prompts](/workspace/planning/phase-2/PROMPTS.md). Task numbers are **not** simple execution order: native option adapters precede the joint-volatility fit, while P2-11 requires the volatility outputs. Follow the graph/runbooks.

| Order / runbook | Tasks | What the work produces |
| --- | --- | --- |
| [00-entry-gate](/workspace/planning/phase-2/subphases/00-entry-gate/RUNBOOK.md) | P2-00 | Verified complete Phase 1.5 release; exact native-root and input availability scope. |
| [01-datasets-and-fitting](/workspace/planning/phase-2/subphases/01-datasets-and-fitting/RUNBOOK.md) | P2-01, P2-02 | Causal snapshots, targets and dataset joins; deterministic preprocessing/fitting/calibration and chronological upstream predictions. |
| [02-native-options-baseline](/workspace/planning/phase-2/subphases/02-native-options-baseline/RUNBOOK.md) | P2-09, P2-10 | Native option/spot/OI adapters, contract definitions, pricing/IV/Greeks and exposure boards across roots and expiries. |
| [03-joint-volatility](/workspace/planning/phase-2/subphases/03-joint-volatility/RUNBOOK.md) | P2-03, P2-04 | Volatility arithmetic and multi-horizon targets; one jointly fitted expert combining GK/YZ/HAR/IV, with baseline comparisons and group ablations. |
| [04-context-mechanisms](/workspace/planning/phase-2/subphases/04-context-mechanisms/RUNBOOK.md) | P2-05, 06, 07, 11, 08 | Directional remaining range/topology/passage time; auction/day/session quality; aggression reward/defense/failed pushes; options flow/exposure changes/repricing; native cross-market/spot-IV coupling. |
| [05-intraday-oi](/workspace/planning/phase-2/subphases/05-intraday-oi/RUNBOOK.md) | P2-12 | Weakly supervised intraday OI-change estimates, uncertainty, baseline comparisons and separate downstream NQ contribution tests. |
| [06-method-experts](/workspace/planning/phase-2/subphases/06-method-experts/RUNBOOK.md) | P2-13–21 | Separately fitted Jumbo, GB failure, GB VWAP, GB scalps, Sires, Saint, Member and Keani experts; process-context artifacts and risk interfaces. |
| [07-plans-and-adaptation](/workspace/planning/phase-2/subphases/07-plans-and-adaptation/RUNBOOK.md) | P2-22, P2-23 | Immutable conditional plans and a fixed context-contribution replay; annual/monthly/weekly/monthly-plus-matured-label-update comparisons. |
| [08-release](/workspace/planning/phase-2/subphases/08-release/RUNBOOK.md) | P2-24 | Full chronological replay, all expert/head/input dispositions, ablations, lineage, release evidence and Phase 3 handoff. |

Use [VOLATILITY.md](/workspace/planning/phase-2/VOLATILITY.md), [CONTEXT.md](/workspace/planning/phase-2/CONTEXT.md), [OPTIONS.md](/workspace/planning/phase-2/OPTIONS.md), [METHOD_EXPERTS.md](/workspace/planning/phase-2/METHOD_EXPERTS.md) and [ADAPTATION.md](/workspace/planning/phase-2/ADAPTATION.md) for exact formulas and model requirements.

Phase 2 method outputs include setup occurrence, conditional utility/path, session/branch/reference/confirmation suitability, timing, target ambition, alternatives, uncertainty, expiry and invalidating evidence. A current descriptive state is not a future forecast; the final day type is not available at the open. A conditional plan is not the final entry integrator.

Options work includes multiple expiry boards, IV/spot/time/OI/flow changes and model uncertainty, not just one maximum-gamma strike. Later-published OI cannot be used earlier. Endpoint OI fitting does not establish true intraday dealer inventory, and expiring 0DTE terminal OI is not a valid intraday-inventory accuracy target. Greek sign/exposure assumptions and American-pricing approximations must stay labelled. New actionable custom price areas remain Phase 3 work.

## 6. Existing code, data and document map

| Location | Purpose / actual state |
| --- | --- |
| [AGENTS.md](/workspace/AGENTS.md) | Workspace rules; read before mutations. |
| [planning/ROADMAP.md](/workspace/planning/ROADMAP.md) | Program responsibilities, scope and phase gates. |
| [wiki/index.md](/workspace/wiki/index.md) | Shared source methods, objects, glossary and evidence links. |
| [planning/phase-1-live/PHASE.md](/workspace/planning/phase-1-live/PHASE.md) | Accepted Phase 1 completion, report links and both family/audit tables. |
| [planning/research-program/TASK_GRAPH.json](/workspace/planning/research-program/TASK_GRAPH.json) | All 46 tasks, dependencies, owners, required reads/artifacts and assigned assurance cases. |
| [planning/research-program/WORKFLOW.md](/workspace/planning/research-program/WORKFLOW.md) | Execution/receipt protocol and subphase boundaries. |
| [planning/research-program/PSTACK_EXECUTION.md](/workspace/planning/research-program/PSTACK_EXECUTION.md) | Grok/pstack routing and role, writer, review and handoff rules. |
| [planning/research-program/ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md) | Current cross-phase evidence, identity, coverage, lineage and review requirements. |
| [planning/research-program/ASSURANCE_CASES.json](/workspace/planning/research-program/ASSURANCE_CASES.json) | 32 silent-failure cases assigned across all tasks; pinned independent checker identity. [Readable casebook](/workspace/planning/research-program/SILENT_FAILURES.md). |
| [implementation/src/trading_research/research/method_pack](/workspace/implementation/src/trading_research/research/method_pack) | Existing accepted Phase 1 scanners, native views, measurement and reconstruction. Reuse without silently changing the baseline. |
| [implementation/src/trading_research/research/contracts](/workspace/implementation/src/trading_research/research/contracts) | Existing foundation `types.py`, `identity.py`, `receipts.py`; current defects are primarily in verification here. |
| [implementation/src/trading_research/research/rule_discovery/baseline_manifest.py](/workspace/implementation/src/trading_research/research/rule_discovery/baseline_manifest.py) | Existing P15-00 baseline and example/engineering-date producer. The remaining rule-discovery modules do not yet exist. |
| [implementation/tests/rule_discovery](/workspace/implementation/tests/rule_discovery) | Only the two foundation task test files and package initializer currently exist here. |
| [implementation/tools/verify_research_release.py](/workspace/implementation/tools/verify_research_release.py) | Existing public verifier CLI; current exit 0 alone is insufficient because of known false acceptance. |
| [implementation/tools/run_phase1_objects.py](/workspace/implementation/tools/run_phase1_objects.py) | Existing Phase 1 object runner; do not launch a census simply to orient a new session. |
| `/workspace/implementation/src/trading_research/research/experts/` | Planned Phase 2 code namespace; absent at this snapshot. |
| `/workspace/data` | Owned raw/derived data, kept on disk and ignored by Git. Never commit it. |

The Python environment used for actual foundation checks is `/workspace/implementation/.venv/bin/python`, with command working directory `/workspace/implementation`. Proposed `run_rule_discovery.py` and `run_context_experts.py` commands in the packs are future deliverables; they are not currently available merely because the documentation names them.

New task receipts live under `implementation/reports/research-work/<task-id>/<semantic-run-id>/attempt-NNNN/`. Coordinator foundation artifacts use the subphase ID in that tree. Later context reports are specified under `implementation/reports/context-experts/`; large caches belong under ignored data paths. Never choose an accepted predecessor by lexicographic directory order. Earlier experimental foundation directories also exist.

The current new planning packs, shared wiki, root tools and foundation source/tests/verifier include important **untracked** files. HEAD alone does not represent all work. Do not reset, clean or discard the working tree as setup. No commit/push/merge was performed by the planning or review work summarized here.

## 7. Invariants that matter when implementing

The following summarizes existing requirements; exact definitions and numerical recipes remain in the linked files.

1. **Causality and availability:** retain event, availability, issue, decision, label-known-at and fit-availability clocks. Enforce every consuming ancestor cutoff. Future outcome edges are explicitly typed and cannot feed predictors. Missing clocks, bool-as-int clocks, nonfinite values and mutable nested state are not harmless omissions.
2. **Native identity and coverage:** keep native asset/contract, actual file hash, resolvable row IDs and exact intervals. Same-timestamp conflicting events remain ambiguous. Unknown aggression is not zero aggression. Coverage is assessed by required input group and lookback, not inferred from a calendar or selected successful outcomes.
3. **All-session accounting:** the operational account day is previous-day 18:00 to labelled-day 17:00 New York time intersected with verified matching hours; source RTH remains its own interval. Use timezone-aware DST handling and actual closures. Flatten before the verified final close. Missing/closed/zero-opportunity/failed/ambiguous are different outcomes.
4. **Preserved baseline:** the existing `HistoricalFeatures` baseline window ends at 16:00 ET; the new MarketView separately extends labels/benchmarks to the matching account-day close. Construct reconstruction semantics from the registry records at initialization. Reuse `native_discovery.scan_branch` and its frozen identity checks; do not toggle reconstruction after construction or monkeypatch old scanners.
5. **New populations and stable lifecycles:** changed formations/references/confirmations generate their own full eligible populations. Developing-reference versions share a lifecycle/contact history rather than manufacturing a new touch population on every update. Preserve source predicates except the explicitly registered change.
6. **Chronological experiments:** use the frozen exposure ledger, purged/embargoed chronological splits, past-only tuning/calibration, causal upstream predictions and all attempted trials. Fit support and evaluation support are explicit. Input masks and joined feature columns must actually reach the fitted predictor, demonstrated by sensitive controls and ablations.
7. **Economic interpretation:** ordered target/stop resolution and executable BBO replay are different from favorable/adverse excursions. The fixed benchmark has explicit latency, adverse ticks, commissions, geometry, day-start risk and gap handling. Preserve actual breaches rather than clipping losses to a limit. Keep zero-trade days. Component acceptance does not certify the user's eventual daily profit goal.
8. **Bounded research:** keep unsupported inputs and inconclusive/negative results when correctly measured. Missing software, failed required tests or absent evidence cannot be called a research limitation. Do not force a winner, an old fixed model count or an arbitrary trade quota.
9. **Evidence-backed closure:** task receipts require actual artifact inventories, hashes and sizes; plan/code copies; semantic draft identities; logged successful commands; and an evidence matrix whose references resolve. Recursively verify exact predecessor IDs/hashes and current assurance requirements. A passing flag is a claim to check.
10. **Final review:** immutable task receipts precede the candidate subphase/phase receipt; the matching review follows it. A review binds candidate, task scope, code, graph/assurance, matrices, checker/results and resolved findings. Final verification logs are sidecars, avoiding self-hashes and circular identities. Known correctness/causality/integrity defects block admission.

Canonical details: [DATA_CONTRACTS.md](/workspace/planning/research-program/DATA_CONTRACTS.md), [TYPE_REFERENCE.py](/workspace/planning/research-program/TYPE_REFERENCE.py), [OUTCOMES.md](/workspace/planning/research-program/OUTCOMES.md), [EVALUATION.md](/workspace/planning/research-program/EVALUATION.md), [MODEL_FITTING.md](/workspace/planning/research-program/MODEL_FITTING.md), [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md) and 13 [reference vectors](/workspace/planning/research-program/fixtures/reference_vectors.json).

Engineering slices are deterministic coverage-based checks per required input group, including year/DST slots and separate partial/roll/gap/ambiguity evidence. They do not replace the complete registered research run or the actual training-history requirements. The fixed independent suite is a minimum, not an exhaustive proof.

## 8. Current stopping point

The current assurance identifier is **`research-assurance-2026-09-14-v3`** and plan version is **`research-plan-2026-09-14-v3`**. `00-foundation`, `01-native-and-outcomes`, `02-source-reconstruction`, `03-primitives` and `04-family-adapters` are closed on the identities in the tables below. Stop here. Do not start `05-finite-search` in this run. The next eligible coordinator prompt is that subphase's runbook.


### B0.1 full-history measurement

Corrected baseline **B0.1-2026-09-14** measured on the full run-1.0.1 evaluation calendar (completed 2026-09-15; committed 687f2bbe, job files gitignored).

| Artifact | Path | Identity |
| --- | --- | --- |
| Run root | [20def36e065c13d7](/workspace/implementation/reports/research-work/baseline-repair/20def36e065c13d7/) | run-id `20def36e065c13d7` |
| Manifest | [MANIFEST.json](/workspace/implementation/reports/research-work/baseline-repair/20def36e065c13d7/MANIFEST.json) | sha256 `20def36e065c13d75d738fbce475cf7ea5425255488861c58a1b5fbbbe8b488f` |
| Summary | [SUMMARY.json](/workspace/implementation/reports/research-work/baseline-repair/20def36e065c13d7/SUMMARY.json) | sha256 `073f270c5a5f454f4a338219eca9421e43bd3440f4ed42252dfb19f5f4d7838d` |
| Completion | [RUN_COMPLETE.json](/workspace/implementation/reports/research-work/baseline-repair/20def36e065c13d7/RUN_COMPLETE.json) | job_count 67938; failed_dates empty |

B0 columns are stored run-1.0.1 job verdicts. SAINT-AMT stays unknown in the census because the frozen repairs leave its C7 stages unevaluated; the 04 adapter binds operational rules and the full-history run belongs to 05 stage A. The `data_unavailable` column is the Phase 1 per-episode label paired with unknown verdicts, not missing market data.


### 04-family-adapters closed artifacts

| Artifact | Path | SHA256 |
| --- | --- | --- |
| P15-09 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-09/72323a6d8f65b77d/attempt-0001/TASK_RECEIPT.json) | `24808e5fa7f6b0760e938affd750525f0d7734161ea3198b197f92d2118a8f03` |
| P15-10 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-10/a856814fe11b24ac/attempt-0001/TASK_RECEIPT.json) | `24ee035f2004e72565dd4d16b9ec56e8f442befe710df7ca2826c7155ca7acc3` |
| P15-11 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-11/a3f84244bc9239c3/attempt-0001/TASK_RECEIPT.json) | `d69dea3844eb5c557e158f87da9c09773b42e189c999224931487659d8a0aec9` |
| P15-12 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-12/2488a221f5843c26/attempt-0001/TASK_RECEIPT.json) | `ad763e3df0c7aefe73f2612a9714951447eccd073effce84be82a48daeebae3d` |
| P15-13 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-13/79e50a6a3faf8be2/attempt-0001/TASK_RECEIPT.json) | `648002fecbe1f8dbf8c5d17dc5d9cbd76582305f5e7a2622449cce4d0a269014` |
| P15-14 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-14/31841425087b5507/attempt-0001/TASK_RECEIPT.json) | `f9b49b80cd0deafdced5b5065851390f20f107cee630b7b727ac278d01fdc4ec` |
| P15-15 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-15/f7df59d81e058166/attempt-0001/TASK_RECEIPT.json) | `cdb641c4244522b892d2f20da2d83a043deb2a380cd58df6b126fd339bb36d53` |
| P15-16 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-16/316dc53caf8bdfac/attempt-0001/TASK_RECEIPT.json) | `1509fd9c5732e34e6e4a64e0cdf78c9f4607f86785da3ebf8837273a2fd09fa8` |
| 04 candidate | [SUBPHASE_RECEIPT.json](/workspace/implementation/reports/research-work/04-family-adapters/924c9a35552250ab/attempt-0001/SUBPHASE_RECEIPT.json) | `3ef9a5ea7d2880a3bafaf36ca24e5fd9d4823f2e50b09f858c209fad9ee8c77d` |
| Matching review | [GATE_REVIEW.json](/workspace/implementation/reports/research-work/04-family-adapters/924c9a35552250ab/attempt-0001/GATE_REVIEW.json) | `226263fa21de8fd9ef78e52c23301654d299618067613f401478a2637968b156` |

Eight NEW task verifiers exit 0 after wiki/handoff edits. Subphase `--gate-review` exit 0. Pinned checker 27/27. Outcome fixtures TOTAL FAILURES 0. All 04 populations are a 9-date engineering slice. Setups: JJ-TBR B0 21 / B0.1 16; GB-FAIL 36/65; GB-VWAP+scalps 19/19; SIRES 15/15; SAINT-AMT 0/0 (40 episodes, no_setup after C7 bind); MEMBER 2/2; KEANI 0/0. F-REFILL-POP path (ii) `population_scale_unreconciled`. First 04 close `b7ed375d0b2721ee` preserved.

### 03-primitives closed artifacts

| Artifact | Path | SHA256 |
| --- | --- | --- |
| P15-05 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-05/8e1ea422bfc8678d/attempt-0001/TASK_RECEIPT.json) | `98446a3ddf415d871ea9925bb5ef89dba48d228c55e160e084b8d561404a687e` |
| P15-06 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-06/50d64d506299dc8d/attempt-0002/TASK_RECEIPT.json) | `79346e962815ad7e9d8209d12ac2ec8504b08b6947dab68e87c8f3f16e9f384a` |
| P15-07 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-07/ac09070f5aeb604b/attempt-0001/TASK_RECEIPT.json) | `9de332211c13f2b1b7279a4e6b3119a5cc1764f3f9edf8e4153ea986f57a7bd7` |
| P15-08 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-08/9728f9ee0bbbdfd5/attempt-0001/TASK_RECEIPT.json) | `bfe62f1cc8e724f87a12fd6fd2e497a3f7ba38999b9799e415b3b7c1f4cb9bbf` |
| 03 candidate | [SUBPHASE_RECEIPT.json](/workspace/implementation/reports/research-work/03-primitives/c1511ed5a468005d/attempt-0001/SUBPHASE_RECEIPT.json) | `00cab78f1e360ec1fc2eb50ee77563633c387ae0a2ab5aee0342711eee034379` |
| Matching review | [GATE_REVIEW.json](/workspace/implementation/reports/research-work/03-primitives/c1511ed5a468005d/attempt-0001/GATE_REVIEW.json) | `2c21645bf715f18a2cabd66b4d5141a2af41636952fb9249232f825d065eb22d` |

`tests/rule_discovery` **234 passed**. Four task verifiers exit 0. Subphase `--gate-review` exit 0. Pinned checker 27/27. Outcome fixtures TOTAL FAILURES 0. Candidate bank: 50 baselines, 160 nonbaseline selected, 840 deferred, 8 process units, T4 on Judas reversal + 7 GB-FAIL sweep branches, B0.1 Judas strict/deferred labels. Per-bank selected: Formation 25, Profile 20, Reference 10, Delta 16, Sequence 52, Memory 23, Timing 14. 20-session declared-scope p90: P15-05 5.30 s, P15-06 6.73 s (engineering finding vs 5 s; bank not reduced). First 03 close `1d3586803dd9688b` is preserved.

### 02-source-reconstruction closed artifacts

| Artifact | Path | SHA256 |
| --- | --- | --- |
| P15-04 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-04/0d0a57cc4de997b4/attempt-0001/TASK_RECEIPT.json) | `f48b3f182111275f3db9f5f98c248c8e0a289c44b09c1d25762a35c142c6a294` |
| 02 candidate | [SUBPHASE_RECEIPT.json](/workspace/implementation/reports/research-work/02-source-reconstruction/c8a2842644f906d6/attempt-0001/SUBPHASE_RECEIPT.json) | `80f2203c943c41ee8c4f7a4bb68891b8ec97320cc1aadaec5885200dec5ca9bf` |
| Matching review | [GATE_REVIEW.json](/workspace/implementation/reports/research-work/02-source-reconstruction/c8a2842644f906d6/attempt-0001/GATE_REVIEW.json) | `fb3916ab93343f16b439984ed51c0d4114abb7a61d2c820d2425f88af63a0d36` |
| Ledger | [SOURCE_RECONSTRUCTION_LEDGER.json](/workspace/implementation/reports/research-work/P15-04/0d0a57cc4de997b4/attempt-0001/SOURCE_RECONSTRUCTION_LEDGER.json) | `fc8c30bcb6e8801aed619f3f38dd0a8a86508e03a6c3729f776eb6980014fbda` |
| Source checks | [SOURCE_CHECKS.json](/workspace/implementation/reports/research-work/P15-04/0d0a57cc4de997b4/attempt-0001/SOURCE_CHECKS.json) | `c51b7bb3fc4adab6a96d1831659dccc95eb4c15794e112a76258116eacdb5af7` |
| Dependency limits | [DEPENDENCY_LIMITS.json](/workspace/implementation/reports/research-work/P15-04/0d0a57cc4de997b4/attempt-0001/DEPENDENCY_LIMITS.json) | `069d1521f3a1871674508eb74520468d6f49c14f30013c92389a658e482bfa48` |

P15-04 pytest **22 passed**. Task verifier exit 0. Subphase `--gate-review` exit 0. Pinned checker 27/27. Outcome fixtures TOTAL FAILURES 0. Refill printed-figure replay disagrees on R sign and median dip; hold rate within 5pp.

### 01-native-and-outcomes closed artifacts

| Artifact | Path | SHA256 |
| --- | --- | --- |
| P15-02 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-02/c9669fa98ba72c43/attempt-0001/TASK_RECEIPT.json) | `38ea80350aa20abecf619b18fe18ad4a9c5a8a2c7ed98461415a340645ef3069` |
| P15-03 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-03/b957ec04d76e9c71/attempt-0001/TASK_RECEIPT.json) | `7f7af3743d42aeff6fc37019b1acbbe2f021193dab7ce9497718779cdb820d81` |
| 01 candidate | [SUBPHASE_RECEIPT.json](/workspace/implementation/reports/research-work/01-native-and-outcomes/207db9ec1a196b8c/attempt-0001/SUBPHASE_RECEIPT.json) | `369529f9424b9ee684646a1f3203ef1bc74da1d4fbb16d05789591ed6527d1fc` |
| Matching review | [GATE_REVIEW.json](/workspace/implementation/reports/research-work/01-native-and-outcomes/207db9ec1a196b8c/attempt-0001/GATE_REVIEW.json) | `d769c4ee16a7d3dabfa44e381ba28e6e9a82a3b858105ff21974ebf7b3847889` |

Whole `tests/rule_discovery` **149 passed**. Both task verifiers exit 0. Subphase `--gate-review` exits 0. Pinned checker 27/27 on the closed foundation receipts. Byte parity **3420/3420**, `byte_for_byte` true; no remaining mismatch dates. Order recovered from run-1.0.1 `completion.json` + job `st_mtime_ns` + recorded `len(input_receipts)`. MarketView n=20 median 3.149s p90 4.806s. Diagnostics through 2021-12-31 are descriptive only.

Previous 01 admissions (preserved): P15-02 `c9756fc1e534b240` sha256 `95a7d487041c3dd5a04d9c5a1f6e4be9551200389df63dd005c484960b31d97e`; P15-03 `babe7a991b6b3dc1` sha256 `5a8e5c5b6abad01e0c79bd8f59015cc63982e2c1ba868a17cf8ca2661378f561`; subphase `50587897e824ede8` sha256 `fb0ea6af7469146a4c37bfb673128ebcd6cd740cb3d986f39a39e0c288f74c62`; GATE_REVIEW sha256 `5c89cd6cff76f07ce6b8b18e6445e5c1e762749ab5a50ca6cd9fc26a559b1d49`. Earlier: P15-02 `cac8165617b72e9f` sha256 `e126ac230dab484ac141a0ef161e71103dff5f57a8d6fb6aef0836222c1049ce`; P15-03 `6986d93967e3eaea` sha256 `f6796aea3233899dfa869508ba22024d3ed8fa4a53e0afcc63564b6c71714c30`; subphase `ceb48321823736a3` sha256 `b38561c6a34155297ff23ab0d9e1c4ff123f147a7a257feabdef414098dee302`; GATE_REVIEW sha256 `cb7627a236a2208d071a073703ed5bea055abc0128f98ac83fa87f042c1da883`. Earlier: P15-02 `ebb1b8270700be4d` sha256 `97c677a2ef9d29c1144dbb5e30e3f9e8ebddac54862bf10bb1e815358b48392f`; P15-03 `53e8f17617f39a87` sha256 `cfe8fc68c1cda6cb4bcb6d48a9012623169d6a5dad7773613c5085c239721412`; subphase `95522aebaedfa3ed` sha256 `8de21ad751caecab4cd9feafa73f4d8b56cb8349ea53750e792789203f119b67`; GATE_REVIEW sha256 `5d192e5f438f9c11355063204526eca0a6a1be0a4b95361727ab73393caceaa2`. Failed 01 bind `e2a2392f99657c2b` is preserved.

### Latest foundation verification evidence (unchanged historical gate)

| Check | Actual observed result |
| --- | --- |
| Targeted P15-00/P15-01 pytest files | **55 passed** in `test_p15_01.py` (includes six new mid-chain/predating/gate-review tests). Whole `tests/rule_discovery` **149 passed**. |
| Unchanged fixed checker on actual v3 foundation receipts | **27/27 passed**. Checker sha256 `c9441fea0a79674991522ae8db5347cdd1060f372d6aa5cffd425c7f30d6b800`. |
| Actual v3 candidate with its actual `--gate-review` | Exit 0. |
| Additional review probe on the new P15-00/subphase/review | 14/14: three accepted controls exit 0, eleven invalid cases exit 2. |
| Preservation checks | Rejected v1 P15-00 remains `a4c5e6bcecdae8af24b69021bf3d9da50f084ee4a2e96c18857e621d69785d20`. Rejected v2 subphase `240838146c38c484` remains `4d96f149d81ffad8173b59bde2d807026e6b8e1fac61c3814531c7b61137b4a0`. |

Saved proof of the defects that required this repair: [v2 REVIEW.md](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/REVIEW.md), [v2 fixed results](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/FIXED_SUITE_RESULTS.json), [v2 additional results](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/additional-suite/RESULTS.json), [v2 preservation check](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/PRESERVATION_CHECK.json).

Current closed artifacts:

| Artifact | Path | SHA256 |
| --- | --- | --- |
| P15-00 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-00/ea9693217cb577cb/attempt-0001/TASK_RECEIPT.json) | `68d5b2505f7961ec8ef8626982af799be954d452eaffb1c34b8a31cd978c5c77` |
| P15-01 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-01/a4c95ab43aef1038/attempt-0001/TASK_RECEIPT.json) | `2f6e9f7ca88462ff8820e27e54e1941fd517b7450bc2cdd0e4dcbab4c1ccf5fa` |
| Foundation candidate | [SUBPHASE_RECEIPT.json](/workspace/implementation/reports/research-work/00-foundation/72c6541ece1cfab0/attempt-0001/SUBPHASE_RECEIPT.json) | `07d0388d88e35348b18e717d9ad7ea9149dce35caddc95a8dfd5c20adbd5ac4f` |
| Matching review | [GATE_REVIEW.json](/workspace/implementation/reports/research-work/00-foundation/72c6541ece1cfab0/attempt-0001/GATE_REVIEW.json) | `b162766b3cdcca89220515dcaa7522ad88ae93a5000d47bfec0a2229f6d4be75` |
| Fixed suite | [RESULTS.json](/workspace/implementation/reports/research-work/00-foundation/72c6541ece1cfab0/fixed-suite/RESULTS.json) | `2829310135408277ae70efd5b0c38795c355e76fc2f41c5354e30b298ba12753` |
| Additional suite | [RESULTS.json](/workspace/implementation/reports/research-work/00-foundation/72c6541ece1cfab0/additional-suite/RESULTS.json) | `ba35a777f9a9b63cd1072ab5b14770423c056a125494a92c32cb38b3b26572f8` |

Previous foundation admission (preserved): P15-00 `3df87f26477a4205` sha256 `3015157cd6a5fd81ea4bb8c222de85a96c456c24a63ad43bb231859cbd7a4cd6`; P15-01 `89ba731db83660ab` sha256 `f131b0dba6df354ca7f557f16e408d7bf11b24296b17e242810c75cbc743fc00`; subphase `1d17f7f63296a745` sha256 `5f09f6b80ce81b30b018395ec1a6139f8376ed0eafe786430848a20287bddf91`; GATE_REVIEW sha256 `dd40523977581bc681cc7a61433b01cf323a0d8bf503b38c60e1587997c711b4`. Earlier: P15-00 `40ffb49bc037e3cc` sha256 `ce57e93846d6a1b3af936703058e15b012aa23720387f00bad4c37cac1341858`; P15-01 `ee71900e26791e89` sha256 `73ec9ea4ccd580275d47901cb807f57733f91d7914daf0e10e7e24fbe5962617`; subphase `6824d15fbda635ce` sha256 `d7f8878b0aa7fda33d0b88d194afff6ca2afb00ea4d85dcca251016b511bb019`; GATE_REVIEW sha256 `d9a6b98c06d67b8716f526710af2eee9c0db92b6503e271fca7f6b03ac4aed95`.

### Five v2 defect groups, now repaired on the v3 receipts

| Defect | Reproduction and consequence |
| --- | --- |
| Final review fails open | `[]` passed as GATE_REVIEW; fabricated results with 27 null cases passed; required code/matrix/graph/command bindings and exact reviewed scope could be removed. The v3 verifier rejects those cases with exit 2. |
| Evidence matrix does not prove acceptance | Every required check could be `fail` with empty evidence while task flags remained true. Passing rows with nonexistent symbols, test nodes and evidence selectors also passed. The v3 verifier now reconciles status with acceptance and resolves references. |
| Snapshot claims are not verified against required bytes/copies | A false source-file hash passed after rebinding the snapshot/draft/run identity. Empty plan-copy mappings and missing code copies were not rejected correctly. The v3 verifier hashes workspace bytes and requires preserved copies. |
| Artifact schema mismatch is missed | An unrelated unsupported SCHEMA_EXAMPLES schema passed after its file hashes were refreshed. The v3 verifier compares parsed schema labels and contents to the declaration. |
| Lineage leaves are incomplete/unresolved | Availability and artifact paths could be omitted; nonexistent row IDs in a real correctly hashed artifact passed. Explicit late availability was already rejected. The v3 verifier requires clocks, paths and resolvable row IDs, and still allows later events only on labelled outcome edges. |

The principal implementation is [contracts/receipts.py](/workspace/implementation/src/trading_research/research/contracts/receipts.py). The v2 review provides exact lines and per-case fixtures. Those were verified acceptance defects; they do not prove every piece of research code is wrong.

### Exact reviewed v2 artifacts — preserved, not current admission

| Artifact | Path | SHA256 |
| --- | --- | --- |
| P15-00 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-00/91ade001fb32cb9b/attempt-0001/TASK_RECEIPT.json) | `2c70bb6ee4a4a1db7ea60c452af8e94cb52e7f68dce24f3e569112bb37e39de0` |
| P15-01 | [TASK_RECEIPT.json](/workspace/implementation/reports/research-work/P15-01/7da6cc99d954e280/attempt-0001/TASK_RECEIPT.json) | `01522514007c1677d553726c0b6a867aa2047f50607d004858886c0c896dc27d` |
| Foundation candidate | [SUBPHASE_RECEIPT.json](/workspace/implementation/reports/research-work/00-foundation/240838146c38c484/attempt-0001/SUBPHASE_RECEIPT.json) | `4d96f149d81ffad8173b59bde2d807026e6b8e1fac61c3814531c7b61137b4a0` |
| Review claiming pass | [GATE_REVIEW.json](/workspace/implementation/reports/research-work/00-foundation/240838146c38c484/attempt-0001/GATE_REVIEW.json) | `7e8a9ccb7afbd8dbcbcefc8d8e145ccbb54504a417b35cea87c2eb516c95e21d` |

The rejected v1 attempts are P15-00 `b291864ccceaca9a`, P15-01 `039267553e8bf721` and foundation `f7135f8d696ff1f5`, each under the same research-work tree with `attempt-0001`. Their hashes and original defects are preserved in the [first review pack](/workspace/planning/research-program/reviews/00-foundation-2026-09-14/REVIEW.md) and [amendment ledger](/workspace/planning/research-program/AMENDMENTS.json). Older P15-00 `d6ee475ab70bbc3a` attempts also exist and have no current assurance version. None should be chosen as an accepted fallback.

Preserve both v1 and the reviewed v2 files. A new repair produces new immutable attempts with complete artifacts and rebound descendants. Do not rewrite old receipts, loosen the spec or edit an independent check to manufacture a passing result.

### What Grok's transcript warnings meant

Grok's final “Attention” said the parent Grok model both implemented and reviewed the change; no separate worker reviewed the diff. That is a review limitation, not a runtime error. One code writer does not prohibit a separate read-only reviewer.

A later `SIGTERM` notification concerned an earlier P15-00 test job stopped after 212 seconds, not a passing run. The later 45-test run was independently reproduced. An intermediate `PREDECESSOR_HASH` test failure was fixed by forwarding the fixture receipts root through phase verification; a failed text replacement was also subsequently applied. Those resolved/interrupted jobs are separate from the ten v2 invalid acceptances that this repair closed.

The saved [transcript review](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/TRANSCRIPT_REVIEW.json) contains relevant public messages and command results. Its source was the Grok session at `/home/arun/.grok/sessions/%2Fworkspace/01a09eee-bd9e-7e73-a2b7-47ff49bf75c1/chat_history.jsonl`. Re-reading the full transcript is unnecessary unless investigating a new discrepancy. The transcript's final next-01 prompt predates the independent rejection and does not authorize proceeding.

## 9. How the next session should continue

Reading this handoff does not itself request a code change or launch all phases. Follow the user's new task. If asked to resume implementation, the next eligible engineering task is `05-finite-search` from the closed 04 receipts in section 8 (`72323a6d8f65b77d` / `a856814fe11b24ac` / `a3f84244bc9239c3` / `2488a221f5843c26` / `79e50a6a3faf8be2` / `31841425087b5507` / `f7df59d81e058166` / `316dc53caf8bdfac` / `924c9a35552250ab`). Do not treat the first 04 close `b7ed375d0b2721ee` or the first 03 close as that gate. Do not start 05 unless the user dispatches that coordinator prompt.

1. Read [AGENTS.md](/workspace/AGENTS.md), the latest [review](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/REVIEW.md) and [single remaining repair prompt](/workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/REPAIR_PROMPT.md). Inspect the actual relevant validators/producers and current identities. If they have not changed, use the retained failing results instead of another broad audit.
2. Use the existing [00 runbook](/workspace/planning/phase-1-5/subphases/00-foundation/RUNBOOK.md) and [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md). Fix the existing five groups, one validator at a time. Add field/failure-specific tests with valid controls; ensure a different malformed field is not accidentally causing the desired rejection. Repair real artifact producers wherever stricter checks expose incomplete output.
3. Retain before/after proof. Verify the new task/candidate/review artifacts with the targeted tests and both independent suites. Passing only the old 27 cases is insufficient. The additional 14 cases must all match: three accepted controls exit 0; eleven invalid cases exit structured 2. Final `--gate-review` verification must also pass on the actual new immutable candidate and review.
4. Record remaining limitations honestly. Passing these suites closes the known holes; it is not proof that every future phase is correct. If the bounded repair cannot meet its criteria, stop at 00 and report the unresolved cases. Do not declare a new task eligible by narrative alone.
5. After a verified closure, update the active status/handoff with exact new identities and resolved review evidence. A subsequent user-dispatched subphase uses one coordinator prompt. Advance to 01 only from the properly closed gate, and never cross the whole-Phase-1.5 prerequisite for Phase 2.

The canonical [FOUNDATION_REPAIR.md](/workspace/planning/research-program/FOUNDATION_REPAIR.md) describes the earlier v1-to-v2 work. It remains useful historical contract context, but the **latest review-specific REPAIR_PROMPT.md linked above is the immediate handoff**. Do not restart the already completed documentation/planning work or discard working foundation code just to begin again.

### Verification commands and their limits

Existing targeted test command, from `/workspace/implementation`:

```bash
.venv/bin/python -m pytest tests/rule_discovery/test_p15_00.py tests/rule_discovery/test_p15_01.py -q -p no:cacheprovider
```

The fixed checker is [tools/check_foundation_adversarial.py](/workspace/tools/check_foundation_adversarial.py), pinned SHA256:

```text
c9441fea0a79674991522ae8db5347cdd1060f372d6aa5cffd425c7f30d6b800
```

Both tools below exist. Replace each uppercase path placeholder with the **actual newly produced immutable artifact**, and choose unused output directories. These commands create isolated probe artifacts; they do not repair implementation. The old v2 paths above reproduce the known failing state.

```bash
/workspace/implementation/.venv/bin/python /workspace/tools/check_foundation_adversarial.py \
  --p15-00 P15_00_RECEIPT_PATH \
  --p15-01 P15_01_RECEIPT_PATH \
  --subphase SUBPHASE_RECEIPT_PATH \
  --output-root NEW_FIXED_SUITE_OUTPUT_DIRECTORY

/workspace/implementation/.venv/bin/python /workspace/planning/research-program/reviews/00-foundation-v2-2026-09-14/additional_probe.py \
  --p15-00 P15_00_RECEIPT_PATH \
  --subphase SUBPHASE_RECEIPT_PATH \
  --review GATE_REVIEW_PATH \
  --output-root NEW_ADDITIONAL_SUITE_OUTPUT_DIRECTORY

/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py subphase \
  --receipt SUBPHASE_RECEIPT_PATH \
  --gate-review GATE_REVIEW_PATH
```

If canonical planning contracts/cards actually change, regenerate bundles with `python tools/build_research_plan_bundles.py` from `/workspace`. Read-only freshness/structure checks are:

```bash
python tools/build_research_plan_bundles.py --check
python tools/check_research_plan.py
```

The historical `--authoring-scope` option was for the earlier documentation-only change; it is not the right scope claim for the existing implementation work. Documentation checks prove document structure, not software correctness. No research run is needed simply to read this handoff or check its links.

## 10. Collaboration and workspace rules to preserve

- The user normally supplies **one prompt per subphase** to Grok, not each worker prompt. The coordinator handles dependencies and internal bounded work.
- In the Grok workflow, use the installed pstack router and parent Grok for every role. Default to at most three live agents including the coordinator, one code writer per shared checkout, and explicit ownership. Read-only review can be separate. If permitted workers are unavailable, proceed sequentially rather than switching to a forbidden model.
- Do not route this project through Astra, Fable or archived Cursor/mill workers unless the user explicitly names them. Old role/playbook files under the archive are history, not live authority.
- Routine implementation choices are already specified or can be resolved with judgment. Do not make the user decode proprietary formulas, pick an empirical winner or repeatedly approve an already authorized bounded run. A new objective or phase boundary change is a new user decision.
- Keep work local. No PR, push, merge, deployment, outside messages or paid data actions are authorized merely by the research packs.
- Git operations belong only in `/workspace`. Preserve existing edits and untracked work. `/workspace/data` stays on disk and out of Git.
- Do not edit `planning/phase-1-from-scratch/`, `planning/phase-1-fable/`, `archive/` or `sources/`. Preserve accepted Phase 1 implementation/report identities and use new versioned outputs for new work.
- Canonical contracts and task cards are edited directly; generated READMEs/prompts/runbooks are rebuilt, not maintained independently. Do not create another competing definitions wiki.
- When reporting family research results, print **both** required tables: `family | variant | n | faithful_disagreements | status | report path` and `family | id | verdict | fixture | leakage | proxy-as-faithful | notes`. Review-only or documentation work does not create new family research results.

## 11. Suggested first message for a new session

```text
Read /workspace/PROJECT_HANDOFF.md first. It is the project context and dated handoff from the previous session. Preserve the settled goals and phase boundaries, distinguish specifications from implemented/verified work, and check whether relevant files changed after the recorded review. The current stopping point is closed `00-foundation` on receipts `40ffb49bc037e3cc` / `ee71900e26791e89` / `6824d15fbda635ce`. Do not restart the project or run later phases automatically. Then carry out my next request using this context.
```

When this file is updated later, retain the historical evidence links, revise the top stopping point and exact current identities, and distinguish new observed verification from claims or inherited results. A future session should not need the original conversation to understand why a gate is open or blocked.
