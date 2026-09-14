# Shared research contracts

These are specifications for future implementation. Proposed Python symbols and commands below do not exist merely because they are documented here. Task cards identify which task creates each one.

| Contract | Purpose |
| --- | --- |
| [Workflow](WORKFLOW.md) | Coordinator/worker responsibilities, task receipts, gates and stopping rules. |
| [Grok/pstack execution](PSTACK_EXECUTION.md) | `/poteto-mode` routing, role overrides, bounded worker prompts, resuming and independent review. |
| [Evidence and failure checks](ASSURANCE.md) | Required evidence matrix, strict identity/artifact/dependency verification, native coverage and independent closure for every subphase. |
| [Silent failure cases](SILENT_FAILURES.md) | 32 concrete probes and expected results assigned across all 46 tasks by [machine-readable registry](ASSURANCE_CASES.json). |
| [Foundation repair](FOUNDATION_REPAIR.md) | Current entry: reproduce and repair the rejected 00-foundation completion; preserve old evidence. |
| [Acceptance amendments](AMENDMENTS.json) | Explicit version/supersession history; old foundation receipts cannot waive the new checks. |
| [Data and clocks](DATA_CONTRACTS.md) | Event identity, availability, coverage, sessions, options and schemas. |
| [Type declaration blueprint](TYPE_REFERENCE.py) | Complete native/rule/expert declarations for the schema-owner tasks; numerical behavior is specified separately. |
| [Evaluation](EVALUATION.md) | Nested chronological experiments, trial accounting, selection and economic diagnostics. |
| [Outcomes](OUTCOMES.md) | Ordered targets/stops, opportunity labels, fixed execution benchmark and unchanged-entry exits. |
| [Model fitting](MODEL_FITTING.md) | Exact preprocessing, estimators, losses, calibration and uncertainty. |
| [Scope audit](SCOPE_AUDIT.md) | Recovered requirements and explicit phase/task dispositions. |
| [Method review](METHOD_REVIEW.md) | Matt and pstack workflow synthesis, pinned review inventory and adaptations. |

Every task also obeys [workspace rules](/workspace/AGENTS.md) and the [roadmap](/workspace/planning/ROADMAP.md). Definitions live in the [wiki](/workspace/wiki/index.md); these files define executable research policy.
