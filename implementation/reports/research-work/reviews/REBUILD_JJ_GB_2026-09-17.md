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

## 6. Open questions

Parameters the sources do not state, and readings only the user or a new source
can settle. None of them was chosen to make a number come out.

1. **The Green Bird fail window.** `FAIL_WINDOW_BARS = 12` (60 minutes) bounds
   the gap between a sweep and its failing five-minute close. The source states
   no window. The bound is four times the longest sweep-to-entry gap on the
   tickets (15 minutes on 2026-09-15, 2026-08-27 and 2026-04-23), chosen so no
   ticket is excluded while a level that "fails" hours later is not counted.
2. **Sweep cycles per level.** `MAX_CYCLES_PER_LEVEL = 6`. The author re-trades
   a level inside one session (2026-08-27 traded the 09:00-10:00 box high on a
   later excursion at 13:00) but never says how often. Six is our bound; the
   population is reported per cycle so a different bound can be read off it.
3. **"Hold".** `CONTINUATION_HOLD_BARS = 2`. "Break out and hold" is not
   quantified anywhere in the archive.
4. **The stop buffer.** `SWEEP_STOP_BUFFER = 2` points beyond the sweep wick.
   The source says "beyond the wick" and the tickets bracket it: 2026-09-03
   stops exactly on the sweep extreme, 2026-08-31 stops 22 points past it,
   2026-09-15 and 2026-08-27 stop *inside* the wick above the retest high.
5. **The big-range threshold.** `BIG_RANGE_MIN_PCT = 0.8%` for "same framework
   when having a big 6-9 range > long/short the EQ". The author never gives a
   number; the bin boundary is his.
6. **The trend switch.** `DOUBLE_BREAK_MAX_PCT = 1.2%` is read off the author's
   own 3,249-day table as the first bin where a single break leads by modal
   category. He states the table, not the switch.
7. **PWH/PWL as an entry reference.** The audit calls it "unverifiable as an
   entry" (2.2) yet `GB-2025-11-19` prints a previous-week-low sweep, reclaim
   and long at 24,625 with the PDH as the objective. It is kept as both a
   reference and an objective rung. Which reading does the user want?
8. **The mirrored session entries** (audit 2.5). We enumerate both edges of
   every session box on both sides; no dated chart shows an Asia-low long or a
   London-high short as the entry.
9. **PDH/PDL scope.** The previous CME session (18:00-16:00) reproduces the
   printed PDL on 2026-09-01 (ours 29,273.50 against his 29,270) where the
   RTH-only scope does not (29,355). PWH/PWL stay RTH-only: the shared
   prior-period loader supplies only RTH windows, recorded as
   `full_session_scope_unmeasured`.
10. **Unsupported inputs.** EVRange and the P-zone generator remain proprietary.
    `JJ-2026-09-01`'s narrated entry is at the EVRange lower line and
    `JJ-2026-01-02` / `JJ-2026-01-09` are P-zone entries; only the six printed
    P-zone dates and two EVRange readouts exist as fixtures.
11. **SessionStat.** Computed (J13) but off by default in the scattered-date
    replay, where sixty cached-window reads per session buy nothing: the
    envelope only ever decorates an operand and never gates an entry. It is on
    in the population run when `--sessionstat` is passed.
12. **The 09:00-09:30 half box (G13)** is dropped. `GB-2026-04-28`'s two
    narrated fills sit at 09:30 and 09:45 inside the still-forming 09:00-10:00
    box, which the author's own "I wait until after 10AM" excludes. Keep it
    dropped, or admit it as an unverified variant?
13. **Population density.** Even after the corrections the branch population is
    one to two orders above the author's trade count; the selection layer is
    what brings it to the authors' one-to-three entries a session. Whether
    Phase 1.5 scores the branch population or the selected trade list is the
    coordinator's call, and it changes what "faithful" means downstream.
