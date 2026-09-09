# Cursor implementation workflow — current

**Active task (user direction September 8, 20:41 UTC): complete Deliverable 1 across all intended families—definitions, measurement validation, statistics, timing and window links—then Context.** Source performance repair is accepted. Reuse the complete 3,589-window receipt catalog; do not rerun source extraction. Current work builds complete-population auction/flow observation tables and enables the separately scoped Jumbo descriptive confirmation. The family table below remains the full validation queue. Context and Location evaluation remain later.


Read [the durable project entry point](/workspace/planning/trading-research/START_HERE.md) first. It links the full plan, every family/child definition, accepted results, pending work and exact budgets. This file is the operational guide for Cursor; it does not establish a competing research plan.

**Current state:** **Source timestamp repair is complete and verified.** Run 36 succeeded for **all 3,589 source/date windows across 167 physical files**, with **zero failed or pending windows**. It reused 3,550 windows and completed the final 39 in **9.16 minutes**. All original timestamps, source fields and rows remain unchanged. Four short timing-uncertainty spans are explicit and excluded from exact duration claims; physical state and later carry continue. Verification ran 154 tests: 152 passed, zero failures/errors and two pre-existing optional-backend skips. All 167 carry chains reconcile. The complete receipt catalog is linked in the [verified result](/workspace/trading-research/reports/auction-flow-reset-clock-repair36-review.md). There are no active workers. The family has used **36/36 authorized attempts, 71,701.255619/192,000 CPU-seconds and 55,928,815,964 bytes of 256 GiB**. Earlier failures, budgets and the exceeded 20:11 cutoff remain recorded. Complete scientific research and full-pipeline three-hour timing are not claimed.

## Ownership and selected model

The user selected **Cursor Grok 4.6 Extra High Fast**, CLI ID **`cursor-grok-4.6-xhigh-fast`**. Codex owns scientific definitions, task selection, performance diagnosis, independent review, integration, registered execution and acceptance. Cursor implements a coherent bounded assignment in an isolated checkout. Its completion message is not verification evidence. Do not substitute another worker model silently.

The launcher is [run_worker.py](run_worker.py). It records the exact assignment bytes/hash, requested and reported model, workspace, process, session ID, timeout, structured events, stderr and completion result under [runs](runs). It does not integrate code or act as an autonomous controller. A saved handoff does not keep an agent working after a task ends.

## Where everything lives

| Location | Role |
|---|---|
| `/workspace/planning/trading-research/START_HERE.md` | Single continuation entry point |
| `/workspace/planning/trading-research/PLAN.md` and `RESEARCH_SPEC.md` | Complete current research scope and science |
| `/workspace/planning/trading-research/UNIT_CATALOG.md` | All 153 parents and 191 refinements, with exact source/case/improvement links |
| `/workspace/planning/trading-research/STATUS.md` and `state/CURRENT.json` | Actual completion, pending work, budgets and receipts |
| `/workspace/trading-research` | Canonical implementation and immutable research evidence |
| `worktrees/` | Isolated worker checkouts; many are stale or unverified |
| `runs/` | Exact prior worker assignments, session logs and outcomes |
| `*-integration.json`, `*-checkpoint.json`, backup directories | Specific historical integration/source hashes and preserved originals |
| `/workspace/planning/trading-research/state/DEPENDENCIES.json` | Current exact accepted refs and all important unverified drafts |

## Prepare one bounded assignment

Choose one concrete pending requirement after reading the current family specification and status. Reuse existing interfaces, data and evidence. Do not send the entire catalogue as one unconstrained worker task, create a new architecture project, or restart the old P0–P7/E0 program.

Refresh only the assigned baseline files in an isolated checkout under `worktrees/`, comparing canonical hashes and preserving worker changes first. Never copy an old checkout wholesale over current source. Checkouts contain their own local history and can predate the C++/NumPy/dependency fixes. Canonical source remains authoritative.

Write an assignment file that includes this block, filled with concrete values:

```text
Goal and why it is needed for the next actual research result:
Deliverable boundary and downstream step it enables:
Relevant family / parent / refinement IDs:
Read first: /workspace/planning/trading-research/START_HERE.md
Exact source definitions, cases, accepted receipts and input files to read:
Canonical baseline and SHA-256 of each file being changed:
Isolated workspace and the only files allowed to change:
Required interfaces, types, units, clocks, state/carry and bounds:
Actual algorithm and required source/definition alternatives:
Independent expected cases and exact acceptance criteria:
Performance/memory/output requirement and measured bottleneck, if relevant:
Accepted unchanged evidence to reuse; unresolved decisions this assignment must resolve:
No research execution: supervisor uses the existing registered family runner.
Stop condition and concrete artifacts to return:
Wall-time allowance and no unsolicited scope expansion:
```

Use full absolute read paths. A worker must have enough source/science context to implement the actual method. A toy substitute, weaker proxy, omitted sibling or new hidden semantic assumption is not acceptable.

## Permissions and launch

Each editable workspace requires `.cursor/cli.json`. Grant Read access to the assignment, current planning bundle, selected canonical reference files and its own checkout. Grant Write only to the listed implementation/test files. Retain denial of Shell execution, network/MCP, raw data changes, canonical code writes, planning writes, `.git`, `.cursor`, frozen references/protocols and unrelated files. Do not reuse stale allow-lists from an earlier assignment.

