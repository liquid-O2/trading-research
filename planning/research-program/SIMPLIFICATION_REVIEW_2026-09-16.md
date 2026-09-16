# Plan simplification review, 2026-09-16

Requested by the user after the P15-17 take-over: find where the program has become more convoluted than its goal needs, propose fewer steps without giving up any scientific requirement or acceptance gate, and say what the wiki must catch up on. This is a review with recommendations; it changes no contract by itself. Every recommendation that alters a frozen plan input goes through a chained entry in `AMENDMENTS.json` after the user's decision.

## What the goal actually needs

The roadmap's objective is an adaptive NQ decision process built in phases: better individual rules (1.5), context and forecasts (2), locations (3), response and entry (4). The scientific core that makes any of this trustworthy is small and good:

- `SEARCH_CONTRACT.md` (65 lines): one-axis candidates, a finite bank of at most 160, refinement neighbourhoods, the trial ledger, failure attribution.
- `EVALUATION.md` (53): chronological outer years, inner fit/tune/calibrate, Holm, the block bootstrap, support floors, promotion gates.
- `OUTCOMES.md`, `RETENTION.md` (19), `DATA_CONTRACTS.md` (149): the benchmark, nothing discarded, availability clocks on every record.
- `PERFORMANCE.md` (46): the parity protocol and worker budgeting.
- The source-fidelity baseline B0.2 with its plausibility gate, and the wiki method pages with their re-read source predicates.

That is roughly 400 lines. Nothing below proposes to change a formula, a budget, a gate, a split, a seed, the bank, or the retention rules.

## Where the weight is

1. **Acceptance machinery per task, not per unit of work.** Every one of the 47 tasks must produce seven common artifacts plus its receipt, resolve 8 to 14 acceptance keys and about ten assigned silent-failure probes, and pass a 2,931-line verifier with recursive predecessor admission. The machinery is sound, but the count is the cost: P15-00 has seven receipt attempts, P15-01 six, P15-16A six. Today the P15-16A closure was blocked for most of the day by receipt production and re-verification, not by research. Verifying one receipt took one to five hours until the round-2 memoisation.
2. **Tasks cut finer than the work.** Subphase 04 is eight per-family adapter cards (P15-09 to P15-16) that share one engine and were in practice built as parallel tracks and integrated once, in P15-16A. Phase 2 repeats the pattern with eight per-method expert cards (P2-13 to P2-20) that `METHOD_EXPERTS.md` already defines as one common engine with a per-method configuration table. Each extra card is another receipt, review and verification.
3. **A process framework layered on a process framework.** `PSTACK_EXECUTION.md` (101 lines), the generated subphase RUNBOOKs that embed it again, `PROMPTS.md` (170 lines), the "Copyable worker prompt" in every card, the model role tables and the poteto router with 23 playbooks. The rewritten `AGENTS.md` says these are replaced. Today an agent picking up P15-17 is told to read ten documents (about 1,500 lines) before its 117-line card, and half of those pages restate each other.
4. **Test volume driven by the assurance cases rather than by behaviour.** 675 test functions over 13,178 lines. `test_p15_01.py` alone is 2,071 lines; the P15-16A family files carry 167 tests. Cases S01 to S04 (receipt forgery, plan and code identity) are assigned to every task, so every task re-probes the shared verifier. `SILENT_FAILURES.md` already permits reuse of bound shared evidence, but the assignment table makes duplication the default.
5. **Documentation redundancy.** README, SPEC, contract, task card, RUNBOOK and PROMPT say overlapping things; each 118-line card carries the same eight boilerplate paragraphs.

The pstack and mattpocock material the user pointed at argues the opposite of what we built around them: small composable skills, one short playbook per situation with a finish condition, "minimise reader load", "subtract before you add", and "build the lever" (a tool the reviewer reruns instead of prose). We copied the router and role tables into every runbook, which is the anti-pattern those repositories warn about.

## Recommendations, in order of payoff and risk

