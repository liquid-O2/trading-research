# Workspace working rules

## Must-follow rules

- Finish the requested behavior and its required verification. Use the existing task requirements to define completion. Resolve routine implementation choices independently.
- Before an expensive full run, verify a small representative end-to-end case, including a meaningful negative case. Check that expected work and output identities are complete.
- Add tests only for distinct behavior, a plausible regression, or a required contract not already covered. Extend existing tests where possible. Skip redundant and low-value tests.
- Avoid tautological tests. Expected results must come from the requirement, a worked example, or an independent reference. Exercise real behavior; source strings, self-reported flags, and mocks of the behavior under test are insufficient evidence.
- For defects, reproduce the reported failure when practical, identify the underlying cause, and check adjacent cases governed by the same rule. Preserve the original acceptance criteria.
- Review the actual change against the original requirements. Consolidate relevant findings into one repair pass. Separate correctness defects from optional cleanup and new scope.
- Run targeted checks during development and required broader checks when ready. Repeat or expand checks only for changed code, failures, or a specific unresolved risk. Missing required evidence remains incomplete; it is never a silent pass.
- Measure performance on comparable inputs and conditions, including loading, computation, output, and verification. Reuse valid completed work. Label projections as projections.
- Keep one main owner. Use additional agents only when requested for clearly separated work. Integrate accepted work regularly; remove only task-owned worktrees whose work is safely merged.
- Read the files and skills relevant to the current task. Keep persistent instructions short and authoritative in one place. Use concise progress updates and completion notifications instead of repeated polling.

## Code quality and delivery

- Share logic when it represents the same rule; preserve intentional differences.
- Keep computation separate from data loading, scheduling, and evidence writing.
- Never turn unexpected errors or missing required inputs into successful outcomes.
- Test observable behavior using independent expectations; each test must catch a distinct plausible defect.
- Review the actual candidate, including relevant uncommitted files. Reproduce findings and inspect sibling paths for the same cause.
- Fix the cause across affected paths, then rerun affected checks and required acceptance checks. Reopen review for changed behavior or concrete unresolved risk.
- Measure runtime and peak memory before scaling a run.
- Merge accepted work and remove its fully merged worktree; preserve active work and historical evidence.

These rules replace legacy model routing, mandatory agent panels, and playbook-copying instructions in workspace workflow documents. Preserve their scientific requirements and acceptance gates. Later explicit user instructions take precedence.

## Find the relevant context

Repository: `/workspace` (`liquid-O2/trading-research`). Implementation: `implementation/`, Python package `trading_research`.

- For phase selection, read `planning/ROADMAP.md`. For current progress, inspect `wiki/current-status.md` and its linked receipts; reconcile stale status prose against accepted evidence before restarting work.
- Before implementing a research task, read its selected task card and referenced contract sections. Packs: `planning/phase-1-live/`, `planning/phase-1-5/`, `planning/phase-2/`. Consult `wiki/` for the relevant shared reference.
- For research acceptance, follow `planning/research-program/ASSURANCE.md`. For Phase 1 object execution, use `implementation/tools/run_phase1_objects.py`; other tasks use their pack's runner.

## Research and execution safeguards

- Before population runs, check native positive and negative cases, causal timing, and missing/invalid inputs where applicable. Synthetic fixtures cannot substitute for required native coverage.
- For acceptance, follow the assurance contract: trace native output, independently recalculate a central result, and reconcile declared jobs with unique artifacts and terminal dispositions. Test verifiers with valid controls and plausible invalid claims; assert the intended rejection reason.
- For semantic or acceptance-critical changes, perform a separate bounded review pass. Read requirements and actual code/artifacts before the author's summary, including relevant untracked files. Use a fresh reviewer when authorized; otherwise state the limitation of self-review. Model agreement alone is not independent evidence.
- If a failure survives repair, revisit the premise before patching again. Blocking defects remain blockers; moving them to another phase or changing thresholds does not resolve them. Equivalence to an old implementation proves preservation, not scientific validity.
- Reuse evidence only while its code, inputs, and contracts remain valid and acceptance rules permit. Revalidate changed dependencies; keep cached parsing separate from fresh integrity checks.
- Parameterize tests for the same rule. Avoid duplicating type-checker guarantees; validate external data at its boundary. Keep call-count assertions for explicit resource bounds. Retire obsolete tests once replacement coverage protects their behavior. Isolate test outputs from research evidence and native data; skipped required coverage leaves acceptance incomplete.
- Turn recurring mechanical errors into shared helpers, invariants, or automated checks. Prefer small interfaces and existing canonical helpers; introduce abstractions for demonstrated variation. Tie cleanup to removed complexity or safer changes, rather than cosmetic uniformity or file length.
- Profile before optimizing. Include cold/warm conditions, worker count, and container limits in measurements. Eliminate repeated work where correctness permits and define cache invalidation. Apply vectorization or Numba to measured compatible hotspots and verify semantics.
- Budget workers against CPU, measured peak memory, and concurrent workloads. Checkpoint completed work, distinguish infrastructure failures from research failures, and reconcile state on retry.
- When delegation is requested, default to at most one additional implementation worker unless more are requested. Give it exclusive write ownership. Avoid manager chains; judge models by time and cost to accepted correctness, including repairs. Use the selected capable model for semantic work and cheaper models only for bounded mechanical work with established checks.
- Batch independent reads. For long tasks, retain compact state: decisions, candidate identity, evidence paths, blockers, and exact next action. Resume from verified state after compaction. Verify configuration support in the running executable; a configuration entry alone does not prove activation.
- Git operations belong to this repository and its worktrees. After family reports, print both tables:
  - PHASE: `family | variant | n | faithful_disagreements | status | report path`
  - Audit: `family | id | verdict | fixture | leakage | proxy-as-faithful | notes`

## Preserve data and evidence

- Keep `planning/phase-1-from-scratch/`, `planning/phase-1-fable/`, `archive/`, and `sources/` read-only. Archived mill-era and Cursor-handoff instructions are historical, not active workflow.
- Keep `/workspace/data` on disk and excluded from Git; never commit it.
- Preserve accepted reports and historical snapshots. Write new evidence into new run directories. Generate future task bundles from canonical sources; do not rewrite old snapshots or identities to make acceptance pass.
- Keep shared operating policy here. Maintain task-specific detail in its canonical contract; other instruction files should reference it rather than copy it. Treat instruction changes as changes to future plan inputs while preserving historical evidence identities.
