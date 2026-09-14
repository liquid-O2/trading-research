# Phase 1.5 / 00-foundation — coordinator runbook

Status: **planned; not implemented by this planning task**. Generated from canonical contracts and task cards. Edit those sources, then rebuild; do not edit this bundle independently.

Source content SHA256: `7e23922646fbd9ebde655643c5793db5b6103ee556e7021465acd23767020c8c`.

Previous gate: **accepted Phase 1 census**. External task dependencies: none beyond the accepted baseline. Read and verify their actual receipts before implementation.

## Coordinator work order

Enter through /poteto-mode new task and run only this bounded subphase to its verification predicate. Match the installed playbook, copy its steps into runtime todos and record explicit skip reasons. Apply the included Grok-only model and host-capability overrides to all routed skills. A large-task figure-it-out route must use this existing runbook, not invent a new research plan.

Implement only the tasks listed below, in dependency order. Start with one verified vertical slice. Delegate bounded cards with the complete brief in PSTACK_EXECUTION; a shared checkout has one code writer at a time. At most three live Grok/poteto agents including the coordinator; unavailable workers mean sequential execution. The coordinator reviews and integrates shared schemas/runners and alone writes SUBPHASE_RECEIPT.json.

Read workspace AGENTS.md. The executable contracts and task cards are included below. Source method wiki pages linked by a task are additional focused worker reads; they retain the precise author predicates. Do not reread the whole archive or invent alternative formulas.

The native slice, numerical checks, coverage, future perturbation, actual output inspection and immutable receipts are part of the task. A negative/inconclusive research result is valid; missing implementation is not. Preserve prior evidence and all unsuccessful trials. Do not start the next subphase automatically.

| Task | Dependencies | Canonical card |
| --- | --- | --- |
| P15-00 — Bind the accepted baseline and define typed records | bootstrap | [Task](/workspace/planning/phase-1-5/tasks/P15-00.md) |
| P15-01 — Build receipt and dependency verification | P15-00 | [Task](/workspace/planning/phase-1-5/tasks/P15-01.md) |

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

This runbook includes only cases assigned to: P15-00, P15-01.

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

### S04 — Forged dependency or phase closure

Assigned tasks: P15-01, P15-20, P2-00, P2-24.

**Probe:** Use a child whose correctly hashed predecessor is blocked; reuse P15-00 for another task ID; pass an unknown empty subphase; claim a Phase 2 release using a pass string without the Phase 1.5 release; introduce a receipt/graph cycle.

**Expected:** All fail recursively for the intended dependency/gate reason. Correct bootstrap, known subphase and legitimate complete miniature phase fixtures pass. A version-1 graph cannot waive the current assurance amendment.

**Evidence:** Public CLI cases plus isolated fixtures preserving unrelated valid fields. Final releases also include the fixed foundation suite.

### S05 — Nested future evidence and mutable frozen records

Assigned tasks: P15-00, P15-01, P15-02, P15-03, P15-05, P15-06, P15-07, P2-00, P2-01, P2-02, P2-22.

**Probe:** Put evidence available at 100 under a record issued at 10, including a nested child issued at 100. Repeat at each evidence-bearing type and deserializer. Mutate caller-owned nested dictionaries/lists after construction.

**Expected:** Every relevant boundary rejects late/malformed evidence. The ancestor cutoff remains 10. Aliased mutation cannot alter the stored record or canonical hash. Forecast train_end <= fit_available <= issue is enforced.

**Evidence:** Per-type parameterized boundary tests, round-trip tests and lineage CLI cases, with explicitly typed outcome edges.

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

### S10 — DST, session or roll leakage

Assigned tasks: P15-00, P15-02, P15-03, P15-05, P2-00, P2-01, P2-03, P2-09, P2-22.

**Probe:** Use the DST transition, a verified early close, an unverified holiday, a contract roll and a missing same-contract lookback. Change later contract volume after the account-day contract was selected.

**Expected:** Timezone-aware session intervals and flatten time match the bound policy. No cross-roll native price/reference is silently stitched. Later volume cannot change causal contract selection. Archive membership and executable contract policy remain distinct.

**Evidence:** Expected UTC/local clocks, source calendar/expiry evidence, contract IDs and unsupported/mismatch counts.

### S13 — Stale cache or conflicting immutable root

Assigned tasks: P15-00, P15-02, P15-05, P15-17, P15-18, P2-01, P2-02, P2-09, P2-10, P2-12, P2-23.

**Probe:** Change one input byte, contract, schema version, transform version, relevant parameter and cutoff in turn. Exercise cold/warm caches and retry a frozen root with conflicting configuration.

**Expected:** Every semantic change gets an appropriate new identity or explicit rejection; no stale object is reused. Cold/warm results match. Conflicting roots fail; interrupted writes cannot appear as valid completed shards.

**Evidence:** Cache key inventory, mutation results and immutable-write/restart tests; retain timing separately from semantic hashes.

### S14 — Unit, sign, precision and nonfinite errors

Assigned tasks: P15-00, P15-03, P15-05, P15-06, P15-19, P2-02, P2-03, P2-10, P2-11, P2-12, P2-22.

**Probe:** Use the literal reference vectors and mirror long/short cases. Check ticks versus points/dollars, seconds versus ns/years, percent versus decimal, prices versus returns and contract multipliers. Inject nested NaN/Infinity, bool clocks and numeric overflow.

**Expected:** Independent expected arithmetic matches within a predeclared justified tolerance. Invalid values fail or receive the contract’s explicit unsupported disposition; no broad exception-to-zero or silently clipped valid geometry.

**Evidence:** Literal inputs/units, expected/actual numbers, tolerance and source equation; edge and finite-domain tests.

### S31 — Provenance or unsupported input silently relabelled

