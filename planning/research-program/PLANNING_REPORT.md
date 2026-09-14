# Implementation-pack handoff

The Phase 1.5 and Phase 2 implementation packs are drafted. They incorporate the user's accepted scope, the completed Phase 1 evidence, the older conversation gaps, and the reviewed Matt/pstack workflows. This work created specifications and documentation tools; it did not run Phase 1.5/2 research experiments or modify the accepted implementation/report files.

| Pack | Size and start point |
| --- | --- |
| Phase 1.5 |21 bounded tasks in8 subphases. Start with [the first coordinator prompt](/workspace/planning/phase-1-5/PROMPTS.md#00-foundation). |
| Phase 2 |25 bounded tasks in9 subphases. [Prompts](/workspace/planning/phase-2/PROMPTS.md) become executable after the complete Phase 1.5 release gate. |
| Shared contracts | [Data/types](/workspace/planning/research-program/DATA_CONTRACTS.md), [declaration blueprint](/workspace/planning/research-program/TYPE_REFERENCE.py), [evaluation](/workspace/planning/research-program/EVALUATION.md), [outcomes](/workspace/planning/research-program/OUTCOMES.md), [fitting](/workspace/planning/research-program/MODEL_FITTING.md) and13 [reference vectors](/workspace/planning/research-program/fixtures/reference_vectors.json). |
| Execution | [Workflow](/workspace/planning/research-program/WORKFLOW.md), [46-task graph](/workspace/planning/research-program/TASK_GRAPH.json),17 generated coordinator runbooks and task-specific worker prompts. |
| Grok with pstack | [Execution contract](/workspace/planning/research-program/PSTACK_EXECUTION.md), `/poteto-mode new task` entrypoints, all-role Grok inheritance, bounded briefs and resume/review/repair/pause prompts. |

The packs fix formulas, units, function/type contracts, candidate/model budgets, training/calibration clocks, source/operational distinctions, native input gates, numerical and causal checks, output receipts, completion criteria and downstream handoffs. Per-method context experts and intraday OI/IV/volatility work are explicitly included. Unknown proprietary definitions, sparse branches and missing native inputs have bounded, honest dispositions; the implementer is not required to invent a winner.

## Documentation verification

The [documentation check receipt](/workspace/planning/research-program/DOCUMENTATION_CHECK.json) records graph/dependency validation, task acceptance keys and ownership, required reads, generated-file freshness, local paths/anchors, type-reference syntax, reference-vector checks, wiki compatibility and documentation-only authoring scope.

The [wiki migration audit](/workspace/planning/research-program/WIKI_MIGRATION_AUDIT.json) maps all191 original pages to `/workspace/wiki`, records before/after hashes and verifies all12 method source-definition cores were preserved. The old phase-local wiki path is a symlink to the same files. Current wiki/README/Phase1 status now points to the completed acquired census; historical versioned reports and frozen manifests remain unchanged.

The [scope audit](/workspace/planning/research-program/SCOPE_AUDIT.md) maps recovered requirements to tasks or explicitly reserved later phases. The [workflow review](/workspace/planning/research-program/METHOD_REVIEW.md) and [237-file pinned inventory](/workspace/planning/research-program/METHOD_REVIEW_INVENTORY.tsv) record 87 fully read skill entrypoints, 31 playbooks, the full pstack guide/index and the distinction between fully read and selectively reviewed supporting material.

Reproduce the documentation checks from `/workspace`:

```bash
python tools/build_research_plan_bundles.py --check
python tools/check_research_plan.py --authoring-scope
git diff --check
```

`--authoring-scope` applies to this documentation-only change. During later implementation, use the checker without that flag and use the future research release verifier for implementation evidence. The recorded Phase1 suite/census results remain existing evidence; they were not rerun for this documentation update.

## Start execution

Send the first Phase 1.5 prompt, including its opening `/poteto-mode new task`, to a Grok task. The coordinator reads its runbook, verifies the accepted baseline and executes only that subphase. The installed router selects the matching workflow; the included project contract keeps every role on Grok and limits shared-checkout writes. The next subphase starts from verified receipts. Phase 2 remains gated on all of Phase 1.5.

Actual progress belongs in verified execution receipts and the [shared wiki status](/workspace/wiki/current-status.md). These frozen specification cards retain their authoring status; a later empirical or implementation result must not be confused with this planning handoff.
