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

## 5. Per-day, per-play opportunity table

Filled from `opps_jj.json` / `opps_gb.json` (uncapped candidate lists) when the runs complete; see the addendum at the end of this file.

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
