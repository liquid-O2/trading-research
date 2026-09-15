# JJumboFX — SDRange / Time-Based Ranges framework

## Current evidence

Phase 1 setup implementation and the acquired historical census are complete. These counts describe observed setups with branch-specific input limitations; they are not fills or profitability. The source definitions below retain author-specific boundaries. Our inferred reconstruction is versioned separately.

[Full method measurements](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/JJ-TBR.md) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) · [Research status](current-status.md).

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR | full acquired historical measurement | 3912 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/JJ-TBR.md |
| JJ-TBR | B0 engineering slice (9 dates, not a family population) | see P15-09 BASELINE_PARITY | not claimed | dual-scan slice; full-history not run (p90>5s, P15-17 projection>24h) | implementation/reports/research-work/P15-09/ |
| JJ-TBR | B0.1 engineering slice (9 dates, not a family population) | see P15-09 BASELINE_PARITY | not claimed | Judas strict/deferred; C2 10:00 window; slice not family population | implementation/reports/research-work/P15-09/ |
| JJ-TBR | F1 changed-formation candidate (9-date engineering slice, not a family population) | 84 episodes beside B0.1 10 | not claimed | own F1 high/low lifecycle contacts (distinct_contacts, 4-tick departure); status evaluated, not assigned | implementation/reports/research-work/P15-09/ |
| JJ-TBR | R-quadrant changed-reference candidate (9-date engineering slice, not a family population) | 156 episodes beside B0.1 10 | not claimed | own EQ/q1/q3 lifecycle contacts; q1 is not the EQ-only source location | implementation/reports/research-work/P15-09/ |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| JJ-TBR | M01 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |

## Source definitions


Operating method / JJ-TBR. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


**Why one method.** The manual calls false breakout/Judas and range breakout applications of the same time-based framework ([TBR] pp.6–12). The raw record says “same ranges, different layers” on 15 May 2026 and “same 6-9 framework, more refinement” when adding order flow on 23 February ([JR] pp.11, 14, posts 2055344660986364371 / 2026059018750378427). The later summary is the author's own ordered phrase: context, location, confirmation ([JR] p.33, post 2093335135789719861).

### Ordered loop and attachments

