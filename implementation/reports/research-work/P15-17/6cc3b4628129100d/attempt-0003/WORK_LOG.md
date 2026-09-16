# P15-17 stage B — attempt-0003 (definitive). One line per decision.

**Definitive breadth screen.** Produced by the orchestrator on the merged code (P15-16A integration
round 3) with both B0.2 roots, the supplemental `823273eba4b9ec50` first and the main
`1019e6c09ee54609` second, at 17 workers. `RUN_META.json` carries one code identity
(`2758b5f8946073de`, no supersessions) and `p15_16a_receipt: PENDING` for the orchestrator to fill.
The rehearsal and parity oracle is `attempt-0002`; stage A `47dedaaa4f5b9ce1` remains the frozen input.

- Run: 1,742 declared dates, 1,741 with 160 job documents and a daily record; `2020-06-30` keeps its
  genuine `no native account-day view` failure record. `RUN_COMPLETE.json` closes the run through the
  retained-failure path: 278,720 declared = 278,560 written + 160 absent on that date, reconciled, with
  `SHARD_INVENTORY.json` carrying the file-level hashes of the gitignored daily and checkpoint shards.
- Terminal dispositions over the 278,560 rows: 256,720 evaluated, 20,880 unsupported, 800
  `input_unavailable` (20 holiday sessions x the 40 SIRES and REFILL-STUDY candidates whose families read
  the native view -- a missing input, recorded at the source by the runner in this run, not a software
  failure), 160 `session_unavailable` (2020-01-01, a closed RTH holiday).
- Blind hold-out (EVALUATION.md amendment 2026-09-16): 112 dates of 2026-04-01..2026-09-03 are trimmed
  out of the 2026 outer test window before anything is scored. They enter no inner tuning, no Holm
  family, no gate and no table here; `BREADTH_RESULTS.json.holdout_excluded` and every ledger row record
  the exclusion. Their job documents stay on disk for the release replay (`search_run.holdout_replay`).
- Evaluation: streaming, 69.7 s, peak RSS 0.285 GB. 800 ledger rows = 160 candidates x 5 folds.
- Result: no candidate clears the promotion gates. 91 inconclusive_support, 38 retained_baseline,
  19 rejected_by_evidence. The baseline is retained in every family; 45 bank selections across the five
  folds go forward to refinement (10, 10, 9, 8, 8).
- The bootstrap now draws block starts inside each calendar-year segment, as EVALUATION.md requires, and
  reports block lengths 1 and 10 beside the frozen block 5 as sensitivity.
- Self-check (`SELF_CHECK.txt`, `self_check.py`): the top candidate's mean paired improvement 25.779936
  over 1,094 hold-out-free test days and 5 blocks recomputes exactly (delta 0); an independent
  implementation of the selection rule reproduces fold 2022's SIRES picks; the native trace reaches the
  P15-16A job bytes with its sha256 recomputed; declared jobs reconcile to unique artifacts and terminal
  dispositions.
- `RESULT_CARD.json` (and REPORT.md's last section): verdict `not_reaching_target`, met `no`.

## Profile supplement (attempt-0004), merged evaluation

- The 2026-09-16 supplement is declared in `../attempt-0004/CANDIDATE_BANK_SUPPLEMENT.json` and hashed
  into that attempt's `RUN_META.bank` *before* the run starts (`declared_at` 2026-09-16T21:10:28Z, the
  first checkpoint later): 20 one-axis candidates, P3 value area .68 and P4 value area .40, on exactly
  the ten branches that carry P1/P2.
- Four are recorded `duplicate` and not run: SAINT-AMT's B0.2 track builds its value area with
  `fraction=".68"`, so P3 on continuation_retest, failed_auction_return, poc_traversal and
  trapped_buyers_retest would be the baseline under another name. Every other family reaches
  `historical_features.profile` at .70, so P3 and P4 are genuine one-axis changes there.
- `search.py` threads the recipe's `fraction` (Decimal) into `profile_value_area`; the stage records
  `profile_fraction` in its operands, so a supplement whose parameter never arrived is visible.
- attempt-0004: 16 candidates x 1,742 dates at 6 workers, 2,256 s, one retained failure (2020-06-30),
  same B0.2 roots, same folds, same hold-out exclusion as attempt-0003.
- Merged evaluation (`evaluate_run(..., extra_run_roots=[attempt-0004])`): one ledger of 880 rows
  (160 x 5 + 16 x 5), one BREADTH_RESULTS, one allowlist, and **one Holm family of 164 decided
  candidates** -- 148 supported breadth candidates plus the 16 executed supplement candidates. The 12
  unsupported breadth cells and the 4 duplicate supplement cells keep their rows but enter no test, so
  the family is 164 of the 180 declared. The 800 earlier trials' p-values are re-adjusted under this
  larger family; the file now in place is the merged one.
- Result unchanged in kind: no candidate clears the gates. 101 inconclusive_support, 44
  retained_baseline, 19 rejected_by_evidence. The best supplement candidate is
  `KEANI-OPEN-ABOVE-VALUE:source_long:P4` at +0.0397 net points per common complete day,
  inconclusive_support.
- For the release's breakdown edition: `search_run.paired_series_rows(run_root)` streams, per candidate
  and per day, the date, both sides' daily net points and the decision clock of every opportunity, so the
  release can cut by year, session bucket or day of week without re-running the search.