Assigned tasks: P15-00, P15-04, P15-08, P15-09, P15-10, P15-11, P15-12, P15-13, P15-14, P15-15, P15-16, P15-20, P2-00, P2-08, P2-09, P2-21, P2-24.

**Probe:** Round-trip an unknown source_exact field, a source-inspired operational rule, missing proprietary constants, cash-index input limits and personal-execution-only data.

**Expected:** Unknown does not become true or false implicitly; proxies remain labelled. Generic implementation still passes fixtures when native cells are unsupported. Personal risk/process records do not gate market setup definitions.

**Evidence:** Raw/normalized round-trip, source/operator ledger, scope/availability receipts and downstream allowlist with exact limitations.

Canonical source: [FOUNDATION_REPAIR.md](/workspace/.worktrees/docs-amend/planning/research-program/FOUNDATION_REPAIR.md).

## Repair 00-foundation before the next subphase

The 2026-09-14 review found that the original completion is not safe to use as a dependency gate. The implementer's 25 tests passed, but the independent 27-case suite accepted 18 invalid cases. Valid controls still passed. Read the [review](/workspace/.worktrees/docs-amend/planning/research-program/reviews/00-foundation-2026-09-14/REVIEW.md), [recorded counterexamples](/workspace/.worktrees/docs-amend/planning/research-program/reviews/00-foundation-2026-09-14/adversarial-confirmed/RESULTS.json) and [amendment](/workspace/.worktrees/docs-amend/planning/research-program/AMENDMENTS.json). `01-native-and-outcomes` waits for repaired foundation receipts and a matching passing review.

This repair is an implementation work order when the user sends the prompt. Authoring this document did not fix the implementation. Do not rerun the Phase 1 census, fit Phase 2 models, or rewrite accepted evidence to repair the foundation.

### Preserve the reviewed attempt

The historical receipts are evidence of what ran, not current admission:

- [P15-00](/workspace/implementation/reports/research-work/P15-00/b291864ccceaca9a/attempt-0001/TASK_RECEIPT.json).
- [P15-01](/workspace/implementation/reports/research-work/P15-01/039267553e8bf721/attempt-0001/TASK_RECEIPT.json).
- [00-foundation](/workspace/implementation/reports/research-work/00-foundation/f7135f8d696ff1f5/attempt-0001/SUBPHASE_RECEIPT.json).

Their hashes and the seven reviewed source/test/tool hashes are in [REVIEWED_IDENTITIES.json](/workspace/.worktrees/docs-amend/planning/research-program/reviews/00-foundation-2026-09-14/REVIEWED_IDENTITIES.json). Leave these files and all earlier attempts intact. New task runs have v2 plan/code snapshots, the new assurance version, new semantic run IDs and explicit supersession references in their reports/exposure ledger. Preserve previously exposed engineering dates and declare the coverage correction before any new outcome inspection. Do not simply add A07–A13 booleans to the old receipt.

### Work in this order

1. Read the current [foundation runbook](/workspace/planning/phase-1-5/subphases/00-foundation/RUNBOOK.md), [ASSURANCE.md](/workspace/.worktrees/docs-amend/planning/research-program/ASSURANCE.md) and assigned failure cases. Inspect the existing modules before editing. The repair owns only the P15-00/P15-01 implementation/test paths and new immutable report outputs. The coordinator may update concise wiki status/evidence links after review. Fixed audit tools, canonical assurance requirements and preserved review outputs are outside the implementation writer's ownership.
2. Reproduce the existing failures using isolated copies. The recorded before-run used the [original graph snapshot](/workspace/.worktrees/docs-amend/planning/research-program/reviews/00-foundation-2026-09-14/TASK_GRAPH_BEFORE.json), so its valid controls test original behavior without the later acceptance amendment creating unrelated missing-key failures. Retain that evidence. It does not authorize admission under an old graph after repair. Each implementation unit test must isolate its intended failure reason; the independent suite is an additional minimum check.
3. Repair required artifacts, snapshot/draft identities, recursive predecessor/task/phase verification, command/log enforcement and evidence-matrix validation. Add valid miniature bootstrap/subphase/phase fixtures alongside the negative cases. Test `--gate-review` with missing, stale, wrong-receipt, wrong-code, unresolved-issue and forged review references. Serialize task artifacts first, task receipts next, coordinator subphase/phase candidates next, and final review sidecars last; never create circular hashes.
4. Repair every nested clock/schema boundary, including deserialization and recursive immutability. A child cutoff cannot relax an ancestor cutoff. Evidence leaves need real hashes/row references. Correct the already-present Forecast boundary: `train_end <= fit_available <= issue`, with finite supported outputs. Preserve that tested public record; do not remove it to bypass the negative case. This is a boundary repair, not permission to implement Phase 2 fitting.
5. Replace calendar-only engineering coverage with deterministic per-input-group native coverage and required lookback intervals. In particular, [2020-01-02 Keani coverage](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/jobs/evaluation/2020-01-02/KEANI-OPEN-ABOVE-VALUE--branch--source_long.json.gz) has an open complete current prefix but a prior-scope omission with 390 unknown minute intervals. It cannot prove a complete prior-profile group. Use accepted calendar/reconstruction and coverage receipts without rereading outcomes to choose dates. Preserve missing slots, roll/holiday uncertainty, and unknown feed completeness. Implement executable gap/batch fixtures and reopen/replay at least one actual native row through the new record schema; generated records remain labelled synthetic.
6. Produce each task's common artifacts and A01–A13 evidence, run targeted tests and inspect actual output. P15-01 validates the new P15-00 receipt retrospectively. The coordinator creates a new immutable subphase candidate, runs the fixed independent suite against these new receipts, and performs the separate behavior review. Resolve all findings and regenerate only affected descendants under new identities. Preserve failed runs.
7. Validate both the candidate and its matching passing review. Update the wiki with exact new evidence links, superseded old admission and limitations. Return the next eligible `01-native-and-outcomes` prompt only after this gate passes; do not execute that subphase in this repair task.

