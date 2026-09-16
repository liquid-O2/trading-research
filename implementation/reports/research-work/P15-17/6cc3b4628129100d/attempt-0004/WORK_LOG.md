# P15-17 profile supplement — attempt-0004. One line per decision.

The 2026-09-16 supplement of SEARCH_CONTRACT's Profile row (P3 value area .68, P4 value area .40), run
as its own attempt under the same run root as the definitive breadth screen and evaluated with it in one
Holm family. The decision trail of the merged evaluation is `../attempt-0003/WORK_LOG.md`.

- Declared before any result: `CANDIDATE_BANK_SUPPLEMENT.json`, `declared_at`
  2026-09-16T21:10:28Z, hashed into `RUN_META.bank.sha256` by the runner's own init, which runs before
  the first session. 20 candidates on the ten branches that carry P1/P2 today.
- Duplicate rule: a candidate whose fraction equals the branch's own B0.2 fraction is recorded
  `duplicate` and not run. SAINT-AMT's B0.2 track uses `fraction=".68"`, so the four SAINT P3 cells are
  duplicates; the other six families reach `historical_features.profile` at .70, so all their P3 and P4
  cells are genuine one-axis changes. 16 executed, 4 duplicates.
- One axis only: the candidates are the branch's own P1 resolution with `fraction` replaced;
  `search.py` passes it to `profile_value_area` as a Decimal and records `profile_fraction` in the stage
  operands, so a parameter that never arrived would be visible rather than silently repeating P1.
- Same roots (both B0.2 roots, supplemental first), same folds, same hold-out exclusion, same engine.
  1,742 dates at 6 workers in 2,256 s; 2020-06-30 keeps its retained failure record.
- Nothing about the supplement is chosen from a result: the branches come from the frozen bank, the two
  fractions from the contract, and the duplicate rule from the code that builds each branch's baseline.
