# P15-16A repair, Green Bird track

Exit predicate. STAGE_AUDIT files exist with measured stages. `scan_b02` enumerates from the market. Confirmation and trigger write market operands that can fail. Family JSON has plausibility blocks. `test_p15_16a_plausibility_greenbird.py` and `test_p15_16a_greenbird.py` are green. Replay reports location reach. B0/B0.1 hashes match the start capture. No git, no receipts, no wiki edits.

## Decisions

F07 versus "one or two A+". F07 forbids a scanner cap. GB p.30 prints "One setup. One strike. Maximum conviction." GB p.31 prints one long and one short on the same session. That is a plausibility bound on measured A+ passes across boxes, not a filter. The scan still emits every box independently.

At-level confirmation. The full-history pass flood (nyam_box 6308, previous_hour 6522) came from `sweep_and_at_level` accepting a later 30-minute touch of the edge and `_finish_level_trade` writing `{mode: "at_level"}`. RR-13 and GB p.58 enter two minutes after the spike. GB p.3 is fail back inside the box. The fail window is now the sweep's 5-minute clock bar plus the next one (`AT_LEVEL_FAIL_BARS=2`, OD). Confirmation operands are `confirm_close`, `inside_box`, `fail_to_continue`, `sweep_depth`.

Trigger. `{sweep: true}` is replaced by `sweep_depth` and `sweep_at_ns`. Any print through the edge remains a sweep. The source never publishes a minimum overshoot (GB p.3 "briefly trades beyond").

cash_open_reclaim_case. Full-history B0.2 had 0 passes versus B0.1 721. The killing stage is objective. `_scan_cash_open` reused the box helper on `low=high=open`, so `target==entry` and `objective_fixed` was false on 1535 dates. That is not the source. GB p.3 / p.40 is "9:30am manipulation below, reclaim, enter for longs targeting retracement into discount, stops at lows." Confirmation duration is unpublished. B0.2 now uses an OD 5-minute reclaim close and the B0/B0.1 retracement formula `open + 0.5*(open - sweep_low)`, labelled OD because the discount parent is unpublished. Wiki/dossier warning that a half-distance target is not printed is recorded here; restoring the B0.1 formula is the measured repair, not a new invention.

VWAP 150 versus 100. GB p.33 caption "One 150-point beauty" plus "30-point stop." GB p.34 reply "30 point stop, 100 point win." SD04 keeps both. The repair prompt takes 150 as the baseline objective, 100 as the OD variant. Neither is an entry condition. Stop stays 30 points OD. Confirmation writes `vwap`, `retest_low`, `retest_high`, `asia_high`, `london_high`, `breakout_close`. Missing retest to RTH close stays fail (F13).

Scalps. F06 A4 is a continuation long. Overnight down-leg pocket stays on GB-FAIL `golden_pocket`. GB-SCALP `golden_pocket_continuation` is up-impulse only, impulse complete before 09:30, NY pullback after 09:30, 5-minute close out of the pocket (OD), near-edge stop. A pullback bar that closes through the far 61.8% edge fails continuation. That is why 1388/1742 was not a scalp rate.

NWOG. Monday destination (GB pp.13, 14, 36, 37). Using the gap edges as the sweep reference is an OD stand-in for the stacked-high recipe. Recorded in the audit.

Population path. `scan_b02` reads only `family`, `method_id`, `branch`, `coverage_id`, `registered_od`, `parameters`. Replay still matches author fills for divergence. Detection is the population scan on that date.

Untriggered rows. Box branches now emit a location/trigger fail when the edge is never swept, so the funnel is not 100% pass of emitted episodes.

B0/B0.1. Hashes taken after restoring `runner.py` identity imports (worktree drift: `directory_listing_digest` does not exist in `contracts/identity.py`, which this track must not edit).

## Source quotes used

