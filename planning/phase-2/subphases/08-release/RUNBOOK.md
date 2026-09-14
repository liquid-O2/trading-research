# Phase 2 / 08-release — coordinator runbook

Status: **planned; not implemented by this planning task**. Generated from canonical contracts and task cards. Edit those sources, then rebuild; do not edit this bundle independently.

Source content SHA256: `cb22d7493f3fb6e4f3298c170a9be613c4ec43e9db7b9862853215fccd06acb5`.

Previous gate: **07-plans-and-adaptation**. External task dependencies: P2-23. Read and verify their actual receipts before implementation.

## Coordinator work order

Enter through /poteto-mode new task and run only this bounded subphase to its verification predicate. Match the installed playbook, copy its steps into runtime todos and record explicit skip reasons. Apply the included Grok-only model and host-capability overrides to all routed skills. A large-task figure-it-out route must use this existing runbook, not invent a new research plan.

Implement only the tasks listed below, in dependency order. Start with one verified vertical slice. Delegate bounded cards with the complete brief in PSTACK_EXECUTION; a shared checkout has one code writer at a time. At most three live Grok/poteto agents including the coordinator; unavailable workers mean sequential execution. The coordinator reviews and integrates shared schemas/runners and alone writes SUBPHASE_RECEIPT.json.

Read workspace AGENTS.md. The executable contracts and task cards are included below. Source method wiki pages linked by a task are additional focused worker reads; they retain the precise author predicates. Do not reread the whole archive or invent alternative formulas.

The native slice, numerical checks, coverage, future perturbation, actual output inspection and immutable receipts are part of the task. A negative/inconclusive research result is valid; missing implementation is not. Preserve prior evidence and all unsuccessful trials. Do not start the next subphase automatically.

| Task | Dependencies | Canonical card |
| --- | --- | --- |
| P2-24 — Verify the complete context release and Phase 3 handoff | P2-23 | [Task](/workspace/planning/phase-2/tasks/P2-24.md) |

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

This runbook includes only cases assigned to: P2-24.

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

### S18 — Computed predictors never reach the fitted model

Assigned tasks: P2-02, P2-04, P2-05, P2-06, P2-07, P2-08, P2-12, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-21, P2-24.

**Probe:** Plant a known synthetic signal in one named feature family. Inspect the actual predictor matrix, masks, head inputs and serialized coefficients. Remove that family and perform the declared ablation with a fresh fit.

**Expected:** The expected named columns reach the optimizer and affect the sensitive prediction. Ablation changes the actual fit input and artifact identity. A computed feature dictionary, copied baseline predictions or all-zero stub cannot satisfy the experiment.

**Evidence:** Feature-to-column-to-head mapping, planted-signal outputs, artifact reload prediction and refitted ablation comparison; no market-win requirement.

### S20 — Model architecture replaced with the wrong fitted units

Assigned tasks: P2-00, P2-02, P2-04, P2-13, P2-14, P2-15, P2-16, P2-17, P2-18, P2-19, P2-20, P2-24.

**Probe:** Inspect the real fit registry, parameter arrays and prediction routing for the joint volatility heads and separate context/method experts.

**Expected:** GK/YZ/HAR/IV feed one jointly fitted volatility artifact with the declared heads. Different mechanisms/method experts have independently fitted parameter identities and correct training/label inputs; renamed copies of one generic fit do not count.

**Evidence:** Fit-call-to-artifact/head map, parameter and configuration hashes, method/branch target matrix and input-consumption audit.

### S24 — Unregistered trials or outcome-driven selection

Assigned tasks: P15-08, P15-17, P15-18, P15-19, P15-20, P2-23, P2-24.

**Probe:** Compare the frozen candidate/job bank to every executed attempt, including failures, unsupported cells and B0/B1/B2 versions. Alter only held-out outcomes and re-run selection.

**Expected:** No trial is missing, duplicated, renamed away or added outside the finite budget. Selection uses only the allowed training/tuning evidence and retains fold-specific rules. A negative result cannot trigger unregistered search or deletion.

**Evidence:** Set reconciliation of planned/executed/failed/selected IDs, immutable trial ledger, fold selections and exposure history.

### S25 — Option definitions, stale quotes or OI publication guessed

Assigned tasks: P2-00, P2-01, P2-09, P2-10, P2-11, P2-12, P2-24.

**Probe:** Use stale spot/option quotes, inverted bid/ask, a close-only cash index, a contract with unknown settlement/expiry, and an OI effective date before publication. Test the declared extra-session publication delay.

**Expected:** Exact freshness/model bounds and dated native definitions gate the rows. Filename date is not availability; close-only cash data is not native intraday spot. Assumed OI clocks remain labelled assumptions. Missing chain members stay in coverage denominators.

**Evidence:** Instrument/source ledger, quote-age and price-bound cases, OI effective/published/available clocks and delay sensitivity.

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

### S29 — Later refits rewrite earlier forecasts or plans