| Step | Source operation, in order | Source-object implementation snapshot and evidence limits |
|---|---|---|
| 1. Choose the session and freeze its geometry | Select the range being traded. Main NY formation is 06:00–09:00 ET; draw H/L, width, EQ, quadrants, range open/close and projections. The manual also lists Asia 20:00–20:30, midnight 00:00–00:30, London 03:00–03:30, 09:30–10:00, 10:00–10:30, lunch 12:00–12:30 and 15:00–15:30. These are applications of the framework, not eight entry products. ([TBR] pp.4–7.) | [O003](clock-grid-and-bars.md) · [O005](tbr-6-9-range.md) · [O006](tbr-remaining-clocks.md) · [O007](range-internals.md) · [O008](range-open-close.md) · [O016](nested-range-geometry.md). Frozen clocks, exact parent identities and nested geometry are implemented. Automatic selection of the author's preferred session remains source-dependent. |
| 2. Set expectations before the entry | Read overnight size and balance, liquidity already purged, open versus previous RTH value/range and today's box, news, and current behavior. Wide/extended overnight and range-bound news conditions reduce targets and risk; compressed/purged conditions can favor single-direction expansion. The raw July examples include continuation from outside value while still inside the prior price range: “outside both AND high RVOL” is a particular case, not the only permission to continue. ([TBR] pp.12, 16–24; [JR] pp.33–39, 48–49.) | [O009](range-width-context.md) · [O010](range-path-class.md) · [O011](overnight-range.md) · [O012](overnight-purge.md) · [O013](open-location-switch.md) · [O027](relative-volume.md) · [O029](news-event-context.md). Chronological purges, opening observations, completed-window relative volume and causal news admission are implemented. Final path labels remain outcomes; later opening volume cannot inform the cash-open decision. |
| 3. Choose a location and a destination within that case | Exhaustion beyond a swept edge, EQ/quadrants on internal entries, 1.33–1.66 after expansion, or a source-drawn P-zone/expected-range boundary. Preserve separate identities for 6–9 EQ, EV midpoint, SessionStat bands, P-zones, and RTH/profile references. Mark the remaining directional objective before acting. ([TBR] pp.8–24, 31–35; [JR] pp.3, 23–26, 48, 53–57.) | [O014](range-exhaustion-area.md) · [O015](extensions-1-33-1-66.md) · [O017](sessionstat-9-12-envelope.md) · [O018](ev-range-expected-move.md) · [O019](p-zones-benchmark.md) · [O020](pd-rth-range-plus.md) · [O087](unfinished-business.md). Range projections and the remaining-object ledger are implemented. EVRange, P-zone and Stat+ proprietary construction remains unavailable; supplied source readouts retain their settings and times. |
| 4. Let the selected location produce the selected entry signature | The manual's favorite reversal entries use 2/3/5-minute orderblocks or rejection blocks; they are expressly personal entry choices, not fixed to the model. Later charts add absorption candles, BigTrades, footprint/profile behavior, and refinements at the same range levels. Use the confirmation actually present in that source episode. ([TBR] pp.27–31, 35; [JR] pp.14, 48, 50, 52, 67–69.) | [O004](execution-bars.md) · [O055](fvg-body-gaps.md) · [O056](sweep-cisd-blocks.md) · [O057](rejection-block.md) · [O058](absorption-candle-jumbo.md) · [O063](developing-profile.md) · [O077](weekly-delta-profile.md) · [O099](big-trades.md) · [O120](footprint.md). Selected-parent geometry, mirrored blocks, native profiles and local execution observations are implemented. Source confirmation choice and unavailable platform settings remain explicit inputs. |
| 5. Enter with the case's risk and target policy | Choose immediate, retracement, or stop-triggered execution and structural invalidation. The OB example distinguishes a midpoint stop/entry from a conservative boundary stop. Size and target ambition depend on the case. Do not turn a ticket's points or R:R into a universal preset. ([TBR] pp.24–29; [JR] pp.3, 54–57.) | [O139](structural-risk.md) · [O140](position-sizing.md) · [O141](trade-objective.md) · [O150](order-lifecycle.md). Entry-side invalidation, exposure, fixed objective and order lifecycle are implemented. A historical source entry or fill still requires its actual linked record. |
| 6. Manage, recognize failure, and reassess | Take the appropriate internal/opposite/external objective, protect or compound justified winners, and reduce ambition in grind. Three failed reversal attempts at the same level, strong bodies/volume continuing through it, or absent rejection defeat a reversal idea. Exit and observe; if continuing after failure the manual says reduce allocation at least 50%. Reassess another case/session rather than relabel the failed fade as a successful breakout. ([TBR] pp.24, 36–37.) | [O024](jumbo-failure-attempts.md) · [O026](confirmed-swing-midpoint.md) · [O142](position-management.md) · [O145](daily-loss-limit.md) · [O150](order-lifecycle.md). Distinct attempts, protected geometry, amendments, partials and session constraints are implemented. Supplied source policies and actual management records remain necessary. |

### Branches inside this loop

