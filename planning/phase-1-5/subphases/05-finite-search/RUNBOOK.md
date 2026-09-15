# Phase 1.5 / 05-finite-search — coordinator runbook

Status: **planned; not implemented by this planning task**. Generated from canonical contracts and task cards. Edit those sources, then rebuild; do not edit this bundle independently.

Source content SHA256: `c6cfc5144b157cbae888189e8b88ce2f32f4b5678ca5ed919d7d83f0d5887706`.

Previous gate: **04-family-adapters**. External task dependencies: P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16. Read and verify their actual receipts before implementation.

## Coordinator work order

Enter through /poteto-mode new task and run only this bounded subphase to its verification predicate. Match the installed playbook, copy its steps into runtime todos and record explicit skip reasons. Apply the included Grok-only model and host-capability overrides to all routed skills. A large-task figure-it-out route must use this existing runbook, not invent a new research plan.

Implement only the tasks listed below, in dependency order. Start with one verified vertical slice. Delegate bounded cards with the complete brief in PSTACK_EXECUTION; a shared checkout has one code writer at a time. At most three live Grok/poteto agents including the coordinator; unavailable workers mean sequential execution. The coordinator reviews and integrates shared schemas/runners and alone writes SUBPHASE_RECEIPT.json.

Read workspace AGENTS.md. The executable contracts and task cards are included below. Source method wiki pages linked by a task are additional focused worker reads; they retain the precise author predicates. Do not reread the whole archive or invent alternative formulas.

The native slice, numerical checks, coverage, future perturbation, actual output inspection and immutable receipts are part of the task. A negative/inconclusive research result is valid; missing implementation is not. Preserve prior evidence and all unsuccessful trials. Do not start the next subphase automatically.

| Task | Dependencies | Canonical card |
| --- | --- | --- |
| P15-16A — Source-fidelity baseline B0.2 and author-example replay | P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16 | [Task](/workspace/planning/phase-1-5/tasks/P15-16A.md) |
| P15-17 — Execute and reconcile the breadth screen | P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A | [Task](/workspace/planning/phase-1-5/tasks/P15-17.md) |
| P15-18 — Run one bounded refinement and choose honest dispositions | P15-17 | [Task](/workspace/planning/phase-1-5/tasks/P15-18.md) |

## Subphase completion

Collect verified task receipts for every listed task. Record acceptance checks, hashes, native date/coverage identities, schema versions, shared-file integration diffs, runtime and remaining input limits. Write SUBPHASE_RECEIPT.json under a new immutable report run and verify it with verify_research_release.py subphase. The foundation coordinator first creates that verifier and retrospectively verifies its bootstrap task. Then apply ASSURANCE.md: inspect every EVIDENCE_MATRIX.json and assigned failure case, run required independent checks, and write a separately hashed GATE_REVIEW.json referencing the immutable candidate receipt. Closure requires receipt verification plus a matching passing review with no unresolved correctness, causality or integrity findings. Valid controls must pass as well as invalid controls fail.

Return the user a concise completion report, both required family tables when reporting family results, real evidence links, limitations and the next eligible prompt. A subphase gate closes only this subphase. Phase 2 requires all of Phase 1.5 closed first.
Canonical source: [PSTACK_EXECUTION.md](/workspace/planning/research-program/PSTACK_EXECUTION.md).

## Run these packs through pstack in Grok

The user's Grok build includes pstack. Start each new coordinator, worker or review task with `/poteto-mode new task.` followed by the concrete goal and finish condition. Resume prompts say that they are taking over existing work. The installed router owns skill sequencing. These packs supply the research specification, ownership and proof requirements.

Every route and subphase obeys [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md) and the task's assigned [silent failure checks](/workspace/planning/research-program/SILENT_FAILURES.md). The v2 acceptance amendment requires real behavior evidence and a separately bound review at each subphase boundary. The [foundation repair](/workspace/planning/research-program/FOUNDATION_REPAIR.md) is the current entry; a prior closing message or receipt PASS does not overrule the independent findings.

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

The registered market experiments are not the pstack **Eval** playbook. That playbook measures agent/prompt behavior with blinded candidate agents; it does not define financial model evaluation. Use [EVALUATION.md](/workspace/planning/research-program/EVALUATION.md) for folds, outcomes, selection and statistical gates.

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

Canonical source: [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md).

## Evidence and failure checks

Acceptance amendment `research-assurance-2026-09-14-v3`. This is part of every Phase 1.5 and Phase 2 task. It strengthens software acceptance without changing research formulas, candidate budgets or statistical thresholds. [Amendment history](/workspace/planning/research-program/AMENDMENTS.json) preserves the previous foundation identities. [Failure cases](/workspace/planning/research-program/SILENT_FAILURES.md) and their [machine-readable assignment](/workspace/planning/research-program/ASSURANCE_CASES.json) specify the additional checks by task.

### Completion requires observable behavior

The implementer must satisfy the task card, the assigned failure cases and the shared contract. The coordinator must inspect the code and reproduce the evidence. An acceptance boolean, a worker's summary, a pytest count, or a successful call to a newly written verifier is insufficient on its own. Treat a verifier as software under test: show it rejects plausible false claims while continuing to accept correctly implemented work.

Each writing task produces `EVIDENCE_MATRIX.json`, `WORK_LOG.md` and its own `DECISIONS.tsv`. Foundation bootstrap does not waive these artifacts. Record actual commands and times as work occurs. A reconstructed time must be labelled reconstructed with its source; do not present it as measured. Shared coordinator logs may link worker logs but cannot replace them. Reviewers inspect implementation behavior separately from log completeness.

Use this matrix schema, `research-evidence-matrix-v2`:

```json
{
  "schema_version": "research-evidence-matrix-v2",
  "task_id": "ACTUAL_TASK_ID",
  "assurance_version": "research-assurance-2026-09-14-v3",
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
2. **Required plan files.** Write `PLAN_SNAPSHOT.json` with `schema_version`, `assurance_version`, `files` (repository-relative path to SHA256) and `snapshot_paths` (same keys to preserved copies). The file set is the task card, all graph `reads`, `TASK_GRAPH.json` and `ASSURANCE_CASES.json`; no omitted references or duplicate aliases. Snapshot the actual bytes. `plan_sha256 = SHA256(canonical_json(files))`. A historical snapshot can be inspected after the live docs change; a downstream admission must also require the currently authorized assurance version. An older graph cannot waive an amendment. Preserved snapshot copies must match that receipt's own declared hashes. Live workspace bytes of a declared plan file verify if they equal the declared hash, or if `AMENDMENTS.json` contains an ordered chain of entries from the declared hash to the live hash for that path. New-shape entries carry `date`, `id`, `changed_files` as objects `{path, sha256_before, sha256_after}`, `assurance_version`, and `previous_entry_sha256` equal to the SHA256 of the canonical JSON of the preceding entry (the first entry uses `null`). Earlier entries may keep their original shape and are the chain root. A gap, a mismatched `previous_entry_sha256`, or an entry dated before the receipt's `DRAFT_MANIFEST.drafted_at` fails with `IDENTITY`. Files present in the workspace but declared by no receipt are ignored. The receipt's `assurance_version` must equal the current version.
3. **Code identity.** Write `CODE_SNAPSHOT.json` containing `schema_version`, `files`, `snapshot_paths`, `runtime` and `dependency_lock_sha256`. Include all owned source/test/tool files and project helpers actually imported by the executed paths, including untracked files. Record the imported-module inventory and statically identified dependencies of unexecuted branches; an import trace alone does not prove the inventory is exhaustive. Bind the existing Python/runtime and lock identities. `code_sha256 = SHA256(canonical_json(CODE_SNAPSHOT document))`. Recompute file hashes; a dirty-patch hash or a current Git commit alone cannot cover untracked implementation. The coordinator checks this inventory against the actual diff/imports. Preserved snapshot copies must match that receipt's own declared hashes. Live workspace bytes of a declared code file verify if they equal the declared hash, or if a later receipt in the same chain — one that lists this receipt among its transitive predecessors and itself verifies under this rule — declares the file with the live hash. Recursion is cycle-safe; a cycle or an unverified successor fails with `IDENTITY`.
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

Canonical source: [SILENT_FAILURES.md](/workspace/planning/research-program/SILENT_FAILURES.md).

## Silent failure checks

Generated from [ASSURANCE_CASES.json](/workspace/planning/research-program/ASSURANCE_CASES.json). These are required prevention cases, not claims that every listed defect was found in current code. Use [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md) for evidence and closure rules.

Reuse a bound shared test/evidence artifact when it proves the same invariant on the same code and inputs. Run task-specific native/behavior cases where scope differs. Do not duplicate a test solely to increase the test count. An inherited check must name its current artifact/hash and applicability; a stale pass cannot be inherited.

This runbook includes only cases assigned to: P15-16A, P15-17, P15-18.

### S01 — Missing, substituted or malformed required artifacts

Assigned tasks: P15-00, P15-01, P15-02, P15-03, P15-04, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A, P15-17, P15-18, P15-19, P15-20, P2-00, P2-01, P2-02, P2-03, P2-04, P2-05, P2-06, P2-07, P2-08, P2-09, P2-10, P2-11, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-23, P2-24.

**Probe:** Remove one required artifact from a valid copied receipt; then substitute a different task’s file with a correct byte hash; separately alter a claimed row count and replace JSON with invalid contents. Keep valid controls.

**Expected:** Each malformed case fails for the affected inventory, identity, schema or row-count reason. All required members and command logs are checked; directory artifacts require a complete file index.

**Evidence:** Actual task CLI results, valid control and isolated mutations with failure codes; use temporary copies.

### S02 — Unimplemented behavior hidden behind green tests

Assigned tasks: P15-00, P15-01, P15-02, P15-03, P15-04, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A, P15-17, P15-18, P15-19, P15-20, P2-00, P2-01, P2-02, P2-03, P2-04, P2-05, P2-06, P2-07, P2-08, P2-09, P2-10, P2-11, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-23, P2-24.

**Probe:** For the central card requirement, identify the actual callable and output field; use independent arithmetic, a frozen baseline or a specified invariant to construct one sensitive check. For a new fix retain before/after; for existing behavior mutate a boundary input.

**Expected:** The check fails when the advertised behavior is absent, reversed or bypassed and passes for the implemented behavior. All Axx keys have resolvable evidence. Test collection and exit 0 alone do not satisfy this.

**Evidence:** EVIDENCE_MATRIX with exact test node IDs, command logs, input/output selectors, expected values and oracle derivation.

### S03 — Self-asserted code, plan and run identities

Assigned tasks: P15-00, P15-01, P15-02, P15-03, P15-04, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A, P15-17, P15-18, P15-19, P15-20, P2-00, P2-01, P2-02, P2-03, P2-04, P2-05, P2-06, P2-07, P2-08, P2-09, P2-10, P2-11, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-23, P2-24.

**Probe:** Recompute the plan/code/draft identities independently from preserved bytes. Mutate each digest separately, omit an owned untracked file, and change a relevant helper/configuration without updating the binding.

**Expected:** False identities are rejected. The file inventory includes actual runtime dependencies and untracked code; historical snapshots retain their authorized plan version.

**Evidence:** PLAN_SNAPSHOT, CODE_SNAPSHOT, draft/frozen manifest and independent recomputation results.

### S06 — Calendar-only coverage and favorable date substitution

Assigned tasks: P15-00, P15-02, P15-03, P15-17, P15-20, P2-00, P2-01, P2-09, P2-24.

**Probe:** Use an open current session with a missing same-contract prior profile; use a complete current slice with incomplete model lookback history; remove the only complete date in a year.

**Expected:** Affected input groups remain partial/missing; unaffected groups keep their own denominators. The deterministic slot becomes missing or the first genuinely complete date by the fixed coverage rule, never by outcomes. Unknown feed completeness remains unknown.

**Evidence:** Per-group coverage rows, native receipt hashes, required lookback intervals, selection replay and partial/roll/holiday/gap fixtures.

### S07 — Synthetic data presented as native evidence

Assigned tasks: P15-00, P15-02, P15-03, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A, P15-17, P15-18, P15-19, P15-20, P2-00, P2-01, P2-03, P2-04, P2-05, P2-06, P2-07, P2-08, P2-09, P2-10, P2-11, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-23, P2-24.

**Probe:** Reopen one actual native artifact and row named in the output lineage and replay the named adapter. Separately include a clearly marked synthetic missing/ambiguous fixture.

**Expected:** Native values, contract and event/availability clocks match the identified source. Synthetic examples are labelled synthetic. A fabricated row ID or unavailable file fails.

**Evidence:** Source path/hash/row, adapter callable, serialized output selector and independently replayed comparison.

### S08 — Future data changes earlier output

Assigned tasks: P15-02, P15-03, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A, P2-01, P2-03, P2-04, P2-05, P2-06, P2-07, P2-08, P2-09, P2-10, P2-11, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-23.

**Probe:** Choose cutoff t; alter all post-t records and all earlier-event records whose availability is after t. Recompute from raw inputs, including the join/preprocessing/fit path. Separately alter a relevant pre-t input on a sensitive fixture.

**Expected:** Earlier features, decisions, predictions and immutable artifacts remain unchanged after the future mutation. The sensitive admissible-input mutation changes its declared output; a constant-output stub cannot pass.

**Evidence:** Before/after input hashes and output fields; cold-cache rerun; boundary equality and as-of join cases.

### S09 — Invented order within one timestamp batch

Assigned tasks: P15-02, P15-03, P15-06, P15-07, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A, P2-01, P2-07, P2-09, P2-11.

**Probe:** Permute conflicting high/low, buy/sell or target/stop events in the same unresolved batch, including row-ID order.

**Expected:** Results preserve the same ambiguity set and batch availability. No row sort creates a favorable ordering, premature confirmation or inferred aggressor.

**Evidence:** Permutation cases and one native ambiguous batch where available, including raw IDs and ambiguity reason.

### S11 — Missing windows silently become zeros

Assigned tasks: P15-02, P15-03, P15-06, P15-17, P15-18, P15-19, P15-20, P2-01, P2-04, P2-05, P2-06, P2-07, P2-08, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-24.

**Probe:** Create three days: complete with no opportunity, incomplete horizon, and an observed event with measured outcome. Also test an absent conditional arrival.

**Expected:** The complete no-opportunity day stays in the denominator with occurrence 0; the incomplete horizon is unknown; conditional reaction/utility is undefined without arrival. Missing outcomes are never imputed to zero, loss or a median.

**Evidence:** Declared/complete/zero/partial/missing day counts, label masks, row IDs and denominator reconciliation.

### S12 — Dropped or duplicated jobs during resume

Assigned tasks: P15-02, P15-17, P15-18, P15-19, P15-20, P2-02, P2-12, P2-23, P2-24.

**Probe:** Register a 2-date by 2-task fixture (four jobs), interrupt after a shard, leave a truncated shard, then resume. Include a valid zero-opportunity job and an explicit unsupported cell.

**Expected:** The same four declared jobs each have exactly one reconciled disposition. Completed validated shards are reused; partial output is never accepted as complete. Counts and semantic outputs match uninterrupted execution at 1 and 4 workers.

**Evidence:** Frozen job inventory, shard hashes, before/resume/fresh comparisons, failed attempts and exclusion reasons.

### S13 — Stale cache or conflicting immutable root

Assigned tasks: P15-00, P15-02, P15-05, P15-17, P15-18, P2-01, P2-02, P2-09, P2-10, P2-12, P2-23.

**Probe:** Change one input byte, contract, schema version, transform version, relevant parameter and cutoff in turn. Exercise cold/warm caches and retry a frozen root with conflicting configuration.

**Expected:** Every semantic change gets an appropriate new identity or explicit rejection; no stale object is reused. Cold/warm results match. Conflicting roots fail; interrupted writes cannot appear as valid completed shards.

**Evidence:** Cache key inventory, mutation results and immutable-write/restart tests; retain timing separately from semantic hashes.

### S15 — Many-to-many joins or feature order silently corrupt rows

Assigned tasks: P15-02, P15-17, P2-01, P2-02, P2-08, P2-09, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20.

**Probe:** Duplicate one right-side key; omit one row; shuffle native row order and predictor columns; collide a timestamp across two assets/contracts/folds.

**Expected:** Declared row identity and join cardinality hold, unmatched rows have explicit masks, and duplicates fail or follow a predeclared deduplication policy. Column names/order/schema are bound in fitted artifacts; reshuffling cannot silently swap meanings.

**Evidence:** Pre/post join counts and key uniqueness, join diagnostics, shuffled-input and serialization/prediction checks.

### S17 — All-history preprocessing or in-sample stacking

Assigned tasks: P15-03, P15-18, P2-01, P2-02, P2-04, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-23.

**Probe:** Put extreme values and altered labels only in validation/future folds. Trace training, tuning, calibration and OOF row IDs for each layer and upstream prediction.

**Expected:** Training preprocessing, selected past configuration and earlier predictions do not change. Fit/calibration/OOF sets obey the contract and no row trains the estimator producing its required OOF prediction.

**Evidence:** Set intersections, fitted preprocessing statistics, upstream artifact/fold IDs and cold rerun perturbation outputs.

### S21 — Source prerequisites disappear in a generic family wrapper

Assigned tasks: P15-04, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20.

**Probe:** Choose a positive source sequence and omit, reverse or mark unknown one source-required stage. Use a case where two required reasons are actually the same underlying evidence.

**Expected:** Original predicates, stage order, branch/context scope and independent-reason constraints remain required except for the explicitly registered replacement axis. Source unknown stays unknown and a generic helper cannot silently collapse distinct branch semantics.

**Evidence:** Source-to-code predicate table, independent-reason/sequence negatives, source/operational verdicts and unchanged-baseline comparison.

### S22 — Changed rules only filter old winners or reset contact state

Assigned tasks: P15-05, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A, P15-17, P15-18.

**Probe:** Construct an opportunity created by new geometry but absent from the baseline qualifying set. Update a developing reference value within one lifecycle; test expiry-only time advancement and rearm just below/at the threshold.

**Expected:** Changed rules enumerate their own eligible formations/contacts. Reference versions preserve lifecycle touch history. Deadlines advance without a trade and rearm uses the frozen predicate; no duplicate opportunity appears from value refresh.

**Evidence:** Baseline/candidate population IDs, boundary transition traces and lifecycle/rearm fixtures.

### S24 — Unregistered trials or outcome-driven selection

Assigned tasks: P15-08, P15-17, P15-18, P15-19, P15-20, P2-23, P2-24.

**Probe:** Compare the frozen candidate/job bank to every executed attempt, including failures, unsupported cells and B0/B1/B2 versions. Alter only held-out outcomes and re-run selection.

**Expected:** No trial is missing, duplicated, renamed away or added outside the finite budget. Selection uses only the allowed training/tuning evidence and retains fold-specific rules. A negative result cannot trigger unregistered search or deletion.

**Evidence:** Set reconciliation of planned/executed/failed/selected IDs, immutable trial ledger, fold selections and exposure history.

### S31 — Provenance or unsupported input silently relabelled

Assigned tasks: P15-00, P15-04, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A, P15-20, P2-00, P2-08, P2-09, P2-21, P2-24.

**Probe:** Round-trip an unknown source_exact field, a source-inspired operational rule, missing proprietary constants, cash-index input limits and personal-execution-only data.

**Expected:** Unknown does not become true or false implicitly; proxies remain labelled. Generic implementation still passes fixtures when native cells are unsupported. Personal risk/process records do not gate market setup definitions.

**Evidence:** Raw/normalized round-trip, source/operator ledger, scope/availability receipts and downstream allowlist with exact limitations.

### S32 — Slice-only or low-support work presented as a full experiment

Assigned tasks: P15-17, P15-18, P15-19, P15-20, P2-02, P2-04, P2-05, P2-06, P2-07, P2-08, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-23, P2-24.

**Probe:** Compare declared full dates, preceding training/tuning/calibration history and registered jobs to actually consumed rows. Restrict output to eight engineering dates and inspect whether fitting was incorrectly restricted too.

**Expected:** A slice limits evaluation/output only; fitting consumes the full declared preceding history. A timeout/resource abort remains incomplete and resumes. Complete low-support/negative results require correctly implemented and executed finite work, with no empirical winner needed.

**Evidence:** Train/tune/calibration/output date ranges and row counts, job inventory, resource logs, exact unresolved work and full-run reconciliation.

Canonical source: [ROADMAP.md](/workspace/planning/ROADMAP.md).

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

[Retention rules](/workspace/planning/research-program/RETENTION.md) add bookkeeping and bounded revisits; they change no formula, budget, gate or date of the existing banks.

1. **Nothing is discarded.** Every registry branch stays in the retention set through Phase 4 with a status: `active_selected`, `active_baseline` or `inactive_retained`. Every attempted candidate keeps its full population definition, parameters and diagnostics in the trial ledger. "Inactive" means not consumed by the next phase's training by default; it never means deleted.
2. **Failure attribution.** Every deselected, inconclusive or not-promoted candidate records `failure_attribution` on its TrialRecord: an ordered list drawn from `frequency` (entries below the frequency floor), `location_miss` (objective not reached while price came within 0.25 S of it, or adverse excursion beyond 0.5 S before any favorable 0.5 S), `confirmation_delay` (missed-move share above the family median), `adverse_before_target` (stop-first share above the family baseline), `cost_sensitivity` (sign reversal under the stress setting), `support` (below the support gate), `coverage` (unexplained input coverage loss). Each is computed from the diagnostics the Strategy Book already reports, with the thresholds fixed before any candidate result is read.
3. **Bounded revisits.** Phase 3 re-screens every retained candidate whose first attribution is `location_miss`, using its improved locations. Phase 4 re-screens every retained candidate whose first attribution is `confirmation_delay` or `adverse_before_target`, using the response and entry experts. A revisit is one registered pass over the retained set with the same folds, scores and promotion gates; it is not a new open search and adds no neighbors.
4. **Phase 2 is split.** Strategy-agnostic context experts (joint volatility, remaining range and passage time, auction and day state, options flow and exposure, intraday OI, cross-market coupling) are fitted once in Phase 2 and are final inputs to Phases 3 and 4. Method-specific suitability experts and conditional plans fitted in Phase 2 are provisional: they are fitted on B0 or the selected rule with baseline locations, and they must be refit in Phase 4 on the final rule-plus-location combination before any decision integration. Phase 2 produces dispositions for strategies, never discards.
5. **Every release reports the retention set** with statuses and first attributions, so a reader knows what is inactive, why, and which later phase will revisit it.

### Reading and starting

Start at the selected phase README, then use its `PROMPTS.md`. Each subphase has a generated `RUNBOOK.md` containing the applicable contracts and its task cards. The coordinator reads one runbook; a worker receives one task card plus the named contract sections. Bundles are generated from canonical files, never independently edited.

[Shared contracts](/workspace/planning/research-program/README.md) · [Execution method](/workspace/planning/research-program/WORKFLOW.md) · [Conversation scope audit](/workspace/planning/research-program/SCOPE_AUDIT.md) · [Workflow repository review](/workspace/planning/research-program/METHOD_REVIEW.md) · [Decision ledger](/workspace/planning/phase-1-live/NEXT_PHASES_DISCUSSION.md) · [Shared wiki](/workspace/wiki/index.md).

Phase 1 source definitions and archived evidence remain read-only. New code belongs to the namespaces named in the task cards. New reports get new immutable run directories. Do not patch an accepted report, source file or old scanner merely to make a comparison look better.

Canonical source: [WORKFLOW.md](/workspace/planning/research-program/WORKFLOW.md).

## Execution and handoff contract

Read this as an implementation work order when the user starts a pack. The current artifact is a plan. A task is complete only when its declared behavior is implemented and verified, or its explicit data/identifiability gate returns an evidenced terminal disposition. Merely writing a report, passing toy tests or finding no profitable variant does not prove implementation completeness.

All 46 tasks and all 17 subphases also obey [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md) and their assigned [silent failure checks](/workspace/planning/research-program/SILENT_FAILURES.md). This is acceptance amendment `research-assurance-2026-09-14-v3`, recorded in [AMENDMENTS.json](/workspace/planning/research-program/AMENDMENTS.json). The original `00-foundation` completion failed independent review; use [the repair work order](/workspace/planning/research-program/FOUNDATION_REPAIR.md) before `01-native-and-outcomes`. Existing Phase 1 acceptance remains under its original protocol. The casebook adds specific software checks; it does not enlarge the research search space.

The task graph/cards describe the frozen specification and retain their authoring status. Track actual execution progress in verified receipts and the shared wiki; do not alter a frozen task's content/check boxes merely to record completion and thereby change its plan identity. A real specification amendment gets a new version and exposure record.

The user's Grok build includes pstack. Enter through the generated `/poteto-mode new task` prompts and follow [PSTACK_EXECUTION](/workspace/planning/research-program/PSTACK_EXECUTION.md) for installed-playbook routing, Grok-only role overrides, bounded worker briefs, decision trails and host-capability adaptations. The router chooses supporting skills. The task cards remain the authority for formulas, finite experiments and completion.

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
    assurance_version: str          # "research-assurance-2026-09-14-v3"
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

Canonical source: [SPEC.md](/workspace/planning/phase-1-5/SPEC.md).

## Phase 1.5 implementation specification

Implement a finite, auditable comparison of individual setup rules. Preserve the accepted Phase 1 baseline, label every departure and return either a supported upgrade, a retained baseline, or an explicit inconclusive/unsupported result for every family. Do not start Phase 2 models, a final entry integrator or a P-zone location optimizer here.

### Existing code to reuse

All existing paths in this table are under `/workspace/implementation/src/trading_research/research/method_pack/`. They were inspected while writing this pack. New signatures below are proposed, not existing APIs.

| Existing module/symbol | Use |
| --- | --- |
| `historical_features.HistoricalFeatures`; `bars`, `range`, `profile`, `vwap`, `prior`, `local`, `coverage`, `at` | Same-contract native market access and completed-window features. |
| `native_discovery.scan_branch(market, row)` | Authoritative frozen branch/scanner dispatch, including extra units and manifest binding. Prefer this to recreating the dispatch table. |
| `event_time.build_event_window`, `EventWindow`; `event_cache.cached_window`, `prepare_date` | Reuse versioned native transforms and cached event-time views. |
| `mbp1_views.plan_window`, `iter_mbp1_window`, `trade_view`, `bbo_view` | Native identities, executions and quote adapters. |
| `historical_price_scanners.scan_jumbo`, `scan_green_failure`, `scan_green_refinement`, `scan_green_vwap` | Immutable source-reconstruction baseline functions. |
| `historical_auction_scanners.scan_saint`, `scan_member`, `scan_keani`, `primary_balance` | Immutable auction-method baselines. |
| `historical_flow.batches`, `exact_contact`, `local_observations`, `flow_stages`, `scan_sires`, `scan_microbalance` | Native batch rules, local flow and source sequence baselines. |
| `historical_process_scanners.scan_refill`, `scan_scalp`, `scan_jetbundle`, `scan_stoic_data`, `scan_risk` | Research/scalp/process scope; risk is not a market-entry scanner. |
| `historical_assembly.HistoricalEpisode`, `window_result` | Read source verdict, inferred-strategy verdict, stages, geometry and omission fields without collapsing them. |
| `measurement_outcomes.interval_extrema`, `rounded_coverage`, `boundary_order` | Independent coverage/extrema conventions; preserve old output schema. |
| `strategy_pzones.inferred_pzones`; `strategy_options.gamma_at`, `key_gamma_reference`; `strategy_context.inferred_auction`, `inferred_macro` | Existing disclosed inferred inputs remain baselines. Do not relabel them source-exact. |

New code root: `implementation/src/trading_research/research/rule_discovery/`. Shared schemas, time-safe labels and execution benchmark go in `research/contracts/`. New tests mirror those namespaces under `implementation/tests/`. Accepted Phase 1 files stay unchanged; if an adapter discovers a baseline bug, write a separate discrepancy report and preserve the accepted version for comparison. A necessary new baseline repair is a separately versioned rule and exposure amendment, never a silent mutation.

#### Baseline adapter details that must not be guessed

`HistoricalFeatures` enables reconstructed strategy semantics from `records['strategy_reconstruction']` **during construction**; this selects `ReconstructionSessionPolicy` and `StrategyWindow`. Build the records mapping from the bound registry's supplied records plus its `registry_sha256` and `strategy_reconstruction` fields, matching `historical_runner._records`. Do not set `market.reconstruct=True` afterward: that would leave the wrong window/calendar object. Dispatch each frozen coverage row through `native_discovery.scan_branch`, which checks the scanner module/function identity against the manifest.

The default Phase 1 `HistoricalFeatures` window ends at 16:00 ET. Preserve that exact window for baseline parity. The new `MarketView` separately covers the full matching account day through 17:00/verified early close for Phase 1.5 labels/benchmarks and Phase 2 snapshots. Build those explicit native windows with `build_event_window`/`cached_window` and split at contract/closure boundaries. Do not extend the old market object and inadvertently change baseline scanner populations. New outcome horizons can use the separate full-account-day view; keep old Phase 1 outcome records unchanged and label the new measurement policy.

The old `historical_runner.software_identity` hashes **all** tests and tools, so new task tests/tools necessarily change that whole-tree identity. Do not bypass its checks or write new jobs into a frozen Phase 1 run root. The new baseline binding verifies every accepted baseline file hash and runtime listed in the frozen manifest, then the new runner records its own current code/test identity in a new root. Direct baseline scanner parity uses the bound original inputs/configuration; release verification distinguishes preserved baseline files from added code. Historical wiki/documentation identities use their frozen snapshots, not the newly edited shared wiki.

The accepted runtime's `measurement_runner.configure_runtime` only installs the tested stable-file digest cache and bounds Arrow worker counts; the new runner may reuse that startup behavior with parity evidence. Do not monkeypatch scanner logic, thresholds or market observations to implement a variant.

### Pipeline and proposed interfaces

```python
class MarketView(Protocol):
    def executions(self, start_ns: int, end_ns: int) -> Iterable[NativeBatch]: ...
    def quotes(self, start_ns: int, end_ns: int) -> Iterable[QuoteBatch]: ...
    def coverage(self, start_ns: int, end_ns: int) -> CoverageReceipt: ...
    def completed_bars(self, start_ns: int, end_ns: int, seconds: int) -> tuple[Bar, ...]: ...

