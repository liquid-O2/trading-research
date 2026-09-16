# The project at a glance

Short version for the owner. One line per idea. Status as of 2026-09-16, 21:00 UTC. Numbers and verdicts per task live in the [results ledger](/workspace/wiki/results-ledger.md).

## What we are building

- A decision process for trading the NQ future, built one part at a time.
- Twelve published methods supply the rules and the reads: Jumbo, Green Bird ×3, Sires, Saint, an unnamed member, Keani, Refill, jetbundle, Stoic ×2.
- Everything is measured on 1,742 sessions, 2020-01-01 to 2026-09-03, with one contract and fixed costs.
- Target at the very end: $3,000 per day, never more than $1,000 lost in a day. No phase before the final replay may claim it.

## The five phases

| Phase | Question | Output | Status |
| --- | --- | --- | --- |
| 1 | What do the methods do, and how often do their setups appear on our data? | The census: 50 branches, 18,747 setups | closed |
| 1.5 | Can any single rule be improved, honestly, within a finite search? | Strategy Book v1, retention set, exit study | closing tonight |
| 2 | What is the market's context now, and what happens next? | Context experts, method experts, plans, Strategy Book v2 | starts 2026-09-18 |
| 3 | Where are the actionable levels, and how does price react there? | Location experts | scope reserved |
| 4 | Whether and when to enter, and how it all performs as one account | Entry experts, the integrator, the combined replay | scope reserved |

Rules that never change:

- The author's own read is the baseline for each part. Our models must beat it, or the author's read stays.
- The last five months, 2026-04-01 to 2026-09-03, are blind. Nothing fits, tunes or selects on them. Each release tests on them once.
- Comparisons are walk-forward by calendar year, purged and embargoed. Phase 2 adds rolling refits beside that.
- Nothing is thrown away. Every rule and candidate keeps a status and a reason.
- Every number points at the file it came from. Every outcome is used only after it was knowable.
- A negative result closes a phase as validly as a positive one.
- Every task ends with a result card: question, numbers, target met or not, verdict, lever.

## Phase 1 · What the methods do (closed)

Steps that were done, in order:

1. Read every source page, chart and post; write the wiki: 12 method pages and about 90 object pages with the exact predicates.
2. Register the formulas, rules and operators, with what is source-exact, printed-but-different, or inferred.
3. Acquire the data and define event-time contracts: executions, quotes, coverage, clocks, availability.
4. Implement one scanner per branch with fixtures, native controls and future-perturbation checks (773 tests).
5. Run the census on all 1,742 sessions: 99,294 daily jobs, 18,747 observed setups.
6. Audit: 341 charts inspected, construction audit, source conformance review, findings and handoffs.

What you got: per method, how many setups occur and what happened after them (prices, not fills). Setups per method: Jumbo 3,912 · GB failure 7,589 · GB VWAP 499 · GB scalps 3,066 · Sires 2,538 · Saint 785 · Member 352 · Keani 6.

Judge it by: every branch searched on every session, limits explicit, no claim of edge.

## Phase 1.5 · Improve single rules (closing tonight)

### 00 Foundation (closed)

| Task | What it makes | Why | Judge by |
| --- | --- | --- | --- |
| P15-00 | One frozen identity for the Phase 1 baseline and typed records | Everything after refers to it | 50 branches and 8 units reconcile; hashes stable |
| P15-01 | The verifier for receipts and dependencies | Nothing counts on a summary | A missing predecessor or one tampered byte fails |

### 01 Native data and outcomes (closed)

| Task | What it makes | Why | Judge by |
| --- | --- | --- | --- |
| P15-02 | The native market view over the full account day | One causal view for every rule and expert | Byte parity with the frozen scanners: 3,420 of 3,420 |
| P15-03 | Outcome labels, the costed replay, the folds | One benchmark for every comparison | The $25 net-P&L fixture; ambiguous same-batch cases labelled |

### 02 Source reconstruction (closed)

| Task | What it makes | Why | Judge by |
| --- | --- | --- | --- |
| P15-04 | The operand ledger: EV, P-zones, KG1/gamma, auction, macro | Says what is source-exact and what is inferred | 48 rows, each with a source pointer and a disposition |

### 03 Primitives (closed)

| Task | What it makes | Why | Judge by |
| --- | --- | --- | --- |
| P15-05 | Formations F1–F3, profiles | First axis of the candidate bank | Volume conserved; 70% area by the specified walk |
| P15-06 | CVD variants C0–C3, cohort memory | Flow inputs with unknown volume kept apart | +10/−4/unknown 6 fixture |
| P15-07 | Response state machines S1–S4 | Explicit sequences, no shortcuts | A retest before a reclaim cannot pass |
| P15-08 | The finite candidate bank | At most 160 candidates, declared before results | One axis per candidate; identical expansion before outcomes |

### 04 Family adapters (closed)

| Task | What it makes | Why | Judge by |
| --- | --- | --- | --- |
| P15-09…15 | One adapter per method | Reproduces each source predicate stage by stage | Empty change reproduces the baseline; unknown operands named |
| P15-16 | Refill, jetbundle, Stoic kept as observations | They are context, not entries | No entry win-rate for observation units |

### 05 Finite search (running)

| Task | What it makes | Why | Judge by |
| --- | --- | --- | --- |
| P15-16A | Baseline B0.2: the source's own rule, measured on the whole population | The comparison must be against the real rule | 41 branches in bound or diagnosed; author examples reach location |
| P15-17 | The breadth screen: every candidate on every fold against B0.2 | Finds which mechanism changes help | Every candidate has a record; outer data never picks a bank |
| P15-18 | One bounded refinement plus one combination per family | Tune only in the past, in fixed neighbourhoods | Neighbours exactly the contract's; a six-example win stays inconclusive |

