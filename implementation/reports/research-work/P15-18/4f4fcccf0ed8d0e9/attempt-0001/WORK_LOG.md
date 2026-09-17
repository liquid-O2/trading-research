# P15-18 — attempt-0001 of bank 4f4fcccf0ed8d0e9 (definitive). One line per decision.

**Definitive refinement round.** It refines the definitive breadth screen
`P15-17/6cc3b4628129100d/attempt-0003` (the 160-candidate bank plus the executed profile supplement),
whose allowlist is pinned by sha256 in `RUN_META.bank.allowlist_sha256`.

**Why the earlier `d183bbbaa3e5b556/attempt-0002` is superseded, not deleted:** it refined the same
breadth run *before* the 2026-09-16 profile supplement was evaluated with it. The merged evaluation
selects a P4 bank for KEANI, so the allowlist changed and with it the bank: 46 distinct candidates
became 53, and the neighbourhood table gained the registered "P value-area fraction" row. That attempt
stays on disk as evidence of the pre-supplement round; nothing in it is reused here.

- Bank: 217 proposals over 5 folds -- 186 attempted, 31 duplicates (a parent's own value re-proposed),
  0 not applicable -- 53 distinct candidates executed on all 1,742 declared dates at 10 workers in
  1,556 s. `2020-06-30` keeps the same retained runtime failure as the breadth run.
- Caps held: at most 12 attempted neighbours per bank and 24 per family, checked independently in
  `SELF_CHECK.txt`.
- Hold-out: 112 dates of 2026-04-01..2026-09-03 are trimmed from every fold window before anything is
  scored, in the selection, in the combination stage and in the ledger rows. A test moves a hold-out
  date's outcome and the fold's choice does not move, against the in-block control that does.
- Combinations: 20 proposals, 10 attempted and 10 `not_applicable` because their two mechanisms live on
  different branches of the family and cannot share one scan; 3 distinct combinations executed with both
  mechanisms installed, and their interaction is labelled against each ingredient and against B0.2.
- Ledger: 237 rows = 217 neighbour proposals + 20 combination proposals. 22 promoted, 143
  inconclusive_support, 41 unsupported_owned_input (duplicates), 18 rejected_by_evidence, 13
  retained_baseline. Every row carries `parent_trial_ids` and, where not promoted, a failure attribution.
- `SELECTED_RULES_BY_FOLD.json` carries a per-fold `selection_manifest_id` with each fold's roles and
  their parents, and the all-history descriptive recommendation
  (`GB-FAIL:previous_hour:T4:shift_minutes=-15`) separately labelled and never applied backward.
- `FAMILY_DISPOSITIONS.json`: 3 families active_selected, 3 active_baseline; nothing discarded.

## Receipt and verification

- `TASK_RECEIPT.json` with PLAN_SNAPSHOT, CODE_SNAPSHOT, DRAFT_MANIFEST, EVIDENCE_MATRIX (every
  acceptance key and assigned assurance case bound to a test node id, a command index and hashed
  evidence), DECISIONS.tsv, REPORT.md and RESULT_CARD.json; the predecessor receipt is pinned by digest.
- 2026-09-17: the branch is merged, so every declared file is hashed from /workspace. The receipt was
  re-issued against the live tree and rebound to the re-issued predecessor digest, and the recorded
  pytest command was re-run there. `tools/verify_research_release.py task` now exits 0.
