# Fidelity rebuild, round 8 (2026-09-17, Fable directly)

Branch `fidelity/jj-gb`. Replay tables: `REPLAY_JJ.md` / `REPLAY_GB.md` (JSON beside them). Records: `planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-17.json`.

## 1. Where the two families stand

The framework's own fills reproduce the authors' entries on the right bar within 10 points (one 5-minute bar for R:R-tool tickets, three bars for chart-read times), on the author's play, branch and side:

| family | author entries inside the tape | reproduced by a framework fill | not reproduced |
| --- | ---: | ---: | --- |
| Jumbo | 24 | 23 | 2026-06-05 London |
| Green Bird | 16 | 15 (14 before the 07-29 record window, see §4) | 2025-11-20 |

The two that are not reproduced are not rule failures (§3).

## 2. What is holding the "selected list" back

The strategies as written are candidate generators. The drawn levels (Green Bird) and the 6–9 range with its edges, internals and projections (Jumbo) admit, mechanically, 10 to 20 opportunities a session (each opportunity = a line, a side and a sweep cycle). The authors take one to three. Which one they take is discretion the manuals do not state beyond "one opportunity at a time", "I wait until after 10AM" and "two trades were enough": on 2026-07-13 the author lets two retests of the PDL go and buys the third cycle; on 2026-07-29 he sells the pocket on a later retest; on 2026-09-01 he waits from a 04:40 overnight sweep to the 12:05 close. Every mechanical rule tried in rounds 4 to 9 to shrink the list (segment caps, one position at a time, cycle limits, adds, flips) dropped some of his trades because his trade is often not the first the framework offers. That is why the "selected" count moved between 17 and 19 of 24 (Jumbo) and 4 and 10 of 16 (Green Bird) without converging.

Decision taken in this round: two lists are computed and both scored, side by side.

- **Candidate list**: every opportunity the family's framework admits that session, once (per segment and play; at most two trades on one line for Jumbo, three for Green Bird; the segment caps of the tool are loose and reported). This is the object the author chooses from and the fidelity object of this report.
- **Executed list**: one position at a time with the family's adds (Jumbo: scale-ins at the projection and internal lines, audit 1.1; Green Bird: a later cycle of the same line) and flips (a setup on the other side closes the open trade). Reported beside the candidate list, never in its place.

The mean list sizes a day are printed beside the author's one to three so the gap is visible, not hidden by a cap. The per-day, per-play opportunity table (§5) is the input to the first context study: his taken opportunities against the untaken ones on the 40 days, by bias, first versus later cycle, sweep depth, time of day and distance to the opposing liquidity. That study, not another selection knob, is where the selection rule comes from.

## 3. The two entries the framework does not reproduce

- **JJ 2026-06-05 London, buy 30,066.50 at 03:20.** The author's drawn range R-Lo 30,162 / R-Hi 30,222 is the 01:30–02:00 ET consolidation on our tape (30,163.00–30,224.75); the 20:00–03:00 overnight box his 2025-10-13 London post draws (JR p.63) and which fits 10-06, 10-07 and 10-08 within 1.5 points is 30,052–30,264 on this day. No rule in the manual or the archive names a 01:30–02:00 range. The fill itself is reproducible once the range is given (the 03:20 bar closes 30,068 at the range's −1.66 line), so this is a discretionary range choice, recorded as such.
- **GB 2025-11-20, sell 25,301.75 at 10:05.** The chart is MNQZ2025; its 9–10 box high is 25,301.75 and its sweep reaches 25,320. On our NQ tape the same box high is 25,291.50 and the sweep reaches 25,299.75; the same rule (limit at the box high on the failure) fills 25,291.50 at 10:00–10:02, 10.25 points from his MNQ fill. No MNQ data is on disk (`/workspace/data` holds NQ and ES continuous only).

## 4. Record corrections made this round (all noted inside the JSON)