### 06 Exit controls (next)

| Task | What it makes | Why | Judge by |
| --- | --- | --- | --- |
| P15-19 | Exit study E0–E4 on frozen entries | Exits cannot rescue a weak entry | No stop is loosened; no future maximum used |

### 07 Release (machinery built)

| Task | What it makes | Why | Judge by |
| --- | --- | --- | --- |
| P15-20 | Strategy Book v1, retention set, release inputs, hold-out report, handoff | The deliverable, with no hand-typed number | Every branch has a verdict; census reconciles; hold-out tested once |

## Phase 2 · Context and experts (starts 2026-09-18)

| Sub | Task | What it makes | Why | Judge by |
| --- | --- | --- | --- | --- |
| 00 | P2-00 | Verification of the Phase 1.5 release; the allowed inputs | Phase 2 uses only verified rules | Phase verifier exits 0; allowlist frozen |
| 01 | P2-01 | Snapshot rows, labels, causal joins | Every expert trains on the same rows | Rows carry availability masks; hold-out rows refused |
| 01 | P2-02 | The fitting engine and chronological stacking | One engine for every expert | Declared grids; purge and embargo respected |
| 02 | P2-09 | Native option, spot and OI adapters | Owned chains with real identities | Every root normalised; raw ids preserved |
| 02 | P2-10 | Pricing, Greeks, exposure boards | Gamma, vega, vanna, OI from owned chains | Pricing fixtures; units explicit |
| 03 | P2-02A | The authors' own context reads, measured | Our models must beat the authors' reads | Each read fires at a plausible rate; causal; same rows as experts |
| 03 | P2-03 | Volatility arithmetic and targets | One volatility expert, many heads | Estimator identities; clocks explicit |
| 03 | P2-04 | The joint volatility expert | Forecast variance, intervals, movement scale | Beats the source read and the baselines, or is retained |
| 04 | P2-05 | Range-path and auction experts | Excursion, first-passage, break topology, day state | Censored bins handled; provisional vs final state separated |
| 04 | P2-11 | Option flow, exposure changes, scenarios | What options did and would do under a shock | Signed/unknown kept apart; roll ambiguity flagged |
| 04 | P2-07 | Flow-memory and cross-market experts | Rewarded aggression; lead/lag; spot/IV coupling | No future returns; no cloned strategies on other assets |
| 05 | P2-12 | Intraday open-interest updates | OI is daily; estimate it intraday | Complete contract-day groups; exclusions with reasons |
| 06 | P2-13 | One context expert per method (eight) | Will a setup occur, how useful, which session and timing | Per method: masks separate, no future value, low support honest |
| 06 | P2-21 | Process context and the risk overlay | Refill memory, jetbundle states, macro; risk stays a rule | Causal zones and contacts only |
| 07 | P2-22 | Conditional plans and the contribution replay | Forecasts become per-method plans | Plan scoring exact; alternatives preserved |
| 07 | P2-23 | Refit cadences, matured-label updates | Which refit schedule holds up | Rolling beside expanding, same purge and hold-out |
| 08 | P2-24 | Full causal replay and the Phase 3 handoff | Proves the whole stack | Every expert has a scorecard; hold-out tested once |

## Phases 3 and 4 (scope reserved)

- Phase 3: register the authors' own location reads first (P-zones, KG1 and gamma levels, prior extremes, value and volume nodes, blocks and gaps), then fit location experts: forward-volatility areas, native gamma/vega/vanna/OI/volume/VWAP areas, arrival and reaction, competing levels. Revisits candidates that failed on `location_miss`.
- Phase 4: entry experts and the integrator; cross-asset responses; one combined account-level replay against the target. Revisits candidates that failed on `confirmation_delay` or `adverse_before_target`.
- Later: learned exit and re-entry management, only after the fixed-entry controls. A user decision.
- The Phase 3 and 4 task packs are written at the Phase 2 release.

## How "done" is checked

- Each task: receipt (pinned plan and code, evidence matrix, work log, report) plus a result card.
- The verifier recomputes every identity, walks predecessors, and fails on any gap or forgery.
- Each subphase: its own receipt and gate review. Each phase: phase receipt and a fresh cross-model review.
- Process: one page, [HOW_TO_RUN.md](research-program/HOW_TO_RUN.md). Policy: [AGENTS.md](/workspace/AGENTS.md).

## Words

- **Branch**: one method's specific setup route, for example Green Bird `nyam_box`.
- **B0 / B0.1 / B0.2**: frozen scanner; corrected semantics; source-faithful re-implementation (the baseline).
- **Candidate**: a branch with one mechanism changed: formation, profile, reference, delta, sequence, memory or timing.
- **Fold**: a test year, 2022 to 2026 (2026 ends 2026-03-31), with fit, tune and calibration windows before it.
- **Hold-out**: 2026-04-01 to 2026-09-03, blind until a release tests on it once.
- **Promotion gates**: support, positive lower bound, Holm p ≤ 0.05, positive blocks, no cost-stress reversal.
- **Retention set**: every branch and candidate with a status and a first failure reason.
- **Receipt**: the evidence bundle a task ends with. **Result card**: the judgement a task ends with.
- **Source read**: an author's own rule for context, location or entry; the baseline a model must beat.