Assigned tasks: P2-02, P2-22, P2-23, P2-24.

**Probe:** Refit after new labels mature, issue a plan revision and reload an earlier artifact. Attempt to overwrite the earlier forecast/run ID; compare OOF upstream versions across cadences.

**Expected:** Earlier forecasts/plans remain immutable. New parameters have later fit availability and new IDs; updates use only mature labels and declared cadence. Revisions append with supersession links and no retroactive forecast improvement.

**Evidence:** Before/after hashes, update ledger, model/plan version clocks, cadence trials and replay using as-issued records.

### S30 — Costed replay changes entries or misstates daily risk

Assigned tasks: P15-03, P15-19, P2-21, P2-22, P2-24.

**Probe:** Use literal long/short costed trades; compare all exit policies with identical entry IDs. Include two trades in a day, a complete zero-trade day, a gap past a stop and final account-day flatten.

**Expected:** Costs, fills, quantity, day-start loss and ambiguity use the fixed policy. Fixed-entry comparisons preserve entries exactly. Daily economic denominators include eligible zero days; a day-start loss bound is not a peak-trailing drawdown. Unsupported fill/ordering evidence stays explicit.

**Evidence:** Entry-ID equality, per-fill arithmetic, account-day ledger and exact risk/flatten boundary cases.

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

Canonical source: [SPEC.md](/workspace/.worktrees/docs-amend/planning/phase-2/SPEC.md).

## Phase 2 context and expert specification

Entry gate: a verified Phase 1.5 phase receipt covering every task and family, including its limitations and fold-specific selected-rule manifests. Exception: P2-09, P2-10 and P2-03 may start from the verified P15-02 receipt (the native MarketView) instead of waiting for that phase receipt; their receipts must be re-verified under P2-00 before P2-04, P2-11 or any method expert consumes them. Do not begin any other Phase 2 implementation while any Phase 1.5 task is still in progress. This pack is written now so the next implementer can start without another planning interview.

### Result and code boundaries

Build separately fitted experts for major context mechanisms and source strategies, sharing deterministic feature calculations and common fitting code. Produce intraday forecasts, current descriptive states and conditional method plans. One jointly fitted volatility expert consumes GK, YZ, HAR and all available IV groups. A collection of hand-written state labels alone is not the required learned context system.

New root: `implementation/src/trading_research/research/experts/`. Reuse `research/contracts/` from Phase 1.5; extend schemas additively with version bumps. New reports: `implementation/reports/context-experts/<run-id>/`; large row/model caches: ignored `/workspace/data/derived/trading-research/context-experts/`. Every artifact binds the Phase 1.5 input release, plan, features, training cutoffs, labels and exact model inputs.

| Expert/artifact | Output | Required specification |
| --- | --- | --- |
| `joint_volatility` | Joint multihead future variance, intervals and converted movement scale | [Volatility](/workspace/.worktrees/docs-amend/planning/phase-2/VOLATILITY.md) |
| `range_path` | Remaining up/down excursion, first-passage time distributions, break topology and post-break acceptance | [Context](/workspace/.worktrees/docs-amend/planning/phase-2/CONTEXT.md) |
| `auction_session` | Current operational auction/day-state descriptors, future transitions, session opportunity quality | [Context](/workspace/.worktrees/docs-amend/planning/phase-2/CONTEXT.md) |
| `flow_memory` | Rewarded aggression, failed pushes, defended persistence and transition forecasts | [Context](/workspace/.worktrees/docs-amend/planning/phase-2/CONTEXT.md) |
| `cross_market` | Native related-market divergence, lead/lag, spot/IV coupling and NQ path contribution | [Context](/workspace/.worktrees/docs-amend/planning/phase-2/CONTEXT.md) |
| `options_context` | Native chain exposure, flow, changes, shock scenarios and context forecast | [Options](/workspace/.worktrees/docs-amend/planning/phase-2/OPTIONS.md) |
| `intraday_oi` | Weakly supervised OI change estimates, uncertainty and baseline comparison | [Options](/workspace/.worktrees/docs-amend/planning/phase-2/OPTIONS.md) |
| one artifact per source entry method | Occurrence probability, conditional utility/path, session/branch/reference suitability and conditional plan | [Method experts](/workspace/.worktrees/docs-amend/planning/phase-2/METHOD_EXPERTS.md) |
| research-process artifacts | Refilling memory, jetbundle transitions and macro-state contribution; risk remains a rule overlay | [Method experts](/workspace/.worktrees/docs-amend/planning/phase-2/METHOD_EXPERTS.md) |

These are responsibility names, not a prescribed final model count. Unsupported heads remain explicitly unavailable. Shared input features are computed once; separately fitted experts have separate parameters, targets, validation and retirement decisions.

### Proposed APIs

