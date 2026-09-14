# Phase 1.5 — copyable coordinator prompts

These prompts start implementation when you send them. The pack itself is a specification; no task is marked implemented by its creation.

pstack is included in the user's Grok build. Copy the entire block, starting with /poteto-mode new task. No separate setup prompt is required. Send one subphase prompt to one Grok task; complete and verify it before the next.

The user sends one coordinator prompt per subphase (17 subphases across both packs). Worker prompts are internal coordinator dispatch material. Resume/review/repair/pause blocks are alternatives for those situations, not additional prompts the user must send for a normal subphase run.

The [pstack execution contract](/workspace/planning/research-program/PSTACK_EXECUTION.md) defines routing, Grok-only roles, worker briefs, local scope and honest stop rules. Each RUNBOOK includes it. The installed router chooses supporting skills; the prompts do not hard-code a skill chain.

Use one coordinator per subphase. A shared checkout has one code writer at a time; independent read-only work may run alongside it. Keep the same declared data-process parallelism and resource limits.

## Current entry: repair 00-foundation

The 2026-09-14 independent audit rejected the original completion claim. Use this repair block before 01-native-and-outcomes. Preserve the original reports. [Findings and repair instructions](/workspace/.worktrees/docs-amend/planning/research-program/FOUNDATION_REPAIR.md).

```text
/poteto-mode new task. Repair Phase 1.5 subphase 00-foundation in /workspace from its rejected 2026-09-14 review; do not start 01-native-and-outcomes.
Read /workspace/AGENTS.md, /workspace/planning/research-program/FOUNDATION_REPAIR.md and /workspace/planning/phase-1-5/subphases/00-foundation/RUNBOOK.md. Follow PSTACK_EXECUTION.md through the installed pstack router; this is a bounded bug-fix execution of the existing amended specification, not a new planning task. No second go is needed.
Use the parent Grok model for every role. At most three live Grok/poteto agents including the coordinator, no nested worker delegation, and one code writer per shared checkout. The coordinator owns shared integration and a fresh behavior review. Give each worker actual inputs, code identity, owned paths and expected observations. If workers are unavailable, execute sequentially and record the review limitation.
Preserve the original reviewed receipts, reports and Phase 1 code/data identities. Reproduce the supplied counterexamples, then repair their root causes in the P15-00/P15-01 owned code and tests. Enforce required parsed artifacts and actual identity binding, recursive dependency/phase admission, unexcused required command failures, every nested clock/schema boundary, per-input-group coverage/lookbacks and an actual native record replay. The frozen independent checker is outside your edit ownership. Do not patch pass flags, weaken checks, substitute synthetic evidence for native, or suppress missing data to close the task.
Apply ASSURANCE.md and every assigned silent-failure case. Record EVIDENCE_MATRIX.json, measured commands/logs and your own WORK_LOG.md/DECISIONS.tsv. Use new v2 snapshots, manifests, receipts and supersession/exposure records; do not rewrite old plan identities or accepted artifacts. Finalize task receipts before the coordinator candidate, then the independent check result and GATE_REVIEW.json to avoid circular hashes.
Keep going until targeted tests and all assigned checks pass, actual new task/subphase receipts verify, /workspace/tools/check_foundation_adversarial.py passes all 27 controls/counterexamples on the new receipts, and subphase verification with the matching passing --gate-review exits 0. Independently inspect code and outputs; the worker summary, log audit and self-authored verifier alone are insufficient. Return the exact repair, evidence links, unresolved limitations and next eligible prompt. Stop at the foundation boundary. Local work only; no PR/push/merge, external messages, Phase 1 census or Phase 2 implementation.
```

## 00-foundation

```text
/poteto-mode new task. Implement Phase 1.5 subphase 00-foundation in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-1-5/subphases/00-foundation/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (accepted Phase 1 census) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 01-native-and-outcomes

```text
/poteto-mode new task. Implement Phase 1.5 subphase 01-native-and-outcomes in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-1-5/subphases/01-native-and-outcomes/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (00-foundation) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 02-source-reconstruction

```text
/poteto-mode new task. Implement Phase 1.5 subphase 02-source-reconstruction in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-1-5/subphases/02-source-reconstruction/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (01-native-and-outcomes) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 03-primitives

```text
/poteto-mode new task. Implement Phase 1.5 subphase 03-primitives in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-1-5/subphases/03-primitives/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (02-source-reconstruction) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 04-family-adapters