### Exact validation commands

Use the existing environment. Substitute the actual **new v2** receipt/review paths and a **new** output directory in the final commands; do not reuse the reviewed v1 receipts as passing controls for final admission.

```bash
cd /workspace/implementation
.venv/bin/python -m pytest tests/rule_discovery/test_p15_00.py tests/rule_discovery/test_p15_01.py -q -p no:cacheprovider
.venv/bin/python tools/verify_research_release.py task --receipt NEW_P15_00_RECEIPT
.venv/bin/python tools/verify_research_release.py task --receipt NEW_P15_01_RECEIPT
.venv/bin/python tools/verify_research_release.py subphase --receipt NEW_SUBPHASE_RECEIPT
.venv/bin/python /workspace/tools/check_foundation_adversarial.py --p15-00 NEW_P15_00_RECEIPT --p15-01 NEW_P15_01_RECEIPT --subphase NEW_SUBPHASE_RECEIPT --output-root NEW_INDEPENDENT_OUTPUT_ROOT
.venv/bin/python tools/verify_research_release.py subphase --receipt NEW_SUBPHASE_RECEIPT --gate-review NEW_GATE_REVIEW
```

The independent checker is already implemented at [check_foundation_adversarial.py](/workspace/tools/check_foundation_adversarial.py); its hash and case count are pinned in [ASSURANCE_CASES.json](/workspace/.worktrees/docs-amend/planning/research-program/ASSURANCE_CASES.json). Exit 0 means every positive and negative case matched. Exit 1 means a behavior failed; exit 2 means the checker could not run, which is also not a pass. Its `RESULTS.json` hashes the checker and its actual receipt/graph inputs. Do not edit the checker, replace it with an implementation helper, filter cases, or cite a stale result after code changes. A closed final review must also inspect coverage/native evidence and the assigned cases outside this fixed suite.

The source-grounded baseline preservation check compares the frozen Phase 1 registry's 248 software file hashes, rather than the newly enlarged whole-tree software identity. Keep accepted reports and raw data intact. Scope the targeted tests to this repair and affected contract/native behavior; full Phase 1 measurement is not a prerequisite to repair these defects.

### Copyable repair prompt

<!-- copyable-repair-start -->
```text
/poteto-mode new task. Repair Phase 1.5 subphase 00-foundation in /workspace from its rejected 2026-09-14 review; do not start 01-native-and-outcomes.
Read /workspace/AGENTS.md, /workspace/planning/research-program/FOUNDATION_REPAIR.md and /workspace/planning/phase-1-5/subphases/00-foundation/RUNBOOK.md. Follow PSTACK_EXECUTION.md through the installed pstack router; this is a bounded bug-fix execution of the existing amended specification, not a new planning task. No second go is needed.
Use the parent Grok model for every role. At most three live Grok/poteto agents including the coordinator, no nested worker delegation, and one code writer per shared checkout. The coordinator owns shared integration and a fresh behavior review. Give each worker actual inputs, code identity, owned paths and expected observations. If workers are unavailable, execute sequentially and record the review limitation.
Preserve the original reviewed receipts, reports and Phase 1 code/data identities. Reproduce the supplied counterexamples, then repair their root causes in the P15-00/P15-01 owned code and tests. Enforce required parsed artifacts and actual identity binding, recursive dependency/phase admission, unexcused required command failures, every nested clock/schema boundary, per-input-group coverage/lookbacks and an actual native record replay. The frozen independent checker is outside your edit ownership. Do not patch pass flags, weaken checks, substitute synthetic evidence for native, or suppress missing data to close the task.
Apply ASSURANCE.md and every assigned silent-failure case. Record EVIDENCE_MATRIX.json, measured commands/logs and your own WORK_LOG.md/DECISIONS.tsv. Use new v2 snapshots, manifests, receipts and supersession/exposure records; do not rewrite old plan identities or accepted artifacts. Finalize task receipts before the coordinator candidate, then the independent check result and GATE_REVIEW.json to avoid circular hashes.
Keep going until targeted tests and all assigned checks pass, actual new task/subphase receipts verify, /workspace/tools/check_foundation_adversarial.py passes all 27 controls/counterexamples on the new receipts, and subphase verification with the matching passing --gate-review exits 0. Independently inspect code and outputs; the worker summary, log audit and self-authored verifier alone are insufficient. Return the exact repair, evidence links, unresolved limitations and next eligible prompt. Stop at the foundation boundary. Local work only; no PR/push/merge, external messages, Phase 1 census or Phase 2 implementation.
```
<!-- copyable-repair-end -->

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

Canonical source: [TYPE_REFERENCE.py](/workspace/.worktrees/docs-amend/planning/research-program/TYPE_REFERENCE.py).

## Type declaration blueprint