| Branch | Source sequence and objective | Boundary on interpretation |
|---|---|---|
| `judas_outbound` — Judas Trade #1 | At the 09:30 open, take the contextual move toward the selected exhaustion projection; close as the 09:40–09:50 reversal window arrives. ([TBR] pp.8–10.) | The direction and exact entry selection are not supplied by the later double-break label. This is an outbound leg, not the reversal entry. |
| `judas_reversal` — Judas Trade #2 | A completed range edge is swept; the exhaustion area produces a reversal signature, normally in the manual's 09:40–09:50 window; trade back through internal levels toward the opposite liquidity/projections. ([TBR] pp.8–11, 27–29.) | A mandatory exact ±0.5 touch is too narrow. Raw charts include shallow edge sweeps. Record depth; do not choose the deepest eventual excursion retrospectively. |
| `single_extended` | Extended overnight: wait for an EQ/quadrant entry in the allowed direction, usually take the range edge, moderate risk and expansion expectations. ([TBR] pp.12–14, 24.) | The eventual “single break” cannot be an entry-time input. “Extended” has no author-exact universal width ratio. |
| `single_purged` | Overnight stop hunts have already removed the relevant liquidity; the contracted range supports expansion from EQ/quadrants. 09:40–09:50 can be a continuation/add window, not a compulsory reversal. ([TBR] pp.12–15.) | Preserve the actual overnight references and when they were taken. Containment of two completed boxes is not a purge-time ledger. |
| `internal_rotation` | In the appropriate wide/in-value context, take confirmed rotations at EQ/expected-range locations, with nearer objectives. The 2 September raw example explicitly trades EQ both ways on a big 6–9 range and includes two losing attempts. ([JR] p.3, post 2095172969035096454; pp.38–43.) | EQ is a location; the author does not publish “touch EQ = reverse.” EV and EQ are different targets. |
| `extension_reaction` | After range expansion reaches the 1.33–1.66 area, examine rejection/continuation and the still-owed objective. The September 9 example combines session-average lows, that extension area, and equal highs as the long's destination. ([TBR] pp.20–21; [JR] pp.23–26, 57, 71.) | Extension touch, HOD/LOD in the band, and a confirmed reversal are different observations. Each projection uses its actual parent range width. |
| `other_session` | Apply the selected geometry and signatures to the observed London or later-session case. AM consolidation can precede PM expansion; AM expansion can precede PM consolidation. ([TBR] pp.7, 36; [JR] pp.46, 50–51, 63–66.) | Every dated London chart builds the box 02:00–03:00 ET and trades it 03:00–06:00 with the same quadrant, ±0.5 and 1.33–1.66 geometry ([JR] pp.50, 63–64); the earlier 00:00–03:00 assumption was wrong (re-read 2026-09-15). “London is cleaner this cycle” does not publish a rolling-ten-day selector. |
| `timed_pzone_reversal` | Use the actual time-anchored P-zone and observed reversal sequence. The January 2 post's “low > range open” describes a path from the low to the range-open line; the December 17 post's “10 am p-zone > london low” names another path. ([JR] pp.53–55.) | The arrow is not an inequality. A 09:00 zone anchor is not proof of a 09:00 fill. Later time-specific examples must not be forced into the manual's 09:40 window. |

**PD RTH Range+ is a context/destination application.** It uses prior 09:30–16:00 highs/lows and M15/H1 imbalances, waits for current RTH direction, then trades toward those objectives with the range framework. In this expressly RTH-only view, an ETH sweep does not consume the RTH objective ([TBR] pp.32–35). This exception does not erase overnight purge information in `single_purged`. [O020](pd-rth-range-plus.md), [O055](fvg-body-gaps.md) and [O087](unfinished-business.md) implement the selected references, availability and remaining-object scope; historical source direction still requires evidence known before the decision.

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



## Source fidelity re-read, 2026-09-15

Every raw post in [JR] (71 pages), the two manuals ([TBR], [SS]) and the duplicate archive [XF] were re-read, with every chart and ticket rendered at native resolution and the small text (order tickets, on-chart tables, axis clocks, indicator panels) read from zoomed crops. This section records how the author actually trades, the dated examples with printed prices, and what the text above and the implementation had wrong or missing. It does not change the Phase 1 predicate; it defines what the source-faithful baseline B0.2 ([P15-16A](/workspace/planning/phase-1-5/tasks/P15-16A.md)) must reproduce.

### How the author actually trades