```text
/poteto-mode new task. Implement Phase 1.5 subphase 04-family-adapters in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-1-5/subphases/04-family-adapters/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (03-primitives) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 05-finite-search

```text
/poteto-mode new task. Implement Phase 1.5 subphase 05-finite-search in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-1-5/subphases/05-finite-search/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (04-family-adapters) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 06-exit-controls

```text
/poteto-mode new task. Implement Phase 1.5 subphase 06-exit-controls in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-1-5/subphases/06-exit-controls/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (05-finite-search) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 07-release

```text
/poteto-mode new task. Implement Phase 1.5 subphase 07-release in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-1-5/subphases/07-release/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (06-exit-controls) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## Resume an interrupted subphase

Use this in the existing subphase task. In a fresh task, append the actual RUNBOOK path, run-root path and prior WORK_LOG/receipt paths from its handoff.

```text
/poteto-mode new task. Take over the interrupted subphase and resume from its existing runbook, WORK_LOG.md, decision trail and immutable manifests. Use Session pickup to establish the resume point, then route the remaining work for execution. Read PSTACK_EXECUTION.md from the runbook; keep all roles on the parent Grok model and the same bounded ownership.
Verify inherited artifact hashes and distinguish done from pending using ASSURANCE.md, EVIDENCE_MATRIX.json and the matching GATE_REVIEW.json. Reuse successful shards and retain failed attempts; finish missing work under the same frozen configuration. Do not invent dates, drop slow/negative cases or overwrite reports. Reconcile defects in bounded repairs and rerun affected silent-failure cases. A real contract amendment requires a new plan/run identity and explicit supersession; obsolete receipts cannot authorize downstream work.
Keep going until the existing subphase completion predicate verifies, or return an evidenced incomplete/blocking disposition under its stop rules. Return actual receipts, decision trail and the next eligible prompt. Local scope only; no automatic later phase or shipping.
```

## Independent review prompt

```text
/poteto-mode new task. Review the completed subphase using the RUNBOOK and receipt paths in the supplied completion handoff. This is a read-only investigation. Use /interrogate as the skeptical-review override; do not change implementation or accepted evidence. Read the runbook's PSTACK_EXECUTION contract and keep every review role on the parent Grok model. A fresh same-model review is not cross-model evidence.
Read actual code and artifacts before the author summary. Apply ASSURANCE.md and every task assigned silent-failure case. Reproduce adversarial controls, independently recalculate a central result, trace a native output and inspect EVIDENCE_MATRIX.json. Check attribution, nested availability, actual predictor matrices, native coverage and zero days, trial/job reconciliation, numerical fixtures, recursive dependency hashes and downstream claims. Review maintainability and decision trails separately. Preserve evidence; use isolated temporary outputs and the fixed independent checks where required, including valid controls.
Done means GATE_REVIEW.json under ASSURANCE.md with a pass, issues or blocked verdict bound to actual candidate receipt/code/evidence hashes, covering every task, findings with reproductions and explicit unverified checks. No unresolved correctness/causality/integrity issue may pass. Test counts or attractive charts alone are insufficient. Return the report to the coordinator; no fixes, PRs or shipping in this review task.
```

## Repair a failed check

Append the failing command, exact error and affected task/runbook paths from the run's receipt.

```text
/poteto-mode new task. Reproduce the reported verification failure first, then fix its root cause within the affected task's ownership and verify it. Read its card and PSTACK_EXECUTION.md. Keep all roles on the parent Grok model. Use the Bug fix playbook; preserve the frozen research contract and all failed evidence.
Apply ASSURANCE.md and assigned silent-failure cases. Done means the discriminating reproduction fails before repair and passes after it, affected native/causal checks pass, the new immutable task receipt verifies and a matching GATE_REVIEW.json passes. Return EVIDENCE_MATRIX.json, commands, evidence and explicitly invalidated downstream artifacts. Preserve prior attempts; do not weaken or edit fixed checks, redesign the model grid or start unrelated work.
```

## Pause safely

```text
/poteto-mode new task. Pause this subphase safely at the next atomic boundary. Preserve existing files, manifests, completed shards and failed attempts. Stop further dispatch, reconcile active workers and write the exact done/pending state, code identity, receipt paths and next resume command into this run's WORK_LOG.md and decision trail. Apply PSTACK_EXECUTION.md and ASSURANCE.md; preserve EVIDENCE_MATRIX.json and pending GATE_REVIEW.json findings. No PR, push, automatic history rewrite or fabricated completion. Return a durable resume handoff and leave the run incomplete when work remains.
```
