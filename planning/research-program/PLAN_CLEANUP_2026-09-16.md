# Plan cleanup, 2026-09-16

The user's decision after the [simplification review](SIMPLIFICATION_REVIEW_2026-09-16.md): clean the plan up, keep only what helps, retire the plugin-routed process layers, and close Phase 1.5 by 2026-09-17. This document is the executable cleanup plan: what changes, in which order, and the schedule. It changes no formula, budget, gate, split, seed, bank or retention rule. Every edit of a pinned plan file is recorded in one chained `AMENDMENTS.json` entry when the edit pass lands.

## 1. What stays exactly as it is

`SEARCH_CONTRACT.md`, `EVALUATION.md`, `OUTCOMES.md`, `RETENTION.md`, `DATA_CONTRACTS.md`, `PERFORMANCE.md`, `MODEL_FITTING.md`, `TYPE_REFERENCE.py`, the assurance contract `ASSURANCE.md` and the pinned foundation checker, the verifier (`contracts/receipts.py`, `verify_research_release.py`), B0.2 with its plausibility gate, the wiki method pages, every closed receipt and its snapshots, and the subphase structure of both phases.

## 2. What is retired

| File or tool | Action | Why |
| --- | --- | --- |
| `research-program/PSTACK_EXECUTION.md` | Replaced by a retirement notice pointing to `HOW_TO_RUN.md` | Router and model role tables are replaced by `AGENTS.md` |
| `phase-1-5/PROMPTS.md`, `phase-2/PROMPTS.md` | Retirement notice | Prompt blocks copied the runbooks; the card plus `HOW_TO_RUN.md` is the prompt |
| `phase-*/subphases/*/RUNBOOK.md` | Retirement notice in each; no longer generated | Each embedded the whole pstack contract again |
| "Copyable worker prompt" sections in cards | Removed from open cards; closed cards untouched | Duplicated the card |
| `tools/build_research_plan_bundles.py`, `tools/check_research_plan.py` | Retired (kept in history; not run) | They only generated and checked the retired bundles |
| `TASK_GRAPH.json` `reads` | `PSTACK_EXECUTION.md` replaced by `HOW_TO_RUN.md` for every task; `WORKFLOW.md` kept only where it adds the two tables | Shrinks each task's read list |
| `WORKFLOW.md` | Trimmed to the execution contract that is not in `AGENTS.md`/`HOW_TO_RUN.md`: the two family tables, terminal statuses, the artifact list | Rest is duplicated |
| Phase READMEs, `ROADMAP.md` "Reading and starting" | Point to `HOW_TO_RUN.md` and the cards; drop the retired process sentences | Current entry points |

Retirement notices keep the file paths alive so that closed receipts, which pin those files by hash, verify through the amendment chain from their declared hash, and nothing is deleted from history.

## 3. Assurance assignments

Cases S01 to S04 (missing or forged artifacts, green tests hiding missing behaviour, self-asserted identities, forged closure) test the shared verifier, which does not change per task. They are assigned to P15-01 (closed), P15-20 and P2-24 only. Every other task cites P15-01's bound evidence, which `SILENT_FAILURES.md` already permits. `ASSURANCE_CASES.json` is edited accordingly and `SILENT_FAILURES.md` regenerated once from it (then the generator is retired). The remaining 28 cases keep their assignments; they concern research behaviour.

## 4. Re-cut of the remaining tasks

Phase 1.5 keeps P15-17, P15-18, P15-19 and P15-20 as they are: they are distinct stages with one owner each, and P15-17 and P15-18 are in flight. Their open cards lose the pstack read pointers and prompt sections and gain the template's "Delivers" and "Out of scope" paragraphs; nothing else changes.

Phase 2 goes from 25 cards to 16. Subphases, gates and the entry rule (P2-09, P2-10, P2-03 may start from the verified P15-02 receipt) are unchanged.

| New card | Absorbs | Owns |
| --- | --- | --- |
| P2-00 entry gate | unchanged | unchanged |
| P2-01 snapshots and datasets | unchanged | unchanged |
| P2-02 fitting and stacking | unchanged | unchanged |
| P2-03 volatility arithmetic | unchanged (staged receipt) | unchanged |
| P2-04 joint volatility expert | unchanged | unchanged |
| P2-05 range and auction experts | P2-05, P2-06 | `experts/range_path.py`, `experts/auction_session.py`, one config each, one test module |
| P2-07 flow and cross-market experts | P2-07, P2-08 | `experts/flow_memory.py`, `experts/cross_market.py`, one config each, one test module |
| P2-09 native option adapters | unchanged (staged receipt) | unchanged |
| P2-10 pricing, Greeks, exposure boards | unchanged (staged receipt) | unchanged |
| P2-11 flow, exposure changes, scenarios | unchanged | unchanged |
| P2-12 intraday OI updates | unchanged | unchanged |
| P2-13 method context experts | P2-13 to P2-20 (eight methods) | `experts/methods/` package with one module and one config per method, one test module parameterised over methods, one report per method |
| P2-21 research-process context and risk overlay | unchanged | unchanged |
| P2-22 conditional plans and replay | unchanged | unchanged |
| P2-23 refit cadences and matured labels | unchanged | unchanged |
| P2-24 release and Phase 3 handoff | unchanged | unchanged |

