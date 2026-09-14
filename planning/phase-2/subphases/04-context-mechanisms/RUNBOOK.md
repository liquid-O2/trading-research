# Phase 2 / 04-context-mechanisms — coordinator runbook

Status: **planned; not implemented by this planning task**. Generated from canonical contracts and task cards. Edit those sources, then rebuild; do not edit this bundle independently.

Source content SHA256: `465ba951eeba35fd842732e8de1418d48884b5cc129f2e5c2f1ed83411d8e419`.

Previous gate: **03-joint-volatility**. External task dependencies: P2-02, P2-04, P2-10. Read and verify their actual receipts before implementation.

## Coordinator work order

Enter through /poteto-mode new task and run only this bounded subphase to its verification predicate. Match the installed playbook, copy its steps into runtime todos and record explicit skip reasons. Apply the included Grok-only model and host-capability overrides to all routed skills. A large-task figure-it-out route must use this existing runbook, not invent a new research plan.

Implement only the tasks listed below, in dependency order. Start with one verified vertical slice. Delegate bounded cards with the complete brief in PSTACK_EXECUTION; a shared checkout has one code writer at a time. At most three live Grok/poteto agents including the coordinator; unavailable workers mean sequential execution. The coordinator reviews and integrates shared schemas/runners and alone writes SUBPHASE_RECEIPT.json.

Read workspace AGENTS.md. The executable contracts and task cards are included below. Source method wiki pages linked by a task are additional focused worker reads; they retain the precise author predicates. Do not reread the whole archive or invent alternative formulas.

The native slice, numerical checks, coverage, future perturbation, actual output inspection and immutable receipts are part of the task. A negative/inconclusive research result is valid; missing implementation is not. Preserve prior evidence and all unsuccessful trials. Do not start the next subphase automatically.

| Task | Dependencies | Canonical card |
| --- | --- | --- |
| P2-05 — Fit directional range, topology and passage-time experts | P2-04 | [Task](/workspace/planning/phase-2/tasks/P2-05.md) |
| P2-06 — Fit auction, day-type and session-quality experts | P2-04 | [Task](/workspace/planning/phase-2/tasks/P2-06.md) |
| P2-07 — Fit flow reward, defense and failed-push experts | P2-04 | [Task](/workspace/planning/phase-2/tasks/P2-07.md) |
| P2-11 — Implement flow, exposure changes and repricing scenarios | P2-10, P2-02, P2-04 | [Task](/workspace/planning/phase-2/tasks/P2-11.md) |
| P2-08 — Fit native cross-market and spot-IV coupling expert | P2-04, P2-11 | [Task](/workspace/planning/phase-2/tasks/P2-08.md) |

## Subphase completion

Collect verified task receipts for every listed task. Record acceptance checks, hashes, native date/coverage identities, schema versions, shared-file integration diffs, runtime and remaining input limits. Write SUBPHASE_RECEIPT.json under a new immutable report run and verify it with verify_research_release.py subphase. The foundation coordinator first creates that verifier and retrospectively verifies its bootstrap task. Then apply ASSURANCE.md: inspect every EVIDENCE_MATRIX.json and assigned failure case, run required independent checks, and write a separately hashed GATE_REVIEW.json referencing the immutable candidate receipt. Closure requires receipt verification plus a matching passing review with no unresolved correctness, causality or integrity findings. Valid controls must pass as well as invalid controls fail.

Return the user a concise completion report, both required family tables when reporting family results, real evidence links, limitations and the next eligible prompt. A subphase gate closes only this subphase. Phase 2 requires all of Phase 1.5 closed first.
Canonical source: [PSTACK_EXECUTION.md](/workspace/.worktrees/docs-amend/planning/research-program/PSTACK_EXECUTION.md).

## Run these packs through pstack in Grok

The user's Grok build includes pstack. Start each new coordinator, worker or review task with `/poteto-mode new task.` followed by the concrete goal and finish condition. Resume prompts say that they are taking over existing work. The installed router owns skill sequencing. These packs supply the research specification, ownership and proof requirements.

Every route and subphase obeys [ASSURANCE.md](/workspace/.worktrees/docs-amend/planning/research-program/ASSURANCE.md) and the task's assigned [silent failure checks](/workspace/.worktrees/docs-amend/planning/research-program/SILENT_FAILURES.md). The v2 acceptance amendment requires real behavior evidence and a separately bound review at each subphase boundary. The [foundation repair](/workspace/.worktrees/docs-amend/planning/research-program/FOUNDATION_REPAIR.md) is the current entry; a prior closing message or receipt PASS does not overrule the independent findings.

Read the installed `poteto-mode/SKILL.md` and the matched playbook before acting. Use the installation exposed by the Grok build; the public repository's `pstack/skills/` prefix is a source locator, not an assumed local installation path. Record the installed revision or content hash when available. The [reviewed guide](https://github.com/cursor/plugins/blob/5bf2b1544db739998121a306340631963c2ff3de/pstack/docs/guide/02-poteto-mode.md) explains goal-based routing and the `new task` phrase. Do not fabricate `/feature`, `/hillclimb` or `/autonomous-run` commands; those are playbook names.

### Start a subphase

1. Load the selected RUNBOOK, workspace rules and actual predecessor receipts. The coordinator prompt is the user's instruction to execute that subphase. Do not ask for a second go or rewrite the phase plan.
2. Let `/poteto-mode` match the work. Copy the installed playbook's steps verbatim into a runtime todo list, then add the runbook's task IDs and acceptance checks. Keep every omitted step visible with `skip: <specific reason>`. Use the existing task/session todo facility or a local `WORK_LOG.md`; frozen plan check boxes remain unchanged.
3. State the exact completion predicate and the four-part throughput checkpoint: blocking first steps, independent workstreams, shared mutable state and smallest safe decomposition. Derive the workstreams from the task graph and allowed paths. A first verified slice precedes expansion.
4. Execute the task cards and inspect their actual outputs. The skill router selects supporting skills as needed. Read any principle leaf before claiming it was applied. Name the concrete decision it changed in the final report.
5. Finish when every task has an accepted receipt and EVIDENCE_MATRIX.json, its assigned checks pass, and the subphase verifier exits 0 on the actual `SUBPHASE_RECEIPT.json` with `--gate-review` pointing to a separately written passing GATE_REVIEW.json. P15-01 creates the verifier and implements these assurance rules; the foundation retrospectively verifies P15-00 and runs the fixed independent suite. Review the real code/output, not only worker logs. Stop at this subphase's boundary.

Do not prepend a chain such as “use how, then architect, then arena” to the generated prompts. The guide warns that hand-written chains can bypass the router's own steps. The complete formulas and interfaces remain in the cards and contracts, where a worker can read them without reconstructing them from a short prompt.

### Match the intent to the playbook

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

The registered market experiments are not the pstack **Eval** playbook. That playbook measures agent/prompt behavior with blinded candidate agents; it does not define financial model evaluation. Use [EVALUATION.md](/workspace/.worktrees/docs-amend/planning/research-program/EVALUATION.md) for folds, outcomes, selection and statistical gates.

Use Hillclimb's frozen measurement and one-change discipline where useful, but its ordinary “keep improving” stop rule does not apply to these finite research tasks. Do not enlarge the candidate bank, add attempts, discard losing evidence, demand a profitable winner or change exposed dates. Research uncertainty can be an accepted result after software and execution are verified. Unverified implementation is never a pass.

**Multi-phase or multi-PR plan** is the authoring route, whose deliverable is a plan. These prompts start execution of an already authored pack. **Orchestrate**, **Autopilot-full** and **Autopilot-stack** manage project/PR programs; they are not the default for one bounded subphase. **Opening a PR**, **Babysit** and **Shipping** are outside this local handoff. **Runtime forensics**, **Trace forensics**, **Refactoring** and **Prototype** are conditional tools for an actual diagnosed need; none changes the frozen research scope. **Visual parity**, **Authoring or modifying a skill** and **Worktree and simulator cleanup** have no default task in these packs. Record inapplicable steps as skips and proceed with the authorized work.

### Grok-only model and worker rules

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

### Give each worker a complete bounded brief

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

### Keep durable local evidence

Use `show-me-your-work`'s canonical TSV format for the decision trail. Store one `DECISIONS.tsv` per active coordinator run and one per independently writing worker run; the coordinator links worker trails rather than letting several agents append to the same file. Keep runtime todo state and the worker assignment table in `WORK_LOG.md`. Reference these files from the run receipt's artifact manifest, hash them at closure and retain the closed attempt. An amended attempt gets a new run/attempt path under WORKFLOW.

The installed skill may describe `/loop`, cloud sleepers, Cursor control skills or a PR toolkit. Those are host capabilities, not guaranteed parts of pstack in Grok. Use only capabilities actually exposed by this build. When no wake facility exists, execute and checkpoint the bounded work normally; a resumed task uses Session pickup. Never claim a heartbeat is armed without a real tool result. Do not install another orchestration system, invoke `orch init`, or create new phase plans to compensate.

These prompts authorize local implementation, declared research runs and their documentation when the user sends them. They do not authorize external messages, PR publication, pushes, merges, deployment, live trading, raw-data deletion or repository-wide cleanup. Upstream commit/rebase/PR steps that conflict with this scope stay visible as skipped. Use the current working tree without rewriting unrelated history or staging unrelated changes. No extra confirmation is needed to perform the authorized local task.

At final review, link the real receipts and decision trail, state what was verified and list material limits. Include both required tables when reporting family results. Separate software verification from whether a market hypothesis passed its statistical gate. Return the next eligible subphase prompt without executing it.

Canonical source: [ASSURANCE.md](/workspace/.worktrees/docs-amend/planning/research-program/ASSURANCE.md).

## Evidence and failure checks

Acceptance amendment `research-assurance-2026-09-14-v2`. This is part of every Phase 1.5 and Phase 2 task. It strengthens software acceptance without changing research formulas, candidate budgets or statistical thresholds. [Amendment history](/workspace/.worktrees/docs-amend/planning/research-program/AMENDMENTS.json) preserves the previous foundation identities. [Failure cases](/workspace/.worktrees/docs-amend/planning/research-program/SILENT_FAILURES.md) and their [machine-readable assignment](/workspace/.worktrees/docs-amend/planning/research-program/ASSURANCE_CASES.json) specify the additional checks by task.

### Completion requires observable behavior

The implementer must satisfy the task card, the assigned failure cases and the shared contract. The coordinator must inspect the code and reproduce the evidence. An acceptance boolean, a worker's summary, a pytest count, or a successful call to a newly written verifier is insufficient on its own. Treat a verifier as software under test: show it rejects plausible false claims while continuing to accept correctly implemented work.

Each writing task produces `EVIDENCE_MATRIX.json`, `WORK_LOG.md` and its own `DECISIONS.tsv`. Foundation bootstrap does not waive these artifacts. Record actual commands and times as work occurs. A reconstructed time must be labelled reconstructed with its source; do not present it as measured. Shared coordinator logs may link worker logs but cannot replace them. Reviewers inspect implementation behavior separately from log completeness.

Use this matrix schema, `research-evidence-matrix-v2`:

```json
{
  "schema_version": "research-evidence-matrix-v2",
  "task_id": "ACTUAL_TASK_ID",
  "assurance_version": "research-assurance-2026-09-14-v2",
  "checks": [
    {
      "id": "A01",
      "requirement": "The exact behavior being checked",
      "code_refs": [{"path": "repository-relative module", "symbol": "actual callable"}],
      "test_nodeids": ["repository-relative test file::test_name"],
      "command_indices": [0],
      "evidence": [{"path": "actual artifact", "sha256": "64 lowercase hex", "selector": "JSON pointer or stable row ID"}],
      "expected": "Literal expected result and tolerance, derived from the specification",
      "observed": "Actual result at the selected row",
      "oracle": "Independent arithmetic, frozen baseline, native receipt, or declared metamorphic relation",
      "status": "pass"
    }
  ]
}
```

The ID set equals all required `Axx` keys plus all failure-case IDs assigned to this task in `ASSURANCE_CASES.json`. Each appears exactly once. Each command index must point to an executed, logged receipt command. Each path/hash/selector must resolve to the advertised evidence. Evidence may support several checks, but each check must explain its own expected result. A structural evidence check may cite a deterministic audit command instead of a pytest node ID. Empty lists, a prose `PASS`, or an unexecuted node name cannot close a behavioral requirement. A07's matrix-completeness check refers to the other entries and their evidence, avoiding a self-hash.

For any new behavior, write the sensitive fixture before the fix, save the observed failure, then save the passing result. For an existing behavior that already works, perform an isolated input mutation, call the public boundary and retain both accepted and rejected controls. Do not rewrite working code merely to manufacture a red test. A known synthetic signal proves a model can use its inputs; actual market improvement is not a software acceptance criterion. A fixed replay proves native I/O and identity; synthetic records alone cannot substitute for it.

### Artifact and identity verification

P15-01 implements these rules; later tasks use them. Emit structured failures and exit 2 for invalid evidence. A failed/incomplete implementation never becomes accepted because its report contains an explanation.

New task/subphase/phase receipts use their corresponding `research-*-receipt-v2` schema and include `assurance_version`. Preserve v1 files for historical inspection; they do not pass current downstream admission. The lineage schema remains v1 with these clarified validation rules. Add `--gate-review PATH` to the subphase/phase verifier: without it the command verifies an immutable candidate; with it the command additionally verifies the review binding and closure predicate. Later-subphase dispatch requires the latter. Internal predecessor tasks in an active subphase need verified task receipts; the separate review is finalized when that subphase closes. P15-01's bootstrap exception remains explicit.

1. **Required inventory.** Require every task-specific artifact in `TASK_GRAPH.json`, every `required_task_artifacts` item, all required command logs and any declared frozen manifest. Match exact logical names, enforce uniqueness and task ownership, then hash actual bytes and check sizes. An empty manifest fails. A directory artifact such as `FAMILY_REPORTS/` requires a hashed index of every file, expected member identities and count; naming an empty directory does not satisfy it. A schema label must match parsed contents and supported schema version. Parse/recount declared JSON/JSONL/table rows; do not accept an asserted row count without checking it. Markdown/log artifacts use their explicit non-record schema.
2. **Required plan files.** Write `PLAN_SNAPSHOT.json` with `schema_version`, `assurance_version`, `files` (repository-relative path to SHA256) and `snapshot_paths` (same keys to preserved copies). The file set is the task card, all graph `reads`, `TASK_GRAPH.json` and `ASSURANCE_CASES.json`; no omitted references or duplicate aliases. Snapshot the actual bytes. `plan_sha256 = SHA256(canonical_json(files))`. A historical snapshot can be inspected after the live docs change; a downstream admission must also require the currently authorized assurance version. An older graph cannot waive an amendment.
3. **Code identity.** Write `CODE_SNAPSHOT.json` containing `schema_version`, `files`, `snapshot_paths`, `runtime` and `dependency_lock_sha256`. Include all owned source/test/tool files and project helpers actually imported by the executed paths, including untracked files. Record the imported-module inventory and statically identified dependencies of unexecuted branches; an import trace alone does not prove the inventory is exhaustive. Bind the existing Python/runtime and lock identities. `code_sha256 = SHA256(canonical_json(CODE_SNAPSHOT document))`. Recompute file hashes; a dirty-patch hash or a current Git commit alone cannot cover untracked implementation. The coordinator checks this inventory against the actual diff/imports.
4. **Semantic run identity.** `DRAFT_MANIFEST.json` binds task ID, assurance version, plan hash, code hash, exact predecessor receipt hashes, input identities, date/coverage identity and registered configuration. `run_id = SHA256(canonical_json(DRAFT_MANIFEST document))[:16]`. Compare these values to the receipt, snapshots and frozen manifest. Canonical JSON is UTF-8, sorted keys, compact separators, finite values only; SHA256s use 64 lowercase hex characters. Run IDs use 16 lowercase hex characters. Execution time, final receipt hash and final audit result do not belong in the semantic draft. No self-references. Declared input hashes must resolve to preserved artifacts; a well-formed 64-character string is not identity verification.
5. **Recursive admission.** Resolve each predecessor by its exact hash and task ID, then validate its full receipt, artifact contents, disposition and dependencies. Detect unknown tasks, wrong IDs, missing dependencies, duplicate receipt reuse, cycles and obsolete assurance versions. Cache successful verification by `(receipt hash, graph hash, assurance version)` only. The subphase must exist in the graph and contain exactly its required task IDs; an unknown empty subphase fails. A phase resolves and verifies all required task receipts, rather than trusting dispositions copied beside their paths. Phase 2 admission requires the actual Phase 1.5 release path/hash and successful recursive validation. A string `phase_1_5_gate: pass` cannot authorize it.
6. **Commands and dispositions.** Required implementation tests/verification commands must exit 0 with existing hashed logs. Nonzero results remain failures even if `unresolved` mentions them. Deliberate negative CLI cases belong in their enclosing passing test/suite artifact with explicit expected exit 2, actual exit 2 and structured error; they are not excused failed implementation commands. Historical red tests live in the decision/evidence trail and are followed by a separately recorded passing rerun. Validate task-specific terminal statuses. Input limits are structured cells with input group, search evidence, scope and downstream effect; arbitrary words such as `native` or `calendar` in prose cannot grant a coverage exception.

EVIDENCE_MATRIX verification checks the exact required key set, supported statuses, code references, executed test/audit commands and every evidence selector/hash. Unknown keys, missing required checks, nonexistent rows/symbols, unavailable logs and an unverified inherited check fail. The coordinator separately checks that the selected evidence proves the stated requirement; structural validation cannot infer scientific correctness from a prose `expected` value. Unit tests must include forged matrices that have true acceptance flags but missing, unrelated or stale evidence.

Snapshot-copy paths inside identity documents are relative to the containing snapshot document, for example `snapshots/code/implementation/src/...`; they cannot contain the new run ID or its absolute output directory. Build these documents in staging, compute the semantic ID, then publish the new attempt. The draft stores predecessor receipt bindings once in `predecessor_receipts`; `input_identities` binds underlying input/configuration artifacts. Runtime metadata in the code snapshot identifies interpreter/packages/lock, not output log paths. These rules avoid a subtler cycle in which the code hash includes a snapshot destination containing its own run ID.

`TASK_RECEIPT.json` does not hash itself or a final release that references it. P15-01 returns `VERIFIER_CASES.json` and verified gate inputs; the coordinator writes `SUBPHASE_RECEIPT.json` after task receipts exist. Similarly P15-20/P2-24 return release inputs and their task receipts; the coordinator then writes `PHASE1_5_RELEASE.json`/`PHASE2_RELEASE.json`. Coordinator outputs are separately declared in the graph. Verification logs about a final receipt are sidecars, not edits to that receipt. This ordering prevents circular hashes and premature acceptance.

### Coverage and native evidence

Engineering dates are selected per **required input group**, from input coverage metadata before new outcomes are inspected. A verified matching calendar is one requirement; it does not establish native history or feed coverage. Preserve `complete_observed_scope` versus unknown exchange-feed completeness. Do not require every branch to share one denominator, and do not treat a structurally inapplicable branch as missing market data.

`ENGINEERING_DATES.json` uses `research-engineering-dates-v2`. It contains the deterministic selection policy, hashed source inventory, `input_groups`, and separate `fixtures`. Each group has `group_id`, `requirements`, `coverage_rows`, `year_slots` and `dst_slot`. Each requirement identifies the native asset/contract, data kind, source policy and exact required current/history interval. Each coverage row contains account day, verified matching intervals, contract IDs, required intervals, known/missing/ambiguous intervals, native receipt path/hash/row selectors and a disposition. Refer to the accepted composed reconstruction calendar and its exceptions where baseline semantics require it. Keep current-session coverage separate from prior-session, week/month, profile and fitting-history coverage.

Recompute each slot from that group's coverage rows: first complete eligible date in each available year 2020–2026, plus the complete eligible date nearest 2023-11-05, ties earlier. Preserve a missing slot when no complete eligible date exists. Do not force eight distinct dates if a deterministic slot coincides with another. Select/reject using coverage only; retain the inspected coverage inventory, including earlier ineligible dates, so selection is reproducible. Group definitions come from required inputs, never from whichever subset happened to be complete. An unsupported group keeps its generic fixture checks and explicit scope limitation.

Include separate actual partial-final-date, roll and unverified-holiday evidence. The feed-gap and same-timestamp-conflict checks need executable fixtures: remove a known interval from a copied complete input and verify the exact unknown interval; permute conflicting events in one batch and verify ambiguity survives. Mark injected fixtures synthetic, and keep actual native gap/roll identities when owned. `not_in_calendar_metadata` is a limitation, not a feed-gap test.

`SCHEMA_EXAMPLES.json` distinguishes native-derived records from synthetic fixtures. For the native example preserve the actual source file, hash, row ID, contract, event/availability clocks, adapter callable and serialized output selector; reopen that source and replay one record. For missing/ambiguous and personal-execution examples show the scope distinction. A generated `NativeTrade` with plausible timestamps is still synthetic.

### Every clock boundary is enforced

Test every evidence-bearing type, not just `FeatureValue`/`Snapshot`. Native records cannot have `available_at_ns` earlier than their evidence. Formations, references, contacts, predicates, sequence states, opportunities and snapshots enforce the appropriate parent cutoff. Immutable wrappers must recursively copy/freeze nested state. Reject noninteger clocks (including booleans), invalid intervals, units, enum values, nonfinite nested numbers and undefined geometry at deserialization as well as construction.

