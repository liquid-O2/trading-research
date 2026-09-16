# P15-17 stage B — attempt-0002 (rehearsal). One line per decision.

**This attempt is the rehearsal and the parity oracle, not the definitive breadth screen.**
It pairs against the uncorrected P15-16A root `1019e6c09ee54609`, and its P15-16A receipt field is
PENDING. No disposition in `BREADTH_RESULTS.json` here is a research finding about a candidate.
The definitive run is `attempt-0003`, launched by the orchestrator after P15-16A closes, on the merged
code, with the corrected and supplemental B0.2 roots and the receipt digest in RUN_META. Every
deliverable below is a function of the run root and re-runs against attempt-0003 in minutes.

Stage A `47dedaaa4f5b9ce1` (bank, splits, gates, seed, resource profile) is the immutable input and is
unchanged. The engine take-over log is `../../_fast/WORK_LOG.md`.

## The run

- The run was produced by the fast engine in this worktree; 1,741 of 1,742 declared dates carry 160 job
  documents and a daily record. `2020-06-30` raised `ContractError: no native account-day view` and keeps
  its `failed/2020-06-30.json` record: a runtime failure, never a data rejection.
- RUN_META carries two code identities: the run started under a runner without the per-session cache
  release and finished under the runner with it. Equivalence is measured, not assumed — four first-segment
  dates re-run under the second identity gave 640/640 candidate documents and 4/4 daily records
  byte-identical (`../../_fast/WORK_LOG.md`, round 2, "Identity equivalence").
- Completion: a run whose only pending dates carry retained failure records is now closed by
  `search_run.complete_run`, which writes `RUN_COMPLETE.json` naming every retained failure and the
  arithmetic that shows what it did not write: 278,720 declared = 278,560 written + 160 absent on the
  failed date. A pending date with no failure record is refused as unfinished work. `complete_run` reads
  checkpoints, shards and failure records only; it never re-runs a date and never touches RUN_META, so the
  run keeps the identities that actually produced its documents.

## The evaluation

- The evaluation is a pure function of the run root: `search_run.evaluate_run(run_root, freeze_path,
  out_dir)`. It streams `daily/<date>.json` one date at a time into per-candidate `CandidateSeries` and
  never holds the 278,560 job documents. Measured on this attempt, one process: 152.4 s, peak RSS 0.287 GB.
- Bounded measurement first (AGENTS.md): 100 dates gave 0.0079 s/date streaming at 0.144 GB and
  1.31 s/date for the job-document reconciliation at 0.145 GB, so the full passes were projected at
  ~14 s and ~38 min before either was started.
- Computation is separate from loading and from evidence writing: `paired_row`, `_inner_from_paired`,
  `_outer_from_paired`, `_select_from_inner_rows`, `classify_failure` and `pick_representative` are pure;
  `stream_run`, `load_daily_table` and `reconcile_jobs` load; `evaluate_run` writes.
- The same scoring core serves both paths, so the streaming evaluation and the in-memory table cannot
  drift apart; a test asserts they produce identical inner rows, outer rows and fold selections.
- `reconcile_jobs` streams every declared job document once, per date and family, holding one at a time:
  it checks A04 on both sides of the pairing, verifies each artifact self-identifies as the declared
  (date, candidate), checks the sanitized artifact names are injective over the bank, tallies exclusion
  and exit reasons per family, and reconciles declared jobs against documents plus explicitly absent ones.
- 800 candidate-date rows recorded `runtime_failure` with `market has no cutoff clock`: 20 holiday
  sessions x the 40 SIRES and REFILL-STUDY candidates whose families read the native view. That is a
  missing input, not a defect in a candidate, so `classify_failure` separates `input_unavailable` from
  `software_failure`: the missing input keeps its row and its dates, informs coverage, and does not fail
  the promotion gate's software flag. All 800 classify as `input_unavailable`; zero software failures.
  The runner now writes that terminal disposition directly, so attempt-0003 records it at the source.

## What the rehearsal produced

- 160 candidates: 148 supported, 12 unsupported with the adapter's own reason. Rows by terminal
  disposition: 256,720 evaluated, 20,880 unsupported, 800 input_unavailable, 160 session_unavailable.
- TRIALS.jsonl: 800 rows = 160 candidates x 5 outer folds, every row with a disposition, every
  non-attempted row with a `failure_attribution`.
- No candidate was promoted. Dispositions: 89 inconclusive_support, 38 retained_baseline,
  21 rejected_by_evidence (13 Holm, 4 coverage, 4 cost stress). First attributions: 48 location_miss,
  43 support, 36 frequency, 12 confirmation_delay, 4 adverse_before_target, 3 cost_sensitivity,
  2 coverage. Retention: 13 active_selected (the fold picks), 147 inactive_retained; nothing discarded.
- REFINEMENT_ALLOWLIST.json: per fold, at most two banks per family (10, 10, 9, 8, 8 across 2022-2026)
  with the exact neighbourhoods refinement.py will expand.

## Self-check (all evidence in this directory)

- Scope: two tracked files changed, `search_run.py` (+575/-53) and `test_p15_17.py` (+292/-3); every
  other change is new evidence under this attempt.
- Independent recomputation, `SELF_CHECK.txt` / `self_check.py` (plain json/gzip/Decimal, none of
  search_run's arithmetic): the top candidate's mean paired improvement 37.435900 over 1,219 test days
  and 5 blocks reproduces the artifact exactly (delta 0); an independent implementation of the
  SEARCH_CONTRACT selection rule (best per bank, 1% simplicity, nonnegative improvement, inner support,
  two banks) reproduces fold 2022's SIRES picks.
- Native trace, same file: `SIRES:absorption_reward_retest:S1` on 2024-03-05 pairs against
  `P15-16A/1019e6c09ee54609/jobs/2024-03-05/SIRES--branch--absorption_reward_retest.json.gz`; its
  recorded sha256 recomputes from the bytes, the entry id is present in that source job's episodes, and
  the entry's net points recompute to 10.75 from fill, exit and commission.
- Declared jobs reconcile with unique artifacts and terminal dispositions, `JOB_RECONCILIATION.json`:
  278,560 documents read, 0 A04 violations, 0 identity mismatches, 0 artifact-name collisions, 278,720
  declared = 278,560 written + 160 absent, dispositions cover the declared set.
- Gates: `test_every_gate_is_load_bearing` mutates one gate input at a time and each flips the verdict;
  `test_a02_outer_outcomes_do_not_change_the_fold_choice` perturbs outer outcomes (choice unchanged) and
  inner tuning (choice changes).
- Negative control: the RA-1 per-family control (no override installed, byte-identical to B0.2) passes in
  the owned suite.
- Measurement protocol, `EVAL_COST.txt`: bounded 100-date measurement first (0.0079 s/date streaming at
  0.144 GB, 1.31 s/date reconciling at 0.145 GB), then the full passes -- evaluation 152.4 s at 0.287 GB
  peak RSS, reconciliation 2,397.5 s at 0.123 GB, both single process. Container usage was read before
  every launch; the heaviest moment was the 3-worker native slice at 14.9 GB of the 77.3 GB cgroup.
- Tests: `logs_pytest_owned.log`, 82 passed, 0 skipped (test_p15_17.py, tests/contracts,
  tests/method_pack/test_event_time_fast.py). The six native-slice checks run here against
  `native-slice/` (5 declared dates, 800/800 job documents, 37.8 s on 3 workers) rather than skipping.
