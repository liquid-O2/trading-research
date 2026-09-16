# The project at a glance

One page for the owner: what the program builds, phase by phase, what each task is for, and what you get out of it. Everything here is drawn from the plan and the wiki; the tables are the map, the linked documents are the territory. Status as of 2026-09-16 evening.

## The objective in one paragraph

Build an adaptive decision process for trading the NQ future, one component at a time, on owned data from 2020 onward (earlier data only as causal lookback). Twelve published trading methods (Jumbo, Green Bird ×3, Sires, Saint, an unnamed member, Keani, the Refill study, jetbundle, Stoic ×2) supply the baselines and the mechanisms. Every claim is measured on 1,742 sessions from 2020-01-01 to 2026-09-03 with a fixed one-contract benchmark, chronological out-of-sample comparison by calendar year, and a verifier that refuses any result whose code, data and plan identities do not check out. The eventual economic target is $3,000 per trading day with a $1,000 maximum daily loss; no phase before the final combined replay may claim it.

## How the phases fit

| Phase | Question it answers | What comes out | Gate to the next |
| --- | --- | --- | --- |
| 1 (complete) | What do the source methods actually do, and how often do their setups occur on our data? | The accepted census: 50 branches and 8 observation units, 99,294 daily jobs, 18,747 observed setups | Accepted census with limitations carried forward |
| 1.5 (closing tonight) | Can any single rule of a method be made better, honestly, within a finite search? | Strategy Book v1: per branch the definition, population, base rates, regime cuts, every attempted upgrade, a verdict; the retention set; fold-specific selected rules; the exit study | Phase receipt verified, every branch with a verdict |
| 2 (starts 2026-09-18) | What is the market's context right now and what will it do next, per mechanism and per method? | Fitted context experts (volatility, range path, auction state, flow, cross-market, options exposure, intraday OI), method-specific suitability experts, conditional plans, Strategy Book v2 | Release receipt, every expert with a scorecard, Phase 3 allowlist |
| 3 (scope reserved) | Where are the actionable locations, and how does price react when it arrives? | Fitted location experts: P-zone upgrades, forward-volatility areas, native gamma/vega/vanna/OI/volume/VWAP/prior-extreme areas, arrival and conditional reaction | Location gate |
| 4 (scope reserved) | Whether and when to enter, given context and location, and how the whole thing performs as one account? | Response and entry experts, the integrator, cross-asset responses, the combined historical replay at account level | Combined replay against the economic target |
| Later management work | Can learned exit and re-entry management beat the fixed-entry controls? | Empirical management specialists | A user decision; not a numbered phase |

Rules that hold in every phase: nothing is discarded (every branch and candidate stays in a retention set with a status and a reason), every number points at the immutable artifact it came from, every date's outcome is used only after its availability clock, and a negative or inconclusive result closes a phase as validly as a positive one.

## Phase 1, complete

The frozen run `run-1.0.1` measured every source branch on the acquired data with owned MBP-1 event-time executions, same-contract references and a versioned NQ session policy. The wiki method pages hold the exact source predicates, re-read against the raw pages and charts on 2026-09-15. Known boundary and bookkeeping defects in the frozen scanners are labelled B0; corrected semantics are B0.1; the source-faithful re-implementation used as the Phase 1.5 baseline is B0.2.

## Phase 1.5, the finite rule search

Subphases in order; a subphase closes with verified task receipts, a subphase receipt and a passing gate review.

### 00 Foundation, closed

| Task | Builds | Why | You get |
| --- | --- | --- | --- |
| P15-00 | Binding of the accepted Phase 1 baseline and typed records for every later artifact | Everything downstream must refer to one frozen identity of code, data and registry | The engineering-date manifest, schema examples, baseline binding |
| P15-01 | The receipt and dependency verifier | No result is accepted on a summary; the verifier recomputes identities, walks predecessors and rejects forged or incomplete evidence | `verify_research_release.py`, the verifier cases |

### 01 Native data and outcomes, closed

| Task | Builds | Why | You get |
| --- | --- | --- | --- |
| P15-02 | The native MarketView over the full account day, delegating unchanged rules to the Phase 1 scanners | One columnar, causal view of executions, quotes and coverage that every rule and expert reads | Byte-identical baseline parity on a stratified sample, throughput measurement |
| P15-03 | Ordered outcome labels, the costed one-contract replay, chronological folds | A single benchmark and evaluation protocol so candidates are compared on the same terms | The split manifest, the evaluation protocol, the outcome contracts |