R:R-tool tickets carry the time the tool was drawn, not the fill. Where the printed fill price does not trade at the drawn time, the record's time is now the window in which that price trades on our tape: GB 08-11 20:01–20:13 (drawn 20:40, price 29,653–29,658 then), 09-03 00:32–00:35 (drawn 00:45), 04-23 12:35–12:36 (drawn 13:00; 27,116.25 prints only there), 08-27 12:50–12:56 (drawn 13:00) and 11:21–11:24 (drawn 11:30; price 29,566–29,580 then), 08-13 11:20–11:27 (drawn 11:30), 07-29 22:04–22:25 (drawn 22:20; the price first trades at the 22:04–22:05 failure close). Branch alternatives "a / b" are recorded where one author level is two adapter references: 08-27 13:00 (the 12:45 high above the 9–10/10–11 highs he names), 04-28 09:30 (the opening bar's sweep of the 09:00–09:30 low inside the developing 9–10 box), 08-13 (the trailing hour's high is the 10–11 box high at 11:24).

## 5. Per-day, per-play opportunity table (uncapped candidate lists)

Every opportunity the framework admits on the 40 dated sessions, once, without segment caps (only the per-line limit: two trades on one line for Jumbo, three for Green Bird). `in list` = the author's entry is one of them within 10 points on the right bar (any supported fill of that opportunity). Full per-day rows: `OPPORTUNITIES_JJ.json`, `OPPORTUNITIES_GB.json` in this directory; the replay tables in this directory carry the capped lists.

| family, rule state | opportunities a day (min–max) | author's entries in the list | a day, by play |
| --- | --- | --- | --- |
| Jumbo, pass 8 | 17.7 (8–34) | 23 of 24 | other_session 7.0, judas_reversal 6.1, internal_rotation 3.4, single_extended 0.5, extension_reaction 0.3, single_purged 0.2, judas_outbound 0.1 |
| Jumbo + Judas raids confined to 09:00–10:15 (TBR p.8) | 17.3 (8–34) | 23 of 24 | other_session 7.0, judas_reversal 5.7, internal_rotation 3.4, single_extended 0.5, extension_reaction 0.3, single_purged 0.2, judas_outbound 0.1 |
| Green Bird, pass 8 | 50.5 (8–72) | 13 of 16 | nyam_box 14.5, previous_hour 14.0, prior_day 4.8, london_box 4.2, asia_tdo_case 3.1, golden_pocket 3.1, cash_open 2.7, prior_week 2.5, asia_box 1.8 |
| Green Bird + a running edge is one line | 46.8 (8–61) | 14 of 16 | previous_hour 14.2, nyam_box 12.3, prior_day 4.8, asia_tdo_case 3.1, golden_pocket 3.1, cash_open 2.7, prior_week 2.5, london_box 2.4, asia_box 1.8 |
| Green Bird + his rules: last completed hour (GB p.1), closed 9–10 box (p.5), overnight bias (pp.9–11), one post-open re-entry | 37.9 (8–57) | 13 of 16 | previous_hour 9.8, nyam_box 9.2, prior_day 4.2, asia_tdo_case 3.1, cash_open 2.8, golden_pocket 2.6, london_box 2.4, prior_week 2.1, asia_box 1.8 |
| Green Bird + the post-open re-entry on the last overnight cycle that failed (final) | 38.0 (8–57) | 14 of 16 | previous_hour 9.8, nyam_box 9.2, prior_day 4.2, asia_tdo_case 3.1, cash_open 2.8, golden_pocket 2.6, london_box 2.4, prior_week 2.2, asia_box 1.8 |

The two Green Bird entries outside the final list are the ones his own rules exclude or the tape cannot print: 2025-11-20 (MNQ level, §3; the user has since confirmed NQ only) and 2026-04-28 09:45 (his documented mistake, GB p.5). Full per-day rows: `OPPORTUNITIES_GB.json`. The author takes one to three trades a day; the framework admits 17 (Jumbo) and roughly 35 (Green Bird) after his stated rules. The remaining multiplier is mechanical breadth he prunes by grading ("you're always scoring and rating a setup", GB p.4; "context - location - confirmation", JR p.33): which of the drawn levels' failures he takes when several occur, and which edge of the 6–9 he takes first.

## 6. Rules verified against the source this round

| rule (code) | source | what the tape showed |
| --- | --- | --- |
| Judas = any raid of the 6–9 edge; depth and coincident exhaustion levels recorded, not gated (`jumbo._scan_judas_reversal`) | JR p.20, 2025-10-13: "first stage of the move taking both high and low of the range before the full reversal between 9:40-9:50" | the 09:05 short is an 11-point raid of the R-Hi on a 147-point range; the 09:05 bar closes back inside at 09:10 and his 24,848.5 prints 09:11–09:16 (orderblock close 24,850 at 09:12) |
| pre-open EQ tag only when the open sits outside prior value on the purged side, or the range is big (`jumbo.selection_for`, `read["aligned"]`) | JR p.34 (2026-07-28 open-location rule), JR p.3 ("big 6-9 range > long/short the EQ"), JR p.38 (07-27 "range mid provided the entry area") | 07-27 opens above the VAH with the overnight high purged; on every other read the tag fired on 16 replay days and stopped on 15 |
| London box 20:00–03:00, traded 03:00–07:00 (`LONDON_BOX`) | JR p.63 charts (2025-10-13) | 10-06/07/08 edges within 1.5 points; 06-05 is the exception in §3 |
| GB previous hour = completed clock hours from 11:00 and the hour in progress from half past; no 5-minute rolling cuts (`_scan_previous_hour`, `session_references`) | GB p.7 "previous hour high/low if you are trading later hours"; tickets 04-23 12:36, 08-13 11:24, 08-27 12:45 | the rolling cuts produced a new level every five minutes and a candidate on most bars |
| one-minute failure read inside the five-minute bar that fails (`failure_close`) | GB p.3 "5 min close back below"; tickets 08-27 11:21 (29,618.5 vs 29,613.75), 09-01 12:07 (29,261.25 vs 29,253.75) | round 3 required the failing minute to have printed the sweep extreme, which no ticket supports |
| next drawn level at any distance (`stop_at_next_level`) | 08-28: the sell prints at the True Day Open 29,674, 29 points under the swept 9–10 high | the 15-point cap on that distance was a fit |
| running cuts live from the bar that closes them (`session_references`) | causal; 2026-08-27 12:45 sweep of the 12:00–12:45 high | the cut was stamped five minutes late, so the sweep bar was never inside a live cut |
| no running Asia box; the developing-edge limit only on the 9–10 box at the cash open (`session_references`, `_fail_branch_episodes`) | 09-03 trades the Asia high after the box closed; 04-28 "the 09:00-10:00 box low (developing)"; 07-30 the London low in progress | the Asia running cuts fired at every new session extreme; no ticket |
| objectives are drawn levels only (`objective_levels`) | "Target opposing liquidity 9-10 lows" (11-20), PDH (08-11), Asia low (09-03) | hour-box and running-cut edges as rungs produced one-minute "targets" a few points from the entry |
| a level's overnight cycle ends at the cash open; the post-open retest is its re-entry (`_fail_branch_episodes`) | 11-19 (PWL swept 04:18, bought 09:35) | an overnight limit was still "working" at 11:40 on 09-01 |

Still FITTED and labelled as such: the approach-and-reject under a level (a one-minute swing of the trailing 15 minutes within 40 points; entry at the first close past the swing bar's midpoint; tickets 04-23, 08-13), the cash-open spike turn (08-31), the pocket rungs.

## 7. Answer to "why hundreds a day"

The episode count a session (6 to 127 in the replay days) is the number of fill variants: every line × cycle × the fill modes the source supports (stop at the line, failure close, orderblock, rejection, next-bar open...). The opportunity count is the number of (line, side, cycle) objects, 10 to 20 a day uncapped. The author's count is one to three. The first two numbers are the strategy as written; the third is his discretion.

## 8. The authors' own "when to use what", and what the pool does with it

The user's point (2026-09-17 17:10): the daily choice is in the authors' posts. It is. The rules below are the ones that select, quoted from the sources, with what the adapter now does.

### Jumbo (Time-Based ranges Framework, TBR; raw archive, JR)

| his rule | source | in the pool |
| --- | --- | --- |
| "the judas trades from 9:30 to the reversal window and the actual reversal trade between the 9:40 and 9:50 ... always terminating my trading session before 10am" | TBR p.8 | Judas raids of the 6–9 edges are scanned 09:00–10:15 only (his dated Judas entries span 09:05–10:10); later edge raids are not Judas |
| "levels of interest will be the mean reversal levels or −0.5 projection" | TBR p.8 | the Judas' scale-ins at ±0.33/0.5/0.66 stay (2026-09-01 buys the −0.33 at 09:40) |
| extended overnight range → EQ/quadrants, targets the 6–9 high/low, "after 10am all interest in being in a position is no longer present" | TBR p.12, p.24 | `single_extended` on the extended read; the pre-open EQ tag on aligned or big-range days |
| purged overnight (stop hunts, liquidity taken) → expansion from EQ/quadrants, 09:40–09:50 as continuation/add | TBR p.12 | `single_purged` on the purged read (2026-07-28) |
| "RTH open location in relation to previous day value/range and the current day 6-9 ... discard mean reversion and range double breaks when these things align" | JR p.34, p.36 (2026-07-28) | the `aligned` read: open outside prior value on the purged side |
| range-size table: double break leads below 1.2%, single break above | JR (2026-06-08 table) | the size rule in the day read |
| "RTH open inside previous day value/range, scalping territory" | JR p.42 (2026-07-10) | `internal_rotation` admitted from 10:00 on inside-value reads |
| "when having a big 6-9 range > long/short the EQ" | JR p.3 (2026-09-02) | `internal_rotation` and the EQ tag on big-range reads |
| "1.33 1.66 provided the move again today ... equal highs above us gave confidence on the reversal off the 1.33 1.66 levels" | JR p.25 (2025-09-09), p.57 (2025-11-18), p.44 (2026-07-06) | `extension_reaction` after 10:00 |
| London: "same principles, same logic different times of action" | JR p.63 (2025-10-13) | the London segment on the 20:00–03:00 box |

What his words do not give: which edge of the 6–9 he takes first on a double-break day, and how many rotation scalps he takes on a scalping day ("a couple diabolical Ls and roundtrips", JR p.42). Those remain the discretionary residue.

### Green Bird (distilled framework, GB pp.1–12, tagged HIS WORDS / HIS CHART)

| his rule | source | in the pool |
| --- | --- | --- |
| "I wait until after 10AM. The 9 to 10AM range is established. No guessing beforehand." / "He documented a $12K day where the mistake was entering at 9:45 AM." | GB p.1, p.5 | the developing 9–10 box is out of the model's list; 2026-04-28 09:45 is recorded as his documented mistake (still a framework fill in the any-fill count) |
| "9:30am manipulation below, reclaim, enter for longs targeting retracement into discount, stops at lows" — "a separate trigger" | GB p.1, p.3 | the cash-open segment, its own play, not bias-filtered |
| "Previous-hour range: the last completed 60 minutes" | GB p.1 | one completed hour live at a time (replaced when the next closes), plus the hour in progress |
| Asia: "Asia highs and lows are the edges of the table ... After midnight the box is finished; the trade is sweep-and-fail of that finished box, often with a close back through TDO" | GB p.1, p.9 | the Asia box is traded once closed; no running Asia cuts |
| "IF Asia high is swept AND price closes back below (ideally also below midnight open / TDO on the 5m) THEN short toward Asia low" | GB p.9 | `asia_box` / `asia_tdo_case` sweep-and-fail with the TDO close as a mode |
| "A reclaim of PDL overnight ... can create the next day's bias (get long overnight, buy pullbacks in NYAM)" / "Bias from overnight PDL sweep and reclaim. Long overnight. NYAM: buy pullbacks / golden pockets / sweeps in the direction of that reclaim." | GB p.7, p.9–11 (Jul 14) | on days with an overnight PDL/PDH sweep-and-reclaim the NY segment's candidates are on the bias side only (the cash-open reaction exempt) |
| "First target = other side of the box, or NWOG / PDL" | GB p.3, p.8 | objectives are the drawn levels only |
| "A+ must include a sweep of the range. No sweep = not A+." / B+ "not easy to trade", 20–30 point scalps | GB p.3, p.6 | the approach-and-reject under a level (no sweep) is his B+ and stays a labelled fitted mode (04-23, 08-13) |
| "Partials every 25 points ... stop to breakeven ... runners" | GB p.8 | management, not selection |

What his words do not give: which of the drawn levels' failures he takes when several occur in a session (the A+ grade is "confluence ... you're always scoring and rating a setup"), and the exact Asia clock ("not stated; he only says Asia high / Asia low").

## 9. Population re-run on the rebuilt adapters (1,742 sessions, 2026-09-17 evening)

`tools/run_jj_gb_population.py --workers 12`: 1,742 of 1,742 sessions, 19 minutes wall, 7.9 s a session, 3.9 GB peak per worker, no failures. Three scan errors (a Jumbo internal line the day had not drawn, fixed) and 85 causality flags (the Asia TDO-close mode's trigger was stamped with the level's later failure close, fixed) were found by this run and repaired before the merge. Full tables: `../../P15-16A` style run root in the session scratchpad `pop-round8/POPULATION.md`; the numbers that matter:

| family | candidate list a day (capped: Jumbo 4 London + 8 NY, Green Bird 6 a segment) | executed fills a day | round trips a day | author |
| --- | ---: | ---: | ---: | --- |
| Jumbo | 9.6 | 11.4 | 9.1 | 1–3 |
| Green Bird | 15.5 | 17.5 | 14.5 | 1–2 |

Day reads over the population: Jumbo 1,178 double-break, 511 single-break, 53 unknown (range bins 0–0.3: 347, 0.3–0.5: 531, 0.5–0.8: 455, 0.8–1.2: 230, 1.2+: 153); Green Bird model sweep-and-fail 989, pullback-continuation 753; an overnight PDL/PDH reclaim sets a bias on 696 sessions. The lists are cap-bound on most days (Jumbo round trips cluster at 6–9, Green Bird at 13–14), which is the honest population reading of §5: the framework admits far more than the author takes, and the grading study is what closes that gap.

## 10. Sires and Saint: the ticketed fills on the drawn levels (20 of 20)

Records: the twenty ticketed fills (ten Sires sessions, one Saint session) are now marked as proper entries; two examples have no ticket (07-23's nine attempts, the WIC week). Every ticketed price prints on our NQ tape within three minutes of the ticket time.

`tools/replay_sires.py` reproduces all twenty within 10 points on the right bar (one five-minute bar) on the author's side, with the levels taken from the records (his own boxes and lines, as the P-zone fixtures were for Jumbo) and the sequence read on one-minute bars:

| mechanism (his words) | source | fills | tickets |
| --- | --- | --- | --- |
| origin of the move: the squeeze through the line, the failure back, the retest of the failure box ("short on the retest of the failed squeeze, stop above the sellers' aggression") | OFM p.7, p.14; K18 p.6; K2345 p.7; CONT p.7 | failure close, stop at the line, next open, limit at the line or the box's near edge on the retest, stop beyond the retest bar | 07-08 10:47, 07-10 10:18 and 10:24, 07-31 09:35, 08-04 09:37, 08-19 09:35, 07-15 01:01 |
| refill / defended band ("sellers absorbed at the bottom, no result for the push") | NYAM p.4; BIG p.16 | the close back away from the band, the next open, the limit at the band's near edge | 07-14 09:37, 08-06 09:52 and 10:04, 07-09 09:51 |
| failed auction / band reclaim ("tag of an older balance's POC, instant rejection") | BIG p.11 | the reclaim close, next open, a stop one tick beyond the edge | 08-06 09:33 and 09:36, 07-31 09:33, 08-04 09:31 |
| break of a short-term balance or of a band's far edge ("strength to push through a short term microbalance"; the third retest of the support band failing) | K2345 p.7; NYAM p.9 | a stop one tick through the level; the retest of the broken level after a 25-point departure | 07-09 09:35, 07-14 10:15, 10:17 and 10:36 |
| Saint: the intraday level breaks, price leaves, comes back once ("two waits, not one") | TRAP pp.6–7 | the retest bar's extreme, its close, the next open | 08-10 19:47 (his panel says 19:51; the price he prints is the 19:47 retest high on NQ) |

What this does not yet do, and is the next step for these two families: draw the levels from data. Sires' boxes are aggression clusters (prints of thirty contracts and more absorbed at one area, BIG p.3) and profile shelves, ledges and nodes; Saint's are the higher-timeframe balance and the intraday levels off the open and balance. The trade data on disk covers the sessions (weekly NQ trade files through 2026-08-31). Generating the aggression boxes from the trades and comparing them with the twenty drawn boxes is the Sires equivalent of the P-zone fit, and the profile objects are Phase 3.

### 10.1 The trade data is fill-level; the author's bubbles are order-level

Probe on the two clearest Sires charts (`cme__nq-continuous-futures__trades`, weekly files):

| window | fills | prints ≥ 30 contracts as recorded | aggressor orders (fills sharing one event timestamp and side) ≥ 30 | ≥ 60 | ≥ 100 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026-07-08 10:30–10:52 | 20,626 | 1 | 19 | 3 | 1 |
| 2026-07-14 09:30–09:40 | 16,285 | 1 | 12 | 2 | 0 |

Read as orders, the prints land where he drew: on 07-08 a 106-contract sell at 10:43:20 spans 29,222–29,228 (his "absorbed aggression" box 29,224–29,231), and 40-contract buys at 10:39:47 and 10:41:17 sit at 29,251–29,256 (his failure box 29,246–29,251.5, the circled buyers "getting exhausted into the catalyst"); on 07-14 a 39-contract buy at 09:37:33 spans 29,741–29,746 (his 29,745 support, "sellers absorbed at the bottom") and a 38-contract buy at 09:33:03 sits in the refill box 29,750–29,757. Deepchart draws an aggressor order as one bubble; our feed records each fill against the book. The earlier Sires adapter (`AGGRESSION_MIN = 30` on fills) and the Refill study's cluster rule therefore almost never saw the prints the authors describe ("sixty, eighty, a hundred contracts hitting in seconds"), which is a large part of the plausibility failures the audit recorded (S3, R1–R2). Level generation for Sires and the Refill re-measurement must start from order-level aggregation.

### 10.2 Generating his boxes from order-level prints (`tools/sires_levels_fit.py`)

Boxes are clusters of aggressor orders (fills grouped by event timestamp and side) within 6 points and 3 minutes of each other, at least two orders. His 32 drawn boxes on the nine sessions split by what they are: 15 aggression / absorption / refill boxes (order-flow prints), 6 squeeze structures (failure box, wick, entry box), 11 profile objects (nodes, resistance and support bands, composite zones). The cluster rule is scored on the first group; the other two are the Phase 3 objects.

| size cut | absorption filter | drawn boxes reproduced (of 32) | aggression boxes (of 15) | structure (of 6) | profile (of 11) | generated boxes a session |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| fixed 30 contracts (BIG p.3) | none | 25 | 13 | 6 | 6 | 21.8 |
| fixed 60 contracts, single orders | none | 16 | — | — | — | 13.4 |
| fixed 30 | no follow-through beyond 4 points in 3 minutes | 10 | — | — | — | 6.1 |
| adaptive: top 0.5% of the trailing hour's orders (floor 20) | none | 29 | 13 | 6 | 10 | 34.0 |
| adaptive 0.5% | no follow-through beyond 1.0 × the trailing median minute range in 2 minutes | 26 | 12 | 4 | 10 | 21.6 |
| adaptive 0.2%, at least 3 orders | same, 1.0 × range | 19 | 11 | 3 | 5 | 13.7 |
| adaptive 0.1% | same, 1.0 × range | 21 | 11 | 3 | 7 | 15.4 |
| adaptive 0.1%, at least 3 orders | none | 18 | 9 | 6 | 3 | 13.3 |
| adaptive 0.5%, at least 3 orders | 1.5 × range in 3 minutes | 23 | 11 | 3 | 9 | 16.7 |
| adaptive 0.2% | 2.0 × range in 5 minutes | 25 | 12 | 3 | 10 | 23.1 |

The sweep settles the shape of the trade-off: the aggression boxes he drew are recovered 11 to 13 of 15 across every adaptive setting, and the count a session moves between 13 and 34 with the size cut and the absorption tolerance. No setting reaches his 2 to 6 while keeping his boxes, so the cluster rule is the admission layer for order-flow levels and the grading model (section 11) is what prunes them, as with the other families.

A fixed contract number is the wrong object, as the user noted and as the author says ("bubble scale adjusted with the session's volume", BIG p.3): the adaptive cut finds the boxes he drew on every session including the quiet overnight one, at the cost of more boxes; the absorption test ("aggression that gets nothing") is what should prune them, and a fixed 4-point tolerance pruned the wrong ones. The tolerance now follows the trailing minute range; those results are appended below when the run completes. He draws 2 to 6 boxes a session; the count after absorption is the number to judge.

### 10.3 The tickets scored on GENERATED boxes

`replay_sires.py --levels generated --adaptive` (boxes from order-level prints with the session-adaptive size cut, no absorption filter, generation from the prior session's 09:30 so the prior day's bands exist, only boxes known before the ticket): **18 of 20 tickets** reproduced within 10 points on the right bar on his side (`REPLAY_SIRES_GENERATED.md`). The two outside: 2026-07-31 09:33 (his "wick box", a squeeze structure, not an aggression box; the nearest generated fill is a break-retest 30 points away at 09:39) and 2026-08-06 09:33 (his long at 29,258 off the prior day's band; the generated boxes there give a failure fill at 29,295.5 at 09:35, 37.5 points above, so the band he used is not a cluster the rule draws). The 08-06 09:52 ticket, missed when generation started at 08:00, is found once the earlier window exists. So the entry mechanics hold on levels the data draws, not only on the levels he drew; what remains is the count (the grading layer) and the two object families the cluster rule does not cover (squeeze structure, profile).

### 10.4 Keani (no dated ticket): where the zero comes from

Forty random sessions through `scan_keani_branch_b02`: 40 fail, 28 at context (the 09:30–10:00 period is not fully above the prior day's 70% value area high) and 12 at the trigger (the break of the current value area high on aggressive imbalances, retest holding). The context condition is the trader's own ("the whole A period above prior value"); the trigger as coded is what never fires on the days that reach it. Without a dated example the trigger cannot be calibrated against a tape; it stays a documented plausibility failure until a dated post exists.

Addendum to 10.4: the Keani trigger asks the footprint object (`market.domain("O109", candle)`) for aggressive buy-imbalance runs on the candle that breaks the current value area high, and the breakout counts only when runs exist. Footprint imbalances are computed from the same fill-level trade file (10.1), so the runs are as under-reported as the aggression prints were; the object must be rebuilt on order-level aggregation before the Keani trigger can be judged. That is Phase 3 work, and it is the same repair as Sires' boxes and the Refill zones.

## 11. The grading study, and the authors' own precedent for it

Every family inflates for one reason: the manuals state admission rules (a level and a sweep-and-fail; a band of absorbed aggression), and admission fires 10 to 40 times a day; the choice among them is grading, which no author writes as a rule. The Refill paper (REF pp.3–9) is the authors' own version of the answer: every touch becomes a row with roughly twenty pre-touch features in four families (memory, construction, location, flow and state), a deliberately simple model is trained on the past and graded on the future, and "selection is what changes the sign" (fade everything −0.285R; the model's top-ranked touches +0.14R, AUC 0.63 against a 0.51 placebo). Their decomposition also says which features carry it: memory and location, not the raw order flow.

The tools for the same study across families are on the branch: `build_grading_dataset.py` (one row per admitted opportunity on the dated sessions, features the authors name: confluence with the drawn levels, cycle index, sweep depth, minutes from the open, side against the overnight bias, the day read, the play, reward available; label = the ticket) and `fit_grading.py` (leave-one-day-out logistic fit, the threshold set at the authors' density, recall at that density, ranked weights). Recall at density is the fidelity of admission plus grading together. Sires and Saint rows follow from the generated-level replay. Two caveats stated up front: 60 positives is a small labelled set (the archives add more dated posts over time), and the features that need Phase 3 objects (profile nodes, delta bands) are not in the first fit.

### 11.1 The first fit (Jumbo and Green Bird, 36 dated sessions)

Dataset `grading/rows.csv`: 876 admitted opportunities on the 36 sessions with an inside-tape ticket (uncapped candidate lists, one row per opportunity: Jumbo 17.3 a day, Green Bird 36.8), 27 rows carrying a ticket (13 Jumbo, 14 Green Bird). Fit: class-weighted logistic regression, L2 = 2, leave-one-day-out, threshold at the target density (`grading/GRADING_FIT_per_day_2.json`, `_3.json`).

| family | tickets | sessions | recall at 2 a day | recall at 3 a day | ticket in the top 1 / 3 / 5 | median rank of the ticket | features carrying the fit |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| Jumbo | 13 | 23 | 0.23 | 0.46 | 0.23 / 0.46 / 0.54 | 4 of 17 | not aligned (−), single-break play (+), fewer coincident levels (−), sweep inside the first third of the box (+), the −0.33 projection (+), open inside value (−), London (−), q25 (+), signature close (−), shorter stop (−) |
| Green Bird | 14 | 13 | 0.00 | 0.00 | 0.00 / 0.07 / 0.14 | 27 of 37 | five-minute close (−), previous-day 10–11 box (−), running 12:00 hour box (+), at-level fill (+), 11:00 hour box (+), Asia box (−), 10–11 box (+), London box (−) |

Read plainly: for Jumbo the stated features carry part of his choice (the ticket is in our top five on seven of thirteen days, and the weights are his own words: the Judas fires on the day the read is *not* aligned, the single-break play on the range-size read, shallow sweeps), but at his density of two a day the fitted scorer recovers three of thirteen tickets. For Green Bird the fitted scorer does not recover his ticket on any day at any of the tested densities; the median rank of his ticket is 27 of 37, worse than chance, and the weights are box names, which is memorisation of thirteen days, not a rule. The features the dataset carries (which box, which mode, confluence with the drawn levels, cycle index, minutes from the open, side with the overnight bias, the day model, reward available) do not contain what he grades on. That is the result, not an error to tune away: what separates his one trade from the thirty-six admitted on a Green Bird day is not in the levels-and-time description, which points at the Phase 3 objects he shows on every chart (the volume profile and delta bands beside the box, the "nice" 9–10 box against a "messy" one) and at the post's own narrative features (which side the overnight session reclaimed and how, which box the previous hour closed against). Sires and Saint rows (level-and-flow features from the order-level boxes) go into the same fit next; a Refill-style feature set (memory of the level, construction, location in the day's range, flow at the touch) is the working hypothesis for both families, since that is the decomposition the authors' own paper found to carry the sign.
