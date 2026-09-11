# JJumboFX — SDRange / Time-Based Ranges framework

Operating method / JJ-TBR. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


**Why one method.** The manual calls false breakout/Judas and range breakout applications of the same time-based framework ([TBR] pp.6–12). The raw record says “same ranges, different layers” on 15 May 2026 and “same 6-9 framework, more refinement” when adding order flow on 23 February ([JR] pp.11, 14, posts 2055344660986364371 / 2026059018750378427). The later summary is the author's own ordered phrase: context, location, confirmation ([JR] p.33, post 2093335135789719861).

### Ordered loop and attachments

| Step | Source operation, in order | Existing attachment / missing work |
|---|---|---|
| 1. Choose the session and freeze its geometry | Select the range being traded. Main NY formation is 06:00–09:00 ET; draw H/L, width, EQ, quadrants, range open/close and projections. The manual also lists Asia 20:00–20:30, midnight 00:00–00:30, London 03:00–03:30, 09:30–10:00, 10:00–10:30, lunch 12:00–12:30 and 15:00–15:30. These are applications of the framework, not eight entry products. ([TBR] pp.4–7.) | `clocks.CLOCKS/clock_bounds`, `sessions.build_session/projections`, `family_clocks.build_clock_table` and range/path producers; [FORMULAS] P3-01/P3-06, R-J05/J09/J23. Basic frozen H/L geometry exists. A faithful source-selected clock, source range-open identity, and the newer inner-range geometry are only partial. |
| 2. Set expectations before the entry | Read overnight size and balance, liquidity already purged, open versus previous RTH value/range and today's box, news, and current behavior. Wide/extended overnight and range-bound news conditions reduce targets and risk; compressed/purged conditions can favor single-direction expansion. The raw July examples include continuation from outside value while still inside the prior price range: “outside both AND high RVOL” is a particular case, not the only permission to continue. ([TBR] pp.12, 16–24; [JR] pp.33–39, 48–49.) | `family_open.build_open_table`, `sessions.width_bin/_purged`, `family_levels.build_level_table/load_red_folder`, `formulas_jumbo.j21_class/j21_targets`; R-J03/J04/J05/J06/J07/J20/J21. Partial: purge chronology, event-time news, and contextual classification. Final single/double-break labels are outcomes. First-five-minute RVOL cannot inform a 09:30 decision. |
| 3. Choose a location and a destination within that case | Exhaustion beyond a swept edge, EQ/quadrants on internal entries, 1.33–1.66 after expansion, or a source-drawn P-zone/expected-range boundary. Preserve separate identities for 6–9 EQ, EV midpoint, SessionStat bands, P-zones, and RTH/profile references. Mark the remaining directional objective before acting. ([TBR] pp.8–24, 31–35; [JR] pp.3, 23–26, 48, 53–57.) | `sessions.projections`, `family_env.build_env_table`, `formulas_jumbo.band_133_166/j10_draw/j19_draw`; R-J01/J02/J08/J10/J11/J12/J13/J19 and P3-02. Geometry/approximation only for several rows. Exact EV, P-zone, and SessionStat minimum-average construction is missing. A time-stamped, source-scoped remaining-liquidity ledger is missing. |
| 4. Let the selected location produce the selected entry signature | The manual's favorite reversal entries use 2/3/5-minute orderblocks or rejection blocks; they are expressly personal entry choices, not fixed to the model. Later charts add absorption candles, BigTrades, footprint/profile behavior, and refinements at the same range levels. Use the confirmation actually present in that source episode. ([TBR] pp.27–31, 35; [JR] pp.14, 48, 50, 52, 67–69.) | `formulas_jumbo.j18_ob_bull/j18_ob_bear`, `family_gap`, `family_levels`, `family_tape._big_at`, `j15_bigtrade_at_level/j16_two_sided_at_eq/j17_node_under`; R-J14–J18. Partial. Current full-RTH profile/median inputs and London prints compared with a later 6–9 box do not establish a contemporaneous confirmation. |
| 5. Enter with the case's risk and target policy | Choose immediate, retracement, or stop-triggered execution and structural invalidation. The OB example distinguishes a midpoint stop/entry from a conservative boundary stop. Size and target ambition depend on the case. Do not turn a ticket's points or R:R into a universal preset. ([TBR] pp.24–29; [JR] pp.3, 54–57.) | `j18_ob_*` exposes block/mid/stop; `j21_targets` and `j24_management` relate to risk/targets; R-J18/J21/J24. Missing: source entry choice, actual entry timestamp, stop policy, partials and adds tied to that entry. |
| 6. Manage, recognize failure, and reassess | Take the appropriate internal/opposite/external objective, protect or compound justified winners, and reduce ambition in grind. Three failed reversal attempts at the same level, strong bodies/volume continuing through it, or absent rejection defeat a reversal idea. Exit and observe; if continuing after failure the manual says reduce allocation at least 50%. Reassess another case/session rather than relabel the failed fade as a successful breakout. ([TBR] pp.24, 36–37.) | `j22_three_strike/j22_failed/j24_management/j25_mid_retrace_hold`; R-J20–J25. Partial: three touch bars are not three distinct attempts; whole-window extrema are not post-entry excursions. The attempt/management ledger is missing. |

