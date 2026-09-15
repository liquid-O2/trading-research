# verifier-gate-chain work log

## How (in-lead, simple path)

`verify_gate_review` binds `GATE_REVIEW.json` to the live assurance registry. Graph hashes already walk `_plan_superseded_by_amendments`. Registry hashes still required exact equality.

`_plan_superseded_by_amendments` walks new-shape `AMENDMENTS.json` entries. It checks `previous_entry_sha256` against `digest(previous)`, then walks `changed_files` `sha256_before` / `sha256_after` for one path from the declared hash to the live hash.

04-family-adapters `GATE_REVIEW.json` pins `planning/research-program/ASSURANCE_CASES.json` at `88324dcfb44de2269fd59783d1671b6d52f5e301ec70f1b0f2210c1a0c523bee`. Live bytes hash to `93024ac8800d426d3d871535a670e6b9bd51ca179309071607409755ca5a10de`. Amendment `amendment-2026-09-15-source-fidelity-task-p15-16a` carries that before/after pair. `_plan_superseded_by_amendments` already returned True. Direct `verify_gate_review` on the 04 review returned `ARTIFACT_HASH` "registry hash does not match file bytes" and `GATE_REVIEW` "review registry hash is not the current assurance registry".

Pinned vs live case bodies: 32 case ids. Only `tasks` changed (P15-16A added). `probe` and `expected` match. P15-09 plan snapshot copy hashes to the pinned digest. The 04 subphase attempt has no `snapshots/` tree.

## Decisions

- Feature playbook. Architect skipped. User capped live agents at two with one code writer, and required the existing plan-file supersession shape.
- Reuse `_plan_superseded_by_amendments` exactly. No second chain walker.
- `_bind_review_file(..., require_hash_match=False)` for the registry, matching graph. Emit `ARTIFACT_HASH` "registry hash does not match file bytes" only when the chain does not carry the change.
- Review-bound case ids: union of graph `assurance_cases` for `expected_tasks` and registry cases whose `tasks` list intersects those ids. Compare only `probe` and `expected`.
- Pinned registry bytes come from a PLAN_SNAPSHOT copy whose digest equals the pinned hash. Search the review attempt, the candidate attempt, then each task receipt `snapshot_paths` entry.
- If no matching copy exists, fall back to the live registry. If a review-bound case id is missing, fail and record that limitation in the detail.
- Tests live in `implementation/tests/contracts/test_gate_review_chain.py`. They call `verify_subphase_receipt` for fixtures. They do not invoke `/workspace/implementation/tools/verify_research_release.py`.
- Full `subphase --gate-review` on the 04 attempt ran 4h56m and returned exit 2. Failures were `IDENTITY` (804) and `PREDECESSOR_HASH` (320). None were `GATE_REVIEW` or registry `ARTIFACT_HASH`. Live `/workspace/implementation/src` rule_discovery bytes drifted from the 04 code snapshots. Plan identity for those receipts is clean through the amendment chain. The 04 pytest binds `verify_gate_review`, which is the `--gate-review` path this change owns.
- `tests/rule_discovery/test_engine_hygiene.py` on this branch pointed `PARITY_PATH` at a missing `stage-a-r3` worktree. Main already points at `/workspace/implementation/reports/research-work/P15-17/_track_r3/PARITY_STRATIFIED.json`, which exists. The path was updated so `tests/rule_discovery` is green.

## Throughput checkpoint

- Blocking first steps: hash and failure reproduction above. Registry branch before tests.
- Independent workstreams: n/a. One function plus one test module.
- Shared mutable state: n/a. Live planning files stayed read-only.
- Smallest safe decomposition: one code writer.

## Verification

- Fixture tests a/b1/b2/b3: 4 passed.
- `verify_gate_review` on the 04 review: 0 failures. `dumps_result` prints `"ok": true`.
- `pytest tests/contracts -p no:cacheprovider -q`: 5 passed in 17.52s.
- `pytest tests/rule_discovery -q -p no:cacheprovider`: 352 passed in 1071.40s.
- Full 04 CLI: exit 2, identity drift on task receipts, registry gate clean.
