# Source-faithful rebuild of the Jumbo and Green Bird scanners

Baseline label **B0.3-2026-09-17**. Branch `fidelity/jj-gb`, worktree
`/workspace/.worktrees/fidelity-jj-gb`. Built against
`implementation/reports/research-work/reviews/FIDELITY_AUDIT_2026-09-17.md`
sections 1 and 2. Where the audit and the old adapter disagreed the audit wins;
where the audit and the wiki method pages disagreed the audit wins. The previous
B0.2 scans stay reachable through git history and the pinned P15-16A receipts;
nothing else preserves them.

## 1. Defect by defect

### 1.1 Jumbo (JJ-TBR), audit 1.3

Paths are in `.../rule_discovery/source_adapters/jumbo.py` unless stated.

| id | the audit's correction | the code |
| --- | --- | --- |
| J1 | the objective is EQ, mislabelled `plus_0_5`; the ladder is EQ 92.8% -> range open 86.8% -> opposite edge 66.2% -> +/-0.5 -> the extension band | `objective_ladder` jumbo.py:1075 returns the author's five named rungs in his own order; `_scan_judas_reversal` jumbo.py:1301 takes the first rung beyond the level; `_scan_judas_outbound` jumbo.py:1422 targets the real `plus_0.5` / `minus_0.5` projection |
| J2 | confirmation from the sweep, at or after 09:00; 09:40-09:50 is an operand | `NY_ACTION = ("09:00","12:00")` jumbo.py:293, `MODAL_WINDOW` jumbo.py:295; the signature search starts at `max(sweep_end, 09:00)` in `_scan_judas_reversal` jumbo.py:1301 and `in_modal_window` sits on the trigger stage |
| J3 | the 15-minute opening-range mid and quadrants have no branch | `_eq_locations` jumbo.py:1659 adds `or15_mid`, `or15_q25`, `or15_q75` to the single-break case |
| J4 | the location set is every drawn liquidity level | `drawn_levels` jumbo.py:545: box edges, London and Asia H/L, D-1..D-3 H/L (`session_levels.prior_sessions`), ONH/ONL, pRTHVAH/pRTHVAL |
| J5 | classify the sweep depth; the rule fires in the exhaustion area | `depth_class` jumbo.py:1019, `exhaustion_hit` jumbo.py:1031: at or beyond the 0.33-0.66 band, at +/-0.5, or coincident with another drawn level; a shallow poke at a box edge fails `location` with `sweep_short_of_exhaustion_area` |
| J6 | record the context read as a stage | `session_read` jumbo.py:641 and `_context_stage` jumbo.py:1279; the read is on every episode and in the document as `day_read` |
| J7 | 2/3/5-minute orderblock or rejection block, not the 3-minute one alone | `confirm_pack` jumbo.py:915 runs 2m, 3m, 5m and the absorption candle |
| J8 | the London entry does not require a box-edge raid | `_scan_other_session` jumbo.py:1546 records `box_edge_swept` and never gates on it |
| J9 | compute the range size in percent and carry the five bins | `range_class` jumbo.py:510; the single-break branches are gated on it in `_scan_eq_branch` jumbo.py:1701 |
| J10 | single_purged admits both directions | `_context_sides` jumbo.py:1677 |
| J11 | the single_purged window is the AM, 09:40-09:50 is the add window | `_scan_eq_branch` jumbo.py:1701 (09:30-12:00, `in_add_window` operand) |
| J12 | the single_purged objective is the projection | `_scan_eq_branch` jumbo.py:1701 targets `plus_1.33` / `minus_1.33` |
| J13 | compute the SessionStat envelope | `sessionstat_envelope` jumbo.py:772 over `SESSIONSTAT_SAMPLE = 60` prior windows, with the 0.5 expansions and the minimum average |

### 1.2 Green Bird, audit 2.3

Paths are in `.../source_adapters/green_b02.py`.

