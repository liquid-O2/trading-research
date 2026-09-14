# Repair 00-foundation before the next subphase

The 2026-09-14 review found that the original completion is not safe to use as a dependency gate. The implementer's 25 tests passed, but the independent 27-case suite accepted 18 invalid cases. Valid controls still passed. Read the [review](reviews/00-foundation-2026-09-14/REVIEW.md), [recorded counterexamples](reviews/00-foundation-2026-09-14/adversarial-confirmed/RESULTS.json) and [amendment](AMENDMENTS.json). `01-native-and-outcomes` waits for repaired foundation receipts and a matching passing review.

This repair is an implementation work order when the user sends the prompt. Authoring this document did not fix the implementation. Do not rerun the Phase 1 census, fit Phase 2 models, or rewrite accepted evidence to repair the foundation.

## Preserve the reviewed attempt

The historical receipts are evidence of what ran, not current admission:

- [P15-00](/workspace/implementation/reports/research-work/P15-00/b291864ccceaca9a/attempt-0001/TASK_RECEIPT.json).
- [P15-01](/workspace/implementation/reports/research-work/P15-01/039267553e8bf721/attempt-0001/TASK_RECEIPT.json).
- [00-foundation](/workspace/implementation/reports/research-work/00-foundation/f7135f8d696ff1f5/attempt-0001/SUBPHASE_RECEIPT.json).

Their hashes and the seven reviewed source/test/tool hashes are in [REVIEWED_IDENTITIES.json](reviews/00-foundation-2026-09-14/REVIEWED_IDENTITIES.json). Leave these files and all earlier attempts intact. New task runs have v2 plan/code snapshots, the new assurance version, new semantic run IDs and explicit supersession references in their reports/exposure ledger. Preserve previously exposed engineering dates and declare the coverage correction before any new outcome inspection. Do not simply add A07–A13 booleans to the old receipt.

## Work in this order

1. Read the current [foundation runbook](/workspace/planning/phase-1-5/subphases/00-foundation/RUNBOOK.md), [ASSURANCE.md](ASSURANCE.md) and assigned failure cases. Inspect the existing modules before editing. The repair owns only the P15-00/P15-01 implementation/test paths and new immutable report outputs. The coordinator may update concise wiki status/evidence links after review. Fixed audit tools, canonical assurance requirements and preserved review outputs are outside the implementation writer's ownership.
2. Reproduce the existing failures using isolated copies. The recorded before-run used the [original graph snapshot](reviews/00-foundation-2026-09-14/TASK_GRAPH_BEFORE.json), so its valid controls test original behavior without the later acceptance amendment creating unrelated missing-key failures. Retain that evidence. It does not authorize admission under an old graph after repair. Each implementation unit test must isolate its intended failure reason; the independent suite is an additional minimum check.
3. Repair required artifacts, snapshot/draft identities, recursive predecessor/task/phase verification, command/log enforcement and evidence-matrix validation. Add valid miniature bootstrap/subphase/phase fixtures alongside the negative cases. Test `--gate-review` with missing, stale, wrong-receipt, wrong-code, unresolved-issue and forged review references. Serialize task artifacts first, task receipts next, coordinator subphase/phase candidates next, and final review sidecars last; never create circular hashes.
4. Repair every nested clock/schema boundary, including deserialization and recursive immutability. A child cutoff cannot relax an ancestor cutoff. Evidence leaves need real hashes/row references. Correct the already-present Forecast boundary: `train_end <= fit_available <= issue`, with finite supported outputs. Preserve that tested public record; do not remove it to bypass the negative case. This is a boundary repair, not permission to implement Phase 2 fitting.
5. Replace calendar-only engineering coverage with deterministic per-input-group native coverage and required lookback intervals. In particular, [2020-01-02 Keani coverage](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/jobs/evaluation/2020-01-02/KEANI-OPEN-ABOVE-VALUE--branch--source_long.json.gz) has an open complete current prefix but a prior-scope omission with 390 unknown minute intervals. It cannot prove a complete prior-profile group. Use accepted calendar/reconstruction and coverage receipts without rereading outcomes to choose dates. Preserve missing slots, roll/holiday uncertainty, and unknown feed completeness. Implement executable gap/batch fixtures and reopen/replay at least one actual native row through the new record schema; generated records remain labelled synthetic.
6. Produce each task's common artifacts and A01–A13 evidence, run targeted tests and inspect actual output. P15-01 validates the new P15-00 receipt retrospectively. The coordinator creates a new immutable subphase candidate, runs the fixed independent suite against these new receipts, and performs the separate behavior review. Resolve all findings and regenerate only affected descendants under new identities. Preserve failed runs.
7. Validate both the candidate and its matching passing review. Update the wiki with exact new evidence links, superseded old admission and limitations. Return the next eligible `01-native-and-outcomes` prompt only after this gate passes; do not execute that subphase in this repair task.

## Exact validation commands

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

The independent checker is already implemented at [check_foundation_adversarial.py](/workspace/tools/check_foundation_adversarial.py); its hash and case count are pinned in [ASSURANCE_CASES.json](ASSURANCE_CASES.json). Exit 0 means every positive and negative case matched. Exit 1 means a behavior failed; exit 2 means the checker could not run, which is also not a pass. Its `RESULTS.json` hashes the checker and its actual receipt/graph inputs. Do not edit the checker, replace it with an implementation helper, filter cases, or cite a stale result after code changes. A closed final review must also inspect coverage/native evidence and the assigned cases outside this fixed suite.

The source-grounded baseline preservation check compares the frozen Phase 1 registry's 248 software file hashes, rather than the newly enlarged whole-tree software identity. Keep accepted reports and raw data intact. Scope the targeted tests to this repair and affected contract/native behavior; full Phase 1 measurement is not a prerequisite to repair these defects.

## Copyable repair prompt

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
