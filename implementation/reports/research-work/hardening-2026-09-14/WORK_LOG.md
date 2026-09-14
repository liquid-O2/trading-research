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