```python
"""Schema blueprint for P15-00/P2-00; not an implemented research package.

The task owners place these declarations in the specified package, implement
boundary validation, and add the numerical behavior from the Markdown contracts.
Money/prices use Decimal; all clocks are UTC nanoseconds. No algorithm runs here.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Iterable, Literal, Protocol, TypeAlias

Ns: TypeAlias = int
AssetId: TypeAlias = str
Side: TypeAlias = Literal[-1, 1]
JSONValue: TypeAlias = None | bool | int | float | str | list["JSONValue"] | dict[str, "JSONValue"]


class Coverage(Enum):
    COMPLETE = "complete_observed_scope"
    PARTIAL = "partial"
    MISSING = "missing"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    path: str
    sha256: str
    schema_version: str
    byte_count: int
    row_count: int | None


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
class CoverageReceipt:
    start_ns: Ns
    end_ns: Ns
    status: Coverage
    expected_matching_intervals: tuple[tuple[Ns, Ns], ...]
    observed_intervals: tuple[tuple[Ns, Ns], ...]
    missing_intervals: tuple[tuple[Ns, Ns], ...]
    calendar_sha256: str
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class NativeTrade:
    event_id: str
    asset_id: AssetId
    event_ns: Ns
    available_at_ns: Ns
    price: Decimal
    quantity: int
    aggressor: Side | None
    evidence: EvidenceRef


@dataclass(frozen=True, slots=True)
class NativeBatch:
    batch_id: str
    event_ns: Ns
    available_at_ns: Ns
    trades: tuple[NativeTrade, ...]
    internal_order_known: bool


@dataclass(frozen=True, slots=True)
class QuoteBatch:
    batch_id: str
    asset_id: AssetId
    event_ns: Ns
    available_at_ns: Ns
    bid: Decimal | None
    ask: Decimal | None
    bid_size: int | None
    ask_size: int | None
    ambiguous: bool
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class Bar:
    bar_id: str
    asset_id: AssetId
    start_ns: Ns
    end_ns: Ns
    available_at_ns: Ns
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal | None
    volume: int
    known_signed_volume: int
    unknown_aggressor_volume: int
    coverage: Coverage
    evidence: tuple[EvidenceRef, ...]


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


@dataclass(frozen=True, slots=True)
class RuleSpec:
    rule_id: str
    family: str
    source_branch: str | None
    version: str
    provenance: Literal["source_literal", "source_inspired", "custom"]
    baseline_rule_id: str | None
    changed_axis: str
    parameters: dict[str, str | int | bool]
    required_inputs: tuple[str, ...]
    required_stages: tuple[str, ...]
    formation_policy: str
    expiry_policy: str


@dataclass(frozen=True, slots=True)
class Formation:
    formation_id: str
    asset_id: AssetId
    start_ns: Ns
    end_ns: Ns
    available_at_ns: Ns
    high: Decimal
    low: Decimal
    volume: int
    profile_id: str | None
    construction_kind: str
    parent_ids: tuple[str, ...]
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class Reference:
    reference_id: str
    reference_lifecycle_id: str
    formation_id: str
    asset_id: AssetId
    lower: Decimal
    upper: Decimal
    issue_at_ns: Ns
    expiry_at_ns: Ns
    permitted_sides: tuple[Side, ...]
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class Contact:
    contact_id: str
    reference_id: str
    batch_id: str
    at_ns: Ns
    available_at_ns: Ns
    side: Side
    kind: Literal["touch", "strict_sweep", "ambiguous"]
    possible_prices: tuple[Decimal, ...]
    departure_evidence: tuple[EvidenceRef, ...]
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class PredicateEvidence:
    name: str
    value: bool | None
    available_at_ns: Ns | None
    evidence: tuple[EvidenceRef, ...]
    missing_reason: str | None


@dataclass(frozen=True, slots=True)
class ContextEvidence:
    family: str
    branch: str
    reference_id: str
    at_ns: Ns
    predicates: tuple[PredicateEvidence, ...]


@dataclass(frozen=True, slots=True)
class SequenceSpec:
    recipe_id: str
    ordered_stages: tuple[str, ...]
    deadline_seconds: int
    parameters: dict[str, str | int | bool]


@dataclass(frozen=True, slots=True)
class SequenceState:
    sequence_id: str
    recipe_id: str
    contact_id: str
    state: str
    state_at_ns: Ns
    available_at_ns: Ns
    deadline_ns: Ns
    stage_evidence: tuple[PredicateEvidence, ...]
    terminal_reason: str | None
    working_memory: dict[str, JSONValue]


@dataclass(frozen=True, slots=True)
class SequenceInputs:
    reference: Reference
    context: ContextEvidence
    completed_bars: tuple[Bar, ...]
    flow_features: tuple[FeatureValue, ...]
    available_at_ns: Ns


@dataclass(frozen=True, slots=True)
class Opportunity:
    opportunity_id: str
    parent_opportunity_id: str | None
    overlap_group_id: str
    rule_id: str
    family: str
    branch: str
    account_day: str
    side: Side
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


@dataclass(frozen=True, slots=True)
class ScanResult:
    opportunities: tuple[Opportunity, ...]
    rejected_contacts: tuple[Contact, ...]
    unknown_contacts: tuple[Contact, ...]
    formations: tuple[Formation, ...]
    sequences: tuple[SequenceState, ...]
    coverage: CoverageReceipt
    baseline_payloads: tuple[dict[str, JSONValue], ...]


BaselineResult: TypeAlias = ScanResult


@dataclass(frozen=True, slots=True)
class TargetRow:
    target_row_id: str
    snapshot_id: str
    target_id: str
    account_day: str
    interval_start_ns: Ns
    interval_end_ns: Ns
    label_available_at_ns: Ns | None
    value: float | str | None
    unit: str
    event_kind: str
    censor_at_ns: Ns | None
    coverage: Coverage
    evidence: tuple[EvidenceRef, ...]


@dataclass(frozen=True, slots=True)
class SplitManifest:
    split_id: str
    fit_days: tuple[str, ...]
    tune_days: tuple[str, ...]
    calibration_days: tuple[str, ...]
    test_days: tuple[str, ...]
    purged_row_ids: tuple[str, ...]
    embargo_days: tuple[str, ...]
    fit_cutoff_ns: Ns
    selection_cutoff_ns: Ns
    label_availability_cutoff_ns: Ns
    exposure_ledger_sha256: str


@dataclass(frozen=True, slots=True)
class ExpertDataset:
    dataset_id: str
    snapshots: ArtifactRef
    targets: ArtifactRef
    predictor_matrix: ArtifactRef
    row_ids: ArtifactRef
    columns: tuple[str, ...]
    target_ids: tuple[str, ...]
    feature_dictionary: ArtifactRef
    target_dictionary: ArtifactRef
    parent_prediction_manifests: tuple[ArtifactRef, ...]
    rule_selection_manifests: tuple[ArtifactRef, ...]


@dataclass(frozen=True, slots=True)
class ExpertConfig:
    expert_id: str
    feature_groups: tuple[str, ...]
    feature_columns: tuple[str, ...]
    target_heads: tuple[str, ...]
    target_units: tuple[str, ...]
    recipe: str
    hyperparameter_grid: dict[str, list[JSONValue]]
    hinge_product_pairs: tuple[tuple[str, str], ...]
    fit_schedule: str
    support_policy: str
    fallback_policy: str
    ablation_groups: tuple[str, ...]
    policy_sha256: str


@dataclass(frozen=True, slots=True)
class ExpertArtifact:
    expert_id: str
    artifact_id: str
    config: ArtifactRef
    dataset_id: str
    split_id: str
    preprocessing: ArtifactRef
    coefficients: ArtifactRef
    calibration: ArtifactRef
    support_by_head: dict[str, str]
    training_row_ids: ArtifactRef
    train_end_ns: Ns
    fit_available_at_ns: Ns
    parent_artifacts: tuple[ArtifactRef, ...]


ModelArtifact: TypeAlias = ExpertArtifact


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
    support: str
    train_end_ns: Ns
    fit_available_at_ns: Ns
    input_feature_ids: tuple[str, ...]
    parent_forecast_ids: tuple[str, ...]


class MarketView(Protocol):
    def executions(self, start_ns: Ns, end_ns: Ns) -> Iterable[NativeBatch]: ...
    def quotes(self, start_ns: Ns, end_ns: Ns) -> Iterable[QuoteBatch]: ...
    def coverage(self, start_ns: Ns, end_ns: Ns) -> CoverageReceipt: ...
    def completed_bars(self, start_ns: Ns, end_ns: Ns, seconds: int) -> tuple[Bar, ...]: ...


class Expert(Protocol):
    def fit(self, dataset: ExpertDataset, split: SplitManifest, config: ExpertConfig) -> ExpertArtifact: ...
    def predict(self, artifact: ExpertArtifact, snapshots: tuple[Snapshot, ...]) -> tuple[Forecast, ...]: ...
    def serialize(self, artifact: ExpertArtifact, destination: str) -> ArtifactRef: ...
    def load(self, artifact: ArtifactRef) -> ExpertArtifact: ...
    def explain_inputs(self, artifact: ExpertArtifact) -> dict[str, JSONValue]: ...

```