| id | the audit's correction | the code |
| --- | --- | --- |
| G1 | one clock each, in every month | `ASIA_BOX` green_b02.py:119 (20:00-00:00), `LONDON_BOX` green_b02.py:120 (02:00-05:00); `asia_box_spec` / `london_box_spec` green_b02.py:145,150 take a date and ignore it; the month-split variant tables are deleted |
| G2 | the 10:00-11:00 box and the later hours are references; drop `ny_session_extreme` | `session_references` green_b02.py:461 builds asia, london, 09:00-10:00 (live 10:00), 10:00-11:00 (live 11:00), each completed hour 11-15, the previous session's NY boxes, the True Day Open, the prior day and the prior week; `B02_BRANCHES` green_b02.py:100 drops `ny_session_extreme` and `nwog` |
| G3 | references live until swept; no entry-window list | `in_entry_windows` is deleted; `sweep_cycles` green_b02.py:632 runs from each reference's `live_from` to the session end with `FAIL_WINDOW_BARS = 12` green_b02.py:87 |
| G4 | the cash-open objective is the retracement of the pre-open range | `_scan_cash_open` green_b02.py:1559: the pocket of the 06:00-09:30 range then its extreme, stop at the manipulation extreme, both directions, and the pre-open edges as levels beside the open print |
| G6 | stops beyond the sweep wick with a measured buffer, sized at $750 | `SWEEP_STOP_BUFFER = 2` green_b02.py:80, `derived_quantity` green_b02.py:155 |
| G7 | the NWOG is an objective, not an entry reference | `_nwog_levels` green_b02.py:400 feeds `objective_levels` green_b02.py:578 only |
| G8 | the pocket leg is the impulse that made the session extreme, both directions, stop beyond the zone | `_impulse_leg` green_b02.py:1648, `_pocket_for_leg` green_b02.py:1678, run on the overnight leg and the NY AM leg |
| G9 | add the break-and-hold continuation | `_scan_continuation` green_b02.py:1776, `CONTINUATION_HOLD_BARS = 2` green_b02.py:95 |
| G10 | the bias is recorded, never a filter | `directional_bias` green_b02.py:946 returns `rule: recorded_not_filtered`; `bias.filtered` is `False` on every document |
| G11 | a selection rule and entries per day beside the author's count | `trade_selection.select_session_trades` (trade_selection.py:85), wired at green_b02.py:2089 and jumbo.py:1854 |
| G12 | the ladder is about 25 points | `LADDER_SPACING = 25` green_b02.py:76 |
| G13 | drop the 09:00-09:30 half box | it is not in `session_references` green_b02.py:461 |

### 1.3 The day read (user instruction, 2026-09-17)

The scanner classifies the session before it scans and runs only the plays the
classification allows; branches whose play is not in the read are recorded as
`play_not_in_the_day_read` omissions. Both documents carry `day_read`, every
episode carries `values.play`, `values.is_primary_play` and `values.read_used`,
and the replay keys on the play: a play mismatch is a miss even when a price
coincides.

**Jumbo** (`session_read` jumbo.py:641). Inputs: the range size in percent and
its bin, the open location against the prior RTH value area and range, the
overnight purge state, and which Asia/London/midnight edges are still drawn.
Sister-index relative strength and the news calendar are not on the owned tape
and are listed in `unavailable_inputs` rather than approximated. Plays:
`double_break` (the 0.33/0.66 band, 0.5 and, after 10:00, the 1.33/1.66 band),
`single_break` (the range open, EQ, the quadrants and the 15-minute opening
range), `big_range_eq`, `london`, `pzone`. The Judas play is switched off only
on a decisive trend read -- the open outside prior value on the side the
overnight already purged **and** a range above the 1.2% bin, the only bin in
which the author's own 3,249-day table puts a single break ahead of a double
break. Below that the classification is a probability, not a switch: his
open-location table still gives "both sides" 27.3% with the open below both VAL
and PDL. The author reads the location twice, when the 06:00-09:00 box freezes
and again at the RTH open, and quotes the second ("open inside prior RTH value:
range scalps", 2026-07-10; "RTH open below the prior RTH value low",
2026-07-28); both reads are kept and an entry taken before 09:30 may only use
the 09:00 read (`play_not_readable_before_the_open`).