### 02 Source reconstruction, closed

| Task | Builds | Why | You get |
| --- | --- | --- | --- |
| P15-04 | The source-to-operator ledger for every numerical operand (EV, P-zones, KG1/gamma, auction, macro) | Says, per operand, whether it is source-exact, printed-but-different, inferred or not identifiable | The ledger, the printed-figure replay, Strategy Book B0-only edition with frozen regime dimensions |

### 03 Primitives, closed

| Task | Builds | Why | You get |
| --- | --- | --- | --- |
| P15-05 | Causal formations F1 to F3 and profile primitives | The candidate bank changes one mechanism at a time; formations are the first axis | Formation identities at registered source clocks |
| P15-06 | CVD variants C0 to C3 and resolved cohort memory | Flow inputs with native aggressor uncertainty kept separate | Delta series with availability clocks |
| P15-07 | Response state machines S1 to S4 | Explicit sequences (contact, sweep, reclaim, retest, confirm) instead of a universal shortcut | Pure transitions with stage evidence and expiry |
| P15-08 | Reference rules and the finite candidate bank | Registers at most 160 candidates so the search is finite and pre-declared | `candidate-bank.json`, the bank axes and neighbourhoods |

### 04 Family adapters, closed

| Task | Builds | Why | You get |
| --- | --- | --- | --- |
| P15-09 to P15-15 | One adapter per method: Jumbo, Green Bird failure, Green Bird VWAP and scalps, Sires, Saint, Member, Keani | Each adapter reproduces its source predicate stage by stage and reports where an operand is unknown | Full-history populations and coverage per branch |
| P15-16 | Research-process and risk observations (Refill, jetbundle, Stoic) preserved as observations | They inform context later; they are not market entries | Their records, without manufactured entries |

### 05 Finite search, in progress

| Task | Builds | Why | You get | State |
| --- | --- | --- | --- | --- |
| P15-16A | The source-faithful baseline B0.2 for every family, plausibility gates, author-example replay | The comparison baseline must be the source's own rule, measured on the population, not a proxy | B0.2 over 1,742 sessions and 41 branches with funnels and bounds, the fidelity matrix | Receipt being re-issued tonight |
| P15-17 | The breadth screen: every registered candidate on every fold, paired against B0.2 | Finds which mechanism changes help, with support gates, Holm and a block bootstrap | Trial ledger, breadth results, refinement allowlist, family reports | Definitive run on the fast engine running now |
| P15-18 | One bounded refinement around the selected banks, plus one combination per family | Tunes only inside each fold's past data, within the contract's exact neighbourhoods | Refined selections per fold, the all-history recommendation kept separate | Rehearsal complete; definitive run next |

### 06 Exit controls, next

| Task | Builds | Why | You get |
| --- | --- | --- | --- |
| P15-19 | The exit study E0 to E4 on frozen entries | Exits are compared after entries are frozen so they cannot rescue a weak entry rule | Paired exit comparisons per selected rule |

### 07 Release, machinery built

| Task | Builds | Why | You get |
| --- | --- | --- | --- |
| P15-20 | Strategy Book v1, the retention set, census reconciliation, release inputs, Phase 2 handoff | The phase's deliverable, with every number pointing at its artifact and no hand-typed figure | `STRATEGY_BOOK.md/.json`, one CSV per branch, `RETENTION_SET.json`, `RELEASE_INPUTS.json` |

## Phase 2, context and experts (17 tasks)