Canonical source: [P15-00.md](/workspace/.worktrees/docs-amend/planning/phase-1-5/tasks/P15-00.md).

## P15-00 — Bind the accepted baseline and define typed records

Status: **planned; implementation not started by this planning task**.

Subphase: `00-foundation`. Dependencies: none (bootstrap task).

### Goal and boundary

Read the accepted historical measurement report and its actual registry/protocol/composed-calendar/input receipts. Record baseline code/data/registry identities, all 58 units, scope kinds and per-branch input limits. Do not reconstruct a baseline identity from the current wiki hash.

Implement only this task and its declared outputs. Preserve accepted Phase 1 code/reports, immutable sources and raw data. All new numerical recipes are registered research policies unless the source ledger proves literal attribution. No future input, later fit or all-history selected rule may enter an earlier decision.

### Read first

- [AGENTS.md](/workspace/AGENTS.md)
- [ROADMAP.md](/workspace/planning/ROADMAP.md)
- [PSTACK_EXECUTION.md](/workspace/planning/research-program/PSTACK_EXECUTION.md)
- [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md)
- [Assigned failure cases](/workspace/planning/research-program/SILENT_FAILURES.md)
- [WORKFLOW.md](/workspace/planning/research-program/WORKFLOW.md)
- [DATA_CONTRACTS.md](/workspace/planning/research-program/DATA_CONTRACTS.md)
- [SPEC.md](/workspace/planning/phase-1-5/SPEC.md)

The named phase specification provides the exact formulas, proposed signatures, units and literal fixtures for this task. Existing symbols are marked as existing; proposed modules/commands are created by their owner tasks. Do not substitute remembered formulas or undocumented library defaults.

Read the complete [type blueprint](/workspace/planning/research-program/TYPE_REFERENCE.py) for the declarations owned by this phase. Implement its boundary validation; the blueprint itself is not a tested research package.

### Input and ownership contract

Consume verified predecessor receipts: **none (bootstrap task)**. Their hashes and actual artifact paths go in this task receipt. Required schema details are in DATA_CONTRACTS; source adapters also read their named method predicates.

Allowed implementation/test paths:

- `/workspace/implementation/src/trading_research/research/contracts/types.py`
- `/workspace/implementation/src/trading_research/research/contracts/identity.py`
- `/workspace/implementation/src/trading_research/research/rule_discovery/baseline_manifest.py`
- `/workspace/implementation/tests/rule_discovery/test_p15_00.py`

A worker does not edit another task’s shared files. Request an explicit integration patch from the subphase coordinator for runner registration, imports or additive shared-schema changes; the coordinator records it and reruns the affected contract tests. Keep independently fitted artifacts separate even when calculators are shared.

### Implementation steps

1. Read the accepted historical measurement report and its actual registry/protocol/composed-calendar/input receipts. Record baseline code/data/registry identities, all 58 units, scope kinds and per-branch input limits. Do not reconstruct a baseline identity from the current wiki hash.
2. Implement the frozen dataclasses/enums in the data contract, canonical JSON hashing, unit validation and nonfinite rejection. Include source/strategy/author-exact distinctions and raw baseline payload preservation.
3. Create BASELINE_BINDING.json, EXPOSURE_LEDGER.json and the deterministic engineering-date manifest from coverage before reading new outcomes. Snapshot task-relevant working-tree changes. Create receipt serialization but do not claim the not-yet-created verifier ran.
4. Trace one actual output through its serialized schema, feature/stage parents and native receipt. Then run the verification below and write immutable evidence. A formula unit test alone does not complete a native-data or fitted-expert task.

