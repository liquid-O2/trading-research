# Phase 1.5 implementation pack

Status: **specified, not implemented by this planning task**.

Reconstruct missing numerical rules and compare finite, explicitly attributed setup improvements. All Phase 1.5 work must close before Phase 2 implementation.

Start with [copyable prompts](/workspace/planning/phase-1-5/PROMPTS.md). Send the first eligible /poteto-mode new task block to Grok; pstack is already in the user's build. Each coordinator runbook includes its task cards, the [Grok/pstack execution contract](/workspace/planning/research-program/PSTACK_EXECUTION.md) and applicable mathematical/data contracts. Workers additionally read their focused source wiki links.

[Specification](/workspace/planning/phase-1-5/SPEC.md) · [Roadmap](/workspace/planning/ROADMAP.md) · [Execution contract](/workspace/planning/research-program/WORKFLOW.md) · [Machine-readable task graph](/workspace/planning/research-program/TASK_GRAPH.json).

## Subphases

| Order | Subphase/runbook | Tasks | Exit evidence |
| --- | --- | --- | --- |
| 0 | [00-foundation](/workspace/planning/phase-1-5/subphases/00-foundation/RUNBOOK.md) | P15-00, P15-01 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 1 | [01-native-and-outcomes](/workspace/planning/phase-1-5/subphases/01-native-and-outcomes/RUNBOOK.md) | P15-02, P15-03 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 2 | [02-source-reconstruction](/workspace/planning/phase-1-5/subphases/02-source-reconstruction/RUNBOOK.md) | P15-04 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 3 | [03-primitives](/workspace/planning/phase-1-5/subphases/03-primitives/RUNBOOK.md) | P15-05, P15-06, P15-07, P15-08 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 4 | [04-family-adapters](/workspace/planning/phase-1-5/subphases/04-family-adapters/RUNBOOK.md) | P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 5 | [05-finite-search](/workspace/planning/phase-1-5/subphases/05-finite-search/RUNBOOK.md) | P15-17, P15-18 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 6 | [06-exit-controls](/workspace/planning/phase-1-5/subphases/06-exit-controls/RUNBOOK.md) | P15-19 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |
| 7 | [07-release](/workspace/planning/phase-1-5/subphases/07-release/RUNBOOK.md) | P15-20 | Verified task receipts + SUBPHASE_RECEIPT.json + passing GATE_REVIEW.json |

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