14. **`tools/produce_p15_16a.py`** maps fidelity rule ids and test names
    (`RR-11`, `RR-13`, `F06-A*`,
    `test_rr11_september_uses_asia_0000_and_london_0200_0500`) that this
    rebuild renamed or retired. It produces the closed P15-16A bundle, so it is
    untouched here; it must be re-pointed when the restructured plan binds a
    new task card.

## 7. Reproducing this

```
git -C /workspace worktree add /workspace/.worktrees/fidelity-jj-gb fidelity/jj-gb
cd /workspace/.worktrees/fidelity-jj-gb
PYTHONPATH=implementation/src /workspace/implementation/.venv/bin/python \
  implementation/tools/replay_jj_gb.py --out <run-root> --charts
PYTHONPATH=implementation/src /workspace/implementation/.venv/bin/python \
  implementation/tools/run_jj_gb_population.py --out <run-root> --workers 12
PYTHONPATH=src /workspace/implementation/.venv/bin/python -m pytest \
  tests/rule_discovery/ tests/contracts/ -q      # from implementation/
```

## 8. The coordinator's guidance of 2026-09-17, rule by rule

The misses after the first rebuild were read as six rules per family. Each was
fixed for every day and the replay re-run.

| rule | what changed in the code | replay after it |
| --- | --- | --- |
| baseline | the rebuild before the guidance | strict 4 / ticket-risk 14 / 3-bar 17, of 40 |
| J-A | the exhaustion projections +/-0.33, +/-0.5 and +/-0.66 are entry locations in their own right (`_scan_judas_reversal`, jumbo.py), and every signature emits both fills -- the limit at the level and the market fill at the signature's close (`_fill_modes`) | (with J-B..J-G) |
| J-B | the two-minute signature is searched first and the slower clocks are alternative fills of the same opportunity (`confirm_pack`) | (with J-A..J-G) |
| J-C | the plays are observed, not switched: every play runs every day, the classification chooses the primary, and the single-break side follows the break the session shows (`session_read`, `break_state`, `_context_sides`) | (with J-A..J-G) |
| J-D | the box edge is an entry location on the first rejection printed there, without waiting for a sweep and reclaim | (with J-A..J-G) |
| J-E | the outbound trade enters on the first pullback to a box internal after the opening break (`_scan_judas_outbound`) | (with J-A..J-G) |
| J-F | London reads the Asia, midnight, overnight and prior-RTH levels from 02:00, and the 02:00-03:00 box once frozen (`drawn_levels`, `_scan_other_session`) | (with J-A..J-G) |
| J-G | the P-zone fill is the limit inside the printed zone (`_scan_pzone`) | (with J-A..J-G) |
| **J-A..J-G together** | | **strict 7 / ticket-risk 17 / 3-bar 21** |
| G-A | after the confirming close the fill is the retest of the level, searched for four hours; the close is the fallback fill (`at_level_fill`) | (with G-B..G-G) |
| G-B | a cycle ends with the five-minute failure, not a one-minute poke while price is still making new extremes (`failure_close`) | (with G-A..G-G) |
| G-C | the open reaction is traded at the swept pre-open reference -- the 09:00-09:30, 06:00-09:30 and overnight extremes -- not at the open print (`_scan_cash_open`) | (with G-A..G-G) |
| G-D | a session's running extreme is a reference an hour after it opens, superseded by the frozen box at its close (`session_references`) | (with G-A..G-G) |
| G-E | the previous hour is the trailing sixty-minute swing, re-cut every fifteen minutes, beside the completed clock boxes (`_scan_previous_hour`) | (with G-A..G-G) |
| G-F | the previous session's NY boxes stay live overnight (`_prior_session_box`) | (with G-A..G-G) |
| G-G | an overnight sweep is re-entered at the same level after the open, as a second fill of the same opportunity (`post_open_retest`) | (with G-A..G-G) |

Two further defects surfaced while fixing these and are fixed with them: a level
is contacted every time it is tested, not only the first time (`level_contacts`,
up to three distinct tests, which is what admits the 2025-10-07 London quadrant
at 04:30); and "fail back inside the range" is the test only when the level is
the reference's own edge on that side -- the close the author waits for at the
far edge, "the 5 min close back below the PDL after sweeping above it", is
*outside* the prior day's range, and testing for containment there suppressed
the whole prior-day short family.