```python
def build_snapshot(market, issue_at_ns: int, feature_spec, parents) -> Snapshot: ...
def build_targets(market, snapshot: Snapshot, target_spec) -> tuple[TargetRow, ...]: ...
def fit_expert(dataset: ExpertDataset, split: SplitManifest,
               config: ExpertConfig) -> ExpertArtifact: ...
def predict_expert(artifact: ExpertArtifact, snapshots: tuple[Snapshot, ...]) -> tuple[Forecast, ...]: ...
def build_conditional_plan(method_id: str, snapshot: Snapshot,
                           forecasts: tuple[Forecast, ...], rules: RuleRelease) -> ConditionalPlan: ...
def replay_context_baseline(plans, opportunities, market, policy) -> ContextReplay: ...
```

`ExpertConfig` declares expert ID, feature groups/columns, target heads/units, model recipe, hyperparameter grid, fit/calibration/adaptation schedule, minimum support, missing-input fallback, runtime budget and exact ablations. `TargetRow` stores snapshot ID, target ID, interval, value or null, event/censoring kind, coverage, label-known-at and evidence. Labels live in `experts/labels/`; the feature package may not import that package. `ExpertArtifact` includes all transformations, coefficients, calibration, target support, training/cutoff times, effective availability and parent model IDs.

Current state and future label are different records. The true final RTH day type is a future target before the close. A partial auction description may be known now. The same column name must not be used for both.

### Required feature groups

Price/auction: current and prior overnight/RTH/account-day ranges, completed source time ranges, profile POC/VAH/VAL and shape, developing and rolling/composite profiles, open location/type, initial balance once complete, value migration, prior extremes, range consumed, distance to source reference, current branch prerequisites and source objective already consumed. Retain each value's availability clock.

Activity/flow: realized variance, range and signed returns at 1/5/15/60 minutes; volume and trade-count intensity relative to prior 20 same-time buckets; CVD variants selected in Phase 1.5; buy/sell cohort markouts, unknown aggression, failed pushes, imbalance/defense persistence, touch history and reference age. Include BBO spread/depth where native coverage supports them.

Related markets: ES, QQQ, SPY, native NDX/SPX and owned YM/RTY, with per-asset clocks, standardized movement, multi-scale SMT, lagged coupling and input gaps. Source setups are NQ-only; these are context/response features, not cloned source strategies on each asset.

Options/volatility: all owned native chains and IV products, expiry/strike structure, gamma/vega/vanna/OI and flow, spot/IV/time changes, cross-expiry concentration, 0DTE plus1–7,8–30,31–90 calendar-day boards, options activity/uncertainty and updated OI. Do not limit context to one maximum-gamma strike or prior-day OI.

Macro/event: only owned dated releases/calendars with known publication and vintage; time to/from scheduled events, released surprise if a dated prior forecast is owned, and lagged macro quantities. Latest revised series cannot be used historically as though unrevised. Missing news/macro inputs produce input-limited features, not fabricated “no event” flags.

### Downstream boundary

Phase 2 may recommend side, reference identity, confirmation recipe, target ambition, time window and invalidating evidence. It may rank a source method or say support is low. It does not create Phase 3 custom actionable price zones, choose the final NQ entry or require every forecast to become a hard veto. A reference recommendation points to an already available Phase 1.5/source reference; new option/volume areas are context boards until Phase 3 validates their location role.

Compare ungated source rules, a price-context baseline, a fixed context score and the fitted method expert with identical response and execution policies. Context contribution must survive incremental/ablation tests and changed coverage. All final entry/economic claims remain reserved for the integrated phase.

Canonical source: [ADAPTATION.md](/workspace/.worktrees/docs-amend/planning/phase-2/ADAPTATION.md).

## Refit, intraday adaptation and replay release

Owners `P2-23` adaptation and `P2-24` final chronological release. Use the four schedules in the [evaluation contract](/workspace/planning/research-program/EVALUATION.md), on identical snapshots, features, target definitions and costs. Model complexity and upstream selection stay frozen for the outer year. Each expert has its own artifact/cadence and evidence; a faster cadence is not automatically better.

### Exact intraday update

Only the monthly-plus-intraday arm changes parameters during a session. Base feature transformations and slopes remain fixed until monthly refit. At each quarter-hour, collect labels that became available since the last update, deduplicate target row IDs, and update intercept residual bias only. For a continuous/log target with raw prediction z, update `b <- .98*b + .02*(y-z)` once per newly matured account-day-normalized batch: first average residuals within each `(label_day, head, update_clock)` so dense overlapping signals do not create hundreds of updates. Apply `prediction=z+b` on the next issue, never earlier.

For probabilities update a class-logit offset vector `a <- .98*a + .02*(onehot(y)-p)` on the same grouped schedule, then center a to mean0 and add it to base logits before frozen temperature calibration. Include only supported observed labels; no imputed outcomes, unfinished horizons, unpublished OI or future day types. Default b/a=0 at the start of the outer evaluation, carry across account days, reset to0 at each monthly refit because the base fit incorporates prior data. This is a bounded online residual correction, not unrestricted intraday retraining.