| Subphase | Task | Builds | Why | You get |
| --- | --- | --- | --- | --- |
| 00 Entry gate | P2-00 | Verification of the whole Phase 1.5 release and the frozen Phase 2 scope | Phase 2 must consume only verified rules and manifests | The Phase 2 allowlist of inputs |
| 01 Datasets and fitting | P2-01 | Snapshots, labels and causal dataset joins on account-day and quarter-hour grids | Every expert trains on the same causal rows | Snapshot and target rows with availability masks |
| | P2-02 | Deterministic fitting and chronological stacking | One fitting engine (ridge, hinge, softmax, quantile, calibration) with declared grids | The shared engine every expert uses |
| 02 Native options baseline | P2-09 | Native option, spot and OI adapters | Owned option chains normalised with their real identities | The options data plane (staged; starting in parallel now) |
| | P2-10 | Pricing, Greeks and exposure boards | Gamma, vega, vanna and OI exposure from owned chains | Native exposure boards (staged) |
| 03 Joint volatility | P2-02A | The authors' own context reads (Jumbo's day and break-topology read, Sires' regime read, Saint's structure read, Keani's open read, Green Bird's session read, Member's area memory) as deterministic baselines measured on the population | Our volatility, gamma and IV experts are upgrades on top of the authors' reads, not replacements; every expert must beat the source read | Source context rules registry, baseline results, the paired-comparison protocol |
| | P2-03 | Volatility arithmetic and multi-horizon targets (GK, YZ, HAR, IV) | One volatility expert with several forecast heads, not one per estimator | Feature groups and targets (staged) |
| | P2-04 | The joint volatility expert and its ablations | Forecast variance, intervals and movement scale | Expert artifact and scorecard |
| 04 Context mechanisms | P2-05 | Range-path and auction-session experts | Remaining excursion, first-passage times, break topology; auction and day state | Two expert artifacts |
| | P2-11 | Option flow, exposure changes and repricing scenarios | What the options market did and would do under a shock | Flow and scenario boards |
| | P2-07 | Flow-memory and cross-market experts | Rewarded aggression, failed pushes; related-market lead/lag and spot/IV coupling | Two expert artifacts |
| 05 Intraday OI | P2-12 | Weakly supervised intraday OI updates | Open interest is published daily; the update estimates it intraday with uncertainty | OI update expert against B0/B1/B2 baselines |
| 06 Method experts | P2-13 | One context expert per source method (eight methods, one engine, one configuration each) | Per method: will a setup occur, how useful will it be, which session, reference, confirmation and timing suit it | Eight artifacts and scorecards |
| | P2-21 | Research-process context and the risk overlay interfaces | Refill memory, jetbundle transitions, macro contribution; risk stays a rule overlay | Interfaces and artifacts |
| 07 Plans and adaptation | P2-22 | Conditional plans and the fixed context-contribution replay | Turns forecasts into per-method conditional plans and measures their contribution | Plans manifest, replay report |
| | P2-23 | Refit cadences and matured-label intraday updates | Which refit schedule (annual, monthly, weekly, plus intraday) holds up chronologically | The cadence comparison |
| 08 Release | P2-24 | The full chronological dependency replay and the Phase 3 handoff | Proves the whole stack causally and hands Phase 3 its admissible inputs | Strategy Book v2, expert scorecards, retention set, `PHASE3_HANDOFF.md` |

## What "done" means, and how it is checked

Each task ends with a receipt: pinned plan and code snapshots, a run manifest, an evidence matrix binding every acceptance key to a real test or audit command, a work log, and a report. The verifier recomputes every identity, walks the predecessor chain, and exits non-zero on any forgery, gap or unreconciled job. A subphase closes with its own receipt and a gate review; a phase with a phase receipt and a fresh cross-model review. The process for running a subphase is one page, [HOW_TO_RUN.md](research-program/HOW_TO_RUN.md); the policy is [AGENTS.md](/workspace/AGENTS.md).

## Glossary

- **Branch**: one source method's specific setup route (for example Green Bird `nyam_box`).
- **B0 / B0.1 / B0.2**: the frozen Phase 1 scanner, its corrected semantics, and the source-faithful re-implementation used as the comparison baseline.
- **Candidate**: a branch with exactly one mechanism axis changed (formation, profile, reference, delta, sequence, memory, timing).
- **Fold**: a calendar-year test block (2022 to 2026) with fit, tune and calibration windows before it.
- **Promotion gates**: support, paired improvement with a positive lower bound, Holm-adjusted p ≤ 0.05, positive blocks, no cost-stress reversal.
- **Retention set**: every branch and candidate with a status (`active_selected`, `active_baseline`, `inactive_retained`) and a first failure attribution that decides which later phase revisits it.
- **Receipt**: the immutable evidence bundle a task ends with; nothing counts without one.

Sources: [ROADMAP.md](ROADMAP.md), [phase 1.5 pack](phase-1-5/README.md), [phase 2 pack](phase-2/README.md), [wiki status](/workspace/wiki/current-status.md).