Lineage validation carries every ancestor cutoff down the graph. A child with local issue 100 cannot make evidence available at 100 usable by a root issued at 10. On feature/parameter edges enforce availability at or before every consuming cutoff; require artifact path/hash and resolvable row IDs at evidence leaves. Missing or malformed clocks cannot be silently skipped. Require `train_end_ns <= fit_available_at_ns <= issue_at_ns` for fitted forecasts, plus mature training labels. Future target ends are allowed on explicitly labelled outcome edges only; those edges cannot become predictor parents. Validate supported outputs and parameters for finite values and domain constraints.

### Independent closure

After implementation tests and task/subphase verification, run the independent foundation checker on the **actual new** receipts. Its path/hash is pinned in `ASSURANCE_CASES.json`. Do not modify it, omit cases, substitute older receipts, or mark expected failures as passes to close a task. It must accept valid controls as well as reject invalid ones; a verifier that rejects everything cannot pass. It is a minimum suite, not an exhaustive proof. Task tests must additionally isolate each assigned failure mode and assert the intended failure code/field, so an unrelated malformed field does not masquerade as a tested safeguard.

The coordinator or fresh permitted reviewer creates `GATE_REVIEW.json` **after** the candidate subphase receipt is immutable. Schema `research-gate-review-v2`: subphase/phase ID; assurance version; candidate receipt path/hash; current code snapshot hashes; reviewed task IDs; evidence matrix path/hashes; independent suite path/hash and results path/hash where required; commands/logs; findings with severity, reproduction, affected outputs and resolution evidence; explicit unverified checks; `verdict = pass | issues | blocked`. It does not edit the candidate. Admission to a later subphase requires both receipt verification and a matching passing review with no unresolved correctness/causality/integrity findings. A narrative “next eligible” statement cannot override the review.

The phase-level sidecar may be named `PHASE_GATE_REVIEW.json` to coexist with its release subphase's review. Validate its contents identically against the phase candidate. Final `--gate-review` verification logs are unreferenced sidecars; hashing the command that validates a review into that same review would create another cycle. A review must bind the current graph/assurance registry hashes, exact candidate task set and their code snapshots. Independent results must name the expected checker hash, all expected cases and the same current graph/foundation receipt inputs. Missing/failed/skipped cases, an older graph, unrelated passing results or changed code fail admission.

A fresh reviewer receives the specification and actual code/artifact paths before the author's summary. It selects and runs counterexamples, traces at least one native output, checks complete job/count reconciliation, and independently recalculates one central result. Review of work logs alone does not count. When fresh agents are unavailable, the coordinator performs the same checks in a separate review pass, records that limitation and retains commands. Same-model review is not independent model diversity.

For foundation and final phase closure rerun the fixed foundation suite against the bound foundation receipts/code. For intervening tasks, verify its accepted result hashes and run affected cases whenever shared contracts/verification/cache code changes. Never reuse stale validation after changing tested code. Keep failed and superseded outputs; invalidate dependent artifacts explicitly and rebuild affected descendants under new identities. No implementation or research run was performed merely by authoring this amendment.

Canonical source: [SILENT_FAILURES.md](/workspace/.worktrees/docs-amend/planning/research-program/SILENT_FAILURES.md).

## Silent failure checks

Generated from [ASSURANCE_CASES.json](/workspace/planning/research-program/ASSURANCE_CASES.json). These are required prevention cases, not claims that every listed defect was found in current code. Use [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md) for evidence and closure rules.

Reuse a bound shared test/evidence artifact when it proves the same invariant on the same code and inputs. Run task-specific native/behavior cases where scope differs. Do not duplicate a test solely to increase the test count. An inherited check must name its current artifact/hash and applicability; a stale pass cannot be inherited.

This runbook includes only cases assigned to: P2-05, P2-06, P2-07, P2-08, P2-11.

### S01 — Missing, substituted or malformed required artifacts

Assigned tasks: P15-00, P15-01, P15-02, P15-03, P15-04, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-17, P15-18, P15-19, P15-20, P2-00, P2-01, P2-02, P2-03, P2-04, P2-05, P2-06, P2-07, P2-08, P2-09, P2-10, P2-11, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-23, P2-24.

**Probe:** Remove one required artifact from a valid copied receipt; then substitute a different task’s file with a correct byte hash; separately alter a claimed row count and replace JSON with invalid contents. Keep valid controls.

**Expected:** Each malformed case fails for the affected inventory, identity, schema or row-count reason. All required members and command logs are checked; directory artifacts require a complete file index.

**Evidence:** Actual task CLI results, valid control and isolated mutations with failure codes; use temporary copies.

### S02 — Unimplemented behavior hidden behind green tests

Assigned tasks: P15-00, P15-01, P15-02, P15-03, P15-04, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-17, P15-18, P15-19, P15-20, P2-00, P2-01, P2-02, P2-03, P2-04, P2-05, P2-06, P2-07, P2-08, P2-09, P2-10, P2-11, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-23, P2-24.

**Probe:** For the central card requirement, identify the actual callable and output field; use independent arithmetic, a frozen baseline or a specified invariant to construct one sensitive check. For a new fix retain before/after; for existing behavior mutate a boundary input.

**Expected:** The check fails when the advertised behavior is absent, reversed or bypassed and passes for the implemented behavior. All Axx keys have resolvable evidence. Test collection and exit 0 alone do not satisfy this.

**Evidence:** EVIDENCE_MATRIX with exact test node IDs, command logs, input/output selectors, expected values and oracle derivation.

### S03 — Self-asserted code, plan and run identities

Assigned tasks: P15-00, P15-01, P15-02, P15-03, P15-04, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-17, P15-18, P15-19, P15-20, P2-00, P2-01, P2-02, P2-03, P2-04, P2-05, P2-06, P2-07, P2-08, P2-09, P2-10, P2-11, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-23, P2-24.

**Probe:** Recompute the plan/code/draft identities independently from preserved bytes. Mutate each digest separately, omit an owned untracked file, and change a relevant helper/configuration without updating the binding.

**Expected:** False identities are rejected. The file inventory includes actual runtime dependencies and untracked code; historical snapshots retain their authorized plan version.

**Evidence:** PLAN_SNAPSHOT, CODE_SNAPSHOT, draft/frozen manifest and independent recomputation results.

### S07 — Synthetic data presented as native evidence

Assigned tasks: P15-00, P15-02, P15-03, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-17, P15-18, P15-19, P15-20, P2-00, P2-01, P2-03, P2-04, P2-05, P2-06, P2-07, P2-08, P2-09, P2-10, P2-11, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-23, P2-24.

**Probe:** Reopen one actual native artifact and row named in the output lineage and replay the named adapter. Separately include a clearly marked synthetic missing/ambiguous fixture.

**Expected:** Native values, contract and event/availability clocks match the identified source. Synthetic examples are labelled synthetic. A fabricated row ID or unavailable file fails.

**Evidence:** Source path/hash/row, adapter callable, serialized output selector and independently replayed comparison.

### S08 — Future data changes earlier output

Assigned tasks: P15-02, P15-03, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P2-01, P2-03, P2-04, P2-05, P2-06, P2-07, P2-08, P2-09, P2-10, P2-11, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-23.

**Probe:** Choose cutoff t; alter all post-t records and all earlier-event records whose availability is after t. Recompute from raw inputs, including the join/preprocessing/fit path. Separately alter a relevant pre-t input on a sensitive fixture.

**Expected:** Earlier features, decisions, predictions and immutable artifacts remain unchanged after the future mutation. The sensitive admissible-input mutation changes its declared output; a constant-output stub cannot pass.

**Evidence:** Before/after input hashes and output fields; cold-cache rerun; boundary equality and as-of join cases.

### S09 — Invented order within one timestamp batch

Assigned tasks: P15-02, P15-03, P15-06, P15-07, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P2-01, P2-07, P2-09, P2-11.

**Probe:** Permute conflicting high/low, buy/sell or target/stop events in the same unresolved batch, including row-ID order.

**Expected:** Results preserve the same ambiguity set and batch availability. No row sort creates a favorable ordering, premature confirmation or inferred aggressor.

**Evidence:** Permutation cases and one native ambiguous batch where available, including raw IDs and ambiguity reason.

### S11 — Missing windows silently become zeros

Assigned tasks: P15-02, P15-03, P15-06, P15-17, P15-18, P15-19, P15-20, P2-01, P2-04, P2-05, P2-06, P2-07, P2-08, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-24.

**Probe:** Create three days: complete with no opportunity, incomplete horizon, and an observed event with measured outcome. Also test an absent conditional arrival.

**Expected:** The complete no-opportunity day stays in the denominator with occurrence 0; the incomplete horizon is unknown; conditional reaction/utility is undefined without arrival. Missing outcomes are never imputed to zero, loss or a median.

**Evidence:** Declared/complete/zero/partial/missing day counts, label masks, row IDs and denominator reconciliation.

### S14 — Unit, sign, precision and nonfinite errors

Assigned tasks: P15-00, P15-03, P15-05, P15-06, P15-19, P2-02, P2-03, P2-10, P2-11, P2-12, P2-22.

**Probe:** Use the literal reference vectors and mirror long/short cases. Check ticks versus points/dollars, seconds versus ns/years, percent versus decimal, prices versus returns and contract multipliers. Inject nested NaN/Infinity, bool clocks and numeric overflow.

**Expected:** Independent expected arithmetic matches within a predeclared justified tolerance. Invalid values fail or receive the contract’s explicit unsupported disposition; no broad exception-to-zero or silently clipped valid geometry.

**Evidence:** Literal inputs/units, expected/actual numbers, tolerance and source equation; edge and finite-domain tests.

### S15 — Many-to-many joins or feature order silently corrupt rows

Assigned tasks: P15-02, P15-17, P2-01, P2-02, P2-08, P2-09, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20.

**Probe:** Duplicate one right-side key; omit one row; shuffle native row order and predictor columns; collide a timestamp across two assets/contracts/folds.

**Expected:** Declared row identity and join cardinality hold, unmatched rows have explicit masks, and duplicates fail or follow a predeclared deduplication policy. Column names/order/schema are bound in fitted artifacts; reshuffling cannot silently swap meanings.

**Evidence:** Pre/post join counts and key uniqueness, join diagnostics, shuffled-input and serialization/prediction checks.

### S16 — Overlapping labels or censored targets leak

Assigned tasks: P15-03, P2-01, P2-03, P2-05, P2-12, P2-23.

**Probe:** Place an issue exactly at a fold boundary, a target whose end crosses it, an unresolved passage event and a training label published after the issue.

**Expected:** Feature windows remain [start,end), outcomes (issue,end]; purge/embargo and maturity rules exclude unavailable targets. Censoring is retained. No full-day outcome becomes an intraday predictor.

**Evidence:** Boundary row membership, label/fit availability, censored/support masks and split manifests.

### S18 — Computed predictors never reach the fitted model

Assigned tasks: P2-02, P2-04, P2-05, P2-06, P2-07, P2-08, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-24.

**Probe:** Plant a known synthetic signal in one named feature family. Inspect the actual predictor matrix, masks, head inputs and serialized coefficients. Remove that family and perform the declared ablation with a fresh fit.

**Expected:** The expected named columns reach the optimizer and affect the sensitive prediction. Ablation changes the actual fit input and artifact identity. A computed feature dictionary, copied baseline predictions or all-zero stub cannot satisfy the experiment.

**Evidence:** Feature-to-column-to-head mapping, planted-signal outputs, artifact reload prediction and refitted ablation comparison; no market-win requirement.

### S19 — Optimizer, gradient or serialization failure hidden as convergence

Assigned tasks: P2-02, P2-04, P2-05, P2-06, P2-07, P2-08, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21.

**Probe:** Check a small analytic or finite-difference gradient case, a constant/collinear input, an absent target class and a known signal. Force nonconvergence/nonfinite parameters; serialize and reload a successful artifact.

**Expected:** Gradients and objective behavior match the recipe. Unsupported/singular or nonconverged fits get explicit diagnostics and cannot masquerade as trained artifacts. Reloaded predictions match, including preprocessing and feature order.

**Evidence:** Solver residual/iteration diagnostics, expected gradient values/tolerance, known-signal loss and reload comparisons.

### S23 — Unresolved cohorts or later outcomes alter earlier memory

Assigned tasks: P15-06, P15-12, P2-07, P2-17.

**Probe:** Include one resolved cohort and one whose outcome becomes known after the issue; alter the latter’s future outcome and change aggregation order.

**Expected:** Only matured cohorts update memory; prior state remains stable under future perturbation and deterministic aggregation. Unknown aggressor volume stays separate and support gates use the specified denominator.

**Evidence:** Cohort event/resolution clocks, state snapshots, literal +10/-4/unknown6 CVD vector and availability negatives.

### S25 — Option definitions, stale quotes or OI publication guessed

Assigned tasks: P2-00, P2-01, P2-09, P2-10, P2-11, P2-12, P2-24.

**Probe:** Use stale spot/option quotes, inverted bid/ask, a close-only cash index, a contract with unknown settlement/expiry, and an OI effective date before publication. Test the declared extra-session publication delay.

**Expected:** Exact freshness/model bounds and dated native definitions gate the rows. Filename date is not availability; close-only cash data is not native intraday spot. Assumed OI clocks remain labelled assumptions. Missing chain members stay in coverage denominators.

**Evidence:** Instrument/source ledger, quote-age and price-bound cases, OI effective/published/available clocks and delay sensitivity.

### S26 — Greeks, exposure or repricing use wrong conventions

Assigned tasks: P2-10, P2-11, P2-12.

**Probe:** Use ATM pricing reference vectors and finite-difference Greeks away from boundaries; vary multiplier, spot/future reference, expiry time, rate/dividend and option side. Compare a zero-change scenario with baseline.

**Expected:** Units/signs and supported pricing conventions match the declared model. Unsupported exercise/settlement inputs stay unsupported. Zero-change repricing reconciles; exposure sums and changes preserve contract-level contributions.

**Evidence:** Independent pricing/Greek calculations, tolerances, per-contract exposure reconciliation and scenario identities.

### S27 — Weak OI labels treated as known intraday truth

Assigned tasks: P2-11, P2-12, P2-24.

**Probe:** Use an endpoint that permits multiple intraday paths; test expiry zero, group ownership, prefix clipping and delayed endpoint labels. Leak next-day OI deliberately into a pre-publication feature.

**Expected:** Unidentified intraday paths retain uncertainty; expiry is not opening/closing-flow supervision. Conservation/bounds and prefix clipping follow the declared equations. Pre-publication features remain unchanged by unavailable endpoint labels.

**Evidence:** Group ledger, literal gradient/prefix vectors, endpoint versus path diagnostics, OOF availability and uncertainty outputs.

### S28 — Outputs ignore supported heads, branches or conditional meaning

Assigned tasks: P2-04, P2-05, P2-06, P2-07, P2-08, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-24.

**Probe:** Inventory every required head, branch and horizon against emitted predictions; include a low-support branch, no-arrival case and missing required input.

**Expected:** All required cells have outputs or explicit typed support dispositions. Probabilities, quantiles, ranges and conditional utilities obey their domains and ordering where required. A global average or one default branch cannot replace separately required targets.

**Evidence:** Expected-versus-emitted head/branch/horizon matrix, domain checks, support denominators and conditional-label masks.

### S31 — Provenance or unsupported input silently relabelled

Assigned tasks: P15-00, P15-04, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-20, P2-00, P2-08, P2-09, P2-21, P2-24.

**Probe:** Round-trip an unknown source_exact field, a source-inspired operational rule, missing proprietary constants, cash-index input limits and personal-execution-only data.

**Expected:** Unknown does not become true or false implicitly; proxies remain labelled. Generic implementation still passes fixtures when native cells are unsupported. Personal risk/process records do not gate market setup definitions.

**Evidence:** Raw/normalized round-trip, source/operator ledger, scope/availability receipts and downstream allowlist with exact limitations.

### S32 — Slice-only or low-support work presented as a full experiment

Assigned tasks: P15-17, P15-18, P15-19, P15-20, P2-02, P2-04, P2-05, P2-06, P2-07, P2-08, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-23, P2-24.

**Probe:** Compare declared full dates, preceding training/tuning/calibration history and registered jobs to actually consumed rows. Restrict output to eight engineering dates and inspect whether fitting was incorrectly restricted too.

**Expected:** A slice limits evaluation/output only; fitting consumes the full declared preceding history. A timeout/resource abort remains incomplete and resumes. Complete low-support/negative results require correctly implemented and executed finite work, with no empirical winner needed.

**Evidence:** Train/tune/calibration/output date ranges and row counts, job inventory, resource logs, exact unresolved work and full-run reconciliation.

Canonical source: [ROADMAP.md](/workspace/.worktrees/docs-amend/planning/ROADMAP.md).

## Research program roadmap

Status: implementation specifications, version `research-plan-2026-09-14-v3`. Phase 1 is complete for the acquired observed-input population. The original Phase 1.5 foundation implementation failed independent acceptance review; the remaining subphases and Phase 2 are specified.

