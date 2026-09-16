# P15-18 stage — attempt-0001 (rehearsal). One line per decision.

**Rehearsal.** The refinement runs on the P15-17 *rehearsal* allowlist
(`P15-17/6cc3b4628129100d/attempt-0002/REFINEMENT_ALLOWLIST.json`, sha256 in `RUN_META.bank`), whose
pairing baseline is the uncorrected P15-16A root. No disposition here is a research finding about a
candidate. The definitive refinement runs on attempt-0003's allowlist: point `run_refinement` and
`evaluate_refinement` at that breadth run root and both re-run unchanged.

## The bank

- The bank is a pure function of the allowlist: `refinement.build_refinement_bank(allowlist, cutoffs)`.
  It calls the existing `generate_neighbors`, so the neighbourhoods are the contract's table and nothing
  else; `REFINEMENT_BANK.json` keeps a row for every proposal with its status and reason.
- Counts: 190 proposals over 5 folds, 165 attempted, 25 duplicates (the parent's own value re-proposed),
  0 not applicable; 46 distinct (family, branch, recipe, parameters) candidates actually executed.
- Caps: at most 12 attempted neighbours per bank and 24 per family, enforced by `generate_neighbors` and
  re-checked independently in `SELF_CHECK.txt`.
- Defect found and fixed at its cause: `select_banks` did not carry the selected bank's `branch`, so two
  branches of one family and recipe collided in the neighbour identity (41 "distinct" candidates instead
  of 46). `select_banks` now emits `branch`, `build_refinement_bank` refuses a bank without one, and an
  allowlist written before the fix still resolves through the parent's own resolution.
- The past-only guard: `generate_neighbors` compares an availability instant to the fold's fit cutoff.
  The registered timing neighbourhood is -30..+30 minutes, so the parent issue is taken one maximum shift
  before the cutoff (`fold_guard`): every registered shift is decidable by the cutoff and a wider shift is
  refused as `past_only_allowlist` (tested).

## The run

- Execution reuses the breadth runner with a different bank: `search_run.run_dates(..., candidates=...)`.
  Same sessions, same B0.2 pairing, same E0 benchmark, same checkpoints, resume and completion path, so a
  refinement run is auditable exactly like a breadth run.
- Measured one session first (HOW_TO_RUN step 4): 2024-03-05 fresh 22.1 s (21.1 s of it load and warm),
  2021-06-01 steady in the same process 6.5 s, peak RSS 2.06 GB after two sessions.
- Budget: cgroup usage read before launch (24.4 GB of 77.3 GB); 12 workers x ~1.6 GB measured = 18.4 GB
  for the whole pool, plus up to 10 GB for the concurrent P15-16A producer, under the 70 GB ceiling.
- The budget gate still projects from the frozen breadth profile (7.05 h at 12 workers against the 24 h
  budget) and is printed in `run.log`; the realised rate was far lower because the bank is 46 candidates.
- `2020-06-30` fails again with `no native account-day view`: the same retained runtime failure as the
  breadth run, kept in the ledger as such, never a data rejection.

## The evaluation

- `refinement.evaluate_refinement(run_root, breadth_run_root, freeze_path)` streams the refinement run's
  daily shards exactly as the breadth evaluation does, selects inside each bank on that fold's fit+tune
  days with the same 1% simplicity rule, and never reads a test day to choose anything.
- Fold isolation is tested directly: moving only the 2022 fold's test days (which are the 2023 fold's fit
  days) leaves the 2022 choice identical and moves the 2023 choice.
- One combined candidate per family per fold, from two different banks, only when each ingredient beats
  B0.2 on inner tuning by itself; `build_combined_overrides` puts both mechanisms on one scan by chaining
  the enumeration hooks and merging the stage hooks.
- The negative control is native: on 2021-06-01 the parent's own parameter value reproduces the parent's
  scan byte for byte and a contract neighbour value does not, so a refinement that never reached the
  scanner would fail.

## Results (rehearsal)

- Bank: 190 proposals, 165 attempted, 25 duplicates, 0 not applicable; 46 distinct candidates executed
  over all 1,742 declared dates (`REFINEMENT_BANK.json`, `RUN_COMPLETE.json`: 80,132 declared jobs =
  80,086 written + 46 absent on the retained failure date, reconciled).
- Caps held with room to spare: at most 9 attempted neighbours in one family-fold (limit 24) and 6 in one
  bank (limit 12) -- recomputed independently in `SELF_CHECK.txt`.
- Combinations: 20 proposals (4 families x 5 folds), 10 attempted and 10 `not_applicable` because their
  two mechanisms live on different branches of the family and cannot share one scan. The 3 distinct
  executable combinations ran as their own bank under `combinations/` with both mechanisms installed.
  Interactions are labelled: GB-FAIL additive in every fold (the combination is below its T4 ingredient
  alone), SAINT-AMT additive in 2022-2024 and synergistic in 2025 and 2026.
- Ledger: 210 rows -- 190 neighbour rows (attempted, duplicate) and 20 combination rows -- every row with
  a disposition, a `failure_attribution` where it is not promoted, and `parent_trial_ids` pointing at the
  breadth-selected bank it refines (`TRIALS.jsonl`).
- Three candidates clear the promotion gates in this rehearsal: `GB-FAIL:previous_hour:T4:shift_minutes=-15`,
  `JJ-TBR:judas_reversal:S4:deadline_minutes=10` and the GB-FAIL combination. They are rehearsal numbers
  against an uncorrected pairing baseline, not research findings.
- `SELECTED_RULES_BY_FOLD.json` carries a per-fold `selection_manifest_id`, the fold's roles with their
  parents, and the all-history descriptive recommendation separately labelled; `FAMILY_DISPOSITIONS.json`
  gives each family a retention status and its first attribution.

## Self-check (evidence in this directory)

- Independent recomputation (`SELF_CHECK.txt`, `self_check.py`, plain json/gzip/Decimal): the fold-2022
  inner improvement of `GB-FAIL:previous_hour:F3:efficiency=0.5` over 455 common complete inner days
  recomputes to 1.744505 against the artifact's 1.744505 (delta 0).
- Native trace: that candidate on 2021-09-28 pairs against the P15-16A job
  `GB-FAIL--branch--previous_hour.json.gz`, whose recorded sha256 recomputes from the bytes, and its
  entry's net points recompute to -3.75 from fill, exit and commission.
- Reconciliation: every neighbour proposal has exactly one ledger row (190/190), every combination
  proposal has one (20/20), every row has a disposition, all 210 carry parent trial ids.
- Cost: the refinement run took 1,362 s on 12 workers for 46 candidates x 1,742 sessions; the combination
  run 3 candidates over the same sessions; the evaluation 45.5 s at 0.158 GB peak RSS, streaming.

## Incidents

- `tests/rule_discovery/test_p15_18.py` already held 42 planning-era tests for refinement.py and was
  overwritten by a `cat >` when the new tests were first written. Restored from `HEAD` and the new tests
  appended instead; no test name collides and the diff is now purely additive (+415/-0). The whole file
  passes, so the restored coverage is intact.
- The first combination run aborted on a `bank_identity` without a digest, and the retry was refused by
  the run root's own conflict guard ("frozen with a different configuration: ['bank']") because the
  aborted attempt had written RUN_META.json. The guard behaved correctly; the empty root was cleared and
  the stage re-launched.
