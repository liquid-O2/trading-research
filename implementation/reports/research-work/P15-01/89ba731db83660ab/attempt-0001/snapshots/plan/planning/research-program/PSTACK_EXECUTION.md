# Run these packs through pstack in Grok

The user's Grok build includes pstack. Start each new coordinator, worker or review task with `/poteto-mode new task.` followed by the concrete goal and finish condition. Resume prompts say that they are taking over existing work. The installed router owns skill sequencing. These packs supply the research specification, ownership and proof requirements.

Every route and subphase obeys [ASSURANCE.md](ASSURANCE.md) and the task's assigned [silent failure checks](SILENT_FAILURES.md). The v2 acceptance amendment requires real behavior evidence and a separately bound review at each subphase boundary. The [foundation repair](FOUNDATION_REPAIR.md) is the current entry; a prior closing message or receipt PASS does not overrule the independent findings.

Read the installed `poteto-mode/SKILL.md` and the matched playbook before acting. Use the installation exposed by the Grok build; the public repository's `pstack/skills/` prefix is a source locator, not an assumed local installation path. Record the installed revision or content hash when available. The [reviewed guide](https://github.com/cursor/plugins/blob/5bf2b1544db739998121a306340631963c2ff3de/pstack/docs/guide/02-poteto-mode.md) explains goal-based routing and the `new task` phrase. Do not fabricate `/feature`, `/hillclimb` or `/autonomous-run` commands; those are playbook names.

## Start a subphase

1. Load the selected RUNBOOK, workspace rules and actual predecessor receipts. The coordinator prompt is the user's instruction to execute that subphase. Do not ask for a second go or rewrite the phase plan.
2. Let `/poteto-mode` match the work. Copy the installed playbook's steps verbatim into a runtime todo list, then add the runbook's task IDs and acceptance checks. Keep every omitted step visible with `skip: <specific reason>`. Use the existing task/session todo facility or a local `WORK_LOG.md`; frozen plan check boxes remain unchanged.
3. State the exact completion predicate and the four-part throughput checkpoint: blocking first steps, independent workstreams, shared mutable state and smallest safe decomposition. Derive the workstreams from the task graph and allowed paths. A first verified slice precedes expansion.
4. Execute the task cards and inspect their actual outputs. The skill router selects supporting skills as needed. Read any principle leaf before claiming it was applied. Name the concrete decision it changed in the final report.
5. Finish when every task has an accepted receipt and EVIDENCE_MATRIX.json, its assigned checks pass, and the subphase verifier exits 0 on the actual `SUBPHASE_RECEIPT.json` with `--gate-review` pointing to a separately written passing GATE_REVIEW.json. P15-01 creates the verifier and implements these assurance rules; the foundation retrospectively verifies P15-00 and runs the fixed independent suite. Review the real code/output, not only worker logs. Stop at this subphase's boundary.

Do not prepend a chain such as “use how, then architect, then arena” to the generated prompts. The guide warns that hand-written chains can bypass the router's own steps. The complete formulas and interfaces remain in the cards and contracts, where a worker can read them without reconstructing them from a short prompt.

## Match the intent to the playbook

This table records project-specific routing decisions after reviewing all 23 poteto-mode playbooks. Playbook paths below are relative to the installed `poteto-mode` skill. The router can select its large-task `figure-it-out` route; it must preserve the existing specification and the bounds in this table.

| Intent and prompt wording | Applicable route | Project finish condition |
| --- | --- | --- |
| “Implement only this subphase. Keep going until its receipts verify.” | Autonomous run (`playbooks/autonomous-run.md`), with `figure-it-out` framing when its large/unattended-task trigger applies. | All listed task receipts accepted, actual subphase verifier exits 0; next subphase is not started. |
| “Implement this feature from task ID.” | Feature (`playbooks/feature.md`). | Named behavior, targeted checks, native slice where required and verified task receipt. Ground existing code and data shapes first. |
| “Run this finite registered research experiment.” | `figure-it-out` for the specified finite experiment; Feature for any missing owned implementation. | Every registered job/trial reconciled and the task receipt verifies, including a supported negative or low-support research disposition. |
| “Take over this interrupted subphase; resume from its manifests.” | Session pickup (`playbooks/session-pickup.md`), then the route for the remaining work. | Reuse verified completed work; finish remaining jobs under the same immutable configuration. |
| “Review this completed subphase; do not change implementation or accepted evidence.” | Investigation (`playbooks/investigation.md`); skeptical review skills when the router calls for them. | Reproducible findings and an evidence-based verdict. Reviewers do not implement fixes in the same task. |
| “Reproduce this failure first, then fix and verify.” | Bug fix (`playbooks/bug-fix.md`). | Reproduction fails before the repair, passes after, affected causal/native checks pass. |
| “Profile this measured runtime; show before and after.” | Perf issue (`playbooks/perf-issue.md`). | Same workload and semantic output, recorded timing/memory change, resource contract satisfied. |
| “Pause safely and leave a resume point.” | Pause safely (`playbooks/pause-safely.md`). | Durable manifests, completed-shard inventory, pending jobs, decision trail and exact next command. An incomplete run stays incomplete. |