- **Clocks.** The 06:00–09:00 ET box is frozen at 09:00 and the author acts from 09:00, not from 09:30: the 2025-10-13 chart takes the range high at 09:00–09:15 and the low inside 09:40–09:50 ([JR] p.20); the 2026-01-02 chart takes a "P-zone + low > range open" long at about 09:22 ([JR] p.54); the 2026-01-09 chart marks an absorption at the 09:00 high before the open ([JR] p.51). The manual's "enter after the open" is superseded by the author's own practice. The 09:40–09:50 window is the modal reversal time (histogram peak of about 1,000 of 4,537 days, with a secondary peak at 09:00–09:06; average reversal time 09:47:36 on the original range, 09:51:05 on the extended range, 86.46% reversal rate from the extended range) ([JR] p.70). Extension reactions at ±1.33/±1.66 are taken after 10:00 (10:15 on 2025-11-10, 10:35 on 2025-09-09, 11:00 on 2025-11-18, 10:45–12:00 on 2026-07-06) ([JR] pp.25–26, 44, 57, 59).
- **London box.** The London range is built 02:00–03:00 ET and traded 03:00–06:00, with the same quadrant, ±0.5 and 1.33–1.66 geometry (2025-10-06, 2025-10-07, 2025-10-08 and 2026-06-05 charts; the 06:00 line hands off to the 6–9 build) ([JR] pp.50, 63–64). The earlier assumption of a 00:00–03:00 London formation in `other_session` is wrong.
- **Timed P-zones.** The SDRange+² table anchors P-zone sessions at 09:00 (Session 1), 10:00 or 09:50 (Session 2) and 02:00 (Session 3) ([JR] pp.16–18, 53–54). The P-zone entry is an absorption print inside the timed box: 2026-01-09 long from 25,664.25 at 09:32 inside the 25,655–25,665 "9am P-zone", original stop 25,617.25 below the box, target the D-1 High 25,850 (sell limit 25,846.50) ([JR] pp.51–52); 2026-01-02 10:00 P-zone reversal from 25,760–25,768 to the London low ([JR] p.53).
- **Levels drawn.** 3-day lookback pivots (D-1, D-2, D-3 highs and lows), London and Asia highs and lows from liquidity sessions 02:00–07:05 and 18:00–00:05, prior RTH high/low and value (pRTHH, pRTHL, pRTHVAH, pRTHVAL), POC, the 15-minute opening range (ORH, ORM, ORL), the overnight high and low, EVRange and its +50% line, SessionStat envelopes ([JR] pp.16–18, 30–31, 33, 36, 38, 42).
- **Model selection by open location.** RTH open below the prior RTH value low with continuation (2026-07-28, +138) discards the fade; open inside prior value (2026-07-10) means range scalps and fast breakout failures; open below the prior RTH high and VAH (2026-07-27) gave a single break entered at the range mid ([JR] pp.36, 38, 42). The author's own first-hour statistics by open location: for opens below VAL inside the range (n=396) the high only was taken 29.5%, the low only 37.6%, both 29.8%, one side 67.2%; for opens below VAL and below PDL (n=517) 23.6% / 46.2% / 27.3% / 69.8% ([JR] p.37).
- **The A+ fade template.** "Range double break expectancy (in value / in range) + overnight H/L + AM vol expected range": on 2026-08-28 the R-Lo 29,592, EVRange lower 29,590 and overnight low 29,578 coincided; long at the 09:30–09:32 drop, sell limits at the overnight high 29,707.25 and EVRange upper 29,724.50, trailing sell stops 29,619 and 29,604.75, +$1,447.50 on 10 MNQ ([JR] p.33). On 2026-09-01 the EVRange envelope was 29,058–29,195 with +50% at 29,290; the timed 09:40 low was bought at the EVRange lower line (5 @ 29,074.25) and the EQ/EVRange upper line was the pivot for the later shorts and the pullback long (5 long at 29,204.75) ([JR] pp.30–31).
- **Size and management.** Clips of 5–10 MNQ or 1–3 NQ; scaling in and out at the range lines (2025-10-03: sell 5 @ 25,119.50, buys 5 @ 25,091.45 and 5 @ 25,072.75 at −0.5, adds 5 @ 25,100 and 10 @ 25,111.50, exits 5 @ 25,117 and 15 @ 25,128.75) ([JR] p.66); exits at +0.5 or the opposite edge rather than the far projection (2025-01-28: buy 2 NQH5 at 21,241.75 at 09:53:46 ET, sell at 21,457.75 at 10:27:05 ET, +216 while the day ran to +1.66 by 15:00) ([JR] p.71). A losing morning with "diabolical BEs" is part of the record ([JR] p.31).
- **Published statistics.** SDRange+² projection summary over 3,753 sessions from 2010-06-07 to 2025-01-21: 1.33× captured the daily high 89.2% and the daily low 65.6%; 1.66× 92.4% and 66.8% ([JR] p.23). SessionStat+ envelopes are the last 60 sessions' average and median high, low and range of the selected clock (RTH 09:30–16:00 Exp Avg 75.28, Dist Avg 100.8, Min Avg 37.14; London 4-hour Exp Avg 74.53) ([JR] pp.26, 69). BigTrades thresholds NQ ≥100 in New York and ≥75 in London ([JR] p.50).