## 4. Replay (entries only)

`implementation/reports/research-work/reviews/REPLAY_JJ_GB.md` and `.json`;
charts in `replay-charts/` with `INDEX.md` mapping each PNG to the author's
source page.

| stage | strict (+/-5 pts) | ticket-risk | within three bars | of |
| --- | --- | --- | --- | --- |
| first rebuild | 4 | 14 | 17 | 40 |
| after J-A..J-G | 7 | 17 | 21 | 40 |
| after G-A..G-G and the two defects they surfaced | 7 | 18 | 22 | 40 |
| after the coordinator's round 2 (R1-R4, the examples corrections and the rule fixes) | **17** | **26** | **27** | **40** |

Nine further proper entries (2026-09-08, 09-11, 09-14, 09-15) are outside the
tape, which ends 2026-09-03, and are carried as printed reference cases.

The play our scanner chose is the author's play on **37 of the 40** inside-tape
entries; the three without an episode at all are `JJ-2026-07-16`,
`JJ-2026-07-27` and the second `GB-2026-04-28` fill.

Detected at strict tolerance: `JJ-2025-01-28` (0.25), `JJ-2025-05-23-LONDON`
(1.25), `JJ-2025-11-10` (2.85), `JJ-2025-11-18` (3.76), `JJ-2025-12-30` (1.25),
`JJ-2026-01-09` (4.25), `JJ-2026-02-24` (0.00).

### Misses, with the stated reason

| example | our entry vs the printed fill | why |
| --- | --- | --- |
| `JJ-2025-09-09`, `JJ-2025-10-06`, `JJ-2026-06-05`, `JJ-2026-01-02`, `GB-2026-09-03` | 0.0-38.5 points, 2.2-3.6 bars late | the printed time is a chart read, not a ticket stamp; the price is inside the ticket's risk on four of the five |
| `JJ-2026-07-06` | 53.75 points | the author's 30,065 is the upper extension band and the branch that owns that band is `extension_reaction`, which is not the play of this example; the `judas_reversal` projection closest to it is 53.75 away |
| `JJ-2026-09-01` | 48.0 points | the narrated entry is at the **EVRange lower line**, a proprietary input we do not own (audit 1.2) |
| `JJ-2026-07-10` | 10.25 points, 21 bars early | the author's 11:05 long is at the R-Lo / pRTHVAL test; ours fires on the first test of the same level at 09:20 |
| `JJ-2026-07-16`, `JJ-2026-07-27` | no episode | the narrated entries are at the EQ on the opening drive; the signature our confirmation requires is not printed at those levels inside the window |
| `GB-2026-07-13` | 21.0 points, 273 bars early | our PDL failure fires at 19:25, his fill is at 20:40 on a later test of the same level |
| `GB-2026-08-11-12` | our 20:15 fill at the previous session's 09:00-10:00 box low is 4 points from his 29,635.75, but the printed 20:40 is 5 bars later; the row shown is a different reference |
| `GB-2026-08-13` | 34.75 points | the reference is a double top made **inside** the current hour; it is neither a completed clock box nor the trailing-hour cut at his entry time |
| `GB-2026-08-27` 13:00 | 18.75 points, 4.4 bars early | he sold 29,642.25, twenty-two points **above** his own 29,620 reference and thirty-three below the 29,675 extreme, before any close back through the level -- a discretionary fill inside the sweep zone |
| `GB-2026-08-31` | 45.25 points | his reference is the opening spike's own extreme on a still-painting box (the audit's G13 finding); at 09:33 it is not a frozen reference |
| `GB-2026-04-28` | no fill price printed; the two narrated fills sit at 09:30 and 09:45 inside the still-forming 09:00-10:00 box, which the author's own "I wait until after 10AM" excludes |
| `GB-2026-07-29-30` | no episode | the 23:20 pocket short is measured from an impulse that ends after our overnight leg window; the 04:00 London long is at the running London low, taken before our running reference goes live |
| `GB-2025-11-19` | 1.0 point, 5.8 bars early | our post-open re-entry fires at 09:31, his at 10:00 |