### Branches inside this loop

| Branch | Source sequence and objective | Boundary on interpretation |
|---|---|---|
| `judas_outbound` — Judas Trade #1 | At the 09:30 open, take the contextual move toward the selected exhaustion projection; close as the 09:40–09:50 reversal window arrives. ([TBR] pp.8–10.) | The direction and exact entry selection are not supplied by the later double-break label. This is an outbound leg, not the reversal entry. |
| `judas_reversal` — Judas Trade #2 | A completed range edge is swept; the exhaustion area produces a reversal signature, normally in the manual's 09:40–09:50 window; trade back through internal levels toward the opposite liquidity/projections. ([TBR] pp.8–11, 27–29.) | A mandatory exact ±0.5 touch is too narrow. Raw charts include shallow edge sweeps. Record depth; do not choose the deepest eventual excursion retrospectively. |
| `single_extended` | Extended overnight: wait for an EQ/quadrant entry in the allowed direction, usually take the range edge, moderate risk and expansion expectations. ([TBR] pp.12–14, 24.) | The eventual “single break” cannot be an entry-time input. “Extended” has no author-exact universal width ratio. |
| `single_purged` | Overnight stop hunts have already removed the relevant liquidity; the contracted range supports expansion from EQ/quadrants. 09:40–09:50 can be a continuation/add window, not a compulsory reversal. ([TBR] pp.12–15.) | Preserve the actual overnight references and when they were taken. Containment of two completed boxes is not a purge-time ledger. |
| `internal_rotation` | In the appropriate wide/in-value context, take confirmed rotations at EQ/expected-range locations, with nearer objectives. The 2 September raw example explicitly trades EQ both ways on a big 6–9 range and includes two losing attempts. ([JR] p.3, post 2095172969035096454; pp.38–43.) | EQ is a location; the author does not publish “touch EQ = reverse.” EV and EQ are different targets. |
| `extension_reaction` | After range expansion reaches the 1.33–1.66 area, examine rejection/continuation and the still-owed objective. The September 9 example combines session-average lows, that extension area, and equal highs as the long's destination. ([TBR] pp.20–21; [JR] pp.23–26, 57, 71.) | Extension touch, HOD/LOD in the band, and a confirmed reversal are different observations. Each projection uses its actual parent range width. |
| `other_session` | Apply the selected geometry and signatures to the observed London or later-session case. AM consolidation can precede PM expansion; AM expansion can precede PM consolidation. ([TBR] pp.7, 36; [JR] pp.46, 50–51, 63–66.) | Modern London charts freeze a box before the marked action; the retained 00:00–03:00 assumption is not a verified universal author clock. A source-known clock is required. “London is cleaner this cycle” does not publish a rolling-ten-day selector. |
| `timed_pzone_reversal` | Use the actual time-anchored P-zone and observed reversal sequence. The January 2 post's “low > range open” describes a path from the low to the range-open line; the December 17 post's “10 am p-zone > london low” names another path. ([JR] pp.53–55.) | The arrow is not an inequality. A 09:00 zone anchor is not proof of a 09:00 fill. Later time-specific examples must not be forced into the manual's 09:40 window. |