def scan_baseline(market: HistoricalFeatures, family: str, branch: str) -> BaselineResult: ...
def build_formations(market: MarketView, spec: RuleSpec, cutoff_ns: int) -> tuple[Formation, ...]: ...
def build_references(market: MarketView, formation: Formation, spec: RuleSpec) -> tuple[Reference, ...]: ...
def enumerate_contacts(market: MarketView, reference: Reference, expiry_ns: int) -> Iterable[Contact]: ...
def resolve_source_context(market: HistoricalFeatures, family: str, branch: str,
                           reference: Reference, at_ns: int) -> ContextEvidence: ...
def advance_sequence(state: SequenceState, batch: NativeBatch | None, spec: SequenceSpec,
                     *, now_ns: int, inputs: SequenceInputs) -> SequenceState: ...
def scan_variant(market: MarketView, source_market: HistoricalFeatures,
                 spec: RuleSpec) -> ScanResult: ...
def compare_rules(baseline: RunManifest, candidates: tuple[RunManifest, ...],
                  split: SplitManifest, evaluation: EvaluationPolicy) -> Comparison: ...
```

`ScanResult` contains opportunities, rejected contacts, unknown-input contacts, formations, expired sequences and coverage omissions. `Formation` contains immutable ID, asset/contract, start/end/available-at, high/low, total volume, profile identity, construction kind and source parents. `Reference` adds lower/upper, issue/expiry, side policy and formation ID. `Contact` contains native batch IDs, contact time/known-at, touch/sweep distinction, pre-touch departure evidence and all possible prices when ordering is ambiguous. `ContextEvidence` retains each source prerequisite as true/false/unknown with its derivation and clock. Never flatten unknown to false before recording coverage.

`SequenceInputs` carries the frozen reference/context, newly completed bars and already available flow/cohort features. Validate every input clock <= now_ns. The driver invokes transitions on native batches, bar-completion clocks and deadline clocks; batch=None advances time/expiry without inventing a trade. Sequence working memory contains only prior batches/partial aggregates, with explicit evidence IDs.

For an unchanged rule, `scan_variant` delegates to the original baseline function and preserves its records. For a changed rule, enumerate its own complete formation/contact population; filtering only old qualifying setups cannot discover new geometry or earlier confirmations. Source adapters provide the unchanged branch context and unchanged stages from the inspected baseline functions and wiki predicates. A changed stage is explicitly replaced by the registered delta and its hypothesis ID; all other source prerequisites stay required. No monkeypatching globals, optimistic fallback to a different branch or recursive copying of whole scanner files per variant.

At most one opportunity per distinct contact/side/rule. A contact is rearmed only after complete native prices depart by `max(4 ticks, .1*S_at_first_contact)` beyond the reference on the approach side and remain outside for a complete 60-second bar. A new reference formation is a new population. Mirror long/short inequalities exactly; both sides in one ambiguous native batch remain ambiguous.

A numerical update to a developing reference is a new immutable version within the same `reference_lifecycle_id`, not a new independent contact population. Group contact/rearm state by `(rule_id, reference_lifecycle_id, side)`; record the exact version used at contact. The lifecycle ID hashes family, branch, native contract, formation ID and reference kind, excluding the later value/version clock. A newly formed independent area creates a new lifecycle. This prevents every VWAP/profile update from resetting touch history and manufacturing opportunities.

### Numerical reconstruction work

`P15-04` produces a source-to-operator ledger for EV/expected move, P-zone, KG1/gamma, auction-state/macro and every missing numerical operand from the completed registry. Each row names the wiki object, raw source anchor, existing implementation, exact formula if printed, availability, source-exact status and downstream dependency. Recover printed formulas and unit mistakes before searching improvements.

EV has three distinct quantities: printed source expected-value/range object; conventional IV-implied horizon move; our forecast of future realized movement. For a source that explicitly supplies annualized sigma and calendar horizon T years, conventional one-standard-deviation log approximation is `move_points=spot*sigma*sqrt(T)`, labelled model-derived; T uses actual seconds/(365*86400). It is not a proprietary EV reconstruction unless the source states that formula. Example spot100,sigma.2,T=.25 gives10 points. Source bands with unpublished probabilities/conditioning stay unknown. P-zone anchors and quantiles remain the existing disclosed baseline through Phase 1.5; improving their actionable locations belongs to Phase 3. Learned intraday volatility forecasts belong to Phase 2.

The source matching budget is one ledger pass plus at most two deterministic checks per printed formula/figure with sufficient dated inputs. If the source does not supply inputs/constants, stop with `not_identifiable_from_owned_source`; implement a labelled research alternative only if it is already in this search bank. Do not ask the user to decode proprietary values or optimize a substitute to match a screenshot.

### Primitives with exact causal definitions

Time formations retain source intervals as B0. Alternative F1 is the preceding 60 matching minutes ending at a registered source issue clock. F2 is volume-completed: at each source issue clock, walk backward over complete one-minute bars until cumulative executed volume reaches the median volume of the corresponding source formation over the prior 20 complete same-contract sessions, at most 180 matching minutes; include the whole final minute and record overshoot. F3 is detected balance: inspect trailing lengths15,30,60 minutes in that order at each source issue clock, choose the first complete window with `width <= .75*S_before_window` and efficiency `abs(C-O)/max(H-L,q) <= .35`; if none, no formation. `S_before_window` uses the prior 60 matching minutes ending before formation starts. Freeze selected geometry at its availability clock; never resize it using the subsequent breakout.

Trade-volume profile: aggregate executed size into integer tick bins. Smooth with triangular kernel `w_j=max(0,b+1-|j|)` for j=-b..b normalized to sum1, using bandwidth b=0 or 2. No Gaussian fit is required. POC is highest smoothed volume, ties closest to volume-weighted mean price, then lower tick. Build 70% value area contiguously from POC by adding the larger adjacent bin, ties lower first, until cumulative **raw** included volume reaches70% of total; use smoothed values for neighbor ranking only and disclose this alternative to the source profile. HVN is a local maximum over +/-2 bins with prominence `(peak-max(left_min,right_min))/max(peak,1) >= .20`, minima taken within 8 bins. Group equal plateaus into one node at their volume-weighted tick rounded to the nearest tick, ties lower. Node band spans adjacent bins with volume >=50% of that peak until a valley or 8 bins. Reject overlap duplicates by retaining higher prominence, then volume, then lower price. LVN uses the symmetric local-minimum criterion with neighboring peaks and the same registered neighborhood. All inputs precede reference issue.

VWAP is `sum(price*executed_size)/sum(executed_size)`. Its volume-weighted price dispersion is `sqrt(sum(v*(p-VWAP)^2)/sum(v))`; it is not forecast volatility or an unweighted standard error. Reference bands use VWAP±1 dispersion for the representative bank. Reset anchors are source anchor B0 or account-day open R1; a source-imperative anchor may change only in a separately labelled custom variant. Greek-weighted centroids are not called VWAP. Prior highs/lows use completed verified same-contract session/week/month windows as the baseline does; choose no future pivot or back-adjusted cross-roll value.

R1 computes its account-day VWAP/dispersion from the account-day anchor through the registered source issue time and freezes that band until the registered expiry. It is explicitly a frozen reference snapshot; do not silently reissue it every minute. Source developing-VWAP behavior remains its own baseline. Developing-profile alternatives that the source stage requires retain immutable value versions and the shared lifecycle/rearm rule above.

### CVD and cohort memory

For batch b, `D_b=sum(q_i*s_i)` over known aggressor signs s=+1 buy,-1 sell; `V_b=sum(q_i)` over all executions; `U_b=sum(q_i*1[sign unknown])`. Unknown volume remains separate. C0 is source/raw session-reset CVD `sum D_b`; C1 normalized delta=`sum D_b/max(sum(V_b-U_b),1)` over trailing 5 matching minutes; C2 exponentially decayed delta `Z_t=exp(-ln2*dt/300s)*Z_prev+D_t`, normalized by similarly decayed known volume; C3 price-level delta z-score: current 5-minute delta minus prior 20-session same-time-bucket median, divided by `max(1,1.4826*MAD)` from those past sessions. If required histories or >20% aggressor volume is unknown, C1–C3 are unavailable. Raw price/volume remain usable where independently known.

Fixture batches signed sizes +10,-4,unknown6: known delta6, total20, unknown6, raw CVD6, known-volume delta ratio6/14. Because unknown share=.30, the ratio is numerically observable but fails the .20 admission gate; retain both value and support flag. Never silently classify unknown6 as selling.

Cohort markout at resolved horizon h=30,120,300 seconds: `M_h=sum(q_i*s_i*(mid_(i+h)-trade_price_i))/sum(q_i)` for known-sign trades whose full horizon and future midpoint are available by the snapshot. Bid/ask midpoint is not a fill. Store buy and sell cohorts separately, median markout, positive fraction, volume and unresolved cohort count. “Rewarded buyers” means positive buy markouts, not high CVD alone. A current unresolved cohort cannot borrow later markouts. For Refilling memory also retain distinct touch count, time since formation/last contact, pre-touch departure, signed volume at the band and previous resolved contact reactions.

### Response state machines

All response alternatives start after a causally issued reference and an admissible distinct contact. Source confirmation B0 remains exact to its disclosed reconstruction. S1 is price reclaim: after a strict edge sweep by >=1 tick, first complete 60-second bar closes back inside; decision is that close's known-at. S2 is reclaim+defended retest: after S1, first later contact within 1 tick of the reclaimed edge, followed by a complete 60-second bar closing at least 2 ticks in the favorable direction without an intervening complete close beyond the swept extreme. S3 is flow-supported reclaim: S1 plus C1 signed in trade direction >.20 and at least one resolved prior 120-second cohort with mean signed favorable markout >0; all cohort resolutions must be known by the S1 decision. S4 is failure-to-progress: within 120 seconds after contact, known opposing aggressive volume exceeds its prior 20-session same-bucket .75 quantile, adverse extension is <=max(2 ticks,.1S), then a complete 60-second favorable close exceeds contact batch favorable extreme by1 tick. Unknown aggression cannot qualify S3/S4.

Sequence states: `issued -> contacted -> swept -> reclaimed -> retested -> confirmed`, with explicit optional stages selected by the recipe. `expired`, `invalidated`, `input_unknown` are terminal for that contact. Default deadline is10 minutes from contact, bounded by source expiry. S4 follows `contacted -> pressure_observed -> stalled -> confirmed`. Store stage times, dependencies and rejected alternatives. No event may satisfy two ordered stages in the same ambiguous batch. Absorption, continuation, stop-run, failure, imbalance and microbalance remain distinct source mechanisms; S1–S4 are representative alternatives, not a universal absorption classifier.

### Completion boundary

The final pack contains the entire baseline registry, all attempted candidates and deltas, construction/coverage evidence, nested selected-rule manifests, rule-level and daily diagnostics, unchanged-entry exit comparisons, and a Phase 2 dependency allowlist. Every source family and every search mechanism has a disposition. Negative results close a correctly executed experiment; missing code does not. All important active definitions and evidence pointers are added to the shared wiki.

Canonical source: [SOURCE_ADDITIONS_2026-09-14.md](/workspace/planning/phase-1-5/SOURCE_ADDITIONS_2026-09-14.md).

## Source additions from greenbirdtrader posts dated 2026-09-14

Raw capture: `/workspace/sources/x-raw-2026-09-14/greenbirdtrader/` (two posts, seven photos, full text). These are dated source examples with printed entries, stops and objectives. They add branches to the accepted Green Bird families and widen one scan window; they change no existing branch. Each addition is a versioned baseline branch with an exposure record dated 2026-09-14, implemented by the family adapters in subphase 04, given its own full-history population, and reported in the Strategy Book beside the accepted branches.

### What the accepted implementation covers and what it does not

`scan_green_failure` builds references for `nyam_box`, `previous_hour`, `asia_tdo_case`, `cash_open_reclaim_case` and the `prior_day/week/month_level` branches, and scans every one of them from `max(09:30, reference known-at)` to the account-day end. There is no London-box reference in the failure scanner (London appears only in the VWAP continuation scanner), the Asia box exists only with the midnight true-day-open confluence forced on, and `pocket_required` is false throughout, so the golden pocket is never evaluated as an entry condition. The GB-SCALP page records the continuation trigger as unpublished.

### GB-FAIL additions, owner P15-10

**A1 `london_box`.** Reference: the finished London box, operational 02:00 to 05:00 ET under A2-GB-CLOCK (the source names the London low and high, never the bounds). Sweep of the London low (long) or high (short) at any time after the box completes, including before 09:30. Confirmation: a complete five-minute close back through the level. Mandatory retest (the post states reclaim, retest, higher low, then the post-open close; corrected 2026-09-15 after the source-fidelity review): after the confirming close, a later contact with a higher low (long) or lower high (short) relative to the sweep extreme, then a further five-minute close through the level; the post's entry is that later close after the New York open. Objectives as named: the midnight true-day open first, then the opposite London edge. Structural stop beyond the sweep extreme. Source, post 2099513366326730859: "London low gets swept before the NY open. We reclaim it, retest it and form a higher low. After the open, price closes back above the London low. That's my entry. Midnight open first. London high next. 100 points long."

**A2 `asia_box`.** The Asia box (20:00 to 00:00) failure without the true-day-open confluence that `asia_tdo_case` requires: sweep of the Asia high and a five-minute close back below it gives a short, mirrored for a long; objective the opposite liquidity as named. Source, same post: "Price pushes higher, sweeps the Asia high and fails to hold above it. There's my failed breakout. I switch sides. Another 100 points short."

**A3 overnight scan window.** For `prior_day_level`, `prior_week_level`, `prior_month_level`, `asia_tdo_case`, `asia_box` and `london_box`, scan from the reference's known-at time through the account-day end instead of from 09:30. The accepted 09:30-start population stays the accepted baseline; the widened window is the addition and is reported separately so the overnight population is visible on its own. Source, post 2099503614372741234: "Overnight, the sweep below the previous day's low and reclaim gave me the first long."

### GB-SCALP addition, owner P15-11

**A4 `golden_pocket_continuation`.** After a defined impulse, a measured range with known start and end (on 2026-09-11 the range created by the 08:30 CPI move), a New York session pullback into the golden pocket of that impulse drawn in the leg's own direction, for an up-leg `[H - 0.618(H-L), H - 0.50(H-L)]` and for a down-leg `[L + 0.50(H-L), L + 0.618(H-L)]` (corrected 2026-09-15: the earlier text transported the down-leg convention into the long), in the impulse direction. Entry on the first complete five-minute close back out of the pocket in the impulse direction; this trigger bar is an operational choice, because the post says "hit the continuation long" without naming the bar, and it stays labelled operational. Stop beyond the far edge of the pocket. Objective the impulse extreme or the prior-day extreme as named. Source, post 2099503614372741234 and its charts: "Bullish context. Defined range. Pullback into my area." with a 35-point stop below the pocket and sell limits at the prior-day high. This supplies the trigger the GB-SCALP page records as unpublished; the directional-context and small-size clauses of that page still apply.

### Search-bank note

The "retest and form a higher low" condition in A1 is the S2 defended-retest alternative applied to a source branch. Record it as source-stated for the London branch, not as a universal rule for other branches.

### Printed fixtures

MNQU2026, 2026-09-14: long entry 28,903.75, drawn target 29,037.00 (the author states about 100 points; a plotted target is not a proven realized exit, corrected 2026-09-15); short entry 29,081.50, stop 29,098.75, target 28,890.50. MNQU2026, 2026-09-11: golden-pocket long entry 29,382.00, stop 29,347.00, targets 29,494.50 and 29,521.75. Replaying these as conformance fixtures needs native data after 2026-09-03, which is not owned at this snapshot; until it is, they are recorded examples, not replay checks.

### Wiki work at the next writer window

Add both posts to `wiki/source-catalog.md`; add the examples and the four additions to `wiki/method-green-bird-failure.md` and `wiki/method-green-bird-directional-scalps.md` with the raw anchors; add a dated `wiki/log.md` entry. Add A1 to A4 to the acceptance checklists of P15-10 and P15-11, rebuild the bundles, and record the change in AMENDMENTS.json.

### Clock caveat for every source-stated time

The chart footers in these posts read "UTC-4", so the times on them are New York daylight time, which our clocks reproduce. But an author who writes "02:00 to 05:00" or "20:00 to 00:00" in text may mean a fixed offset all year, a platform default, or a different zone, and our implementation converts every stated clock as New York time with daylight-saving handling. For a source that does not, every winter session window shifts by one hour. The reconstruction ledger records, per source, the zone each stated clock is expressed in and the evidence for it (chart footers across summer and winter posts, or an explicit statement), and lists the branches whose windows would move if the zone were a fixed offset. Until a source's zone is established, its clock-based branches carry the label `clock_zone_unverified`.

Canonical source: [PERFORMANCE.md](/workspace/planning/research-program/PERFORMANCE.md).

## Engine performance and parity contract

Applies to all new Phase 1.5 and Phase 2 engine code under `implementation/src/trading_research/research/rule_discovery/`, `research/contracts/` and `research/experts/`, and to any separately versioned runtime that re-executes accepted `method_pack` scanners. Accepted Phase 1 code, the frozen run `run-1.0.1` and the warm event cache under `/workspace/data/derived/phase1-event-time-v2` are unchanged inputs. This contract adds engineering acceptance; it changes no research formula, budget or gate.

### Measured baseline, 2026-09-14 profile of run-1.0.1

Per-job durations were never stored; these are mtime proxies at one-second resolution plus one in-process cProfile of session 2024-03-05.

| Measure | Value |
| --- | --- |
| Job phase wall clock | 5.72 h for 1,742 dates × 57 branches |
| Branch CPU time, summed | 79.6 h; median 1 s, p90 6 s, p99 31 s, max 434 s per branch-day |
| Concurrency | 48 workers on 17.85 effective cgroup CPUs; achieved 13.9× (78%) |
| Per-worker startup | 10–17 s (142 parquet footers, registry and software-tree hashing) × 1,742 = 5–8 CPU-h |
| JETBUNDLE:B | 13.9 CPU-h (17.5% of total); 43.5 s of 59.6 s per session is `deepcopy` of 213k event dicts plus re-serialising them for `content_hash` |
| SIRES:vwap_deviation_fade | 17.9 s per session; 10.0 s is `EventWindow.coverage` rescanning minutes (393 calls), 4.1 s is per-row MBP-1 dict decode |
| Market load | 10.5 s per session before any scanner runs |
| Output layout | 315,655 content-addressed files in one flat `domain/` directory |

Conclusion: the census is dominated by redundant copying, hashing, per-minute rescans and per-row dict decoding, then by oversubscription. Numeric loops are second-order. A Numba or Cython port of scanner arithmetic alone would not fix it.

### Why it matters now

Breadth search runs up to 160 candidates on their eligible branches over all 1,742 sessions. At Phase 1 efficiency (79.6 CPU-h / 57 branches ≈ 1.4 CPU-h per branch-census) with about three eligible branches per candidate, breadth costs roughly 670 CPU-h ≈ 38 h wall on 17 workers, above the 24-hour stage budget in WORKFLOW.md. The new engine must be at least 3× more efficient per branch-session, measured, before P15-17 is dispatched.

### Required properties of new engine code

1. **Columnar session data plane.** Decode each MBP-1 window once into NumPy arrays: `t_ns int64`, `price_ticks int64` (price/0.25 exactly), `size int64`, `side int8`, `action int8`, `bid_ticks`, `ask_ticks`, `bid_sz`, `ask_sz`, `flags`, plus `row_id` preserving `f"{source_file}:{source_row}"`. Every primitive consumes arrays. `Decimal` appears only at serialization, constructed from integer ticks, never from floats. The out-of-order timestamp check and the equal-timestamp batch boundaries are computed once as index arrays.
2. **Per-minute state tables once per window.** Bar-present, observed-complete, known-at, schedule state and unowned-interval overlap are arrays over the window's minutes. `coverage(start, end)` is a slice plus `np.bincount`; `unknown_intervals` is a run over a boolean mask. Session policy state is memoized per minute bucket. No per-minute `datetime` construction inside hot paths.
3. **Prefix sums and reduceat.** VWAP, dispersion, CVD variants and cohort aggregates use cumulative sums of `p·v`, `v`, `p²·v` and signed `q` with `searchsorted` window bounds. Bars use `np.add.reduceat` / `np.maximum.reduceat` on boundary indices. Profiles use `np.bincount` over tick bins and `np.convolve` for the triangular kernel. First passage scans batch-grouped arrays and checks target/stop crossings per batch for ambiguity.
4. **State machines on the contact subset only.** S1–S4 and book-observation machines run in Numba `@njit` over arrays, or in plain Python over the small subset of batches after a contact. Never per-event Python over a full session.
5. **No copying or re-hashing of inputs.** Producers read event arrays without `deepcopy`. Content hashes and canonical manifests are computed once per object identity and memoized per process. Bytes fed to any existing hash function are unchanged.
6. **Process hygiene.** Worker count defaults to `floor(cpu.cfs_quota_us / cpu.cfs_period_us)` when a cgroup quota exists, else `os.cpu_count()`, never a hard-coded 48. A pool initializer loads the registry, ownership manifest and calendars once per process. Unit of work is one session date. Content-addressed outputs are sharded by the first two hex characters of the hash. Per-job wall seconds and peak RSS are written into every job record and receipt.
7. **Cache identity is frozen.** `event_time.py`, `event_cache.py`, `mbp1_views.py`, `adapters.py`, `native_resolution.py`, `empirical_tape.py` and `objects/profiles.py` define the event-cache transform identity. Phase 1.5 engine work does not edit them. New views are new modules with their own versioned identity that read the parquet and the warm cache.

### Parity protocol

- **Baseline delegation parity.** For a stratified sample of at least 40 dates (eight per year 2020–2025 plus 2026, including both DST transitions, an early close, a roll week and the partial 2026-09-03), replay whole dates in manifest order 0..57 through the new runtime and compare each `jobs/evaluation/<date>/<branch>.json.gz` byte-for-byte with `run-1.0.1`. Byte inequality is a failure; a differing `input_receipts` list caused by branch order is a harness bug, not an accepted difference.
- **Primitive parity.** Every vectorized primitive has a plain-Python reference in tests built from the specification's literal fixtures plus randomized arrays with ambiguous batches, gaps and unknown aggressors. Integer and Decimal outputs must be exactly equal; float outputs within 1e-12 relative. Tests fail if the reference is removed.
- **Write guard.** Tests and parity harnesses monkeypatch `event_cache.build_event_window` to raise, so a cache miss can never write under `/workspace/data`. Nothing writes into `run-1.0.1`.

### Throughput acceptance

- Before P15-17 runs, measure the new engine on 20 sessions: full account-day view plus all applicable bank primitives for one candidate-branch, single core. Record median and p90 seconds per session per candidate-branch.
- Project breadth cost as `candidates × eligible branches × 1,742 × p90 seconds / (workers × 3600)`. The runner refuses to start a stage whose projection exceeds the 24-hour budget and prints the projection; it does not reduce coverage or dates.
- Target: at most 5 s per session per candidate-branch at p90 on one core, at least 3× the Phase 1 branch-session average. Report measured values; a miss is an engineering finding to fix, never a reason to shrink the bank.

Canonical source: [DISPOSITION.md](/workspace/planning/research-program/reviews/phase1-code-review-2026-09-14/DISPOSITION.md).

## Disposition of the 2026-09-14 Phase 1 code review

Orchestrator ruling on [FINDINGS.md](/workspace/planning/research-program/reviews/phase1-code-review-2026-09-14/FINDINGS.md) (seven proven defects with reproductions in this directory, thirteen unproven suspicions). The reviewer's verdict is accepted: the causal spine is sound and no post-decision read was found; the defects are boundary and bookkeeping errors, three of which move measured pass, fail and unknown counts or the population denominator.

### Rulings

1. The accepted run `run-1.0.1` and the frozen `method_pack` code stay unchanged. They remain **B0** and the byte-identical parity target for P15-02's baseline delegation.
2. A corrected baseline **B0.1** is registered as a separately versioned rule and exposure amendment, as SPEC.md requires for a discovered baseline bug. Phase 1.5 comparisons in P15-17 and P15-18 pair every candidate against B0.1. The B0 to B0.1 difference is reported per branch as its own "baseline repair" row in the Strategy Book and is never folded into a candidate's delta.
3. Where each fix lives:
   - **P2** zero-length coverage certified complete: the new MarketView coverage in P15-02 returns unknown for a zero-length or unobservable interval, never complete. Fixture required at the 01 hardening pass.
   - **P3** population completeness measured from 09:30: P15-02 and P15-03 measure it from the earliest reference-formation clock the branch consumes, per the registry's required input groups. Fixture at 01 hardening.
   - **P5** missing tail span and **P7** mixed endpoint conventions: P15-03 first passage and extrema use one convention, the contract's `(t, t+h]`, with the tail span included. Fixture at 01 hardening.
   - **P1** effort window compared with the previous non-empty chunk: the Sires adapter P15-12, and Member P15-14 and Keani P15-15 where they share the flow stages, compare with the immediately preceding equal-duration window, an empty window counting as zero effort and recorded. B0.1 rule ID; fixture from `f7_previous_chunk_skips_empty.py`.
   - **P4** empty sweep path raising: the Green Bird failure adapter P15-10 records an availability omission instead. Fixture from `f4_green_failure_empty_path.py`.
   - **P6** pivot-less references collapsing: the Sires key-gamma adapter P15-12 keys dedup on the reference lifecycle ID. Fixture from `f3_kg1_reference_collapse.py`.
4. The thirteen unproven suspicions are assigned for adjudication with fixtures, each becoming a ledger row that is either confirmed (a B0.1 fixture) or refuted (a test proving the current behavior): `expressions.py` items to P15-07; balance-adoption and vacuous `all()` items to P15-13 and P15-12; `price_origin` fallback and the `known_at=None` guard to P15-03; `delta()` unknown handling to P15-06; the value-area walk on sparse rows to P15-05; late-`known_at` bar drops without omission to P15-02.
5. Required before subphase 02: a hardening pass on the closed 01 attempts adding the P2, P3, P5 and P7 fixtures to the new modules, with fixes if any fail, producing new immutable attempts and a fresh gate review.
6. At the next status update: a dated `wiki/log.md` entry and a "known baseline discrepancies" note in `wiki/current-status.md` linking this directory.

### Addendum from the rejection audit, 2026-09-14

The independent [rejection audit](/workspace/planning/research-program/reviews/rejection-audit-2026-09-14/REJECTION_AUDIT.md) re-measured 690 failing conjuncts across all 258 reconstruction-sample rejections and 527 across a stratified 196-episode census sample (40 dates, 36 branches), 83% by recomputation rather than reading. Result: 0 of 258 sample rejections are artifacts; 21 of the 1,644-episode census pool (1.3%) are, extrapolating to roughly 800 of 72,387 census rejections, and those become `data_unavailable`, never setups. P1 is inert on this tape (every published 5-second flow window is contiguous); P2 accounts for 30 SAINT-AMT conjunct instances but is decisive in only 4 episodes; P3 touches only `population_complete`.

- **D1**, proven here and previously listed as an unproven suspicion: `historical_price_scanners.py:314` rebinds the GB-VWAP `continuation_context` operand with the retest-absence answer, discarding the `True` computed at line 308. Every GB-VWAP rejection in the census pool is this artifact (reproduction `repro_d1.py`, example 2023-12-08). Ruling: the Green Bird VWAP adapter P15-11 evaluates the breakout-context conjunct and the retest conjunct as separate operands; B0.1 rule ID; fixture from `repro_d1.py`. Until then GB-VWAP's rejection column is treated as unknown, and the Strategy Book marks the branch's B0 population as affected.
- Recorded `failed_conditions` name at least one vacuous reason in 3 to 4% of rejections; verdicts are trustworthy, the failure-reason metadata is not. The new outcome and diagnostics code in P15-03 must not consume `failed_conditions` as ground truth for the rejection funnel; it recomputes conjunct outcomes.

### Addendum from the unknown-label audit, 2026-09-14

The independent [unknown-label audit](/workspace/planning/research-program/reviews/unknown-audit-2026-09-14/UNKNOWN_AUDIT.md) checked all 17,037 distinct unknown minutes and 460 sampled labels against the raw parquet. Zero instances of code failing to read available data. 99.4% of unknown minutes have no rows of any kind (holidays, closure evenings, the archive end); the rest are deliberate rules; about 22,600 branch-session labels concern inputs the project never owned. Net effect: 0.41% of candidates undecided, 2.4% of setups outside the complete-session denominator, no measured price affected.

- **D2**, a rule artifact rather than a defect: monthly file ownership is defined from the first to the last observed row (`adapters.py:2896-2901`), leaving a hairline unowned gap of tens of milliseconds at each of 47 monthly seams that contains no rows in either file; 94 seam minutes and 1,196 entry-setup sessions are flagged limited by nothing else. Ruling: the new engine's ownership logic in P15-02 treats adjacent monthly files as contiguous across a seam whose gap holds no rows, records the rule in the coverage receipt, and adds a two-file test. Frozen code and byte parity are untouched; the new engine's coverage differs by design and is labelled.
- The ownership relaxation that treats a fully enumerated archive interval as complete makes "zero unknown minutes" mean "the archive covers the interval", not "a trade printed every minute". This is correct but must be stated in the Strategy Book's coverage section.

### Addendum from the method-conformance audit, 2026-09-14

The independent [conformance audit](/workspace/planning/research-program/reviews/conformance-audit-2026-09-14/CONFORMANCE_AUDIT.md) built 261 stage rows across all twelve methods (47 exact, 98 operational, 39 inferred, 47 mismatch, 30 missing) and proved five stage mismatches with fixtures. Verdicts accepted: no method is invented; JJ-TBR, GB-FAIL, GB-VWAP, SIRES, SAINT-AMT, KEANI and STOIC-DATA are partially faithful; the rest are faithful with labelled choices.

Rulings, all carried by the corrected baseline B0.1 with the accepted B0 preserved:

- **C1** JJ-TBR `judas_reversal` searches the sweep only inside 09:40 to 09:50; the source places the false breakout before that window. B0.1 searches the outbound sweep from 09:30 to 09:40 and the reversal entry from 09:40 to 09:50. Owner P15-09; fixture f1.
- **C2** four JJ-TBR branches keep an action window to 16:00 although the source says no position interest after 10:00. B0.1 ends the window at 10:00; the 16:00 population stays as B0 and is reported separately. Owner P15-09; fixture f2.
- **C3** every GB-FAIL sweep branch reads only the five-minute candle containing the sweep; the source waits for the five-minute close back through the level. B0.1 takes the first complete five-minute close back through the level at or after the sweep candle, forward to the branch deadline, and records the bar offset. This is the largest family and today's Green Bird posts show the reclaim arriving bars after the sweep. Owner P15-10; fixture f3.
- **C4** KEANI tests a wick into the developing value-area low; the source rejects off the POC or the previous day's value-area high. B0.1 evaluates those two levels and records which one; the developing-VAL variant stays as B0. Owner P15-15; fixture f4.
- **C5** SIRES `microbalance_break` binds the thesis-direction conjunct to the same expression that selected the trigger, so it can never refuse. B0.1 derives the thesis direction from the larger balance (toward its target edge) as a labelled operational rule, with None when it cannot be derived. Owner P15-12; fixture f6.
- **C6** is D1, already ruled.
- **C7**, systemic: 25 predicate operands are bound to Python literals. Ruling distinguishes two kinds. Structural flags that define a branch's scope (`pocket_required=False`, `retracement_entry=False`, `tdo_required`) stay literal and are recorded as `structural_not_required`. Assertions of checks that never ran (`vwap_reset_verified`, `alignment_ok`, `arrival_read_recorded`, side-independent `bias_recorded`, `source_clock_verified`, `source_case_verified`, `exit_window_recorded`, `kg1_retest`, `same_band_retest`, `microbalance_frozen`, the four REFILL record conjuncts, `cycle_and_indicator_rules_recorded`, `real_extreme` true by construction, `profile_allows_trade` that can never refuse) are bound to None in B0.1 with an `unevaluated_operand` note, so a verdict becomes unknown rather than pass until an adapter evaluates the stage. Owners: the family adapters P15-09 to P15-16; the location objects the absorption source requires (naked POC, HVN, LVN, shelf, ledge, prior reaction area, unfinished business, refill zone; O065 to O069, O072, O087, O116) are built by P15-05 and consumed by the adapters.
- **Missing stages** assigned: three-tick replenishment filter to P15-06 and P15-12; TBR quadrant entries, the outbound exit at the reversal window and the `single_purged` add window to P15-09; the golden pocket and entry-on-retracement variant to P15-10 (see also SOURCE_ADDITIONS_2026-09-14.md); the OFM 1R to 3R objective to P15-12; the arrival read to P15-13; the REFILL zone, thesis and label records to P15-16.

**Characterization that the Strategy Book must state, corrected 2026-09-14.** The audit's "skipped, external" rows refer to the author's own artifacts, which the project cannot possess: engine band values, a key-gamma number, gamma maps, hand-applied auction labels, touch grades, ledgers and orders. They fall into three groups. (1) Evaluated with a labelled computed substitute today: P-zones (`strategy_pzones.inferred_pzones` in JJ-TBR `timed_pzone_reversal`), the gamma regime and key-gamma level (`strategy_options` in SIRES `ofm_aggressive` and `kg1_retest`), and the B-A-D-E-W states (`strategy_context.inferred_auction` in JETBUNDLE). Their base rates are complete-rule rates under the inferred substitute, which Phase 2 (options and gamma boards, auction state experts) and Phase 3 (locations) improve. (2) Scheduled builds: the GB-SCALP entry trigger from SOURCE_ADDITIONS_2026-09-14 A4 (P15-11); the refill touch grader as the REFILL memory expert for subsequent-touch occurrence and conditional reaction (Phase 2 METHOD_EXPERTS, P2-20/P2-21 process-context artifacts); jetbundle transition observations computed from our own state sequence (P15-16, P2-06); the Stoic risk ladder as the Phase 4 account-level overlay on our validated process. (3) Personal records excluded from setup qualification by the settled decision: the authors' management, re-entry, case-description, account-stop and selected-order units. Every Strategy Book entry lists each source stage with one status: evaluated, evaluated_with_inferred_substitute, structural_not_required, unevaluated, scheduled_build, or personal_record_excluded. DELIVERABLES.md is amended to require this at the next writer window.

#### C7 refinement, 2026-09-14 evening

Round two of the corrected baseline applied the C7 ruling literally and turned nearly every pass into unknown, which is not what the evidence supports. The 25 literal operands are three kinds, and only one kind is an unevaluated market stage:

- **By construction or provenance, kept True and recorded as `literal_operand_kind: by_construction`:** `exit_window_recorded` (the branch defines its exit window), `source_clock_verified` and `source_case_verified` (provenance of the authored case; the conformance audit is now that verification), `real_extreme` (contacts form only at balance edges by construction), `same_band_retest`, `kg1_retest` and `microbalance_frozen` (the contact is at that reference by construction and the reference is frozen at known-at), the four REFILL record conjuncts (the study's zone definition, instrument and threshold, thesis and post-touch labelling are the registry's own recorded parameters and code), `cycle_and_indicator_rules_recorded` (the macro composite rules are recorded in the inferred implementation), and the restating flags `location_touched`, `ltf_balance_broken`, `actual_band_contact`, `selected_deviation_touched`, `source_zone_known`, `source_session_allowed`, `reduced_expectations`, `expansion_policy`.
- **Operational assumption, kept True and recorded as `literal_operand_kind: operational_assumption` with the assumption ID:** `vwap_reset_verified` (the 18:00 reset declared in A2-GB-CLOCK).
- **Computed presence with an unevaluated direction, kept as computed and recorded as `context_direction_unevaluated`:** `bias_recorded` in GB-FAIL; whether the recorded directional context matches the trade side is a Phase 2 context question, not a baseline gate.
- **Genuinely unevaluated market stages, bound to None so the verdict is unknown until the Saint adapter P15-13 evaluates them with operational rules:** `arrival_read_recorded`, `alignment_ok`, `profile_allows_trade`.

Consequence: SAINT-AMT's corrected baseline is unknown until P15-13; every other family keeps its evaluated population, with the C1 to C5 and D1, P2, P4 corrections applied. The Strategy Book shows the literal-operand kind per stage.

#### Orchestrator review of the corrected baseline, rounds three and four

Two defects found by direct reading and fixed in round four: the Green Bird structural stop used the first sweep candle's extreme even when the reclaim came later, so a deeper excursion before the reclaim put the stop inside the wick (188 of the sampled episodes reclaimed later; 123 stops moved); and the Judas reversal had no entry-window operand, so a confirmation completing before 09:40 entered before the source's reversal window. Round four's result for the second: 31 of 37 Judas reversal episodes on the sample confirm before 09:40. The source sentence, "the actual reversal trade between the 9:40 and 9:50", supports two readings: reject an early confirmation, or wait for the window and enter at its first complete bar if the reclaim still holds. Ruling: B0.1 measures both as labelled variants, `judas_reversal` (strict) and `judas_reversal_deferred` (entry at the first complete bar at or after 09:40 while price remains on the reversal side of the swept edge; the entry price is that bar's close, the stop and objective unchanged), and the Strategy Book shows both beside the accepted B0. The strict reading stays the default comparison point. The entry-window operand is not an M01 catalog field and was recorded on the episode values; the Jumbo adapter P15-09 registers it properly. The strategy status must equal the research verdict for these failures (no_setup 35, not 32); fixed in round five.

#### Orchestrator review of the hardening pass, 2026-09-14 evening

Read directly: the amendment-chain rule (`_plan_superseded_by_amendments`: contiguous before-to-after links, `previous_entry_sha256` over the canonical JSON of the preceding entry, no entry dated before the receipt's draft, chain must end at the live hash), the successor rule (`_code_superseded_by_successor`: the successor must list the receipt as a predecessor with the matching digest, declare the live hash and itself verify, cycle-safe), the columnar decode (`decode_arrow_table`, exact decimal128 ticks) and the two rewritten tests (they drive `daily_benchmark_series` and `build_evaluation_splits`). Accepted. Two minor items for P15-02's successor tasks, batched, not a round: `_ticks_from_decimal_column` floors rather than asserting that every price sits on the 0.25 grid, so an off-grid price would be truncated silently instead of raising; and `row_id` is built by a per-row Python string loop, which should be materialised lazily for retained rows only. The driver's concern that the parity order-recovery segments invocations using the gold file's own receipt-length drops on 2 of 60 dates is accepted as a known limitation of an engineering check; an independent segmentation signal (the frozen run's interrupted-partials records) is preferred if the harness is reused.

#### Verifier limitation recorded after the repair pass, 2026-09-14 night

Re-issuing a task's receipt changes the code pins the older attempt declared, and `_code_superseded_by_successor` accepts only a receipt that lists the old one as a predecessor, so superseded attempts of the same task no longer verify against the live tree (`WORKTREE_SNAPSHOT.supersedes` is written but never read). Ruling: acceptable; superseded attempts are historical and the current chain verifies. Improvement for a later batched verifier pass: treat a same-task successor that names the old attempt in `supersedes` as a valid supersession link, with the same must-itself-verify and cycle-safety rules.

#### Findings from the 02-source-reconstruction closure, 2026-09-14 night

- **F-REFILL-POP (high), owner P15-16.** The refill printed-figure replay over 2024-12-01 to 2025-11-30 found zone touches on only 15 of 260 sessions (824 touches, 123 traded) against the paper's 235 sessions and 41,152 touches. Our refill zone population is about fifty times narrower than the source's, so the hold-rate agreement within five points is not a reproduction and the per-trade R and median-dip disagreements cannot be interpreted. The adapter must re-derive the zone formation and touch rules from refill-effect.pdf pp.5 to 9 (the BigTrades threshold may gate the wrong stage), reconcile the population to the printed order of magnitude (about 175 touches per session), and only then rerun the pre-registered comparison. Until then the REFILL-STUDY book entry carries the label population_scale_unreconciled.
- **Pre-registration rule for every printed-figure replay from here on:** the tolerance file is committed to git before the replay runs, and the receipt cites that commit hash; a self-asserted boolean is not evidence of ordering.
- **Strategy Book link defect (medium), owner P15-20 and the next book edition:** every branch lists all 48 ledger rows as its ledger links; section 1 requires the rows for the operands the branch actually reads.
- Minor: ledger row L004b's quote carries a trailing period the raw post lacks; fix in the next ledger edit.

#### Early Phase 2 track (P2-09, P2-10, P2-03 drafts), rulings 2026-09-15

Drafts accepted as engineering with three mandatory items for the post-merge batch before any receipt is issued: (1) P2-03 realized-variance targets must use bid-ask midpoints at the contract's 5-second age rule, not one-minute trade closes; the produced slice is not the contract's definition. (2) NQ and ES option definitions, open interest and quotes are owned data in Databento DBN form and must be decoded with the official decoder, not labelled unsupported; install the decoder as a recorded dependency and register those roots' coverage. (3) The Level Atlas is a pipeline proof only: it used run-1.0.1 geometry and outcomes and OHLC extremes; it is rerun over the full history with the corrected-baseline populations, the P15-03 benchmark outcomes, the new market view's extremes and the decoded futures-option roots before any number is cited. Minor: per-task DECISIONS.tsv holds one row each; numba is a hard import in pricing (acceptable, installed and already used).

### Addendum: 04-family-adapters round-three rulings (2026-09-15)

Independent verification of the second 04 close and the orchestrating session's read produced four items, batched into one final follow-up (the second and last for this run):

- **F8, B0 parity.** `dual_scan` applied the registered family transforms to the B0 document as well as B0.1, so B0 for SIRES, SAINT-AMT, MEMBER-TWO-REASONS and KEANI no longer equalled the frozen scanner's bytes (12 of 24 replay rows differed; P15-12's B0 moved from 141/19 to 116/15 between attempts with `method_pack` untouched). Ruling: transforms bind into B0.1 only; B0 is `scan_branch` output byte-identical except `baseline_version` and adapter metadata; one parity fixture per transform family.
- **F9, own-population contacts.** The second close proved "own population" with a function that makes every complete bar overlapping the reference a contact and assigns `setup` to each. That is a dedup artifact, not new geometry. Ruling: a candidate's own population uses the family's B0.1 contact definition (one contact per reference lifecycle per approach, departure rule between contacts) and evaluates the family's rule at each contact; fixtures: ten-bar dwell yields one contact, a failing contact yields `no_setup`, long and short mirror.
- **F10, Saint arrival default.** A missing confirmation time made the arrival read pass. Ruling: missing operand is unknown (`None`), and the episode verdict is unknown.
- **F11, ordering.** Method pages freeze before the new snapshots; status pages update after the verifiers pass and the verifiers run again on the final bytes; no closure claim otherwise.

Routed elsewhere, not reopened in 04: the throughput target and the full-history populations of the 04 additions (05 stage A, an engine-and-freeze run under PERFORMANCE.md that precedes the search; the corrected baseline for the 39 census branches is read from census run `20def36e065c13d7`, never recomputed per candidate); the 260-session refill printed-figure replay (07, citing the git commit of `REFILL_PRINTED_TOLERANCE.json` made at this checkpoint as the pre-registration ordering evidence). Every 04 population stays labelled engineering slice until stage A.

Reading note for the census: its `data_unavailable` and `no_setup` columns are the Phase 1 per-episode strategy-assessment labels and pair one-to-one with unknown and fail verdicts; they are not statements about market data coverage, which the job records carry in `market_feed_completeness` and `current_prefix_coverage`.

### Addendum: source-fidelity rulings (2026-09-15)

The Astra source-fidelity review at [planning/research-program/reviews/astra-fidelity-2026-09-15/REVIEW.md](/workspace/planning/research-program/reviews/astra-fidelity-2026-09-15/REVIEW.md) (effort max, commit 4a775b07) concludes that the entry-strategy families are not yet faithful replications of the authors' complete methods, and lists twenty ranked findings F01 to F20 with source locations. The orchestrating session accepts the review and rules as follows. These rulings define baseline version **B0.2-2026-09-15**: the source-faithful baseline, implemented natively in the family adapters on the array engine, measured over the full history beside the frozen B0 and B0.1 rows. B0 and B0.1 stay frozen comparison rows. Each ruling states the rule, its classification (source-specific literal, or operational where the source is discretionary, labelled OD in the code and the Strategy Book) and the evidence that proves it. The search (P15-17) pairs candidates against B0.2; no upgrade is scored before B0.2 verifies.

**JJ-TBR.**
- F08: the 10:00 reduced-expectation rule applies to `single_extended` only (TBR p12). `extension_reaction` and `internal_rotation` take reactions at any time of the session (TBR p21; JR p23). Evidence: the 906 extension episodes removed under B0.1 return in B0.2; a confirmed 13:00 1.33/1.66 reaction fixture is admitted.
- F11: confirmation admits the author's stated favourites, any of a full-C2 order block on the 2, 3 or 5-minute chart or a rejection block (TBR pp25–29), at the first contact or a later fresh confirmation inside the window; the record names which. The single 3-minute first-contact template is one registered timing variant, not the baseline. Absorption confirmation stays OD.
- E1 (Judas): strict and deferred readings both stay, both labelled OD; the deferred read checks that the edge held from the early confirmation to the in-window bar, not only that bar.
- E3 (`single_purged`): the add is a 09:40–09:50 continuation after all significant overnight liquidity is purged and the range compressed then expanded (TBR pp12–15); implement the add-on state and entry; never reinterpret it as a Judas fade.
- A2 (context): open classification relative to value, width and purged liquidity stays OD with the thresholds registered and reported as a funnel; the prior-RTH sweep is not "all significant overnight liquidity purged" and must be labelled as the stand-in it is.
- A5 (P-zones): the proprietary generator stays unknown; expiry follows the source display rule (until 18:00) and invalidation deletes the zone; label the quantile settings OD.

**GB-FAIL, GB-VWAP, GB-SCALP.**
- F01: the two old scalp case branches leave entry scope; they are observations (`condition_present` / `condition_absent`), not entry setups, because GB p40 discloses no repeatable entry. Report the removal of the 3,066 rows from the setup book. `golden_pocket_continuation` (A4) is the only scalp entry branch.
- F06: A1 to A4 become executable branches with stage and episode records. A1 London: pre-open London-low sweep, reclaim, retest (mandatory as the post states), higher low, post-open close, targets midnight open then London high (NG 2099513366326730859). A2: Asia-high failure short as stated, without a TDO requirement; a long mirror is a registered candidate, not baseline. A3: overnight prior-day-low reclaim long as stated (NG 2099503614372741234; GB pp48,52–54 corroborate); extension to week and month levels and to every box branch is a registered candidate, not baseline. A4: the pocket is drawn from the impulse leg in the leg's own direction, for an up-leg [H − 0.618W, H − 0.50W]; long in bullish context as the post states; the first 5-minute close confirmation stays OD; stop and target from the drawings are case geometry: in the author's 2026-09-11 example the stop sits at the pocket's near (50%) edge, 35 points below the entry, so the baseline stop is that near edge (labelled OD, with beyond-the-far-edge as the registered variant) and the target is the range high / prior-day high with the 25-to-30-point limit ladder.
- F07: directional compatibility is a source-stated admission (GB pp25,35,37–40), not "context exists". Implement a labelled OD bias rule derived from those pages (higher-timeframe direction from the prior day's close relative to its value and the 09:00–10:00 box direction), admit only compatible trades, and report both the unfiltered and the bias-filtered populations with per-day multiplicity. No cap on trades per day: the source states no cap.
- A2/A3 (GB-FAIL): the 5-minute close confirmation is literal for the Asia and PDL cases (GB pp19,25) and OD for the others, labelled per case; the golden-pocket down-leg case requires the pocket and the retracement entry after the close (GB pp23–25); the stop is the case-selected structure (above PDL or the swing high), not a universal sweep-extreme plus one tick.
- A5: add the NWOG branch (GB p37 and pp23,30–39); no 09:00–11:00 cutoff, the source has afternoon trades.
- F13: the GB-VWAP retest window is unspecified in the source. The baseline searches to the RTH close; "no retest before the close" is a fail (measured absence), never unknown; unknown is reserved for missing coverage. The 60-minute expiry becomes a registered timing candidate. Report how the 628 unknowns resolve.
- F14: correct SOURCE_ADDITIONS_2026-09-14.md items 11, 19 and 27 accordingly (retest mandatory; A4 long-pocket geometry; drawn targets are not realized exits).
- F18: the clock rows for JJ-TBR (ET stated, TBR p6; SS p8) and Green Bird (UTC−5 in November, UTC−4 in summer; GB pp43,45,48; NG photos) record seasonal New York time as supported by evidence; remove the blanket `clock_zone_unverified` for those two sources. SIRES' PST statistics (MAMT p20) are noted for that document only.

**SIRES.**
- F02: `clean_squeeze` is the fast, rewarded breakout with no retest and no false start (CONT p11). The pullback-absorption-continuation sequence is the failed-squeeze catalyst (OFM p10) and lives in that branch. Fixture: the author's clean example is admitted; a retest disqualifies.
- F03: replenishment operands bind to the native producer fields (`added_at`, `added_size`, `displayed_defense`, baseline_repairs.py lines 259–305); no default of zero; a missing operand is unknown, never a dropped episode; the three-tick replenishment applies to `stop_four_stage` too; before-and-after replay of one native episode must show an explicit verdict, not a deletion.
- F09: location eligibility follows the source (LVN, shelf, value-area edge and auction extremes; never the POC chop, C1 pp3–10; AMT1 pp5–9; MAMT pp5–13), replacing the four-pivot pre-open balance; thesis direction follows higher-timeframe value migration (OD, labelled), replacing C5's microbalance-half rule; thesis invalidation on structural acceptance or value migration is an OD stage, labelled, with `thesis_alive` no longer a stop-distance proxy.
- A3/A5: entry within one to two ticks of the defended level, two to four upticks, fresh sequence before re-entry, −4R daily stop (STOP pp3,9–15) are literals; the 1R to 3R objective is a target price, not a width diagnostic; aggressive-print thresholds 30–60 (BIG) replace 100 for this family.
- A7: VWAP anchor and deviation are the author's chosen anchor with 1, 2 and 2.5 deviations, outer bands preferred (VWAP pp5–10); the fixed session ±1σ is one variant.
- A8/F17: the KG1 and gamma nodes are inferred proxies, labelled as such wherever a pass count appears; max pain joins the historical binding.

**SAINT-AMT.**
- F04: the three stages implement the source readings, not substitutes. Arrival read: fast versus slow approach into the balance, measured as displacement per bar over the approach relative to the balance width (OD threshold, registered). Profile permission: the profile shape category (balanced single distribution, double distribution, P, b, unrebalanced trend) from the HTF profile with the continuation preference and the trend avoidance (RTVP pp4–11; WIC p4), not "POC inside its own balance". Alignment: independent higher-timeframe control direction (value migration of the HTF balance) agreeing with the LTF break direction (WIC pp7–10), never derived from the trade side. Bind `confirm_at` and `ltf_balance` on all four routes.
- F05: remove the older-auction exploration gate from `failed_auction_return`; the sequence is new-value failure then return to the original accepted value (AMTL pp8–12).
- A2/A3: the scan is not NY-only (the source's trapped-buyers example is an Asia short); add the long mirror of trapped buyers that the source describes.
- Evidence: per-stage funnel counts over the full history; the 972 census unknowns reported separately from the 8,308 fails; the S13 to S15 diagrams as fixtures.

**MEMBER-TWO-REASONS.**
- F15: remove the 12:45 temporal split; two reasons are a prior reaction and a minor HVN at the same location from any prior history, overlapping windows allowed, or KG1 as the alternative second reason when aligned (K10 pp5–8); the independence check binds into admission; the 1.5R spoken target is literal (K10 pp7–8).

**KEANI.**
- F16: remove the 11:00 cutoff and the 60-minute retest expiry; the A period is 09:30–10:00 (TPO p3), the observation is around 10:00, the break-retest sequence runs to the session end; the objective is a pre-chosen higher-timeframe level (OD, registered: the nearest of prior-day high, prior VAH and the weekly level above), not A-high plus A-width. Report the fully-above-A eligible denominator and the stage funnel.

**REFILL-STUDY.**
- F10, F20: zone formation follows the source (aggressive clusters create zones, departure, every later touch recorded, REF pp5–9) with the OD parameters registered; the departure timestamp is the actual departure; the printed execution bracket (12 ticks inside, stop 32, target 96, cancel 30 minutes, one position, one-tick cost and slippage, REF p12) is connected to the historical touch path; the 260-session printed-figure replay runs against the tolerance file committed at ad24fba3, and the population is reconciled to 41,152 touches over 235 sessions before hold rate, R sign and dip are compared. If the population cannot be reconciled, REFILL-STUDY stays `population_scale_unreconciled` with the measured figure.

**JETBUNDLE, STOIC.** Observational and process scope as reviewed; no baseline change. The ledger labels the L1 proxy, the classifier thresholds and the macro proxy as ours.

**Ledger and records (F19).** Correct SOURCE_RECONSTRUCTION_LEDGER rows L018 (five-minute close is printed, GB pp19,25), L021 (A ends 10:00, TPO p3), L024 (1.5R is printed, K10 pp7–8), L030 (the 3-minute option is printed, TBR p27), L032 (entry distances are printed, STOP pp9–10), L038 to L044 (clock evidence), and the SOURCE_AUDIT rows they feed; bind each printed literal.

**Author-example replay.** The review's example index (J01–J18, G01–G28, S01–S22) is the fidelity test. Every example marked Y (inside the tape) with an identifiable session date and setup is replayed through B0.2 for its family; the Strategy Book reports, per example, detected yes or no, our level and direction against the author's, and the divergence. A miss is a finding; no rule is adjusted to make an example pass without a source quote.

**Task structure.** This work is task P15-16A "source-fidelity baseline B0.2" in subphase 05-finite-search, the predecessor of P15-17, run as parallel family tracks in worktrees and integrated with one merged-tree run that measures B0.2 over the full history on the array engine and issues the receipts. FREEZE.json cites B0.2.

### Addendum: source fidelity re-read rulings (2026-09-15, evening)

The orchestrating session re-read every family against its raw sources with all charts, tickets, on-chart tables and whiteboards rendered at native resolution and zoomed (wiki/log.md entry 2026-09-15; each method page's "Source fidelity re-read, 2026-09-15" section; wiki/source-catalog.md's dated-example inventory). Astra's per-family dossiers (planning/research-program/reviews/astra-family-dossiers-2026-09-15/) are folded in as they complete; the JJ-TBR dossier's J21 and J22 are ruled here after independent verification. These rulings extend the source-fidelity rulings above and bind P15-16A (A01, A03).

**JJ-TBR.**
- RR-01 (Astra J21, verified): `extension_reaction` in `method_pack/historical_price_scanners.py` (line 85) and `rule_discovery/baseline_repairs.py` (line 690) places the band at edge ± [0.33, 0.66]·W while the author's ±1.33/±1.66 lines sit at edge ± [1.33, 1.66]·W, as the standalone object O015 (`objects/range_geometry.py` o015) and the author's charts show (2025-01-28: H 21,410, W 152.50, +1.33/+1.66 at 21,600–21,660; 2025-09-09: L 23,810, W 50, −1.33/−1.66 at 23,745–23,730; 2025-11-10: H 25,560, W 60, band 25,635–25,650). B0 and B0.1 measured this branch a full width too close to the edge. B0.2 uses edge ± [1.33, 1.66]·W; the ±0.33–0.66 band is a registered candidate labelled OD, not the source; the geometry identity test (H 110, L 100 → 123.30–126.60 / 83.40–86.70) is a required fixture.
- RR-02 (Astra J22, verified): `source_adapters/common.py` (lines 1104–1140) assigns R-eq and R-q1 long and R-q3 short and labels q1/q3 "not the EQ-only source location". The author trades EQ both ways (2026-09-02, 2026-09-01) and the manual permits quadrant entries in the extended and purged cases (TBR pp.12–15); the sides are case-selected, not fixed by the level. B0.2 enumerates EQ and quadrant contacts on both sides and binds the side to the branch's context.
- RR-03: the action starts at the 09:00 range close (2025-10-13 first stage 09:00–09:15; 2026-01-02 09:22 P-zone long; 2026-01-09 09:00 absorption marker; the 09:00–09:06 secondary reversal peak on the 4,537-day histogram). The sweep search and the P-zone Session 1 anchor start at 09:00; the 09:30 start is a candidate, not baseline.
- RR-04: the London box is built 02:00–03:00 ET and traded 03:00–06:00 (JR pp.50, 63–64); `other_session` uses this clock with the same quadrant, ±0.5 and 1.33–1.66 geometry; the 00:00–03:00 assumption is retired.
- RR-05: the P-zone entry is an absorption print inside the timed P-zone box (Session 1 09:00, Session 2 10:00 or 09:50, Session 3 02:00), stop below the box, target the 3-day pivot (D-1 High on 2026-01-09). Where the proprietary zone cannot be regenerated, the author's printed zones are fixtures and the branch is measured as a fixture check (F17 stands).
- RR-06: the reclaim entry after the reversal window (2025-01-28 buy at 09:53:46 ET on the reclaim of the low) and the exit below +0.5 (sell at 10:27:05 ET) define `judas_reversal`'s baseline entry and objective; the projection ladder runs to ±3 and the mean-reversal band is ±0.33–0.66 from December 2025 (the manual's ±0.5 sits inside it).
- RR-07: SessionStat envelopes (60-session statistics of the selected clock) and EVRange (AM expected-move envelope around the open, +50% line) are locations; supplied readouts are fixtures with their settings (F17). The A+ fade template is the coincidence of R-Lo/R-Hi, an EVRange edge and the overnight low/high (2026-08-28).
- RR-08: the open-location model selector (fade / single break / scalp) is read pre-open from the prior RTH value and range (2026-07-27, 07-28, 07-10); B0.2 records it as a decision-time context label, not an outcome.
- RR-09: published statistics to replicate in the Strategy Book: 86.46% reversal from the extended range over 4,537 days with the 09:40–09:50 modal window; the 3,753-session 1.33/1.66 capture table (89.2/65.6, 92.4/66.8); the first-hour sweep table by open location (n 396: 29.5/37.6/29.8/67.2; n 517: 23.6/46.2/27.3/69.8); BigTrades ≥100 NY / ≥75 London.
- RR-10: author-example replay set for JJ-TBR inside the tape: 2025-01-28, 2025-05-23 (London), 2025-09-09, 2025-10-03, 2025-10-06/07/08 (London), 2025-10-13, 2025-11-10, 2025-11-18, 2025-12-30, 2026-01-02, 2026-01-09, 2026-02-24, 2026-06-05 (London), 2026-06-09, 2026-07-06, 2026-07-10, 2026-07-16, 2026-07-27, 2026-07-28; after the tape: 2026-08-28, 2026-09-01, 2026-09-02 (data_unavailable).

**GB-FAIL, GB-VWAP, GB-SCALP.**
- RR-11: three sessions, one template. Asia box as painted (20:00–21:00, 20:00–23:00 or 20:00–00:00 by month), London box as painted (03:00–04:30 in April and August 2026; 02:00–05:00 in late August and September 2026), NY 09:00–10:00 with the 09:30–10:00 / 10:00–11:00 sub-box; the scan covers the overnight (00:30–01:00 and 20:40 entries), London (03:00–04:30) and the PM (12:45–14:00 sweeps of the AM highs). Both London variants are registered as the author's; a NY-only scan is a candidate.
- RR-12: risk is a fixed dollar amount per account ($750 on every position tool) with the quantity derived from the stop distance; the exit is a limit ladder of 1-lot orders (4–18 rungs, 8–25 points apart) toward the opposing liquidity with the position tool's target at the far level. B0.2 records the ladder as the objective path and the first rung as the first objective; a single target is a candidate.
- RR-13: the box edges are traded on the failure as soon as the sweep fails (2026-08-31 09:33 short at the 09:00–09:30 box high; 2026-09-08 long at the 9–10 low), and the completed box after 10:00; "not before 10:00" is retired for the at-level branch. The 5-minute close confirmation stays literal for the Asia-high, TDO and PDL cases.
- RR-14: the golden pocket has three uses (overnight short on the retracement of the last impulse, 2026-07-29; stacked PDL short, 2026-09-01; continuation long, 2026-09-11); the pocket is measured on the leg in its own direction; the stop sits at the pocket's near edge in the author's example (F14 correction stands).
- RR-15: objectives can lie in the next session (2026-08-11 Asia long held into the 2026-08-12 NY open; 2026-07-29 short into the 2026-07-30 London session); B0.2 measures the objective path to the next session's open before censoring, and reports the 30-minute research horizon separately.
- RR-16: author-example replay set for GB inside the tape: 2025-11-20, 2026-04-23, 2026-04-28, 2026-07-13, 2026-07-29/30, 2026-08-11/12, 2026-08-13; after the tape: 2026-08-27/28, 2026-08-31, 2026-09-01, 2026-09-03, 2026-09-08, 2026-09-11, 2026-09-14 (data_unavailable). The 2026-04 MNQM26 long (undated) is a fixture only.

**SIRES, REFILL-STUDY.**
- RR-17: the session PDFs are dated and the ledger is printed (wiki/method-sires-thesis-flow.md, "Dated ledger with printed prices"). Author-example replay set inside the tape: 2026-07-08, 2026-07-09, 2026-07-10, 2026-07-14, 2026-07-15 (overnight), 2026-07-23, 2026-07-31, 2026-08-04, 2026-08-06, 2026-08-19; each with the levels drawn by the author as fixtures and the printed fills as the detection target.
- RR-18: the OFM entry is a resting stop order below the failed-squeeze wick (2026-08-04 "−1 STP | 0.00 $" at 29,370.25; OFM pp.11–14); B0.2 models the resting-stop entry as the baseline for `ofm_aggressive` and the drive-retest as the second entry. Stops are 7–27 ticks beyond the failure box on the OFM shorts and 13–18 points on drives and refills; the OFM shorts carry a fixed 40-tick target or the far side of the last control zone; these are registered as the author's literals with their dates.
- RR-19: the printed entries sit in the first fifteen minutes of the cash session on most dated days (09:31–09:41); B0.2 reports per-branch time-of-entry distributions and the funnel from 09:30, and the trailing rule (stop behind protected highs and lows after a close past the prior swing with aggression) is implemented for management.
- RR-20: aggression thresholds per family: Sires bubbles 30–60 contracts NY AM NQ (OFM p.4; BIG p.3), imbalance 350% (BIG p.5), generic footprint flag 3–4× (FP8 p.5); Jumbo's 100/75 does not apply. VWAP bands ±1, ±2, ±2.5 with trades beyond the 1 band, ideally at 2, with absorption (VWAP p.4).
- RR-21: the ES lessons (STOP pp.11–13 on EPZ25; FP9 footprints) are ES examples; their tick distances are not NQ thresholds (F03 stands). The Refill Effect's construction, population (about 175 touches per session), bracket and statistics are as ruled at F10/F20; the hold-label boundary is registered OD.

**SAINT-AMT.**
- RR-22: the worked example is an Asia-session trade on 2026-08-10 evening ET (short 5 MNQ at 29,729.25, stop box to 29,736.75, exit 29,678.75) inside the balance 29,600–29,960 drawn on Sierra Chart, with the WIC week 2026-08-04 to 2026-08-12 as the higher-timeframe context. The scan covers the Asia session; the replay set is the 2026-08-10/11 trade and the WIC 29,740 break-and-retest. F04 and F05 stand; GEX levels (put wall, call wall, GEX flip, vol trigger) are on the author's chart and belong to the Phase 2 context.

**MEMBER-TWO-REASONS.**
- RR-23: the only worked example is on ES-202609 with ES tick economics and a fixed $500 risk (K10 pp.7–8, 12–13). The NQ adapter is labelled a transfer; the author-example replay is data_unavailable until an ES tape exists; F15 stands (the drawn first ticket is R:R 1.00, the second 9.60, the prose 1.5R: the target-policy check stays separate).

**KEANI.** F16 stands; no dated ticket exists; the replay set is empty and the stage funnel is the fidelity report.

**JETBUNDLE, STOIC.** No change; definitions verified literal against MATH and DATA.

**Author-example fixtures.** The dated examples with printed levels, fills, resting orders and expected detections are compiled in [AUTHOR_EXAMPLES_2026-09-15.json](/workspace/planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-15.json) (54 examples, 42 inside the native calendar); P15-16A replays that file (A03) and supersedes the review's J/G/S index where the two overlap.

**Clocks (all families).** Deepchart screenshots print ET; the 2026 NinjaTrader screenshots print UK local time; TradingView prints the footer's UTC−4/−5; the Tradesea chart and the 2025-01-28 order ticket print UTC; Sierra Chart prints ET. Every replay fixture carries its converted ET time.

#### Evidence-binding gap in the closed Phase 1.5 receipts (recorded 2026-09-15, evening)

Inspection of the closed P15-16 receipt `cf6bf4778e53a0b0` shows the receipt-level keys A06, A07 and A08 and the assigned cases S01 and S03 bound to the same unrelated test (`test_s07_native_replay`) with the pytest log as evidence; the S01 and S03 mutation probes SILENT_FAILURES.md defines were not executed as receipt evidence. The verifier accepts such rows because it only checks that node ids and selectors resolve. The same pattern was found and rejected in the Phase 2 early-track producer today (two follow-ups). Ruling: from P15-16A onward, a passing matrix row binds only to a test whose function name starts with `test_<id>_`, or (A06 to A08) to the recorded pytest command plus the artifact hashes it attests, or (S01, S03) to an executed mutation-probe file with a verifying control; anything else is "deferred" with its reason. The closed 00 to 04 receipts are not re-opened for this: their verifier-enforced identity, inventory and predecessor checks stand, and the 07-release task (P15-20) re-verifies every receipt and must re-bind or explicitly list these rows as a known limitation of the earlier closes.

#### Successor-rule dependency after the pre-search merge (recorded 2026-09-15, evening)

Merging the P15-17 pre-search tracks (97284bcd) changed native.py, runner.py, engine_slice.py, formations.py, profiles.py, sequences.py, source_adapters/common.py and every family adapter, all of which the closed P15-02 to P15-16 receipts pin. Under the verifier's supersession rule these receipts now verify only through a later verified receipt that lists them as transitive predecessors and pins those files at their live bytes. The P15-16A receipt is designated that successor: its identity must declare the full changed-file set (instruction added to the integration step), and its verification is the test that the chain is whole again. Receipts finalized in between (the Phase 2 early-track receipts, whose p15_02 predecessor must also be moved to the closed attempt `c9756fc1e534b240`) wait for it.

Canonical source: [REVIEW.md](/workspace/planning/research-program/reviews/astra-fidelity-2026-09-15/REVIEW.md).

## Astra source-fidelity review (2026-09-15, commit 4a775b07, effort max)

SOURCE-FIDELITY REVIEW — 4a775b07782837978c407e312df0958414528b4d
Conclusion: the entry-strategy families are not yet faithful replications of the authors' complete methods. Several useful components match; B0.1 fixes real B0 defects, but also retains or introduces population-changing substitutions. The process/risk families require separate, narrower verdicts below.
Scope: read-only review of the detached worktree. PDF page references count covers. Text extraction covered 41 PDFs; image-only/embedded charts are identified below. For older Jumbo/discretionary chart details I rely on wiki/source-catalog.md:5,51 and the wiki-linked M/source_cases_v2.json transcription; I independently inspected the seven September 14 photos and all 35 cached GB chart/account images on pp43–60. This is not an independent visual transcription of every archived chart/video, so the example index preserves unidentified figures rather than inventing their dates or prices.
Verification: no full-history replay was run. Small in-memory executions of the actual adapter functions reproduced field-binding, contact-status, scope and departure-timestamp defects; receipts: /tmp/astra-fidelity-2026-09-15/READ_ONLY_REPRODUCTIONS.json. Population numbers below are the committed reports, independently read and totalled, not newly measured fills.
Code aliases: M = implementation/src/trading_research/research/method_pack; R = implementation/src/trading_research/research/rule_discovery/baseline_repairs.py; A = implementation/src/trading_research/research/rule_discovery/source_adapters. B0 = frozen M scanners; B0.1 = R/REPAIRS; 04 = A transforms/helpers. A component contract or synthetic fixture does not establish that the historical scanner consumes it (M/catalog.py:28,57; A/common.py:1245).
Review aliases: CENS = implementation/reports/research-work/baseline-repair/20def36e065c13d7/SUMMARY.md; U = planning/research-program/reviews/unknown-audit-2026-09-14/UNKNOWN_AUDIT.md; DIS = planning/research-program/reviews/phase1-code-review-2026-09-14/DISPOSITION.md; ADD = planning/phase-1-5/SOURCE_ADDITIONS_2026-09-14.md; SA = planning/phase-1-5/SOURCE_AUDIT_2026-09-14.md; L = implementation/reports/research-work/P15-04/0d0a57cc4de997b4/attempt-0001/SOURCE_RECONSTRUCTION_LEDGER.json (row IDs are stable locations).
Report aliases R09–R16 mean implementation/reports/research-work/P15-NN/HASH/attempt-0001, respectively: 250e5aea146f3516, b89cbd7b0f4473cc, 9e7fda7b291cce99, f33f750e365a04c1, 8de8e78a21b0838a, f01de253cf514105, ced9a15cf6c6dae2, cf6bf4778e53a0b0. Each /FAMILY_REPORT.md:3–23 is the family summary; /NATIVE_CASES.json supplies case/population keys, except R16 has no such file.
Raw aliases: TBR = sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf; SS = same directory/SessionStat+.pdf; FIND = same directory/jjumbo-findings.pdf; XF = same directory/xfcmg2.pdf; JR = sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf; GB = same directory/greenbirdtrader-complete.pdf; NG = sources/x-raw-2026-09-14/greenbirdtrader. NG post IDs identify tweet-ID.json and its numbered photo files.
D = sources/documents/discretionary. Source abbreviations expand to D/NAME.pdf: C1=code-1-thesis; C2=code-2-risk; C3=code-3-orderflow; AMT1=amt-lesson-1; VP2=vp-lesson-2; TPO=tpo-lesson-3; VIX=vix-lesson-4; DOM5/6/7=dom-lesson-5/6/7; FP8/9=fp-lesson-8/9; VWAP=vwap-lesson-10; GEX=gex-framework; ABS=your-mistakes-with-absorption; STOP=stop-re-entering; RD=reading-delta; BIG=only-trade-big-trades; OFM=origin-of-the-move.
Further D aliases: REF=refill-effect; MAMT=mastering-amt-vp; ANAT=anatomy-of-a-losing-start; NYAM=ny-am-session; K18=18k-payout-session; K2345=2345-funded-session; CONT=a-clean-continuation-short; RTVP=reading-the-volume-profile; AMTL=amt-on-live-markets; WIC=whos-in-control; TRAP=trapped-buyers-one-retest; K10=10k-first-month; AVG=average-unprofitable-trader; MATH=the-math-behind-auction-market-theory; DATA=data-engine.
Reading authority: sources/documents/README.md:3–6 distinguishes author claims from user hypotheses and assistant proposals in conversations; inventory/DATA_INVENTORY.md, not databento_pull_list.md, records acquisition. Pine formulas are owned code, not automatically an author's proprietary formula. Example: indicators/Pinescript-indicators--main.zip::Expected Volatility .txt:12 uses fixed GMT-5; ::Statistical VWAP study Session and RTH VWAP.txt:8 uses GMT-4; ::6 to 9 Session and Levels.txt:22 uses America/New_York. They cannot all certify one universal author clock.
Table notation: F=faithful; Dv=divergent; OS=operationalized although source is specific; OD=operationalized where source is genuinely discretionary; MISSING=source-stated rule absent from the historical path; INVENTED=unsupported enforced condition. Each A row reads source/location | implementation/version | classification and population effect. E/P/F/U below means episodes/passes/fails/unknowns, never winning/losing trades.
Clock convention for every family: M/clocks.py:21,51 converts dated America/New_York wall time, including DST, to UTC nanoseconds; intervals are half-open. JJ explicitly says “Eastern Standard Time, ET” (TBR p6), with New York corroboration in SS p8 and the 6–9 Pine:22; that supports ET, not proof of a fixed UTC-5 rule. GB says EST (GB pp33,37); the dated November 20,2025 chart (GB p43, right) shows UTC-5 and April/summer/September charts UTC-4 (GB pp45,48; NG photos). Together these support seasonal New York time; blanket winter-clock-unverified is not justified for those examples. SIRES' ES statistics explicitly say 06:30–13:00 PST/IB 06:30–07:30 PST (MAMT p20), which cannot silently certify all source chart clocks. SAINT, MEMBER, KEANI, REFILL and process illustrations do not establish a universal fixed offset; their named sessions/bar durations remain usable. Blanket clock_zone_unverified is cautious, but “no stated clock” loses the evidence just listed (L038–L044; ADD:33–35).

JJ-TBR
A1. Eight ranges: 20:00–20:30, 00:00–00:30, 03:00–03:30, 06:00–09:00, 09:30–10:00, 10:00–10:30, 12:00–12:30, 15:00–15:30 ET (TBR p7) | B0 M/historical_price_scanners.py:52; M/coverage.json assumptions.tbr_sessions | F formation clocks; OD fixed 60-minute action horizon for other_session, which the source does not prescribe.
A2. Classify open relative to value/range, width/volatility, prior/overnight liquidity and inter-index context before choosing reversal/extension; preselect PD RTH 09:30–16:00 extremes/15m–H1 imbalances, ignoring ETH consumption of those PD destinations (TBR pp8–15,21,32–36; JR pp3,37–43) | B0 M/historical_price_scanners.py:14–22; B0.1 R:647,782 | Dv: simple pre-range/open direction and width ratios replace that context; prior-RTH sweep is not “all significant overnight liquidity purged.” Invented thresholds admit wrong regimes and omit discretionary qualified ones.
A3. Sweep, then confirmation: author's “PERSONAL FAVORITES” are 2/3/5-minute full-C2 OB, rejection block, or optional absorption; C2 sweeps C1, C3 confirms; midpoint/conservative full-C2 stop and optional retracement entry (TBR pp25–29,31,35) | B0 M/historical_price_scanners.py:25–40; B0.1 R:547–563,764 | OS/Dv: mandatory single 3-minute C2/C3 template at first contact; full-C2-plus-tick stop only. Alternatives and later fresh confirmations are MISSING; population contracts sharply.
A4. 1.33/1.66 reactions, EQ/quarters, directional objectives; single-extended has reduced expectations/no interest after 10, whereas extension reactions also occur AM/PM (TBR pp12,15,21; JR p23) | B0 M/historical_price_scanners.py:72; B0.1 R:52,647–676,687 | F basic levels; Dv C2 repair applies 10:00 cutoff to extension_reaction/internal_rotation too. B0.1 only EQ in these entry paths; quadrant flag does not implement quadrant selection.
A5. P-zones use per-ticker volume/volatility-filtered distances, 500 sessions, S1 09:00/S2 10:00/S3 02:00, displayed until 18:00 and invalidation deletion; f02 instead shows S2 09:50 (JR pp16–18,55; wiki/source-catalog.md:51 transcription of frames f02/f05) | B0/B0.1 M/strategy_policy.py:30–36; M/strategy_pzones.py:43–74 | F printed anchors/lookback partly; OD .70/.80 quantiles, median-volume filter, 60-minute normalization and 20-session minimum; Dv 16:00 expiry, MISSING invalidation. Exact proprietary generator remains unknown; display-end versus training-end and S2 discrepancy remain unresolved.
A6. News-dependent second cycle, market/limit/stop-order alternatives, stop after three failed attempts or reduce size at least 50% (TBR pp18,22,25–26,37) | B0/B0.1 M/historical_price_scanners.py:52–186; M/catalog.py:71 management predicate | MISSING from scanner admission/execution lifecycle; supplied management contracts do not reconstruct these decisions. Fixed research boundary outcomes are not the author's order management.
B. Genuine unknowns: proprietary EVRange/P-zone distribution and live selected context/management; individual fills; unreadable chart dates. Recoverable: quarter geometry, 2/3/5-minute choices, ET wording, learning window/anchors/invalidation, single-purged continuation and scoped 10:00 rule (above). L030's “unprinted 180s” misses the printed 3-minute option; L039's no-clock characterization misses TBR p6/SS p8. Formation emptiness/width≤0 are data/geometry, not undisclosed strategy rules (U:23,31–34).
C. CENS:41–50: Judas strict 1714/41/1671/2 versus deferred 1714/213/1496/5; B0 1397/133/1258/6. Strict's 2.4% pass rate is not the source's 86.46% excursion statistic (TBR p30); neither is a win rate. First-contact/3-minute confirmation timing likely explains much of the gap, not proof of extreme author rarity. Extended 568/8/560/0; purged 568/21/546/1; internal 1132/3/1128/1; extension 1221/149/1069/3; other 13116/1730/11371/15; P-zone 2633/305/2310/18; outbound 1695/1528/148/19. Extension episodes fall 2127→1221 under the unjustified broad cutoff. TBR p8 describes roughly two opportunities/80–120 points, not two obligatory filled trades per day.
D. Replay index J01–J18 below; source figure controls are distinguished from dated author examples.
E1. Judas: “actual reversal trade between the 9:40 and 9:50” (TBR p8). B0 starts sweeps in that interval; B0.1 R:676–705 correctly allows 09:30–09:40 sweeps, then requires entry in [09:40,09:50). Strict rejects early confirmation; deferred R:632–642 enters first complete in-window bar holding the edge. Both are OD readings, not two source-published strategies; deferred checks that bar, not uninterrupted holding since the early confirmation. A/jumbo.py:77–80 really dispatches deferred despite its absence from the default branch tuple.
E2. Quadrants: “EQ/quadrant” entries (TBR pp12–15; wiki/range-internals.md:5) | 04 A/common.py:589,1075–1179 computes quarters but substitutes generic contacts; A/common.py:816 needs source_confirmation, absent on native bars. MISSING executable family confirmation, not a faithful quadrant population. Outbound 09:30 toward 09:40–09:50 (TBR p8): B0/B0.1 M/measurement_outcomes.py:98–102 already cap boundary observation at 09:40; A/jumbo.py:47 adds metadata. F for the named 09:40 variant, OD exact choice, not evidence of a filled timed exit.
E3. single_purged: all significant overnight liquidity swept, compressed range, expansion and an additional 09:40–09:50 CONTINUATION (TBR pp12–15) | R:782–790 checks either prior-RTH extreme plus width≤half prior range; A/jumbo.py:39 only names the add. Dv context; MISSING add-on state/entry. Do not reinterpret this add as Judas fading the move.
F. Three priorities: mandatory first-contact OB; overbroad 10:00 cutoff; incomplete purged/quadrant/P-zone context. Verdict: not yet replicated (range arithmetic and named clock variants are useful faithful components).

GB-FAIL
A1. Completed 09:00–10:00 box, preceding hour, prior day/week/month, Asia and TDO; HTF/directional context first (GB pp23–25,30–35,38–40) | B0 M/historical_price_scanners.py:189–200; B0.1 R:836–919 | F completed references within declared scopes; OD approximate Asia 20:00–00:00/London 02:00–05:00; Dv all scans start ≥09:30 and prior references use RTH scopes/fallback charts without establishing the author's exact period scope. Invented “context exists” substitutes for directional compatibility (R:890–902).
A2. “Sweep → reclaim → opposing liquidity”; explicit Asia/PDL cases wait a five-minute close (GB pp19,25,31) | B0 M/historical_price_scanners.py:219–223 only sweep candle; B0.1 R:836–883 searches subsequent completed 5m closes | F B0.1 repair of temporal order; B0 divergent, undercounting later reclaims. Universal 5m confirmation across every case is OS: GB p40's cash-open variant and p43's sweep entry do not specify that same prerequisite.
A3. Golden-pocket down-leg 50–61.8%, PDL sweep/failure, then a few-point retracement after the close; stop above PDL/swing high as described (GB pp23–25) | R:887–902 pocket_required=False, retracement_entry=False; stop whole excursion plus one tick | MISSING pocket/entry retracement; OD one-tick padding, Dv universal sweep-extreme stop versus case-selected structure. A formed pocket alone is not an entry.
A4. November 20 chart enters short at the high sweep, 25301.75; MSS/FVG appears later (GB pp31,43; wiki/method-green-bird-failure.md:33–47 transcription) | B0/B0.1 refinement M/historical_price_scanners.py:255; R:920–949 requires NYAM-reclaim parent then MSS/FVG retracement | Dv if represented as that author's entry; valid only as separately named research refinement. Exact source fill timestamp is genuinely unknown.
A5. Opposite edge, midpoint partial, TDO/NWOG/other named liquidity; 25-point partial/BE, runners, quality sizing/no averaging down; 09–11 best window, with actual afternoon examples (GB pp23,30–39) | R:883–917; M/catalog.py:28; M/strategy_policy.py:41 | F some opposing-edge geometry; MISSING NWOG branch and case-specific target/management lifecycle. A universal 09–11 hard cutoff would also be an invention: the source has PM trades.
B. L018 calls 300-second reclaim “unprinted”: false for the explicitly cited 5m cases (GB pp19,25). Exact Asia/London bounds and universal prior-period scope remain uncertain. Winter/summer UTC-5/UTC-4 footers support New York DST (GB pp43,45,48); L038/04 blanket clock uncertainty overlooks this owned evidence. Cash-open/close ordering, missing references and prior-contract limitations are genuine measurement constraints, separately detailed under U below. Bias compatibility is specified conceptually, not an unavailable personal journal (GB pp25,35; DIS's context_direction_unevaluated ruling).
C. CENS:15–22, E/P/F/U: NYAM 2275/2048/227/0; previous_hour 11705/9035/2668/2; Asia-TDO 2513/442/2062/9; prior-day 1645/1258/387/0; week 1133/561/557/15; month 972/258/674/40; cash-open 1594/721/872/1; MSS/FVG 2023/89/1933/1. Previous-hour = 6.72 episodes and 5.19 passes per date: plausible as repeated bilateral level events, implausible as a reproduction of the selective one/two-trade narratives without a context/quality filter (GB pp33,37–40). The increase 5353→9035 passes partly fixes real late reclaims, not necessarily spurious signals.
D. Replay G01–G28; retain losing DLL day and repeated attempts, not just profitable captions.
E. A1 London: NG 2099513366326730859 explicitly requires reclaim→retest→higher low→post-open close, then midnight open/London high. ADD:11 wrongly makes that retest optional for this case; five-minute bar is chart-based, not typed in the post. A2 same post specifies Asia-high failure short without TDO, not a universal long mirror. A3 NG 2099503614372741234 explicitly gives overnight PDL reclaim long; older GB pp48,52–54 already show July/August overnight longs; widening week/month and all box branches is OD extrapolation, not six literal source rules. 04 A/green_failure.py:67–101 returns reference/window dictionaries; A/common.py:85–94,1245 lacks A1/A2/A3 execution dispatch. MISSING all three executable additions/populations; metadata/family JSON names do not implement them.
F. Three priorities: missing directional/quality admission; unimplemented London/Asia/overnight additions; altered case-specific entry/target sequencing. Verdict: not yet replicated.

GB-VWAP
A1. Break and close above BOTH Asia and London highs→retrace to VWAP→long (GB pp33–34, February 24 post) | B0 M/historical_price_scanners.py:282–317; B0.1 R:951–989 | F core order/direction. OD 5m breakout, reconstructed session bounds, native-trade VWAP reset at 18:00 (M/historical_features.py:162), completed-minute sampling; source does not prescribe these settings.
A2. The example states 30-point stop and reports 150 points, with a later reply saying 100 (GB pp33–34) | R:970–987 uses retest low minus one tick and no source-exact destination | OS/Dv for this example's stop; no basis to universalize either profit number into a fixed target. Generic stop/target policy remains unknown, not the dated example's 30-point risk.
B. Retest window is genuinely unspecified. R:958–986 censors at breakout+60m/session end; no retest produces None. D1 correctly stops overwriting breakout context, but 619 fail→unknown conversions do not imply 619 missing tapes (CENS:14; DIS D1). A complete search proves no retest in the chosen hour; whether the author would wait longer is a strategy uncertainty. Calling that one-hour window “source” (A/green_vwap_scalp.py:46–57) overstates the evidence.
C. 1127/499/0/628 (CENS:14): 44.3% confirmed under the chosen rule, 55.7% unknown. One public case cannot validate that frequency. Diagnose later-than-one-hour retests and reset/clock sensitivity before treating unknowns as lost trades. R11's 19/19 setups pool VWAP with SCALP via A/green_vwap_scalp.py:82–99; they are not 19 independently verified source_long trades.
D. G05 contains the February 24 example and its conflicting outcome captions.
E. A4 is a separate golden-pocket continuation; the raw post does not turn it into a VWAP entry (ADD:17–19; A/green_vwap_scalp.py:62–75).
F. Three priorities: arbitrary retest censoring; dated stop not reproduced; VWAP/session settings and pooled reporting. Verdict: replicated with named divergences for the narrow sequence; full author entry/exit method not established.

GB-SCALP
A. Bearish small 20–30-point scalps/no A+ and bullish discount pullbacks/smaller size (GB p40) | B0/B0.1 M/historical_process_scanners.py:60–85 | OD preselected directional swing; INVENTED last pivot pair in 06:00–09:30 or 09:00–10:00 and first 50% pullback as an entry selector. Source does not give a complete repeatable entry, stop or target. M/strategy_policy.py:6,41–46 excludes the size/management operands and labels the two case branches entry_setup despite automatic_entry_admission=None.
B. “GB p40 discloses no complete repeatable scalp entry” is genuine for those cases (U:20); absence of personal quantities/management is genuine too. A4 adds a distinct setup/location, not a universal confirmation rule for all old scalps. Its exact confirmation bar is still an operational choice (ADD:19).
C. run-1.0.1/methods/GB-SCALP.md:7–9 under implementation/reports/phase1-live/historical-measurement records 1603 bearish +1463 bullish =3066 entry setups, all lacking boundaries (U:29): 16.35% of the 18747 setup book is discretionary context counted as entries. No corresponding corrected full-history SCALP row appears in CENS; 04 pooling preserves the problem.
D. G13 holds the identifiable bearish/bullish posts; G17 the separate September 11 continuation; G27 shows the September 10 scalp chart.
E. NG 2099503614372741234: “Bullish context. Defined range. Pullback into my area.” Chart shows CPI impulse→pocket→long, but does not state first 5m close out. 04 A/green_vwap_scalp.py:62–75 only returns a band and strings; A/common.py:95–96 has no executable A4 branch. The helper gives the same [L+.50W, L+.618W] band for both directions, whereas a 50–61.8% pullback from an up-leg high is [H−.618W, H−.50W]; GB p50 left explicitly draws the long pocket below its 50% line. ADD:19 transports a down-leg convention into the long; exact drawing anchors still require care. Photo1's 29347 stop lies inside the drawn pocket area, so “beyond the far edge” is not established by that picture.
F. Three priorities: case descriptions counted as entries; A4 unwired; A4 direction/entry/stop overinterpretation. Verdict: not yet replicated.

SIRES THESIS FLOW
A1. Thesis/locations/objectives precede signal; invalidate on structural acceptance/value migration/news, use correlated ES/NQ/YM and consumed objectives; select LVN/shelf/auction extremes rather than POC chop (C1 pp3–10; AMT1 pp5–9; VP2; MAMT pp5–13; ABS pp4–8) | B0 M/historical_flow.py:126–134,272–323; B0.1 R:174–190,514–545 | Dv: “thesis_alive” is positive stop distance, a four-pivot pre-open balance stands in for auction selection, and C5 gives direction from which half contains the microbalance. Those are research constructions, not the author's thesis/invalidation process; narrow and misdirect populations.
A2. DOM: prior area→opponent effort without progress→passive defense/reload→own-side reward; absorption then reward, refreshed retest, CVD confirmation (DOM5–7; ABS pp5–12) | B0 M/historical_flow.py:27–101,165–177; B0.1 R:240–310,315–450 | F conceptual stage order partly; OD 5s chunks/120s horizon, fixed 2-tick band/no-progress and effort counts. Native BBO additions establish displayed participation, not individual hidden reserve or a full DOM wall. Fresh participants within two ticks (DOM7) and reward within three (ABS) are specific evidence, not wholly unpublished concepts.
A3. Four-stage entry: defense→≥3 ticks replenishment→opponent thins→absorber liftoff; 2–4 upticks/downticks, entry within 1–2 ticks, fresh sequence before reentry, stop for −4R (STOP pp3,9–15) | B0 M/historical_flow.py:178–186; B0.1 R:315–450; 04 A/sires.py:81–116 | OS/Dv: reward_ticks=3 is not itself measurement of three-tick replenishment; 04 reads absent passive_replenishment_ticks/passive_adds/displayed_defense_ticks, defaults to zero, then drops OFM episodes. It does not even apply its replenish filter to stop_four_stage. Native producer uses added_at/added_size/displayed_defense (R:259–305). Reproduction confirms silent episode removal; this is a binding defect, not missing market data.
A4. Footprints: diagonal 3–4× imbalance, “two or three” stacked levels (FP8 p7), current candle POC relocation and CVD/price disagreement; protected delta extreme, not simply last wick (FP8 pp4–6; FP9 pp5–7; RD pp5–9) | M/historical_flow.py:187–202,255–268; M/coverage.json assumptions.imbalance/flow | F diagonal mechanics/components; OS selecting only three stacked levels where two or three are printed; OD lower ratio/zero handling/bar size. MISSING full same-candle POC/delta-protected-level selection in the scanner; generic pivots and final snapshots are not these observations.
A5. Aggressive OFM: short-gamma context, 40-range NQ/NYAM, failed squeeze then return/replenishment and aggression working→entry/structural stop→1–3R or selected HTF destination; aggressive print MIN/MAX 30–60 in BIG, not Jumbo's 100 (BIG pp5–15; OFM pp6–14) | M/historical_flow.py:103–112,203–217; R:315–450; A/sires.py:117–128 | F skeleton failed-move sequence; OS fixed clock sampling and substituted detection; MISSING source-specific sizing/print configuration/objective selection. 04 “1R–3R” only appends width diagnostics, not target prices or execution objectives.
A6. Passive OFM can occur with tape dying, no aggressive-print requirement; clean squeeze is fast, “no retest, no false start”; balance-failure fade instead lacks reward/squeeze; defended band/microbalance continuation remains thesis-aligned (OFM p14; CONT pp10–11; BIG pp15–16; K2345 pp5–8) | M/historical_flow.py:144,218–245,326; R:514 | Dv: clean_squeeze explicitly requires pullback/absorption/continuation, the opposite of the source's no-retest case. Shared frozen first-contact/two-minute sequence bottlenecks several distinct catalysts; passive long-only reflects its illustrated case, not a proven universal prohibition on short mirrors.
A7. VWAP chosen anchor/session/swing, 1/2/2.5 deviations, especially outer bands plus context/absorption (VWAP pp5–10) | M/historical_flow.py:299–305; M/historical_features.py:162 | OS: fixed session ±1σ only; VWAP arithmetic faithful, selected anchor/deviation strategy narrower. 40% intraday profile in C3 p7 versus generic 70% AMT1 p5 must be case-bound; one universal default does not resolve both.
A8. Short/long gamma affects permission; QQQ 0DTE for NQ, walls/max pain, refresh context; KG1 is separately proprietary (GEX pp6–13; NYAM p9; K10 p6) | M/strategy_options.py:65–151; M/strategy_policy.py:23–29 | F qualitative walls/sign concepts; OD signed-OI, zero rates/dividends, nearest-expiry fallback, 09:32 mapped largest-|gamma| strike ±1 tick; MISSING max pain in historical binding. The code explicitly says inferred node, not proprietary KG1; 475 kg1_retest passes cannot certify KG1 replication.
A9. Stops first; funded fixed reward/partial variants, structural trailing, MAE/MFE review, confidence/process journal, calibrated risk and −4R stop (C2; C3; STOP pp14–15; K18 pp7–12; ANAT) | M/historical_flow.py:156–161,269; M/strategy_policy.py:6–7 | OD stop one tick beyond selected balance; MISSING executable author-specific trailing, reentry risk state and daily stop after excluding daily_r_before. Personal historical actions remain unknown, but the rules themselves are stated.
B. Recoverable unknowns: replenishment minimum, close entry distance, no-retest clean squeeze, A clock, 1–3R objective and profile/VWAP choices; L032 erroneously groups printed entry-distance/near-origin numbers with unprinted settings. Genuine unknowns: exact CVD median/band selector, discretionary thesis choice, private KG1 engine, hidden/full-depth events and personal ledgers. Missing option files/previous OI/ambiguous NQ endpoint can additionally block even the inferred gamma node (U:69–89); these do not explain away source-specific rule omissions.
C. CENS:23–33,49 E/P/F/U: DOM 2523/339/2175/9; absorption 2523/7/2514/2; four-stage 2523/14/2507/2; footprint 2523/4/2519/0; VWAP 2758/153/2604/1; aggressive OFM 2523/0/2520/3; passive 1253/0/1249/4; clean 2523/1/2512/10; balance fade 2523/2/2507/14; defended band 701/57/641/3; KG proxy 1758/475/1283/0; microbalance 4069/1355/2713/1. Zero aggressive passes over 6.7 years conflicts with BIG's occasional weekly/few-monthly opportunity description; one clean pass is particularly suspect given the inverted retest rule. R12 slice falls 141/19 episodes/setups→116/15; silent adapter drops change the denominator, not merely admission.
D. S01–S12 below include the nine July 23 attempts and undated positive/negative worked examples.
E. 04 three-tick/1–3R additions are not correctly connected as explained in A3/A5; TBR/Green Bird additions are not SIRES rules (A/sires.py:98–128).
F. Three priorities: thesis/location replaced; clean-squeeze/catalyst sequencing; 04 replenishment drops. Verdict: not yet replicated.

SAINT-AMT
A1. Fix/redraw HTF balance, assess profile: approximately 68% value; balanced/double-distribution/P/b context, continuation preference, avoid unrebalanced trend; read fast versus slow arrival (RTVP pp4–11; WIC p4; TRAP pp3–4) | B0 M/historical_auction_scanners.py:45–55; B0.1 R:1011–1024; 04 A/saint.py:28–32,72–102 | F 68% calculation; Dv arrival becomes complete-bar chronology and profile permission becomes “POC inside its own balance,” usually tautological. B0 true literals and B0.1 None do not implement the source categories.
A2. Confirm higher/lower timeframe control, 15m when needed; LTF break→same-boundary retest→current directional body/aggression before entry; no entry in unresolved free-game chop (WIC pp7–10; TRAP pp5–9) | R:1031–1079; A/saint.py:40–69 | F break/retest ordering; OD one-minute/five-minute pivot balances, two directional bars and 60-minute expiry; Dv alignment reads the LTF break already selected for that trade side, not independent HTF/LTF agreement. A fixed 09:30 start also misses the actual Asia example.
A3. Trapped buyers: redraw lower HTF balance; repeated upper failures in prior AM and PM, current break, retest and short control (TRAP pp3–9) | R:1063–1070, M/historical_auction_scanners.py:16–43 | F two prior failures as a component; OS generic disjoint failures rather than the demonstrated session/structural sequence. Source also describes an explicit long mirror; short-only branch does not cover that mirror (wiki/method-saint-amt.md:75).
A4. Failed new auction returns to original accepted value; POC rejection versus efficient passage changes destination, then far value edge; choose structural invalidation/Asia-appropriate target (AMTL pp8–12; RTVP pp5–11; TRAP pp8–9) | R:1080–1137 | Dv requires an additional older completed balance/value test for failed_auction_return; source does not make that universal. OS stop at combined extremes+tick, far-edge-only target, extra two-bar control. Missing older auction is often an invented gate, not unavailable information demanded by Saint.
B. Source resolves what arrival, alignment and profile permission mean; precise numeric speed/shape thresholds remain discretionary. They are unimplemented market stages, not unknowable concepts (WIC pp4,9; RTVP pp6,9). R:1080–1137 never binds confirm_at/ltf_balance for failed-auction/POC routes; A/saint.py:83–90 therefore cannot complete those 04 stages even with full tape. R13/NATIVE_CASES.json saint_arrival reports 28 None, zero resulting status changes. False AND unknown legitimately evaluates false; unknown does not force every episode unknown.
C. Correcting the question's premise: CENS:37–40 has 9280 episodes, 0 pass, 8308 fail, 972 unknown, NOT all verdicts unknown. Continuation 2470/0/2431/39; trapped 1230/0/1215/15; failed auction 2790/0/2251/539; POC 2790/0/2411/379. B0 passed 26+9+471+279=785 with unsupported stages. R13's 40 slice episodes all no_setup, none unknown. Zero is not an estimate of author opportunity frequency: missing stage bindings and wrong structural gates make that conclusion unavailable.
D. S13–S15 below: actual Asia short plus failed-auction/profile/control illustrations, mostly undated.
E. The 04 operational stages do not implement the named source readings; corrected missing-confirmation handling is necessary but insufficient (A/saint.py:72–102; DIS F10).
F. Three priorities: substituted arrival/profile/alignment; absent route bindings; imported older-auction requirement/NY-only scan. Verdict: not yet replicated.

MEMBER-TWO-REASONS
A1. Predefine thesis; prior reaction plus minor HVN as two reasons, or KG1 when aligned as alternative; choose ES execution with NQ context (K10 pp5–8,12–13) | B0 M/historical_auction_scanners.py:180–246; B0.1 R:1140–1210 | F reaction/node concept; INVENTED separate prior-day windows split at 12:45, latest eligible pair only, two-tick confluence and restricted lookback. Distinct evidential reasons do not require disjoint time samples; source permits other histories and KG1 alternative.
A2. Short after resistance reaction; planned return long after absorption, structural stop, spoken 1.5R; ticket/expanded plan disagree (K10 pp7–8) | R:1170–1209 | F broad side/sequence and 1.5R as the spoken variant; OD four-tick reaction/two-tick node/one-tick stop padding; MISSING case-bound plan expansion and real HTF thesis validity. L024 wrongly says no source sentence for 1.5R.
B. Exact node/reaction selection, clock, distances and private fills remain genuinely discretionary/unknown. The two-reason requirement and stated target do not. 04 A/member.py:51–80 looks for reaction_window in geometry rather than the actual reference, writes independent_hvn rather than consumed independent_minor_hvn_known, and does not reassess admission: additional validation metadata is not enforcement.
C. CENS:34–35: short 716/112/603/1; long 634/240/394/0, unchanged B0.1; R14 slice 2/2 setups. Source offers two teaching trades, no complete frequency distribution; 352 passes cannot be disproved by that sample, but arbitrary time split likely suppresses valid confluence.
D. S16–S17, including the failed shorts against demand, not just the two successful illustrations.
E. No A1–A4/Judas addition applies; 04 independence check remains inadequately bound as above.
F. Three priorities: invented temporal separation; incomplete thesis/alternative confluence; ineffective 04 validation. Verdict: replicated with named divergences as an operational reaction/HVN model, not established as the author's full method.

KEANI OPEN ABOVE VALUE
A1. Current A TPO entirely above prior value, observe around 10:00; reject developing POC OR prior VAH, develop value higher (AVG pp21–22; TPO p3 says A=09:30–10:00) | B0 M/historical_auction_scanners.py:249–277 incorrectly tests developing VAL; B0.1 R:1211–1282 corrects POC/prior VAH | F corrected level choice and completed A clock; OS volume-profile implementation of a TPO-described setup and strict developing-VAL rise are additional choices, not source-complete identity.
A2. Aggressive break of CURRENT VAH→freeze actual imbalance→retest same band with DOM defense→long toward prechosen HTF objective (AVG p22) | R:1235–1281 | F broad order/band freeze; OD 1m bars, 3×/three-row imbalance, two-minute flow; INVENTED hard 11:00 cutoff and 60-minute retest expiry; Dv fallback target A-high+A-width instead of source-selected HTF objective. One-tick stop beyond imbalance is an operational structural-risk choice.
B. Source resolves A duration, POC/prior-VAH rejection and same imbalance retest; L021's unlocated 10:00 clock is a finding. Source leaves precise imbalance/DOM thresholds, exact “around 10” tolerance and generic stop/target selector unspecified. Empty A-period data is different (U:29,90). A/keani.py applies bookkeeping/operational checks, not recovery of those source parameters.
C. CENS:36: B0 1695/6/1669/20→B0.1 1695/39/1630/26; correction adds and removes candidates, not just +33 identical setups. 39/1695=2.3% of all A observations is not intrinsically implausible for a restrictive gap/value setup. Need the fully-above-A eligible denominator and stage funnel before claiming rarity; R15's 0 slice setups is not a contradiction.
D. S18: undated long example, date/instrument not established; no dated source fill to replay yet.
E. No Green Bird/Judas additions apply; 04 changed-reference contacts still lack native family confirmation (A/common.py:816).
F. Three priorities: B0 wrong reference (repaired); added timing/shape constraints; invented objective. Verdict: replicated with named divergences; author-example reproduction not established.

REFILL-STUDY
A1. Aggressive clusters create zones; after departure record every later touch using only prior-known memory/construction/location/flow; roughly 20 features and model selection, not unconditional touch trading (REF pp5–9) | B0 M/historical_process_scanners.py:22–57; B0.1 R:1284–1319 | F causal record concept; OD min100×two prints/120s/two-tick width/four-tick departure/15m response. Source's zone/normalization/model details are incomplete, but Jumbo NY100/London75 cannot supply another author's zone definition (L004; FIND pp9–10).
A2. Printed execution: 12 ticks inside, stop 32/target 96, cancel30 minutes, one position, 1-tick round-trip cost and 1-tick stop slippage (REF p12) | generic M objects/order lifecycle and supplied_selected_order contract; historical touch path R:1284–1319, 04 A/processes.py:59–159 | F contract parameters where supplied; MISSING connected source-grade-selected historical execution. These numbers are not genuinely unknown and should not be replaced by the touch-response horizon.
A3. 04 uses ≥40-print filter, 5s clusters, ≥80 size or ≥2 prints, width2 ticks/depart4 (A/processes.py:22–29,59–100) | OD new zone algorithm, still not recovered source formula. A/processes.py:149–154 stores departure_at_ns equal to touch_at_ns; actual departure occurs earlier. Reproduction with formed=1/departure=2/touch=3 records 3/3: Dv audit chronology, not proof the scan used a future touch to form the zone.
B. Genuine unknowns: exact 20-feature definitions, trained model, normalization, hold-label boundaries and individual selected-order ledger. Source resolves chronology, execution bracket/costs/cancel, study dates/counts and score meaning: AUC .63 overall, .51 scrambled placebo, .54 FLOW-ONLY, not .54 overall (REF pp3,9,20). Model-selection absence cannot be cured by a matching aggregate hold rate.
C. Source 41152 touches/235 regular sessions, Dec2024–Nov 2025 ≈175/session (REF p8). Prior replay 824 touches on only 15 of 260 sessions,123 traded (DIS F-REFILL-POP:76); CENS:51 has 1666 touch records across 1742 dates, not 1666 entries. R16's new 1072 touches/nine dates≈119/session is closer scale but different dates/definition; it does not reconcile the registered 235-session population. Full printed replay was explicitly deferred (DIS final 04 ruling).
D. S19: study interval and undated touch/entry illustrations; no individual author fill ledger.
E. 04 “re-derived” zone formation is OD; its reported engineering slice and stand_in=False (A/processes.py:109) are not evidence of exact source recovery.
F. Three priorities: unreconciled zone population; source grading/execution unconnected; incorrect departure timestamps. Verdict: not yet replicated.

JETBUNDLE AUCTION STATES
A1. B=two-sided balance/revisits; A=high aggression+little displacement+opposite book holds/refills; D=effective directional discovery; E=effort then replenishment fails; W=cancels dominate (MATH pp3–11) | B0/B0.1 M/strategy_context.py:46–85; M/historical_process_scanners.py:174–222 | F qualitative components; OD 120s windows, 1.5 effort ratio, .2/.6 response efficiencies, .25 refill cutoff. Displayed L1 removal-minus-execution is an estimate, not observed full-depth cancellation/hidden inventory.
A2. Observe state sequences/transitions, not a standalone trade signal (MATH pp10–11) | M/historical_process_scanners.py:174–222 compares 09:28–09:30 with 09:30–09:32; M/strategy_policy.py:44 | F non-entry scope; Dv one daily sample instead of continuous author state transitions; MISSING source-comparable transition census. No source clock/entry/stop/target policy is published for this engine; 09:30 sample is INVENTED scheduling, not a missing author's entry.
B. Classifier thresholds/full-depth cancels are genuine unknown/input limitations. State meanings are explicit, not unpublished. Empty two-minute windows legitimately block observations (U:68); a supplied source transition ledger is unavailable, but our own classified transitions could be computed and labelled as ours.
C. No JETBUNDLE row in the 39-branch CENS; U:68 reports 10 sampled unavailable cases with truly empty windows. Source 20,000 AAPL ten-level events and D→D84%/D→A12% illustration (MATH pp10–11) are not NQ daily-entry base rates; zero entry setups is correct scope, not failed replication evidence.
D. S20: AAPL transition study, undated; not replayable from NQ alone.
E. 04 A/processes.py retains the alphabet/process scope, not a newly verified state-transition implementation; no trading additions apply.
F. Three priorities: L1 proxy versus full participation; arbitrary classification thresholds; single-window sampling. Verdict: replicated with named divergences as a labelled observational proxy; source state engine not yet replicated exactly.

STOIC DATA ENGINE
A. Define trading rules first→collect every observation uniformly→compare winners/losers as aggregates→revise from evidence; macro cycle uses trend strength, historical comparisons, C-scores and dispersion (DATA pp3–6) | B0/B0.1 M/historical_process_scanners.py:144–170; M/strategy_context.py:88–101 | F research-process contract; OD macro model of twelve prior first releases, equal-weight payroll/CPI signed z-scores, explicitly not source C-score. MISSING source-complete cycle/credit/leverage/housing/valuation recipe; it is not published precisely enough to recover. No source entry clock/bracket exists.
B. Actual dated process records absent and collection review emitted after job are genuine chronology/record limitations, not undisclosed instructions to collect/compare (U:18–20). C-score formula/indicator universe and cycle decision thresholds genuinely unspecified (DATA pp5–6); label the implemented proxy accordingly.
C. CENS:52 has zero macro episodes; U counts3484 later-review labels. Neither says there were zero possible market trades: this is a research process requiring records, outside setup scope (M/strategy_policy.py:44).
D. S21: undated bubble narrative, no identifiable instrument/date/price trade.
E. No entry additions apply; 04 keeps process scope (A/common.py:115).
F. Three priorities: source research contract present; proprietary macro recipe absent; dated process evidence absent. Verdict: replicated with named divergences for process validation, not a replicated macro trading strategy.

STOIC ASYMMETRIC COMPOUNDING
A1. Existing validated strategy, ≥100 observations, known win rate/average RR/Monte Carlo loss streak, base risk≤1% (DATA p8) | B0/B0.1 M/historical_process_scanners.py:225–243; M/method_slices/m12.py:24–117; printed_ladder via M/catalog.py:69 | F eligibility/chronology contract, conditional on supplied genuine records. No price entry, session clock, stop distance or target price is created by this overlay.
A2. Printed fixed-initial-unit ladder: first risk 1 for 3R; after its win risk 1+3=4 for 3R; second win adds12, total 15; loss after first win leaves−1; reset to1 (DATA p7) | M/historical_process_scanners.py:225–243; M/method_slices/m12.py:109–130 | F printed arithmetic. The heading “two trade winning streak” conflicts with escalation after the FIRST win; code correctly preserves the explicit ladder, not an invented two-win activation or continuously rebased equity formula.
B. Source resolves the ladder and eligibility; unavailable personal validation/trade/risk ledger is genuine (U:19). Other outcome transitions, generic account denominator outside this illustration and actual Monte Carlo construction remain unspecified. An unavailable ledger does not mean the 1→4→1 rule is unknown.
C. Zero entry setups and 5226 risk-ledger limitations are expected for three non-entry branches over 1742 dates (U:19; M/strategy_policy.py:42–43). No comparison against source's illustrative “8–10% in2–4 trades” can establish a market frequency or expected return (DATA pp7–8).
D. S22: undated worked two-trade sequence, arithmetic fixture only.
E. No A1–A4/Judas addition applies (A/common.py:116).
F. Three priorities: printed ladder faithful; genuine eligibility records absent; generic overlay unresolved. Verdict: replicated faithfully within the explicit printed-ladder contract; a complete live compounding system is not established.

SHARED UNKNOWN / DATA-UNAVAILABLE CROSSWALK (supplements each B)
U:9–17,26–29: candidate_status:data_unavailable/research_verdict unknown/unavailable_candidates describe undecidable operands, not missing raw files; author_exact_verdict is a constant unknown even for fully evaluated candidates (M/historical_assembly.py:85–96). completed_search, observed_search_with_input_limitations, personal_execution_out_of_scope and scheduled_closure are search/scope labels, not four author rules. U's421 unknowns belong to old57-branch B0; CENS's39-branch B0.1 totals are a different population.
U:18–21,38–44: actual dated process/source records 12194, risk ledger5226, later collection review3484, unpublished scalp entry 1742, and missing dated P-zones35 mix genuine private-record absence with reconstruction limitations. Sources resolve process sequence, risk ladder and P-zone settings, not historical personal actions or proprietary zone bounds. The old scalp trigger remains genuinely absent; its invented scanner admission is a separate defect.
U:16–17,55–67: unknown_current_minutes/current-prefix-unknown:16938/17037 distinct minutes have no raw rows per the retained audit;96 contain owned-contract trades at ownership boundaries;3 have quotes without trades. No reader failure was found by that audit. The scripts/sample support that scoped conclusion, not source-fidelity certification; I did not rerun the 17,037-minute raw scan.
U:22–25,81–91: same_contract_prior_scope_unknown1812 day-rows includes1355 prior-month GB rows;14/18 sampled had other-contract trading,4 no rows. “calendar_unverified”544 means missing dated exchange schedule, even on trading days. Empty formation435 rows, A-period47, session_reference_missing21 are observed-window/contract constraints; sources define windows but cannot manufacture trades in them. “No distinct older auction”90 is algorithmic selection and, for Saint, partly an unsupported gate (R:1095), not generally missing raw history.
U:24,69–89: KG1/key-gamma unavailable107: sampled missing QQQ quotes9/14, plus ambiguous same-nanosecond endpoint/prior-OI problems despite files existing. Proprietary KG1 remains unknown even on successful proxy days. Cash_open_order_unknown58 and earlier-potential-breakout-close unknown34+4 reflect missing ordering/failed vendor reconciliation, not absent published entry definitions; GB2020-04-17 last batch8817.50/.75 and SIRES2020-02-27 last batch8659.75/8660 exemplify real ambiguity.
U:29–35: nonpositive_formation_width22 is invalid geometry, not author discretion; one bar-contact-without-exact-band-execution is a selected measurement requirement. boundaries_not_defined3066 is the SCALP classification defect, not a tape hole; measurement_reference_unavailable=0. Source quotations cannot resolve indistinguishable same-timestamp execution ordering.
U:35–36,95–116: incomplete future horizons2768/74988 comprise2753 beyond 16:00 and 15 thin-data horizons; unresolved boundary future90/18747 is censoring, not an unknown entry rule. Zero unknown minutes means enumerated owned archive, not continuous market/feed completeness: early-close/expired-contract silent minutes sometimes remain “complete.” Month-seam rules exclude206 otherwise measured setups from the eligible denominator without changing measured prices.
Reconstruction audit findings, in addition to family rows: L018 five-minute close, L021 A-end10:00, L024 target 1.5R, L030 printed3-minute option, L0321–2/3-tick distances, L039 clock evidence all require qualification against the cited raw pages. L014's “printed-formula-recovered” VWAP dispersion is arithmetic/other-Pine corroboration, not evidence the source publishes that exact anchor/band generator. SA also calls the three-row stack unprinted, although FP8 p7 prints “two or three.” Conversely, actual source-specific unknowns must not be “resolved” by unrelated indicator code (SA:107–142; VWAP p8).

04 FAMILY RECEIPTS — reproduced claims, not my source-fidelity endorsement. n is reported setups unless contacts explicitly stated; all are nine-date engineering slices, not full history (each RNN/FAMILY_REPORT.md:3–23).
PHASE: family | variant | n | faithful_disagreements | status | report path
JJ-TBR | B0 / B0.1 | 21 /16 | not claimed | engineering slice | R09/FAMILY_REPORT.md
GB-FAIL | B0 / B0.1 | 36 /65 | not claimed | engineering slice | R10/FAMILY_REPORT.md
GB-VWAP label (actually VWAP+SCALP) | B0 / B0.1 | 19 /19 | not claimed | pooled engineering slice | R11/FAMILY_REPORT.md; A/green_vwap_scalp.py:82
SIRES | B0 / B0.1+04 | 19 /15 | not claimed | engineering slice | R12/FAMILY_REPORT.md
SAINT-AMT | B0 / B0.1+04 | 0 /0 | not claimed | 40 episodes each | R13/FAMILY_REPORT.md; NATIVE_CASES.json.cases
MEMBER-TWO-REASONS | B0 / B0.1+04 | 2 /2 | not claimed | engineering slice | R14/FAMILY_REPORT.md
KEANI-OPEN-ABOVE-VALUE | B0 / B0.1+04 | 0 /0 | not claimed | engineering slice | R15/FAMILY_REPORT.md
REFILL-STUDY | B0 / B0.1 | 0 /0 entry setups | not claimed | 1072 newly formed touch observations separately | R16/FAMILY_REPORT.md; R16/PROCESS_OBSERVATIONS.json:73
audit: family | id | verdict | fixture | leakage | proxy-as-faithful | notes
JJ-TBR | P15-09 | reported implemented_verified | reported pass | reported 0 | reported 0 | R09/FAMILY_REPORT.md:17–21; empty delta delegates/changed-axis own population; not source-fidelity certification.
GB-FAIL | P15-10 | reported implemented_verified | reported pass | reported 0 | reported 0 | R10/FAMILY_REPORT.md:17–21; empty delta delegates/changed-axis own population; not source-fidelity certification.
GB-VWAP/SCALP | P15-11 | reported implemented_verified | reported pass | reported 0 | reported 0 | R11/FAMILY_REPORT.md:17–21; empty delta delegates/changed-axis own population; not source-fidelity certification.
SIRES | P15-12 | reported implemented_verified | reported pass | reported 0 | reported 0 | R12/FAMILY_REPORT.md:17–21; empty delta delegates/changed-axis own population; not source-fidelity certification.
SAINT-AMT | P15-13 | reported implemented_verified | reported pass | reported 0 | reported 0 | R13/FAMILY_REPORT.md:17–21; empty delta delegates/changed-axis own population; not source-fidelity certification.
MEMBER-TWO-REASONS | P15-14 | reported implemented_verified | reported pass | reported 0 | reported 0 | R14/FAMILY_REPORT.md:17–21; empty delta delegates/changed-axis own population; not source-fidelity certification.
KEANI-OPEN-ABOVE-VALUE | P15-15 | reported implemented_verified | reported pass | reported 0 | reported 0 | R15/FAMILY_REPORT.md:17–21; empty delta delegates/changed-axis own population; not source-fidelity certification.
REFILL-STUDY | P15-16 | reported implemented_verified | reported pass | reported 0 | reported 0 | R16/FAMILY_REPORT.md:17–21; empty delta delegates/changed-axis own population; not source-fidelity certification.
All eight report changed-formation n=1; changed-reference n=1/5/11/0/0/0/5/0 respectively. Retained R09–R15/NATIVE_CASES.json.changed_axis.new_contact_records are unknown, not setups; A/common.py:748–787,816–825 never supplies native source_confirmation. A dwell-dedup/mirror fixture alone cannot verify family-rule evaluation (DIS F9).

RANKED FINDINGS (severity concerns Strategy Book base rates; demonstrate by tests/replays described, not by asserting source profit equals model profit)
F01 HIGH | M/strategy_policy.py:6,41; M/historical_process_scanners.py:60 | GB p40 | Discretionary scalp descriptions become3066 entry setups after excluding their remaining process operands. Demonstrate observation_scope for both branches plus all boundaries_not_defined rows; remove them from entry scope to quantify16.35% book impact.
F02 HIGH | M/historical_flow.py:103,225; R:315 | CONT p11 | clean_squeeze requires the retest that its source explicitly excludes. Replay a fast rewarded breakout with no retest and the author's clean example; compare admission/funnel for 2523 episodes.
F03 HIGH | A/sires.py:81–116; R:259–305 | STOP pp3,10 | 04 reads nonexistent replenishment fields and silently deletes OFM candidates. Actual-function field-shape reproduction returns 0 ticks/0 episodes; replay identical native episode before/after transform and require an explicit retained verdict.
F04 HIGH | A/saint.py:28,51,72; R:1017,1080 | WIC pp4,9; RTVP pp6,9 | Arrival, profile and alignment stages are substituted, with missing bindings on two routes. Contrast fast/slow and balanced/trending source cases having identical POC bounds; inspect28 missing confirmations and the 972 census unknowns separately from 8308 fails.
F05 HIGH | R:1095–1124 | AMTL pp8–12 | Saint's failed-auction return requires an extra older-auction exploration absent from the universal source sequence. Replay new-value failure→original value return without a second old profile; inspect failures/omissions before altering any detector.
F06 HIGH | A/green_failure.py:67–101; A/green_vwap_scalp.py:62–75; A/common.py:85–96,1245 | NG posts2099513366326730859/2099503614372741234 | A1–A4 are named/helpers rather than executable source additions. Route each named branch and demand real stage/episode records; current registry/helper output cannot supply them, even with synthetic complete market data.
F07 HIGH | R:890–902; M/historical_price_scanners.py:189 | GB pp25,33,35,37–40 | Existence of pre-open context substitutes for directional/quality selection, allowing9035 previous-hour passes. Hold level/confirmation fixed and reverse recorded bias; current rule remains admitted; replay both Aug 27 attempts and inspect per-day multiplicity.
F08 HIGH | R:52,647–676 | TBR p12 versus p21; JR pp11,23 | A single-extended 10:00 restriction is applied to other JJ branches, removing906 extension episodes. Replay a confirmed13:00 1.33/1.66 reaction and source PM examples against B0/B0.1.
F09 HIGH | M/historical_flow.py:126,272; R:174,514 | C1; CONT pp3–9; BIG pp5–15 | Price-balance/stop-distance proxies replace SIRES thesis/location lifecycle. Replay identical local flow under live versus invalidated HTF thesis; compare zero aggressive and one clean pass with the source's stated occasional opportunities.
F10 HIGH | R:1284; A/processes.py:22,59 | REF pp5–12 | Refill zone selection/grading/execution has not reproduced the source population. Use the committed tolerance and original Dec2024–Nov 2025 period; reconcile41152/235 before interpreting hold/R agreement; current 824/15 and 1072/nine are different populations.
F11 MEDIUM | M/historical_price_scanners.py:25; R:547 | TBR pp25–29 | Mandatory first-touch three-minute OB excludes stated confirmation/entry alternatives. Replay 2m and 5m OB, rejection-block and later fresh confirmation variants with identical source context.
F12 MEDIUM | A/common.py:748,816,1075 | TBR pp12–15; DIS F9 | Changed geometry enumerates generic contacts without family confirmation, producing unknowns as the claimed new population. Pass a complete native-shaped contact without source_confirmation (receipt returns unknown); then prove actual family evaluation on passing and failing source cases.
F13 MEDIUM | R:958–986; A/green_vwap_scalp.py:46 | GB pp33–34 | An unpublished one-hour retest expiry drives628 VWAP unknowns, masking measured within-window absence as unresolved strategy admission. Separate no-retest-in-observed-window from missing coverage and replay later retests/reset alternatives.
F14 MEDIUM | ADD:11,19,27; A/green_vwap_scalp.py:62 | NG two posts/photos | Source-specific retest is made optional and A4's long pocket/stop/“exit” are overinterpreted. Preserve literal London sequence; mirror an impulse; compare drawn position/target markers with caption, without calling planned targets realized exits.
F15 MEDIUM | R:1147–1175; A/member.py:51–80 | K10 pp5–8 | Invented12:45 split narrows two-reason selection and 04 validation writes unconsumed fields. Supply independent reaction/HVN evidence from overlapping time windows and verify current rejection/binding.
F16 MEDIUM | R:1211–1282 | AVG pp21–22 | Keani's repaired level still carries unpublished11:00/60m gates and a synthetic objective. Replay otherwise identical10:59/11:01 breaks and the actual imbalance/HTF-objective example; report funnel sensitivity.
F17 MEDIUM | M/strategy_options.py:140–151; M/strategy_pzones.py:43–74 | NYAM p9; JR pp16–18,55 | KG1 and P-zone passes belong to disclosed inferred engines, not recovered proprietary formulas. Compare report labels/inputs against literal source configuration; never use475/305 proxy passes as source-fidelity evidence.
F19 MEDIUM | L018, L021, L024, L030, L032; SA:111–129 | GB pp19,25; TPO p3; K10 pp7–8; TBR p27; STOP pp9–10 | The reconstruction record calls several printed rules unlocated/unprinted. Reopen cited pages and compare each literal with bound operands; exact thresholds being printed does not certify the rest of their detector.
F18 LOW | L038–L044; A/green_failure.py:33 | GB p43 November 20 UTC-5 versus pp45,48/NG summer UTC-4; TBR p6/SS p8 | Blanket unverified-clock labels discard owned seasonal-clock evidence; current New York conversion is supported for these GB charts. Compare both dated footers and distinguish unrelated fixed-GMT Pine scripts; no present pass-count change is demonstrated.
F20 LOW | A/processes.py:149–154 | REF pp5–7 | Refill departure timestamp is overwritten with touch timestamp. Actual-function replay of events1,2,3 returns departure3/touch3; assert formed<departure<touch and correct provenance before chronological audits.

CONSOLIDATED AUTHOR-EXAMPLE INDEX (D for all strategies)
Notation: Y=date falls within NQ tape span, not proof of complete event coverage; N=outside; P=partly covered endpoint; ?=trading date unknown. Raw tape ends2026-09-03 06:09UTC/02:09ET, so September3 RTH and September8–14 are unavailable (U:57–63). NQ-context means Nasdaq author context but exact traded contract is unestablished; MNQ/ES/GC/AAPL examples need that instrument's tape for execution replay. “Post” dates are not silently treated as session dates. Unless a price is printed below, numeric level/actual fill is unstated; “chart only” also means direction/outcome cannot be recovered from text. Repeated XF/JR copies and duplicate photos are one example; source-case synthetic mirrors/control dates are not author trades.
J01 | TBR pp9,10,13,14,17 (image-only; rely wiki/method-jumbo-tbr.md), pp27–29 | undated ?; instrument? | separate range/open/purged illustrations and long full-C2 OB/rejection-block illustrations; numeric levels/outcomes not established. M/source_cases_v2.json JJ-range-control-2026-02-24 and short mirror are explicitly inferred controls, excluded from author-date replay.
J02 | JR p71 |2025-01-28 Y, NQ-context |09:40 Judas exhaustion→RTH high/1.33–1.66; successful day described; Jan30 post p70 points back to Tuesday. JR pp27–29 |2025-04-01/02 post Y| first range-presentation video, illustrated session/date/side/outcome?; not a fabricated April2 fill.
J03 | JR pp68–69 |2025-05-23 Y, NQ-context| London-high absorption short? (direction not explicit in caption), +78 closed before 208/225 available; missing-picture imbalance post separately noted. JR p68 |2025-05-29 Y| two trades/one mini from Spain,9–12-minute average, four GsIT charts; side/levels/result? beyond caption.
J04 | JR pp24–26 |2025-09-09 Y, NQ-context| long extension+RTH average lows toward equal highs,+84 with 1BE/1L; unfinished-setup post separate. JR p23 |2025-09-12 Y|1.33/1.66 framed HOD/LOD until16:00, both-side level illustration, realized outcome unstated. JR p22 |2025-09-24 Y| three profile/context charts, not three identified fills.
J05 | JR p21 |2025-10-01 Y, NQ-context| range-open→09:40–09:50 reaction, result?; pp65–67 |2025-10-03 Y, NQ/ES/YM charts| “easiest” sequence, two charts, side/fills?; p20 |2025-10-13 Y, NQ-context| both extremes taken→full09:40 reversal,100+ available; pp63–64 same post's four London examples lack individual dates; p19 |2025-10-14 Y| “beautiful,” chart-only geometry/result.
J06 | JR pp60–62 |2025-11-04 post Y, NQ/GC/YM| settings/chart examples, individual sessions/fills?; p59 |2025-11-10 Y, NQ-context| missed short then 9am P-zone long;105s video absent; p58 |2025-11-16 Y, GC| Sunday18:00 P-zone,+23 points; NQ date overlap does not reproduce GC. p57 |2025-11-18 Y, NQ-context|1.33/1.66 reversal→London high; p57 Nov 21 multiasset promotional charts, individual trades?; p56 Nov 25 projection arithmetic, not identified fill.
J07 | JR pp15–18,55 |2025-12-28/30 post Y, NQ1! settings| SDRange/P-zone video frames; illustrated trading dates?; p55 |2025-12-30 Y, NQ-context| early short BE, then after 09:40 long→London/Asia highs. Source settings are evidence, not additional dated trades.
J08 | JR pp53–54 |2026-01-02 Y, NQ-context| early P-zone-low fade loss, range-open/full09:40–09:50 reversal;10am P-zone→London low. pp51–52 |2026-01-09 Y| reversal→EQ→10am expansion/daily high, exit front-run; video not retained as stills. p51 |2026-01-14 Y| midpoint retrace down toward Jan4 gap; exact realized result?.
J09 | JR p14 |2026-02-23 Y, NQ-context| order-flow6–9 chart, result?; pp13–14 |2026-02-24 Y|+155, two losses; p51 same date London setup chart, result? (XF p26 duplicate). p12 |2026-04-21 Y| platform-change trading chart, side/levels/outcome?.
J10 | JR p11 |2026-05-15 Y, NQ-context| afternoon+80; p10 |2026-05-19 Y| “cinema,” chart-only; p9 |2026-05-20 Y| mean reversion, two stops/two longs/one short, net result not quantified.
J11 | JR p50/XF p25 |2026-06-05 Y, NQ-context| London1.33–1.66 exhaustion long, outcome?; JR pp48–49 |2026-06-08 Y| wide1.2% range/midpoint absorption, stats74% single/60.4% midpoint are context, not filled-trade wins.
J12 | JR pp6–8 |2026-06-09 Y, NQ-context| execution chart, two-micro “enough” result chart, aggressive buyers fail high in09:40–09:50; quantities/individual profits not fully stated. p5 |2026-06-10 Y| “well” result/quote of June 9 case. p4 |2026-06-12 Y| recoup/profile chart, detailed fill result?.
J13 | JR pp46–47 |2026-06-11/12 Y, NQ-context| June 12 post describes yesterday's6–9 high→low short and lunchtime giveback; today's London3/3,+354. Treat yesterday/today separately, not two June 12 sessions.
J14 | JR pp44–45 |2026-07-06 Y, NQ-context| exhaustion/09–12 boundaries/evaluation accounts, result?; p43 |2026-07-07 Y| abandon mean reversion, PM recovery at prior-week low; p42 |2026-07-08 Y| someone else's10am P-zone short cited positively, not established as Jumbo's fill.
J15 | JR p42 |2026-07-10 Y, NQ-context| in-value mean reversion,10:30 losses/roundtrips but green; p41 |2026-07-16 Y|+143 first 20min, missed midpoint long; p40 |2026-07-21 Y|6–9 OR midpoint,50–70-point winners and BE; p39 |2026-07-23 Y|1000-lot aggression/dunk,664s chart, realized points?.
J16 | JR p38 |2026-07-27 Y, NQ-context| single break/A-mid,+124; pp34–37 |2026-07-28 Y| open/value chart and projection reversal; discarded MR,+138. p34 |2026-08-04 Y|09:30 P-zone example, result?; Aug 26 p34 GC08:20/CL09 clocks are settings examples, not identified trades.
J17 | JR p33 |2026-08-27 Y, NQ-context| large-range/single-break45% statistics and chart, no specific fill; pp32–33 |2026-08-28 Y| overnight double-break/value context and result chart, numeric outcome?. pp30–31 |2026-09-01 Y|−60/poor BE then flip to buy retrace; p3 |2026-09-02 Y| EVRange↔EQ scalps both ways, two falling-knife losses, worked after 10.
J18 | SS pp2–12; FIND/XF settings/geometry figures; JR pp16–18,27–28,53–62 | undated chart instances ? unless associated above | indicator/settings demonstrations, not additional proven executions; old embedded images/video-only content relies on wiki/source-catalog.md:51 and source-case transcriptions. No exact prices/date are asserted where the retained textual evidence supplies none.
G01 | GB pp28–30 |2025-06-26 Y, NQ-context| short 5R, fleet 20189;2025-09-18 Y|fleet 40k, side/level?; Sep 19 Y|PDH failure short→TDO; Sep 26 03:13UTC post Y|describes Sep 25 NYAM200-point long, done10:30; Sep 28 post Y|Friday100-point long (likelySep26, unconfirmed); Sep 29 Y|NYAM150+ short.
G02 | GB p30 |2025-11-19 04:23UTC post Y, NQ-context| OR-low reclaim long 250→previous-hour high/TDO, then short 140–150; session possiblyNov18. Same Nov 19 p30 |previous-week-low reclaim long→PDH; p31 |AM350-point long and PM400-point long, range-low→high; separate described setups, overlapping execution identity unresolved.
G03 | GB pp31,43 (image detail via wiki/method-green-bird-failure.md:34) |2025-11-20 Y, MNQZ2025| short 25301.75 at 9–10 high sweep; later MSS/FVG,250+ points reported; exact fill clock unknown. GB p31 |2025-11-21 Y, NQ-context| long 400+ and short 100+; Nov 24 Y|unconfirmed shorts, red/DLL24800, negative example.
G04 | GB p32 |2025-11-25 Y, NQ-context| Asia short 100+; Nov 27 01:56UTC post Y|previous-week-high failure short 50→9–10 high, stop PWH; likelyNov26 session, not established. GB p32 |2026-02-17 Y|9–10 low reclaim long→midpoint→high during9–11.
G05 | GB p33 |2026-02-23 Y, NQ-context| previous-month-low sweep/instant rejection short→TDO100; laterPDL sweep/reclaim long 100 then runnerBE. GB pp33–34 |2026-02-24 Y, instrument not established| BOTH Asia/London breakout→VWAP retrace long,30-point stop,150 stated; Feb25 reply says100. GB p34 Feb25 Y|one stop, avoids NVDA, side/level?.
G06 | GB p34 |2026-06-12 Y, NQ-context| TDO/London-high targets, side/outcome?; Jun22 Y|previous-hour-low/London-low/TDO liquidity targets hit, short path. GB p35 |2026-07-15 Y|25 DLLs/recovery narrative, individual dates/levels?; not 25 identified replay trades.
G07 | GB p37 |2026-08-03 post Y, NQ-context| Sunday18:00 fresh NWOG short 28665; “same as last Monday” adds July27 described setup, exact clock/result?; p35 Aug 10 Y|100+ points, bodies/wicks context, side/level?.
G08 | GB p35 |2026-08-12 Y, NQ-context| Asia long 260/zero drawdown held through CPI; NYAM failed-low long; HTF bullish golden-pocket/hour-low reclaim long, stop below; these posts may show the same NYAM position, not necessarily three extra trades.
G09 | GB p36 |2026-08-13 Y, NQ-context| one100-point trade, fleet 41k; Aug 17 Y|NY-open/TDO failure short→NWOG,2–4MNQ closed; Aug 20 Y|choppy repeated shorts, individual entries/results?; p37 Aug 27 Y|previous-hour-high failure short 50 then runnerstop, repeat100; ticket19.25 stop/9.66R drawing, partialPDH.
G10 | GB p38 |2026-08-28 Y, NQ-context| wait for 9–10 completion, high+PDH failure short→low, runnerBE. GB pp23–26 |2026-09-01 Y|NYAM down-leg50–61.8 pocket/PDL sweep/5m failure short, stop abovePDL or swinghigh, delayed retracement entry; numeric stop≈49.75 and drawingRR≈4.2 are case geometry, not universal.
G11 | GB p40 |2026-09-01 Y, NQ-context| overnight-selloff long 100, fleet 31k by10:30; distinct09:30 below-open manipulation/reclaim/discount long, stop lows; relation to p25 short must be reconstructed, not merged into one directional trade.
G12 | GB pp26–28 |2026-09-03 P, NQ-context| Asia-high sweep/close belowTDO short→Asia low; only tape before 02:09ET covered, actual trade time must be checked. GB pp16–20 |2026-09-08 N|Asia-high/5m belowTDO short 100+, fleet 81k; p22 same date N|after 10 NYAM-low+PDL reclaim long→box high, partial25/BE.
G13 | GB pp20–21 |2026-09-09 N, NQ-context| NYAM failure short→PDL. GB p40/post2095257805242446135 |2026-09-02 post Y, NQ-context|bearish20–30 scalps, small/noA+, individual fills unknown; post2098075540607410229 |2026-09-10 post N|bullish NYAM discount scalps, smaller, noA+, fleet 45k; exact trading dates inferred from current-session captions, not filled ledgers.
G14 | NG post2099513366326730859,2026-09-14 14:59UTC, photos1–4 |2026-09-14 N, MNQU2026| London-low preopen sweep→reclaim/retest/higher low→postopen long; position28903.75, drawn target 29037.00, stop drawing 28875.25; author says100 long, TDO thenLondon high. A plotted target is not proven realized29037 exit; ADD:27 overstates it.
G15 | same NG post/photos2–3 |2026-09-14 N, MNQU2026| Asia-high failure short; position29081.75 versus drawing 29081.50, stop 29098.75, target order28890.50/drawing 28890.25; author says another100 short, screenshot still open. Alternate ticket29074.25 with buy limits 28952/28843.25 may be another account, not a proven additional setup; fleet 28657.10 photo4 is account aggregate.
G16 | NG post2099503614372741234,2026-09-14 14:20UTC, photo2 |2026-09-11 N, MNQU2026| overnightPDL≈29040 sweep/reclaim long, position≈29059.50/stop 29029, target 29324.25 drawing; author calls this first long. Date and CPI description are author's, not independently verified release-calendar facts.
G17 | same NG post/photos1–3 |2026-09-11 N, MNQU2026| CPI impulse→NY pocket continuation long; drawing 29382.00/stop 29347, limits 29494.50/29521.75; position marker29381.75, alternate ticket29382.25 with 29469.75/29496.75/29528.25 limits. These are displayed entry/order variants, not evidence all targets filled; photo shows open gain, text says “hit the continuation long.”
G18 | GB p43 left |undated ?, MNQZ2025| PWH/PDH/TDO and NY-range chart, current 25315.75, side/result not shown; p43 right supplements G03 with buy-limit25112.50, TDO25189.25 and UTC-5 footer. GB p44 left |2025-11-26 Y, MNQ account card|+22125, not a separate identified fill; right |undated ?, MNQM26| long 26336.75, ladder sell limits 26457–26684.75, open profit, entry basis unspecified.
G19 | GB p45 left |2026-04-23 Y, MNQM2026,15m| NY-high sweep short 27116.25, stop 27146.50, target 26827.25 (289-point drawing,9.55R); open profit318.50, current 26956, not a completed target fill. Right |2026-04-28 Y, MNQM2026,1m| NY range with multiple long/short execution arrows, day+13410.40/open 0; exact individual entries/results unlabelled.
G20 | GB p46 left |undated ?, MNQM2026,2m| range-high/TDO/PWH reversals, short 27906.75, buy-limit27787, day+11647.82/open 857.50; multiple earlier arrows. Right |date text too small to establish ?, MNQM2026,2m| NY range-high failed breakout short, staggered lower buy limits, day+9607.48/open 2370; precise price labels unresolved.
G21 | GB p47 cards |2026-06-29 Y, NQ/MNQ| total 83187.78 displayed red but individual rows green: do not infer a signed trade loss; June 26 Y, MNQ|+91945.70. GB p48 left |2026-07-10 Y, MNQ|+283026.18 account aggregate. These dated results lack individual levels/directions; not additional identified setups.
G22 | GB p48 right |2026-07-13 Y, MNQU2026,15m, UTC-4| evening Asia/PDL failure-reclaim long 29414.25, limits 29537.50/29552.75/29569.50/29589.75; day+71355.65/open 11322.50. GB p49 cards |2026-07-14 Y, MNQ|+48283.20 at 21:59 and+255352.10 at 15:01, distinct account aggregates, not proven separate trades.
G23 | GB p50 left |undated ?, MNQ1! daily| high 30975.25, low 22884.75,50%=26930/golden pocket below it; projected long area, not an entry. Right |undated ?, MNQU2026,5m| late-session low long 29462.25, limits 29626.75–29849, day−20841.30/open+45680; exact date/result unavailable.
G24 | GB p51 both |displayed 2026-07-29→30 Y, MNQU6,5m| golden-pocket down-leg shorts27644.50 and 27652.75; stop 27717.50/27716.50, target 27189/27190.25; 6.24/7.19R drawings, open gains4478/5295.50, not final outcomes; timezone unprinted. GB p52 right |same displayed date span Y, MNQU6,3m| long 27359.75, protective stop 27382, limits 27521.25–27680.50, open 1361; may be a later reversal, exact linkage not established.
G25 | GB p52 left |2026-08-11 evening Y, MNQU2026,1m, UTC-4| Asia/earlier-low long 29437.75,50-point stop 29387.75, target 29652.50,4.3R drawing. GB p53 right/p54 left |Aug 11 evening→Aug 12 NY Y, MNQU2026,5m| Asia long 29635.75, stop 29587.50, target 29896,260.25-point drawing; later image shows target traversed and NY reversal, not exact fills. P53 left Aug 12 account+86300.66. P54 right |Aug 13 Y, MNQU26,2m| short 30227.50, stop 30238.75, buy-limit30069.50; additional long marker30011.75, open positions shown, not settled outcomes.
G26 | GB p55 left/p56 right cards |2026-08-24/25 Y, MNQ|+16047.98/+37721.18, individual trades unstated. P55 right |chartAug27–28, hoverAug30 Y, MNQU6,15m| high failure short 29680.75, limits 29492.75 down to29384.50, open 2388.50; hover in future blank area is not execution date. P56 left |Aug 27 Y, MNQU2026,5m| afternoon high failure short 29642.25, stop 29664, target 29425.25; limits on path, open 1216; distinguishes this21.75-point-stop drawing from G09's19.25-point ticket.
G27 | GB p57 |2026-09-10 N, MNQU2026,3m| multiple NYAM pullback/scalp arrows; displayed long 29222, target 29276; account+45540.40 at 15:38UTC corroborates G13 bullish case. P58 left |2026-08-31 Y, MNQU2026,1m| NY high failure short 29510.50, stop 29538.50, target 29280.25 (230-point drawing), open profit; no final fill record. P58 right Sep 1 account+31411.88 supplements G11.
G28 | GB p59 left |2026-09-03 P, MNQU2026,15m| Asia-high/TDO failure short, drawn entry 29238.25, stop 29255, target 29126.50; chart about01:18 before tape endpoint, so this overnight example may be covered, not its later RTH. P59 right Sep 2 Y account+18098.98 supplements bearish G13. P60 |Tuesday, associated Sep 8 post N, MNQU2026,15m| Asia-high failed breakout short,17.75-point stop/198.50 target drawing,11.18R; opposing Asia/London liquidity/NWOG, not proof target order filled.
S01 | ANAT pp1,6–9; M/source_cases_v2.json SIRES-losses-2026-07-23 transcription |2026-07-23 Y, NQ| nine attempts:10:14 loss,10:15 loss,10:17 win,10:24 loss,10:25 win,10:27 win,10:30 loss,10:31 loss,10:32 win; directions/price levels not all established; chart timezone unknown. Session4W/5L,≈+500,−480 trough; introductory “four losses” conflicts with displayed early win.
S02 | ANAT p8 |same date Y, NQ| defended long,35-tick stop/188-tick target,5.37R illustration; p9 short 15-tick stop/211-tick target,14.07R; spoken960 versus 1055 potential differs. Targets/drawings are not evidence of realized full-target fills; map each to the nine attempts before exact replay.
S03 | NYAM pp4–11 |undated ?, instrument not established| first defended/refill low long,+755 toHTF area; third support test short loses; KG1 retest trailRR.69→1.83; late weak push into resistance short, risk 100, winner; ≈1000 session acrosssix accounts. Preserve four linked trades, including loss; dates/prices absent.
S04 | K18 pp5–12 |undated ?, NQ-context| first two shorts lose≈100/40; third OFM short/retest, initial.69RR, protected-high trailing, lock775 toward 2300 then 1240 toward 2645; fourth same-size short after buyer absorption once profit secured. ≈2300 session/seven accounts;18k payout spans prior results, not this one trade.
S05 | K2345 pp5–9 |undated ?, NQ-context| ATH/weekly-delta/second failed seller-control, microbalance break long, stop below,5.59R target hit; later small short. Five trades/account+2345, prior−558→1787; spoken≈1300 differs. Individual extra trade directions/levels not printed.
S06 | CONT pp3–11 |undated ?, NQ/ES/YM context| HTF short/5m minorLVN and negative-delta stack; initial short stop then refreshed-band reentry; ticketp8 short, target 1100/stop 180=6.11R; p10 failed-squeeze OFM andp11 clean no-retest squeeze are separate illustrative catalysts. Post-trade POC alignment is annotation, not demonstrated pre-entry gate.
S07 | OFM pp7–14 |undated ?, NQ-context| p7B+ short 27-risk/40-reward; p8 cleaner short; p9A+ long trailed until absorption; p10A+ short aftertwo failures; pp11–13 aggressive short stop-limit belowwick→daily value; p14 passive long abovefailedbuyers,1–3R. Realized results not uniformly stated; p18 negative mechanical experiment is aggregate, not a dated author trade.
S08 | BIG pp6–16 |undated ?, NQ40-range| failed squeeze/reclaim/refill and aggression/continuation illustrations; p11 long 87.25-target/18-stop=4.85R potential; p15 short 33-target/9-stop=3.67R; p16 failed balance-fade4–5R potential. Label diagram targets as potential, not fills; 30–60 print examples are configuration evidence.
S09 | STOP pp7–13; ABS pp5–12 |undated ?| STOP failed early/repeated entries and fresh-confirmation illustrations; pp11–12 EPZ25 confirmed long, p13 premature/late long loses (ES proxy symbol, not NQ). ABS holds/rewards/refreshed retests versus unconfirmed defense examples; each source page is a schematic fixture unless date/price can be recovered.
S10 | RD pp5,7,9; FP8 pp3–6; FP9 pp5–7; DOM5–7 |undated ?, instrument? | RD long at protected delta low and two short illustrations; footprint cells6663.75/6662.75, diagonal/POC relocation, DOM defense/dry/reload/own-reward illustrations. Exact dates and complete trade brackets absent; useful component fixtures, not dated native author fills.
S11 | AMT1 pp5–9; VP2; TPO; VWAP pp5–10; MAMT pp5–18 |undated ?, instrument varies| balance fades/ledge continuation, four open types/IB/single prints, VWAP outer-band/anchor reactions, composite shorts and overnightLVN/shelf hold/olderPOC alignment; raw figures are identifiable by page, but native dates/selected bands absent in retained transcription. MAMT p20 ES1040-session2021–24 statistics have Y date overlap/instrument mismatch, not 1040 identified trades.
S12 | C1/C2/C3; D/emotion.pdf; VIX pp3–5; GEX pp4–20 |undated ?, ES/NQ context| thesis/risk/psychology illustrations and VIX12.5≈30pt,16≈50pt,22≈95pt ES-day examples; no dated price/chain or actual fills stated. Numeric risk/volatility illustrations are unit fixtures; they cannot serve as native day replays without missing identities.
S13 | TRAP pp3–10 |undated ?, instrument? | Asia short from redrawn HTF balance; priorAM andPM upper failures, downbreak/same-band retest/trapped buying→short; display501.50 result and 150–160 normal target context. Exact numeric price band and calendar date unavailable; retain prior failures as separate setup observations.
S14 | AMTL pp8–12 |undated ?, instrument? | failed newer value→original balance return; delayed/deep rejection examplep10; week higher balance failure→old auction p11. WIC pp3–10 fast/slow arrival, control/retest/flip and 15m alignment examples: directions per individual diagram, outcome/date unestablished, not all actual fills.
S15 | RTVP pp5–11 |undated ?, instrument? | POC failure→VAL versus efficient POC passage→VAH, balanced/double-distribution rotations andP/b/trend balance-retest examples. These are identifiable alternative setup diagrams; no dated author execution is established.
S16 | K10 pp7–8 |undated ?, ES (NQ context)| resistance short at priorreaction+minorHVN, stop abovehigh, spoken1.5R butticket1R; planned-return long after second-tap absorption, spoken1.5R withlaterexpanded9.6R drawing. Source treats them as teaching successes; exact realized bracket/fill record unavailable.
S17 | K10 pp12–13 |undated ?, ES-context| HTF/yearPOC lesson andthree bad shorts into held demand; negative confluence/thesis examples, individual prices/results absent. KG1 alternative p6 is a setup-selection example, no identified dated trade.
S18 | AVG pp21–22 |undated ?, instrument? | A abovepriorvalue→POC/priorVAH rejection→aggressiveVAH break→defended imbalance-retest long; preselected HTF target, realized outcome absent. Other AVG dashboard/behavior examples do not identify replayable fills.
S19 | REF pp5–7,10–12,20 |Dec2024–Nov 2025 Y, NQ/MNQ study|41152 touches/235sessions; individual dates/levels/directions absent. Undated touch/deeper-limit versus market-entry examples;12/32/96 ticks and 30m order expiry are execution fixtures. Q1 comparison64 limit versus 312 market fills is a study aggregate, not identified author orders.
S20 | MATH pp3–11 |undated ?, AAPL|20,000 ten-level events, B/A/D/E/W distribution/transition illustration, D→D84%, D→A12%; no NQ-date replay. MATH pp12–14 Sires current-auction LVN/shelf examples are additional undated structure illustrations, no source fill/outcome established.
S21 | DATA pp3–6 |undated ?, no specific instrument| research-process and bubble-cycle/leverage/credit/housing/valuation example; no price, direction, date or trade result to replay.
S22 | DATA pp7–8 |undated ?, no specific instrument| first risk 1→win3;secondrisk4→win12, total 15, orloss→sequence−1;reset1. Outcomes are worked arithmetic, not observed trades.
Example-index limitation: older Jumbo/discretionary image-only figures with unreadable dates remain page-identified using the wiki transcription, as explicitly permitted by the request; the source transcriptions do not justify assigning prices/dates/outcomes to them. No author example has been claimed here as successfully replayed through B0/B0.1/04.

Canonical source: [SEARCH_CONTRACT.md](/workspace/planning/phase-1-5/SEARCH_CONTRACT.md).

## Finite breadth and refinement search

Owner `P15-08` registers the candidate bank; `P15-17` executes breadth; `P15-18` refines. Read [specification](/workspace/planning/phase-1-5/SPEC.md), [evaluation](/workspace/planning/research-program/EVALUATION.md), [outcomes](/workspace/planning/research-program/OUTCOMES.md) and [retention](/workspace/planning/research-program/RETENTION.md) together.

### Candidate identity and counts

Always include B0, the accepted source-inspired reconstruction. A candidate changes exactly one declared mechanism axis unless it is in the later explicit combination round. It carries a diff of stage/parameter meanings, not just a cryptic integer. Apply candidates to every eligible branch listed below; the branch IDs come from the frozen Phase 1 registry, never from a hand-maintained second branch catalog.

| Bank | Representative alternatives beyond B0 | Eligible population |
| --- | --- | --- |
| Formation | F1 trailing 60m; F2 prior-volume-completed; F3 causal balance | JJ other_session, single_extended, single_purged, internal_rotation; GB nyam_box/previous_hour; Saint balance branches; Sires microbalance. Source clocks stay fixed. |
| Profile | P1 raw tick profile b0; P2 triangular b2 | Saint and Member profile references; Keani developing value; Sires balance references. Use the same causal formation. |
| Reference | R1 account-day VWAP/band; R2 prior completed session edge | Custom siblings of GB-VWAP, GB-SCALP and Sires vwap_deviation_fade/defended_band_continuation only. Preserve original source variants separately. |
| Delta | C1 normalized5m; C2 5m half-life; C3 past-bucket robust score | Every branch that actually consumes delta/flow in Sires, GB-SCALP, Saint; confirm input use in the source adapter. A branch with no delta input is explicitly not applicable. |
| Sequence | S1 reclaim; S2 defended retest; S3 flow-supported reclaim; S4 failure-to-progress | JJ reversal/extension/other_session; GB failure/scalps; Sires reaction/continuation; Saint retests; Member reaction; Keani retest. Do not change the Judas outbound opening-entry branch into a retest without a distinct custom family. The separate Timing bank explicitly tests custom Judas reversal windows. |
| Memory | M1 require at most 1 previous completed distinct contact; M2 require previous resolved120s favorable reaction >.25S and no subsequent invalidation | Existing reference-contact candidates in Member/Sires/Saint; Refilling observations separately. Not a universal ban on old/saturated levels. |
| Timing | T1 source reversal/action window +15m; T2 window -15m using only an already complete formation; T3 condition-defined morning reversal; T4 no clock limit: the same sweep and confirmation searched from 09:30 through the account-day flatten, with expiry 60 minutes after qualification | JJ judas_reversal/other_session and GB nyam_box custom siblings. If formation is not yet available at T2, omit with a reason; never truncate a source range and call it unchanged. T4 applies to JJ judas_reversal and every GB-FAIL sweep branch as a custom sibling; source-identity output remains B0. |

This is at most 19 nonbaseline axis recipes per branch, but only applicable cells are created. `P15-08` emits a concrete expanded `candidate-bank.json` with a maximum of 160 nonbaseline branch candidates for the breadth round, plus all baseline branches. If the mechanical expansion exceeds160, apply round-robin by bank then family then branch ID, taking one candidate per applicable family/bank before second candidates; preserve deferred cells and their deterministic order. No result may affect this expansion. This cap is a first-stage breadth budget, not a claim that exactly 160 models should exist.

Separate method adapters own source constraints and construction. `P15-09` Jumbo; `P15-10` GB-FAIL; `P15-11` GB-VWAP/scalps; `P15-12` Sires; `P15-13` Saint; `P15-14` Member; `P15-15` Keani; `P15-16` research processes. Context/research/risk units never enter entry-setup denominators because their candidate bank has a row.

### Custom reversal timing recipe

T1/T2 shift the action-window start and end together by the registered offset, keeping formation already complete; source-identity output remains B0 and changed clocks use custom sibling IDs. Their expiry is the shifted window end, capped at account-day flatten. T3 uses the source-frozen overnight/range reference and a 09:30–12:00 ET custom action window. Require a strict edge sweep, then a complete trailing 15-minute balance with width<=.75 of the 60-minute scale ending before that balance and efficiency<=.35, then the S1 reclaim within 10 minutes. Entry follows that causal reclaim, structural stop is beyond the swept extreme by1 tick, objective is the still-unconsumed opposite frozen edge, and expiry is the earlier of 60 minutes after qualification or 12:00. If the objective is already consumed after the sweep, reject it. Retain all unchanged source context that can be evaluated before contact; publish the timing/balance additions as our hypothesis, not an author Judas formula. This tests condition-based reversal beyond a small clock adjustment.

T4 removes the reversal clock entirely: after the source-frozen sweep and its five-minute confirmation, the entry may occur at any time from 09:30 to the account-day flatten; structural stop and objective are unchanged; expiry is the earlier of 60 minutes after qualification or the flatten. It tests whether the source's clock limit adds value beyond the sweep-and-reclaim mechanism itself. Its refinement neighborhood in the table below is the T issue offset row, unchanged.

### Breadth stage

Run the entire registered applicable bank in each outer fold with inner fit/tune separation. In inner tuning rank each candidate on primary daily net-point improvement, displaying frequency and delay. Pick at most two mechanism banks per source family that have nonnegative tuning improvement and pass inner support. Retain the best representative within each bank using the 1% simplicity rule. When none qualifies, choose no refinement and retain B0. This is a selection step; outer outcomes cannot expand the bank or choose the two banks.

Baseline comparisons use both common complete-input dates and full native coverage. Include density-matched controls for reference variants: choose the same count of bands on the same issue times, widths and expiry, with deterministic offsets `{-2S,-S,+S,+2S}` cycled by SHA256(reference_id) mod4. Reject a control that duplicates a real band within 1 tick and try the next offset; if all duplicate, mark unavailable. Controls preserve direction and stage/exit rules. They test whether concentration/placement adds value beyond the number and width of bands, not whether arbitrary shifted zones are a tradable strategy.

### Refinement stage

Refine only the two selected banks per family and only inside each fold's past fit/tune data. Use these exact one-axis neighborhoods; keep other chosen values fixed:

| Chosen mechanism | Neighbor values |
| --- | --- |
| F1 trailing duration | 30,60,90 matching minutes |
| F2 volume threshold multiplier | .75,1,1.25 times the prior 20-session median |
| F3 balance maximum width / efficiency | width .5,.75,1S with efficiency fixed.35; then efficiency .2,.35,.5 at chosen width |
| P smoothing / prominence | b0,2,4 with prominence.20; then prominence .10,.20,.30 at chosen b |
| R VWAP band | .5,1,1.5 dispersion; prior edge alternative has no numeric refinement |
| C1 window / C2 half-life / C3 history | 2,5,10 minutes / 120,300,600 seconds / 10,20,40 sessions |
| S deadline / reclaim favorable distance | 5,10,15 minutes / 1,2,4 ticks, one at a time |
| M1 touch count / M2 reaction threshold | at most 0,1,2 previous contacts / .1,.25,.5S |
| T issue offset | -30,-15,0,+15,+30 minutes; availability still required |

Maximum 12 new neighbors per selected bank per family, maximum 24 per family. After choosing the best two refined mechanisms, permit exactly one combined candidate with both changes, only if each individually beats B0 on inner tuning and all source dependencies remain causal. Compare combination against each ingredient and B0; label interaction explicitly. Maximum 25 refined/combined candidates per family per outer fold. There is one breadth round and one refinement round; no recursive “keep searching until profitable” loop.

If two families share a primitive, share cached calculations but keep their fitted/selected identities and evidence separate. Store attempted, duplicate, not-applicable, unsupported, timed-out and rejected candidate rows. Runtime failures never disappear from the trial count or become data rejections. A resumed run uses the same bank and seed.

### Trial ledger and final choice

`TrialRecord`: trial_id, parent_trial_ids, family, branch, outer_fold, stage, bank, exact parameters, code/data/plan hashes, fit/tune/calibration windows, outcome-exposure cutoff, candidate population counts, score/loss, support, all test metrics, reason, disposition, runtime, artifacts, and `failure_attribution`. Write append-only JSONL; a new attempt gets a new ID and `replaces_attempt_id`, leaving the old row intact.

`failure_attribution` is required for every deselected, inconclusive or not-promoted candidate. It is an ordered list drawn from `frequency` (entries below the frequency floor), `location_miss` (objective not reached while price came within 0.25 S of it, or adverse excursion beyond 0.5 S before any favorable 0.5 S), `confirmation_delay` (missed-move share above the family median), `adverse_before_target` (stop-first share above the family baseline), `cost_sensitivity` (sign reversal under the stress setting), `support` (below the support gate), `coverage` (unexplained input coverage loss). Each is computed from the diagnostics the Strategy Book already reports, with these thresholds fixed before any candidate result is read.

Bounded revisits: Phase 3 re-screens every retained candidate whose first attribution is `location_miss`, using its improved locations. Phase 4 re-screens every retained candidate whose first attribution is `confirmation_delay` or `adverse_before_target`, using the response and entry experts. A revisit is one registered pass over the retained set with the same folds, scores and promotion gates; it is not a new open search and adds no neighbors.

Select a final recommended research rule only by the shared promotion gates. Record the fold-specific selected rule role separately from an all-history descriptive final recommendation. Phase 2 historical training consumes the fold-specific causal role or B0, never a backward-applied final winner. Unselected alternatives remain available as research evidence, not automatically active downstream inputs. A disposition never deletes a candidate.

The exit study compares E0–E4 after entry selection is frozen. Its trials are an additional, separately counted decision family; it cannot rescue an entry candidate by replacing the primary exit during the earlier rule test. Final release includes both unchanged-entry evidence and the frozen baseline management policy for Phase 2 suitability labels.

Canonical source: [EVALUATION.md](/workspace/planning/research-program/EVALUATION.md).

## Chronological evaluation and selection

Owner: `P15-03`, extended by `P2-02` and `P2-24`. These are registered research defaults. They define a finite experiment; they are not claims about trading edge.

### Freeze and exposure

The Phase 1 baseline is the [acquired measurement](/workspace/implementation/reports/phase1-live/historical-measurement/MEASUREMENT_REPORT.md), run `run-1.0.1`, and its immutable registry, scope, composed calendars, input manifests and accepted implementation identities. `P15-00` reads the actual receipts rather than deriving identity from a folder name. Preserve all 1,742 declared labels and each branch's eligibility; do not make every branch complete by borrowing another branch's denominator.

All existing dates have some research exposure. Record Phase 1 engineering/reconstruction/measurement and this plan's design exposure. The following are chronological out-of-sample comparisons of newly fitted rules/models, **not an untouched holdout**. Freeze candidates, search limits and scoring before running them. A result-driven amendment creates a new exploratory version and adds exposure; it never reuses the same dates as fresh confirmation.

### Outer and inner splits

Outer test blocks are calendar years 2022, 2023, 2024, 2025 and the acquired part of 2026. Earlier dates are training/lookback only. Within outer year `Y`, initial fitting data end June 30 of `Y-1`; tuning is July 1–September 30; calibration is October 1–December 31. Choose candidates/hyperparameters on fit+tune as specified below, refit chosen parameters through September 30, and calibrate only on October–December. Test year outcomes never choose that year's candidates.

Examples: for test 2022, initial fit is 2020-01-01 through 2021-06-30, tune July–September 2021, calibrate October–December 2021. For test 2025, initial fit expands through June 2024. Missing years/inputs stay missing; no random split fills them.

Purge any training row whose label interval overlaps a tune/calibration/test interval or whose label was not available before the fitting cutoff. Add one entire eligible account day between adjacent partitions; the earlier partition loses the boundary day. Group all events, variants, overlapping horizons and assets from one account day together. No row-wise shuffle split, ordinary IID standard error, or random-fold stacking.

Hyperparameter tuning uses the fixed grid in [model fitting](/workspace/planning/research-program/MODEL_FITTING.md). Rule selection uses the finite bank in the [Phase 1.5 search contract](/workspace/planning/phase-1-5/SEARCH_CONTRACT.md). Ties within 1% of the best tuning loss/score choose the simpler model, then lower candidate ID lexically. Complexity order is constant/base rule, linear, hinge basis, combination; fewer changed axes wins within an order. Never use test results to break ties.

### Causal stacking and adaptation

Generate every upstream training prediction chronologically. Use consecutive 20-eligible-day blocks; for each block, fit on prior available labels and reserve the most recent 42 eligible prior days for calibration. Minimum fit history is 126 complete days and 500 rows. Hyperparameter selection uses the 42 eligible days immediately before calibration, with training before that; if unavailable, use the declared default hyperparameters. A fold therefore may have no supported upstream predictions early on. Preserve the warm-up mask and loss of training support.

Any Phase 1.5 selected-rule role used in a historical Phase 2 row must be selected using evidence available before that row's block. Do not apply the global 2026 winning rule backward as if it had been selected in 2022. Persist `selection_manifest_id`, its cutoff and all candidate IDs for each block. Always retain the fixed source baseline features. For scarce cells, use the baseline role and mark selection unsupported.

Initial Phase 2 comparison holds parameters fixed for an outer test year. The adaptation experiment later compares: fixed annual; monthly refit at the first account-day open; weekly refit at Monday account-day open; and monthly refit plus intraday intercept updates. Refit uses a fixed trailing 756 complete eligible days (or all available if fewer), with the trailing 42 days reserved for calibration. The selected model/rule families and hyperparameters remain frozen for the outer year. Intraday updates may consume only matured, published labels, per the exact update rule in the Phase 2 adaptation contract. Every fit is versioned and becomes available at the next scheduled issue after measured fitting completion, never retrospectively at its data cutoff.

### Support and honest terminal outcomes

For a fitted continuous expert: at least 500 complete training rows on 100 account days, and 100 evaluation rows on 30 days. For a binary head: additionally at least 20 examples of each class on at least 10 distinct training days. For multiclass: apply that condition to each class; unsupported classes are pooled into an explicit `other_low_support` only if the target contract allows it, otherwise use the empirical prior and mark the head low-support. Never silently remove rare source branches.

For a Phase 1.5 upgrade: at least 100 resolved benchmark opportunities on 30 eligible test days in aggregate, represented in at least three outer blocks. A branch below the gate is `inconclusive_support`, even if all six examples succeed. It remains in the registry and downstream baseline allowlist, with low-support status. Support gates are research defaults and their counts must be shown alongside sensitivity at half/twice the gate; changing the gate cannot manufacture a claim. A disposition never deletes a candidate: `inconclusive_support`, `rejected_by_evidence`, `retained_baseline` and `unsupported_owned_input` keep the full population, parameters and diagnostics in the trial ledger and the retention set, and "inactive" means not consumed by the next phase's training by default. The trial ledger, its `failure_attribution` field and the bounded revisit rule are defined once in the [search contract](/workspace/planning/phase-1-5/SEARCH_CONTRACT.md) and the [retention rules](/workspace/planning/research-program/RETENTION.md).

### Scores and uncertainty

Each family report contains (a) all attempted variants, (b) common complete-day paired comparisons, and (c) full candidate-specific coverage. A method's own source prerequisites remain in its eligible population. No missing feature/outcome is silently treated as no-setup. Unresolved order is an explicit excluded primary outcome with counts and pessimistic/optimistic bounds.

For setup rules the primary score is the mean daily net points in the deterministic one-contract benchmark in [outcomes](/workspace/planning/research-program/OUTCOMES.md). Compare a candidate with the unchanged baseline on common complete eligible days, including zero-entry days. Also report eligible opportunities/day, retained baseline opportunities, new opportunities, ordered target/stop rate, median net points/opportunity, drawdown from day-start, confirmation delay and missed-move counts. This benchmark measures an isolated family under a fixed scheduler; it is not a combined portfolio or a certification of the user's daily target.

For forecasts: QLIKE for variance; pinball for excursion/time quantiles; multiclass log loss and Brier for probabilities; absolute error for continuous state forecasts; censored time outcomes use the discrete survival loss specified in Phase 2. Report calibration and support for every head, horizon, session and year. Standardize multihead tuning losses by the loss of the training-only baseline, with denominator `max(abs(baseline_loss), 1e-8)` except QLIKE: use QLIKE excess `y/v - log(y/v) - 1` for positive y, and ordinary QLIKE differences for zero y. Average only supported heads with equal head weights; report the supported-head set so missing difficult heads cannot improve the aggregate silently.

Uncertainty uses a paired circular moving-block bootstrap of account days, block length 5, 2,000 draws, NumPy `Generator(PCG64(15022026))`. Draw block starts uniformly within each calendar-year segment and wrap only within that segment; concatenate blocks and truncate to its original day count. Use identical draws for baseline/candidate and all variants. Report percentile 2.5/97.5 bounds of the mean difference. Also report block lengths 1 and 10 as sensitivity, not additional selection opportunities.

For an exploratory one-sided improvement p-value use the centered bootstrap: observed mean difference `d`; each draw computes `d_b`; `p=(1 + count(d_b-d >= d))/(B+1)` under the null of no mean improvement. Family-level p-values include every candidate tested at that decision stage. Apply Holm adjustment: sort p ascending, compare `p_(i) <= .05/(m-i+1)` until the first failure, reject no later hypotheses. Publish raw p, adjusted p, candidate count and all unsuccessful trials. This dependence-aware exploratory procedure does not erase prior exposure or make adaptive search confirmatory.

Promotion requires: software/causality gates pass; support passes; paired mean improvement > 0 with the 95% lower bound > 0; Holm-adjusted p <= .05; at least three supported outer blocks and a positive difference in at least 60% of supported blocks; no cost-stress sign reversal at the declared stress setting; and no unexplained loss of input coverage. Frequency is a second objective: publish the quality–frequency Pareto set. A candidate with <50% of baseline entries cannot replace the family baseline; it may remain a separately labelled high-selectivity option if it passes all other checks. Keep the baseline whenever no candidate clears the gate.

### Economic evidence and limits

Show every eligible account day: net dollars, trades, zero-trade indicator, day-start worst marked P&L, risk-stop trigger, slippage/gap breach, and coverage. Summaries include median, mean, 5th percentile, worst day, fraction below $0/$1,000/$3,000 and fraction exceeding the $1,000 loss limit. Do not replace the user's daily floor with an average threshold, hide zero days or clip a loss to the limit.

Phase 1.5 and Phase 2 may close with retained baselines or negative/inconclusive findings. They cannot claim the final economic goal is met. Only a later combined decision replay can evaluate the integrated historical daily distribution; future realized performance remains a separate question.

Canonical source: [OUTCOMES.md](/workspace/planning/research-program/OUTCOMES.md).

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

Canonical source: [DELIVERABLES.md](/workspace/planning/research-program/DELIVERABLES.md).

## Phase deliverables and definition of done

Receipts, matrices and gate reviews prove that software ran and that checks passed. This contract defines what the user receives at the end of each phase and the exact artifact that marks a phase finished. It adds reporting requirements; it changes no formula, budget, gate or date.

### Phase 1.5 outcome: Strategy Book, version 1

One entry per family and per branch in the frozen Phase 1 registry, including research, process and risk units, with entry setups distinguished from observations. Every number carries a pointer to the immutable artifact it was computed from. Sections per branch:

1. **Definition.** Source method, branch, ordered stages, reference, confirmation, structural stop and objective, expiry, session clock, and for every operand whether it is source-exact, printed-but-different, inferred or not identifiable, linking the source-reconstruction ledger row. For every source stage of the branch, one status: evaluated, evaluated_with_inferred_substitute, structural_not_required, unevaluated, scheduled_build, or personal_record_excluded, with the ledger row or code reference that justifies it. Where a literal operand is kept by construction or by declared assumption, the entry names it and the assumption ID.
2. **Population.** Eligible account days, opportunities, opportunities per day and per week, by year; unknown-input, ambiguous-order and missing-coverage counts; the stage-rejection funnel (how many contacts fail at which prerequisite).
3. **Base rates, baseline B0, fixed one-contract benchmark.** Ordered outcome rates (target first, stop first, neither, ambiguous) on the rule's structural geometry and on the diagnostic grid; net points per opportunity (mean, median, 5th and 95th percentiles); win rate and payoff ratio; expectancy per eligible day; daily P&L distribution (median, mean, 5th percentile, worst day, fraction of days below zero); maximum drawdown from day start; time to resolution; MFE and MAE quantiles at each horizon; confirmation delay; missed-move counts. Every rate carries the contract's block-bootstrap 95% interval and its support count.
4. **Conditional rates by pre-registered regime dimension.** One-way cuts only, no interactions, each cell with count, rate and interval, cells under 30 opportunities marked low-support. Dimensions are frozen in `REGIME_DIMENSIONS.json` before any candidate result is read, each computed causally from owned data as of the decision time: calendar year and outer fold; session bucket (Asia, London, New York morning, New York afternoon); day of week; realized-volatility tercile from the prior 20 sessions' daily ranges; overnight range relative to its prior-20-session median, in terciles; prior-close VIX bucket (below 15, 15 to 20, 20 to 30, above 30); inferred aggregate gamma sign at 09:32 (positive, negative, unknown; labelled inferred); prior-day type by the registered trend-or-balance rule; scheduled macro release day (CPI, payrolls, FOMC) where the calendar is owned. This section is descriptive. It never selects candidates, and it is disclosed in the exposure ledger.
5. **Upgrades.** Every attempted candidate for the family with bank, axis, parameters and disposition (attempted, duplicate, not applicable, unsupported, timed out, rejected, selected). For the selected candidate per outer fold: sections 2 to 4 recomputed and paired against B0 with differences, intervals, raw and Holm-adjusted p, fraction of positive blocks, cost-stress result, and the quality-frequency Pareto set. The exit study E0 to E4 on the frozen entries.
6. **Verdict.** Promoted, retained baseline, inconclusive support or not applicable, with the reason, the fold-specific selected-rule manifest IDs, and the all-history descriptive recommendation kept separate from the causal fold roles.
7. **Limitations.** Coverage gaps, inferred inputs, unknown operands, exposure notes, and what the branch's numbers cannot claim.

**Formats.** `STRATEGY_BOOK.md` (one section per family, one subsection per branch), `STRATEGY_BOOK.json` (the same numbers under a versioned schema) and one CSV per branch for sections 3 to 5. Produced by P15-20 from the immutable trial ledgers. A **B0-only edition** covering sections 1 to 4 and 7 is produced as soon as the outcome machinery exists, so base rates are readable before any search result; it is regenerated, never edited, when the full edition is built.

**Definition of done for Phase 1.5.** The release receipt verifies; every registry branch has a book entry with a verdict; the B0-only and full editions render from artifacts with no hand-typed number; all attempted candidates appear; the Phase 2 allowlist and selected-rule manifests are frozen.

### Phase 2 outcome: Strategy Book, version 2, plus context experts

Per strategy, adding to version 1: fitted conditional probability of target-first, expected net points and suitability (session, reference, confirmation, timing, target ambition) as functions of the context state; calibration by year and session (reliability tables, Brier and log loss); a context-sensitivity ranking from group ablations (volatility forecast, options and gamma exposure, auction and day state, cross-market coupling, flow); the immutable conditional plan; and the adaptation comparison (fixed annual, monthly, weekly, monthly with intraday updates). Per expert (joint volatility, remaining range and passage time, auction and day quality, options flow and repricing, intraday OI estimate): scores against the registered baselines by horizon, session and year, ablations, support and lineage.

**Definition of done for Phase 2.** The release receipt verifies; every strategy has a version 2 entry and every expert has a scorecard; the chronological replay, ablations and lineage are complete; the Phase 3 handoff lists which context outputs are admissible inputs for location work.

### Subphase outcomes, what the user can inspect at each boundary

| Subphase | User-facing outcome |
| --- | --- |
| 1.5 / 00 | The verifier and the baseline binding. Nothing to read about strategies yet. |
| 1.5 / 01 | Native full-account-day market view with byte-identical baseline parity on the stratified sample; outcome and benchmark machinery; throughput measurement; the fit-period baseline diagnostics. |
| 1.5 / 02 | The source-reconstruction ledger, the printed-figure replay result, versioned source-exact amendments. The B0-only Strategy Book edition. |
| 1.5 / 03 | The primitive library with literal fixtures and the registered candidate bank. |
| 1.5 / 04 | Every family adapter run on full history: first candidate populations and coverage per branch. |
| 1.5 / 05 | Breadth and refinement trial ledgers with every disposition. |
| 1.5 / 06 | The exit study. |
| 1.5 / 07 | Strategy Book version 1 and the release. |
| 2 / 00–08 | Expert scorecards as each is fitted; Strategy Book version 2 at release. |

Canonical source: [RETENTION.md](/workspace/planning/research-program/RETENTION.md).

## Retention, failure attribution and revisit rules

Amends ROADMAP.md, EVALUATION.md and SEARCH_CONTRACT.md. Adds bookkeeping and bounded revisits; changes no formula, gate, budget or date of the existing banks.

### The problem this closes

The program selects components in sequence: rules in Phase 1.5, context in Phase 2, locations in Phase 3, response and integration in Phase 4. Each selection is made against the objective given the downstream components that exist at that time. A candidate whose weakness lies in a component that a later phase improves can therefore be deselected early for the wrong reason and never looked at again. Example: a reference variant loses in Phase 1.5 because the baseline P-zone location is poor, Phase 3 improves locations, but the variant is no longer in play.

### Rules

1. **Nothing is discarded.** Every registry branch stays in the retention set through Phase 4 with a status: `active_selected`, `active_baseline` or `inactive_retained`. Every attempted candidate keeps its full population definition, parameters and diagnostics in the trial ledger. "Inactive" means not consumed by the next phase's training by default; it never means deleted.
2. **Failure attribution.** Every deselected, inconclusive or not-promoted candidate gets a `failure_attribution` field in its TrialRecord: an ordered list drawn from `frequency` (entries below the frequency floor), `location_miss` (objective not reached while price came within 0.25 S of it, or adverse excursion beyond 0.5 S before any favorable 0.5 S), `confirmation_delay` (missed-move share above the family median), `adverse_before_target` (stop-first share above the family baseline), `cost_sensitivity` (sign reversal under the stress setting), `support` (below the support gate), `coverage` (unexplained input coverage loss). Each is computed from the diagnostics the Strategy Book already reports, with the thresholds fixed here before any candidate result is read.
3. **Bounded revisits.** Phase 3 re-screens every retained candidate whose first attribution is `location_miss`, using its improved locations. Phase 4 re-screens every retained candidate whose first attribution is `confirmation_delay` or `adverse_before_target`, using the response and entry experts. A revisit is one registered pass over the retained set with the same folds, scores and promotion gates; it is not a new open search and adds no neighbors.
4. **Phase 2 is split.** Strategy-agnostic context experts (joint volatility, remaining range and passage time, auction and day state, options flow and exposure, intraday OI, cross-market coupling) are fitted once in Phase 2 and are inputs to Phases 3 and 4. Method-specific suitability experts and conditional plans fitted in Phase 2 are provisional: they are fitted on B0 or the selected rule with baseline locations, and they must be refit in Phase 4 on the final rule-plus-location combination before any decision integration. Phase 2 produces dispositions for strategies, never discards.
5. **Every release reports the retention set** with statuses and first attributions, so a reader knows what is inactive, why, and which later phase will revisit it.

### What can be parallelised without breaking the Phase 1.5 gate

The gate "complete all Phase 1.5 before implementing Phase 2" protects Phase 2 from consuming unverified Phase 1.5 research outputs. The strategy-agnostic experts consume only the verified native market view, outcome contracts and raw options data, not selected rules. After subphase 01 verifies, P2-09 and P2-10 (native option, spot and OI adapters, pricing, Greeks, exposure boards) and P2-03 (volatility arithmetic and targets) can be implemented in a separate git worktree by a second writer, with their own receipts, and merged at the Phase 1.5 release. Anything that reads a selected rule or a Phase 1.5 candidate result stays behind the gate. This is a user decision because it narrows a settled gate.

Canonical source: [P15-16A.md](/workspace/planning/phase-1-5/tasks/P15-16A.md).

## P15-16A — Source-fidelity baseline B0.2 and author-example replay

Status: **planned; implementation not started by this planning task**.

Subphase: `05-finite-search`. Dependencies: P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16.

### Goal and boundary

Implement the source-faithful baseline **B0.2-2026-09-15** for every family natively in the family adapters on the array engine, applying every ruling in the source-fidelity addendum of [DISPOSITION.md](/workspace/planning/research-program/reviews/phase1-code-review-2026-09-14/DISPOSITION.md) (findings F01 to F20 of the [Astra source-fidelity review](/workspace/planning/research-program/reviews/astra-fidelity-2026-09-15/REVIEW.md)); measure B0.2 over all 1,742 sessions beside the frozen B0 and B0.1 rows; replay every author example that the tape covers; record ledger corrections. No candidate is scored here; P15-17 pairs candidates against B0.2.

Implement only this task and its declared outputs. Preserve accepted Phase 1 code/reports, immutable sources and raw data. B0 (`method_pack`) and B0.1 (`baseline_repairs.py`) stay byte-identical frozen comparison rows. Every rule is either a literal with its source location or an operational rule labelled `OD` with registered parameters; no rule is adjusted to make an author example pass without a source quote. No future input, later fit or all-history selected rule may enter an earlier decision.

### Read first

- [AGENTS.md](/workspace/AGENTS.md)
- [ROADMAP.md](/workspace/planning/ROADMAP.md)
- [PSTACK_EXECUTION.md](/workspace/planning/research-program/PSTACK_EXECUTION.md)
- [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md)
- [Assigned failure cases](/workspace/planning/research-program/SILENT_FAILURES.md)
- [WORKFLOW.md](/workspace/planning/research-program/WORKFLOW.md)
- [Source-fidelity rulings](/workspace/planning/research-program/reviews/phase1-code-review-2026-09-14/DISPOSITION.md) (addendum "source-fidelity rulings (2026-09-15)")
- [Astra source-fidelity review](/workspace/planning/research-program/reviews/astra-fidelity-2026-09-15/REVIEW.md)
- [SPEC.md](/workspace/planning/phase-1-5/SPEC.md)
- [SOURCE_ADDITIONS_2026-09-14.md](/workspace/planning/phase-1-5/SOURCE_ADDITIONS_2026-09-14.md)
- [PERFORMANCE.md](/workspace/planning/research-program/PERFORMANCE.md)
- The family wiki pages and the raw sources each ruling cites.

The rulings provide the exact rule, its classification and the evidence; the review provides the source locations. Do not substitute remembered formulas or undocumented library defaults.

### Input and ownership contract

Consume verified predecessor receipts: **P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16**. Their hashes and actual artifact paths go in this task receipt. B0.1 populations are read from the census run `20def36e065c13d7`; B0 from run-1.0.1 job files; neither is recomputed.

Allowed implementation/test paths:

- `/workspace/implementation/src/trading_research/research/rule_discovery/source_adapters/` (every family adapter, `common.py`, `confirmation.py`)
- `/workspace/implementation/src/trading_research/research/rule_discovery/families/`
- `/workspace/implementation/src/trading_research/research/rule_discovery/run_adapter_populations.py`
- `/workspace/implementation/tools/replay_author_examples.py`
- `/workspace/implementation/tests/rule_discovery/test_p15_16a.py`

A worker does not edit another task's shared files. Request an explicit integration patch from the subphase coordinator for runner registration, imports or additive shared-schema changes; the coordinator records it and reruns the affected contract tests.

### Implementation steps

1. For each family, implement the rulings as the native B0.2 scan in its adapter: literals bound from the cited pages, `OD` rules labelled with registered parameters, stage funnels recorded per episode. Write FIDELITY_MATRIX.json: one row per finding F01 to F20 and per family ruling with status implemented or deferred (with the source reason), file:line, fixture name and evidence pointer.
2. Run B0.2 over all 1,742 sessions for every family and branch with the checkpointed runner (manifest, per-date completion, resume, RUN_COMPLETE.json last); SUMMARY per branch gives B0, B0.1 and B0.2 episodes, pass, fail, unknown, verdict transitions and the per-stage funnel.
3. Replay every author example marked inside the tape with an identifiable session in the review's index through B0.2 for its family; AUTHOR_EXAMPLE_REPLAY.json and .md report, per example, source location, date, detected yes or no, our level and direction against the author's, and the divergence.
4. Record LEDGER_CORRECTIONS.json for the reconstruction ledger rows the review names (L018, L021, L024, L030, L032, L038 to L044), without editing the immutable P15-04 artifact. Trace one actual B0.2 output through its serialized schema, stage parents and native receipt; then run the verification below and write immutable evidence.

### Worked and discriminating checks

Use the literal cases the rulings cite (for example CONT p11 for the clean squeeze, TRAP pp3–9 for trapped buyers, NG 2099513366326730859 for the London sequence) as fixtures, plus one independently constructed negative case per family. Every fixture fails if its rule is removed, reversed, delayed incorrectly or fed future information. Add the negative control that a frozen-row replay (B0, B0.1) stays byte-identical after the B0.2 code exists.

### Required failure checks

Acceptance amendment: `research-assurance-2026-09-14-v3`. Assigned cases: **S01, S02, S03, S07, S08, S09, S21, S22, S31**. Use the exact probes, expected results and evidence in SILENT_FAILURES.md. Reuse current bound shared evidence where applicable; do not replace the task's own sensitive/native check with a test count. Preserve prior attempts and produce the common task artifacts listed in TASK_GRAPH.json as well as the task-specific outputs below.

### Acceptance checklist

- [ ] A01: Every ruling in the source-fidelity addendum is implemented in B0.2 with a fixture that fails if the rule is removed, or recorded as deferred with the source reason, in FIDELITY_MATRIX.json.
- [ ] A02: B0.2 is measured over all 1,742 sessions per branch beside B0 and B0.1 with verdict transitions and per-stage funnels; the B0 and B0.1 rows are byte-identical to their frozen sources.
- [ ] A03: Every author example inside the tape with an identifiable session is replayed; the table reports detected yes or no, level and direction against the author's; no rule was changed to pass an example without a source quote.
- [ ] A04: Every operational rule is labelled `OD` in code and report with its registered parameters, every literal cites its source location, and the ledger corrections are recorded.
- [ ] A05: Populations are plausible against the source's stated frequencies, or the gap is explained by the per-stage funnel (at least SAINT-AMT stages, SIRES catalysts, GB-FAIL bias filter, GB-VWAP retest resolution).
- [ ] A06: Evidence includes command exit codes, artifact hashes, coverage/unknown counts, runtime, actual output inspection and the task's declared limitations. All predecessor receipts verify.

- [ ] A07: EVIDENCE_MATRIX.json resolves every acceptance key and assigned failure case to actual code, executed commands, hashed evidence and inspected output under ASSURANCE.md; artifact/identity/command forgeries fail.
- [ ] A08: The assigned silent-failure probes pass with sensitive positive and negative controls, honest native/unknown/job counts, and no stale evidence. Return review-ready artifacts; subphase admission additionally requires the coordinator's matching passing GATE_REVIEW.json.

### Commands and evidence

Commands below are **to run during implementation after their owner task creates the entrypoint**. Use the existing environment; do not install arbitrary packages.

```bash
cd /workspace/implementation
.venv/bin/python -m pytest /workspace/implementation/tests/rule_discovery/test_p15_16a.py -q
/workspace/implementation/.venv/bin/python /workspace/implementation/src/trading_research/research/rule_discovery/run_adapter_populations.py --baseline B0.2 --workers WORKERS
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/replay_author_examples.py --index /workspace/planning/research-program/reviews/astra-fidelity-2026-09-15/REVIEW.md --run-root RUN_ROOT
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt TASK_RECEIPT_PATH
```

Expected artifacts under the task's immutable report run (large data shards may be in the ignored cache, with file-level hashes in the manifest):

- `FIDELITY_MATRIX.json`
- `B02_SUMMARY.json` and `B02_SUMMARY.md` (with the run root identity)
- `AUTHOR_EXAMPLE_REPLAY.json` and `AUTHOR_EXAMPLE_REPLAY.md`
- `LEDGER_CORRECTIONS.json`
- `FAMILY_REPORT.md`
- `TASK_RECEIPT.json` and `REPORT.md`, including acceptance keys A01–A08 and exact predecessor/artifact hashes.

### Completion and stop rules

Software checks must pass. A finding may be deferred only with the source reason recorded (a genuinely proprietary or discretionary rule); a rule the source states is work remaining. Sparse or negative populations are valid findings when the funnel explains them; they do not authorize loosening a rule. Use the shared receipt statuses; do not mark a phase complete.

Any family report prints both the PHASE table and the audit table defined in WORKFLOW.md. Report the real completed behavior, commands, native evidence, limitations and next eligible dependency. Do not claim author-exact proprietary recovery or complete native coverage without the required evidence.

### Copyable worker prompt

Generated from the task graph and pstack execution contract by tools/build_research_plan_bundles.py. Edit the canonical task above for research requirements; rebuild this section after prompt changes.

```text
/poteto-mode new task. Implement this feature: P15-16A — Source-fidelity baseline B0.2 and author-example replay.
Read /workspace/planning/phase-1-5/tasks/P15-16A.md and /workspace/planning/research-program/PSTACK_EXECUTION.md. Use the installed pstack router and the card's required contracts; this is execution of an existing specification.
Use the coordinator's actual working root, code identity, predecessor receipt paths/hashes, frozen manifest, dates and run root. Resolve missing values from those artifacts; report unresolved fields to the coordinator instead of inventing them.
Use the parent Grok model for every pstack role (inherit-parent means omit model). Use the installed poteto-agent wrapper when supported. No nested delegation; the coordinator owns fresh review and shared-file integration. Respect its single-writer checkout assignment.
Follow the exact formulas, clocks, schemas, allowed paths, finite budgets and A01, A02, A03, A04, A05, A06, A07, A08 checks. Name the data shape, implement one vertical behavior, run sensitive tests and the declared native slice/full run, and inspect actual output.
Done means all required artifacts exist and verify_research_release.py task exits 0 on the actual TASK_RECEIPT.json, with truthful coverage and disposition. Return real artifact paths, command results, decision-trail path and limitations. Keep runtime todos in the run's WORK_LOG.md and record playbook skips there.
Apply /workspace/planning/research-program/ASSURANCE.md and the card's assigned silent-failure cases: S01, S02, S03, S07, S08, S09, S21, S22, S31. Produce EVIDENCE_MATRIX.json linking every required check to real code, executed commands, hashes and inspected output selectors. Show sensitive accepted/rejected controls; preserve missing/ambiguous data and all declared jobs. A pass flag or your own verifier alone cannot prove completion. Return the evidence for the coordinator's separate GATE_REVIEW.json; do not edit fixed independent checks to obtain a pass.
Preserve accepted Phase 1 evidence, raw sources, missing/ambiguous inputs and unsuccessful trials. Perform the local task only; no external publication, shipping workflow or later phase. Do not stop at a plan or a passing toy test.
```

Canonical source: [P15-17.md](/workspace/planning/phase-1-5/tasks/P15-17.md).

## P15-17 — Execute and reconcile the breadth screen

Status: **planned; implementation not started by this planning task**.

Subphase: `05-finite-search`. Dependencies: P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A.

### Goal and boundary

Freeze the expanded bank, split/exposure manifests and run resource profile. Execute all registered applicable candidates on each chronological fold, retaining errors and zero days.

Implement only this task and its declared outputs. Preserve accepted Phase 1 code/reports, immutable sources and raw data. All new numerical recipes are registered research policies unless the source ledger proves literal attribution. No future input, later fit or all-history selected rule may enter an earlier decision.

### Read first

- [AGENTS.md](/workspace/AGENTS.md)
- [ROADMAP.md](/workspace/planning/ROADMAP.md)
- [PSTACK_EXECUTION.md](/workspace/planning/research-program/PSTACK_EXECUTION.md)
- [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md)
- [Assigned failure cases](/workspace/planning/research-program/SILENT_FAILURES.md)
- [WORKFLOW.md](/workspace/planning/research-program/WORKFLOW.md)
- [SEARCH_CONTRACT.md](/workspace/planning/phase-1-5/SEARCH_CONTRACT.md)
- [EVALUATION.md](/workspace/planning/research-program/EVALUATION.md)
- [OUTCOMES.md](/workspace/planning/research-program/OUTCOMES.md)
- [SPEC.md](/workspace/planning/phase-1-5/SPEC.md)

The named phase specification provides the exact formulas, proposed signatures, units and literal fixtures for this task. Existing symbols are marked as existing; proposed modules/commands are created by their owner tasks. Do not substitute remembered formulas or undocumented library defaults.

### Input and ownership contract

Consume verified predecessor receipts: **P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-16A**. Candidates pair against the source-faithful baseline B0.2 from P15-16A; B0 and B0.1 rows are reported beside it. Their hashes and actual artifact paths go in this task receipt. Required schema details are in DATA_CONTRACTS; source adapters also read their named method predicates.

Allowed implementation/test paths:

- `/workspace/implementation/src/trading_research/research/rule_discovery/search.py`
- `/workspace/implementation/tests/rule_discovery/test_p15_17.py`

A worker does not edit another task’s shared files. Request an explicit integration patch from the subphase coordinator for runner registration, imports or additive shared-schema changes; the coordinator records it and reruns the affected contract tests. Keep independently fitted artifacts separate even when calculators are shared.

### Implementation steps

1. Freeze the expanded bank, split/exposure manifests and run resource profile. Execute all registered applicable candidates on each chronological fold, retaining errors and zero days.
2. Compute paired/common-coverage and full-population metrics, controls, frequency/delay tradeoffs and per-bank/family dispositions.
3. Select at most two banks per family using inner tuning only. Write append-only trial ledger and the per-fold refinement allowlist.
4. Trace one actual output through its serialized schema, feature/stage parents and native receipt. Then run the verification below and write immutable evidence. A formula unit test alone does not complete a native-data or fitted-expert task.

### Worked and discriminating checks

Use the literal cases in the named mathematical contract and add one independently constructed negative case.

Use the shared [reference vectors](/workspace/planning/research-program/fixtures/reference_vectors.json) where applicable. Add a negative control that fails if the central behavior is removed, reversed, delayed incorrectly or fed future information. Model tests must include a known synthetic signal and a native chronological slice; never demand an empirical market improvement merely to pass software verification.

### Required failure checks

Acceptance amendment: `research-assurance-2026-09-14-v3`. Assigned cases: **S01, S02, S03, S06, S07, S11, S12, S13, S15, S22, S24, S32**. Use the exact probes, expected results and evidence in SILENT_FAILURES.md. Reuse current bound shared evidence where applicable; do not replace the task’s own sensitive/native check with a test count. Preserve prior attempts and produce the common task artifacts listed in TASK_GRAPH.json as well as the task-specific outputs below.

### Acceptance checklist

- [ ] A01: Every registered candidate has an attempted or explicitly deferred/not-applicable record.
- [ ] A02: Changing outer outcomes does not change that fold’s bank choice.
- [ ] A03: No result-driven new candidates enter the frozen breadth run.
- [ ] A04: Primary daily metrics reconcile to opportunities/fills/exclusions/zero days.
- [ ] A05: Resource timeout resumes the same run; no slow dates disappear.
- [ ] A06: Evidence includes command exit codes, artifact hashes, coverage/unknown counts, runtime, actual output inspection and the task’s declared limitations. All predecessor receipts verify.

- [ ] A07: EVIDENCE_MATRIX.json resolves every acceptance key and assigned failure case to actual code, executed commands, hashed evidence and inspected output under ASSURANCE.md; artifact/identity/command forgeries fail.
- [ ] A08: The assigned silent-failure probes pass with sensitive positive and negative controls, honest native/unknown/job counts, and no stale evidence. Return review-ready artifacts; subphase admission additionally requires the coordinator’s matching passing GATE_REVIEW.json.

### Commands and evidence

Commands below are **to run during implementation after their owner task creates the entrypoint**. They have not been run by this planning change. Use the existing environment; do not install arbitrary packages.

```bash
cd /workspace/implementation
.venv/bin/python -m pytest /workspace/implementation/tests/rule_discovery/test_p15_17.py -q
```

Then run the frozen engineering slice with the actual manifest and date list produced by the prerequisite (substitute the three ALL_CAPS paths/values; do not invent dates from outcomes):

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/run_rule_discovery.py slice --run-root RUN_ROOT --manifest FROZEN_MANIFEST --dates FROZEN_DATES --task P15-17
```