Store update ID, previous/new artifact offsets, consumed label IDs and availability, actual compute finish time and first affected snapshot. A matured label arriving exactly at an issue time becomes usable only after update computation completes; the issue may use the prior artifact. Simulated runtime uses measured engineering median plus p95 sensitivity, not zero-cost hindsight fitting.

### Drift and retirement

At each monthly boundary report population stability on continuous standardized features using fixed training decile bins: `PSI=sum((p_new-p_train)*ln(p_new/p_train))`, with each count smoothed by.5 then renormalized. Report missingness change and recent42-day loss relative to its causal baseline. PSI>.2 or loss worsening>20% on at least 30 supported days creates a diagnostic flag, not an automatic unexplained veto.

Retire a fitted head to its declared baseline for the next month only if recent loss is worse than baseline in two consecutive monthly reports and its paired day-block95% improvement interval is entirely below0, or a schema/causality defect invalidates it immediately. Keep the artifact and failure receipt. Re-entry requires a newly versioned verified fit using only then-available evidence. Do not choose a retirement date backward from a test equity curve.

### Release checks

Replay every declared test-year snapshot and opportunity with dependency order: raw/as-of data -> shared primitives -> upstream forecasts -> method forecasts -> conditional plans -> comparison-only selector -> unchanged execution benchmark. The code path must reject a forecast trained/selected after issue time. Use causal stacking for training rows too, including the intraday OI artifact and Phase 1.5 selected rules.

Required release artifacts: feature/target dictionaries and matrices; availability by root/year/session; split/exposure manifests; all attempted models and ablations; calibrated forecasts and support; plan/revision/death records; baseline/selector daily replays; errors/censoring/zero days; runtime/cache receipts; task/subphase receipts; deterministic charts; a full dependency graph; and `PHASE2_RELEASE.json` with downstream allowlist and prohibited interpretations.

Compare annual/monthly/weekly/monthly-plus-intraday on paired days and loss/utility, using the shared multiple-trial accounting. Choose cadence using only the inner tuning available at each outer origin; outer results assess that policy. A final all-history cadence recommendation is descriptive and cannot replace the causal outer record.

The Phase 3 handoff lists each expert output, units, horizon, availability, confidence/support, fallback, model identity, measured incremental contribution and input limitations. It explicitly reserves native actionable location extraction/arrival-reaction evaluation for Phase 3, final response/entry integration for Phase 4, and later learned management for a separately planned milestone. Missing native NDX/SPX inputs yield `closed_with_limits` and exact restricted downstream scope, never a false complete-native release.

Canonical source: [METHOD_EXPERTS.md](/workspace/.worktrees/docs-amend/planning/phase-2/METHOD_EXPERTS.md).

## Method-specific context experts and conditional plans

Owners `P2-13` through `P2-21`; `P2-22` owns conditional plans/replay. Each source entry method has a separately fitted artifact/configuration using the common engine. Do not pool Jumbo, Green Bird, Sires and Saint into one unexplained “good market” score. Share primitives and fitting code; keep branch/source semantics and tests distinct.

### Training population and targets

At every shared snapshot, build a row for every source method whose source clock and required prefix can be evaluated. Include complete no-setup rows. For each method/branch over next 30 and 60 matching minutes: occurrence y=1 if an eligible frozen rule opportunity qualifies within the horizon, else0 on complete coverage. Conditional utility is the fixed benchmark net points of the **first** qualifying opportunity, selected by qualification time then stable ID, not the best future setup. If no opportunity occurs, utility is missing. If geometry/fill/coverage is unsupported, occurrence can still be observed while utility is unknown. Store both masks.

Also build pre-opportunity rows at the actual source qualification clock before any subsequent outcomes; these predict that opportunity's utility, ordered outcome, delay and directional remaining movement. Do not mix occurrence-grid rows and already-qualified rows in one loss without a target-kind column and separate heads/denominators. Response evidence used to qualify a source setup is available on the pre-opportunity row; it was not available on a prior planning row.

Per method fit: branch occurrence softmax/binary heads; conditional mean utility ridge; .1/.5/.9 utility and remaining-excursion quantiles; ordered target/stop/neither class probabilities. Multi-label branch occurrences use independent binary heads inside that method artifact, since several branches can occur in one horizon. Conditional plans are built from these heads plus causal global forecasts. Exact fitting, support and calibration follow the shared contracts. Unsupported rare branches retain baseline eligibility and low-support priors; a profitable-looking six-example Keani cell cannot be declared learned.

### Source-specific feature and output contract

