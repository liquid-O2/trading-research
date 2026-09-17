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

Every opportunity the framework admits on the 40 dated sessions, once, without segment caps (only the per-line limit: two trades on one line for Jumbo, three for Green Bird). `in list` = the author's entry is one of them within 10 points on the right bar (any supported fill of that opportunity). Full per-day rows: `opps_jj2.json`, `opps_gb4.json` in the session scratchpad; the replay tables in this directory carry the capped lists.

| family, rule state | opportunities a day (min–max) | author's entries in the list | a day, by play |
| --- | --- | --- | --- |
| Jumbo, pass 8 | 17.7 (8–34) | 23 of 24 | other_session 7.0, judas_reversal 6.1, internal_rotation 3.4, single_extended 0.5, extension_reaction 0.3, single_purged 0.2, judas_outbound 0.1 |
| Jumbo + Judas raids confined to 09:00–10:15 (TBR p.8) | 17.3 (8–34) | 23 of 24 | other_session 7.0, judas_reversal 5.7, internal_rotation 3.4, single_extended 0.5, extension_reaction 0.3, single_purged 0.2, judas_outbound 0.1 |
| Green Bird, pass 8 | 50.5 (8–72) | 13 of 16 | nyam_box 14.5, previous_hour 14.0, prior_day 4.8, london_box 4.2, asia_tdo_case 3.1, golden_pocket 3.1, cash_open 2.7, prior_week 2.5, asia_box 1.8 |
| Green Bird + a running edge is one line | 46.8 (8–61) | 14 of 16 | previous_hour 14.2, nyam_box 12.3, prior_day 4.8, asia_tdo_case 3.1, golden_pocket 3.1, cash_open 2.7, prior_week 2.5, london_box 2.4, asia_box 1.8 |
| Green Bird + his rules: last completed hour (GB p.1), closed 9–10 box (p.5), overnight bias (pp.9–11), one post-open re-entry | 37.9 (8–57) | 13 of 16 | previous_hour 9.8, nyam_box 9.2, prior_day 4.2, asia_tdo_case 3.1, cash_open 2.8, golden_pocket 2.6, london_box 2.4, prior_week 2.1, asia_box 1.8 |

The two Green Bird entries outside the list in the last row are the ones his own rules exclude or the tape cannot print: 2025-11-20 (MNQ level, §3) and 2026-04-28 09:45 (his documented mistake, GB p.5); 2025-11-19 dropped out of that row through a coding slip in the post-open re-entry (it must ride the last overnight cycle that failed, not the last cycle), fixed and being re-counted. The author takes one to three trades a day; the framework admits 17 (Jumbo) and roughly 35 (Green Bird) after his stated rules. The remaining multiplier is mechanical breadth he prunes by grading ("you're always scoring and rating a setup", GB p.4; "context - location - confirmation", JR p.33): which of the drawn levels' failures he takes when several occur, and which edge of the 6–9 he takes first.

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
