# How to run a subphase

This page replaces `PSTACK_EXECUTION.md`, the generated subphase runbooks and the copyable prompt blocks. It adds nothing to the scientific contracts; it says how one owner takes a subphase from its cards to a verified receipt. Workspace policy is `AGENTS.md`.

## Before starting

1. Read `AGENTS.md`, the subphase's task cards, and only the contracts the cards name (usually `SEARCH_CONTRACT.md`, `EVALUATION.md`, `OUTCOMES.md`, `DATA_CONTRACTS.md`, `PERFORMANCE.md`, `ASSURANCE.md`).
2. Verify the predecessor receipts named by the cards with `tools/verify_research_release.py task --receipt <path>`; note their hashes. Work starts from verified state, never from a summary.
3. State the exit predicate in one sentence: which artifacts exist, which command exits 0 on which receipt. It is not relaxed later.
4. Budget the run: measure one session's runtime and peak RSS, read the cgroup limits (`/sys/fs/cgroup/memory/memory.limit_in_bytes`, `cpu.cfs_quota_us`), and choose workers so that workers × peak RSS plus concurrent processes stay under 70 GB.

## Doing the work

5. One owner per subphase with exclusive write ownership of the card's paths; at most one additional implementation worker, on clearly separated paths, when the user asks for it. A fresh reviewer only when authorized.
6. Build one vertical slice first: the smallest end-to-end path through load, compute, evidence write, with one sensitive positive case and one negative control taken from the contract's worked example or an independent reference. Then the declared native slice, then the full run.
7. Keep computation separate from loading, scheduling and evidence writing. Never turn a missing input or an unexpected error into a success; record it with its reason.
8. Checkpoint completed work; resume from checkpoints; distinguish infrastructure failures (OOM, broken pool, cache write blocked) from research failures (no native view, unsupported cell) in the run's failure records.
9. Tests: the primitive's parity against its plain reference, the sensitive behaviour test with its negative control, the reconciliation test, and the assigned research cases. Nothing that only re-tests the shared verifier; cite its bound evidence instead.
10. Keep a decision trail as you go: one line per decision in the attempt's `WORK_LOG.md` with the artifact or command that proves it. Resume from it after any interruption; never redo verified work.

## Closing

11. Produce the receipt with the task's producer tool (PLAN_SNAPSHOT, CODE_SNAPSHOT, DRAFT_MANIFEST, EVIDENCE_MATRIX, WORK_LOG, DECISIONS, REPORT, TASK_RECEIPT). Every EVIDENCE_MATRIX row binds to the test node or audit command that proves it.
12. Run the verifier on the actual receipt; then the independent probes stage; fix causes, not symptoms, and re-run only the affected checks.
13. The subphase owner writes `SUBPHASE_RECEIPT.json` and `GATE_REVIEW.json` after the task receipts are immutable; a fresh reviewer writes the phase-level review at phase closure.
14. Merge accepted work into main, remove the merged worktree, update `wiki/current-status.md` and `wiki/log.md`, and print the PHASE and audit tables for any family result.

## Handing off or pausing

State where you stopped, what is on disk versus still in your head, the commits made, whether the tree is clean, and the first action on resume. Point at artifacts; do not restate them.