### Dated examples with printed prices

| Date (ET) | Session and clock | Geometry | Printed fills and orders | Source |
|---|---|---|---|---|
| 2025-01-28 | 6–9 range 152.50 pts; 09:40 Judas to −0.5 (21,180) | H 21,410 / EQ 21,334 / L 21,258 | Buy 2 NQH5 21,241.75 at 09:53:46; Sell 2 21,457.75 at 10:27:05 (ticket clock UTC) | [JR] p.71 |
| 2025-05-23 | London 02:20–03:15; SessionStat 4-hour LOW box 21,086–21,102 | prior RTH low 21,115 | Buy 10 @ 21,108.50 (02:20), buy 5 @ 21,170.50 (03:10), sells 5 @ 21,169.75 / 21,172.25 / 21,17x.75 (03:15) | [JR] p.69 |
| 2025-09-09 | −1.66 at 10:35 inside the RTH SessionStat LOW box | H 23,860 / L 23,810; −1.66 ≈ 23,730 | long from −1.66 to the range low by 11:45 (+84) | [JR] pp.25–26 |
| 2025-10-03 | 09:55 short at 75%; 10:05–10:15 −0.5 longs | H 25,196 / EQ 25,150 / L 25,104 / −0.5 25,058 | sell 5 @ 25,119.50; buys 5 @ 25,091.45, 5 @ 25,072.75, 5 @ 25,100, 10 @ 25,111.50; sells 5 @ 25,117, 15 @ 25,128.75 (MNQZ2025) | [JR] p.66 |
| 2025-10-06 / 10-07 | London box 02:00–03:00, traded 03:00–06:00 | Oct 6 H 25,108 / EQ 25,080 / L 25,052; Oct 7 H 25,187 / EQ 25,154 / L 25,122 | dips to the 25% line (03:40; 04:30), returns to the high and +0.5 before 06:00 | [JR] p.64 |
| 2025-11-10 | +1.66 short at 10:15 to −0.5 and the London low by 11:45; PM run to +2.5 | H 25,560 / EQ 25,530 / L 25,500; L1 25,458 | none printed | [JR] p.59 |
| 2026-01-02 | 09:00 P-zone long 09:22–09:31; 10:00 P-zone reversal | H 25,741 / EQ 25,711 / L 25,681; P-zones 25,758–25,764, 25,718–25,725, 25,660–25,666, 25,620–25,626 | none printed | [JR] pp.53–54 |
| 2026-01-09 | 9am P-zone absorption long at 09:32; D-1 High target | H 25,810 / EQ 25,760 / L 25,710; P-zone 25,655–25,665 | long 1 NQ 25,664.25, stop 25,617.25, sell limit 25,846.50, stop trailed to 25,733.25 (+$3,120 at 10:26) | [JR] pp.51–52 |
| 2026-06-05 | London −1.66 long 03:20, R-Hi short 04:30, R-Lo long 05:03 | R-Hi 30,222 / EQ 30,195 / R-Lo 30,162; −1.66 30,058 | buy 3 @ 30,066.50; sell 10 @ 30,215.25; entry 5 @ 30,160.75; close 5 @ 30,215.75 | [JR] p.50 |
| 2026-07-16 | opening sweep of 29,525 at 09:30–09:35, ride to R-Lo | R-Hi 29,555 / EQ 29,460 / R-Lo 29,358 | sells 3 @ 29,451.50 and 2 @ 29,438 (09:35); buy 5 @ 29,312.25 (09:45) (+143) | [JR] p.41 |
| 2026-08-28 | A+ fade at the R-Lo / EVRange / ONL confluence at 09:30–09:32 | R-Hi 29,668 / EQ 29,630 / R-Lo 29,592; ONH 29,707, EVRange 29,590–29,724 | sell limits 29,707.25 and 29,724.50; trailing stops 29,619 and 29,604.75; +$1,447.50 on 10 MNQ | [JR] pp.32–33 |
| 2026-09-01 | range and EVRange scalps 09:25–11:00; pullback long 10:40 | R-Hi 29,260 / EQ ≈29,192 / R-Lo 29,120; EVRange 29,058–29,195, +50% 29,290 | 19 fills including buy 5 @ 29,074.25 at 09:40 and sell 5 @ 29,196.25 at 10:32; 5 long at 29,204.75 with a sell stop 29,214.75 | [JR] pp.30–31 |