| Method | Required method context and forecasts | Branch distinctions and invalidation |
| --- | --- | --- |
| JJ-TBR | Overnight extension/compression, prior purge and its age, source range geometry, open location, value/profile, single/double-break topology and order, remaining directional excursion, consumed objective, source timing, vol/range forecast and alternatives | Preserve all eight registry branches: outbound/reversal, extended/purged/rotation, extension reaction, other session and timed P-zone. Predict branch suitability separately. Existing P-zones are input references; no Phase 3 zone optimizer. Outbound source deadline remains09:40. |
| GB-FAIL | Reference type/age, prior session/hour/week/month, sweep/reclaim chronology, cash-open/Asia case, direction, failed breakout versus continuation probability, opposing liquidity and confirmation delay | All eight registry branches including refinement scope; preserve the source sweep-entry exception and each source clock. A reclaim continuation is not automatically a failed breakout. |
| GB-VWAP | London/Asia high relationship and close condition, VWAP anchor/band, pullback depth, directional continuation, remaining expansion and reversal alternative | Source long branch remains distinct. A newly proposed short/custom reference belongs to its labelled Phase 1.5 custom sibling, not a fabricated source short. |
| GB-SCALP | Bearish/bullish direction, favorable/discounted pullback, trend exhaustion versus continuation, local flow and shorter remaining reward | Two source case branches plus the known partial automatic-admission scope. Explicit operational trigger is our version; a partial source description is not magically complete. |
| SIRES | Operational day taxonomy and uncertainty, gamma/KG1 regime assumptions, thesis direction, value/balance, flow/reward/defense, squeeze versus failed auction, session quality, invalidation and remaining draw | Preserve12 registry branches and management/re-entry observations. Distinguish DOM rejection, absorption/reward/retest, four-stage stop, footprint reaction, VWAP fade, aggressive/passive OFM, squeeze, balance failure, defended continuation, microbalance and KG1. Low-support branches remain visible. |
| SAINT-AMT | Higher-timeframe balance/trending/new balance, POC/value migration, arrival/control, lower-timeframe agreement and defended retest | Four source routes: continuation retest, trapped-buyers retest, failed-auction return, POC traversal. Require independent HTF/LTF clocks and source control conditions. |
| MEMBER-TWO-REASONS | Prior reaction area, independent minor HVN formation, touch memory, arrival/response quality and competing nearby source reference | Two routes remain distinct. Same-price coincidence or a profile made from the reaction period does not create two independent reasons. |
| KEANI-OPEN-ABOVE-VALUE | Whole A period above prior VAH, higher developing value, aggressive break and defended imbalance retest | The single source long route retains sequence/availability. Before A completion predict the later route; do not mark its complete predicate true. Sparse outcome is acceptable as inconclusive. |

Read each source wiki method and its exact predicate in the canonical Phase 1 formulas when implementing its adapter. These tables do not replace those source predicates. Use Phase 1.5 `resolve_source_context` and normalized records so the new expert cannot silently change setup qualification.

Method feature matrix is the common price/auction/flow/options/cross-market set plus its own source-prerequisite booleans/masks, reference identity/type/age, branch clock distances, selected-rule role and causal upstream predictions. Allowed hinge products, same six semantics mapped to existing method columns: distance_to_reference×predicted_vol30m; reference_age×touch_count; directional_context×flow_reward120s; value_migration×reference_side; confirmation_delay_prior_median×remaining_excursion_median; gamma_scenario_sign×auction_efficiency. An unavailable semantic column disables and records that interaction; it does not get an invented input.

### Research/process scope

REFILL-STUDY gets a memory expert for subsequent touch occurrence and conditional reaction. It requires a causal formation and distinct contacts, prior resolved reactions and pre-touch grade/features. It does not claim actual selected limit orders or the author's private grading model. Complete nonarrival=0 for arrival; reaction given nonarrival is undefined.

JETBUNDLE-STATES gets a distinct transition artifact for B/A/D/E/W only on source-supplied labels with adequate evidence, plus our separately labelled operational states when true ten-level/cancellation inputs are absent. Do not call B/A/D/E/W AMT day types. An annotation fit reports annotation agreement; predictive contribution needs future NQ outcomes independently. When source labels are unavailable, retain the operational auction/flow expert and mark source-state learning unsupported.

STOIC-DATA gets macro/process context features and a fitted contribution head only where publication/vintage support exists. Its scientific collection process is not a trade trigger. STOIC-RISK stays a deterministic separately tested risk overlay; private account states are not invented for a fitted entry model. The benchmark's fixed one-mini/day-start limit is its own research policy.

### Conditional plan schema and deterministic builder

```python
@dataclass(frozen=True, slots=True)
class ConditionalPlan:
    plan_id: str
    method_id: str
    snapshot_id: str
    issue_at_ns: int
    expires_at_ns: int
    thesis_id: str
    revision_of: str | None
    status: str       # supported | watch | low_support | unavailable
    alternatives: tuple[dict, ...] # branch/side/reference, probabilities, utility interval
    selected_branch: str | None
    side: int | None
    reference_id: str | None
    confirmation_recipe: str | None
    ambition: str | None           # reduced | baseline | extended
    time_window: tuple[int, int]
    death_conditions: tuple[dict, ...]
    evidence_for_revision: tuple[str, ...]
    forecast_ids: tuple[str, ...]
    selection_manifest_id: str
```

