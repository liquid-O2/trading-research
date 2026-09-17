# P15-19 exit study — definitive-0001. One line per decision.

**Definitive fixed-entry exit study.** The frozen entries are the selected rules of the definitive
refinement `P15-18/4f4fcccf0ed8d0e9/attempt-0001`, whose entries were produced against the definitive
breadth run `P15-17/6cc3b4628129100d/attempt-0003` (both B0.2 roots, supplemental first). The rehearsal
`P15-19/rehearsal-0001` stays on disk as evidence of the same machinery on the rehearsal allowlist.

- Boundary: a separately counted decision family, run after entry selection is frozen. Every comparison
  carries the entry stage's own disposition unchanged and `entry_rescued: false`; a test gives a rejected
  entry rule a hugely better E2 and shows the entry verdict does not move.
- Frozen entries: 18 selected rules (refined, retained-parent and combined roles), 9,575 entries over
  1,680 account days, taken from the entry runs' own job documents -- entry id, side, fill clock and
  price, initial structural stop, objective and round-trip cost. Nothing is re-scanned.
- E0 is recomputed from those frozen entries and compared with the E0 the entry run recorded: **0
  mismatches over 9,575 entries**, so the reconstruction loses nothing and no source deadline bound
  ahead of the 60-minute expiry anywhere in this population. A day that did not reproduce would leave
  the paired comparison with its reason rather than be averaged in.
- Run: 6 workers, 409.6 s, one shard per day, checkpoint per day, 0 failed dates. Measured first: one
  account day costs 9.1 s cold and 0.75-3.1 s warm, peak RSS 0.58 GB; cgroup usage read before launch.
- Comparisons: 72 = 18 rules x E1..E4, all against E0 on the same unchanged entries, with the frozen
  block bootstrap (seed 15022026, 2,000 draws, block 5, segmented by calendar year) and Holm across the
  exit stage. Mean improvement over the rules: E1 -0.47, E2 +0.35, E3 +0.40, E4 -0.13 net points per
  common complete day. **None clears the promotion gates**: 47 retained_baseline, 13
  rejected_by_evidence, 12 inconclusive_support.
- Hold-out: no hold-out date enters any comparison; each comparison reports its own excluded count and
  the study records the range.
- Unsupported E3/E4 records (undefined initial R) keep their entry in the ledger and remove only that
  policy's day; occupancy-flagged entries are counted per policy, not merged into the primary series.

## Receipt and verification

- `TASK_RECEIPT.json` with PLAN_SNAPSHOT, CODE_SNAPSHOT, DRAFT_MANIFEST, EVIDENCE_MATRIX (every
  acceptance key and assigned assurance case bound to a test node id, a command index and hashed
  evidence), DECISIONS.tsv, REPORT.md and RESULT_CARD.json; the predecessor receipt is pinned by digest.
- 2026-09-17: the branch is merged, so every declared file is hashed from /workspace. The receipt was
  re-issued against the live tree and rebound to the re-issued predecessor digest, and the recorded
  pytest command was re-run there. `tools/verify_research_release.py task` now exits 0.