The registered market experiments are not the pstack **Eval** playbook. That playbook measures agent/prompt behavior with blinded candidate agents; it does not define financial model evaluation. Use [EVALUATION.md](EVALUATION.md) for folds, outcomes, selection and statistical gates.

Use Hillclimb's frozen measurement and one-change discipline where useful, but its ordinary “keep improving” stop rule does not apply to these finite research tasks. Do not enlarge the candidate bank, add attempts, discard losing evidence, demand a profitable winner or change exposed dates. Research uncertainty can be an accepted result after software and execution are verified. Unverified implementation is never a pass.

**Multi-phase or multi-PR plan** is the authoring route, whose deliverable is a plan. These prompts start execution of an already authored pack. **Orchestrate**, **Autopilot-full** and **Autopilot-stack** manage project/PR programs; they are not the default for one bounded subphase. **Opening a PR**, **Babysit** and **Shipping** are outside this local handoff. **Runtime forensics**, **Trace forensics**, **Refactoring** and **Prototype** are conditional tools for an actual diagnosed need; none changes the frozen research scope. **Visual parity**, **Authoring or modifying a skill** and **Worktree and simulator cleanup** have no default task in these packs. Record inapplicable steps as skips and proceed with the authorized work.

## Grok-only model and worker rules

Use the parent Grok model for every pstack role. `inherit-parent` is a policy alias: omit the subagent tool's `model` field. It is not a model slug to pass literally. This project override also covers roles inside routed skills, such as design panels, explanation, judgment and audit; otherwise upstream defaults can select a different model family. If the runtime does not support inheritance, resolve an actually available Grok model from its tool configuration before spawning. Never guess a model name.

