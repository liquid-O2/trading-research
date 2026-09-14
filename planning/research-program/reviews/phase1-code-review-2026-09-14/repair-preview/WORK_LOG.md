# B0.1 baseline repairs work log

Worktree `/workspace/.worktrees/baseline-repair`, branch `fix/baseline-repairs`. Frozen `method_pack` files were not edited. No writes under `/workspace/data`, `/workspace/sources`, or `implementation/reports/phase1-live`. No git commit/push/checkout/reset/stash.

Python: `/workspace/implementation/.venv/bin/python`. Commands used `cwd=implementation` and `PYTHONPATH=src` unless noted.

## Round 1 (HEAD c9bdd423)

- **REPAIRS branch IDs** come from run-1.0.1 `coverage.json` as `{method}:branch:{branch}`. Extra units are not repaired.
- **Dispatcher.** A coverage id in any REPAIRS entry goes to the family scanner that includes every applicable repair for that branch. Other branches call `native_discovery.scan_branch` and get `baseline_version=B0`.
- **D1 / P1 / P2 / P4 / P6** as recorded in `implementation/src/trading_research/research/rule_discovery/WORK_LOG.md`.

## Round 2 decisions

- **C1 judas_reversal.** Sweep is searched in 09:30–09:40 first; if none, 09:40–09:50 is accepted and flagged `sweep_in_reversal_window` on the `contact` stage. `source_time_window` is True for a sweep in 09:30–09:50 so the 09:35 source case can enter. Confirmation stays the frozen O056 search around the sweep bar (on the f1 tape that confirms at 09:39). A separate reversal-window O056 search is not added: `_ob` on the 09:40 bar returns False, and TBR's outbound-exit / reversal-window missing stage is assigned to P15-09, not this repair. Sweep time remains `sweep_at`.
- **C2.** The 16:00 `action_end` override is omitted. Formation default 09:30–10:00 is the corrected window. The 16:00 population is B0 and is not altered.
- **C3.** First complete five-minute close back through the level at or after the sweep candle, forward to the branch end bound. `confirm_bar_offset` 0 is the sweep candle. Stop/objective still use the sweep-candle path. If that path is empty (P4), later bars are not searched; confirmation stays the sweep candle as frozen, so empty-path episodes remain unknown rather than flipping to fail.
- **C4.** Rejection is a wick into developing POC or prior-day VAH with a close back above, recorded as `rejection_level` on geometry and the `developing_value_rejection` stage. Developing VAL stays B0. Prior VAH requires `prior.scope_complete`; the f4 harness has no prior session, so that tape exercises developing POC.
- **C5.** Operational rule: thesis direction is +1 when the microbalance midpoint is in the lower half of the larger balance, -1 in the upper half, None if either midpoint is missing or the midpoints are equal (f6's 99–101 inside 90–110). Conjunct is numeric `sign(C-boundary)` equal to that direction, independent of the trigger selector. `historical_features.sign` is a side helper and is not used for this comparison.
- **C7.** Named assertion operands are bound to `None` with `details['unevaluated_operand']` on a `baseline_repair` stage. Structural `pocket_required` / `retracement_entry` / `tdo_required` keep their literals; False values are listed in `details['structural_not_required']`. f7 tokens the ruling did not name (`location_touched`, `reduced_expectations`, `expansion_policy`, `source_zone_known`, `source_session_allowed`, `ltf_balance_broken`, `actual_band_contact`, `selected_deviation_touched`, `actual_account_or_trade`) are left literal. `alignment_ok`, `cycle_and_indicator_rules_recorded`, `real_extreme`, `profile_allows_trade` and side-independent `bias_recorded` are in the ruling but not always f7 `True`/`False` tokens; they are still nulled. Table: `LITERAL_OPERANDS.md` beside this file.
- **C7 vs C3 verdict.** GB-FAIL `bias_recorded=None` makes a successful later reclaim **unknown**, not pass (Kleene). C3 tests check `confirm_close` / `confirm_bar_offset`. C7 tests check pass→unknown on the in-sweep-candle tape.
- **C7 vs mss_fvg_refinement.** Parent still requires `research_verdict=='pass'`. After C7 the parent is unknown, so refinement is silent until bias is evaluated. Documented, not worked around.
- **Parity branch.** `SIRES:microbalance_break` is now in C5/C7. Parity uses `GB-SCALP:bearish_small_scalp`, still outside REPAIRS, byte-equal except `baseline_version=B0`.
- **Thin wrappers.** `judas_outbound` is dispatched through the existing jumbo copy (C7 `exit_window_recorded`). `scan_refill_repaired` and `scan_stoic_data_repaired` are copies of the frozen bodies with the C7 binds. `scan_microbalance_repaired` is a copy with C5+C7.
- **P1 REPAIRS entry** is unchanged: `microbalance_break` is not added to `SIRES_LOCAL_BRANCHES`.

## Commands

```
cd implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider -q tests/rule_discovery/test_baseline_repairs.py --tb=short
# 17 passed in 23.34s, exit 0
```

```
cd implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python \
  /workspace/.worktrees/baseline-repair/planning/research-program/reviews/phase1-code-review-2026-09-14/repair-preview/run_preview.py
# 40/40 dates ok, 38 branches, orchestrator_wall_s 739.4311, exit 0
```

## Preview result (round 2, not a receipt)

- **C1** `judas_reversal`: 32→37 episodes, 3→5 pass. Five source-window sweeps enter; no C7 on this branch.
- **C2** 10:00 window: `extension_reaction` 49→25, `internal_rotation` 38→28, `single_extended` 19→14, `single_purged` 19→14. Afternoon contacts leave the corrected population.
- **C3+C7 GB-FAIL:** every B0 pass becomes unknown (`bias_recorded`). Some B0 fails become unknown where C3 finds a later reclaim that would otherwise pass. `mss_fvg_refinement` 23→0 because the parent is no longer `pass`.
- **C4 KEANI:** 0→2 pass (1 fail→pass, 1 unknown→pass).
- **C5+C7 microbalance_break:** 40 pass → 0; 38 pass→unknown (`microbalance_frozen`), 2 pass→fail (thesis-direction conjunct).
- **C7 pass→unknown elsewhere:** `judas_outbound` 35, `other_session` 55, GB-VWAP 10 (plus D1's 17 fail→unknown), SAINT passes, `kg1_retest` 11, `absorption_reward_retest` 1, `defended_band_continuation` 1, REFILL `touch_record` 9.
- **STOIC-DATA macro_application:** 0 episodes on this tape (no process_review records). C7 is implemented; census does not exercise it.
- D1/P2 fail→unknown rows from round 1 remain.

## Not done (round 2)

- No git commit. P3/P5/P7 still out of scope. TBR quadrant entries (f5) remain a missing-stage assignment. C6 is D1, already in round 1.

## Round 3 decisions (C7 refinement, 2026-09-14 evening)

The evening refinement replaces round two's C7 policy. Only Saint's three market stages stay unevaluated. Everything else keeps its frozen value.

- **`details['literal_operand_kind']` is a map** of operand name → kind (`by_construction` or `operational_assumption`). A string would collide on mixed stages (GB-FAIL: by-construction `source_session_allowed` plus `context_direction_unevaluated` plus `structural_not_required`). Tests look up the operand in that map. Recorded here because the refinement's assignment syntax was per-operand, not a single stage-wide string.
- **By construction, restored to the frozen value:** `exit_window_recorded`, `source_clock_verified`, `source_case_verified`, `real_extreme` (frozen edge-contact expression, not hardcoded True), `same_band_retest`, `kg1_retest`, `microbalance_frozen`, the four REFILL record conjuncts, `cycle_and_indicator_rules_recorded` (`True if reconstruct else None`). Restating flags already left literal in round two (`location_touched`, `ltf_balance_broken`, `actual_band_contact`, `selected_deviation_touched`, `source_zone_known`, `source_session_allowed`, `reduced_expectations`, `expansion_policy`) now also carry `literal_operand_kind=by_construction` on the corrected path.
- **`vwap_reset_verified`** stays True with `literal_operand_kind=operational_assumption` and `assumption_id=A2-GB-CLOCK`.
- **`bias_recorded`** returns to frozen `context_known` (`pre is not None and pre['known_at']<=trigger['start']`). `details['context_direction_unevaluated']=True`. Directional match to trade side is not a baseline gate.
- **Unevaluated, still None:** `arrival_read_recorded`, `alignment_ok`, `profile_allows_trade` with `details['unevaluated_operand']` as in round two. SAINT-AMT corrected baseline is unknown until P15-13.
- **C3 after bias restore.** A later five-minute reclaim now decides pass (synthetic later-reclaim tape) or fail. `mss_fvg_refinement` sees parent `pass` again. P4 empty-path still unknown (sweep extremes/stop None), never an exception.
- **C5 after microbalance_frozen restore.** Thesis-direction refusals remain fail. Mass pass→unknown from round two is gone.
- **C1–C5, D1, P1, P2, P4, P6** unchanged except the C7 operand restores above.
- **`actual_account_or_trade`** is still not a predicate operand; left unchanged.

## Round 3 commands

```
cd implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider -q tests/rule_discovery/test_baseline_repairs.py --tb=short
# 20 passed in 25.18s, exit 0
```

```
cd implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python \
  /workspace/.worktrees/baseline-repair/planning/research-program/reviews/phase1-code-review-2026-09-14/repair-preview/run_preview.py
# 40/40 dates ok, 38 branches, orchestrator_wall_s 733.3873, exit 0
```

## Preview result (round 3, not a receipt)

Matches the evening-refinement picture.

- **SAINT-AMT** passes become unknown: continuation_retest 1, failed_auction_return 9, poc_traversal 7. Round-one P2 fail→unknown remains (1+1+2). trapped_buyers_retest still 0 pass, unchanged.
- **GB-FAIL** later-reclaim C3 is pass again: asia_tdo 7, cash_open 14, nyam_box 26, previous_hour 85, prior_day 15, prior_month 3, prior_week 8 fail→pass. Two fail→unknown (prior_month 1, prior_week 1); no GB-FAIL pass→unknown. `mss_fvg_refinement` 23→48 episodes (25 new parent-pass annotations, 0→2 pass).
- **JJ-TBR C1/C2** same as round two: judas_reversal 32→37 / 3→5 pass; extension_reaction 49→25, internal_rotation 38→28, single_extended 19→14, single_purged 19→14. judas_outbound and other_session unchanged vs B0 (by-construction restore).
- **SIRES microbalance_break** 40→38 pass, 2 pass→fail (thesis refusals), 0 unknowns.
- **Unchanged vs B0** except D1/P2/C4 already in rounds 1–2: GB-VWAP 10 passes kept, 17 fail→unknown (D1); KEANI 0→2 pass; MEMBER, REFILL, remaining SIRES local branches, STOIC-DATA, timed_pzone_reversal.

## Not done

- No git commit. P3/P5/P7 still out of scope. TBR quadrant entries (f5) remain a missing-stage assignment. C6 is D1, already in round 1. P15-13 still owns Saint arrival/alignment/profile stages.

## Round 4 decisions (C3 stop excursion, C1 Judas entry window)

- **C3 stop / sweep extremes.** After the confirming five-minute bar is found, high/low/stop/sweep_high/sweep_low are taken from `m.bars(trigger['start'], confirmation_end)` — the whole 1-minute excursion through that bar. `cash_open_reclaim_case` target uses the same recomputed low. `confirm_bar_offset` 0 keeps `confirmation_end == sweep_candle_end`, so first-candle episodes are unchanged. `details['excursion_bars'] = confirm_bar_offset + 1`. P4 empty-path still does not search later bars and still leaves high/low/stop None.
- **C1 judas_reversal entry window.** TBR p.8 places the reversal trade in 09:40–09:50. `entry_in_reversal_window = (m.at('09:40') <= decision_at < m.at('09:50'))`. Sweep search and `source_time_window` (09:30–09:50) are unchanged. Do not defer or reprice: decision_at, entry, and stop stay the O056 confirmation.
- **bind() rejected the operand.** `entry_in_reversal_window` is not an M01 field (`unknown historical operand JJ-TBR:entry_in_reversal_window`). Recorded the boolean on `values` and on a `reversal_entry_window` stage (`bind_rejected_unknown_operand`, `bind_rejected_operand`). When False, evaluate() is left as-is (operands stay truthful) and the episode is failed after `finish()` with `research_verdict=fail` and reason `entry_outside_reversal_window` appended to `failed`. That is the existing episode fail shape, not a new Kleene layer.
- **09:38 vs 09:39.** A 09:33 sweep's O056 C3 on the 180s grid ends at 09:39; the last minute inside that bar is 09:38. The test uses decision_at 09:39, which is still `< 09:40`. Control uses a 09:36 sweep so C3 ends at 09:42.
- **Frozen scan_jumbo cannot pass a 09:33 sweep** (N=0, C1 round 2). The new test shows pre-window repaired conjuncts pass and the round-4 gate fails. Control repaired pass.
- **Preview.** Only GB-FAIL and JJ-TBR rows are refreshed (`run_preview.py --only GB-FAIL JJ-TBR --merge`). Other family rows stay round 3.

## Round 4 commands

```
cd implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider -q tests/rule_discovery/test_baseline_repairs.py --tb=short
# 22 passed in 22.20s, exit 0
```

```
cd implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python \
  /workspace/.worktrees/baseline-repair/planning/research-program/reviews/phase1-code-review-2026-09-14/repair-preview/run_preview.py \
  --only GB-FAIL JJ-TBR --merge
# 40/40 dates ok, orchestrator_wall_s 175.8216, exit 0
```

## Preview result (round 4, not a receipt)

Only GB-FAIL and JJ-TBR rows were refreshed. Other families remain round 3.

- **C3 GB-FAIL.** 188 episodes had `confirm_bar_offset > 0`; 123 of those changed stop vs the first-candle extreme. Verdict counts unchanged except `cash_open_reclaim_case` 17→18 pass (14→15 fail→pass): a later reclaim whose first-candle stop sat inside the excursion now has `risk_defined`. asia_tdo 13, nyam_box 50, previous_hour 198, prior_day 31, prior_month 4, prior_week 14, mss_fvg 2 pass unchanged.
- **C1 judas_reversal.** 37 B0.1 episodes; 31 fail `entry_outside_reversal_window`. Pass 5→2 (the three early O056 completions leave the pass set). fail 32→35. `verdict_changed` vs B0 stays 0 because most C1 extra episodes do not share B0 candidate ids. `no_setup` stays 32: the window fail is applied after `finish()`, so reconstruct `strategy_assessment` is not rewritten.
- **Other JJ-TBR** episode/pass/fail counts unchanged vs round 3 (C2 10:00 window already in). Wall seconds on those rows are the round-4 subset rerun.

## Not done (round 4)

- No git commit. P3/P5/P7 still out of scope. TBR quadrant entries (f5) remain a missing-stage assignment. `entry_in_reversal_window` was not added to FORMULAS/M01 (frozen pack). Strategy_assessment for the 3 Judas research-fail/setup rows was not rewritten.

## Round 5 decisions (deferred Judas entry, post-finish strategy status)

- **Deferred variant is a labelled entry-timing sibling of `judas_reversal`, not a new M01 CASE.** FORMULAS has no `judas_reversal_deferred` branch. `HistoricalEpisode` evaluates the `judas_reversal` CASE (`values['branch']` stays `judas_reversal`); after `finish()` the episode is relabelled `judas_reversal_deferred` and `candidate_id` is recomputed from that identity. Window-result `branch` and coverage id are `judas_reversal_deferred`.
- **`scan_jumbo_repaired(m, 'judas_reversal')` produces both episode sets.** Strict episodes stay in `episodes`; deferred go to `deferred_variant`. Direct callers of the strict branch keep the same `N_observed`. `scan_jumbo_repaired(m, 'judas_reversal_deferred')` returns only the deferred set. `scan_branch_repaired` returns each under its coverage id with `baseline_version=B0.1-2026-09-14`.
- **REPAIRS.** `judas_reversal_deferred` is added to C1 `branch_ids` and `JJ_TBR_REPAIRED_BRANCHES`. No new REPAIRS key: `test_repairs_registry_covers_named_defects` still expects the round-2/4 key set. Frozen coverage.json has no deferred row; `run_preview.py` clones the `judas_reversal` manifest row.
- **Swept edge is the 6-9 formation edge**, not the wick extreme. Long: close `>` formation low. Short: close `<` formation high. Remaining beyond the wick but still outside the range is not a held reclaim. Search is 1-minute complete bars in `[09:40, 09:50)` via `m.bars(09:40, 09:50)`. First bar that is complete *and* on the reversal side; a 09:40 miss can still enter at 09:41. No such bar fails with `reclaim_not_held_at_window` after `finish()`. Confirmations already in 09:40–09:50 are not repriced.
- **Stop and objective (target) stay the O056/strict values.** Entry and `decision_at` become that bar's close and `known_at`. `risk_defined` / `objective_fixed` recompute from the new entry. `confirm_at` stays the O056 known_at.
- **Post-finish fail is generic.** `_fail_after_finish(episode, reason)` sets `research_verdict=fail`, appends the reason, and `_sync_strategy_status` maps pass/fail/unknown → setup/no_setup/data_unavailable (or condition_present/absent for non-entry_setup). Used for `entry_outside_reversal_window` and `reclaim_not_held_at_window`. Not per-reason copies.
- **Preview B0 for the deferred row is native `judas_reversal`.** Accepted B0 has no deferred branch; `scan_branch` would KeyError. The deferred B0.1 row sits beside that B0. Candidate ids differ (branch in identity), so `verdict_changed` vs B0 is not the comparison to read; pass/fail/no_setup columns are.
- **Merge.** Only JJ-TBR rows (including the new deferred row) are refreshed. Round-4 GB-FAIL diagnostics stay. Note line: only JJ-TBR rows were refreshed in round five.

## Round 5 commands

```
cd implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest -p no:cacheprovider -q tests/rule_discovery/test_baseline_repairs.py --tb=short
# 25 passed in 26.66s, exit 0
```

```
cd implementation
PYTHONPATH=src /workspace/implementation/.venv/bin/python \
  /workspace/.worktrees/baseline-repair/planning/research-program/reviews/phase1-code-review-2026-09-14/repair-preview/run_preview.py \
  --only JJ-TBR --merge
# 40/40 dates ok, orchestrator_wall_s 66.0647, exit 0
```

## Preview result (round 5, not a receipt)

Only JJ-TBR rows were refreshed, including the new `judas_reversal_deferred` row. Other families remain round 3/4.

- **C1 judas_reversal (strict).** Still 37 B0.1 episodes, 2 pass, 35 fail, 31 `entry_outside_reversal_window`. `no_setup` 32→35, equal to fail. The three post-finish window fails now rewrite strategy status.
- **C1 judas_reversal_deferred.** 37 episodes (same sweep population). pass 5, fail 32, no_setup 32. Of the 37: 5 pass, 13 fail `reclaim_not_held_at_window`, 19 fail for other reasons, 0 unknown. The 5 passes are the 2 in-window strict passes plus the 3 early O056 completions whose reclaim still held at 09:40.
- **Other JJ-TBR** episode/pass/fail/no_setup unchanged vs round 4.

## Not done (round 5)

- No git commit. P3/P5/P7 still out of scope. TBR quadrant entries (f5) remain a missing-stage assignment. `entry_in_reversal_window` and `judas_reversal_deferred` were not added to FORMULAS/M01 (frozen pack); deferred episodes evaluate the `judas_reversal` CASE and are relabelled after `finish()`.