- GB p.3. "9:30am manipulation below, reclaim, enter for longs targeting retracement into discount, stops at lows." "A+ — must include a sweep of the range. No sweep = not A+."
- GB p.19. "closed on the 5 minute below TDO."
- GB p.25. "I wait for the 5 min close back below the PDL after sweeping above it."
- GB p.30. "Perfect NYAM Execution. Well over 150 points short. One setup. One strike. Maximum conviction."
- GB p.31. Trade 1 long 250 points, Trade 2 short 140-150 points.
- GB p.33. "One 150-point beauty. Broke & closed above London + Asia highs → retraced into VWAP → long entry. 30-point stop."
- GB p.34. "30 point stop, 100 point win."
- GB p.37. "Breakout fails. Price falls back inside the range."
- GB p.58. 09:30-09:33 sweep of the 09:00-09:30 box high, short two minutes later.

## Author example 2026-07-13

Location miss. The tape example is an Asia-session long: sweep below PDL 29,385 to AS.L 29,340, buy 29,414.25 at 20:40 on the reclaim (GB p.48). F06 A2 baseline is Asia-high short only. The long mirror is a registered candidate, not B0.2. RR-11 July Asia box is 20:00-23:00. The example paints 20:00-21:00. `prior_day_level` uses the data-engine prior day, which did not match painted PDL 29,385 within 2.00. No rule was moved to make the fill pass.

## Shared files

`runner.py` only. Restored two hunks to match main so `common.py` can import. No `common.py` or `confirmation.py` edits.

## Verification-fix round (driver failures + 2026-09-15 source)

Gate sensitivity. `_diagnose()` is deleted. An out-of-bound branch fails unless `plausibility.<branch>.observed_rate_justification` is a human `{page, text}` quoting a page that supports the observed rate. `test_mutated_asia_box_bound_fails_the_gate` copies the family JSON, sets `asia_box.pass_rate` to `[0,0]`, and asserts the gate would fail.

At-level window. `AT_LEVEL_FAIL_BARS=1` (the sweep's 5-minute clock bar) plus the next 1-minute hold. A same-bar wick is not the fail. A later-bar new extreme aborts.

Density, measurement not bounds. nyam no longer scans 09:30-10:00 (subset of 09:00-10:00) or 10:00-11:00 as a third fail reference (grey developing hour on the Sep-2026 chart, context for the 10:05 9-10 retest). 09:00-09:30 is searched only until 10:00 (GB p.58), then the green 09:00-10:00 box until 11:30 (GB p.43 11:20). PM is the 12:45-13:00 short of the 09:00-10:00 highs (GB pp.45, 56), not 09:00-11:00 into 14:30. previous_hour is hours 13-14 only: 8-10 are named NYAM/pre-cash, 11-12 sit in the lunch gap and the PM 9-10 window. NWOG is Monday-only. VWAP retest must hold the breakout.

ny_session_extreme. Freeze the 09:30-11:00 NY range at 11:00; scan 11:00-16:00 at-level of those two edges. The 2026-09-15 NY marker is the 10:55 low, swept at 15:35. A later print that makes a new extreme is a break of the frozen level, not a new setup. Bound [0, 2] eps / [0, 0.20] pr; measured 2.00 / 0.167 on the 15 dates, 5 passes on 5/15 sessions.

Two stop placements. Retest higher-low minus a tick (2026-09-14) versus sweep extreme minus 11.75 (2026-09-15 direct reclaim after 09:30). Fixtures `test_retest_stop_is_not_sweep_buffer` and `test_direct_reclaim_stop_is_sweep_buffer_not_retest_low` each fail if the other formula is applied.

Ladder. RR-12 `author_spacing` is [8, 33].

Replay. After-tape returns `detected=None`, `divergence='date outside the tape'` before any market view. Every `detected=False` row names `failing_operand` (`window_or_branch_mismatch` when location passed on a window/branch mismatch). GB-2026-09-15 is copied from main into the worktree examples file and is data_unavailable.

Evidence. Round-1 `_track_greenbird/` five files restored to committed bytes. This round writes only under `_repair_greenbird/` or tmp_path.

Cache. After-tape replay does not call `event_cache.build_event_window` (monkeypatch test). Slice dates use `load_source_market` with the existing write guard. Concurrent sibling tracks may still write after-tape cache; this track's after-tape examples do not.