The supported role labels come from the reviewed [setup skill](https://github.com/cursor/plugins/blob/5bf2b1544db739998121a306340631963c2ff3de/pstack/skills/setup-pstack/SKILL.md). Apply these choices in this task's prompts. They are not an instruction to run the interactive setup wizard or write Cursor's global configuration in a Grok build.

```text
feature, refactoring: inherit-parent
bug-fix: inherit-parent
perf-issue: inherit-parent
hillclimb: inherit-parent
judgment and prose: inherit-parent
hardest tasks: inherit-parent
how explorer: inherit-parent
how explainer: inherit-parent
why investigators: inherit-parent
why synthesizer: inherit-parent
reflect tooling: inherit-parent
reflect judgment, divergent, synthesizer: inherit-parent
arena runners: inherit-parent, inherit-parent
arena cross-judge pool: inherit-parent
swarm workers: inherit-parent
architect runners: inherit-parent, inherit-parent
interrogate reviewers: inherit-parent, inherit-parent
```

Use `subagent_type: "poteto-agent"` for ordinary workers when the Grok integration exposes that type. Preserve specialized wrapper types that routed skills require, while applying the Grok-only model override to them. Use background execution when supported, with a real completion/result collection step. If a field or wrapper is unavailable, use the actual native Grok equivalent and record the mapping. Do not fabricate a Cursor `Task` call or silently route through Astra, Fable or mill workers.

Use at most three live agents including the coordinator for this pack by default. A normal implementation worker does not spawn nested workers; its coordinator owns decomposition and a fresh review. Routed read-only panels consume the same cap. A single shared checkout has at most one code-writing agent at a time. Pause coordinator edits while its writing worker owns the checkout; read-only analysis can proceed independently. This avoids conflicting Git, generated-file and shared-module writes despite apparently disjoint task cards. Parallel data-process workers follow the separate measured resource limits in WORKFLOW.

If isolated workspaces are already available under the user's repository rules, the coordinator may use independent writers only after providing each one's actual working root, equivalent absolute file paths and single-writer output ownership. Do not ask workers to create or reset worktrees. Without that isolation, serialize code writers. If permitted subagents are unavailable, do the same cards sequentially and record that fresh-agent review could not run. Do not block implementation waiting for a different model subscription.

A fresh Grok reviewer provides separation from the author but is not cross-model evidence. Record that limitation instead of claiming model diversity or switching to a forbidden model. Preserve useful mathematical/causality comments when they explain non-obvious units or constraints; comment cleanup must not erase the research contract.

## Give each worker a complete bounded brief

Dispatch only after the predecessor receipts verify. The generated card prompt is the instruction body. Attach these actual values using file pointers the worker can access:

| Brief field | Coordinator supplies |
| --- | --- |
| Task and scope | Exact task card, working root, owned paths, prohibited shared writes and reviewer role. |
| Input identity | Current code revision plus dirty-patch identity, predecessor receipt paths and SHA256 hashes. |
| Run identity | Actual immutable run root, frozen manifest, engineering-date manifest and declared slice/full-run mode. |
| Completion | All acceptance keys and assigned assurance IDs, exact verifier command, required common/task artifacts and the separate review predicate. |
| Limits | Card runtime/resource budget, Grok-only role override, no nested delegation and finite search bounds. |
| Return | Actual artifact paths, EVIDENCE_MATRIX.json, measured commands/exit codes, unresolved checks, coverage, disposition and the worker's own decision trail. |

For P15-00, the baseline inputs replace predecessor receipts; the future shared verifier is explicitly pending until P15-01. A worker may inspect its named code and contract references. It should not reread the entire wiki/source archive or choose new algorithms, thresholds or study dates. If the packet is incomplete, first resolve values from accessible predecessor artifacts; otherwise return the concrete missing field to the coordinator while other ready work continues.

Review the worker's diff and output, not just its summary. Record every spawned worker as completed, failed, cancelled or superseded with the evidence pointer. A worker returning after reassignment must reconcile with the current code and receipts before its changes are accepted. The coordinator owns shared registration, integration and subphase receipts.

The worker brief includes the expected observation for its sensitive test and how to distinguish success from a stub, missing input, stale artifact or future leak. A review brief begins with the specification, code identity and actual artifact paths; the author summary is supplementary. Use bounded native examples and existing shared fixtures to control cost. Do not replace semantic checks with a larger test count, or repeat already verified shared work without a code/input change. Preserve fixed checker files; the repair target is the implementation.

## Keep durable local evidence

Use `show-me-your-work`'s canonical TSV format for the decision trail. Store one `DECISIONS.tsv` per active coordinator run and one per independently writing worker run; the coordinator links worker trails rather than letting several agents append to the same file. Keep runtime todo state and the worker assignment table in `WORK_LOG.md`. Reference these files from the run receipt's artifact manifest, hash them at closure and retain the closed attempt. An amended attempt gets a new run/attempt path under WORKFLOW.

The installed skill may describe `/loop`, cloud sleepers, Cursor control skills or a PR toolkit. Those are host capabilities, not guaranteed parts of pstack in Grok. Use only capabilities actually exposed by this build. When no wake facility exists, execute and checkpoint the bounded work normally; a resumed task uses Session pickup. Never claim a heartbeat is armed without a real tool result. Do not install another orchestration system, invoke `orch init`, or create new phase plans to compensate.

These prompts authorize local implementation, declared research runs and their documentation when the user sends them. They do not authorize external messages, PR publication, pushes, merges, deployment, live trading, raw-data deletion or repository-wide cleanup. Upstream commit/rebase/PR steps that conflict with this scope stay visible as skipped. Use the current working tree without rewriting unrelated history or staging unrelated changes. No extra confirmation is needed to perform the authorized local task.

At final review, link the real receipts and decision trail, state what was verified and list material limits. Include both required tables when reporting family results. Separate software verification from whether a market hypothesis passed its statistical gate. Return the next eligible subphase prompt without executing it.