At issue t, score each eligible branch/reference as `p_occurrence * conditional_mean_net_points`. Do not score unavailable conditional utility as0. Select the highest supported score>0, ties within 1% choose the source baseline then stable ID. Keep every alternative and uncertainty. If no positive supported score, status=`watch`; a missing essential native input yields unavailable; inadequate fit support yields low_support. A plan is a recommendation for a later integrator, not a hard veto of baseline setup discovery.

Confirmation recipe is the frozen Phase 1.5 choice for that branch/fold; context may recommend among the registered alternatives only when separate conditional heads have sufficient data for each. Otherwise keep baseline confirmation. Ambition: reduced when forecast favorable median<baseline target distance; extended when forecast favorable .1 quantile>1.5*baseline target distance; baseline otherwise. This tag does not change the benchmark's actual target/exit in the Phase 2 context comparison. Reference/side must exist and be causal; no novel price is manufactured from a forecast quantile here.

Expire at min(next scheduled quarter-hour update, source expiry, account-day flatten). Death conditions are the source structural invalidation, source window close, reference invalidation/replacement, stale essential input and a known change in the source prerequisite. Revision retains thesis ID while branch/side/reference remain the same; otherwise creates a new thesis ID linked to the old one with evidence and time. Never rewrite a prior plan's probability or pretend the final daily explanation was the initial forecast.

### Context contribution replay

For a comparison-only selector, keep a qualifying source opportunity if the latest valid supported method plan scores its branch>0. Compare with ungated source opportunities, a training-only session-frequency gate and an interpretable price-context gate (directional ER30m>=.35 and target remains positive). All use identical qualification, confirmation, fills, costs, stop/target and day-start risk policy. Unsupported plans default to the unchanged baseline in a separate `fallback_inclusive` replay; also report supported-only coverage. Do not hide absence of IV/native data behind a good subset result.

Admit a context expert for downstream use only with the shared support/causality gates and demonstrated loss/calibration improvement or a measured conditional-utility contribution with uncertainty. Useful descriptive context can be retained as descriptive even when its fitted head fails. Separate branch reliability, calibration, incremental value, opportunity loss and actual model consumption. Final entry selection and combined account economics remain Phase 4 work.

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

For a Phase 1.5 upgrade: at least 100 resolved benchmark opportunities on 30 eligible test days in aggregate, represented in at least three outer blocks. A branch below the gate is `inconclusive_support`, even if all six examples succeed. It remains in the registry and downstream baseline allowlist, with low-support status. Support gates are research defaults and their counts must be shown alongside sensitivity at half/twice the gate; changing the gate cannot manufacture a claim. A disposition never deletes a candidate: the trial ledger, its `failure_attribution` field and the bounded revisit rule are defined once in the [search contract](/workspace/.worktrees/docs-amend/planning/phase-1-5/SEARCH_CONTRACT.md) and the [retention rules](/workspace/.worktrees/docs-amend/planning/research-program/RETENTION.md). A disposition never deletes a candidate: `inconclusive_support`, `rejected_by_evidence`, `retained_baseline` and `unsupported_owned_input` keep the full population, parameters and diagnostics in the trial ledger and the retention set; "inactive" means not consumed by the next phase's training by default.

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

Canonical source: [P2-24.md](/workspace/.worktrees/docs-amend/planning/phase-2/tasks/P2-24.md).

## P2-24 — Verify the complete context release and Phase 3 handoff

Status: **planned; implementation not started by this planning task**.

Subphase: `08-release`. Dependencies: P2-23.

### Goal and boundary

Run full chronological dependency replay on the declared acquired test population, including causal stacking, B0/B1/B2 options/OI comparisons and all attempted expert/cadence configurations.

Implement only this task and its declared outputs. Preserve accepted Phase 1 code/reports, immutable sources and raw data. All new numerical recipes are registered research policies unless the source ledger proves literal attribution. No future input, later fit or all-history selected rule may enter an earlier decision.

### Read first

- [AGENTS.md](/workspace/AGENTS.md)
- [ROADMAP.md](/workspace/planning/ROADMAP.md)
- [PSTACK_EXECUTION.md](/workspace/planning/research-program/PSTACK_EXECUTION.md)
- [ASSURANCE.md](/workspace/planning/research-program/ASSURANCE.md)
- [Assigned failure cases](/workspace/planning/research-program/SILENT_FAILURES.md)
- [WORKFLOW.md](/workspace/planning/research-program/WORKFLOW.md)
- [SPEC.md](/workspace/planning/phase-2/SPEC.md)
- [ADAPTATION.md](/workspace/planning/phase-2/ADAPTATION.md)
- [METHOD_EXPERTS.md](/workspace/planning/phase-2/METHOD_EXPERTS.md)
- [EVALUATION.md](/workspace/planning/research-program/EVALUATION.md)
- [OUTCOMES.md](/workspace/planning/research-program/OUTCOMES.md)
- [DELIVERABLES.md](/workspace/.worktrees/docs-amend/planning/research-program/DELIVERABLES.md)
- [RETENTION.md](/workspace/.worktrees/docs-amend/planning/research-program/RETENTION.md)

