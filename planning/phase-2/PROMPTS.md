# Phase 2 — copyable coordinator prompts

These prompts start implementation when you send them. The pack itself is a specification; no task is marked implemented by its creation.

pstack is included in the user's Grok build. Copy the entire block, starting with /poteto-mode new task. No separate setup prompt is required. Send one subphase prompt to one Grok task; complete and verify it before the next.

The user sends one coordinator prompt per subphase (17 subphases across both packs). Worker prompts are internal coordinator dispatch material. Resume/review/repair/pause blocks are alternatives for those situations, not additional prompts the user must send for a normal subphase run.

The [pstack execution contract](/workspace/planning/research-program/PSTACK_EXECUTION.md) defines routing, Grok-only roles, worker briefs, local scope and honest stop rules. Each RUNBOOK includes it. The installed router chooses supporting skills; the prompts do not hard-code a skill chain.

Use one coordinator per subphase. A shared checkout has one code writer at a time; independent read-only work may run alongside it. Keep the same declared data-process parallelism and resource limits.

## 00-entry-gate

```text
/poteto-mode new task. Implement Phase 2 subphase 00-entry-gate in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-2/subphases/00-entry-gate/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (Phase 1.5 final release) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 01-datasets-and-fitting

```text
/poteto-mode new task. Implement Phase 2 subphase 01-datasets-and-fitting in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-2/subphases/01-datasets-and-fitting/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (00-entry-gate) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 02-native-options-baseline

```text
/poteto-mode new task. Implement Phase 2 subphase 02-native-options-baseline in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-2/subphases/02-native-options-baseline/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (01-datasets-and-fitting) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 03-joint-volatility

```text
/poteto-mode new task. Implement Phase 2 subphase 03-joint-volatility in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-2/subphases/03-joint-volatility/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (02-native-options-baseline) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 04-context-mechanisms

```text
/poteto-mode new task. Implement Phase 2 subphase 04-context-mechanisms in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-2/subphases/04-context-mechanisms/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (03-joint-volatility) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 05-intraday-oi

```text
/poteto-mode new task. Implement Phase 2 subphase 05-intraday-oi in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-2/subphases/05-intraday-oi/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (04-context-mechanisms) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 06-method-experts

```text
/poteto-mode new task. Implement Phase 2 subphase 06-method-experts in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-2/subphases/06-method-experts/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (05-intraday-oi) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 07-plans-and-adaptation

```text
/poteto-mode new task. Implement Phase 2 subphase 07-plans-and-adaptation in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-2/subphases/07-plans-and-adaptation/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (06-method-experts) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
Use the parent Grok model for every role, including design, judgment and review; inherit-parent means omit the model field. Use the installed poteto-agent/native Grok wrapper, at most three live agents including you. One code writer per shared checkout; you own integration and fresh review. Give each worker its generated card prompt and actual input/receipt/run paths.
State the throughput checkpoint, then implement, test, run the declared native slice or registered full run, inspect output and reconcile failures/unknowns. Keep going until every listed task receipt is accepted and verify_research_release.py subphase exits 0 on your actual SUBPHASE_RECEIPT.json. The foundation first builds this verifier and checks its bootstrap task.
Apply the included ASSURANCE.md and assigned silent-failure cases to every task. Require EVIDENCE_MATRIX.json with sensitive controls, actual code/command/output references, complete job/coverage reconciliation and preserved identities. Independently inspect and reproduce behavior after implementation; logs and self-authored pass flags are insufficient. Finish only after a matching passing GATE_REVIEW.json and required independent checks. Never edit a fixed check to force success; order final receipts and reviews without circular hashes.
Keep a local decision trail. Preserve the frozen formulas, dates, candidate limits, accepted Phase 1 evidence and raw data. Negative or inconclusive market findings may satisfy a research gate; missing implementation cannot. Do not invoke agent/prompt Eval or an open-ended Hillclimb for a market experiment.
This is local implementation and evidence, with no PR/push/merge or shipping workflow. Return verified artifact links, limitations, both required tables for family reports and the next eligible prompt. Stop at this subphase boundary; do not ask for a second go.
```

## 08-release

```text
/poteto-mode new task. Implement Phase 2 subphase 08-release in /workspace.
Read /workspace/AGENTS.md and /workspace/.worktrees/docs-amend/planning/phase-2/subphases/08-release/RUNBOOK.md.
This is one bounded autonomous run using the existing specification. Let the installed pstack router select the playbook and supporting skills. Copy its steps into runtime todos, record skips, and apply the runbook's PSTACK_EXECUTION contract.
Verify the previous gate (07-plans-and-adaptation) and exact predecessor receipts before starting. For a prior research subphase, also require the matching passing GATE_REVIEW.json under ASSURANCE.md. The accepted Phase 1 census retains its original acceptance protocol. The old foundation receipts need the documented repair; a historical PASS string cannot waive the amendment.
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
