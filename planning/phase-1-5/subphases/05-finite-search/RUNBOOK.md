# Phase 1.5 / 05-finite-search — coordinator runbook

Status: **planned; not implemented by this planning task**. Generated from canonical contracts and task cards. Edit those sources, then rebuild; do not edit this bundle independently.

Source content SHA256: `456d1a03d7890d6c62c645a4d12e18843377cfd1188d1962456cbf643b858444`.

Previous gate: **04-family-adapters**. External task dependencies: P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16. Read and verify their actual receipts before implementation.

## Coordinator work order

Enter through /poteto-mode new task and run only this bounded subphase to its verification predicate. Match the installed playbook, copy its steps into runtime todos and record explicit skip reasons. Apply the included Grok-only model and host-capability overrides to all routed skills. A large-task figure-it-out route must use this existing runbook, not invent a new research plan.

Implement only the tasks listed below, in dependency order. Start with one verified vertical slice. Delegate bounded cards with the complete brief in PSTACK_EXECUTION; a shared checkout has one code writer at a time. At most three live Grok/poteto agents including the coordinator; unavailable workers mean sequential execution. The coordinator reviews and integrates shared schemas/runners and alone writes SUBPHASE_RECEIPT.json.

Read workspace AGENTS.md. The executable contracts and task cards are included below. Source method wiki pages linked by a task are additional focused worker reads; they retain the precise author predicates. Do not reread the whole archive or invent alternative formulas.

The native slice, numerical checks, coverage, future perturbation, actual output inspection and immutable receipts are part of the task. A negative/inconclusive research result is valid; missing implementation is not. Preserve prior evidence and all unsuccessful trials. Do not start the next subphase automatically.

| Task | Dependencies | Canonical card |
| --- | --- | --- |
| P15-17 — Execute and reconcile the breadth screen | P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16 | [Task](/workspace/planning/phase-1-5/tasks/P15-17.md) |
| P15-18 — Run one bounded refinement and choose honest dispositions | P15-17 | [Task](/workspace/planning/phase-1-5/tasks/P15-18.md) |

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

This runbook includes only cases assigned to: P15-17, P15-18.

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

### S06 — Calendar-only coverage and favorable date substitution

Assigned tasks: P15-00, P15-02, P15-03, P15-17, P15-20, P2-00, P2-01, P2-09, P2-24.

**Probe:** Use an open current session with a missing same-contract prior profile; use a complete current slice with incomplete model lookback history; remove the only complete date in a year.

**Expected:** Affected input groups remain partial/missing; unaffected groups keep their own denominators. The deterministic slot becomes missing or the first genuinely complete date by the fixed coverage rule, never by outcomes. Unknown feed completeness remains unknown.

**Evidence:** Per-group coverage rows, native receipt hashes, required lookback intervals, selection replay and partial/roll/holiday/gap fixtures.

### S07 — Synthetic data presented as native evidence

Assigned tasks: P15-00, P15-02, P15-03, P15-05, P15-06, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-17, P15-18, P15-19, P15-20, P2-00, P2-01, P2-03, P2-04, P2-05, P2-06, P2-07, P2-08, P2-09, P2-10, P2-11, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-22, P2-23, P2-24.

**Probe:** Reopen one actual native artifact and row named in the output lineage and replay the named adapter. Separately include a clearly marked synthetic missing/ambiguous fixture.

**Expected:** Native values, contract and event/availability clocks match the identified source. Synthetic examples are labelled synthetic. A fabricated row ID or unavailable file fails.

**Evidence:** Source path/hash/row, adapter callable, serialized output selector and independently replayed comparison.

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

### S22 — Changed rules only filter old winners or reset contact state

Assigned tasks: P15-05, P15-07, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-17, P15-18.

**Probe:** Construct an opportunity created by new geometry but absent from the baseline qualifying set. Update a developing reference value within one lifecycle; test expiry-only time advancement and rearm just below/at the threshold.

**Expected:** Changed rules enumerate their own eligible formations/contacts. Reference versions preserve lifecycle touch history. Deadlines advance without a trade and rearm uses the frozen predicate; no duplicate opportunity appears from value refresh.

**Evidence:** Baseline/candidate population IDs, boundary transition traces and lifecycle/rearm fixtures.

### S24 — Unregistered trials or outcome-driven selection

Assigned tasks: P15-08, P15-17, P15-18, P15-19, P15-20, P2-23, P2-24.

**Probe:** Compare the frozen candidate/job bank to every executed attempt, including failures, unsupported cells and B0/B1/B2 versions. Alter only held-out outcomes and re-run selection.

**Expected:** No trial is missing, duplicated, renamed away or added outside the finite budget. Selection uses only the allowed training/tuning evidence and retains fold-specific rules. A negative result cannot trigger unregistered search or deletion.

**Evidence:** Set reconciliation of planned/executed/failed/selected IDs, immutable trial ledger, fold selections and exposure history.

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

Canonical source: [SEARCH_CONTRACT.md](/workspace/.worktrees/docs-amend/planning/phase-1-5/SEARCH_CONTRACT.md).

## Finite breadth and refinement search