The named phase specification provides the exact formulas, proposed signatures, units and literal fixtures for this task. Existing symbols are marked as existing; proposed modules/commands are created by their owner tasks. Do not substitute remembered formulas or undocumented library defaults.

### Input and ownership contract

Consume verified predecessor receipts: **P2-23**. Their hashes and actual artifact paths go in this task receipt. Required schema details are in DATA_CONTRACTS; source adapters also read their named method predicates.

Allowed implementation/test paths:

- `/workspace/implementation/src/trading_research/research/experts/release.py`
- `/workspace/implementation/tests/context_experts/test_p2_24.py`
- `/workspace/wiki/current-status.md`
- `/workspace/wiki/research-architecture.md`
- `/workspace/wiki/log.md`

A worker does not edit another task’s shared files. Request an explicit integration patch from the subphase coordinator for runner registration, imports or additive shared-schema changes; the coordinator records it and reruns the affected contract tests. Keep independently fitted artifacts separate even when calculators are shared.

### Implementation steps

1. Run full chronological dependency replay on the declared acquired test population, including causal stacking, B0/B1/B2 options/OI comparisons and all attempted expert/cadence configurations.
2. Reconcile every snapshot/target/forecast/plan/daily record and required input group, verify hashes/restart/future perturbation, inspect deterministic charts and audit actual model input consumption.
3. Write RELEASE_INPUTS.json, both family tables and downstream feature/forecast contracts. Finalize and verify this task receipt. The coordinator then writes PHASE2_RELEASE.json including this receipt, followed by its review sidecar; neither is hashed back into this task receipt. Update the wiki only after final admission passes, preserving native/support limits.
4. Trace one actual output through its serialized schema, feature/stage parents and native receipt. Then run the verification below and write immutable evidence. A formula unit test alone does not complete a native-data or fitted-expert task.

### Worked and discriminating checks

Use the literal cases in the named mathematical contract and add one independently constructed negative case.

Use the shared [reference vectors](/workspace/planning/research-program/fixtures/reference_vectors.json) where applicable. Add a negative control that fails if the central behavior is removed, reversed, delayed incorrectly or fed future information. Model tests must include a known synthetic signal and a native chronological slice; never demand an empirical market improvement merely to pass software verification.

### Required failure checks

Acceptance amendment: `research-assurance-2026-09-14-v2`. Assigned cases: **S01, S02, S03, S04, S06, S07, S11, S12, S18, S20, S24, S25, S27, S28, S29, S30, S31, S32**. Use the exact probes, expected results and evidence in SILENT_FAILURES.md. Reuse current bound shared evidence where applicable; do not replace the task’s own sensitive/native check with a test count. Preserve prior attempts and produce the common task artifacts listed in TASK_GRAPH.json as well as the task-specific outputs below.

### Acceptance checklist

- [ ] A01: Every predecessor Phase 2 task and requested expert/native root has a verified disposition; the coordinator adds this task’s own immutable receipt when finalizing the phase release.
- [ ] A02: No historical forecast uses later-selected rules, later-trained parents or unpublished OI.
- [ ] A03: B2 OI contribution is tested downstream separately from endpoint accuracy.
- [ ] A04: Daily economic tables include zero days and loss-limit breaches without average substitution.
- [ ] A05: Phase 3 handoff has exact units, clocks, uncertainty, fallback and allowed uses; missing native cash-index coverage cannot yield complete_native_coverage.
- [ ] A06: Evidence includes command exit codes, artifact hashes, coverage/unknown counts, runtime, actual output inspection and the task’s declared limitations. All predecessor receipts verify.

- [ ] A07: EVIDENCE_MATRIX.json resolves every acceptance key and assigned failure case to actual code, executed commands, hashed evidence and inspected output under ASSURANCE.md; artifact/identity/command forgeries fail.
- [ ] A08: The assigned silent-failure probes pass with sensitive positive and negative controls, honest native/unknown/job counts, and no stale evidence. Return review-ready artifacts; subphase admission additionally requires the coordinator’s matching passing GATE_REVIEW.json.
- [ ] A09: Strategy Book version 2 exists as `STRATEGY_BOOK.md`, `STRATEGY_BOOK.json` and one CSV per branch, produced from immutable trial ledgers with no hand-typed number.
- [ ] A10: Every strategy has a version 2 book entry with a verdict.
- [ ] A11: Every number carries a pointer to the immutable artifact it was computed from.
- [ ] A12: `REGIME_DIMENSIONS.json` was frozen before any candidate result was read.
- [ ] A13: The release reports the retention set with statuses and first attributions.
- [ ] A14: Every expert has a scorecard.