The 2026 NinjaTrader screenshots print UK local time (09:40 ET appears as 14:40); TradingView charts print UTC−4 or UTC−5; the 2025-01-28 ticket clock is UTC.

### What the text above and the implementation had wrong or missing

1. The sweep search must start at 09:00 (range close), and the 09:00–09:30 segment is traded off the 09:00 P-zone anchor; the manual's after-the-open rule is not what the author does ([JR] pp.20, 51, 54).
2. `other_session` assumed a 00:00–03:00 London formation; the box is 02:00–03:00 with action 03:00–06:00 ([JR] pp.50, 63–64).
3. `judas_reversal` did not model the reclaim entry after the window (2025-01-28 09:53 entry) nor the exit below +0.5; `extension_reaction` was scanned inside the 10:00 window it should exclude (ruled F08).
4. The mean-reversal band is drawn as ±0.33 to ±0.66 beyond the edge from December 2025 (the manual's ±0.5 sits inside it), and the projection ladder runs to ±3 ([JR] pp.16–18, 59).
5. SessionStat envelopes are 60-session statistics of the selected clock and are the confluence for extension entries; EVRange is an AM expected-move envelope around the open with a +50% line; neither was modelled as a location ([JR] pp.26, 30–31, 69).
6. The open-location model selector (fade versus single break versus scalp) was treated as an outcome label; the author reads it pre-open from the prior RTH value and range ([JR] pp.36, 38, 42).
7. Position handling is scaled and laddered at the range lines; a single bracket per branch does not reproduce the ledger ([JR] pp.30–31, 66).
8. The historical scanners place the `extension_reaction` band at edge ± [0.33, 0.66]·W while the author's ±1.33/±1.66 lines sit at edge ± [1.33, 1.66]·W (2025-01-28: H 21,410, W 152.50, band 21,600–21,660; 2025-09-09: L 23,810, W 50, band 23,745–23,730; 2025-11-10: H 25,560, W 60, band 25,635–25,650); the standalone object O015 is right and the census branch is a full width too close (Astra J21, verified; ruled RR-01).
9. The candidate-reference enumeration fixes EQ and q1 as long and q3 as short; the author trades EQ both ways and the manual permits quadrant entries in the extended and purged cases (Astra J22, verified; ruled RR-02).

### What B0.2 must reproduce

Timed windows as stated (09:00 close, 09:40–09:50 modal reversal, extension after 10:00, London 02:00–03:00 build); the P-zone anchors; the level set above; the reclaim entry and the +0.5 exit; the published statistics (86.46%, the 1.33/1.66 capture table, the first-hour sweep table) reproduced on our tape as the plausibility section of the Strategy Book; and the author-example replay of the eleven dated sessions above (the 2025 and 2026-01 to 2026-08 dates lie inside the run-1.0.1 calendar; 2026-08-28 and 2026-09-01 lie after the native data endpoint).


### Astra dossier corrections (2026-09-15, night)

From [JJ-TBR.md](/workspace/planning/research-program/reviews/astra-family-dossiers-2026-09-15/JJ-TBR.md), ruled SD01 and SD02: the 35% footprint transaction filter ([JR] pp.49–50) is a separate flow view from the 100/75 BigTrades threshold and is labelled as such; SessionStat readouts depend on chart aggregation and cannot span midnight ([SS] pp.7–8), so a supplied readout keeps its chart settings; the manual's "before 10:00" preference belongs to the extended case only; the 2025-01-28 ticket clock is UTC by the 09:53 ET match, recorded as an inference.

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