## 5. Population and plausibility

Measured before scaling, on the twenty-session representative slice
(2025-01, 2025-10, 2026-04, 2026-08, five sessions each; the slice includes
2025-01-01, a day with no session, as the negative control):

* 20 sessions in 37.3 s wall on 6 workers, 8.4 s per session per worker
  (11 s of that is the market load), worker peak RSS 1.90 GB. Against the
  container's 17.85 cores and 77.3 GB (cgroup v1, `cpu.cfs_quota_us`
  1,785,000 / `cpu.cfs_period_us` 100,000 and `memory.limit_in_bytes`
  82,999,996,416), twelve workers is 23 GB and inside the CPU budget.
* causality violations across the slice: **0**.
* negative control 2025-01-01: the Jumbo read is `unknown` with only the London
  play enabled and no pass; Green Bird records `reference_window_unavailable`
  for every box, zero episodes, zero passes. Positive control 2026-08-28: 8
  Jumbo passes, 151 Green Bird passes, 3 selected trades.
* selected trade list on the slice: **JJ-TBR 1.60 entries a session,
  GB-FAIL 2.05, GB-SCALP 0.80, GB-VWAP 0.25** against the authors' one to
  three a day. Stop distances GB-FAIL median 20.75 points (the tickets are
  17.25-48.25, median about 27) and R:R at target median 9.1 (the tickets print
  3.99-11.09).

The full-history run over the same 1,742-session list was still in flight when
this report was written (`run_jj_gb_population.py --workers 10`, 900 of 1,742
complete at 679 s, about 22 minutes end to end). The slice above is the
measured basis for it; the completed run's `POPULATION.json` / `.md` and the
gzipped per-episode rows are the outstanding artifact.

### The plausibility gate fails, and that is the finding

`tests/rule_discovery/test_p15_16a_plausibility_jumbo.py` now scans the session
market (B0.3 reads the session window itself, so the replay view it used before
produced nothing) and reports, over its fifteen-date slice:

| branch | episodes/session | pass rate | bound in `families/jumbo.json` |
| --- | --- | --- | --- |
| judas_reversal | 73.9 | 0.485 | eps [0, 4] |
| other_session | 51.0 | 0.448 | eps [0, 12] |
| internal_rotation | 27.6 | 0.396 | eps [0, 8] |
| single_extended | 10.9 | 0.129 | eps [0, 6] |
| single_purged | 7.1 | 0.349 | eps [0, 6] |
| judas_outbound | 4.9 | 0.000 | eps [0, 2] |

The bounds are **not** widened. They were cut for the old B0.2 enumeration, and
the rebuilt scanner enumerates a much larger branch population: every drawn
level, on both sides, on up to three tests each, with two fills per signature.
The author's frequency is recovered by the selection layer (1.6 and 2.05 entries
a session above), not by the branch population. The coordinator has to choose
which object Phase 1.5 scores -- the branch population, in which case the
enumeration has to be narrowed and these bounds are the target, or the selected
trade list, in which case the bounds must be re-cut against it. Either way the
gate is a live blocker on the old reading and is reported as one.

## 9. Coordinator round 2 (2026-09-17)

Applied in the order the coordinator gave, matcher first.

