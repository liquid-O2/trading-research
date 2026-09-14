# Hardening pass 2026-09-14 — 00-foundation and 01-native-and-outcomes

Coordinator work log. One writer in `/workspace`. Python `/workspace/implementation/.venv/bin/python`. pytest `-p no:cacheprovider`. No git commit/push/reset/clean/stash/checkout/rebase. Do not start 02.

## Exit condition

Part A verifier supersession under `research-assurance-2026-09-14-v3`, Part B review fixtures plus B5–B9, Part C new immutable attempts for P15-00, P15-01, 00 subphase, P15-02, P15-03, 01 subphase, Part D status documents. Stop at the end of this pass.

## Decisions

1. Plan-file live mismatch is explained only by an ordered `AMENDMENTS.json` chain of new-shape entries (`date`, `id`, `changed_files[{path,sha256_before,sha256_after}]`, `assurance_version`, `previous_entry_sha256`). Snapshot copies still match the receipt's own declared hashes.
2. The 2026-09-14 v2 assurance amendment keeps its original shape and is the chain root. `previous_entry_sha256` of the v3 plan amendment is `digest` of that root object.
3. Files that did not exist at `03451e72` (DELIVERABLES.md, RETENTION.md) use SHA256 of empty bytes as `sha256_before`.
4. Code-file live mismatch is explained only by a later receipt in `receipts_root` that lists this receipt among transitive predecessors, declares the live hash, and verifies under this rule. Recursion is cycle-safe via `pending_ok` (skip re-verifying the receipt being superseded) distinct from graph-cycle placeholders.
5. Receipt `assurance_version` mismatch is `IDENTITY`, not `SCHEMA`. `validate_receipt_shape` only requires a nonempty string.
6. Draft time for the date-before rule is `DRAFT_MANIFEST.drafted_at` (ISO date prefix). Missing drafted_at skips the date check.
7. Tests inject `AMENDMENTS.json` via `--amendments`. Production default is `planning/research-program/AMENDMENTS.json`.
8. Coordinator edits P15-00-owned `identity.py` only to pin `ASSURANCE_VERSION` and the shape check; that is shared-file integration for the assurance bump.

## Hardening 2 — 2026-09-14 verifier mid-chain walk

Headless. One writer in `/workspace`. grok-4.6. No nested code writers. Do not start 02.

### Reproduction

Verifier on P15-02 `c9756fc1e534b240` exit 2; first failure IDENTITY `plan declared hash does not match workspace bytes for planning/research-program/TASK_GRAPH.json`. Subphase `50587897e824ede8 --gate-review` exit 2; first failure the same IDENTITY, plus GATE_REVIEW `review graph hash is not the current task graph`. Declared graph `859d5c6e...` (entry 2 after-hash); live `938c847e...` (entry 3 after-hash). Saved under `hardening-2/repro-*.json`.

### Decisions

9. `_plan_superseded_by_amendments` starts the path walk at the first chained entry whose `sha256_before` for that path equals the declared hash. Earlier chained entries and entries that do not touch the path are skipped, not rejected.
10. `previous_entry_sha256` is still checked for every new-shape entry from the first new-shape entry onward, even when the path walk starts mid-chain.
11. An entry dated strictly before `DRAFT_MANIFEST.drafted_at` is skipped unless it supplies the declared hash's successor, in which case it is rejected. Same-day dates are not predating.
12. GATE_REVIEW graph path must still be the live graph file. The bound graph hash, and the independent-results "current graph path and hash are bound together" check, accept a mid-chain hash when the same walk connects it to the live hash. A hash in no chain still fails GATE_REVIEW.
13. `_bind_review_file` does not require the graph hash to equal live file bytes; the chain-tolerant check owns that comparison. Other review bindings still require byte identity.
14. Subphase and phase CLI gain `--amendments` and forward it into nested task verification and `verify_gate_review`.
15. After new P15-00/P15-01 exist, update P15-02-owned `runner.py` predecessor pins and `produce_01.py`'s foundation-checker subphase path as shared-file integration. Do not edit the pinned checkers or review probes.
16. Part C uses a separate process and an isolated AMENDMENTS copy so the in-process verify cache cannot leak. The live ledger is not edited for that proof.
17. Part D appends one chained amendment after the chain proof. Assurance version stays `research-assurance-2026-09-14-v3`. Wiki/handoff update only if 00 and 01 `--gate-review` exit 0.

18. Part C on previous P15-02 `c9756fc1e534b240`: live-ledger verification no longer reports TASK_GRAPH IDENTITY (the walk through entry 3 succeeds). Full exit 0 is blocked by this repair's own live code bytes (`runner.py` pin retarget; nested P15-01 `receipts.py` / `test_p15_01.py` / `verify_research_release.py`). Previous P15-00 `3df87f26477a4205` declares the same `859d5c6e` graph hash, has no code mismatch, and verifies exit 0 through entry 3. Isolated AMENDMENTS copy with entry 3 removed fails IDENTITY first on TASK_GRAPH. Live ledger was not edited for that copy.

19. After the new amendment entry, both `--gate-review` commands still exit 0. No planning formula/budget/date files were changed; changed_files are receipts.py, test_p15_01.py, verify_research_release.py, and runner.py.