The [v2 assurance amendment](/workspace/planning/research-program/ASSURANCE.md) applies to all 46 tasks and all 17 subphases. Until replacement foundation receipts and their matching review pass, use the [foundation repair prompt](/workspace/planning/research-program/FOUNDATION_REPAIR.md#copyable-repair-prompt), before `01-native-and-outcomes`. [Current execution status](/workspace/wiki/current-status.md) links the applicable evidence; an old completion message cannot authorize the next subphase.

The objective is an adaptive NQ decision process whose context, location and response components can each be tested. Source methods supply baselines and mechanisms; they do not impose a fixed model count. All numerical choices introduced in these packs are our registered research policies, not recovered proprietary constants.

| Development phase | Responsibility and deliverable | Gate |
| --- | --- | --- |
| 1 — complete | Reconstruct and measure source-linked setups. [Evidence](/workspace/planning/phase-1-live/PHASE.md). | Accepted acquired census; limitations carried forward. |
| 1.5 — specified | Reconstruct missing numerical rules; improve CVD; compare representative formation, reference, sequence, confirmation and setup rules; refine within a finite budget; retain unchanged-entry exit comparisons. [Pack](/workspace/planning/phase-1-5/README.md). | Every task has a verified terminal disposition, all attempted variants are recorded, baseline and selected rules are frozen. No winner is required. |
| 2 — specified | Intraday jointly fitted volatility/range forecasts, native options context and intraday OI/IV updates, auction/session/cross-market forecasts, and separately fitted method context experts. [Pack](/workspace/planning/phase-2/README.md). | Chronological predictions, conditional plans, input lineage, ablations, calibration and support limits are reproducible. |
| 3 — scope reserved | Fitted location experts: P-zone upgrades, forward-volatility-derived actionable areas, native gamma/vega/vanna/OI/volume/VWAP/prior-extreme areas, arrival and conditional reaction, competing areas. | Detailed implementation pack follows the actual Phase 2 outputs. |
| 4 — scope reserved | Response/entry experts and integrator: combine context and location, choose whether/when to enter NQ, use cross-asset responses, evaluate account-level execution and risk. | Combined historical replay and daily economic distribution; prospective evidence remains separate. |
| Later management work — recommendation | Empirical exit/management specialists, thesis changes and re-entry after fixed-entry controls. | Not a user-approved numbered Phase 5; do not silently add partial contracts to a one-mini account. |

**All of Phase 1.5 must finish before Phase 2 implementation**, except that P2-09, P2-10 and P2-03 may start from the verified P15-02 receipt (the native MarketView) instead of waiting for the Phase 1.5 release. Those three receipts must be re-verified under P2-00 before P2-04, P2-11 or any method expert consumes them. The packs may be read now; their runners may not otherwise cross this gate. Independent tasks within a released subphase can run concurrently with one owner per output path.

### Decisions that implementation must preserve

- NQ is the execution asset. Study 2020 onward on owned data, using earlier data only for causal lookbacks. Include every matching session within an account day; source branches retain their particular clocks. No position crosses the account-day boundary.
- Other assets do not run Jumbo, Green Bird or Sires clones. Their custom locations are gamma, vega, vanna, OI, rolling-volume improvements, VWAP/bands and prior highs/lows. Flow and response may come from another asset. A location on A, response on B and execution on NQ is allowed without an NQ local touch for a separately named custom candidate. Source-linked NQ methods keep their required NQ stages.
- Cover native NDX/NDXP, SPX/SPXW, QQQ, SPY, NQ, ES and their owned option chains. Verify availability before claiming native coverage. Missing native cash-index intraday prices cannot be replaced with a futures conversion labelled native. YM/RTY and volatility indices/futures are contextual inputs where owned.
- Garman–Klass, Yang–Zhang, HAR-RV and IV features feed **one fitted volatility expert**, with multiple forecast heads. Do not build a separate fitted expert for each of these estimators. Different major context mechanisms and source strategies have separate fitted artifacts and diagnostics.
- Phase 2 includes method-specific day/context/setup classification, path forecasts, session suitability, branch/reference/confirmation recommendations, timing and target ambition. It is more than a global market-state classifier.
- Search breadth first using a small representative bank, then focus on evidence-supported mechanisms. Preserve opportunity frequency, missed moves and confirmation delay alongside quality. Source matching is a bounded construction check; it is not the optimization objective.
- Use owned data only. Missing inputs get precise availability dispositions; no paid acquisition proposals or external account actions are part of these packs.
- The eventual economic objective jointly optimizes profit and downside. The user's ambition is $3,000 per trading day, with less than $1,000/day unacceptable for the eventual system and a $1,000 maximum daily loss measured from day-start. Keep every eligible zero-trade day visible. A historical average cannot substitute for that daily requirement. Phase 1.5/2 component admission is not certification that this objective is achievable.

### Retention, failure attribution and revisits

[Retention rules](/workspace/.worktrees/docs-amend/planning/research-program/RETENTION.md) add bookkeeping and bounded revisits; they change no formula, budget, gate or date of the existing banks.

1. **Nothing is discarded.** Every registry branch stays in the retention set through Phase 4 with a status: `active_selected`, `active_baseline` or `inactive_retained`. Every attempted candidate keeps its full population definition, parameters and diagnostics in the trial ledger. "Inactive" means not consumed by the next phase's training by default; it never means deleted.
2. **Failure attribution.** Every deselected, inconclusive or not-promoted candidate records `failure_attribution` on its TrialRecord: an ordered list drawn from `frequency` (entries below the frequency floor), `location_miss` (objective not reached while price came within 0.25 S of it, or adverse excursion beyond 0.5 S before any favorable 0.5 S), `confirmation_delay` (missed-move share above the family median), `adverse_before_target` (stop-first share above the family baseline), `cost_sensitivity` (sign reversal under the stress setting), `support` (below the support gate), `coverage` (unexplained input coverage loss). Each is computed from the diagnostics the Strategy Book already reports, with the thresholds fixed before any candidate result is read.
3. **Bounded revisits.** Phase 3 re-screens every retained candidate whose first attribution is `location_miss`, using its improved locations. Phase 4 re-screens every retained candidate whose first attribution is `confirmation_delay` or `adverse_before_target`, using the response and entry experts. A revisit is one registered pass over the retained set with the same folds, scores and promotion gates; it is not a new open search and adds no neighbors.
4. **Phase 2 is split.** Strategy-agnostic context experts (joint volatility, remaining range and passage time, auction and day state, options flow and exposure, intraday OI, cross-market coupling) are fitted once in Phase 2 and are final inputs to Phases 3 and 4. Method-specific suitability experts and conditional plans fitted in Phase 2 are provisional: they are fitted on B0 or the selected rule with baseline locations, and they must be refit in Phase 4 on the final rule-plus-location combination before any decision integration. Phase 2 produces dispositions for strategies, never discards.
5. **Every release reports the retention set** with statuses and first attributions, so a reader knows what is inactive, why, and which later phase will revisit it.

### Reading and starting

Start at the selected phase README, then use its `PROMPTS.md`. Each subphase has a generated `RUNBOOK.md` containing the applicable contracts and its task cards. The coordinator reads one runbook; a worker receives one task card plus the named contract sections. Bundles are generated from canonical files, never independently edited.

[Shared contracts](/workspace/planning/research-program/README.md) · [Execution method](/workspace/planning/research-program/WORKFLOW.md) · [Conversation scope audit](/workspace/planning/research-program/SCOPE_AUDIT.md) · [Workflow repository review](/workspace/planning/research-program/METHOD_REVIEW.md) · [Decision ledger](/workspace/planning/phase-1-live/NEXT_PHASES_DISCUSSION.md) · [Shared wiki](/workspace/wiki/index.md).

Phase 1 source definitions and archived evidence remain read-only. New code belongs to the namespaces named in the task cards. New reports get new immutable run directories. Do not patch an accepted report, source file or old scanner merely to make a comparison look better.

Canonical source: [WORKFLOW.md](/workspace/.worktrees/docs-amend/planning/research-program/WORKFLOW.md).

## Execution and handoff contract

Read this as an implementation work order when the user starts a pack. The current artifact is a plan. A task is complete only when its declared behavior is implemented and verified, or its explicit data/identifiability gate returns an evidenced terminal disposition. Merely writing a report, passing toy tests or finding no profitable variant does not prove implementation completeness.

All 46 tasks and all 17 subphases also obey [ASSURANCE.md](/workspace/.worktrees/docs-amend/planning/research-program/ASSURANCE.md) and their assigned [silent failure checks](/workspace/.worktrees/docs-amend/planning/research-program/SILENT_FAILURES.md). This is acceptance amendment `research-assurance-2026-09-14-v2`, recorded in [AMENDMENTS.json](/workspace/.worktrees/docs-amend/planning/research-program/AMENDMENTS.json). The original `00-foundation` completion failed independent review; use [the repair work order](/workspace/.worktrees/docs-amend/planning/research-program/FOUNDATION_REPAIR.md) before `01-native-and-outcomes`. Existing Phase 1 acceptance remains under its original protocol. The casebook adds specific software checks; it does not enlarge the research search space.

The task graph/cards describe the frozen specification and retain their authoring status. Track actual execution progress in verified receipts and the shared wiki; do not alter a frozen task's content/check boxes merely to record completion and thereby change its plan identity. A real specification amendment gets a new version and exposure record.

The user's Grok build includes pstack. Enter through the generated `/poteto-mode new task` prompts and follow [PSTACK_EXECUTION](/workspace/.worktrees/docs-amend/planning/research-program/PSTACK_EXECUTION.md) for installed-playbook routing, Grok-only role overrides, bounded worker briefs, decision trails and host-capability adaptations. The router chooses supporting skills. The task cards remain the authority for formulas, finite experiments and completion.

### Work shape

One coordinator owns a subphase. It first checks predecessor receipts, then owns the first end-to-end slice through implementation and review. Only after that slice works may it expand to independent tasks. Use native Grok or the user's permitted poteto-agent workers, with every pstack role inheriting the parent Grok model. Default at most three live agents including the coordinator. A shared checkout has one code writer at a time; read-only analysis may run independently. Do not substitute Astra, Fable or archived Cursor mill workflows. If no permitted worker is available, execute the same task cards sequentially and record the review limitation.

The coordinator owns shared schemas, runners, registries, dependency integration and the subphase receipt. Workers own only the paths named in their cards. Shared helper changes go back to the coordinator as a concrete proposed patch; two workers never modify the same shared file. Each worker gets one bounded task, its required contract sections, exact predecessor artifact paths and the current code revision. It must not browse the whole source archive or invent another plan tree.

Use existing isolated working roots only when the coordinator can supply the actual path mapping and exclusive output ownership under the repository rules; otherwise serialize writers in `/workspace`. All Git operations remain within `/workspace`. Do not let workers create/reset worktrees or perform concurrent Git operations. Do not reset, clean, stash or overwrite other work. Record unrelated working-tree changes at task start.

### Task loop

1. Read the task's goal, allowed paths, input schemas, equations, fixtures, acceptance checklist and assigned assurance case IDs. Confirm its dependencies are verified; an external subphase dependency also needs its matching passing GATE_REVIEW.json. Inspect the named existing functions; the docs distinguish existing adapters from proposed code.
2. State the smallest observable behavior to add. For a meaningful new numerical or causal behavior, first add a fixture that fails if the behavior is absent or wrong. Do not test a copied implementation against itself.
3. Implement pure calculations separately from native I/O and orchestration. Use typed dataclasses, explicit units and enums; reject invalid inputs at the boundary. Avoid hidden global fitting state, implicit clock conversions and broad exception-to-zero fallbacks.
4. Run the task's targeted tests, including at least one discriminating negative or future-perturbation test. For a data task, run its declared native slice and reconcile identities, row counts, coverage and actual output fields.
5. Trace a real output back through model inputs to native receipts. Verify that each advertised input reaches the actual predictor matrix; a computed but unused feature does not satisfy the task.
6. Inspect the diff and output artifacts. Record commands, exit codes, duration, artifact hashes, tests, limitations and exact disposition in the task evidence matrix and receipt. Run the assigned failure probes with valid controls. No new task starts until its dependencies' receipts pass the verifier; subphase closure additionally requires the separate review described in ASSURANCE.md.

Keep the matched playbook steps and task progress in the run's `WORK_LOG.md`; record skipped steps with their concrete reason. Use the installed show-me-your-work format in the run's `DECISIONS.tsv`. The coordinator owns its log, each writing worker owns a separate log, and closed receipts hash the logs through their artifact manifests. Do not copy runtime progress into frozen task cards or let workers share an append target.

The implementer follows the current repository test runner and existing dependency environment. Do not install arbitrary new ML packages: the specified first release uses the existing pinned NumPy stack. Any needed dependency change requires its own small documented task and reproducible lock update before model code uses it.

### Receipts and statuses

Proposed code owner `P15-00` creates the shared receipt serializer; `P15-01` creates its validator. A task writes `implementation/reports/research-work/<task-id>/<run-id>/TASK_RECEIPT.json` and `REPORT.md`. Large caches and model-row shards belong under ignored `/workspace/data/derived/trading-research/`; the report records relative shard paths, hashes, row counts and availability, never just an unverified path.

```python
from typing import Literal, TypedDict

Disposition = Literal[
    "implemented_verified", "retained_baseline", "rejected_by_evidence",
    "inconclusive_support", "unsupported_owned_input", "blocked_implementation"
]

class TaskReceipt(TypedDict):
    schema_version: str             # "research-task-receipt-v2"
    assurance_version: str          # "research-assurance-2026-09-14-v2"
    task_id: str
    run_id: str
    plan_sha256: str                # recomputed PLAN_SNAPSHOT file-map identity
    code_sha256: str                # recomputed CODE_SNAPSHOT document identity
    predecessor_receipts: dict[str, str]  # task ID -> receipt sha256
    command_results: list[dict]     # argv list, cwd, exit_code, seconds, log path/hash
    artifact_manifest: list[dict]   # path, sha256, bytes, rows or null, schema
    acceptance_checks: dict[str, bool]
    disposition: Disposition
    reason: str
    coverage: dict
    unresolved: list[str]
```

`blocked_implementation` never closes a phase. `unsupported_owned_input` closes only the affected research cell after the owned-data search and dependency alternatives specified in the card are evidenced; it cannot excuse missing generic implementation. `inconclusive_support` requires a correctly implemented and executed finite experiment. Every required capability needs software verification even if a particular asset/date has no native coverage. A phase with missing mandatory native inputs is `closed_with_limits`, not `complete_native_coverage`.

A subphase produces `SUBPHASE_RECEIPT.json`: ID, task receipt hashes, accepted schema versions, native slice IDs, test evidence, coverage dispositions, single-writer audit and `gate = pass | closed_with_limits | fail`. Only the coordinator writes it. A final phase receipt adds trial-ledger hashes, all family dispositions, prediction/rule artifact hashes, exposure history and a machine-readable downstream allowlist. Preserve failed attempts in separate run directories; never relabel a failed run as the accepted one.

### Verification commands to implement

`P15-01` creates `implementation/tools/verify_research_release.py` with subcommands `task --receipt PATH`, `subphase --receipt PATH`, `phase --receipt PATH`, and `lineage --manifest PATH`. Each command exits 0 only when its schema, referenced hashes, required acceptance keys, dependency graph and scope gates pass; otherwise exits 2 with machine-readable failures. A report saying PASS is not sufficient. The phase verifier checks every task in `TASK_GRAPH.json`, including allowed terminal statuses and phase-boundary gates.

Under the v2 amendment, implement the exact inventory, parsed-schema, row-count, snapshot/draft identity, recursive dependency and evidence-matrix rules in ASSURANCE.md. Subphase/phase commands accept `--gate-review PATH` for final admission, which additionally validates the separate review and its code/receipt/evidence hashes. A bare candidate verification cannot authorize the next subphase. Tests include valid candidates, failed parents with correct hashes, wrong-task receipt reuse, unknown empty subphases, missing actual prior releases, forged review/matrix evidence and each assigned negative. Never excuse a failed required command through free-text `unresolved`.

`P15-02` creates `implementation/tools/run_rule_discovery.py`; `P2-00` creates `implementation/tools/run_context_experts.py`. Both use `freeze`, `slice`, `run`, `resume`, `summarize` subcommands. Exact common arguments: `--run-root PATH --manifest PATH`; `slice` additionally accepts `--dates YYYY-MM-DD,... --task ID`; `run`/`resume` accept `--workers N` and `--task ID`. Freeze writes immutable configuration and identities before any outcome-dependent selection. A conflicting existing run root is an error, not an overwrite. Task cards name additional subcommands where needed.

### Run naming and manifests

The coordinator creates a draft manifest containing task_id, plan contract hashes, exact predecessor receipts, code/input identities, registered candidate/model config, declared study dates and engineering-date manifest. P15-00 supplies the baseline-bound template; later tasks fill only their owned configuration. Semantic run ID is the first 16 hex characters of SHA256 of this canonical manifest. Task evidence defaults to `implementation/reports/research-work/<task-id>/<semantic-id>/attempt-0001/`; retries use the next attempt number and reference previous attempts without overwriting them. Phase release indexes collect these artifacts under their specified release directory. Large data shards remain in the ignored derived-data root.

`freeze --manifest DRAFT_PATH --run-root ACTUAL_RUN_ROOT` verifies the draft and writes `FROZEN_MANIFEST.json` plus input/config identities. All subsequent commands pass that frozen file as --manifest and the same actual root. Identical freeze input may verify/reuse an existing frozen root; conflicting input fails. The coordinator supplies actual roots/manifests/date lists to workers, replacing the clearly labelled placeholders in cards. Workers never choose dates or models from observed results.

### Native slices and resource discipline

Freeze eight complete eligible engineering dates per required input group: first complete date in each available calendar year 2020–2026, plus the complete date nearest 2023-11-05 (DST transition), ties earlier. For missing years write explicit missing slots; do not replace them with favorable outcomes. Include separate fixtures for a partial final date, a roll, an unverified holiday, a feed gap and same-timestamp conflicting events. The frozen date manifest is created from coverage metadata before scanning outcomes. Engineering dates remain disclosed exposed dates. For fitted experts the slice limits evaluation/output dates; fitting still uses the full declared preceding training/tuning/calibration history. Do not fit on just eight engineering dates and call the resulting low support a completed model experiment. Component tasks implement and verify recipes on these slices; P15-17/18 and P2-24 own the declared full search/replay. Registered B0/B1/B2 options versions are evaluated through the same dependency runner with new immutable artifact IDs, reusing already implemented fit recipes when B2 becomes available. No earlier B0 artifact is overwritten.

Profile one date and four dates before a census. Persist one canonical native transform per input hash/contract/date/transform version. Default 4 process workers, increase to 8 only if measured peak memory at four workers projects below 60% of available RAM and I/O throughput improves by at least 20%. Never exceed 16 without a new resource receipt. Deterministic results must match at 1 and 4 workers. Abort and record `resource_limit` when projected free disk after the run is below 20% or below twice the next shard size. Resource aborts are implementation work remaining, not evidence against a research hypothesis.

Each task run has a 2-hour slice budget; each full registered search stage has a 24-hour wall-clock budget after profiling. Checkpoint per account day. A timeout writes an incomplete receipt and resumes the same immutable run; it never drops slow dates. Finite candidate counts are defined in the phase search contract. Increase budgets only through a recorded plan amendment made before resuming, not by secretly reducing coverage or tests.

### Review and final reporting

Review numerical behavior against this specification and separately review code quality. For charts, generate deterministic cases: positive, negative, missing, ambiguous, earliest/latest by time and worst residual; do not choose attractive examples. Inspect the required charts visually and save the list and findings. Full-archive chart spam is not required.

The coordinator/fresh permitted reviewer reads actual code and artifacts before the author's summary, reproduces counterexamples, independently recalculates a central result and traces native evidence. Review of logs alone is not behavioral review. Each subphase ends with a separate `GATE_REVIEW.json` binding the immutable candidate receipt, current code, every task matrix and required independent results. A final phase uses its own review sidecar as well. Do not mutate the candidate to hash its own final verification. All unresolved correctness/causality/integrity findings prevent admission, even with green unit tests. Record review limitations honestly; a fixed test suite reduces known failure modes but is not a proof of all behavior.

Every family report and phase summary prints both workspace-mandated tables:

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| example | registered ID | complete eligible observations | not claimed unless source-exact comparison exists | verified disposition | actual report |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| example | task ID | evidence disposition | pass/fail | count | count | support, limitations, baseline retained |

At handoff give the user the completed subphase, verification evidence, exact limitations, next eligible prompt and real artifact links. Update the shared wiki with concise definitions/status and links to immutable evidence; do not paste full reports into multiple wiki pages. No external messages, publishing or trading are authorized by these packs.

Canonical source: [CONTEXT.md](/workspace/.worktrees/docs-amend/planning/phase-2/CONTEXT.md).

## Context, path, auction, flow and cross-market experts

Owners `P2-05` through `P2-08`. Use independently fitted artifacts and the common chronological fitting, support and calibration contracts. Thresholds in this file define **our operational v1 labels**, not author-exact Sires/AMT or jetbundle constants. Preserve raw source terminology and the source-object distinction in the wiki.

### Common causal features

Let q=.25 for NQ, S be the prior 60-matching-minute scale. For a complete window W define range R=H-L, efficiency `ER=abs(C-O)/max(R,q)`, close location `(C-L)/max(R,q)`, signed displacement `(C-O)/S`, and volume intensity `V/median(prior20 same-bucket V)` with missing if history<10. Value overlap of bands A,B is `max(0,min(A.hi,B.hi)-max(A.lo,B.lo))/max(q,min(widthA,widthB))`; value migration is `(POC_now-POC_prior)/S` and signed VA-edge changes. Current profiles use only completed events through issue time. Composite profiles combine exactly prior 5 or 20 complete same-contract account days, never future or reselected sessions.

Opening descriptors compare first available opening price with prior VAH/VAL and high/low; store four distances/S and categorical inside-value/above-value/below-value/outside-prior-range. During the first 30 minutes, a provisional open type uses completed 5-minute bars: drive if ER>=.7 and no close returns through opening price after the first bar; rejection-return if a prior range edge is swept then price closes back inside; otherwise auction. This label is unavailable before enough bars; after 30m it is a completed descriptor, not something known at the open. IB is first 60 RTH minutes, unavailable before 10:30 ET or the corresponding interrupted/short-session completion.

### Range-path expert

Forecast directional remaining extrema from current midpoint p: `U=max_future(P-p,0)/S`, `D=max_future(p-P,0)/S` for next 30,60,120 matching minutes and remaining account day. Fit .1/.5/.9 quantiles using the common pinball recipe, independently named heads within this expert. Features include range already consumed, current value/side, source range boundaries, prior directional excursions, joint-volatility **causal predictions** and their uncertainty. Do not use a future observed daily range as a normalization denominator.

Break topology uses a frozen reference [L,H] available at t. In `(t,end]`, a strict crossing beyond H+q or below L-q counts. Classes are `none`, `up_only`, `down_only`, `up_then_down`, `down_then_up`; if first crossings are inseparable in one native batch, target=`ambiguous`, excluded from the primary class loss but counted. Reference is each active source range, then prior account-day range as fallback. Forecast next 60 minutes and remaining account day separately. No later-resized range can redefine the earlier topology.

Post-first-break behavior is a separate target. For the first unambiguous break, inspect next five complete one-minute closes: acceptance if >=3 close beyond the broken edge by>=q and no close penetrates the opposite edge; rejection if a close returns inside before acceptance and a subsequent close reaches the range midpoint within 30 matching minutes; otherwise unresolved/other. Do not assign the post-break label at break time; label-known-at is the final required observation. Also measure whether the opposite edge is later crossed and its delay, so double-break frequency cannot masquerade as useful reversal quality.

First-passage timing: thresholds+.5S,+1S,-.5S,-1S; bins `(0,5],(5,15],(15,30],(30,60],(60,120]` matching minutes. For each threshold, fit discrete hazards with the common binary logistic recipe on expanded at-risk rows, including a one-hot bin index. A row contributes failure0 for each fully observed no-event bin, event1 for its first crossing bin, and no later rows. Right-censor at coverage/allowed end, recording the partial final bin without a false0. Survival `S_k=product_(j<=k)(1-h_j)`; event-bin probability=`S_(k-1)*h_k`. Output cumulative arrival probabilities, conditional median bin when cumulative probability reaches.5, and `not_reached_by_120` probability. Report likelihood, calibration by bin and censoring counts.

Fixtures: range[99,101], native future102 then98 gives up_then_down; same-batch[98,102] gives ambiguous. A completely observed path100 throughout gives none and every relevant completed hazard bin failure0. A gap at 7m yields first bin0 and later censoring, not five zeros.

### Auction/session expert

At every snapshot classify a current operational state from the preceding30 matching minutes: trending_up/down when ER>=.65 and signed displacement magnitude>=.5; balance when ER<=.35 and value overlap with the preceding30m>=.5; failed_auction when a previously frozen edge is swept and reclaimed with subsequent2-tick favorable close; otherwise transition. Priority is failed_auction, trending, balance, transition. This deterministic current-state descriptor feeds, but does not replace, a fitted next 30/60-minute state-transition model.

For the completed RTH day label, compute IB width W and final range/close/ER, using the source day-type vocabulary only with suffix `operational_v1`: neutral if both IB edges are strictly broken; trend if max one-sided extension beyond IB>=W, day ER>=.5 and close location>=.8 or<=.2 in that direction; nontrend if final RTH range<=.75*median(prior 20 complete RTH ranges); normal_variation if max extension>.5W; normal otherwise. Apply this exact priority. Missing IB/prior history gives unknown. Before RTH completion this is a forecast target, never a current input. Publish a confusion table and explicit source-taxonomy limitations.

Session opportunity quality targets each forthcoming analysis bucket within the account day: occurrence of at least one eligible frozen rule opportunity; total eligible count; first opportunity time; and the fixed benchmark's net points conditional on occurrence. Complete no-opportunity bucket means occurrence0/count0 and conditional utility missing. Use log1p count ridge (inverse exp minus1 clipped0) plus occurrence classifier and conditional utility ridge/quantiles. Include eligible source family masks so a session is not penalized for a method whose source clock forbids it. Show each session's prediction contribution, not only RTH aggregate.

Hinge products: value_migration×volume_intensity, range_consumed×vol_forecast30m, open_distance_VAH×overnight_return, ER30m×CVD5m, IB_extension×time_since_open, value_overlap×prior_session_range. Fit transition, day-type and session-quality heads, keeping their target populations distinct.

### Flow-memory expert

Use Phase 1.5 CVD/cohort calculations, with separate buys/sells,30/120/300s markouts, unknown volume, age and unresolved counts. Additional features: rolling 120s adverse/favorable displacement per known aggressive contract; failed push count (pressure above prior 20-bucket .75 quantile with progress<=.1S); defended contact count; consecutive known favorable response duration; and BBO depth/spread changes. BBO size changes alone do not prove cancellation/refill or ten-level order-book state.

Forecast next 30m directional excursion, first-passage probabilities and whether current rewarded aggression persists: future resolved cohort signed markout remains>0 for at least 60% of known volume. The latter target's label availability includes the cohort markout horizon beyond its trade window; purge accordingly. Separate `aggression_reward`, `defense`, `failed_push` feature groups and ablate each. A high delta without favorable subsequent markout must not be called rewarded.

### Cross-market expert

For each owned related asset normalize returns/range by its own causal volatility/scale and preserve native units. Compute log-return correlations on trailing 120 matching one-minute pairs at lags -5..+5; a pair exists only when both timestamps/quotes are valid and available by t. Minimum 60 pairs per lag. Positive lag means the related asset's earlier return is paired with a later NQ return; write that convention into columns. These are historical associations, not proof of causal leadership. Future perturbation must not alter any lag feature.

Multi-scale SMT descriptors use 5,15,60-minute completed windows and confirmed two-right-bar pivots. Bullish divergence: NQ has a newly confirmed lower low relative to its preceding confirmed low while the related asset's matched window low is not lower than its own preceding low; bearish symmetric. A matched window is the same wall-time interval intersect both products' matching hours, not a cherry-picked related pivot. Preserve divergence age, price displacement, confirmation delay and coverage. Report pairwise and pooled contribution; no NQ local level touch is required for these context features.

Spot/IV coupling features are paired changes in native underlying return and ATM IV over 5/30/60 minutes, rolling correlation, and residual NQ return after trailing 120-minute ridge on contemporaneously available related returns. Forecast NQ next 30/60-minute directional/variance surprise relative to the causal joint-vol baseline. Hinge products: NQ_ES_divergence×ES_flow_reward, NQ_QQQ_divergence×QQQ_IV_change, spot_return×ATM_IV_change, lag1_corr×related_return5m, correlation_change×NQ_range_consumed, related_gamma_change×NQ_return5m. Unsupported assets produce masks and per-asset dispositions, not synthetic native prices or cloned source setups.

Canonical source: [MODEL_FITTING.md](/workspace/.worktrees/docs-amend/planning/research-program/MODEL_FITTING.md).

## Exact first-release model recipes

Owner `P2-02`; Phase 1.5 may reuse quantiles/ridge only where its registered candidate requires them. Proposed module `research/experts/fitting.py`. The first release uses the existing pinned NumPy float64 stack, with no network model service. Different experts have different fitted artifacts. The joint volatility expert has one fit interface and one multihead artifact containing all historical and IV features.

### Preprocessing

Fit every transformation on the current fit partition only. For each feature: convert nonfinite values to missing with a reason, append a binary missing mask, impute the training median, and standardize by training mean and population standard deviation. If a column has no observed training values, impute 0, leave scale 1 and flag unsupported; do not claim it contributed. A constant column uses scale1. Clip standardized values to [-10,10], preserving a clipped flag for diagnostics. Categorical values use a frozen domain vocabulary plus `unknown`; no full-dataset category fitting. Do not impute targets.

Quantile implementation is linear interpolation: sorted `x`, `a=(n-1)p`, `i=floor(a)`, `Q=x[i]+(a-i)*(x[min(i+1,n-1)]-x[i])`. Empty returns unavailable; n=1 returns the only value. Fixture `[0,10,20,30]`, p=.25 gives7.5. Fitted transformations persist ordered columns, medians, means, scales, vocabulary, knots, training IDs and hashes.

### Ridge and nonlinear challenger

`fit_ridge(X, Y, target_mask, row_weight, alpha, transform) -> ModelArtifact`; `predict(artifact, X) -> float64[n,h]`. Add intercept column1. For each output h within the same artifact solve `(X_h.T W_h X_h + alpha D) b_h = X_h.T W_h y_h`, where `D=diag(0,1,...,1)`, available-target rows only, and weights sum to1 per head. Use `numpy.linalg.solve`, falling back to `lstsq` only on a recorded singularity. One shared preprocessing/feature matrix, one alpha chosen across supported heads, and one serialized coefficient matrix constitute the joint fit. Separate GK/YZ/HAR models are ablations, not the production architecture.

Alpha grid `{.001,.01,.1,1,10}`; default `.1` if tuning is unsupported. Equalize account-day weight: each row gets `1/n_rows_on_its_day`, then normalize within available targets. Multiple heads get equal tuning weight after the shared evaluation normalization. Prediction fixture: X=[0,1,2], y=[1,3,5], alpha0 must produce intercept1,slope2 within 1e-10.

Nonlinear challenger `hinge_ridge`: take standardized continuous features, append `max(0,x-k)` at each training .25/.5/.75 quantile knot, removing duplicate knots. Retain the original linear and missing-mask columns; do not hinge masks or categorical one-hot columns. Append pairwise products only for the explicit feature-pair list in each expert contract, at most 12 pairs. Same ridge solver and alpha grid. This is a specified nonlinear function basis, not an invitation to an unbounded model zoo. Tune linear versus hinge once per expert/outer origin. If tied within 1%, choose linear.

### Probabilities

`fit_softmax(X, y, class_names, row_weight, l2) -> ModelArtifact`. Stable logits `z=X B`, `p_k=exp(z_k-max z)/sum exp(z-max z)`. Minimize weighted mean negative log likelihood plus `(l2/2)*sum(nonintercept B**2)`. Gradient `X.T@(w[:,None]*(p-onehot)) + l2*D@B`. Initialize B=0; use full-batch gradient descent, learning rate `1/(.5*||sqrt(W)X||_2**2+l2+1e-12)`, maximum 5,000 iterations, stop when relative objective change <=1e-9 for 10 consecutive iterations. Log objective trace; nonfinite or increasing loss beyond1e-10 is a solver failure. L2 grid `{.001,.01,.1,1}`, default.1. Use the same linear/hinge basis choice as the declared expert candidate.

Calibrate probabilities with one temperature T in `{.5,.75,1,1.5,2,3}` minimizing calibration log loss; ties choose T closest to1, then lower. Apply softmax(z/T). Calibration does not change feature coefficients. For unsupported fits, output Laplace-smoothed historical class probabilities `(n_k+1)/(n+K)`, support=`low_support`, fit cutoff and counts. For an absent required class this is a fallback, not a successfully learned classifier.

Binary Brier=`mean((p-y)**2)`; multiclass Brier=`mean(sum_k(p_k-onehot_k)**2)`; log loss clips p to[1e-12,1-1e-12] only for evaluation. Reliability bins use fixed probability edges0,.1,...,1 and report bin counts; do not average empty bins as zero error. Constant-probability and session-frequency baselines use training labels only.

### Quantiles, positive means and intervals

For nonnegative variance targets fit `z=log(y+1e-12)`. A mean variance forecast is `max(1e-12, exp(pred_z)*mean_train(exp(residual))-1e-12)`, where residuals are chronological training predictions, never in-sample residuals or test residuals. If fewer than 100 causal residuals on30 days, smearing=1 and mark calibration low-support. QLIKE=`y/v+log(v)` for v>0 including y=0; compare differences to avoid irrelevant additive constants. Fixture y=4: v4 gives1+ln4; v2 gives2+ln2, which is worse.

For excursion/time quantiles use linear/hinge quantile regression, minimizing weighted pinball `rho_tau(u)=u*(tau-1[u<0])` plus `(l2/2)||b_nonintercept||²`. Implement deterministic Adam with initial b=0, lr.01, betas(.9,.999), epsilon1e-8, 5,000 steps, full-batch gradient `-X.T@(w*(tau-(y<Xb)))+l2*D b`; at exact equality set that row's residual subgradient to0 before multiplying by X. Adam bias correction uses the one-based step. Keep the best objective iterate, require relative improvement<1e-7 across last 200 steps or flag convergence failure. L2 `{.001,.01,.1}`, default.01; taus .1,.5,.9. Sort predicted quantiles per row to remove crossing and report the raw crossing rate. Nonnegative targets clip quantiles at 0; do not alter signed-return targets.

For calibrated 80% intervals around a point forecast, use absolute residuals on the disjoint calibration block. `k=min(n,ceil((n+1)*.8))`; radius is kth smallest absolute residual (one-based). Bounds=`pred±radius`, lower floored0 only for nonnegative targets. For log-variance intervals calibrate absolute log residuals then exponentiate; distinguish mean estimate from median/log-center. Minimum 100 residuals on30 days. Report empirical coverage, width and coverage by session/horizon; no exchangeability or guaranteed coverage claim under market drift.

### Adaptation and artifact checks

Every estimator implements `fit(dataset, split, config)`, `predict(snapshot_batch, artifact)`, `serialize`, `load` and `explain_inputs`. Loading validates schema, hashes, feature order, target units and training/availability cutoffs. Round-trip predictions must agree at absolute/relative1e-10; parallelism may not change candidate selection. Do not pickle untrusted arbitrary code; use JSON metadata plus NumPy arrays with `allow_pickle=False`.

Required discriminating checks: reverse labels and observe changed predictions; remove an actually used input and observe the declared ablation matrix change; append future rows and prove all earlier transforms/predictions unchanged; permute input columns with correct names and recover identical predictions; rename/miss a required column and fail; insert a never-observed IV group and obtain a mask/fallback rather than a fabricated contribution. Positive-control synthetic data has a known signal only in an IV feature and must favor the joint model over the historical-only ablation on held-out synthetic rows.

Canonical source: [EVALUATION.md](/workspace/.worktrees/docs-amend/planning/research-program/EVALUATION.md).

## Chronological evaluation and selection

Owner: `P15-03`, extended by `P2-02` and `P2-24`. These are registered research defaults. They define a finite experiment; they are not claims about trading edge.

### Freeze and exposure

The Phase 1 baseline is the [acquired measurement](/workspace/implementation/reports/phase1-live/historical-measurement/MEASUREMENT_REPORT.md), run `run-1.0.1`, and its immutable registry, scope, composed calendars, input manifests and accepted implementation identities. `P15-00` reads the actual receipts rather than deriving identity from a folder name. Preserve all 1,742 declared labels and each branch's eligibility; do not make every branch complete by borrowing another branch's denominator.

All existing dates have some research exposure. Record Phase 1 engineering/reconstruction/measurement and this plan's design exposure. The following are chronological out-of-sample comparisons of newly fitted rules/models, **not an untouched holdout**. Freeze candidates, search limits and scoring before running them. A result-driven amendment creates a new exploratory version and adds exposure; it never reuses the same dates as fresh confirmation.

### Outer and inner splits

Outer test blocks are calendar years 2022, 2023, 2024, 2025 and the acquired part of 2026. Earlier dates are training/lookback only. Within outer year `Y`, initial fitting data end June 30 of `Y-1`; tuning is July 1–September 30; calibration is October 1–December 31. Choose candidates/hyperparameters on fit+tune as specified below, refit chosen parameters through September 30, and calibrate only on October–December. Test year outcomes never choose that year's candidates.

Examples: for test 2022, initial fit is 2020-01-01 through 2021-06-30, tune July–September 2021, calibrate October–December 2021. For test 2025, initial fit expands through June 2024. Missing years/inputs stay missing; no random split fills them.

Purge any training row whose label interval overlaps a tune/calibration/test interval or whose label was not available before the fitting cutoff. Add one entire eligible account day between adjacent partitions; the earlier partition loses the boundary day. Group all events, variants, overlapping horizons and assets from one account day together. No row-wise shuffle split, ordinary IID standard error, or random-fold stacking.

Hyperparameter tuning uses the fixed grid in [model fitting](/workspace/.worktrees/docs-amend/planning/research-program/MODEL_FITTING.md). Rule selection uses the finite bank in the [Phase 1.5 search contract](/workspace/planning/phase-1-5/SEARCH_CONTRACT.md). Ties within 1% of the best tuning loss/score choose the simpler model, then lower candidate ID lexically. Complexity order is constant/base rule, linear, hinge basis, combination; fewer changed axes wins within an order. Never use test results to break ties.

### Causal stacking and adaptation

Generate every upstream training prediction chronologically. Use consecutive 20-eligible-day blocks; for each block, fit on prior available labels and reserve the most recent 42 eligible prior days for calibration. Minimum fit history is 126 complete days and 500 rows. Hyperparameter selection uses the 42 eligible days immediately before calibration, with training before that; if unavailable, use the declared default hyperparameters. A fold therefore may have no supported upstream predictions early on. Preserve the warm-up mask and loss of training support.

Any Phase 1.5 selected-rule role used in a historical Phase 2 row must be selected using evidence available before that row's block. Do not apply the global 2026 winning rule backward as if it had been selected in 2022. Persist `selection_manifest_id`, its cutoff and all candidate IDs for each block. Always retain the fixed source baseline features. For scarce cells, use the baseline role and mark selection unsupported.

Initial Phase 2 comparison holds parameters fixed for an outer test year. The adaptation experiment later compares: fixed annual; monthly refit at the first account-day open; weekly refit at Monday account-day open; and monthly refit plus intraday intercept updates. Refit uses a fixed trailing 756 complete eligible days (or all available if fewer), with the trailing 42 days reserved for calibration. The selected model/rule families and hyperparameters remain frozen for the outer year. Intraday updates may consume only matured, published labels, per the exact update rule in the Phase 2 adaptation contract. Every fit is versioned and becomes available at the next scheduled issue after measured fitting completion, never retrospectively at its data cutoff.

### Support and honest terminal outcomes

For a fitted continuous expert: at least 500 complete training rows on 100 account days, and 100 evaluation rows on 30 days. For a binary head: additionally at least 20 examples of each class on at least 10 distinct training days. For multiclass: apply that condition to each class; unsupported classes are pooled into an explicit `other_low_support` only if the target contract allows it, otherwise use the empirical prior and mark the head low-support. Never silently remove rare source branches.

For a Phase 1.5 upgrade: at least 100 resolved benchmark opportunities on 30 eligible test days in aggregate, represented in at least three outer blocks. A branch below the gate is `inconclusive_support`, even if all six examples succeed. It remains in the registry and downstream baseline allowlist, with low-support status. Support gates are research defaults and their counts must be shown alongside sensitivity at half/twice the gate; changing the gate cannot manufacture a claim. A disposition never deletes a candidate: `inconclusive_support`, `rejected_by_evidence`, `retained_baseline` and `unsupported_owned_input` keep the full population, parameters and diagnostics in the trial ledger and the retention set; "inactive" means not consumed by the next phase's training by default.

### Trial ledger

`TrialRecord`: trial_id, parent_trial_ids, family, branch, outer_fold, stage, bank, exact parameters, code/data/plan hashes, fit/tune/calibration windows, outcome-exposure cutoff, candidate population counts, score/loss, support, all test metrics, reason, disposition, runtime, artifacts, and `failure_attribution`. Write append-only JSONL; a new attempt gets a new ID and `replaces_attempt_id`, leaving the old row intact. Thresholds below are the [retention](/workspace/.worktrees/docs-amend/planning/research-program/RETENTION.md) rule 2 values, fixed before any candidate result is read.

`failure_attribution` is required for every deselected, inconclusive or not-promoted candidate. It is an ordered list drawn from `frequency` (entries below the frequency floor), `location_miss` (objective not reached while price came within 0.25 S of it, or adverse excursion beyond 0.5 S before any favorable 0.5 S), `confirmation_delay` (missed-move share above the family median), `adverse_before_target` (stop-first share above the family baseline), `cost_sensitivity` (sign reversal under the stress setting), `support` (below the support gate), `coverage` (unexplained input coverage loss). Each is computed from the diagnostics the Strategy Book already reports.

Bounded revisits: Phase 3 re-screens every retained candidate whose first attribution is `location_miss`, using its improved locations. Phase 4 re-screens every retained candidate whose first attribution is `confirmation_delay` or `adverse_before_target`, using the response and entry experts. A revisit is one registered pass over the retained set with the same folds, scores and promotion gates; it is not a new open search and adds no neighbors.

### Scores and uncertainty

Each family report contains (a) all attempted variants, (b) common complete-day paired comparisons, and (c) full candidate-specific coverage. A method's own source prerequisites remain in its eligible population. No missing feature/outcome is silently treated as no-setup. Unresolved order is an explicit excluded primary outcome with counts and pessimistic/optimistic bounds.

For setup rules the primary score is the mean daily net points in the deterministic one-contract benchmark in [outcomes](/workspace/.worktrees/docs-amend/planning/research-program/OUTCOMES.md). Compare a candidate with the unchanged baseline on common complete eligible days, including zero-entry days. Also report eligible opportunities/day, retained baseline opportunities, new opportunities, ordered target/stop rate, median net points/opportunity, drawdown from day-start, confirmation delay and missed-move counts. This benchmark measures an isolated family under a fixed scheduler; it is not a combined portfolio or a certification of the user's daily target.

For forecasts: QLIKE for variance; pinball for excursion/time quantiles; multiclass log loss and Brier for probabilities; absolute error for continuous state forecasts; censored time outcomes use the discrete survival loss specified in Phase 2. Report calibration and support for every head, horizon, session and year. Standardize multihead tuning losses by the loss of the training-only baseline, with denominator `max(abs(baseline_loss), 1e-8)` except QLIKE: use QLIKE excess `y/v - log(y/v) - 1` for positive y, and ordinary QLIKE differences for zero y. Average only supported heads with equal head weights; report the supported-head set so missing difficult heads cannot improve the aggregate silently.

Uncertainty uses a paired circular moving-block bootstrap of account days, block length 5, 2,000 draws, NumPy `Generator(PCG64(15022026))`. Draw block starts uniformly within each calendar-year segment and wrap only within that segment; concatenate blocks and truncate to its original day count. Use identical draws for baseline/candidate and all variants. Report percentile 2.5/97.5 bounds of the mean difference. Also report block lengths 1 and 10 as sensitivity, not additional selection opportunities.

For an exploratory one-sided improvement p-value use the centered bootstrap: observed mean difference `d`; each draw computes `d_b`; `p=(1 + count(d_b-d >= d))/(B+1)` under the null of no mean improvement. Family-level p-values include every candidate tested at that decision stage. Apply Holm adjustment: sort p ascending, compare `p_(i) <= .05/(m-i+1)` until the first failure, reject no later hypotheses. Publish raw p, adjusted p, candidate count and all unsuccessful trials. This dependence-aware exploratory procedure does not erase prior exposure or make adaptive search confirmatory.

Promotion requires: software/causality gates pass; support passes; paired mean improvement > 0 with the 95% lower bound > 0; Holm-adjusted p <= .05; at least three supported outer blocks and a positive difference in at least 60% of supported blocks; no cost-stress sign reversal at the declared stress setting; and no unexplained loss of input coverage. Frequency is a second objective: publish the quality–frequency Pareto set. A candidate with <50% of baseline entries cannot replace the family baseline; it may remain a separately labelled high-selectivity option if it passes all other checks. Keep the baseline whenever no candidate clears the gate.

### Economic evidence and limits

Show every eligible account day: net dollars, trades, zero-trade indicator, day-start worst marked P&L, risk-stop trigger, slippage/gap breach, and coverage. Summaries include median, mean, 5th percentile, worst day, fraction below $0/$1,000/$3,000 and fraction exceeding the $1,000 loss limit. Do not replace the user's daily floor with an average threshold, hide zero days or clip a loss to the limit.

Phase 1.5 and Phase 2 may close with retained baselines or negative/inconclusive findings. They cannot claim the final economic goal is met. Only a later combined decision replay can evaluate the integrated historical daily distribution; future realized performance remains a separate question.

Canonical source: [OUTCOMES.md](/workspace/.worktrees/docs-amend/planning/research-program/OUTCOMES.md).

## Outcome labels and fixed execution benchmark

Owner `P15-03`. Proposed implementation modules: `research/contracts/outcomes.py`, `research/contracts/execution.py`. Reuse native batching and coverage from the existing `method_pack` modules; keep future labels in a module that scanners and feature builders cannot import.

### Causal scale and descriptive movement

Tick `q=0.25` NQ points. At time t define `S_t=max(4q, H-L)` from the complete preceding 60 matching minutes on the same contract. If fewer than 60 matching minutes are available, scale is missing, not filled from the future. A scheduled closed interval does not count as a matching minute; a feed gap inside a scheduled minute makes scale missing. This is a fixed research normalization, separate from the Phase 2 forecast.

For direction `s ∈ {-1,+1}` and reference price p, favorable excursion is `max(0, max_u s*(P_u-p))`; adverse excursion is `max(0, max_u -s*(P_u-p))`. Divide by S for normalized values. Use native interval extrema in `(t,t+h]` with h=5,15,30,60,120 minutes and remaining account-day, recording exact elapsed matching/wall time. Fixed horizons extending past the allowed close are unsupported fixed-horizon labels; separately report the truncated-to-close descriptor. Preserve raw Phase 1 labels unchanged.

Example: long p=100, later prices 102,99,104, S=4 gives MFE=4 points=1S and MAE=1 point=.25S. These extrema do not reveal whether a target preceded a stop.

### Ordered outcomes

`first_passage(events, *, start_ns, end_ns, side, entry, stop, target, coverage) -> PassageResult` returns `target_first | stop_first | neither | same_batch_ambiguous | prior_gap_unknown | missing_future | invalid_geometry`, resolution time, evidence IDs and available-at time. Scan entire equal-timestamp native batches; if both boundaries first occur in one batch, ordering is ambiguous. A gap before the first observed crossing prevents certifying first passage. If complete coverage ends without crossing, return `neither`. Require `side*(entry-stop)>0` and `side*(target-entry)>0`.

Ordered diagnostic grid uses stop distances `{.25S,.5S,1S}` and target distances `{.5S,1S,2S}` at horizons 15,30,60,120 minutes and account-day end. Compute all cells as descriptive diagnostics. The registered primary rule comparison uses the rule's causal structural stop and objective, with a 60-minute expiry; an explicitly earlier source deadline takes precedence. If the rule has no structural pair, use .5S stop and 1S target and label this `standardized_research_geometry`. Never choose the best grid cell after reading test outcomes.

Literal fixtures: long entry100, stop99,target102; batches `(t+1,[100.5]),(t+2,[102]),(t+3,[98.5])` give target-first. Replace the second batch with `[98.5,102]` and result is same-batch-ambiguous. Insert a missing interval before t+2 and result is prior-gap-unknown. Complete prices bounded in [99.25,101.75] give neither. Mirror prices/direction to test shorts.

### Executable benchmark

`replay_family(opportunities, market, policy) -> DayReplay` is a deterministic one-NQ-mini, one-position-at-a-time research simulation. It is separate from descriptive price labels. Contract economics are $20/point and .25-point tick ($5/tick), as specified by [CME NQ](https://www.cmegroup.com/markets/equities/nasdaq/e-mini-nasdaq-100.contractSpecs.html). The commission assumption is $2.50 per contract per side; this is our replaceable research assumption, not a broker quote.

Default latency 250ms after qualification. Enter at the first complete available BBO batch at or after `decision+250ms`, no later than 5 seconds after that time. Long pays ask+one tick; short receives bid-one tick. Quote must be noncrossed, have positive displayed size, be at most one second old and have known availability. No quote means no simulated fill, separately counted. The entry direction must retain valid stop/target geometry after costs; otherwise skip `geometry_invalid_after_latency`. No favorable backfill to the qualification price.

At a simultaneous decision time choose earliest reference issue, then stable opportunity ID; priority is fixed before outcomes. While a position is open, log later signals as `occupied`, including their counterfactual descriptive labels. At most one entry per `(rule_id, reference_id, distinct_contact_id)`; a new contact requires the registered departure/rearm rule. Do not impose a fixed daily trade quota.

Exit is a market-order benchmark triggered when executable liquidation BBO crosses the fixed stop or target: bid for a long, ask for a short. Fill at first valid BBO at or after trigger+250ms, with one adverse tick. A price gap fills at that actual quote, not the boundary. Simultaneous ambiguous stop/target evidence produces two bounded replay paths; exclude from primary paired inference if paths disagree and show both bounds. The source expiry or 60-minute expiry triggers the same delayed market exit. Force flatten at least one minute before the verified account-day matching close. If no usable quote before close, mark replay incomplete, never carry the position into another account day or invent a fill.

Daily marked P&L includes realized cash, commissions and open liquidation value at bid/ask less estimated exit commission/slippage. If it reaches -$1,000 relative to day-start, submit the same delayed flatten and reject later entries for that day. A gap/latency can breach -$1,000; record the breach, do not clip it. Before entry, reject if estimated stop risk including round-trip costs exceeds the remaining loss budget. Unrealized gains do not reset the day-start loss limit. There are no partial contracts or scaling in this benchmark.

Net points for long = exit-entry - commissions/20; short reverses the price difference. Example: quoted ask100.00, entry100.25; later exit bid102.00, filled101.75; $5 round-trip commission gives `(1.50*20)-5=$25`, or 1.25 net points. Stress setting uses 500ms latency, two adverse ticks per side and $3.50 commission per side. All settings are frozen assumptions, not predicted fills.

### Opportunity quality, confirmation delay and missed moves

Compare a response-confirmed entry against: (1) the same reference's first admissible contact; (2) a time-only delayed contact with delay equal to that variant's **training-fold median** confirmation delay for family/session, fallback family then global; (3) unchanged source confirmation. The delay distribution is never fitted on test outcomes. If its median is unsupported, use exactly 60 seconds and label fallback. Every comparison uses the same reference formation and candidate exposure window, plus candidate-specific coverage reporting.

A missed-move descriptor records a favorable .5S,1S,2S crossing before confirmation and whether the structural opportunity remains positive after the actual delayed fill. It is not automatically a loss. Late entries can be useful if subsequent net reward remains positive; this is evaluated rather than forbidden.

### Unchanged-entry exit experiment

Hold a frozen set of entries, sizes, costs and initial structural stops constant. Compare exactly five policies: E0 structural objective + 60-minute/source expiry; E1 30-minute/source expiry with the same stop/target; E2 120-minute/source expiry; E3 break-even activation after +1 initial R, stop becomes entry plus round-trip assumed costs, updated only after the triggering batch is known; E4 trailing stop after +1R, long stop=max(old stop, highest observed executable bid -1R), short symmetric, never loosen. All end at the account-day close. If an explicit source deadline is earlier, all policies retain it and report no effective change where applicable.

No target/stop uses a future maximum or an ex-post optimal exit. Entries with unavailable initial R remain in the denominator ledger and are unsupported for E3/E4. Report paired entry-level and serialized daily results; entries changed by prior exit occupancy are separately identified. Choose exits only in inner tuning; final test comparisons retain every policy. This is a bounded baseline study, not the final learned management system.

Canonical source: [DATA_CONTRACTS.md](/workspace/.worktrees/docs-amend/planning/research-program/DATA_CONTRACTS.md).

## Data, time and identity contracts

Owner tasks: `P15-00` defines schemas and baseline binding; `P15-02` supplies native adapters; `P2-00` extends the availability ledger. All types below are proposed APIs in `implementation/src/trading_research/research/contracts/`. Use Python 3.12, `dataclass(frozen=True, slots=True)`, `Enum`, `Decimal` for money/prices and integer UTC nanoseconds for clocks. NumPy float64 is allowed inside numerical models after explicit conversion. Serialize prices as decimal strings; NaN/Infinity are forbidden JSON values.

The complete declaration blueprint is [TYPE_REFERENCE.py](/workspace/planning/research-program/TYPE_REFERENCE.py). P15-00 implements the shared/native/rule portion; P2-00 adds expert declarations after the phase gate. Markdown excerpts explain the same fields. At construction, copy and recursively freeze nested mappings/sequences so a frozen record cannot be changed through an aliased dictionary; serialize immutable mappings back to canonical JSON. Validate units, finite values, IDs, intervals, enum domains and nested evidence clocks at the boundary.

The v2 acceptance amendment in [ASSURANCE.md](/workspace/.worktrees/docs-amend/planning/research-program/ASSURANCE.md) makes these boundaries executable requirements for every evidence-bearing constructor and deserializer. A late nested parent, malformed clock or future-trained forecast must fail even if its immediate wrapper looks valid. It also defines preserved plan/code snapshots, required artifact inventory, native evidence selectors and engineering coverage by input group. Task-specific formulas and the declared future-outcome edge convention remain unchanged.

### Clock invariant

For decision/issue time `t`, every feature dependency must satisfy `available_at_ns <= t`; every fitted parameter must satisfy `fit_available_at_ns <= t`. Source event time describes what happened; availability describes when the system could know it. Use the existing native receive/known-at rule and whole timestamp batches. If internal order within a batch is unknown, preserve that uncertainty. Neither sorting row IDs nor interpolating a favorable print creates order.

Past feature windows are `[start, end)` with `end <= t`; decision-time native events are usable only when the entire required batch is available. Future outcome windows are `(t, end]`. A confirmed pivot at bar `k` with two right neighbors is available after bar `k+2` closes, never at the pivot's event time.

```python
Ns = int
AssetId = str       # e.g. NQ:<native instrument_id>, QQQ, NDX

class Coverage(Enum):
    COMPLETE = "complete_observed_scope"
    PARTIAL = "partial"
    MISSING = "missing"
    AMBIGUOUS = "ambiguous"

@dataclass(frozen=True, slots=True)
class EvidenceRef:
    artifact_sha256: str
    row_ids: tuple[str, ...]
    event_start_ns: Ns
    event_end_ns: Ns
    available_at_ns: Ns
    coverage: Coverage
    limitation_ids: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class FeatureValue:
    name: str
    value: float | None
    unit: str
    available_at_ns: Ns
    evidence: tuple[EvidenceRef, ...]
    missing_reason: str | None

@dataclass(frozen=True, slots=True)
class Snapshot:
    snapshot_id: str
    account_day: str
    asset_id: AssetId
    issue_at_ns: Ns
    feature_schema: str
    values: tuple[FeatureValue, ...]
    policy_sha256: str
```

Empty known windows and missing windows differ. A complete future horizon with no arrival/setup has occurrence label 0. Conditional reaction/utility is undefined when no arrival/setup occurs. An incomplete future horizon has unknown labels; never convert it to 0 or a loss. Missing features get masks and explicit support flags; missing outcomes never get median imputation.

### Sessions, contracts and denominators

Use `method_pack.session_policy.NQSessionPolicy` and its frozen reconstruction policy as separately identified inputs; preserve evidenced exceptions and historical halts. An operational account day is the research interval from previous calendar day 18:00 America/New_York to labelled day 17:00, intersect verified matching hours. DST conversion uses timezone-aware conversion, never a fixed UTC offset. Final flatten is one minute before the verified final matching close; unverified close implies no certified economic replay for that day. Source RTH is 09:30–16:00 intersect actual matching hours, not an account-day definition or universal trading restriction.

Analysis buckets, all in New York time and intersect matching hours: reopen 18:00–00:00, Asia 00:00–03:00, Europe 03:00–09:30, US morning 09:30–12:00, US afternoon 12:00–16:00, late 16:00–17:00. These are our reporting buckets. Do not rename a source's Asia/London window to these definitions. Snapshot grid is each quarter-hour from account-day open plus 09:29, 09:30, 10:00, 10:30, 16:00 and each source opportunity immediately before its decision; drop closed times and deduplicate exact time/asset/schema IDs. Extra source clocks are allowed only by the registered method contract.

Do not concatenate rolled futures prices into returns, ranges or previous-session references. Use existing native event ownership to deduplicate input files, and separately register traded-contract selection; preserve native instrument IDs. Each target must stay within its contract and allowed horizon; a crossing roll is unsupported unless a separate labelled return-only stitching policy is registered. Native prior highs/lows and profiles require same-contract history. Summaries report declared dates, complete eligible dates, zero-opportunity dates, partial dates, missing dates, observations and overlap groups separately.

The existing `event_cache.contract_at` explicitly describes its roll map as **acquired continuous membership, not a tradable roll forecast**. Preserve that map for Phase 1 parity and identify it as archive membership. Do not assume its selection was known intraday. For the new executable benchmark, register a deterministic calendar contract rule: at account-day open choose the nearest unexpired native quarterly NQ contract whose dated expiry is at least 8 calendar days after the account-day label. This is our fixed research roll policy, not a claim about the exchange's recommended roll. Require its dated definition and usable native data. If the accepted source opportunity is on a different contract, record `contract_policy_mismatch`; keep its descriptive observation but exclude it from the certified benchmark with counts. Never switch to whichever contract later had more volume. Native context/features retain per-contract series; actual mapping/expiry uncertainty remains a coverage limitation. P15-02 must test both archive-membership parity and the separate causal benchmark selection.

### Opportunity and rule schemas

```python
@dataclass(frozen=True, slots=True)
class RuleSpec:
    rule_id: str
    family: str
    source_branch: str | None
    version: str
    provenance: str   # source_literal | source_inspired | custom
    baseline_rule_id: str | None
    changed_axis: str
    parameters: dict[str, str | int | bool]
    required_inputs: tuple[str, ...]
    required_stages: tuple[str, ...]
    formation_policy: str
    expiry_policy: str

@dataclass(frozen=True, slots=True)
class Opportunity:
    opportunity_id: str
    parent_opportunity_id: str | None
    overlap_group_id: str
    rule_id: str
    family: str
    branch: str
    account_day: str
    side: int                 # +1 long, -1 short
    issue_at_ns: Ns
    decision_at_ns: Ns
    reference_asset: AssetId
    response_asset: AssetId
    execution_asset: AssetId
    reference_id: str
    lower: Decimal
    upper: Decimal
    entry_reference: Decimal | None
    invalidation: Decimal | None
    objective: Decimal | None
    expiry_at_ns: Ns
    stages: tuple[EvidenceRef, ...]
    coverage: Coverage
    source_exact: bool
    hypothesis_ids: tuple[str, ...]
```

Every source baseline adapter preserves the complete original `phase1-historical-episode-v2` payload alongside this normalized record. The existing `historical_assembly.HistoricalEpisode.finish` emits `candidate_id`, method/branch, decision time, operand derivations, stages, source/strategy verdicts, reference/trigger/geometry and hashes. Preserve all distinctions. `author_exact_verdict=unknown` cannot become `source_exact=True` because a new adapter matches geometry.

IDs are SHA256 of canonical JSON using UTF-8, sorted object keys, compact separators, stable enum strings and exact decimal strings. No wall-clock run time, path ordering or worker number enters a semantic record ID. Record full SHA256; human short IDs are display only. Order records by `(account_day, decision_at_ns, family, branch, opportunity_id)`. Same native occurrence reused by multiple rules gets an overlap group using native contract, source trigger identity and reference formation identity; report additional time-overlap dependence without falsely merging distinct signals.

### Feature and forecast artifacts

```python
@dataclass(frozen=True, slots=True)
class Forecast:
    forecast_id: str
    expert_id: str
    artifact_sha256: str
    snapshot_id: str
    issue_at_ns: Ns
    horizon_id: str
    target_end_ns: Ns | None
    output: dict[str, float | str | None]
    support: str     # supported | low_support | input_limited | unavailable
    train_end_ns: Ns
    fit_available_at_ns: Ns
    input_feature_ids: tuple[str, ...]
    parent_forecast_ids: tuple[str, ...]
```

An inapplicable or calendar-unknown horizon emits `target_end_ns=None`, support=`unavailable` and null output values with its reason. Do not invent a zero-length future target or a zero variance. A supported forecast requires a known target end after its issue time.

Persist row-level feature order, column names, units, masks, imputer/scaler hashes, model input matrix hash, input-row IDs, prediction row IDs, fitted parameter identity and training label availability. A stored feature is not considered consumed until the matrix and fitted artifact reference it. Forecast intervals and probabilities are evidence outputs; downstream code must retain uncertainty and fallback behavior.

### Options availability ledger

Per native contract store root, underlying ID, expiry timestamp, strike, call/put, multiplier, currency, exercise style, settlement style/time, quote/trade coverage, spot source, rate/dividend source and dated instrument-definition evidence. Do not assume NDX and NDXP or SPX and SPXW share expiry/settlement clocks. Native NQ/ES options reference their actual underlying future, not a guessed continuous front contract.

Every daily OI record has `effective_session`, `published_at`, `available_at`, `publication_policy` and `is_assumed_clock`. Use historical publication metadata when owned. If absent, permit only the conservative research assumption “available at 12:00 ET on the next verified business session after the effective date,” with `is_assumed_clock=True`; compare an extra one-session delay. This assumption does not certify live availability. Unknown calendar/definition blocks that row. Never read a filename date as the publication clock.

An option midpoint is usable when bid/ask are nonnegative, ask >= bid, timestamp is available, age <= 60 seconds, spread <= max(0.05, 0.20 * mid) in option quote units, and price satisfies the chosen model's bounds. Native quote/tick spot must have age <= 5 seconds. If only native one-minute OHLC is owned, permit an explicitly tagged `completed_native_minute_close` snapshot whose close is unambiguous, whose bar is published by issue time and whose bar-start age is <= 120 seconds (a conservative bound on the underlying print age). Retain source resolution/age and compare a strict quote-only sensitivity cohort. A daily cash-index close cannot satisfy either intraday policy. Record rejection reasons. Use 5-minute snapshots for expensive surface reconstruction and the most recently completed snapshot at each decision. Never carry a quote or surface through expiry or a market closure. Coverage fractions use the predeclared contract universe, not only surviving liquid strikes.

Baseline OI is the latest available dated observation, with age in sessions; exposure uses current as-of price/IV/time. An intraday OI estimate is a separate model output with uncertainty. Next-day OI can supervise training only after its availability clock. Expiry-driven zero OI is not a label of intraday opening/closing flow. Underlying cash indices have price and option flow, not a fictitious underlying trade tape.

Canonical source: [OPTIONS.md](/workspace/.worktrees/docs-amend/planning/phase-2/OPTIONS.md).

## Native options context and intraday updates

Owners `P2-09` instrument/quote adapters, `P2-10` pricing/exposure boards, `P2-11` flow and scenarios, `P2-12` learned intraday OI. All formulas here are explicit research models. Native instrument prices and model-derived exposures are different kinds of evidence; neither reveals an actual dealer's inventory.

### Universe and availability

Required roots are NDX/NDXP, SPX/SPXW, QQQ, SPY, NQ and ES options on their actual native underlying. Keep root, exercise and settlement conventions from dated owned instrument definitions. The current product descriptions from [Nasdaq](https://www.nasdaq.com/products/north-american-markets/nasdaq-100-options-xnd-ndx) and [Cboe SPX specifications](https://www.cboe.com/tradable-products/sp-500/spx-options/spx-specifications) are reference checks, not a substitute for historical contract metadata. Futures option exercise/underlying delivery also comes from the actual product definition.

At each time the eligible universe is all owned, then-known active contracts in the latest available definitions/chain, plus contracts first observed and available by that time. Do not look ahead to the final daily chain to learn which strikes will trade. Include all owned expiries; boards are0DTE,1–7,8–30,31–90 and>90 calendar days, split by root and settlement style. 0DTE means expiry on the local date with positive time remaining, not already settled. Record complete-chain versus scoped intraday coverage for each root/day; the absence of a strike from a scoped feed is not zero exposure or zero flow.

Use the quote/spot/OI clocks and filters in [data contracts](/workspace/planning/research-program/DATA_CONTRACTS.md). Rates and dividends require dated availability. For European spot contracts, derive a forward from synchronous call-put pairs at the same strike and expiry when at least three valid pairs exist: each pair implies `F=K+exp(r*T)*(C-P)`; use the median across the five strikes nearest spot, at least three. If a dated rate is absent, a separately flagged r=0 sensitivity model is allowed; it is not the primary rate-supported result. Record pair dispersion and reject relative dispersion>.01. For American contracts, parity-derived forward is not assumed exact; require dated dividend/carry inputs or use the explicitly labelled equivalent-European approximation with a coverage limitation.

Each expensive surface snapshot is frozen after a completed 5-minute bucket. Downstream minute/quarter-hour issues use the last completed available surface, maximum age10 minutes; reprice Greeks with current valid spot/IV/time when possible and record which inputs moved. No interpolation through a missing session or expiry. Native NDX/SPX intraday spot absence blocks native cash-index intraday exposure; mapped QQQ/futures remains a separately labelled historical comparison only.

### Pricing and Greeks

Proposed pure functions:

```python
def european_price(underlier, strike, tau_years, sigma, rate, carry, right, model) -> float: ...
def implied_vol(mid, instrument, market_inputs) -> IVResult: ...
def european_greeks(instrument, market_inputs, sigma) -> Greeks: ...
def american_tree_price(instrument, market_inputs, sigma, steps=400) -> float: ...
def exposure_board(contracts, oi_state, surface, inventory_scenario) -> ExposureBoard: ...
def decompose_change(previous, current, order=("spot","iv","time","oi","universe")) -> tuple[Change, ...]: ...
```

Let Phi be the standard normal CDF using `0.5*(1+erf(x/sqrt(2)))`, phi=`exp(-x*x/2)/sqrt(2*pi)`. T is exact seconds to settlement/exercise expiry divided by365*86400, sigma is annualized log volatility. Positive S/F,K,sigma,T are required. Expired contracts return expiry/intrinsic status and no live Greeks.

For European spot BSM with continuous dividend yield q and rate r:

`d1=[ln(S/K)+(r-q+.5*sigma²)*T]/(sigma*sqrt(T))`, `d2=d1-sigma*sqrt(T)`.

`call=S*exp(-qT)*Phi(d1)-K*exp(-rT)*Phi(d2)`; `put=K*exp(-rT)*Phi(-d2)-S*exp(-qT)*Phi(-d1)`.

`delta_call=exp(-qT)*Phi(d1)`, `delta_put=exp(-qT)*(Phi(d1)-1)`, `gamma=exp(-qT)*phi(d1)/(S*sigma*sqrt(T))`, `vega=S*exp(-qT)*phi(d1)*sqrt(T)`, `vanna=-exp(-qT)*phi(d1)*d2/sigma`. Vega is derivative per 1.00 absolute volatility; vanna is delta derivative per 1.00 absolute volatility. A one-volatility-point shock is .01, not1.

For European futures options use Black76: replace underlying by F; `d1=[ln(F/K)+.5*sigma²*T]/(sigma*sqrt(T))`; discount the full payoff by exp(-rT). Call=`exp(-rT)*(F*Phi(d1)-K*Phi(d2))`, put analogous. Delta with respect to F is exp(-rT)*Phi(d1) for calls and exp(-rT)*(Phi(d1)-1) for puts. Gamma=`exp(-rT)*phi(d1)/(F*sigma*sqrt(T))`; vega=`exp(-rT)*F*phi(d1)*sqrt(T)`; vanna=`-exp(-rT)*phi(d1)*d2/sigma`. Do not substitute spot BSM Greeks while labelling them futures Greeks.

For American contracts the full-history context reference uses equivalent-European BSM/Black76 with a mandatory `american_equivalent_european_approximation` flag and continuous-carry provenance. This keeps the full native-chain experiment computationally bounded; it is not an exact American valuation. The mandatory sensitivity model is a400-step Cox–Ross–Rubinstein tree with continuous carry. `dt=T/N`, `u=exp(sigma*sqrt(dt))`, `d=1/u`, spot risk-neutral `p=(exp((r-q)dt)-d)/(u-d)`; for futures p=(1-d)/(u-d). Reject p outside[0,1], then retry N=800 once; failure remains explicit. Terminal payoff is max(s*(U-K),0). Backward node value=`max(intrinsic, exp(-r*dt)*(p*up+(1-p)*down))`. Dated discrete dividends not represented by continuous q are flagged `continuous_dividend_approximation`; price/Greek comparisons must separate this cohort. This is a specified numerical approximation, not an exact American price.

American delta/gamma use central underlying bumps `h=max(.01,.001*U)`; vega uses volatility bump v=.001; vanna uses the four-price mixed central derivative divided by4*h*v. If sigma<=v, use v=sigma/2. Compute N400 and N800 for numerical sensitivity on engineering cases; exclude primary Greeks if their relative difference exceeds10% using denominator max(abs(N800),1e-6), but retain price/IV and the numerical limitation. Run this sensitivity on a deterministic sample of 16 valid contracts per supported American root/engineering date: four expiry groups (0DTE,1–7,8–30,>30) by four absolute log-moneyness rank quartiles, choosing the earliest stable contract ID in each populated cell. Keep missing cells. The full-history reference stays the fast equivalent-European model; flag any root/expiry/moneyness cohort with>10% Greek discrepancy in the sensitivity sample as model-limited, and compare forecasts with that cohort excluded. Report the sampled scope; do not claim all American Greeks were individually validated.

IV inversion uses bisection sigma in[1e-4,5], up to100 iterations; stop price error<=max(1e-6,1e-5*mid) or sigma bracket<=1e-8. A target outside endpoint prices is `no_bracket`, not clipped IV. European bounds and parity must pass; American prices must be at least intrinsic and no more than underlying for calls or strike for puts (discount conventions may tighten but never loosen incorrectly). Use the instrument's recorded reference model for primary inversion/Greeks and its American tree dispatch for the bounded sensitivity sample. Never label the equivalent-European result an exact American Greek. Persist model version, rate/carry provenance, quote filters, convergence and numerical flags.

Independent fixtures: S=K=100,T=1,r=q=0,sigma=.2 gives European call≈7.96556746, delta≈.539827837, gamma≈.019847627, vega≈39.69525475 and vanna≈.198476274. Put-call parity C-P=S exp(-qT)-K exp(-rT). At r=0 and F=S, Black76 and zero-carry BSM coincide. Finite-difference each analytic Greek at h=.01 and v=.0001 within relative1e-4 on nondegenerate cases. An American call with q=0 should approach its European value as N grows; early exercise should not artificially increase its value materially beyond convergence error.

### Exposure and flow units

For signed position estimate n contracts, multiplier M and underlying U: delta notional=`n*M*U*delta`; gamma hedge-notional change per 1% underlying move=`.01*n*M*U²*gamma`; vega dollars per 1 vol point=`.01*n*M*vega`; vanna delta-notional change per 1 vol point=`.01*n*M*U*vanna`. Store units and underlying separately; never sum raw NQ and SPX points into a combined level.

Inventory scenarios: unsigned OI-weighted magnitude; call-positive/put-negative proxy (existing baseline assumption); its sign reverse; all-long; all-short. These are sensitivity scenarios, never known dealer positions. Intraday trade direction does not identify whether an existing position was opened or closed. Report scenario-dependent sign flips separately from stable concentration. Baseline B0 uses latest available OI revalued with current native spot/IV/time. B1 adds observed flow descriptors but leaves OI fixed. B2 adds the trained OI estimate. Compare all three on equal coverage.

Trade sign is +1 at/above a synchronized ask, -1 at/below bid; inside-spread or missing/ambiguous quote is unknown. Preserve vendor conditions, exchange sequence, quote age, corrections and cancellations under the native event contract. Group possible multi-leg events by explicit trade-condition/package ID where owned; otherwise mark `possible_complex` for same-underlying/expiry events within 1ms with multiple strikes/rights. This heuristic is a flag, not proof of a spread or roll; do not infer aggressive opening inventory from it.

For known signed trades record contracts=sum(s*q), premium=sum(s*q*M*trade_price), delta=sum(s*q*M*U*delta), gamma=sum(s*q*.01*M*U²*gamma), vega=sum(s*q*.01*M*vega), and vanna analog. Also record unsigned and unknown-sign totals. Trade Greeks use only surface inputs available by that trade. Rolling windows5/30/60 minutes and account-day cumulative flow are distinct columns. Missing scoped strikes do not contribute zeros to an asserted full-chain flow total.

### Boards, migration and repricing

Per root/expiry bucket/strike retain OI, volume, all exposure units, distance from spot, IV, age and uncertainty. Extract local concentration maxima over adjacent strikes, their share of total absolute exposure and gap to the next node; retain nonmaximum nodes. Weighted centroid=`sum(K*abs(exposure))/sum(abs(exposure))`, explicitly `exposure_centroid`, not VWAP. Churn is `sum_K abs(w_K_now-w_K_prev)/2` on normalized absolute weights over the union of then-known strikes. Migration is matched-node strike change and centroid change, with new/disappeared nodes separate. These are context features; location entry/reaction rules await Phase 3.

Decompose exposure change using a fixed telescoping order: change spot only; then IV surface; then elapsed time; then OI/flow state; then universe. Each component is the difference between consecutive repricings, so sum equals final minus initial exactly. Also compute reverse order as attribution sensitivity; components are order-dependent interaction allocations, not unique causes. Missing a required input produces an unresolved component and no false exact decomposition. Quote-universe change is not dealer rehedging.

Shock grid is spot returns{-1%,-.5%,0,+.5%,+1%} × parallel IV changes{-2,0,+2 vol points} × elapsed time{0,30,120 minutes}, bounded before actual expiry. Reprice full models; keep strike IV fixed under spot changes (`sticky_strike`) and compare a separately labelled sticky-log-moneyness interpolation sensitivity. No negative volatility; invalid shock cells are unavailable. The grid is context sensitivity, not a future path prediction. Scenario summaries include gamma sign/size, delta-notional change, vega/vanna and concentration migration.

Surface features: nearest-ATM IV by minimum abs(log(K/F)), ties tighter spread then lower strike;25-delta call/put IV by linear interpolation in absolute delta between bracketing strikes (no extrapolation); RR=IV_call25-IV_put25, BF=.5*(IV_call25+IV_put25)-IV_ATM. Across expiries interpolate **total variance** w=IV²*T linearly at 7,30,90 calendar days only when bracketed; convert back sqrt(w/T). A negative forward variance between nodes is a surface-quality flag; do not arbitrarily smooth it away. Store term slope w(T2)-w(T1) over T2-T1 and missing brackets.

### Fitted options-context expert

P2-11 fits its own artifact after the joint-volatility code/causal forecasts exist. For each root and expiry bucket, consume these exact board summaries: log1p total OI, log1p unsigned trade quantity5m/30m, signed premium5m/30m and signed delta30m, unsigned gamma magnitude, call-positive/put-negative gamma proxy, vega/vanna proxy, exposure-centroid log-distance from underlying, top-node share, churn,5m IV change, term slope, unknown-flow fraction, quote-coverage fraction and model-limited fraction. Keep root/bucket names and missing masks; normalize exposures by their trailing 20-session same-time median absolute value, minimum 10 prior sessions. If denominator is0, mark unavailable rather than divide by1 and obscure units.

Targets are NQ signed midpoint change/S over next 30/60 minutes and log variance surprise `log((observed_RV+1e-12)/(causal_joint_vol_RV+1e-12))` over the same horizons. Use the exact volatility label builder and causal joint-vol forecasts, with separately masked targets. Fit ridge/hinge regression and .1/.5/.9 quantiles, compare zero/price-only baselines, B0 versus B1 flow, and leave-one-root-out ablations. Hinge products are gamma_proxy×spot_return5m, vanna_proxy×IV_change5m, flow_delta30m×centroid_distance, churn×top_node_share, term_slope×time_to_close, and unknown_flow_fraction×flow_premium5m, for the NQ board aggregate summed across expiry buckets after unit-safe normalization. B2 uses the same recipe and feature names with causal estimated OI/updated boards after P2-12; the dependency runner refits/replays it under a new version, never mutating B0/B1. Final downstream B2 assessment is in P2-24.

### Learned intraday OI update

Training unit g is one native contract and one verified full trade-reporting cycle with complete flow and beginning/end OI whose effective dates bracket that cycle. Both OI publications must be available before fitting. Exclude expiry day, contract adjustment/corporate-action days, uncertain cycle boundaries and `abs(delta_OI)>total_trade_quantity`. Keep all excluded counts. Expiring0DTE terminal OI cannot validate intraday OI. Nonexpiring contracts with next-day OI support only an aggregate endpoint target, not observed intraday inventory.

For trade i, standardized prefix-known features x_i are: intercept; known trade sign and unknown-sign mask; log1p size; spread/mid; abs log-moneyness; log1p time-to-expiry hours; call/put; possible-complex flag; time-of-day sine/cosine; cumulative unsigned volume/max(prior OI,1); cumulative signed volume/max(prior OI,1); and prior 5-minute IV change. Fit transformations on training groups only. No end-of-day quantity or future OI enters x_i.

Let `a_i=tanh(beta.T x_i)` be a bounded net-opening contribution in[-1,1], not a probability of dealer direction. Predict `Dhat_g=sum_i q_i*a_i`; `V_g=max(1,sum_i q_i)`. Minimize `L=(1/G)*sum_g((Dhat_g-D_g)/V_g)^2 + lambda*sum(beta_nonintercept²)`. Gradient=`(2/G)*sum_g[(Dhat_g-D_g)/V_g² * sum_i q_i*(1-a_i²)*x_i] +2*lambda*D*beta`. Initialize beta0; Adam lr.01, betas(.9,.999), epsilon1e-8, exactly 2,000 steps; retain best training objective, tune lambda{.001,.01,.1} on chronological complete contract-day groups. Native day grouping prevents train/test trades from the same day leaking across roots.

Intraday OI estimate at t is `max(0, OI_start + sum_(i available<=t) q_i*tanh(beta.T*x_i))`. Keep the unclipped estimate and clipping amount. Recompute from the cumulative raw sum; do not recursively discard negative contributions at each prefix. For each contract-day also evaluate clipped endpoint error separately from the fitted unclipped endpoint objective. Minimum 100 complete contract-day groups on30 days, and at least 10 groups per supported root/exercise cohort; below this retain B0 with low support.

Uncertainty: refit20 day-block bootstrap parameter replicates using the training data and seeds15022026+j, j=0..19, then report .1/.9 quantiles of prefix OI. These are model-sensitivity intervals, not calibrated confidence intervals for unobserved true intraday OI. Evaluate held-out endpoint MAE, signed bias and normalized error against unchanged prior OI and a training-mean opening-fraction baseline. Separately test whether B2 improves NQ context forecasts/conditional utility over B0/B1 under chronological stacking. Endpoint calibration alone cannot establish reaction quality or actual inventory accuracy.

Fixtures: priorOI100 and contributions+10,-5 gives raw/clipped105; contribution -150 gives raw-50, clipped0 with amount50; later+60 gives raw10, clipped10, not60. Beta0 predicts no change. One trade q10 with tanh(beta.x)=.5 predicts+5. Compare analytic gradient with central finite differences1e-6 at nonzero beta, absolute tolerance1e-5. Replace next-day OI after a snapshot and prove its stored features, OI estimate and forecast unchanged.

Canonical source: [VOLATILITY.md](/workspace/.worktrees/docs-amend/planning/phase-2/VOLATILITY.md).

## Joint intraday volatility and movement forecasts

Owners `P2-03` feature/target arithmetic, `P2-04` joint fit and validation. Proposed modules `experts/features/volatility.py`, `experts/labels/volatility.py`, `experts/volatility.py`. Use the [shared fitting recipe](/workspace/planning/research-program/MODEL_FITTING.md), not separate fitted GK/YZ/HAR experts.

### Historical inputs and units

For a complete same-contract OHLC interval with positive prices define `u=ln(H/O)`, `d=ln(L/O)`, `c=ln(C/O)`. The registered simplified Garman–Klass input is `GK=.5*ln(H/L)^2-(2*ln(2)-1)*c^2`. Store interval log-return variance; reject inconsistent OHLC. Values between -1e-12 and 0 may round to0 with a numerical flag; larger negatives fail validation. This is the conventional simplified no-opening-jump version, not every estimator in the [original Garman–Klass paper](https://www.cmegroup.com/trading/fx/files/a_estimation_of_security_price.pdf).

For n=20 complete account days, `o_i=ln(O_i/C_(i-1))`, `c_i=ln(C_i/O_i)`, `v_o=sum((o_i-mean(o))^2)/(n-1)`, `v_c=sum((c_i-mean(c))^2)/(n-1)`, `v_RS=mean(u_i*(u_i-c_i)+d_i*(d_i-c_i))`, `k=.34/(1.34+(n+1)/(n-1))`, and `YZ=v_o+k*v_c+(1-k)*v_RS`. Require n>1 and the preceding same-contract close. Account-day and RTH estimators are separately named. These equations follow the multiple-period construction in [Yang and Zhang](https://www.atmif.com/papers/range.pdf); rolling length20 and the application to our windows are research choices.

Realized variance `RV_[a,b]=sum_j ln(P_j/P_(j-1))^2` uses one-minute sampling, including a final shorter interval if the horizon is not a whole minute. P_j is the last valid native BBO midpoint available at or before the sampling boundary, age<=5 seconds; a missing boundary makes the target incomplete. At t use a midpoint already available at t. Do not bridge contract changes, unscheduled feed gaps or closed markets with a continuous return. Scheduled closure jumps are a separately named return feature/target component; the matching-interval RV excludes them. For account-day targets report matching RV and reopen jump variance separately rather than silently blending definitions.

HAR inputs are prior complete account-day RV, mean of prior 5, mean of prior 22, each `log(RV+1e-12)`, plus same-session versions where complete. The multiscale structure comes from [Corsi's HAR-RV model](https://academic.oup.com/jfec/article-abstract/7/2/174/856522); this pack's intraday multihead and IV extension are our hypotheses. Add recent1/5/15/60-minute RV, GK for completed 15/60-minute windows and prior day, rolling 20-day GK mean/YZ, elapsed matching minutes, remaining minutes, session bucket, prior 20-session same-bucket RV fractions and current range/volume intensity.

IV inputs come from the native option surface contract: ATM IV,25-delta risk reversal/butterfly, term slopes, 0DTE/1–7/8–30/31–90 boards and changes over 5/30 minutes for NDX/NDXP, SPX/SPXW, QQQ, SPY, NQ, ES. Include owned VIX/VX/VVIX/VXN-family series using their actual instrument metadata and known clocks. Different index horizon conventions stay named; do not claim VIX is a next-hour NQ forecast. Preserve spot/option basis, publication/quote age, exercise-model and missing masks. Optional groups absent in training are shown as unconsumed; the native-coverage ledger still requires a disposition for every requested group.

### Targets and forecast times

Use the shared quarter-hour/source-opportunity snapshot grid. Heads are matching-interval RV over next 15,30,60,120 minutes; remaining current analysis bucket; next analysis bucket within the same account day; remaining RTH when t<its close; and remaining account day. Each head stores actual start/end/duration and coverage. Next-bucket target starts at that bucket's open and does not include the intervening interval; identify it explicitly. No fixed-horizon head crosses the account-day/contract boundary. Unsupported heads are masked, not zero. The fitted coefficient matrix has all eight named heads, with per-head support.

Also output `sigma_log=sqrt(predicted_RV)` and conventional points scale `current_spot*sigma_log`. This scale is a volatility conversion, not a guaranteed high/low or a location band. Directional extrema are fitted separately by the range-path expert. The model may predict further movement after a large already-consumed range; there is no fixed daily allowance to subtract mechanically.

### Fits, ablations and acceptance

One `JointVolatilityExpert.fit` consumes all feature groups and produces one multihead artifact. Compare the shared linear ridge and hinge-ridge recipes. Hinge products, exactly six: HAR1×ATM_NQ, HAR22×ATM_NDX, recent15mRV×minutes_remaining, GK60m×ATM_QQQ, YZ20×term_slope_NDX, current_range/S×IV_change5m_NDX. Missing groups retain masks and an unsupported interaction flag.

Ablations: A0 past same-bucket mean variance; A1 HAR-only; A2 GK+YZ+realized-price features; A3 IV-only plus clocks; A4 all historical features without IV; A5 joint all groups. The production architecture is A5 when supported; if A5 fails contribution gates, retain the best supported simpler baseline with an explicit negative joint-input result, never invent improvement. Report each head's QLIKE, log-MAE, calibrated80% coverage/width, support, year/session performance and native-input contribution. Retain failed models and all tuned configurations in the shared trial ledger.

Fixtures: O=100,H=110,L=90,C=100 gives GK=`.5*ln(110/90)^2`; flat OHLC gives0. For n=3 with all o_i=.01, c_i=.02, u_i=.03,d_i=-.01, sample opening/closing variances are0, RS=.0006 and YZ=(1-k)*.0006. RV prices100,101,100 gives `2*ln(1.01)^2`. Annualized IV.2 over one calendar day gives variance`.04/365` only for the explicitly labelled IV scaling feature, never as a realized target.

Future perturbation replaces all prices/IV/OI after issue time and must leave snapshot and forecast bytes unchanged; it must change at least one future target in a positive control. Native charts show predicted versus realized variance and interval width for one high, low, missing-IV and large-error case per supported head. Verify exact numerical expectations independently with hand calculations or scalar math, not by calling the production function twice.

Canonical source: [P2-05.md](/workspace/.worktrees/docs-amend/planning/phase-2/tasks/P2-05.md).

## P2-05 — Fit directional range, topology and passage-time experts

Status: **planned; implementation not started by this planning task**.

Subphase: `04-context-mechanisms`. Dependencies: P2-04.

### Goal and boundary

Implement the exact Range-path expert feature/target recipes, units, horizons, state semantics and missing/censored populations.

Implement only this task and its declared outputs. Preserve accepted Phase 1 code/reports, immutable sources and raw data. All new numerical recipes are registered research policies unless the source ledger proves literal attribution. No future input, later fit or all-history selected rule may enter an earlier decision.

### Read first

- [AGENTS.md](/workspace/AGENTS.md)
- [ROADMAP.md](/workspace/planning/ROADMAP.md)
- [PSTACK_EXECUTION.md](/workspace/planning/research-program/PSTACK_EXECUTION.md)
- [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md)
- [Assigned failure cases](/workspace/planning/research-program/SILENT_FAILURES.md)
- [WORKFLOW.md](/workspace/planning/research-program/WORKFLOW.md)
- [CONTEXT.md](/workspace/planning/phase-2/CONTEXT.md)
- [MODEL_FITTING.md](/workspace/planning/research-program/MODEL_FITTING.md)
- [EVALUATION.md](/workspace/planning/research-program/EVALUATION.md)
- [OUTCOMES.md](/workspace/planning/research-program/OUTCOMES.md)
- [DATA_CONTRACTS.md](/workspace/planning/research-program/DATA_CONTRACTS.md)

The named phase specification provides the exact formulas, proposed signatures, units and literal fixtures for this task. Existing symbols are marked as existing; proposed modules/commands are created by their owner tasks. Do not substitute remembered formulas or undocumented library defaults.

### Input and ownership contract

Consume verified predecessor receipts: **P2-04**. Their hashes and actual artifact paths go in this task receipt. Required schema details are in DATA_CONTRACTS; source adapters also read their named method predicates.

Allowed implementation/test paths:

- `/workspace/implementation/src/trading_research/research/experts/features/range_path.py`
- `/workspace/implementation/src/trading_research/research/experts/labels/range_path.py`
- `/workspace/implementation/src/trading_research/research/experts/range_path.py`
- `/workspace/implementation/src/trading_research/research/experts/configs/range_path.json`
- `/workspace/implementation/tests/context_experts/test_p2_05.py`

A worker does not edit another task’s shared files. Request an explicit integration patch from the subphase coordinator for runner registration, imports or additive shared-schema changes; the coordinator records it and reruns the affected contract tests. Keep independently fitted artifacts separate even when calculators are shared.

### Implementation steps

1. Implement the exact Range-path expert feature/target recipes, units, horizons, state semantics and missing/censored populations.
2. Fit the declared linear/hinge classifier/regression/quantile heads with causal parent forecasts and fixed grids; keep artifact and support separate from other experts.
3. Run constant/session-frequency and price-only baselines, specified group ablations, chronological evaluation and deterministic native diagnostics.
4. Trace one actual output through its serialized schema, feature/stage parents and native receipt. Then run the verification below and write immutable evidence. A formula unit test alone does not complete a native-data or fitted-expert task.

### Worked and discriminating checks

Use the literal cases in the named mathematical contract and add one independently constructed negative case.

Use the shared [reference vectors](/workspace/planning/research-program/fixtures/reference_vectors.json) where applicable. Add a negative control that fails if the central behavior is removed, reversed, delayed incorrectly or fed future information. Model tests must include a known synthetic signal and a native chronological slice; never demand an empirical market improvement merely to pass software verification.

### Required failure checks

Acceptance amendment: `research-assurance-2026-09-14-v2`. Assigned cases: **S01, S02, S03, S07, S08, S11, S16, S18, S19, S28, S32**. Use the exact probes, expected results and evidence in SILENT_FAILURES.md. Reuse current bound shared evidence where applicable; do not replace the task’s own sensitive/native check with a test count. Preserve prior attempts and produce the common task artifacts listed in TASK_GRAPH.json as well as the task-specific outputs below.

### Acceptance checklist

- [ ] A01: Up-then-down and same-batch ambiguous topology fixtures differ.
- [ ] A02: Censored partial bins are not treated as full no-event bins.
- [ ] A03: Directional quantiles do not use the future daily range for scaling.
- [ ] A04: Every advertised feature group reaches the actual model matrix and has an ablation/support record.
- [ ] A05: Retain unsupported heads/assets and negative incremental results with honest downstream status.
- [ ] A06: Evidence includes command exit codes, artifact hashes, coverage/unknown counts, runtime, actual output inspection and the task’s declared limitations. All predecessor receipts verify.

- [ ] A07: EVIDENCE_MATRIX.json resolves every acceptance key and assigned failure case to actual code, executed commands, hashed evidence and inspected output under ASSURANCE.md; artifact/identity/command forgeries fail.
- [ ] A08: The assigned silent-failure probes pass with sensitive positive and negative controls, honest native/unknown/job counts, and no stale evidence. Return review-ready artifacts; subphase admission additionally requires the coordinator’s matching passing GATE_REVIEW.json.

### Commands and evidence

Commands below are **to run during implementation after their owner task creates the entrypoint**. They have not been run by this planning change. Use the existing environment; do not install arbitrary packages.

```bash
cd /workspace/implementation
.venv/bin/python -m pytest /workspace/implementation/tests/context_experts/test_p2_05.py -q
```

Then run the frozen engineering slice with the actual manifest and date list produced by the prerequisite (substitute the three ALL_CAPS paths/values; do not invent dates from outcomes):

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/run_context_experts.py slice --run-root RUN_ROOT --manifest FROZEN_MANIFEST --dates FROZEN_DATES --task P2-05
```

Reconcile all required cases, inspect output and profile before a full run. Search/release tasks additionally use the runner’s `run`, `resume` and `summarize` on the same immutable manifest; complete declared jobs before claiming an executed experiment.

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt TASK_RECEIPT_PATH
```

Expected artifacts under the task’s immutable report run (large data shards may be in the ignored cache, with file-level hashes in the manifest):

- `FEATURE_TARGET_CASES.json`
- `EXPERT_ARTIFACT.json`
- `ABLATIONS.json`
- `FORECASTS_MANIFEST.json`
- `VISUAL_QA.json`
- `TASK_RECEIPT.json` and `REPORT.md`, including acceptance keys A01–A08 and exact predecessor/artifact hashes.

### Completion and stop rules

Software checks must pass. A native cell may be unsupported only after the specified owned-input search and generic implementation/fixture verification. Sparse or negative research findings retain the baseline and all counts; they do not authorize more unregistered search. An implementation defect, unresolved job or timeout is work remaining. Use the shared receipt statuses; do not mark a phase complete from this individual card.

Any family report prints both the PHASE table and the audit table defined in WORKFLOW.md. Report the real completed behavior, commands, native evidence, limitations and next eligible dependency. Do not claim final profitability, author-exact proprietary recovery or complete native coverage without the required evidence.

### Copyable worker prompt

Generated from the task graph and pstack execution contract by tools/build_research_plan_bundles.py. Edit the canonical task above for research requirements; rebuild this section after prompt changes.

```text
/poteto-mode new task. Implement this feature: P2-05 — Fit directional range, topology and passage-time experts.
Read /workspace/planning/phase-2/tasks/P2-05.md and /workspace/planning/research-program/PSTACK_EXECUTION.md. Use the installed pstack router and the card's required contracts; this is execution of an existing specification.
Use the coordinator's actual working root, code identity, predecessor receipt paths/hashes, frozen manifest, dates and run root. Resolve missing values from those artifacts; report unresolved fields to the coordinator instead of inventing them.
Use the parent Grok model for every pstack role (inherit-parent means omit model). Use the installed poteto-agent wrapper when supported. No nested delegation; the coordinator owns fresh review and shared-file integration. Respect its single-writer checkout assignment.
Follow the exact formulas, clocks, schemas, allowed paths, finite budgets and A01, A02, A03, A04, A05, A06, A07, A08 checks. Name the data shape, implement one vertical behavior, run sensitive tests and the declared native slice/full run, and inspect actual output.
Done means all required artifacts exist and verify_research_release.py task exits 0 on the actual TASK_RECEIPT.json, with truthful coverage and disposition. Return real artifact paths, command results, decision-trail path and limitations. Keep runtime todos in the run's WORK_LOG.md and record playbook skips there.
Apply /workspace/planning/research-program/ASSURANCE.md and the card's assigned silent-failure cases: S01, S02, S03, S07, S08, S11, S16, S18, S19, S28, S32. Produce EVIDENCE_MATRIX.json linking every required check to real code, executed commands, hashes and inspected output selectors. Show sensitive accepted/rejected controls; preserve missing/ambiguous data and all declared jobs. A pass flag or your own verifier alone cannot prove completion. Return the evidence for the coordinator's separate GATE_REVIEW.json; do not edit fixed independent checks to obtain a pass.
Preserve accepted Phase 1 evidence, raw sources, missing/ambiguous inputs and unsuccessful trials. Perform the local task only; no external publication, shipping workflow or later phase. Do not stop at a plan or a passing toy test.
```

Canonical source: [P2-06.md](/workspace/.worktrees/docs-amend/planning/phase-2/tasks/P2-06.md).

## P2-06 — Fit auction, day-type and session-quality experts

Status: **planned; implementation not started by this planning task**.

Subphase: `04-context-mechanisms`. Dependencies: P2-04.

### Goal and boundary

Implement the exact Auction/session expert feature/target recipes, units, horizons, state semantics and missing/censored populations.

Implement only this task and its declared outputs. Preserve accepted Phase 1 code/reports, immutable sources and raw data. All new numerical recipes are registered research policies unless the source ledger proves literal attribution. No future input, later fit or all-history selected rule may enter an earlier decision.

### Read first

- [AGENTS.md](/workspace/AGENTS.md)
- [ROADMAP.md](/workspace/planning/ROADMAP.md)
- [PSTACK_EXECUTION.md](/workspace/planning/research-program/PSTACK_EXECUTION.md)
- [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md)
- [Assigned failure cases](/workspace/planning/research-program/SILENT_FAILURES.md)
- [WORKFLOW.md](/workspace/planning/research-program/WORKFLOW.md)
- [CONTEXT.md](/workspace/planning/phase-2/CONTEXT.md)
- [MODEL_FITTING.md](/workspace/planning/research-program/MODEL_FITTING.md)
- [EVALUATION.md](/workspace/planning/research-program/EVALUATION.md)
- [OUTCOMES.md](/workspace/planning/research-program/OUTCOMES.md)
- [DATA_CONTRACTS.md](/workspace/planning/research-program/DATA_CONTRACTS.md)

The named phase specification provides the exact formulas, proposed signatures, units and literal fixtures for this task. Existing symbols are marked as existing; proposed modules/commands are created by their owner tasks. Do not substitute remembered formulas or undocumented library defaults.

### Input and ownership contract

Consume verified predecessor receipts: **P2-04**. Their hashes and actual artifact paths go in this task receipt. Required schema details are in DATA_CONTRACTS; source adapters also read their named method predicates.

Allowed implementation/test paths:

- `/workspace/implementation/src/trading_research/research/experts/features/auction_session.py`
- `/workspace/implementation/src/trading_research/research/experts/labels/auction_session.py`
- `/workspace/implementation/src/trading_research/research/experts/auction_session.py`
- `/workspace/implementation/src/trading_research/research/experts/configs/auction_session.json`
- `/workspace/implementation/tests/context_experts/test_p2_06.py`

A worker does not edit another task’s shared files. Request an explicit integration patch from the subphase coordinator for runner registration, imports or additive shared-schema changes; the coordinator records it and reruns the affected contract tests. Keep independently fitted artifacts separate even when calculators are shared.

### Implementation steps

1. Implement the exact Auction/session expert feature/target recipes, units, horizons, state semantics and missing/censored populations.
2. Fit the declared linear/hinge classifier/regression/quantile heads with causal parent forecasts and fixed grids; keep artifact and support separate from other experts.
3. Run constant/session-frequency and price-only baselines, specified group ablations, chronological evaluation and deterministic native diagnostics.
4. Trace one actual output through its serialized schema, feature/stage parents and native receipt. Then run the verification below and write immutable evidence. A formula unit test alone does not complete a native-data or fitted-expert task.

### Worked and discriminating checks

Use the literal cases in the named mathematical contract and add one independently constructed negative case.

Use the shared [reference vectors](/workspace/planning/research-program/fixtures/reference_vectors.json) where applicable. Add a negative control that fails if the central behavior is removed, reversed, delayed incorrectly or fed future information. Model tests must include a known synthetic signal and a native chronological slice; never demand an empirical market improvement merely to pass software verification.

### Required failure checks

Acceptance amendment: `research-assurance-2026-09-14-v2`. Assigned cases: **S01, S02, S03, S07, S08, S11, S18, S19, S28, S32**. Use the exact probes, expected results and evidence in SILENT_FAILURES.md. Reuse current bound shared evidence where applicable; do not replace the task’s own sensitive/native check with a test count. Preserve prior attempts and produce the common task artifacts listed in TASK_GRAPH.json as well as the task-specific outputs below.

### Acceptance checklist

- [ ] A01: Current provisional states and completed future day type have different fields/clocks.
- [ ] A02: The exact operational label priority is tested at overlapping thresholds.
- [ ] A03: All matching session buckets retain no-opportunity/unknown counts.
- [ ] A04: Every advertised feature group reaches the actual model matrix and has an ablation/support record.
- [ ] A05: Retain unsupported heads/assets and negative incremental results with honest downstream status.
- [ ] A06: Evidence includes command exit codes, artifact hashes, coverage/unknown counts, runtime, actual output inspection and the task’s declared limitations. All predecessor receipts verify.

- [ ] A07: EVIDENCE_MATRIX.json resolves every acceptance key and assigned failure case to actual code, executed commands, hashed evidence and inspected output under ASSURANCE.md; artifact/identity/command forgeries fail.
- [ ] A08: The assigned silent-failure probes pass with sensitive positive and negative controls, honest native/unknown/job counts, and no stale evidence. Return review-ready artifacts; subphase admission additionally requires the coordinator’s matching passing GATE_REVIEW.json.

### Commands and evidence

Commands below are **to run during implementation after their owner task creates the entrypoint**. They have not been run by this planning change. Use the existing environment; do not install arbitrary packages.

```bash
cd /workspace/implementation
.venv/bin/python -m pytest /workspace/implementation/tests/context_experts/test_p2_06.py -q
```

Then run the frozen engineering slice with the actual manifest and date list produced by the prerequisite (substitute the three ALL_CAPS paths/values; do not invent dates from outcomes):

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/run_context_experts.py slice --run-root RUN_ROOT --manifest FROZEN_MANIFEST --dates FROZEN_DATES --task P2-06
```

Reconcile all required cases, inspect output and profile before a full run. Search/release tasks additionally use the runner’s `run`, `resume` and `summarize` on the same immutable manifest; complete declared jobs before claiming an executed experiment.

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt TASK_RECEIPT_PATH
```

Expected artifacts under the task’s immutable report run (large data shards may be in the ignored cache, with file-level hashes in the manifest):

- `FEATURE_TARGET_CASES.json`
- `EXPERT_ARTIFACT.json`
- `ABLATIONS.json`
- `FORECASTS_MANIFEST.json`
- `VISUAL_QA.json`
- `TASK_RECEIPT.json` and `REPORT.md`, including acceptance keys A01–A08 and exact predecessor/artifact hashes.

### Completion and stop rules

Software checks must pass. A native cell may be unsupported only after the specified owned-input search and generic implementation/fixture verification. Sparse or negative research findings retain the baseline and all counts; they do not authorize more unregistered search. An implementation defect, unresolved job or timeout is work remaining. Use the shared receipt statuses; do not mark a phase complete from this individual card.

Any family report prints both the PHASE table and the audit table defined in WORKFLOW.md. Report the real completed behavior, commands, native evidence, limitations and next eligible dependency. Do not claim final profitability, author-exact proprietary recovery or complete native coverage without the required evidence.

### Copyable worker prompt

Generated from the task graph and pstack execution contract by tools/build_research_plan_bundles.py. Edit the canonical task above for research requirements; rebuild this section after prompt changes.

```text
/poteto-mode new task. Implement this feature: P2-06 — Fit auction, day-type and session-quality experts.
Read /workspace/planning/phase-2/tasks/P2-06.md and /workspace/planning/research-program/PSTACK_EXECUTION.md. Use the installed pstack router and the card's required contracts; this is execution of an existing specification.
Use the coordinator's actual working root, code identity, predecessor receipt paths/hashes, frozen manifest, dates and run root. Resolve missing values from those artifacts; report unresolved fields to the coordinator instead of inventing them.
Use the parent Grok model for every pstack role (inherit-parent means omit model). Use the installed poteto-agent wrapper when supported. No nested delegation; the coordinator owns fresh review and shared-file integration. Respect its single-writer checkout assignment.
Follow the exact formulas, clocks, schemas, allowed paths, finite budgets and A01, A02, A03, A04, A05, A06, A07, A08 checks. Name the data shape, implement one vertical behavior, run sensitive tests and the declared native slice/full run, and inspect actual output.
Done means all required artifacts exist and verify_research_release.py task exits 0 on the actual TASK_RECEIPT.json, with truthful coverage and disposition. Return real artifact paths, command results, decision-trail path and limitations. Keep runtime todos in the run's WORK_LOG.md and record playbook skips there.
Apply /workspace/planning/research-program/ASSURANCE.md and the card's assigned silent-failure cases: S01, S02, S03, S07, S08, S11, S18, S19, S28, S32. Produce EVIDENCE_MATRIX.json linking every required check to real code, executed commands, hashes and inspected output selectors. Show sensitive accepted/rejected controls; preserve missing/ambiguous data and all declared jobs. A pass flag or your own verifier alone cannot prove completion. Return the evidence for the coordinator's separate GATE_REVIEW.json; do not edit fixed independent checks to obtain a pass.
Preserve accepted Phase 1 evidence, raw sources, missing/ambiguous inputs and unsuccessful trials. Perform the local task only; no external publication, shipping workflow or later phase. Do not stop at a plan or a passing toy test.
```

Canonical source: [P2-07.md](/workspace/.worktrees/docs-amend/planning/phase-2/tasks/P2-07.md).

## P2-07 — Fit flow reward, defense and failed-push experts

Status: **planned; implementation not started by this planning task**.

Subphase: `04-context-mechanisms`. Dependencies: P2-04.

### Goal and boundary

Implement the exact Flow-memory expert feature/target recipes, units, horizons, state semantics and missing/censored populations.

Implement only this task and its declared outputs. Preserve accepted Phase 1 code/reports, immutable sources and raw data. All new numerical recipes are registered research policies unless the source ledger proves literal attribution. No future input, later fit or all-history selected rule may enter an earlier decision.

### Read first

- [AGENTS.md](/workspace/AGENTS.md)
- [ROADMAP.md](/workspace/planning/ROADMAP.md)
- [PSTACK_EXECUTION.md](/workspace/planning/research-program/PSTACK_EXECUTION.md)
- [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md)
- [Assigned failure cases](/workspace/planning/research-program/SILENT_FAILURES.md)
- [WORKFLOW.md](/workspace/planning/research-program/WORKFLOW.md)
- [CONTEXT.md](/workspace/planning/phase-2/CONTEXT.md)
- [MODEL_FITTING.md](/workspace/planning/research-program/MODEL_FITTING.md)
- [EVALUATION.md](/workspace/planning/research-program/EVALUATION.md)
- [OUTCOMES.md](/workspace/planning/research-program/OUTCOMES.md)
- [DATA_CONTRACTS.md](/workspace/planning/research-program/DATA_CONTRACTS.md)

The named phase specification provides the exact formulas, proposed signatures, units and literal fixtures for this task. Existing symbols are marked as existing; proposed modules/commands are created by their owner tasks. Do not substitute remembered formulas or undocumented library defaults.

### Input and ownership contract

Consume verified predecessor receipts: **P2-04**. Their hashes and actual artifact paths go in this task receipt. Required schema details are in DATA_CONTRACTS; source adapters also read their named method predicates.

Allowed implementation/test paths:

- `/workspace/implementation/src/trading_research/research/experts/features/flow_memory.py`
- `/workspace/implementation/src/trading_research/research/experts/labels/flow_memory.py`
- `/workspace/implementation/src/trading_research/research/experts/flow_memory.py`
- `/workspace/implementation/src/trading_research/research/experts/configs/flow_memory.json`
- `/workspace/implementation/tests/context_experts/test_p2_07.py`

A worker does not edit another task’s shared files. Request an explicit integration patch from the subphase coordinator for runner registration, imports or additive shared-schema changes; the coordinator records it and reruns the affected contract tests. Keep independently fitted artifacts separate even when calculators are shared.

### Implementation steps

1. Implement the exact Flow-memory expert feature/target recipes, units, horizons, state semantics and missing/censored populations.
2. Fit the declared linear/hinge classifier/regression/quantile heads with causal parent forecasts and fixed grids; keep artifact and support separate from other experts.
3. Run constant/session-frequency and price-only baselines, specified group ablations, chronological evaluation and deterministic native diagnostics.
4. Trace one actual output through its serialized schema, feature/stage parents and native receipt. Then run the verification below and write immutable evidence. A formula unit test alone does not complete a native-data or fitted-expert task.

### Worked and discriminating checks

Use the literal cases in the named mathematical contract and add one independently constructed negative case.

Use the shared [reference vectors](/workspace/planning/research-program/fixtures/reference_vectors.json) where applicable. Add a negative control that fails if the central behavior is removed, reversed, delayed incorrectly or fed future information. Model tests must include a known synthetic signal and a native chronological slice; never demand an empirical market improvement merely to pass software verification.

### Required failure checks

Acceptance amendment: `research-assurance-2026-09-14-v2`. Assigned cases: **S01, S02, S03, S07, S08, S09, S11, S18, S19, S23, S28, S32**. Use the exact probes, expected results and evidence in SILENT_FAILURES.md. Reuse current bound shared evidence where applicable; do not replace the task’s own sensitive/native check with a test count. Preserve prior attempts and produce the common task artifacts listed in TASK_GRAPH.json as well as the task-specific outputs below.

### Acceptance checklist

- [ ] A01: Unresolved cohorts remain unavailable to the current forecast.
- [ ] A02: High delta with negative markout is not rewarded aggression.
- [ ] A03: BBO changes do not certify ten-level cancellation/refill state.
- [ ] A04: Every advertised feature group reaches the actual model matrix and has an ablation/support record.
- [ ] A05: Retain unsupported heads/assets and negative incremental results with honest downstream status.
- [ ] A06: Evidence includes command exit codes, artifact hashes, coverage/unknown counts, runtime, actual output inspection and the task’s declared limitations. All predecessor receipts verify.

- [ ] A07: EVIDENCE_MATRIX.json resolves every acceptance key and assigned failure case to actual code, executed commands, hashed evidence and inspected output under ASSURANCE.md; artifact/identity/command forgeries fail.
- [ ] A08: The assigned silent-failure probes pass with sensitive positive and negative controls, honest native/unknown/job counts, and no stale evidence. Return review-ready artifacts; subphase admission additionally requires the coordinator’s matching passing GATE_REVIEW.json.

### Commands and evidence

Commands below are **to run during implementation after their owner task creates the entrypoint**. They have not been run by this planning change. Use the existing environment; do not install arbitrary packages.

```bash
cd /workspace/implementation
.venv/bin/python -m pytest /workspace/implementation/tests/context_experts/test_p2_07.py -q
```

Then run the frozen engineering slice with the actual manifest and date list produced by the prerequisite (substitute the three ALL_CAPS paths/values; do not invent dates from outcomes):

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/run_context_experts.py slice --run-root RUN_ROOT --manifest FROZEN_MANIFEST --dates FROZEN_DATES --task P2-07
```

Reconcile all required cases, inspect output and profile before a full run. Search/release tasks additionally use the runner’s `run`, `resume` and `summarize` on the same immutable manifest; complete declared jobs before claiming an executed experiment.

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt TASK_RECEIPT_PATH
```

Expected artifacts under the task’s immutable report run (large data shards may be in the ignored cache, with file-level hashes in the manifest):

- `FEATURE_TARGET_CASES.json`
- `EXPERT_ARTIFACT.json`
- `ABLATIONS.json`
- `FORECASTS_MANIFEST.json`
- `VISUAL_QA.json`
- `TASK_RECEIPT.json` and `REPORT.md`, including acceptance keys A01–A08 and exact predecessor/artifact hashes.

### Completion and stop rules

Software checks must pass. A native cell may be unsupported only after the specified owned-input search and generic implementation/fixture verification. Sparse or negative research findings retain the baseline and all counts; they do not authorize more unregistered search. An implementation defect, unresolved job or timeout is work remaining. Use the shared receipt statuses; do not mark a phase complete from this individual card.

Any family report prints both the PHASE table and the audit table defined in WORKFLOW.md. Report the real completed behavior, commands, native evidence, limitations and next eligible dependency. Do not claim final profitability, author-exact proprietary recovery or complete native coverage without the required evidence.

### Copyable worker prompt

Generated from the task graph and pstack execution contract by tools/build_research_plan_bundles.py. Edit the canonical task above for research requirements; rebuild this section after prompt changes.

```text
/poteto-mode new task. Implement this feature: P2-07 — Fit flow reward, defense and failed-push experts.
Read /workspace/planning/phase-2/tasks/P2-07.md and /workspace/planning/research-program/PSTACK_EXECUTION.md. Use the installed pstack router and the card's required contracts; this is execution of an existing specification.
Use the coordinator's actual working root, code identity, predecessor receipt paths/hashes, frozen manifest, dates and run root. Resolve missing values from those artifacts; report unresolved fields to the coordinator instead of inventing them.
Use the parent Grok model for every pstack role (inherit-parent means omit model). Use the installed poteto-agent wrapper when supported. No nested delegation; the coordinator owns fresh review and shared-file integration. Respect its single-writer checkout assignment.
Follow the exact formulas, clocks, schemas, allowed paths, finite budgets and A01, A02, A03, A04, A05, A06, A07, A08 checks. Name the data shape, implement one vertical behavior, run sensitive tests and the declared native slice/full run, and inspect actual output.
Done means all required artifacts exist and verify_research_release.py task exits 0 on the actual TASK_RECEIPT.json, with truthful coverage and disposition. Return real artifact paths, command results, decision-trail path and limitations. Keep runtime todos in the run's WORK_LOG.md and record playbook skips there.
Apply /workspace/planning/research-program/ASSURANCE.md and the card's assigned silent-failure cases: S01, S02, S03, S07, S08, S09, S11, S18, S19, S23, S28, S32. Produce EVIDENCE_MATRIX.json linking every required check to real code, executed commands, hashes and inspected output selectors. Show sensitive accepted/rejected controls; preserve missing/ambiguous data and all declared jobs. A pass flag or your own verifier alone cannot prove completion. Return the evidence for the coordinator's separate GATE_REVIEW.json; do not edit fixed independent checks to obtain a pass.
Preserve accepted Phase 1 evidence, raw sources, missing/ambiguous inputs and unsuccessful trials. Perform the local task only; no external publication, shipping workflow or later phase. Do not stop at a plan or a passing toy test.
```

Canonical source: [P2-11.md](/workspace/.worktrees/docs-amend/planning/phase-2/tasks/P2-11.md).

## P2-11 — Implement flow, exposure changes and repricing scenarios

Status: **planned; implementation not started by this planning task**.

Subphase: `04-context-mechanisms`. Dependencies: P2-10, P2-02, P2-04.

### Goal and boundary

Compute signed/unsigned/unknown option contracts,premium,delta,gamma,vega/vanna at trade-available surfaces; keep complex/roll ambiguity flags.

Implement only this task and its declared outputs. Preserve accepted Phase 1 code/reports, immutable sources and raw data. All new numerical recipes are registered research policies unless the source ledger proves literal attribution. No future input, later fit or all-history selected rule may enter an earlier decision.

### Read first

- [AGENTS.md](/workspace/AGENTS.md)
- [ROADMAP.md](/workspace/planning/ROADMAP.md)
- [PSTACK_EXECUTION.md](/workspace/planning/research-program/PSTACK_EXECUTION.md)
- [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md)
- [Assigned failure cases](/workspace/planning/research-program/SILENT_FAILURES.md)
- [WORKFLOW.md](/workspace/planning/research-program/WORKFLOW.md)
- [OPTIONS.md](/workspace/planning/phase-2/OPTIONS.md)
- [MODEL_FITTING.md](/workspace/planning/research-program/MODEL_FITTING.md)
- [EVALUATION.md](/workspace/planning/research-program/EVALUATION.md)
- [OUTCOMES.md](/workspace/planning/research-program/OUTCOMES.md)

The named phase specification provides the exact formulas, proposed signatures, units and literal fixtures for this task. Existing symbols are marked as existing; proposed modules/commands are created by their owner tasks. Do not substitute remembered formulas or undocumented library defaults.

The joint-volatility [feature/target contract](/workspace/planning/phase-2/VOLATILITY.md) supplies the exact variance labels and causal baseline used by this options-context fit.

### Input and ownership contract

Consume verified predecessor receipts: **P2-10, P2-02, P2-04**. Their hashes and actual artifact paths go in this task receipt. Required schema details are in DATA_CONTRACTS; source adapters also read their named method predicates.

Allowed implementation/test paths:

- `/workspace/implementation/src/trading_research/research/experts/options/flow.py`
- `/workspace/implementation/src/trading_research/research/experts/options/scenarios.py`
- `/workspace/implementation/src/trading_research/research/experts/options/context.py`
- `/workspace/implementation/tests/context_experts/test_p2_11.py`

A worker does not edit another task’s shared files. Request an explicit integration patch from the subphase coordinator for runner registration, imports or additive shared-schema changes; the coordinator records it and reruns the affected contract tests. Keep independently fitted artifacts separate even when calculators are shared.

### Implementation steps

1. Compute signed/unsigned/unknown option contracts,premium,delta,gamma,vega/vanna at trade-available surfaces; keep complex/roll ambiguity flags.
2. Implement node churn/migration, telescoping spot-IV-time-OI-universe decomposition and fixed shock grid plus sticky-strike/moneyness sensitivity.
3. Fit a separate options-context expert for NQ next 30/60m directional/variance surprise using B0/B1 features and common recipes. Preserve all-root contribution ablations.
4. Trace one actual output through its serialized schema, feature/stage parents and native receipt. Then run the verification below and write immutable evidence. A formula unit test alone does not complete a native-data or fitted-expert task.

### Worked and discriminating checks

Use the literal cases in the named mathematical contract and add one independently constructed negative case.

Use the shared [reference vectors](/workspace/planning/research-program/fixtures/reference_vectors.json) where applicable. Add a negative control that fails if the central behavior is removed, reversed, delayed incorrectly or fed future information. Model tests must include a known synthetic signal and a native chronological slice; never demand an empirical market improvement merely to pass software verification.

### Required failure checks

Acceptance amendment: `research-assurance-2026-09-14-v2`. Assigned cases: **S01, S02, S03, S07, S08, S09, S14, S25, S26, S27**. Use the exact probes, expected results and evidence in SILENT_FAILURES.md. Reuse current bound shared evidence where applicable; do not replace the task’s own sensitive/native check with a test count. Preserve prior attempts and produce the common task artifacts listed in TASK_GRAPH.json as well as the task-specific outputs below.

### Acceptance checklist

- [ ] A01: Inside-spread trades remain unknown and cannot become known aggressive opening flow.
- [ ] A02: A trade cannot consume a later surface snapshot.
- [ ] A03: Decomposition components sum to total change; reverse-order differences are reported.
- [ ] A04: Changing universe alone cannot be described as observed dealer rehedging.
- [ ] A05: Options-context artifact has a separate fit/target/lineage from the joint volatility expert.
- [ ] A06: Evidence includes command exit codes, artifact hashes, coverage/unknown counts, runtime, actual output inspection and the task’s declared limitations. All predecessor receipts verify.

- [ ] A07: EVIDENCE_MATRIX.json resolves every acceptance key and assigned failure case to actual code, executed commands, hashed evidence and inspected output under ASSURANCE.md; artifact/identity/command forgeries fail.
- [ ] A08: The assigned silent-failure probes pass with sensitive positive and negative controls, honest native/unknown/job counts, and no stale evidence. Return review-ready artifacts; subphase admission additionally requires the coordinator’s matching passing GATE_REVIEW.json.

### Commands and evidence

Commands below are **to run during implementation after their owner task creates the entrypoint**. They have not been run by this planning change. Use the existing environment; do not install arbitrary packages.

```bash
cd /workspace/implementation
.venv/bin/python -m pytest /workspace/implementation/tests/context_experts/test_p2_11.py -q
```

Then run the frozen engineering slice with the actual manifest and date list produced by the prerequisite (substitute the three ALL_CAPS paths/values; do not invent dates from outcomes):

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/run_context_experts.py slice --run-root RUN_ROOT --manifest FROZEN_MANIFEST --dates FROZEN_DATES --task P2-11
```

Reconcile all required cases, inspect output and profile before a full run. Search/release tasks additionally use the runner’s `run`, `resume` and `summarize` on the same immutable manifest; complete declared jobs before claiming an executed experiment.

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt TASK_RECEIPT_PATH
```

Expected artifacts under the task’s immutable report run (large data shards may be in the ignored cache, with file-level hashes in the manifest):

- `OPTION_FLOW.json`
- `EXPOSURE_CHANGE_CASES.json`
- `SCENARIO_BOARDS.json`
- `OPTIONS_CONTEXT_EVALUATION.json`
- `TASK_RECEIPT.json` and `REPORT.md`, including acceptance keys A01–A08 and exact predecessor/artifact hashes.

### Completion and stop rules

Software checks must pass. A native cell may be unsupported only after the specified owned-input search and generic implementation/fixture verification. Sparse or negative research findings retain the baseline and all counts; they do not authorize more unregistered search. An implementation defect, unresolved job or timeout is work remaining. Use the shared receipt statuses; do not mark a phase complete from this individual card.

Any family report prints both the PHASE table and the audit table defined in WORKFLOW.md. Report the real completed behavior, commands, native evidence, limitations and next eligible dependency. Do not claim final profitability, author-exact proprietary recovery or complete native coverage without the required evidence.

### Copyable worker prompt

Generated from the task graph and pstack execution contract by tools/build_research_plan_bundles.py. Edit the canonical task above for research requirements; rebuild this section after prompt changes.

```text
/poteto-mode new task. Implement this feature: P2-11 — Implement flow, exposure changes and repricing scenarios.
Read /workspace/planning/phase-2/tasks/P2-11.md and /workspace/planning/research-program/PSTACK_EXECUTION.md. Use the installed pstack router and the card's required contracts; this is execution of an existing specification.
Use the coordinator's actual working root, code identity, predecessor receipt paths/hashes, frozen manifest, dates and run root. Resolve missing values from those artifacts; report unresolved fields to the coordinator instead of inventing them.
Use the parent Grok model for every pstack role (inherit-parent means omit model). Use the installed poteto-agent wrapper when supported. No nested delegation; the coordinator owns fresh review and shared-file integration. Respect its single-writer checkout assignment.
Follow the exact formulas, clocks, schemas, allowed paths, finite budgets and A01, A02, A03, A04, A05, A06, A07, A08 checks. Name the data shape, implement one vertical behavior, run sensitive tests and the declared native slice/full run, and inspect actual output.
Done means all required artifacts exist and verify_research_release.py task exits 0 on the actual TASK_RECEIPT.json, with truthful coverage and disposition. Return real artifact paths, command results, decision-trail path and limitations. Keep runtime todos in the run's WORK_LOG.md and record playbook skips there.
Apply /workspace/planning/research-program/ASSURANCE.md and the card's assigned silent-failure cases: S01, S02, S03, S07, S08, S09, S14, S25, S26, S27. Produce EVIDENCE_MATRIX.json linking every required check to real code, executed commands, hashes and inspected output selectors. Show sensitive accepted/rejected controls; preserve missing/ambiguous data and all declared jobs. A pass flag or your own verifier alone cannot prove completion. Return the evidence for the coordinator's separate GATE_REVIEW.json; do not edit fixed independent checks to obtain a pass.
Preserve accepted Phase 1 evidence, raw sources, missing/ambiguous inputs and unsuccessful trials. Perform the local task only; no external publication, shipping workflow or later phase. Do not stop at a plan or a passing toy test.
```

Canonical source: [P2-08.md](/workspace/.worktrees/docs-amend/planning/phase-2/tasks/P2-08.md).

## P2-08 — Fit native cross-market and spot-IV coupling expert

Status: **planned; implementation not started by this planning task**.

Subphase: `04-context-mechanisms`. Dependencies: P2-04, P2-11.

### Goal and boundary

Implement the exact Cross-market expert feature/target recipes, units, horizons, state semantics and missing/censored populations.

Implement only this task and its declared outputs. Preserve accepted Phase 1 code/reports, immutable sources and raw data. All new numerical recipes are registered research policies unless the source ledger proves literal attribution. No future input, later fit or all-history selected rule may enter an earlier decision.

### Read first

- [AGENTS.md](/workspace/AGENTS.md)
- [ROADMAP.md](/workspace/planning/ROADMAP.md)
- [PSTACK_EXECUTION.md](/workspace/planning/research-program/PSTACK_EXECUTION.md)
- [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md)
- [Assigned failure cases](/workspace/planning/research-program/SILENT_FAILURES.md)
- [WORKFLOW.md](/workspace/planning/research-program/WORKFLOW.md)
- [CONTEXT.md](/workspace/planning/phase-2/CONTEXT.md)
- [MODEL_FITTING.md](/workspace/planning/research-program/MODEL_FITTING.md)
- [EVALUATION.md](/workspace/planning/research-program/EVALUATION.md)
- [OUTCOMES.md](/workspace/planning/research-program/OUTCOMES.md)
- [DATA_CONTRACTS.md](/workspace/planning/research-program/DATA_CONTRACTS.md)

The named phase specification provides the exact formulas, proposed signatures, units and literal fixtures for this task. Existing symbols are marked as existing; proposed modules/commands are created by their owner tasks. Do not substitute remembered formulas or undocumented library defaults.

### Input and ownership contract

Consume verified predecessor receipts: **P2-04, P2-11**. Their hashes and actual artifact paths go in this task receipt. Required schema details are in DATA_CONTRACTS; source adapters also read their named method predicates.

Allowed implementation/test paths:

- `/workspace/implementation/src/trading_research/research/experts/features/cross_market.py`
- `/workspace/implementation/src/trading_research/research/experts/labels/cross_market.py`
- `/workspace/implementation/src/trading_research/research/experts/cross_market.py`
- `/workspace/implementation/src/trading_research/research/experts/configs/cross_market.json`
- `/workspace/implementation/tests/context_experts/test_p2_08.py`

A worker does not edit another task’s shared files. Request an explicit integration patch from the subphase coordinator for runner registration, imports or additive shared-schema changes; the coordinator records it and reruns the affected contract tests. Keep independently fitted artifacts separate even when calculators are shared.

### Implementation steps

1. Implement the exact Cross-market expert feature/target recipes, units, horizons, state semantics and missing/censored populations.
2. Fit the declared linear/hinge classifier/regression/quantile heads with causal parent forecasts and fixed grids; keep artifact and support separate from other experts.
3. Run constant/session-frequency and price-only baselines, specified group ablations, chronological evaluation and deterministic native diagnostics.
4. Trace one actual output through its serialized schema, feature/stage parents and native receipt. Then run the verification below and write immutable evidence. A formula unit test alone does not complete a native-data or fitted-expert task.

### Worked and discriminating checks

Use the literal cases in the named mathematical contract and add one independently constructed negative case.

Use the shared [reference vectors](/workspace/planning/research-program/fixtures/reference_vectors.json) where applicable. Add a negative control that fails if the central behavior is removed, reversed, delayed incorrectly or fed future information. Model tests must include a known synthetic signal and a native chronological slice; never demand an empirical market improvement merely to pass software verification.

### Required failure checks

Acceptance amendment: `research-assurance-2026-09-14-v2`. Assigned cases: **S01, S02, S03, S07, S08, S11, S15, S18, S19, S28, S31, S32**. Use the exact probes, expected results and evidence in SILENT_FAILURES.md. Reuse current bound shared evidence where applicable; do not replace the task’s own sensitive/native check with a test count. Preserve prior attempts and produce the common task artifacts listed in TASK_GRAPH.json as well as the task-specific outputs below.

### Acceptance checklist

- [ ] A01: Lag sign convention and future perturbation catch accidental future returns.
- [ ] A02: SMT pivots become available only after right-neighbor confirmation.
- [ ] A03: No source strategy is cloned on ES/QQQ/SPX or another related asset.
- [ ] A04: Every advertised feature group reaches the actual model matrix and has an ablation/support record.
- [ ] A05: Retain unsupported heads/assets and negative incremental results with honest downstream status.
- [ ] A06: Evidence includes command exit codes, artifact hashes, coverage/unknown counts, runtime, actual output inspection and the task’s declared limitations. All predecessor receipts verify.

- [ ] A07: EVIDENCE_MATRIX.json resolves every acceptance key and assigned failure case to actual code, executed commands, hashed evidence and inspected output under ASSURANCE.md; artifact/identity/command forgeries fail.
- [ ] A08: The assigned silent-failure probes pass with sensitive positive and negative controls, honest native/unknown/job counts, and no stale evidence. Return review-ready artifacts; subphase admission additionally requires the coordinator’s matching passing GATE_REVIEW.json.

### Commands and evidence

Commands below are **to run during implementation after their owner task creates the entrypoint**. They have not been run by this planning change. Use the existing environment; do not install arbitrary packages.

```bash
cd /workspace/implementation
.venv/bin/python -m pytest /workspace/implementation/tests/context_experts/test_p2_08.py -q
```

Then run the frozen engineering slice with the actual manifest and date list produced by the prerequisite (substitute the three ALL_CAPS paths/values; do not invent dates from outcomes):

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/run_context_experts.py slice --run-root RUN_ROOT --manifest FROZEN_MANIFEST --dates FROZEN_DATES --task P2-08
```

Reconcile all required cases, inspect output and profile before a full run. Search/release tasks additionally use the runner’s `run`, `resume` and `summarize` on the same immutable manifest; complete declared jobs before claiming an executed experiment.

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt TASK_RECEIPT_PATH
```

Expected artifacts under the task’s immutable report run (large data shards may be in the ignored cache, with file-level hashes in the manifest):

- `FEATURE_TARGET_CASES.json`
- `EXPERT_ARTIFACT.json`
- `ABLATIONS.json`
- `FORECASTS_MANIFEST.json`
- `VISUAL_QA.json`
- `TASK_RECEIPT.json` and `REPORT.md`, including acceptance keys A01–A08 and exact predecessor/artifact hashes.

### Completion and stop rules

Software checks must pass. A native cell may be unsupported only after the specified owned-input search and generic implementation/fixture verification. Sparse or negative research findings retain the baseline and all counts; they do not authorize more unregistered search. An implementation defect, unresolved job or timeout is work remaining. Use the shared receipt statuses; do not mark a phase complete from this individual card.

Any family report prints both the PHASE table and the audit table defined in WORKFLOW.md. Report the real completed behavior, commands, native evidence, limitations and next eligible dependency. Do not claim final profitability, author-exact proprietary recovery or complete native coverage without the required evidence.

### Copyable worker prompt

Generated from the task graph and pstack execution contract by tools/build_research_plan_bundles.py. Edit the canonical task above for research requirements; rebuild this section after prompt changes.

```text
/poteto-mode new task. Implement this feature: P2-08 — Fit native cross-market and spot-IV coupling expert.
Read /workspace/planning/phase-2/tasks/P2-08.md and /workspace/planning/research-program/PSTACK_EXECUTION.md. Use the installed pstack router and the card's required contracts; this is execution of an existing specification.
Use the coordinator's actual working root, code identity, predecessor receipt paths/hashes, frozen manifest, dates and run root. Resolve missing values from those artifacts; report unresolved fields to the coordinator instead of inventing them.
Use the parent Grok model for every pstack role (inherit-parent means omit model). Use the installed poteto-agent wrapper when supported. No nested delegation; the coordinator owns fresh review and shared-file integration. Respect its single-writer checkout assignment.
Follow the exact formulas, clocks, schemas, allowed paths, finite budgets and A01, A02, A03, A04, A05, A06, A07, A08 checks. Name the data shape, implement one vertical behavior, run sensitive tests and the declared native slice/full run, and inspect actual output.
Done means all required artifacts exist and verify_research_release.py task exits 0 on the actual TASK_RECEIPT.json, with truthful coverage and disposition. Return real artifact paths, command results, decision-trail path and limitations. Keep runtime todos in the run's WORK_LOG.md and record playbook skips there.
Apply /workspace/planning/research-program/ASSURANCE.md and the card's assigned silent-failure cases: S01, S02, S03, S07, S08, S11, S15, S18, S19, S28, S31, S32. Produce EVIDENCE_MATRIX.json linking every required check to real code, executed commands, hashes and inspected output selectors. Show sensitive accepted/rejected controls; preserve missing/ambiguous data and all declared jobs. A pass flag or your own verifier alone cannot prove completion. Return the evidence for the coordinator's separate GATE_REVIEW.json; do not edit fixed independent checks to obtain a pass.
Preserve accepted Phase 1 evidence, raw sources, missing/ambiguous inputs and unsuccessful trials. Perform the local task only; no external publication, shipping workflow or later phase. Do not stop at a plan or a passing toy test.
```