### Worked and discriminating checks

Use one entry setup, one context/research record, one personal-execution unit, one missing-input record and one same-batch ambiguity from existing schemas. Decimal("1.00") has a documented canonical representation; do not accidentally alternate with binary float1.

Use the shared [reference vectors](/workspace/planning/research-program/fixtures/reference_vectors.json) where applicable. Add a negative control that fails if the central behavior is removed, reversed, delayed incorrectly or fed future information. Model tests must include a known synthetic signal and a native chronological slice; never demand an empirical market improvement merely to pass software verification.

### Required failure checks

Acceptance amendment: `research-assurance-2026-09-14-v2`. Assigned cases: **S01, S02, S03, S05, S06, S07, S10, S13, S14, S31**. Use the exact probes, expected results and evidence in SILENT_FAILURES.md. Reuse current bound shared evidence where applicable; do not replace the task’s own sensitive/native check with a test count. Preserve prior attempts and produce the common task artifacts listed in TASK_GRAPH.json as well as the task-specific outputs below.

### Acceptance checklist

- [ ] A01: All 50 branches and eight extra units reconcile to the accepted registry; the 18,747 total is not confused with independent trades.
- [ ] A02: Canonical hashes are independent of dictionary insertion order and worker count; semantic clock/price changes alter them.
- [ ] A03: Future evidence, invalid side/geometry units and NaN fail at schema boundaries.
- [ ] A04: Original source_exact unknown remains unknown after normalized round-trip.
- [ ] A05: The eight-date selection is reproducible from coverage alone and preserves missing slots.
- [ ] A06: Evidence includes command exit codes, artifact hashes, coverage/unknown counts, runtime, actual output inspection and the task’s declared limitations. All predecessor receipts verify.

- [ ] A07: EVIDENCE_MATRIX.json resolves every acceptance key and assigned failure case to actual code, executed commands, hashed evidence and inspected output under ASSURANCE.md; artifact/identity/command forgeries fail.
- [ ] A08: The assigned silent-failure probes pass with sensitive positive and negative controls, honest native/unknown/job counts, and no stale evidence. Return review-ready artifacts; subphase admission additionally requires the coordinator’s matching passing GATE_REVIEW.json.
- [ ] A09: Every evidence-bearing type and its deserializer reject late parents, malformed clocks, nested nonfinite values and mutable aliasing; existing Forecast boundaries also enforce train_end <= fit_available <= issue without implementing Phase 2.
- [ ] A10: Engineering slots are selected from hashed native coverage by required input group and same-contract lookback; open calendar days alone cannot be complete inputs. The known prior-profile omissions are discriminating negatives.
- [ ] A11: Preserved plan/code snapshots and the draft manifest recompute to the receipt identities, including owned untracked files and relevant helper dependencies; each identity field has a separate tamper negative.
- [ ] A12: At least one real native row is reopened and replayed through serialization. The gap and batch-conflict fixtures execute and preserve unknown coverage/order; synthetic examples are explicitly labelled.
- [ ] A13: The new attempt preserves the original reviewed receipt identities, declares the assurance amendment and records its own measured work/decision trail; no old acceptance evidence is overwritten.

### Commands and evidence

Commands below are **to run during implementation after their owner task creates the entrypoint**. They have not been run by this planning change. Use the existing environment; do not install arbitrary packages.

```bash
cd /workspace/implementation
.venv/bin/python -m pytest /workspace/implementation/tests/rule_discovery/test_p15_00.py -q
```

P15-00 bootstraps receipt serialization. P15-01 creates the verifier and must verify this receipt retrospectively before closing the foundation gate.

Expected artifacts under the task’s immutable report run (large data shards may be in the ignored cache, with file-level hashes in the manifest):

- `BASELINE_BINDING.json`
- `EXPOSURE_LEDGER.json`
- `ENGINEERING_DATES.json`
- `SCHEMA_EXAMPLES.json`
- `TASK_RECEIPT.json` and `REPORT.md`, including acceptance keys A01–A13 and exact predecessor/artifact hashes.

### Completion and stop rules

Software checks must pass. A native cell may be unsupported only after the specified owned-input search and generic implementation/fixture verification. Sparse or negative research findings retain the baseline and all counts; they do not authorize more unregistered search. An implementation defect, unresolved job or timeout is work remaining. Use the shared receipt statuses; do not mark a phase complete from this individual card.

Any family report prints both the PHASE table and the audit table defined in WORKFLOW.md. Report the real completed behavior, commands, native evidence, limitations and next eligible dependency. Do not claim final profitability, author-exact proprietary recovery or complete native coverage without the required evidence.

### Copyable worker prompt

Generated from the task graph and pstack execution contract by tools/build_research_plan_bundles.py. Edit the canonical task above for research requirements; rebuild this section after prompt changes.

