# Phase 2 implementation pack

Status: **specified, not implemented by this planning task**.

Build intraday forecasts, native options updates and separately fitted context/method experts. Start only after the verified complete Phase 1.5 release.

Start with [copyable prompts](/workspace/planning/phase-2/PROMPTS.md). Send the first eligible /poteto-mode new task block to Grok; pstack is already in the user's build. Each coordinator runbook includes its task cards, the [Grok/pstack execution contract](/workspace/planning/research-program/PSTACK_EXECUTION.md) and applicable mathematical/data contracts. Workers additionally read their focused source wiki links.

[Specification](/workspace/planning/phase-2/SPEC.md) · [Roadmap](/workspace/planning/ROADMAP.md) · [Execution contract](/workspace/planning/research-program/WORKFLOW.md) · [Machine-readable task graph](/workspace/planning/research-program/TASK_GRAPH.json).

## Subphases

| Order | Subphase/runbook | Tasks | Exit evidence |
| --- | --- | --- | --- |
| 0 | [00-entry-gate](/workspace/.worktrees/docs-amend/planning/phase-2/subphases/00-entry-gate/RUNBOOK.md) | P2-00 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 1 | [01-datasets-and-fitting](/workspace/.worktrees/docs-amend/planning/phase-2/subphases/01-datasets-and-fitting/RUNBOOK.md) | P2-01, P2-02 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 2 | [02-native-options-baseline](/workspace/.worktrees/docs-amend/planning/phase-2/subphases/02-native-options-baseline/RUNBOOK.md) | P2-09, P2-10 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 3 | [03-joint-volatility](/workspace/.worktrees/docs-amend/planning/phase-2/subphases/03-joint-volatility/RUNBOOK.md) | P2-03, P2-04 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 4 | [04-context-mechanisms](/workspace/.worktrees/docs-amend/planning/phase-2/subphases/04-context-mechanisms/RUNBOOK.md) | P2-05, P2-06, P2-07, P2-11, P2-08 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 5 | [05-intraday-oi](/workspace/.worktrees/docs-amend/planning/phase-2/subphases/05-intraday-oi/RUNBOOK.md) | P2-12 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 6 | [06-method-experts](/workspace/.worktrees/docs-amend/planning/phase-2/subphases/06-method-experts/RUNBOOK.md) | P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 7 | [07-plans-and-adaptation](/workspace/.worktrees/docs-amend/planning/phase-2/subphases/07-plans-and-adaptation/RUNBOOK.md) | P2-22, P2-23 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 8 | [08-release](/workspace/.worktrees/docs-amend/planning/phase-2/subphases/08-release/RUNBOOK.md) | P2-24 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |

## Operating rules

One coordinator owns a subphase. Workers get one bounded card and actual predecessor/run artifacts. The pstack router selects supporting skills; all roles inherit the parent Grok model. Default at most three live agents including the coordinator and one code writer per shared checkout. Dependency order governs task execution; shared integration and fresh review belong to the coordinator. Unavailable permitted workers mean sequential execution.

All source-independent thresholds, costs, numerical recipes and search limits are registered research defaults. Preserve baselines, complete no-opportunity days, missing data, ambiguous ordering and unsuccessful trials. Negative or low-support findings can close a correct experiment; missing code or unreconciled runs cannot.

The commands and proposed Python APIs in this pack are implementation requirements. This planning task has not created those research runners or executed their tests/censuses. Every task/subphase obeys ASSURANCE.md and its assigned silent-failure cases. A final release requires receipt verification, fixed independent checks and a matching passing GATE_REVIEW.json, plus both workspace-required family/audit tables.

## Document maintenance

Canonical contracts and task-card requirements are the source of truth. The builder updates coordinator bundles and only the Copyable worker prompt section of each task card. The checker rejects stale prompts or missing pstack routing. From /workspace:

```bash
python tools/build_research_plan_bundles.py
python tools/check_research_plan.py
```
