# P15-17 stage B — work log (one line per decision)

Attempt `6cc3b4628129100d/attempt-0001`. Stage A record `47dedaaa4f5b9ce1` is kept and cited;
its FREEZE.json is the immutable input of this attempt (bank, splits, gates, seed, resource profile).

- Run root id `6cc3b4628129100d` = first 16 hex of SHA256 of the canonical run manifest
  (task, stage, freeze sha256, bank sha256, split/evaluation-protocol sha256, B0.2 roots, date count,
  pairing baseline); deliberately independent of the code hash so a code fix does not move the root.
- New module `rule_discovery/search_run.py` owns stage B; `search.py` keeps the candidate machinery.
- Runner registration is additive: `runner.slice_run` / `runner.resume` dispatch on `task_id == "P15-17"`
  and `runner.summarize` dispatches when the run root's RUN_META.json carries that task id. No other
  task's path changes; `tools/run_rule_discovery.py` is untouched.
- P15-17 passes its frozen FREEZE.json as `--manifest`; it has no P15-02 frozen manifest of its own.
- Budget gate: projection = dates x (frozen per-session p90 156.901 s + measured stage B overhead 18 s)
  / (workers x 3600). 1,742 dates on 17 workers = 4.98 h against the 24 h stage budget. The gate refuses
  to start over budget and prints the projection; it never reduces coverage, dates or the bank.
- Worker count = floor(cpu.max quota/period) = 17, minus none (PERFORMANCE.md process hygiene).
- Per session: `search.load_b02_market(day, warm=True, branches=<26 bank branches>)` loads the account
  day once and prepays every branch's cold B0.2 scan; all 148 supported candidates then run on that view.
- The 12 unsupported candidates get an `unsupported` job row carrying the adapter's own reason. They are
  never silently dropped, and they stay in the ledger and the retention set.
- Pairing baseline: the P15-16A job bytes under the supplied run root, read-only, with path and sha256
  recorded per job. Branch `REFILL-STUDY:supplied_selected_order` has no B0.2 job in any P15-16A root,
  so its 2 candidates fall back to the in-process B0.2 scan and record
  `pairing_baseline_source = in_process_b02_scan` with the reason. Open item for the corrected root.
- Benchmark: entries frozen from each scan's own `pass` episodes (`exits.frozen_entry_from_b02_episode`),
  managed by the frozen E0 policy (`exits.evaluate_policy_compact`), whose exit price, 1-tick slippage,
  250 ms latency and $2.50/side commission come from `contracts/execution.py`. Day accounting is the
  one-mini benchmark's: one position at a time, the $1,000 day loss limit, complete zero-entry days kept.
- A04 is an assertion inside `daily_benchmark`: opportunities == fills + exclusions, and daily net points
  == the sum of the filled entries. A day that cannot reconcile raises instead of being written.
- `contracts.execution.replay_family` is NOT used per candidate: it rescans the whole day's quote list per
  opportunity, which is O(day) per entry for 148 candidates x 1,742 days. The same costed arithmetic is
  reached through `exits.py`, which imports it. Declared, not hidden.
- Cost stress uses the declared setting (500 ms latency, 2 ticks, $3.50/side) by rebinding the two module
  constants `exits.py` reads at call time inside a context manager that restores them; no file is edited.
- Diagnostics for `failure_attribution` come from the tape: missed-move share (exit by expiry/deadline),
  stop-first share, `nearest_approach_S` and `adverse_S_before_favorable_0_5S`, with S = the registered
  60-minute scale (`search._f1_geometry(view, at, 60)`), the same scale F3 balances against.
- Density-matched controls: Reference-bank candidates also run with their own enumeration hook wrapped so
  the reference band moves by offset x S, offset cycled by SHA256(reference_id) mod 4 over {-2,-1,+1,+2};
  count, width, issue time, expiry, direction and every stage/exit rule are unchanged; an offset that
  would duplicate a real band within one tick is skipped, and exhaustion marks the control unavailable.
- Selection is inner-only: fit + tune days of the fold, ranked on primary daily net-point improvement over
  B0.2 on common complete days, then the 1% simplicity rule inside each bank (`pick_representative`),
  then `refinement.select_banks` for at most two banks per family with nonnegative improvement and inner
  support. Outer test outcomes are not read by `select_for_fold` at all (A02).
- Decision stage: `refinement.centered_bootstrap_pvalue` for every candidate (moving block, seed 15022026,
  2,000 draws, block length 5, via contracts.evaluation), Holm across every candidate, then
  `refinement.evaluate_promotion` with support sensitivity at half and twice the gate and the frequency
  floor at 50% of baseline entries.
- `search.py` TAPE_LAST corrected from 2026-08-19 to 2026-09-03: that literal was a stale stage A guard;
  the chained amendment on main (cd76b741) corrects the native calendar endpoint, and the last 11 declared
  sessions load, warm with zero failures and scan. Without the fix 11 of 1,742 dates would have been lost.
- Native slice: five dates from the registered engineering set chosen by fixture role (first complete date
  of 2020, the 2023-11-06 DST transition, the first complete dates of 2024 and 2026, and the partial final
  2026-09-03), never by outcome.
- In-process scans get their episode identity from P15-16A's own `_ensure_candidate_ids`: without it
  `exits.frozen_entry_from_b02_episode` has no entry id and declines the entry, which cost MEMBER, SAINT,
  SIRES and JJ candidates entries their paired baseline kept (measured: MEMBER 0 -> 6 fills on the slice).
- Each benchmark entry records fill price, initial stop, objective, exit price and the round-trip cost, so
  any reader can recompute `net_points` from the artifact alone (632 recomputed on the slice, all equal).
- A resume under changed code records the superseded code identity in RUN_META.previous_code_identities;
  identity is never silently rewritten.
- Run identity binds the runtime modules (search, search_run, runner, refinement, exits), not test bytes,
  so editing a test cannot rewrite the identity of jobs already on disk.
- A declared session outside the native tape (2020-01-01, a closed RTH holiday for which P15-16A wrote
  zero-episode jobs) gets a `session_unavailable` row for every candidate with the reason, `complete=false`,
  and is excluded from every paired denominator. It is reconciled, never dropped and never imputed as a
  zero-net-points trading day.
- An episode the E0 policy cannot manage (its decision clock is at or after the account-day flatten, so
  `exits.FrozenEntry` refuses it) is an exclusion carrying the contract's own message, not a lost date.
  The first launch lost 3 dates in the first 14 to that; the burn-in root re-runs exactly those dates.
- A failure inside one candidate (scan or benchmark) is a `runtime_failure` row for that candidate and a
  failure of the paired baseline is recorded on the branch; only a session that cannot load fails a date.
- Burn-in evidence: `burn-in/` re-runs 2020-01-01, 2020-01-06, 2020-01-10, 2020-01-24 and 2021-03-12 --
  0 failed dates, 148 evaluated + 12 unsupported rows per available date.