Merged cards keep every acceptance key of the cards they absorb, expressed per method or per mechanism where the original was per task; a merged task reports one family table per method. The assigned research cases are the union. Dependencies collapse accordingly (P2-22 depends on P2-13 instead of on eight tasks).

## 5. Patterns adopted from the mat and pstack repositories

Adopted, in `HOW_TO_RUN.md` and `TASK_CARD_TEMPLATE.md`: a card is a tracer-bullet vertical slice sized for one context window with declared blocking edges, and work proceeds on the frontier (mat `to-tickets`); a spec states problem, solution, decisions, testing decisions and out-of-scope, without file paths in prose (mat `to-spec`); hand-offs and briefs point at artifacts instead of restating them (mat `implement-spec` and its handoff skill); an autonomous run states its exit predicate first, picks a wake mechanism, makes the smallest change the evidence justifies, and never relaxes the predicate (pstack `autonomous-run`); the four-part throughput checkpoint before fan-out (pstack `feature`); resume from the trail and verify inherited claims on the real artifact (pstack `session-pickup`); a durable wip commit and a resume note when pausing (pstack `pause-safely`); subtract before you add, minimise reader load, build the lever (pstack principles).

Not adopted: the skill router, model role tables, agent panels (arena, interrogate, swarm), PR and shipping playbooks, and any playbook copied verbatim into a runbook.

## 6. Phase 1.5 closure by 2026-09-17: the schedule

Owners: the P15-16A integration implementer on main until its receipt verifies; the stage B implementer owns 05, 06 and 07 sequentially in the fast worktree (`refinement.py`, `exits.py`, `release.py` are its paths; the machinery for P15-18 and P15-19 is already built and tested). The orchestrator merges, verifies, writes subphase receipts and gate reviews, and updates the wiki. A fresh reviewer is used once, for the phase-level review at closure, as authorized.

| When (UTC) | Step | Exit predicate |
| --- | --- | --- |
| 16th, by 23:00 | P15-16A receipt verified, probes pass, main committed and pushed; subphase 04 already closed | `verify_research_release.py task` exits 0 on the P15-16A receipt |
| 16th, by 23:30 | Merge main into the fast worktree; RA-1 and a five-date parity check on the merged engine; if a Green Bird scan legitimately changed, record it | RA-1 digests equal or the difference traced to a named P15-16A change |
| 17th, by 00:30 | Definitive breadth run `attempt-0003`, 17 workers, both B0.2 roots, receipt digest in RUN_META; the rehearsal `attempt-0002` is the parity oracle | RUN_COMPLETE with 1,741 dates and the one retained failure |
| 17th, by 03:00 | Fold evaluation, TRIALS.jsonl, allowlist, family reports, P15-17 receipt verified | verifier exits 0 |
| 17th, by 08:00 | P15-18 refinement (at most 24 neighbours per family, fast engine), receipt verified | verifier exits 0 |
| 17th, by 09:00 | Subphase 05 receipt and gate review | subphase verifier exits 0 with `--gate-review` |
| 17th, by 13:00 | P15-19 exit study E0 to E4 on the frozen entries, receipt; subphase 06 receipt and review | verifier exits 0 |
| 17th, by 18:00 | P15-20 release: retention set with statuses and first attributions, selected-rule manifests per fold, phase receipt | phase verifier exits 0 |
| 17th, by 21:00 | Fresh phase-level review, PHASE_GATE_REVIEW, foundation suite rerun on the bound receipts, wiki status and log, merge and worktree removal | Phase 1.5 closed |

Slack is about three hours before midnight. What consumes slack: a repair loop on any receipt (each costs about an hour), an OOM (worker budget is now 17 × 2.5 GB under 70 GB with nothing else heavy), or a research surprise in P15-18 that changes a disposition (allowed and recorded; it does not change the schedule). Phase 2 starts on the 18th on the re-cut cards.

## 7. Status of the cleanup edits

Landed on main on 2026-09-16 evening, each with a chained amendment: pass 1 (ebe9e7dc, `amendment-2026-09-16-plan-cleanup-1`): retirement notices, WORKFLOW trim, roadmap and README pointers, open Phase 1.5 cards; pass 2 (696deaa7, `plan-cleanup-2-phase-2-recut`): Phase 2 re-cut to 16 tasks on the template; pass 3 (f15c7b2d, `plan-cleanup-3-phase-1-5-open-tasks`): open Phase 1.5 tasks read HOW_TO_RUN.md, S01 to S03 assigned once, bundle tools retired. Remaining: the wiki catch-up at the P15-16A closure and the guard test extension for the new process pages.

## 7a. Original order of the cleanup edits

1. Tonight, after the P15-16A receipt verifies (so no verifier run races the edits): retirement notices, `TASK_GRAPH.json` reads, `WORKFLOW.md` trim, phase READMEs and `ROADMAP.md` pointers, `ASSURANCE_CASES.json` assignments and the regenerated `SILENT_FAILURES.md`, the open Phase 1.5 cards thinned; one chained amendment listing every changed file with its hashes; the guard test extended to keep `HOW_TO_RUN.md` and `TASK_CARD_TEMPLATE.md` chained.
2. On the 17th, while the runs execute: the fourteen Phase 2 cards rewritten on the template, `TASK_GRAPH.json` re-cut, a second amendment.
3. Memory and briefs: every future brief cites `HOW_TO_RUN.md` and the card; nothing else is copied into it.