The root [.cursor/cli.json](.cursor/cli.json) supports read-only coordination. The host previously could not start Cursor's OS sandbox, so the existing launcher uses Cursor's documented permission mode with `--sandbox disabled`; project permissions remain enabled. Do not broaden permissions or change global authentication/sandbox settings as part of ordinary implementation.

Read-only onboarding or investigation:

```bash
python /workspace/coordination/trading-research-cursor/run_worker.py /absolute/path/to/assignment.md --workspace /workspace/coordination/trading-research-cursor --timeout 600
```

Bounded implementation in a prepared isolated checkout:

```bash
python /workspace/coordination/trading-research-cursor/run_worker.py /absolute/path/to/assignment.md --workspace /workspace/coordination/trading-research-cursor/worktrees/CHOSEN_CHECKOUT --edit --timeout 1800
```

Explicitly resuming the same unfinished assignment, only after checking current scope and prior outcome:

```bash
python /workspace/coordination/trading-research-cursor/run_worker.py /absolute/path/to/assignment.md --workspace /workspace/coordination/trading-research-cursor/worktrees/CHOSEN_CHECKOUT --edit --resume RETAINED_SESSION_ID --timeout 900
```

These are templates, not instructions to launch a job during consolidation. `--edit` requires an isolated path under `worktrees/`; otherwise the launcher uses ask mode. It saves a new run record for each invocation. A timeout/failure stays recorded. Do not pretend a stopped worker finished or infer acceptance from its exit code.

## Review, integrate, execute, accept

1. Read the actual complete diff and compare it with the brief and exact scientific definition. Check source/clock/identity/carry semantics and performance structure. Reuse unchanged verified evidence.
2. Consolidate defects once. The latest user instruction rejects repeated worker review/repair loops. Make a necessary direct correction or give one coherent correction when it is clearly more efficient; do not start serial unbounded repair rounds.
3. Recheck canonical baseline hashes. Preserve the pre-change canonical files in a recorded backup, then integrate only the intended reviewed files. Record before/worker/after hashes and any direct changes. Do not integrate worker reports as test results.
4. Run the relevant consolidated checks and actual-data study through its **existing registered family runner**, preserving the live attempts, CPU and output limits. No direct pytest, unregistered candidate import, benchmark, scan or fit bypass is allowed. For new scientific questions, use an honest distinct bounded registration, not a renamed exhausted workload.
5. Join the runner's immutable receipt, source/runtime identity, actual comparisons and resource accounting. Accept only the scope actually verified. Preserve all failed attempts. A fixture, resource probe or source parity run is not a completed empirical family.
6. Update the planning STATUS/CURRENT state and this directory's state.json. Proceed to the next authorized research work without requiring the user to babysit every intermediate step.

Existing auction runner: `/workspace/trading-research/tools/run_auction_flow_study.py` supports `check`, `profile`, `compute`, `benchmark`, `downstream`, and `throughput`. Latest executed extension V20 and production plan V2 are bound in CURRENT.json to verification31. All 31 consumed attempts and original CPU/output budgets remain charged. Do not resume historical V16 holdout or controller assignments merely because their files remain present.

Benchmark23passed121tests, all9source comparisons and3continuation replays. Downstream20passed70tests and reproduced18complete anchor/cohort payloads in130.973elapsed seconds using accepted source/trade artifacts. [Exact current performance](/workspace/trading-research/reports/auction-flow-performance23-review.md). The source allowance is152,641.745CPU seconds /261.16GB; a separately frozen quote dual-count recalibration134,722.304CPU seconds awaits the17-window holdout. Full under-three-hour end-to-end feasibility is not established.

No Cursor worker is currently active. Quote replay run20260908T144921Z-8398c571 and fusion run20260908T150342Z-ab015305 completed; exact owned files plus documented Codex corrections were integrated and accepted by23. Failed21 and deliberately stopped22 remain charged. Attempt 25 retained 12 completed units and five clock failures but failed its coordinator summary; audit 26 retained original all-field neighbors and receipt identities. The 17-window holdout has not passed. Reuse retained evidence and consult CURRENT.json for the next acceptance conditions.

## Drafts that must not be mistaken for accepted work

- The deferred Jumbo prediction-reuse draft is in `worktrees/implementation`, recorded by `jumbo-prediction-integration.json` and its worker run. Its four original canonical files were restored. Known review defects: same-object feature/group mutation can escape the cache key; model identity is recomputed redundantly; oversized prediction arrays are copied before capacity rejection. No model fit/acceptance occurred.
- `src/trading_research/research/auction_flow_book_recovery.py`, `auction_flow_structure.py` and `auction_flow_memory.py`, plus corresponding tests, are canonical **unverified drafts**. They were not included in the latest focused source benchmark's verified import/test closure. Their integration JSONs record exact origins and direct corrections.
- `worktrees/auction-book-probe` and `worktrees/auction-structure-memory` contain stopped, incomplete actual-source comparison probes. Retain their source contracts, logs and partial code. Do not resume the workers automatically or mark these probes passed.
- `paused-v5-wiring`, `check10-wiring-before`, earlier accepted canonical backups and the original efficiency baseline are preserved recovery material. V5 is historical; the latest executed extension is V20.

The complete earlier accumulating handoff is preserved at `/workspace/planning/trading-research/history/2026-09-08-consolidation/coordination/HANDOFF.md`. It explains historical events but its statements about “currently running” jobs are superseded by the state above.