Owner `P15-08` registers the candidate bank; `P15-17` executes breadth; `P15-18` refines. Read [specification](/workspace/.worktrees/docs-amend/planning/phase-1-5/SPEC.md), [evaluation](/workspace/planning/research-program/EVALUATION.md), [outcomes](/workspace/planning/research-program/OUTCOMES.md) and [retention](/workspace/.worktrees/docs-amend/planning/research-program/RETENTION.md) together.

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
| Timing | T1 source reversal/action window +15m; T2 window -15m using only an already complete formation; T3 condition-defined morning reversal | JJ judas_reversal/other_session and GB nyam_box custom siblings. If formation is not yet available at T2, omit with a reason; never truncate a source range and call it unchanged. |

This is at most 19 nonbaseline axis recipes per branch, but only applicable cells are created. `P15-08` emits a concrete expanded `candidate-bank.json` with a maximum of 160 nonbaseline branch candidates for the breadth round, plus all baseline branches. If the mechanical expansion exceeds160, apply round-robin by bank then family then branch ID, taking one candidate per applicable family/bank before second candidates; preserve deferred cells and their deterministic order. No result may affect this expansion. This cap is a first-stage breadth budget, not a claim that exactly 160 models should exist.

Separate method adapters own source constraints and construction. `P15-09` Jumbo; `P15-10` GB-FAIL; `P15-11` GB-VWAP/scalps; `P15-12` Sires; `P15-13` Saint; `P15-14` Member; `P15-15` Keani; `P15-16` research processes. Context/research/risk units never enter entry-setup denominators because their candidate bank has a row.

### Custom reversal timing recipe

T1/T2 shift the action-window start and end together by the registered offset, keeping formation already complete; source-identity output remains B0 and changed clocks use custom sibling IDs. Their expiry is the shifted window end, capped at account-day flatten. T3 uses the source-frozen overnight/range reference and a 09:30–12:00 ET custom action window. Require a strict edge sweep, then a complete trailing 15-minute balance with width<=.75 of the 60-minute scale ending before that balance and efficiency<=.35, then the S1 reclaim within 10 minutes. Entry follows that causal reclaim, structural stop is beyond the swept extreme by1 tick, objective is the still-unconsumed opposite frozen edge, and expiry is the earlier of 60 minutes after qualification or 12:00. If the objective is already consumed after the sweep, reject it. Retain all unchanged source context that can be evaluated before contact; publish the timing/balance additions as our hypothesis, not an author Judas formula. This tests condition-based reversal beyond a small clock adjustment.

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

Canonical source: [SPEC.md](/workspace/.worktrees/docs-amend/planning/phase-1-5/SPEC.md).

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

Canonical source: [DELIVERABLES.md](/workspace/.worktrees/docs-amend/planning/research-program/DELIVERABLES.md).

## Phase deliverables and definition of done

Receipts, matrices and gate reviews prove that software ran and that checks passed. This contract defines what the user receives at the end of each phase and the exact artifact that marks a phase finished. It adds reporting requirements; it changes no formula, budget, gate or date.

### Phase 1.5 outcome: Strategy Book, version 1

One entry per family and per branch in the frozen Phase 1 registry, including research, process and risk units, with entry setups distinguished from observations. Every number carries a pointer to the immutable artifact it was computed from. Sections per branch:

1. **Definition.** Source method, branch, ordered stages, reference, confirmation, structural stop and objective, expiry, session clock, and for every operand whether it is source-exact, printed-but-different, inferred or not identifiable, linking the source-reconstruction ledger row.
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

Canonical source: [RETENTION.md](/workspace/.worktrees/docs-amend/planning/research-program/RETENTION.md).

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

Canonical source: [P15-17.md](/workspace/.worktrees/docs-amend/planning/phase-1-5/tasks/P15-17.md).

## P15-17 — Execute and reconcile the breadth screen

Status: **planned; implementation not started by this planning task**.

Subphase: `05-finite-search`. Dependencies: P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16.

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

Consume verified predecessor receipts: **P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16**. Their hashes and actual artifact paths go in this task receipt. Required schema details are in DATA_CONTRACTS; source adapters also read their named method predicates.

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

Acceptance amendment: `research-assurance-2026-09-14-v2`. Assigned cases: **S01, S02, S03, S06, S07, S11, S12, S13, S15, S22, S24, S32**. Use the exact probes, expected results and evidence in SILENT_FAILURES.md. Reuse current bound shared evidence where applicable; do not replace the task’s own sensitive/native check with a test count. Preserve prior attempts and produce the common task artifacts listed in TASK_GRAPH.json as well as the task-specific outputs below.

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

Canonical source: [P15-18.md](/workspace/.worktrees/docs-amend/planning/phase-1-5/tasks/P15-18.md).

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

Acceptance amendment: `research-assurance-2026-09-14-v2`. Assigned cases: **S01, S02, S03, S07, S11, S12, S13, S17, S22, S24, S32**. Use the exact probes, expected results and evidence in SILENT_FAILURES.md. Reuse current bound shared evidence where applicable; do not replace the task’s own sensitive/native check with a test count. Preserve prior attempts and produce the common task artifacts listed in TASK_GRAPH.json as well as the task-specific outputs below.

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