**Green Bird** (`session_read` green_b02.py:1180). The overnight names the
reference: a PDL/PDH sweep-and-reclaim puts the prior-day level in play and
sets the bias, an Asia-edge sweep puts the Asia box in play, and an open held
beyond both session boxes makes the NY session a pullback/continuation day
rather than a "ONE MODEL" sweep-and-fail day. `break_and_hold` and
`vwap_continuation` run only on a continuation day; `previous_hour_fail` runs
from 12:00 ("Optional: previous hour high/low if you are trading later hours");
`weekly_level` runs only when the weekly level is within reach of the overnight
range.

Both classifiers were checked against the play the author narrates: on all 23
dated sessions whose play is identifiable, the author's play is enabled
(23 of 23).

### 1.4 Causality (coordinator instruction, 2026-09-17)

`decision_at` is now the latest `at_ns` of every stage that admitted the
episode. `_episode` (green_b02.py:824, jumbo.py:1136) computes `evidence_at`,
records `confirmation_delay_ns`, and fails the episode with `causality` /
`entry_precedes_evidence` when the entry would be priced before the bar that
confirmed it. Four constructions were repaired to satisfy it rather than be
caught by it: the Judas trigger is the sweep (the reclaim is an operand of the
confirmation, which *is* the reclaim); the Judas and extension stops come from
the confirming orderblock or rejection block instead of a running sweep extreme
that can still be moving; the London drawn-level entries are stamped at the
level's own `known_at` instead of the 03:00 box close; and the Green Bird
one-minute failure mode carries its own trigger bar instead of the later
five-minute one. Tests: a positive over every episode of a session, and a
negative control asserting the named rejection reason, in both families.

## 2. Contracts kept

`scan_b02(market, rec) -> document` keeps `episodes` / `omissions` /
`baseline_version` and the `strategy_assessment.status` vocabulary that
`common.population_counts` and `common.episode_status` read; Jumbo also keeps
`populations["B0.2"]`. `replay_example(market, example) -> dict` keeps
`detected` / `reached_location` / `failing_stage` / `failing_operand` /
`branch` / `our_side` / `our_level` / `our_entry_ns` / `author_level` /
`author_side` / `divergence`, and adds `entries`, `play`, `expected_play`,
`day_read`, `other_fills`. `RULES` stays keyed by rule id with `kind`,
`source`, `finding` and `file_line`; `green_failure.RULES` and
`green_vwap_scalp.RULES` re-filter the new ids.

`common.py` was **not** edited. Two new shared modules sit under
`source_adapters/`: `trade_selection.py` (the per-session selection layer) and
`session_levels.py` (the previous sessions' full CME windows and the prior RTH
value area).

## 3. The entry rule and the replay tolerance

The replay matches ENTRIES only (user instruction). An example is detected when
**every** proper entry on it is reproduced on the author's play, on his side,
within one five-minute bar of the printed time, and within the stated price
tolerance. `proper_entry` and `marked_by` were added to
`planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-17.json`, a superset of the pinned
2026-09-15 file (every field of which is copied through unchanged, asserted by
`test_author_examples_2026_09_17_is_a_superset_of_the_pinned_file`).

**Tolerance.** Two columns are reported for every entry.

* `strict`: +/-5 points. This is the "within a few points" reading.
* `det`: the ticket's own printed risk, `|stop - entry|`, and 27 points (the
  median printed stop, audit 2.4) where the ticket prints no stop. The
  justification is measured: the author's own fills sit 0 to 34.5 points inside
  the level he names (2026-09-03 and 2025-11-20 exactly at it, 2026-08-27 6.25
  inside, 2026-09-15 11.5 inside, 2026-08-28 34.5 inside) while his stops are
  17.25 to 48.25 points. An entry within the trade's own risk, at the same
  reference and on the same side, is the same trade; beyond it the R profile
  changes materially.
* `3bar` is a diagnostic column only: the same price test with the time window
  widened to three five-minute bars, because several examples print a chart-read
  time rather than a ticket time. It never counts as a detection.

Green Bird emits the two confirmation modes the audit names -- the five-minute
close back through the level, and the limit at the level once the failure is
visible -- plus the same "fail back inside" trigger read on the one-minute
clock, which is how the tickets are filled inside the five-minute bar
(2026-08-28 prints at 10:05 inside the 10:00-10:05 bar). All three are
alternative fills of one opportunity; the selection layer and the opportunity
count treat them as one.