Reconcile all required cases, inspect output and profile before a full run. Search/release tasks additionally use the runner’s `run`, `resume` and `summarize` on the same immutable manifest; complete declared jobs before claiming an executed experiment.

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt TASK_RECEIPT_PATH
```

Expected artifacts under the task’s immutable report run (large data shards may be in the ignored cache, with file-level hashes in the manifest):

- `TRIALS.jsonl`
- `BREADTH_RESULTS.json`
- `REFINEMENT_ALLOWLIST.json`
- `FAMILY_REPORTS/`
- `TASK_RECEIPT.json` and `REPORT.md`, including acceptance keys A01–A08 and exact predecessor/artifact hashes.

### Completion and stop rules

Software checks must pass. A native cell may be unsupported only after the specified owned-input search and generic implementation/fixture verification. Sparse or negative research findings retain the baseline and all counts; they do not authorize more unregistered search. An implementation defect, unresolved job or timeout is work remaining. Use the shared receipt statuses; do not mark a phase complete from this individual card.

Any family report prints both the PHASE table and the audit table defined in WORKFLOW.md. Report the real completed behavior, commands, native evidence, limitations and next eligible dependency. Do not claim final profitability, author-exact proprietary recovery or complete native coverage without the required evidence.

### Copyable worker prompt

Generated from the task graph and pstack execution contract by tools/build_research_plan_bundles.py. Edit the canonical task above for research requirements; rebuild this section after prompt changes.

```text
/poteto-mode new task. Run this finite registered research experiment: P15-17 — Execute and reconcile the breadth screen.
Read /workspace/planning/phase-1-5/tasks/P15-17.md and /workspace/planning/research-program/PSTACK_EXECUTION.md. Use the installed pstack router and the card's required contracts; this is execution of an existing specification.
Use the coordinator's actual working root, code identity, predecessor receipt paths/hashes, frozen manifest, dates and run root. Resolve missing values from those artifacts; report unresolved fields to the coordinator instead of inventing them.
Use the parent Grok model for every pstack role (inherit-parent means omit model). Use the installed poteto-agent wrapper when supported. No nested delegation; the coordinator owns fresh review and shared-file integration. Respect its single-writer checkout assignment.
Follow the exact formulas, clocks, schemas, allowed paths, finite budgets and A01, A02, A03, A04, A05, A06, A07, A08 checks. Name the data shape, implement one vertical behavior, run sensitive tests and the declared native slice/full run, and inspect actual output.
Done means all required artifacts exist and verify_research_release.py task exits 0 on the actual TASK_RECEIPT.json, with truthful coverage and disposition. Return real artifact paths, command results, decision-trail path and limitations. Keep runtime todos in the run's WORK_LOG.md and record playbook skips there.
Apply /workspace/planning/research-program/ASSURANCE.md and the card's assigned silent-failure cases: S01, S02, S03, S06, S07, S11, S12, S13, S15, S22, S24, S32. Produce EVIDENCE_MATRIX.json linking every required check to real code, executed commands, hashes and inspected output selectors. Show sensitive accepted/rejected controls; preserve missing/ambiguous data and all declared jobs. A pass flag or your own verifier alone cannot prove completion. Return the evidence for the coordinator's separate GATE_REVIEW.json; do not edit fixed independent checks to obtain a pass.
Use the specified finite-experiment route, not pstack's agent/prompt Eval protocol or an open-ended Hillclimb. Reconcile every registered trial; a verified negative or inconclusive research result is valid. Do not expand the search to force a winner.
Preserve accepted Phase 1 evidence, raw sources, missing/ambiguous inputs and unsuccessful trials. Perform the local task only; no external publication, shipping workflow or later phase. Do not stop at a plan or a passing toy test.
```

Canonical source: [P15-18.md](/workspace/planning/phase-1-5/tasks/P15-18.md).

## P15-18 — Run one bounded refinement and choose honest dispositions

Status: **planned; implementation not started by this planning task**.

Subphase: `05-finite-search`. Dependencies: P15-17.

### Goal and boundary

Generate the exact neighbors from the past-only allowlist, maximum 24 neighbors and one combination per family/fold. Record duplicates and inapplicable neighbors.

Implement only this task and its declared outputs. Preserve accepted Phase 1 code/reports, immutable sources and raw data. All new numerical recipes are registered research policies unless the source ledger proves literal attribution. No future input, later fit or all-history selected rule may enter an earlier decision.

### Read first

- [AGENTS.md](/workspace/AGENTS.md)
- [ROADMAP.md](/workspace/planning/ROADMAP.md)
- [PSTACK_EXECUTION.md](/workspace/planning/research-program/PSTACK_EXECUTION.md)
- [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md)
- [Assigned failure cases](/workspace/planning/research-program/SILENT_FAILURES.md)
- [WORKFLOW.md](/workspace/planning/research-program/WORKFLOW.md)
- [SEARCH_CONTRACT.md](/workspace/planning/phase-1-5/SEARCH_CONTRACT.md)
- [EVALUATION.md](/workspace/planning/research-program/EVALUATION.md)
- [OUTCOMES.md](/workspace/planning/research-program/OUTCOMES.md)

The named phase specification provides the exact formulas, proposed signatures, units and literal fixtures for this task. Existing symbols are marked as existing; proposed modules/commands are created by their owner tasks. Do not substitute remembered formulas or undocumented library defaults.

### Input and ownership contract

Consume verified predecessor receipts: **P15-17**. Their hashes and actual artifact paths go in this task receipt. Required schema details are in DATA_CONTRACTS; source adapters also read their named method predicates.

Allowed implementation/test paths:

- `/workspace/implementation/src/trading_research/research/rule_discovery/refinement.py`
- `/workspace/implementation/tests/rule_discovery/test_p15_18.py`

A worker does not edit another task’s shared files. Request an explicit integration patch from the subphase coordinator for runner registration, imports or additive shared-schema changes; the coordinator records it and reruns the affected contract tests. Keep independently fitted artifacts separate even when calculators are shared.

### Implementation steps

1. Generate the exact neighbors from the past-only allowlist, maximum 24 neighbors and one combination per family/fold. Record duplicates and inapplicable neighbors.
2. Fit/select on inner data, evaluate unchanged outer blocks, account for every trial, and apply support/uncertainty/multiplicity/frequency gates.
3. Write causal per-fold selected-rule manifests plus a separately labelled all-history descriptive recommendation. Retain B0 when nothing clears promotion.
4. Trace one actual output through its serialized schema, feature/stage parents and native receipt. Then run the verification below and write immutable evidence. A formula unit test alone does not complete a native-data or fitted-expert task.

### Worked and discriminating checks

Use the literal cases in the named mathematical contract and add one independently constructed negative case.

Use the shared [reference vectors](/workspace/planning/research-program/fixtures/reference_vectors.json) where applicable. Add a negative control that fails if the central behavior is removed, reversed, delayed incorrectly or fed future information. Model tests must include a known synthetic signal and a native chronological slice; never demand an empirical market improvement merely to pass software verification.

### Required failure checks

Acceptance amendment: `research-assurance-2026-09-14-v3`. Assigned cases: **S01, S02, S03, S07, S11, S12, S13, S17, S22, S24, S32**. Use the exact probes, expected results and evidence in SILENT_FAILURES.md. Reuse current bound shared evidence where applicable; do not replace the task’s own sensitive/native check with a test count. Preserve prior attempts and produce the common task artifacts listed in TASK_GRAPH.json as well as the task-specific outputs below.

### Acceptance checklist

- [ ] A01: A combination exists only when each ingredient individually passes inner selection.
- [ ] A02: Outer data never select a neighbor or rescue a failed bank.
- [ ] A03: A six-example perfect result remains inconclusive.
- [ ] A04: All unsuccessful trials count in reporting and multiple-trial adjustment.
- [ ] A05: The downstream selected role is time-scoped and never an all-history winner copied backward.
- [ ] A06: Evidence includes command exit codes, artifact hashes, coverage/unknown counts, runtime, actual output inspection and the task’s declared limitations. All predecessor receipts verify.

- [ ] A07: EVIDENCE_MATRIX.json resolves every acceptance key and assigned failure case to actual code, executed commands, hashed evidence and inspected output under ASSURANCE.md; artifact/identity/command forgeries fail.
- [ ] A08: The assigned silent-failure probes pass with sensitive positive and negative controls, honest native/unknown/job counts, and no stale evidence. Return review-ready artifacts; subphase admission additionally requires the coordinator’s matching passing GATE_REVIEW.json.

### Commands and evidence

Commands below are **to run during implementation after their owner task creates the entrypoint**. They have not been run by this planning change. Use the existing environment; do not install arbitrary packages.

```bash
cd /workspace/implementation
.venv/bin/python -m pytest /workspace/implementation/tests/rule_discovery/test_p15_18.py -q
```

Then run the frozen engineering slice with the actual manifest and date list produced by the prerequisite (substitute the three ALL_CAPS paths/values; do not invent dates from outcomes):

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/run_rule_discovery.py slice --run-root RUN_ROOT --manifest FROZEN_MANIFEST --dates FROZEN_DATES --task P15-18
```