```text
/poteto-mode new task. Implement this feature: P15-00 — Bind the accepted baseline and define typed records.
Read /workspace/planning/phase-1-5/tasks/P15-00.md and /workspace/planning/research-program/PSTACK_EXECUTION.md. Use the installed pstack router and the card's required contracts; this is execution of an existing specification.
Use the coordinator's actual working root, accepted Phase 1 report/input identities, code identity and new run root. This bootstrap task creates the draft/frozen manifest templates and initial receipts; do not wait for future task artifacts or a verifier that P15-01 has not built yet.
Use the parent Grok model for every pstack role (inherit-parent means omit model). Use the installed poteto-agent wrapper when supported. No nested delegation; the coordinator owns fresh review and shared-file integration. Respect its single-writer checkout assignment.
Follow the exact formulas, clocks, schemas, allowed paths, finite budgets and A01, A02, A03, A04, A05, A06, A07, A08, A09, A10, A11, A12, A13 checks. Name the data shape, implement one vertical behavior, run sensitive tests and the declared native slice/full run, and inspect actual output.
Bootstrap exception: implement and check the serializer, baseline identities, types and manifest template now. Return the real TASK_RECEIPT.json plus local check evidence to the foundation coordinator. P15-01 creates the verifier and must verify this receipt before the subphase can close; do not claim that future command ran. Keep the decision trail and runtime todos in the run's WORK_LOG.md/DECISIONS.tsv.
Apply /workspace/planning/research-program/ASSURANCE.md and the card's assigned silent-failure cases: S01, S02, S03, S05, S06, S07, S10, S13, S14, S31. Produce EVIDENCE_MATRIX.json linking every required check to real code, executed commands, hashes and inspected output selectors. Show sensitive accepted/rejected controls; preserve missing/ambiguous data and all declared jobs. A pass flag or your own verifier alone cannot prove completion. Return the evidence for the coordinator's separate GATE_REVIEW.json; do not edit fixed independent checks to obtain a pass.
Preserve accepted Phase 1 evidence, raw sources, missing/ambiguous inputs and unsuccessful trials. Perform the local task only; no external publication, shipping workflow or later phase. Do not stop at a plan or a passing toy test.
```

Canonical source: [P15-01.md](/workspace/.worktrees/docs-amend/planning/phase-1-5/tasks/P15-01.md).

## P15-01 — Build receipt and dependency verification

Status: **planned; implementation not started by this planning task**.

Subphase: `00-foundation`. Dependencies: P15-00.

### Goal and boundary

Implement task/subphase/phase/lineage verification with exit0/2 and structured errors. Read TASK_GRAPH.json for required tasks, dependencies and acceptance keys; never trust a report PASS string.

Implement only this task and its declared outputs. Preserve accepted Phase 1 code/reports, immutable sources and raw data. All new numerical recipes are registered research policies unless the source ledger proves literal attribution. No future input, later fit or all-history selected rule may enter an earlier decision.

### Read first

- [AGENTS.md](/workspace/AGENTS.md)
- [ROADMAP.md](/workspace/planning/ROADMAP.md)
- [PSTACK_EXECUTION.md](/workspace/planning/research-program/PSTACK_EXECUTION.md)
- [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md)
- [Assigned failure cases](/workspace/planning/research-program/SILENT_FAILURES.md)
- [WORKFLOW.md](/workspace/planning/research-program/WORKFLOW.md)
- [DATA_CONTRACTS.md](/workspace/planning/research-program/DATA_CONTRACTS.md)

The named phase specification provides the exact formulas, proposed signatures, units and literal fixtures for this task. Existing symbols are marked as existing; proposed modules/commands are created by their owner tasks. Do not substitute remembered formulas or undocumented library defaults.

### Input and ownership contract

Consume predecessor artifacts and the bootstrap receipt from **P15-00**. Inspect its local checks and hashes first, build this task's verifier, then verify P15-00 retrospectively before closing this task. This is the declared foundation bootstrap exception; it does not require the not-yet-created verifier before implementation. Predecessor hashes and actual artifact paths go in this task receipt. Required schema details are in DATA_CONTRACTS.

Allowed implementation/test paths:

- `/workspace/implementation/src/trading_research/research/contracts/receipts.py`
- `/workspace/implementation/tools/verify_research_release.py`
- `/workspace/implementation/tests/rule_discovery/test_p15_01.py`

A worker does not edit another task’s shared files. Request an explicit integration patch from the subphase coordinator for runner registration, imports or additive shared-schema changes; the coordinator records it and reruns the affected contract tests. Keep independently fitted artifacts separate even when calculators are shared.

### Implementation steps

1. Implement task/subphase/phase/lineage verification with exit0/2 and structured errors. Read TASK_GRAPH.json for required tasks, dependencies and acceptance keys; never trust a report PASS string.
2. Validate file hashes, schemas, command exit codes, lineage times and predecessor receipt identities. Detect missing tasks, dependency cycles, changed artifacts, forged completion and incompatible phase gates.
3. Verify P15-00 retrospectively and return the foundation gate inputs to the coordinator, which alone writes SUBPHASE_RECEIPT.json. Test failures using copied tiny fixture artifacts, never corrupt accepted reports.
4. Trace one actual output through its serialized schema, feature/stage parents and native receipt. Then run the verification below and write immutable evidence. A formula unit test alone does not complete a native-data or fitted-expert task.

### Worked and discriminating checks

Use the literal cases in the named mathematical contract and add one independently constructed negative case.

Use the shared [reference vectors](/workspace/planning/research-program/fixtures/reference_vectors.json) where applicable. Add a negative control that fails if the central behavior is removed, reversed, delayed incorrectly or fed future information. Model tests must include a known synthetic signal and a native chronological slice; never demand an empirical market improvement merely to pass software verification.

### Required failure checks

Acceptance amendment: `research-assurance-2026-09-14-v2`. Assigned cases: **S01, S02, S03, S04, S05**. Use the exact probes, expected results and evidence in SILENT_FAILURES.md. Reuse current bound shared evidence where applicable; do not replace the task’s own sensitive/native check with a test count. Preserve prior attempts and produce the common task artifacts listed in TASK_GRAPH.json as well as the task-specific outputs below.

### Acceptance checklist