R1. **Retire the pstack layer now** (no verifier change, no science change). Remove the "Read first" pointers to `PSTACK_EXECUTION.md`, stop generating RUNBOOK bundles and copyable prompts, and replace `PSTACK_EXECUTION.md` and the prompt blocks with one 40-line page, "How to run a subphase": read `AGENTS.md`, the subphase's cards, the five contracts above; implement one vertical slice with a negative case; run the declared slice, then the full run; produce the receipt with the producer tool; verify. Cards' read lists shrink from ten documents to four. Keep the two tools (`build_research_plan_bundles.py`, `check_research_plan.py`) only if they still check something the guard test and the verifier do not.

R2. **Re-cut the remaining tasks so one task is one unit of work with one owner.** Phase 1.5 keeps P15-17, P15-18, P15-19, P15-20 as they are; they are distinct stages. Phase 2 goes from 25 cards to 14: merge P2-13 to P2-20 into one "method context experts" task with a per-method section and the same acceptance keys; merge P2-05/P2-06 and P2-07/P2-08 into two mechanism tasks that share the fitting engine of P2-02; keep P2-00 to P2-04, P2-09 to P2-12 (P2-03, P2-09 and P2-10 already have staged receipts), P2-21 to P2-24. Receipts, reviews and verifications fall by eleven. The subphases and their gates do not change.

R3. **Assign S01 to S04 once.** They belong to the verifier's owner (P15-01, closed) and the two phase closures (P15-20, P2-24). Every other task cites the bound shared evidence, which the contract already allows. This removes four probes from roughly forty tasks without weakening any check, because the check is on the shared verifier, which does not change per task.

R4. **Thin the card template.** Keep Goal, Inputs (predecessor receipts), Owned paths, Steps, Acceptance (the behavioural keys), Artifacts, Commands. Drop the paragraphs now stated once in `AGENTS.md` and `ASSURANCE.md`. About 118 lines becomes about 50 without losing a requirement.

R5. **Test economy going forward** (already policy in `AGENTS.md`): a new task's tests are the primitive parity against its plain reference, one sensitive native-slice behaviour test with a negative control, the reconciliation test, and the assigned research cases. Existing passing tests stay; they are evidence. No new receipt-mutation tests outside the verifier's own suite.

R6. **Keep the verifier as it is.** The recursive admission, plan-drift chain and successor rule are what caught the false completions on 2026-09-14 and 2026-09-15. Its cost problem was verification time, which the round-2 index and memos fixed. Do not spend effort re-cutting it to subphase granularity; R2 achieves most of the reduction with plan edits only.

What is deliberately left alone: the finite bank, the folds, the gates, the retention rules, B0.2 and the plausibility gate, the parity protocol, the per-record availability clocks, and the wiki's method pages.

## Wiki catch-up needed

`current-status.md` still leads with the P15-16A repair merge of the morning and does not record the P15-17 fast engine (168 s to 15 s per session, byte-identical on 75 dates), the completed rehearsal run, the two OOM-killed runs and the 77.3 GB container limit, the runner's per-session cache release, or the `AGENTS.md` rewrite and its amendments. Its 30-line B0.1 census table belongs in a linked report page. `index.md` and `research-architecture.md` still describe Phase 1.5 as "specified" although five of eight subphases are closed. `log.md` is current to the calendar amendment. The status page needs a short progress table (subphase, status, receipt) at the top. These updates are written by the orchestrator at the P15-16A closure, so the page reflects a verified state rather than an in-flight one.

## Estimated timeline from 2026-09-16 19:00Z

Labelled as projections. They assume no further repair loops and the R1 to R4 changes applied to Phase 2 before it starts.

| Milestone | Projection |
| --- | --- |
| P15-16A receipt verified and closed | 2026-09-16, 21:00 to 23:00Z (blocked on the receipt production now running; verification about 30 minutes after it) |
| P15-17 definitive run (about 30 minutes at 17 workers), fold evaluation, receipt | 2026-09-17 morning |
| P15-18 refinement (at most 24 neighbours per family on the fast engine) and P15-19 exit study | 2026-09-17 afternoon |
| P15-20 release, gate review, Phase 1.5 closure | 2026-09-18 |
| Phase 2 (14 tasks after R2, fitting runs dominate) | start 2026-09-18, close about 2026-09-23 to 24 |

Without R1 to R4, Phase 2's per-task receipt and review overhead alone adds two to three days.