**PD RTH Range+ is a context/destination application.** It uses prior 09:30–16:00 highs/lows and M15/H1 imbalances, waits for current RTH direction, then trades toward those objectives with the range framework. In this expressly RTH-only view, an ETH sweep does not consume the RTH objective ([TBR] pp.32–35). This exception does not erase overnight purge information in `single_purged`. R-J19 / `j19_draw/j19_pd_touch/j19_htf_fvg` attach here; the current caller's final-path direction and whole-AM reach are insufficient.

**SessionStat, EV, P-zones, and flow are not standalone trades.** SessionStat's average/median high-low areas, minimum-average levels, projection extensions, selected session, and lookback frame likely reach/exhaustion ([SS] pp.3–12); its choppy/low-volatility limitations remain part of the read. The source settings do not publish the exact minimum-average engine. P-zone settings show learning-window/percentile controls, not a recoverable formula ([JR] pp.16–18, 58–62). Newer nested profile/range spans must not be mistaken for outer 6–9 width or automatically named EV.

Jumbo explicitly distinguishes BigTrades from absorption bubbles and gives **NQ 100 during NY, 75 during London** ([JR] p.50). An MNQ chart is not evidence for an NQ print-size threshold. The Absorption Zone+ settings actually display body threshold **0.6**, volume multiplier **1.5**, and a **14-period** volume average ([TBR] p.35); the old “unprinted” claim is wrong. Those settings still do not prove passive replenishment. The OB is the second candle's full range; a rejection block is its rejection wick. The two “midpoint” stop captions on p.29 conflict with the differently drawn stops; retain the fixture's geometry and mark the generic conservative rule unresolved.

### Phase 1 predicate — `JJ-TBR`

The branch fields below are observations made by the decision time: `extended_context`, `purged_compressed_context`, `rotation_context`, and `directional_context` are source-context labels, not final-session path classes. `source_confirmation` identifies the chosen OB/rejection/flow signature and its location/side. `source_time_window` is the documented timing for that particular branch/fixture.

```sql
range_frozen AND context_fixed AND location_touched
AND source_confirmation AND risk_defined AND objective_fixed
AND range_known_at <= touch_at
AND context_at <= touch_at AND touch_at <= confirm_at
AND confirm_at <= decision_at
AND CASE branch
  WHEN 'judas_outbound' THEN
    directional_context AND at_rth_open
    AND objective_is_selected_exhaustion AND exit_window_recorded
  WHEN 'judas_reversal' THEN
    reversal_context AND edge_swept AND sweep_at <= confirm_at
    AND source_time_window AND objective_is_opposing_draw
  WHEN 'single_extended' THEN
    extended_context AND entry_at_eq_or_quadrant
    AND objective_is_range_edge AND reduced_expectations
  WHEN 'single_purged' THEN
    purged_compressed_context AND purge_known_at < decision_at
    AND entry_at_eq_or_quadrant AND expansion_policy
  WHEN 'internal_rotation' THEN
    rotation_context AND entry_at_named_internal_or_ev_band
    AND objective_is_named_rotation_target
  WHEN 'extension_reaction' THEN
    prior_expansion AND touch_in_source_extension_area
    AND reaction_side_confirmed AND objective_is_remaining_draw
  WHEN 'other_session' THEN
    source_clock_verified AND source_case_verified
  WHEN 'timed_pzone_reversal' THEN
    source_zone_known AND source_time_window
    AND zone_known_at <= touch_at AND directed_path_recorded
  ELSE NULL
END
```