### Commands and evidence

Commands below are **to run during implementation after their owner task creates the entrypoint**. They have not been run by this planning change. Use the existing environment; do not install arbitrary packages.

```bash
cd /workspace/implementation
.venv/bin/python -m pytest /workspace/implementation/tests/context_experts/test_p2_24.py -q
```

Then run the frozen engineering slice with the actual manifest and date list produced by the prerequisite (substitute the three ALL_CAPS paths/values; do not invent dates from outcomes):

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/run_context_experts.py slice --run-root RUN_ROOT --manifest FROZEN_MANIFEST --dates FROZEN_DATES --task P2-24
```

Reconcile all required cases, inspect output and profile before a full run. Search/release tasks additionally use the runner’s `run`, `resume` and `summarize` on the same immutable manifest; complete declared jobs before claiming an executed experiment.

```bash
/workspace/implementation/.venv/bin/python /workspace/implementation/tools/verify_research_release.py task --receipt TASK_RECEIPT_PATH
```

Expected artifacts under the task’s immutable report run (large data shards may be in the ignored cache, with file-level hashes in the manifest):

- `RELEASE_INPUTS.json` (task output; the coordinator writes `PHASE2_RELEASE.json` after this task receipt is immutable)
- `CENSUS_RECONCILIATION.json`
- `INPUT_CONSUMPTION_AUDIT.json`
- `VISUAL_QA.json`
- `COMPLETION_REPORT.md`
- `PHASE3_HANDOFF.md`
- `STRATEGY_BOOK.md`
- `STRATEGY_BOOK.json`
- `STRATEGY_BOOK_CSVS/`
- `REGIME_DIMENSIONS.json`
- `RETENTION_SET.json`
- `EXPERT_SCORECARDS/`
- `TASK_RECEIPT.json` and `REPORT.md`, including acceptance keys A01–A14 and exact predecessor/artifact hashes.

### Completion and stop rules

Software checks must pass. A native cell may be unsupported only after the specified owned-input search and generic implementation/fixture verification. Sparse or negative research findings retain the baseline and all counts; they do not authorize more unregistered search. An implementation defect, unresolved job or timeout is work remaining. Use the shared receipt statuses; do not mark a phase complete from this individual card.

Any family report prints both the PHASE table and the audit table defined in WORKFLOW.md. Report the real completed behavior, commands, native evidence, limitations and next eligible dependency. Do not claim final profitability, author-exact proprietary recovery or complete native coverage without the required evidence.

### Copyable worker prompt

Generated from the task graph and pstack execution contract by tools/build_research_plan_bundles.py. Edit the canonical task above for research requirements; rebuild this section after prompt changes.

```text
/poteto-mode new task. Complete this planned phase-release verification and replay: P2-24 — Verify the complete context release and Phase 3 handoff.
Read /workspace/planning/phase-2/tasks/P2-24.md and /workspace/planning/research-program/PSTACK_EXECUTION.md. Use the installed pstack router and the card's required contracts; this is execution of an existing specification.
Use the coordinator's actual working root, code identity, predecessor receipt paths/hashes, frozen manifest, dates and run root. Resolve missing values from those artifacts; report unresolved fields to the coordinator instead of inventing them.
Use the parent Grok model for every pstack role (inherit-parent means omit model). Use the installed poteto-agent wrapper when supported. No nested delegation; the coordinator owns fresh review and shared-file integration. Respect its single-writer checkout assignment.
Follow the exact formulas, clocks, schemas, allowed paths, finite budgets and A01, A02, A03, A04, A05, A06, A07, A08, A09, A10, A11, A12, A13, A14 checks. Name the data shape, implement one vertical behavior, run sensitive tests and the declared native slice/full run, and inspect actual output.
Done means all required artifacts exist and verify_research_release.py task exits 0 on the actual TASK_RECEIPT.json, with truthful coverage and disposition. Return real artifact paths, command results, decision-trail path and limitations. Keep runtime todos in the run's WORK_LOG.md and record playbook skips there.
Apply /workspace/planning/research-program/ASSURANCE.md and the card's assigned silent-failure cases: S01, S02, S03, S04, S06, S07, S11, S12, S18, S20, S24, S25, S27, S28, S29, S30, S31, S32. Produce EVIDENCE_MATRIX.json linking every required check to real code, executed commands, hashes and inspected output selectors. Show sensitive accepted/rejected controls; preserve missing/ambiguous data and all declared jobs. A pass flag or your own verifier alone cannot prove completion. Return the evidence for the coordinator's separate GATE_REVIEW.json; do not edit fixed independent checks to obtain a pass.
Preserve accepted Phase 1 evidence, raw sources, missing/ambiguous inputs and unsuccessful trials. Perform the local task only; no external publication, shipping workflow or later phase. Do not stop at a plan or a passing toy test.
```