- [ ] A01: A missing predecessor fails even if a child report says PASS.
- [ ] A02: Tampering one artifact byte or a required acceptance flag fails verification.
- [ ] A03: blocked_implementation never passes a phase gate; scoped input limitations cannot excuse missing software checks.
- [ ] A04: Phase 2 receipts without the complete Phase 1.5 gate fail.
- [ ] A05: Verifier tests include valid bootstrap receipt and each required negative.
- [ ] A06: Evidence includes command exit codes, artifact hashes, coverage/unknown counts, runtime, actual output inspection and the task’s declared limitations. All predecessor receipts verify.

- [ ] A07: EVIDENCE_MATRIX.json resolves every acceptance key and assigned failure case to actual code, executed commands, hashed evidence and inspected output under ASSURANCE.md; artifact/identity/command forgeries fail.
- [ ] A08: The assigned silent-failure probes pass with sensitive positive and negative controls, honest native/unknown/job counts, and no stale evidence. Return review-ready artifacts; subphase admission additionally requires the coordinator’s matching passing GATE_REVIEW.json.
- [ ] A09: Recursive verification rejects a correctly hashed failed parent, wrong task-ID reuse, unknown empty subphase, forged phase dispositions and missing actual Phase 1.5 release, with valid controls and intended error-code assertions.
- [ ] A10: Required task/common artifacts, schemas, row counts, directory inventories, evidence-matrix references and actual plan/code/run/input bindings are enforced; true A flags cannot excuse absent evidence.
- [ ] A11: Required failed or unlogged commands never pass via unresolved prose; expected negative commands are evidenced inside a passing suite. Typed input limits cannot excuse missing generic implementation.
- [ ] A12: Lineage retains every ancestor cutoff and rejects missing/malformed clocks and unresolved evidence hashes/rows. Receipt/release/review ordering is acyclic; --gate-review verifies admission separately from a candidate receipt.
- [ ] A13: The fixed independent 27-case foundation checker passes on actual new receipts with all valid controls and intended invalid rejections; return evidence for the coordinator’s matching GATE_REVIEW.json. The checker itself is not modified.

### Commands and evidence

Commands below are **to run during implementation after their owner task creates the entrypoint**. They have not been run by this planning change. Use the existing environment; do not install arbitrary packages.

```bash
cd /workspace/implementation
.venv/bin/python -m pytest /workspace/implementation/tests/rule_discovery/test_p15_01.py -q
```


```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt TASK_RECEIPT_PATH
```

Expected artifacts under the task’s immutable report run (large data shards may be in the ignored cache, with file-level hashes in the manifest):

- `VERIFIER_CASES.json`
- Verified foundation gate inputs; the coordinator writes `SUBPHASE_RECEIPT.json` after this task receipt verifies.
- `TASK_RECEIPT.json` and `REPORT.md`, including acceptance keys A01–A13 and exact predecessor/artifact hashes.

### Completion and stop rules

Software checks must pass. A native cell may be unsupported only after the specified owned-input search and generic implementation/fixture verification. Sparse or negative research findings retain the baseline and all counts; they do not authorize more unregistered search. An implementation defect, unresolved job or timeout is work remaining. Use the shared receipt statuses; do not mark a phase complete from this individual card.

Any family report prints both the PHASE table and the audit table defined in WORKFLOW.md. Report the real completed behavior, commands, native evidence, limitations and next eligible dependency. Do not claim final profitability, author-exact proprietary recovery or complete native coverage without the required evidence.

### Copyable worker prompt

Generated from the task graph and pstack execution contract by tools/build_research_plan_bundles.py. Edit the canonical task above for research requirements; rebuild this section after prompt changes.

```text
/poteto-mode new task. Implement this feature: P15-01 — Build receipt and dependency verification.
Read /workspace/planning/phase-1-5/tasks/P15-01.md and /workspace/planning/research-program/PSTACK_EXECUTION.md. Use the installed pstack router and the card's required contracts; this is execution of an existing specification.
Use the coordinator's actual working root, code identity, predecessor receipt paths/hashes, frozen manifest, dates and run root. Resolve missing values from those artifacts; report unresolved fields to the coordinator instead of inventing them.
Use the parent Grok model for every pstack role (inherit-parent means omit model). Use the installed poteto-agent wrapper when supported. No nested delegation; the coordinator owns fresh review and shared-file integration. Respect its single-writer checkout assignment.
Follow the exact formulas, clocks, schemas, allowed paths, finite budgets and A01, A02, A03, A04, A05, A06, A07, A08, A09, A10, A11, A12, A13 checks. Name the data shape, implement one vertical behavior, run sensitive tests and the declared native slice/full run, and inspect actual output.
Done means all required artifacts exist and verify_research_release.py task exits 0 on the actual TASK_RECEIPT.json, with truthful coverage and disposition. Return real artifact paths, command results, decision-trail path and limitations. Keep runtime todos in the run's WORK_LOG.md and record playbook skips there.
Bootstrap dependency: inspect P15-00's actual artifacts and local checks, implement this task's verifier, then verify P15-00 retrospectively before verifying your own receipt. Return foundation gate inputs to the coordinator, which alone writes SUBPHASE_RECEIPT.json.
Apply /workspace/planning/research-program/ASSURANCE.md and the card's assigned silent-failure cases: S01, S02, S03, S04, S05. Produce EVIDENCE_MATRIX.json linking every required check to real code, executed commands, hashes and inspected output selectors. Show sensitive accepted/rejected controls; preserve missing/ambiguous data and all declared jobs. A pass flag or your own verifier alone cannot prove completion. Return the evidence for the coordinator's separate GATE_REVIEW.json; do not edit fixed independent checks to obtain a pass.
Preserve accepted Phase 1 evidence, raw sources, missing/ambiguous inputs and unsuccessful trials. Perform the local task only; no external publication, shipping workflow or later phase. Do not stop at a plan or a passing toy test.
```