Citations for the sequence: [TBR] pp.6–12, 20–29, 37; [JR] pp.3, 14, 25, 33, 50–57. A source-drawn proprietary band can support a fixture check; an automatically generated approximation cannot set `source_zone_known` true. Report branch eligibility, confirmation, and directional target outcomes separately. Negative controls include momentum through an exhaustion level without rejection, a presumed purge occurring after entry, and a location/target picked from the final morning range. No current R-J predicate establishes this whole loop.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Session and range geometry.** [Jumbo's 06:00–09:00 range](tbr-6-9-range.md) · [Other time-based range formations](tbr-remaining-clocks.md) · [Range EQ and quadrants](range-internals.md) · [Source range-open and range-close references](range-open-close.md) · [Range width and expectations](range-width-context.md) · [Retrospective range path](range-path-class.md) · [Overnight high, low and width](overnight-range.md) · [Chronological liquidity purges](overnight-purge.md) · [Opening location and participation](open-location-switch.md) · [Range exhaustion and mean-reversal area](range-exhaustion-area.md) · [The 1.33–1.66 extension area](extensions-1-33-1-66.md) · [Nested source range geometry](nested-range-geometry.md) · [SessionStat+ envelopes](sessionstat-9-12-envelope.md) · [Jumbo EVRange](ev-range-expected-move.md) · [Time-anchored P-zones](p-zones-benchmark.md) · [PD RTH Range+ destinations](pd-rth-range-plus.md) · [Jumbo reversal and action windows](reversal-time-window.md) · [Source session-cleanliness assessment](clean-session-label.md) · [Accumulation, manipulation and distribution phases](amd-phase-labels.md) · [Jumbo failure signatures and three attempts](jumbo-failure-attempts.md) · [Opening-range midpoint reference](opening-range-midpoint.md) · [Confirmed swing midpoint retrace](confirmed-swing-midpoint.md) · [Relative-volume context at the open](relative-volume.md) · [Equal-high or equal-low liquidity objective](equal-high-low-objectives.md).

**Regime and thesis context.** [Scheduled news and changing information](news-event-context.md).

**Price references and price-action confirmation.** [Sweep, failure and reclaim](sweep-reclaim.md) · [Prior day, week and month extremes](prior-day-week-month-levels.md) · [09:30 cash-open price](cash-open-reference.md) · [Fair-value gaps and higher-timeframe imbalances](fvg-body-gaps.md) · [Jumbo orderblocks](sweep-cisd-blocks.md) · [Jumbo rejection blocks](rejection-block.md) · [Jumbo Absorption Zone+ candle](absorption-candle-jumbo.md).

**Auction and profile structure.** [Volume profile](value-and-profiles.md) · [Profile value area](value-area.md) · [Developing profile snapshot](developing-profile.md) · [Profile point of control](profile-poc.md) · [High-volume node](hvn.md) · [Low-volume node](lvn.md) · [Profile shelf](profile-shelf.md) · [Profile ledge](profile-ledge.md) · [Overnight volume structure](overnight-profile.md) · [ETH profile identity](prior-eth-profile.md) · [Signed volume-by-price profile](weekly-delta-profile.md) · [Prior-session auction landmarks](prior-session-reference-levels.md) · [Remaining auction objectives](unfinished-business.md) · [Source-conditioned reference statistics](reference-statistics.md).

**Order-flow evidence.** [Executed aggressor-side trades](aggressor-trades.md) · [BigTrades aggression markers](big-trades.md) · [Absorption: effort without price reward](absorption-and-big-trades.md) · [Local delta concentration at an extreme](delta-spike.md) · [Native candle footprint](footprint.md).

**Risk, objectives and process.** [Entry-side structural invalidation](structural-risk.md) · [Exposure fitted to source risk constraints](position-sizing.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md) · [Source account and session stop](daily-loss-limit.md).

**Research, execution-study and risk records.** [Observed order lifecycle](order-lifecycle.md) · [Economic observation and release vintage](economic-release-vintage.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[SS]: </workspace/sources/documents/jumbo/SessionStat+.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
