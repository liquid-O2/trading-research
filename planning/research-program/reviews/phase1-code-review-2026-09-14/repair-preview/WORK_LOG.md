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