| rule | change | file |
| --- | --- | --- |
| R1 | every fill of the matched opportunity is tested and the matched fill's mode is printed (`fills_tested`, `matched_fill`) | `match_entry` in both adapters |
| R2 | the time window follows the evidence: `marked_by: rr_tool` keeps one five-minute bar, `marked_by: narration` gets three | `match_entry` |
| R3 | a printed price of `None` matches on play, side and time alone | `match_entry` |
| R4 | the Jumbo band ladder is emitted at every rung the sweep reaches and any rung can match | `_scan_judas_reversal` |
| examples | 2025-11-19 entry 09:35; 2026-08-13 entry 11:30 at the trailing-hour equal highs; 2026-07-16 is the EQ rejection on the single-break read; 2026-07-29 short prints 22:20 on our tape | `AUTHOR_EXAMPLES_2026-09-17.json` |
| G-A | the retest fill searches from the five-minute close as well as the one-minute read | `at_level_fill` |
| G-D | the running session extreme is re-cut every fifteen minutes until the box closes | `session_references` |
| G-E | the trailing sixty-minute swing is re-cut every five minutes | `_scan_previous_hour` |
| G-8 | the pocket leg's origin is searched back through the prior RTH session | `_impulse_leg` |
| cash open | the fade fills at the open of the bar after the one-minute rejection candle | `_rejection_fill`, wired into the fail branches too |
| J-A | the London box carries its 0.33 / 0.5 / 0.66 band rungs | `_scan_other_session` |
| J-B | the rejection candle's own close is a fill of the same signature | `_rejection_block`, `_three_candle_ob`, `_fill_modes` |
| J-C | the observed break is context on the single-break play, and the EQ / quadrant play reads six contacts through its window | `_scan_eq_branch` |
| J-G | a printed P-zone is a resting limit filled on the touch | `_scan_pzone` |

**Result: strict 7 -> 17, ticket-risk 18 -> 26, three-bar 22 -> 27, of 40.**

Newly matched at strict tolerance, with the fill that matched:
`GB-2025-11-19` 1.0 pt (post-open retest), `JJ-2025-09-09` 3.75 (orderblock),
`JJ-2025-10-03` 2.95 (signature close), `JJ-2025-10-06` 2.25 and
`JJ-2025-10-07` 2.0 (rejection block), `JJ-2025-10-13` 09:05 1.5 (signature
close), `JJ-2026-01-02` 0.0 (rejection close), `JJ-2026-07-06` 3.65
(absorption), `JJ-2026-08-28` 1.25 (at level), `JJ-2026-09-01` 3.29 (at level --
the EVRange line is reached through the drawn-level set after all).

Still open after round 2, each with its measured distance:

| example | ours | delta | bars | the rule that is still short |
| --- | --- | --- | --- | --- |
| `GB-2026-09-03` 00:45 | 29,227.75 | 10.5 | 3.0 | G-A: the TDO retest at 00:40-00:45 is still not the chosen fill |
| `GB-2026-08-27` 13:00 | 29,623.50 | 18.75 | 4.4 | G-E: the trailing swing high the spike takes is still not cut at 12:55 |
| `GB-2026-08-13` 11:30 | 30,192.75 | 34.75 | 12.4 | G-E: same |
| `GB-2026-08-31` 09:33 | 29,465.25 | 45.25 | 0.4 | the rejection-candle fill is not firing on the spike |
| `GB-2026-08-11-12` 20:40 | 29,887.25 | 251.5 | 449 | G-F: the previous session's 09:00-10:00 low is not the chosen reference that evening |
| `GB-2026-07-13` 20:40 | 29,393.25 | 21.0 | 273 | G-A: the later retest of the PDL is not the chosen fill |
| `GB-2026-07-29` 22:20 | 27,600.00 | 44.5 | 274 | the pocket leg still measures from the wrong origin |
| `GB-2026-07-30` 04:00 | none | - | - | G-D: the running London low at 27,360 is still not a reference |
| `GB-2026-04-28` | none / 14 bars | - | - | the 09:00-10:00 box before 10:00 (G13 stands) |
| `JJ-2026-06-05` 03:20 | 30,098.50 | 32.0 | 0.8 | J-A: the London -0.5 rung is not the chosen level |
| `JJ-2026-07-10` 11:05 | 29,837.75 | 28.75 | 0.6 | J-C: the 11:05 q25 contact is close but not the chosen one |
| `JJ-2026-07-16` 09:35 | 29,384.75 | 66.75 | 1.0 | the EQ rejection short is not the chosen episode |
| `JJ-2026-07-27` 09:35 | none | - | - | open question (the coordinator's own note) |
