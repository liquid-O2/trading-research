# Agent operations

How agents are used for this program and why, recorded so a new session does not rediscover it. Policy is [AGENTS.md](/workspace/AGENTS.md); process is [HOW_TO_RUN.md](HOW_TO_RUN.md); the cleanup that produced both is [PLAN_CLEANUP_2026-09-16.md](PLAN_CLEANUP_2026-09-16.md). This page names roles, not products or models; the user selects the model for each role.

## Roles

| Role | Who | Why |
| --- | --- | --- |
| Owner and orchestrator | The main session | Plans, judges, writes canonical prose (wiki, plan pages, amendments), merges, writes subphase receipts and gate reviews, keeps the persistent memory. It does the implementation itself when that is the fastest correct path; the P15-17 engine was taken over and finished in an afternoon. |
| Implementation worker | One worker per subphase, the selected capable model at high effort, in its own worktree, with exclusive write ownership of the card's paths | Delivers complete work; a second worker only for clearly separated paths when the user asks. Cheaper models only for bounded mechanical work with established checks. |
| Verifier | A separate worker with a fresh context, reading requirement and artifacts before the author's report | Independence of context. The report states whether the verifier shares the author's model family; the checks are recomputations, not opinions. |
| Fresh reviewer at phase closure | A reviewer from a different model family when available | Cross-model independence for the phase-level review and for source-fidelity readings of author pages. Not a mandatory panel; used at closure and where a second reading adds real independence. |
| Retired | The previous plugin-routed CLI workflow | Fast but rewarded hacking: incomplete stages passed as measured, bounds fitted to results, commits against the rules. Its skill repositories remain reference material, not workflow. |

## How the sessions behave

Workers run in the background and notify on completion; notifications do not always arrive, so the owner keeps a heartbeat every twenty minutes and event watches (a background loop on a run's completion file, a memory threshold or process death). A worker can be resumed with its context by message, which is cheaper than a fresh brief. Briefs point at files and line ranges and never paste logs or artifacts. Reports are under 70 lines with one evidence pointer per claim. A worker is told the exact measurement protocol and the self-check list before it reports, so there is no verification round trip.

A cross-model review runs in a throwaway root; every output is copied out before the root is removed.

The container is a rented pod: 17.85 cores and 77.3 GB enforced by cgroup, read from `/sys/fs/cgroup`, never from `free` or `nproc`. Two runs were lost to that limit on 2026-09-16; the worker budget and the per-session cache release in the runner are the permanent fix.

## Things that cost days and their fixes

| Cost | Fix now in force |
| --- | --- |
| Verification round trips after each implementation | Self-check list and measurement protocol in the brief; the verifier is a spot check |
| Receipt re-verification taking hours | Receipt index, failure de-duplication and memoised digests in the verifier |
| Unmeasured full runs (plausibility, memory) | Small end-to-end case with a negative control, then measure runtime and peak RSS, then scale |
| Process framework copied into every runbook | One page, HOW_TO_RUN.md; cards on the template; contracts linked, not copied |
| Per-task receipts for one unit of work | Tasks re-cut to one owner per unit of work; assurance cases on the verifier assigned once |
| Reviews repeating the same defect class | Every repeated class gets a permanent automated check |

## Borrowed from the mat and pstack skill repositories

Tracer-bullet tickets with blocking edges and a frontier (mat `to-tickets`); specs as problem, solution, decisions, testing decisions and out-of-scope, without file paths in prose (mat `to-spec`); hand-offs as pointers, not restatements (mat `implement-spec` and its handoff skill); an autonomous run with an exit predicate stated first and never relaxed, plus a wake mechanism (pstack `autonomous-run`); the four-part throughput checkpoint (pstack `feature`); session pickup from the trail with inherited claims verified on the artifact (pstack `session-pickup`); a durable pause (pstack `pause-safely`); subtract before you add, minimise reader load, encode lessons in structure, build the lever (pstack principles). Not borrowed: routers, model role tables, agent panels, PR playbooks.