Reconcile all required cases, inspect output and profile before a full run. Search/release tasks additionally use the runner’s `run`, `resume` and `summarize` on the same immutable manifest; complete declared jobs before claiming an executed experiment.

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt TASK_RECEIPT_PATH
```

Expected artifacts under the task’s immutable report run (large data shards may be in the ignored cache, with file-level hashes in the manifest):

- `REFINEMENT_BANK.json`
- `TRIALS.jsonl`
- `SELECTED_RULES_BY_FOLD.json`
- `FAMILY_DISPOSITIONS.json`
- `TASK_RECEIPT.json` and `REPORT.md`, including acceptance keys A01–A08 and exact predecessor/artifact hashes.

### Completion and stop rules

Software checks must pass. A native cell may be unsupported only after the specified owned-input search and generic implementation/fixture verification. Sparse or negative research findings retain the baseline and all counts; they do not authorize more unregistered search. An implementation defect, unresolved job or timeout is work remaining. Use the shared receipt statuses; do not mark a phase complete from this individual card.

Any family report prints both the PHASE table and the audit table defined in WORKFLOW.md. Report the real completed behavior, commands, native evidence, limitations and next eligible dependency. Do not claim final profitability, author-exact proprietary recovery or complete native coverage without the required evidence.

### Copyable worker prompt

Generated from the task graph and pstack execution contract by tools/build_research_plan_bundles.py. Edit the canonical task above for research requirements; rebuild this section after prompt changes.

```text
/poteto-mode new task. Run this finite registered research experiment: P15-18 — Run one bounded refinement and choose honest dispositions.
Read /workspace/planning/phase-1-5/tasks/P15-18.md and /workspace/planning/research-program/PSTACK_EXECUTION.md. Use the installed pstack router and the card's required contracts; this is execution of an existing specification.
Use the coordinator's actual working root, code identity, predecessor receipt paths/hashes, frozen manifest, dates and run root. Resolve missing values from those artifacts; report unresolved fields to the coordinator instead of inventing them.
Use the parent Grok model for every pstack role (inherit-parent means omit model). Use the installed poteto-agent wrapper when supported. No nested delegation; the coordinator owns fresh review and shared-file integration. Respect its single-writer checkout assignment.
Follow the exact formulas, clocks, schemas, allowed paths, finite budgets and A01, A02, A03, A04, A05, A06, A07, A08 checks. Name the data shape, implement one vertical behavior, run sensitive tests and the declared native slice/full run, and inspect actual output.
Done means all required artifacts exist and verify_research_release.py task exits 0 on the actual TASK_RECEIPT.json, with truthful coverage and disposition. Return real artifact paths, command results, decision-trail path and limitations. Keep runtime todos in the run's WORK_LOG.md and record playbook skips there.
Apply /workspace/planning/research-program/ASSURANCE.md and the card's assigned silent-failure cases: S01, S02, S03, S07, S11, S12, S13, S17, S22, S24, S32. Produce EVIDENCE_MATRIX.json linking every required check to real code, executed commands, hashes and inspected output selectors. Show sensitive accepted/rejected controls; preserve missing/ambiguous data and all declared jobs. A pass flag or your own verifier alone cannot prove completion. Return the evidence for the coordinator's separate GATE_REVIEW.json; do not edit fixed independent checks to obtain a pass.
Use the specified finite-experiment route, not pstack's agent/prompt Eval protocol or an open-ended Hillclimb. Reconcile every registered trial; a verified negative or inconclusive research result is valid. Do not expand the search to force a winner.
Preserve accepted Phase 1 evidence, raw sources, missing/ambiguous inputs and unsuccessful trials. Perform the local task only; no external publication, shipping workflow or later phase. Do not stop at a plan or a passing toy test.
```
