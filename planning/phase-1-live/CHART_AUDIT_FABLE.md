# CHART_AUDIT_FABLE.md — Phase 1 chart and source audit (Fable pass, 2026-09-11)

Audit only. Not a new plan, not Phase 2. `CHART_AUDIT.md`, `FORMULAS.md` and `RULES.md` are unchanged; every correction lives in the specs of this file (§5). Canvases, traces and the source crops used as evidence live under `implementation/reports/phase1-live/chart-audit-fable/`.

Precedence used everywhere: the raw sets `sources/x-raw-2026-09-11/` (Jumbo v2 archive + media zip, `greenbirdtrader-complete.pdf`) beat `FIND`, `PACK`, `XF` and the GB distillation; a figure beats the prose that describes it; a dated author chart beats a reconstruction. Where `FORMULAS.md` disagrees with them, the row says so.

## 1. What was read and viewed

- **Jumbo raw (v2).** `JJumboFX_Raw_X_Archive_v2.pdf`: every page rendered and every embedded image opened with its tweet text; quadrant crops (763 across the Jumbo/GB sets) and 2–4× zooms where labels were small. `JJumboFX_media_v2.zip`: unzipped next to the PDF; 45 stills (36 missed images + 9 video frames) and 2 mp4 files; every still opened; zip images were used only to zoom figures already identified in the archive.
- **Green Bird.** `greenbirdtrader-complete.pdf`: every chart and its post opened; boxes, labels, tickets read.
- **Every other cited PDF** (39 tags: TBR, SS, FIND, XF, AMT1, AMTL, MAMT, MATH, TPO, VP2, RTVP, FP8, FP9, VWAP, DOM5–7, ABS, STOP, RD, WIC, TRAP, BIG, OFM, REF, NYAM, K18, K2345, K10, ANAT, CONT, AVG, DATA, EMO, GEX, VIX4, C1–C3): full text of every page read; every embedded figure of 500 px or more opened (smaller ones are logos, buttons and page frames); zoom crops for tables, tickets, settings panes and axis labels. Figures under 500 px carry no price geometry.
- **Pine.** Every line range cited by R-P01–R-P20, plus MVFL and OSF, read at the cited lines and the helper functions they call.
- **Code.** `recipe_score.py` (catalog + `_preds`), `family_recipes.py`, `family_levels.py`, `family_fail.py`, `family_tape.py`, `family_gap.py`, `formulas.py`, `formulas_jumbo.py`, `formulas_flow.py` (functions used by the flags), `sessions.py`, `grid.py`, `clocks.py`.
- **Data checks against author prices** (our NQ 1-minute bars, ET): 6–9 box on 14 Oct 2025, 2 Jan 2026, 2 Sep 2026; PDH/PDL/TDO on 27 Aug, 28 Aug, 1 Sep 2026, 20 Aug 2026, 19–20 Nov 2025; ONH on 28 Aug 2026; EVRange on 28 Aug, 1 Sep, 2 Sep 2026; NYAM session identified as 14 Jul 2026; STOP clip as 15 Jul 2026 overnight; GB "13 Jul" Asia chart = trade date 14 Jul 2026. Details in §2 and §3. Re-check of the cannot-tell ids (11 Sep 2026): 6–9 boxes on 24 Sep 2025, 8 Jun, 16 Jul, 21 Jul, 23 Jul and 27 Jul 2026 against his printed lines; 27 Jul ticket fills; NWOG Mondays 27 Jul, 3 Aug (MBP-1 tape) and 17 Aug 2026.
- **Canvases.** 105 ids × 2 cases = 210 PNG canvases plus JSON traces in `implementation/reports/phase1-live/chart-audit-fable/plots/`, one family per canvas (Jumbo, GB, AMT, flow, regime, Sires, Pine never overlaid). Case A = a session the author's own chart shows when it lies in slice F, else the first code-positive session; case B = the opposite scorer result (a same-result fallback is labelled). Blocked ids (R-F02, R-F07, R-R04, R-P18) are drawn from their retained diagnostic flag and titled BLOCKED. Index: `chart_cases.json`, `plot_results.json`, `scorer_fire_dates.json`; tool `implementation/tools/chart_audit_fable_plots.py` (reuses the family drawing of `chart_audit_plots.py`).
- **Not possible.** The EVRange, P-zone and SessionStat minimum-average formulas are unpublished; they are specified from their printed settings and dated prices, never guessed. GB Asia/NY charts dated after 2 Sep 2026 are outside our bars.

## 2. Labels and settings the sources print that the recipes never named

| label / setting as printed | where | what it is | in our code? | ids |
|---|---|---|---|---|
| green line = **range open**, blue line = **range close** | Jumbo TV charts 2025 (30 Jan, 1 Oct 2025) | first print 06:00 and last print 08:59 of the 6–9 box | range open partly (`open`), range close never | J01–J05, J12 |
| 2026 colours: NT 16 Jul green line = 06:00 open 29,530.25; TradingView 21 Jul green line labelled "EQ" and a thick blue line ≈29,154.4 = our 06:00 open 29,155.25 (08:59 close 29,171.50); 24 Sep 2025 TV green line ≈24,905.5 = 06:00 open 24,905.75 | 2025–2026 charts | colours change by platform and version: identify the range open by value, not colour | range open partly | J05 |
| TV 21 Jul 2026 "D-2 High [Thu]" ≈29,219.9; the line ends at 09:29; NT 27 Jul London-low line cut at ≈07:30 ET; H1 = London high 28,763.25, L2 = Asia low 28,500.00 (27 Jul) | 21 / 27 Jul 2026 | D-2 = the full-session high of two sessions back (our 17 Jul session high 29,220.00, printed Thu 18:04, hence [Thu]); lines stop where price takes them (our 09:29 high 29,225.00) = deleted once purged | no | J04, J10 |
| three dotted lines 0.1 / 0.2 / 0.3·W beyond each edge | 29 May, 1 Apr 2025 charts (pixel-checked) | mean-reversal ladder, both sides | yes (`mr01..03`), both sides | J01, J02, J18, J22 |
| **"0.33, 0.66, 1.33, 1.66, 2.33, 2.66"**, ".33 .66 Levels Color + Shading ✓", "Projections Direction: Both" | SDRange+² video frames (28 Dec 2025); 30 Dec 2025, 24 Feb 2026 charts | post-Dec-2025 ladder adds ±0.33 / ±0.66 (shaded) and ±2.33 / ±2.66, beyond the edge in W | no (no 0.33/0.66/2.33/2.66) | J01, J08, J23 |
| shaded **1.33–1.66 band** | 14 Oct 2025, 9 Sep 2025, TBR p.21 | the retracement/reversal AREA | levels only, band partly | J08, J09 |
| "Range Projection Performance Summary … 3,753 sessions 2010-06-07→2025-01-21: 1.33x Daily High Captured 88.2%, Low 65.6%; 1.66x 92.4% / 66.8%" | 12 Sep 2025 chart | printed claim; "captured" undefined | no | J08 |
| "Histogram of Reversal Times (9-12 window)", "Overall Reversal Percentage = 86.46%", "Average Reversal Time (Original Range) = 09:47:36; (Extended Range) = 09:51:05", "4537 days" | 30 Jan 2025 console, TBR p.30 | tallest bar at ≈9.6–9.7 decimal hours (≈09:36–09:42) | no | J01, J02, J20 |
| per-depth bars "Reversal % by Projection" lower ≈87 / 82.5 / 78 / 70.5, upper ≈85.5 / 80.5 / 74.5 / 66.5 at 0.1 / 0.2 / 0.3 / 0.5 | TBR p.30 | per-touch reversal share, pooled across sessions | no | J01 |
| break table by width "0-0.3% n1034 double 55.5 … 1.2%+ n169 17.8; ALL n3249 44.8 / 28.0 / 26.1 / 1.1" | 8 Jun 2026 (XF p.24 image, now read) | path-class shares by `w.pct` | classes yes, table no | J07 |
| open-location table "Below VAL, in range n396: HIGH only 29.5 / LOW only 37.6 / BOTH 29.8 / ONE side 67.2"; "Below VAL & below PDL n517: 23.6 / 46.2 / 27.3 / 69.8" (09:30–10:30) | 8 Jun 2026 (XF p.11 image, now read) | path class by open cell, 09:30–10:30 window | cells yes, window no | J06 |
| retrace table "09:00-10:00 n2043 →High 66.2 →Open 86.8 →EQ 92.8; 10:00-11:00 n1955 51.5 / 76.3 / 85.5; 11:00-12:00 n1751 35.4 / 62.3 / 75.2" | 2 Jan 2026 chart | after a LOW sweep in that hour: retrace to the range high / range open / EQ | no | J05, J12 |
| "P-ZONES: Learning window (sessions) 500; Percentile scaling ✓; Delete invalidated zones ✓; T1/T2 green, T3/T4 red; S1 09:00-18:00, S2 10:00-18:00, S3 02:00-18:00"; table "NQ! 0.42% 09:00 09:50 02:00"; NT "S1: 15:30 NY S2: 09:50 NY S3: 02:00 NY" | SDRange+² frames, 4 Nov 2025 sheet, 20 May 2026 NT | P-zone boxes ≈5–8 pts tall at H±/L±, anchored at session opens; **invalidated zones are deleted** | band [p50,p75] ≈70–80 pts from 09:30 | J12 |
| **H1 / L1** (London, S1 02:00–07:05 in v2; 03:00–07:00 in the manual), **H2 / L2** (Asia, S2 18:00–00:05 in v2; 20:00–00:00 manual), **"D-1 / D-2 / D-3 High/Low [weekday]"** (3-day lookback pivots) | SDRange+² liquidity map, 25 Nov 2025, 30 Dec 2025, 2 Jan 2026 charts | time-based liquidity lines, **deleted once purged** (TBR p.11) | Asia 20–00 / London 00–03 H/L, no D-1..D-3, no deletion | J10, J04, J06 |
| London TBR box: internals start at a dotted **02:00** vertical; dashed "03:00am" and "06:00am" verticals; HIGH/LOW lines start ≈20:00 | 6/7/8/13 Oct 2025 London charts | London box build ≈20:00→02:00, action from 02:00/03:00, handoff 06:00 | box 00:00–03:00 | J09 |
| SessionStat+: "Type Daily, Lookback 60, Average Type Simple"; "Avg/Med Box? ✓", "Show Midpoint Line? ✓"; "Upper/Lower Expansion 0.5" → "+MEH S / −MEL S"; "Show Min Avg Shading ✓"; tables "Exp Avg / Dist Avg / Min Avg / Sample Count 60" | SS p.4–5, p.9; 23 May 2025 London H4; 9 Sep 2025 | each level is a BOX between median and average (dotted midline), plus ±0.5 expansion lines; Min Avg < both averages (40.74 vs 74.53 / 65.55) | one line (mean) per side; min avg = min(mean_up, mean_dn) | J11 |
| **EVRange** upper/lower lines, "EVRange +50%" / "+60%" | 28 Aug, 1 Sep, 2 Sep 2026 NT | expected AM range; estimator unpublished | 09:30 open ± 60-session mean excursion (does not match his prices) | J13 |
| Absorption Zone+ "Body Size Threshold (as % of range) 0.6; Volume Multiplier 1.5; Show box ☐"; "14-period volume average" | TBR p.35 settings | absorption candle constants **are printed** | body ≤ 0.3, k = 2.5 | J14 |
| PD RTH Range+: "RTH HIGH / RTH LOW", red dashed EQ, grey box labelled **"15"** | 1 Apr 2025 (15M) | first-presented M15 imbalance box | no | J19 |
| MGILevels: **PDH / PDL** and separately **pRTHH / pRTHL**, pRTHVAH / pRTHVAL, pdVAH / pdVAL, POC, RTHop, ORH / ORM / ORL (15m OR), "DRH / DRL" | NT charts May–Jul 2026 | full-session PDH/PDL are a different object from prior-RTH H/L | only prior-RTH H/L | J06, J19, G01, G08, G09 |
| GB labels **AS.L, LO.L, NYAM.L, NYL.L**, **PWH / PWL**, NWOG two lines, TDO line, green 09:00–10:00 box, grey 10:00–11:00 box, pink Asia 20:00–00:00, pink London ≈02:00–05:00 | GB charts 2025–2026 | session lows/highs as targets; weekly extremes | AS/LO boxes yes, PWH/PWL no | G01–G11 |
| GB tickets: stop just beyond the sweep wick (17.75, 34.50, 32.50, 19.25, 49.75 pts), buy/sell-limit ladders 20–40 pts apart to the target | GB 2025–2026 | exit geometry | no | G01–G07 |
| AMT1 p.4 "80% Chance of returning to this VAH (balance extreme)" arrow from a poke into the older balance to the FAR edge; VA drawn as a band with a dashed midline | AMT1 p.4–5 | far-edge target; value area as a band | A06 targets the near edge | A01, A03, A06 |
| TPO figures with letters past M (to X, Y, Z, "#") and repeating cycles | TPO p.4–7 | full-session or multi-day TPO, while the text starts A at 09:30 | RTH only | A14 |
| VP2: HVN and LVN both drawn as BANDS; "Shelfs" = thin bands at volume steps; "Ledge" = red/blue lines, four around the POC | VP2 p.3–5 | node geometry | single-price nodes | A02, A16, A17 |
| VWAP p.3 hand labels "−2" on the UPPER band, "+2" on the LOWER band | VWAP p.3 | the author's sign convention is inverted | not relevant to code | F01 |
| OFM schematics: catalyst BOX across three absorbed buy circles; "REFILL clock: AGGRESSIVE (NO RESULT) to AGGRESSIVE (WITH RESULT)"; main "Entry" at the edge of the failure rectangle; "SL → Below aggression" | OFM p.4–6 | the OFM entry is the re-squeeze at the failure area | no | F15, F18, S03 |
| DeepCharts "Speed of Tape (10)", "SD+1 / SD+2" on the price axis, "OFM" line, grey bands between white lines | NYAM, STOP, K18, CONT | levels are bands; tape speed window "10" (unit unstated) | no | S01–S08 |
| GEXRADAR "P: Max Pain", "GFlip", "Call Wall ▲▲▲", "Vol Trig", **"Mom Trigger"** | GEX p.7 | Mom Trigger is a fifth marker the text never names | no | R01 |
| K10 p.8 ticket "BUY 2 \| R:R 9.60", −$500 \| 20 ticks, +$4,800 \| 192 ticks | K10 p.8 | FORMULAS records "R:R 1.00" for this ticket | n/a | S06 |

## 3. Hidden rules the figures and text imply (folded into the specs)

1. **A reference level lives only until it is taken.** TBR p.11 prints "deleted once purged"; SDRange+² prints "Delete invalidated zones ✓"; FIND p.5 "Lines stay until purged". An Asia high or low that London trades through is no longer a draw in New York; a PDH taken overnight stops being a Jumbo draw (TBR p.34 keeps the *RTH* extreme for PD RTH Range+ because ETH is ignored there — that is the only exception). Every level ledger in §5 carries `born_at`, `taken_at`, and is used only while `taken_at` is empty. Applies to J01, J04, J06, J10, J12, G01–G02, G08–G09, A06, A13, A14, P06.
2. **The sweep that counts is of a FINISHED box.** GB: "After midnight the box is finished; the trade is sweep-and-fail of that finished box"; NYAM after 10:00 only; Jumbo "only enter after open". A poke during the build is part of the box, not a sweep.
3. **Green Bird PDH/PDL are full-session extremes.** His printed PDH/PDL match our prior 18:00→17:00 high/low within 0.75–3.5 pts on 27 Aug, 28 Aug, 1 Sep 2026 and 19 Nov 2025, and miss the prior-RTH values by 4–85 pts. MGILevels prints PDH/PDL beside pRTHH/pRTHL, so Jumbo also separates them.
4. **An Asia chart belongs to the next trade date.** GB's "13 Jul" Asia chart is the 14 Jul 2026 session (20:00–00:00 of 13 Jul). Our session key already works this way; the author-date list had to be moved.
5. **">" in Jumbo's tweets is a path arrow**, not an inequality: "P-zone, low > range open" (2 Jan 2026) = long at the P-zone under the low, target the range open (hit 09:32); "10 am p-zone > london low" = short from the 10:00 P-zone to the London low; "Range open > 9:40-9:50" (1 Oct 2025) = range-open tap first, reversal in the window second.
6. **The Judas reversal can start at the swept edge itself.** The "textbook" 13 Oct 2025 day swept the 6–9 low by ≈5 pts (0.03·W) inside 09:40–09:50 and reversed to +0.5 by 13:00; the ladder levels are deeper candidates, not a requirement.
7. **The 86.46% and the p.30 bars are per-touch shares pooled over both sides and 4,537 days**, not a per-session probability; the tallest reversal-time bar sits at ≈09:36–09:42, partly before the 09:40 window.
8. **SessionStat levels are boxes.** Box = [open + median, open + average] above and [open − average, open − median] below, a dotted midline, and ±0.5 expansion lines (+MEH / −MEL) at 0.5 × (upper − lower) beyond; the minimum average is smaller than both averages (reading consistent with the table: average over sessions of the smaller of the two excursions; not printed).
9. **Absorption candle constants are printed** (0.6 body share, 1.5 × a 14-period volume average). The indicator's average runs continuously on the chart timeframe; our AM reset makes 09:30–10:12 unflaggable on 3-minute bars.
10. **P-zones are thin boxes at the range edges, anchored at session opens (09:00 / 09:50 or 10:00 / 02:00, or 15:30 on NT), learned over 500 sessions with percentile scaling, and deleted when invalidated.** They are never a 70–80-point band.
11. **The London TBR box closes at 02:00.** Action starts 02:00–03:00, handoff at 06:00; the 00:00–03:00 box is not his.
12. **Post-December-2025 ladders add 0.33 / 0.66 and 2.33 / 2.66** (shaded 0.33–0.66 like 1.33–1.66); NT 2026 charts are on the UK clock (ET = chart − 5 h) and plot MNQ SEP26, so their BigTrades bubbles and footprint volumes are MNQ sizes, not NQ MBP-1 prints (§4 R-J15, R-J16); DeepCharts stamps are ET (STOP 15 Jul 2026 01:01 = our 01:00 ET bars).
13. **GB invalidation sits just beyond the sweep wick and targets are the opposite edge / AS.L / PDL / NWOG with limit ladders**; A+ = sweep **plus** fail-back of the traded range; he closes at NWOG tag and locks out by ≈10:00 on NWOG Mondays.
14. **Sires/Saint levels are bands, and the re-entry is live only while price is back inside the same band** (ANAT p.7); a first touch of a fresh zone is the weakest (REF p.16, K18 p.7); trades only after the level is defended a second time (K18 p.14).
15. **Value from today is lagging; previous-day value is fixed** (MAMT p.4, ABS p.7): any intraday VAH/VAL must be computed as-of the bar (developing), never from the 16:00 profile.
16. **Directional tables are per condition.** The Pine files print rates per hour, per side, per open location, per pattern; pooling them into one rate (P01, P02, P06, P09) changes the claim.

## 4. Verdict table (105 section B ids)

Values: yes / no / blocked / cannot-tell / gap. `source_ok` = RULES.md + FORMULAS.md read the source faithfully (v2 wins); `code_ok` = the retained function computes that faithful procedure; `score_event_ok` = the scored predicate is the source event (a presence flag, a pooled table or a saturated touch is not); `chart_ok` = our implemented geometry sits where the author (or the Pine script) draws it. "A" / "B" are the two canvases in `implementation/reports/phase1-live/chart-audit-fable/plots/<id>-<case>-<date>.png`; "code T/F" is the current scorer result on that date. Prices are NQ, times ET.

| id | source_ok | code_ok | score_event_ok | chart_ok | evidence |
|---|---|---|---|---|---|
| R-J01 | no | no | no | yes | A 2025-10-14 code T: our 6–9 H 24,665.00 / L 24,502.50 vs his ≈24,660 / 24,500; −0.5 low 24,421.25 touched 09:45; his chart runs to +1.33/+1.66 by 12:30–15:00. B 2025-10-01 code F: his range-open tap 09:32, rally through H into the mr/+0.5 area (our mr01–03 high 24,813.88–24,830.62, +0.5 24,847.38) and reversal in the window — missed. His "textbook" 2025-10-13 reversed at the swept L itself (≈0.03·W), which RULES/FORMULAS call a different object. `j01_ladder` picks the deepest level from the whole-AM extreme (lookahead). |
| R-J02 | yes | no | no | yes | A 2025-10-14 T, B 2024-01-04 F. `open_to_m05_before_0940` fires on any ladder level (0.1·W and deeper) in 09:30–09:40 on either side while the catalog says −0.5; rate 0.28 is a reach of a 0.1·W line. TBR p.9–10 draw trade #1 into the mr/±0.5 area on the side the open leg runs. |
| R-J03 | yes | no | no | yes | A 2026-07-27 F (low broken at 09:30, retrace peaked ≈28,603, EQ 28,693.62 never retested), B 2026-07-16 F. `midretrace_hold_1000` is false on all 647 sessions: `formulas.py::midretrace_hold` starts the h=15 hold at the EQ-touch bar, whose close sits at or through EQ by construction, so `grid.py::hold_after_break` returns on the first bar. EQ / quadrants are where TBR p.12 draws. |
| R-J04 | no | no | yes | no | A 2026-07-28 F: our Asia 28,195.00 / 27,932.50 (20–00) and London 28,049.25 / 27,839.50 (00–03); his liquidity map draws London H1/L1 over 02:00–07:05 and Asia H2/L2 over 18:00–00:05 (v2 settings), and he called 28 Jul a one-way discard day. B 2024-01-16 T. Reach of 1.0 after a purged single break is the right outcome; the purged test runs on the wrong windows. |
| R-J05 | no | no | no | yes | A 2026-07-27 F: NT chart on the UK clock (ET = chart − 5 h); his R-Hi ≈28,759 / EQ ≈28,693.8 / R-Lo ≈28,628.9 = our 28,758.00 / 28,693.62 / 28,629.25. "Sell 5 @ 28,685.75" fills in our 09:00 bar (H 28,700.00 tags EQ), 25 min before the low break (09:25 close 28,627.00); add "Entry @ 28,578.00" (the MGILevels pRTHVAH) at 09:30–09:31; cover "Buy 3 @ 28,503.75" at L2 = Asia low 28,500.00 (the Sunday 18:00 open; our 09:33 low 28,487.00); H1 = London high 28,763.25; the high side stays untouched to 12:00. FORMULAS reads "range mid provided the entry area" as a retrace after the break; on the chart the mid entry comes first. B 2026-07-16 T: his MNQ box R-Hi ≈29,562 / R-Lo ≈29,354 vs our 29,561.25 / 29,361.00 (the 07:49 spike bar: his MNQ wick 7 pts deeper); green line = range open 29,530.25, tagged 09:30–09:32 and rejected (his sells 29,451.50 / 29,438.00, cover 29,312.25 at 09:45); low break 09:41 (close 29,350.50); "retracement-to-mid from the lows" = EQ 29,461.12 and 15m OR mid 29,420.25, both reached by 10:16. Predicate = any later EQ touch on the 09:30–12:00 path; the OP and OR-mid rows and the v2 table are not scored. |
| R-J06 | yes | no | no | no | A 2026-07-10 F: his MGILevels pRTHVAL 29,795 / pRTHVAH 29,985 vs our prior VAL 29,823.00 / VAH 29,986.25 (VAL 28 pts off); open 29,834.75 inside → his "expected mean reversion day". B 2024-02-02 T. The v2 open-location table uses 09:30–10:30; our path class uses 09:30–12:00. |
| R-J07 | yes | no | no | yes | A 2026-06-08 F (width 1.15%, bin 0.8–1.2), B 2024-01-10 T. Predicate = pooled double-break share 0.34 while the claim is by width bin (v2 8 Jun 2026 table: double 55.5% at 0–0.3% down to 17.8% at 1.2%+, ALL 44.8%); his table is labelled "9-12 window", ours is 09:30–12:00. Box geometry matches his dated boxes. |
| R-J08 | no | no | no | yes | A 2025-09-09 F: our −1.33/−1.66 band 23,747.24–23,731.24; his circled reversal inside that band at 10:45 ("confluences with the RTH session averages at the lows"). The code scores 13:00–16:00 only, so it misses his own example; FORMULAS also restricts to PM. B 2024-02-27 T. |
| R-J09 | no | no | no | no | A 2025-10-08 F: our London box 00:00–03:00 (L 25,026.25); his box internals start at a dotted 02:00 vertical with HIGH/LOW lines from ≈20:00, a 03:05 wick below LOW (25,028) then a rally to 75% — a reversal at the edge the code does not score. B 2025-10-06 T. |
| R-J10 | no | no | no | no | A 2025-12-30 T: our Asia 25,752.50 / 25,696.75, London 25,755.00 / 25,684.75 (00–03); his H1/L1 (02:00–07:05), H2/L2 (18:00–00:05) and "D-1 Low [Sun]" lines with "textbook longs after 9:40 to London/Asia highs". D-1..D-3 pivots and the "10am expansion to Daily high" (9 Jan 2026: D-1 High [Wed] 25,850, sell limit 25,846.50) are absent. B 2024-01-03 F. |
| R-J11 | no | no | no | no | A 2025-09-09 T: our lines ss_hi 23,931.16 / ss_lo 23,742.55 from the 09:00 open; SessionStat draws Avg/Med boxes with a dotted midline (SS p.4, p.9; his 9 Sep RTH LOW box 23,735–23,765). London H4 table Min Avg 40.74 < Exp 74.53 and Dist 65.55 falsifies min(mean_up, mean_dn). Event scored = reach of a mean line (0.75); his event = reaction at the box / ±0.5 / 1.33–1.66 coincidence (6 Jul 2026: HIGH box 30,040–30,080 on +1.33/+1.66). B 2024-01-10 F. |
| R-J12 | no | no | no | no | A 2026-01-02 F: our 6–9 H 25,742.75 / L 25,679.25 / range open 25,730.25 / EQ 25,711.00 equal his 25,743 / 25,680 / 25,730 / 25,712; his P-zone boxes 25,760–65 / 25,720–25 / 25,660–65 / 25,620–25 (5 pts tall) vs our T1 bands 25,762.75–25,831.50 and 25,526.75–25,607.75; his long 09:22 from the box under L to the range open at 09:32 ("low > range open" = path). B 2024-10-18 T. |
| R-J13 | no | no | no | no | A 2026-08-28 T: our EV 29,784.39 / 29,399.65 (mean60) and 29,757.62 / 29,444.88 (median60) vs his EVRange sell limit 29,724.50 beside ONH 29,707.25 (our ONH 29,707.00). 2026-09-02: his 29,115 / 28,870 vs ours 29,253.40 / 28,864.29; 2026-09-01: his lower-EVRange buy 29,074.25 at ≈09:40 vs ours 28,870.81. Predicate = in-value and reach (0.24); his use is a fade at the line toward EQ. B 2024-01-03 F. |
| R-J14 | no | no | no | no | A 2026-01-09 F: his "9am P-zone" 25,657–25,663 on our −0.5 25,664.25 with "Absoprtion" markers at 09:05 high and 09:33 low; the code's AM-reset trailing SMA14 on 3m bars has no baseline before 10:12, and uses body ≤ 0.3, k = 2.5 against the printed 0.6 / 1.5 (TBR p.35). B 2024-02-29 T. |
| R-J15 | yes | no | no | no | A 2026-07-23 F: NT chart (UK clock); his R-Lo ≈28,754 = our L 28,754.75. He boxes ≈28,656–28,672 around 714- and 213-lot buy bubbles at ≈28,664.5 (10:48 ET; "1000+ lots dunked on"), then price falls to ≈28,484 by 11:15. The box is not a TBR level (it sits between −0.2·W 28,681.25 and −0.3·W 28,644.50), and our flag tests only EQ and ±0.5. His bubble sizes are not our NQ prints: the largest NQ print in 28,655–28,672 over 10:30–11:00 is 39 lots; on 19 May 2026 (header "NQ |") he shows 162 / 174 against our largest RTH print of 84; the 16 and 27 Jul bubbles (450, 325, 213, 117) are absent from our tape; the July charts' series is "MNQ SEP26 (1 Minute)". So the ≥ 100 / ≥ 75 population is MNQ prints or aggregated orders (measurement deferred). Thresholds 100 NY / 75 London match XF p.25; the flag's London is 02:00–05:00, his 02:00–07:05. B 2024-01-05 T. |
| R-J16 | yes | no | no | no | A 2026-06-08 F: NT chart (UK clock); his R-Hi ≈29,511.7 / EQ ≈29,343.0 / R-Lo ≈29,175.2 = our 29,510.50 / 29,342.75 / 29,175.00. He draws a teal band ≈29,334.6–29,359.8 across the EQ from the 10:00–10:01 bars (our 10:00 low 29,331.50, 11.25 pts under EQ; 10:01 close 29,400.50), and a 302 bubble marks the 10:04–10:05 retest (our low 29,348.50). His 2-minute footprint (the 10:00–10:01 candle = our H 29,409.00 / L 29,331.50) boxes negative-delta rows 29,338–29,350 and thin rows at the low (the "taper"). Our window (EQ ±2 ticks, excursion ≤ 2 ticks) excludes his probe; no 35% filter. His footprint is MNQ (candle volume 22,631 vs our NQ 5,844 for those 2 minutes). B 2024-01-04 T. |
| R-J17 | no | no | no | yes | A 2026-06-08 T: code LVN 29,342.50 under EQ 29,342.75. Our 06:00–09:00 profile is thin across 29,332.5–29,345 (78–158 lots per 2.5-pt block vs a 289.5 median), and his 8 Jun band (≈29,334.6–29,359.8) sits on that slot and on the thin lower tail of his RTH session profile, so the location matches. Source: FORMULAS rests on FIND p.7–8 and cites "range profile*". That correction belongs to the 24 Sep 2025 post, where the range profile is a shape classifier ("Range Profile: Profile Type b, Direction Bearish"; our box 24,913.50 / 24,869.50 = his HIGH / LOW; single break low to the −1.33/−1.66 band 24,810.98 / 24,796.46, where he covers 2 @ 24,820.00). The profile on his charts is the RTH session VP (16 Jul 2026 reply), which FORMULAS lists as a different object. Predicate is presence; level set EQ / ±0.5 only. B 2024-01-03 F. |
| R-J18 | yes | no | no | yes | A 2025-10-14 F: his −0.5 reversal at 09:45; no OB detected at ±0.5 by the 3m scan. B 2024-01-23 T: C2 17,409.50–17,444.25 at m05_low 17,410.00. Only ±0.5 is tested (no mr ladder, band, P-zone, 2m/5m, rejection block). |
| R-J19 | yes | no | yes | yes | A 2025-04-01 T: our prior RTH H 19,489.75 / L 18,976.75 vs his RTH HIGH 19,490 / LOW 18,985 and EQ 19,240 (ours 19,233.25); his grey "15" box 19,300–19,325 (first-presented M15 imbalance) is not built. B 2025-10-03 F. |
| R-J20 | yes | no | no | yes | A 2024-01-03 T (JOLTS/ISM 10:00 day; first −0.5 touch 10:17 in bin 10:00–10:30), B 2024-01-04 F. The flag times the first −0.5 touch, not the reversal TBR p.18 describes. |
| R-J21 | yes | no | no | yes | A 2026-07-10 F: his three sell limits at +1.33 = 30,041.25; our +1.33 = 29,887.75 + 1.33 × 116.50 = 30,042.70. B 2024-02-13 T. `j21_class` is called with `red_folder_0830=False`, so "extended" is `w_rel ≥ 1` only (25 sessions); the scored value is the class share, not the per-class target table. |
| R-J22 | yes | no | no | yes | A 2025-10-13 F (his textbook reversal, correctly not a failure), B 2024-01-05 T. Three-strike only, at the path side's ±0.5, returns measured from the same bar; extended bodies, window violation and volume divergence exist but are not in the predicate. |
| R-J23 | yes | no | no | yes | A 2024-01-03, B 2024-01-04 (predicate is always True). Boxes sit on the eight printed clocks; no ladder beyond ±1.66 and no mr lines on any of them; the scored rate is the midnight box's double-break share only. |
| R-J24 | yes | no | no | yes | A 2025-10-14 T, B 2025-11-06 F; rate 0.997. `j24_mfe_pos` takes the 09:30–09:50 extremes (`first20`), which include prints before the entry, so MFE > 0 almost always. |
| R-J25 | yes | no | no | no | A 2026-01-14 F: his "clean retraces to midpoint of every swing"; our single mid 25,729.25 from the first swing L 25,668.25 and first swing H 25,790.25 found over the whole AM. `j25_mid_hold` is false on all 647 sessions. B 2024-01-03 F. |
| R-G01 | no | no | yes | yes | A 2026-08-28 T: our NYAM H 29,703.25 vs his box high ≈29,700; his short 29,674.25 after the 10:03 sweep to 29,710, stop 29,708.75 = full-session PDH (ours 29,708.00; prior-RTH 29,704.50), target 29,374 toward PDL 29,400 (ours full-session 29,401.75; RTH 29,423.75). B 2024-01-04 F. RULES/FORMULAS use prior-RTH PDH/PDL. Code sweep depth is 0 ticks and the fail-back cap k = 30 is unprinted. |
| R-G02 | yes | no | yes | yes | A 2026-07-14 F: his "13 Jul" Asia chart (trade date 14 Jul): sweep of PDL 29,380 (ours full-session 29,386.50) inside the Asia box at ≈23:20, long 29,414.25 with limits 29,537.50–29,589.75 at the Asia high (ours 29,541.25); the code only looks for sweeps after 00:00 and sees the 01:14 Asia-high sweep with no fail. B 2026-08-12 T. |
| R-G03 | yes | no | no | yes | A 2026-08-27 T: our 10:00 hour H 29,623.50 vs his grey box 29,620; 11:00–11:30 high 29,635.00 vs his sweep to 29,633; TDO 29,538.00 vs 29,540; PDH (full session) 29,437.75 vs 29,440. B 2025-06-09 F. Rate 0.9985: every clock hour 09–14 with a two-hour outcome window, events summed. |
| R-G04 | yes | no | yes | yes | A 2026-08-31 T (09:30 open 29,437.75), B 2024-01-23 F. 5m reclaim is the named confirmation; the "hold on the original side" and the discount target are absent. |
| R-G05 | yes | no | yes | yes | A 2026-08-28 T: our TDO 29,668.00; his short at 29,674.25 labelled True Day Open. B 2026-04-23 F: his TDO 26,900 vs ours 26,906.25. Only the AM window; his Asia-sweep → TDO shorts at 00:30–00:45 (3 and 8 Sep 2026) are outside the flag. |
| R-G06 | yes | no | yes | yes | A 2026-08-17 T: our gap is Friday 15:59 close 30,144.50 → Sunday 18:00 open 30,170.00 (the 16:59 close, 30,154.00, moves only the far edge). His text (posted 10:17 ET): "One short after the New York open. Price swept midnight, failed, draw sitting at the NWOG. Closed when price hit the Weekly Opening Gap." Our 09:31 high 30,266.00 sweeps TDO 30,246.75, the 09:32 close 30,205.50 is back below, and the near edge 30,170.00 (the Sunday open) is tagged at 09:39 (low 30,165.50). 27 Jul: near edge = Sunday open 28,500.00 (also the Asia low and Jumbo's L2), tagged 09:33. The 18:00 bar itself trades into the gap (17 Aug low 30,163.75), so "valid until tagged" must start after price leaves the gap. 3 Aug (from the MBP-1 tape; the 1m index has 0 of 1,380 bars for 3 and 4 Aug 2026): Sunday open 28,565.00, Friday 31 Jul closes 28,402.75 (15:59) / 28,287.00 (16:59); his "Clean short from 28,665" sits at TDO 28,669.00 (first print ≥ 28,665 at 22:13 Sunday); the near edge 28,565.00 is tagged at 03:02, before his 08:21 post; the low before 08:21 is 28,383.50, through the 15:59 far edge but not the 16:59 one. No Monday chart with NWOG lines falls in F (the 8 Sep 2026 lines 29,530.50 / 29,524.75 come after our data ends on 2 Sep). B 2024-01-03 F (not a Monday). |
| R-G07 | yes | no | no | no | A 2026-07-30 F: our pocket 27,934.05–27,977.62 from the NYAM box; his "Golden Pocket" 27,645–27,718. 2026-09-01: his short under the pocket of the ONH→low leg (29,571.25 → 29,040.25, 50% = 29,305.75; his retrace to ≈29,315) vs our NYAM-box pocket ≈29,099–29,113. B 2026-08-12 T. Predicate = touch only. |
| R-G08 | no | no | yes | no | A 2026-07-14 T: overnight low 29,303.50 swept his PDL 29,380 (ours: RTH 29,393.25, full session 29,386.50) and reclaimed. B 2025-11-19 F: his example is a sweep and reclaim of the previous WEEK low (PWL 24,625); no PWL object exists. Reclaim is read from the 09:29 close. |
| R-G09 | no | no | no | no | A 2026-07-27 F: our NWOG 28,283.25 → 28,500.00 (15:59 close), PDH (RTH) 28,630.75, Asia H 28,733.75, London H (00–03) 28,728.50. B 2024-05-20 T. London is 00–03 not 02:00–05:00; no failed-breakout or structure-shift step. |
| R-G10 | yes | no | no | yes | A 2026-08-20 T: his PDL 29,377 = ours 29,375.75; our NYAM H 29,470.25 under his short stop box 29,449–29,473; he fades only the up-pops (red arrows) while the code counts both sides. B 2024-01-03 F. |
| R-G11 | yes | no | no | yes | A 2026-08-28 T, B 2024-01-16 F; rate 0.978. A+ is a property of the traded range; the flag ORs three boxes per session. |
| R-A01 | yes | no | no | yes | A 2024-02-16 T (open 17,926.75 inside VA 17,838.00–17,928.25), B 2024-01-03 F (open below VAL). The inside-balance precondition and POC reach are computed but outside the predicate. AMT1 p.9 draws the extremes as bands. |
| R-A02 | yes | no | no | no | A 2024-01-04 T, B 2024-01-03 F; the fresh producer returns False on A (inconsistent). The ledge is the VA edge picked by the open; VP2 p.5 draws ledges as lines at volume steps, AMT1 p.9 the retest from below after the break. |
| R-A03 | yes | no | yes | yes | A 2024-02-06 T, B 2024-01-03 F. Re-entry → traverse is the claim; only open-outside cases are scored (RTH breakout-then-re-entry missing). AMT1 p.4 arrow to the far edge. |
| R-A04 | yes | no | no | yes | A 2024-04-29 T (open 17,921.50 above VAH 17,894.00), B 2024-01-03 F. Predicate = precondition (closes inside at bars 29 and 59); the traverse is not computed. |
| R-A05 | yes | no | no | yes | A 2024-01-04 T, B 2024-01-03 F. Chop label only; the far/near-edge reach split that is the claim is not scored. |
| R-A06 | yes | no | no | no | A 2024-01-03 T (prior POC 16,700.00 untraded overnight), B 2024-01-04 F. Predicate = naked-POC presence; `a06_failed_auction` targets the near edge; no older-balance POC. AMT1 p.4 / MAMT p.11 target the far edge. |
| R-A07 | yes | no | yes | yes | A 2024-04-09 T (IB 18,270.50–18,405.00), B 2024-01-03 F. Break and retest are searched in the same window; prior VA / ledge boundaries and next-value reach absent. |
| R-A08 | yes | no | no | yes | A 2024-03-25 T, B 2024-01-03 F. Side chosen by the open; the opposite-edge reach is outside the predicate. |
| R-A09 | yes | no | no | yes | A 2024-02-06 T, B 2024-01-03 F. Adds an unprinted 30-minute cap between the two edge closes; continuation share not scored. |
| R-A10 | yes | no | no | yes | A 2024-01-08 T (drive), B 2024-01-03 F. Only "drive" of four open types is scored; no MAMT four-class day label; a label share is not an outcome. |
| R-A11 | yes | no | no | no | A 2024-03-26 T, B 2024-01-03 F; 2 positives in 647. Shape from prior-RTH bar HLC3 volume (not trades); only RTVP's continuation pairing is tested; MAMT's opposite resolution not printed separately. |
| R-A12 | yes | no | no | no | A 2024-01-05 T: code LVN prices 16,449.50 / 16,450.50 / 16,451.50 vs open 16,449.25. MAMT p.14 draws the LVN and the shelf as bands and scores respected / disrespected. B 2024-01-03 F. |
| R-A13 | yes | yes | yes | yes | A 2024-01-03 T (ON 16,591.50–16,737.25), B 2024-04-10 F. ONH-or-ONL touched in RTH is MAMT's 94% claim (0.879 on F). The 73% MPOC row is a separate claim not yet scored. |
| R-A14 | yes | no | no | no | A 2024-01-03 T, B 2024-01-04 T; rate 1.0 by construction (poor ∨ excess ∨ fill on the current RTH). TPO figures print full-session letters. |
| R-A15 | yes | yes | no | yes | A 2024-01-03 T (IB 16,556.50–16,653.50), B 2024-01-04 F. Extension presence (0.80) is not the claim; MAMT p.23's "Closes Above IBH / Below IBL" continuation rows are not scored. |
| R-A16 | yes | no | no | no | A 2024-04-09 T: "ledge" = prior VAL, partner = AM VWAP known at 12:00 (18,278.70). B 2024-01-03 F. |
| R-A17 | yes | no | no | no | A 2024-01-29 T: minimum from the current session's RTH profile known at 16:00 (17,636.75). B 2024-01-03 F. |
| R-A18 | yes | no | no | no | A 2024-01-05 T, B 2024-01-03 F. The producer passes synthetic tick integers as single-print prices; the scored flag is "AM high reaches prior VAH". |
| R-F01 | yes | no | no | no | A 2024-01-04 T, B 2024-01-03 F. ORs the running 18:00 VWAP ±2σ touch with an absorption at the final-AM (noon) trade VWAP band; the source needs touch plus absorption at the band, then median reach. |
| R-F02 | yes | blocked | blocked | blocked | A 2024-01-03 (`f02_divergence` true), B 2024-01-18 (false). CVD trade tape-trusted no. |
| R-F03 | yes | no | no | no | A 2024-04-08 T: AM VWAP (noon) 18,313.40, overnight VWAP 18,311.84, prior VA mid 18,316.62 — stand-ins for session/weekly/swing anchors. B 2024-01-03 F. |
| R-F04 | yes | no | no | no | A 2024-01-03 T: stack zone 16,522.25–16,523.00 found on the full RTH (16:00). B 2024-01-04 F. |
| R-F05 | yes | no | no | no | A 2024-01-03 T: AM treated as one candle (O 16,610.00, C 16,562.25, Δ 10,817), no candle POC flip. B 2024-01-04 F. |
| R-F06 | yes | no | no | yes | A 2024-01-23 T, B 2024-01-03 F. Absorption A at prior VAL/VAH (a DOM6 level type) but its flag already requires the 15-minute reversal, so trigger and outcome are one event. |
| R-F07 | yes | blocked | blocked | blocked | A 2024-11-18 (`iceberg_touch` true), B 2024-11-19 (true; fires 439 of 446 MBP-1 sessions). |
| R-F08 | yes | no | no | no | A 2024-01-03 T: reward origin = first AM trade 16,610.00, no location gate. B 2024-01-05 F. |
| R-F09 | yes | no | no | no | A 2026-07-15 F: STOP p.8–9 overnight NQ clip (01:01 and 03:04 ET; our 01:00–01:05 range 30,001.25–30,058.25); the flag reads first-20 vs last-20 AM print medians (1 vs 1) and is false on all sessions. B 2024-01-03 F. |
| R-F10 | yes | no | no | no | A 2024-01-03 T: "final AM low + 2 ticks" 16,544.50. B 2025-03-28 F; rate 0.9985. RD p.4–5 protected low = confirmed swing low after an escape. |
| R-F11 | yes | no | no | no | A 2024-12-18 T: RTH POC (16:00) 21,322.50 near LVNs 21,315.50–21,330.25; not the delta print, no touch. B 2024-01-03 F. |
| R-F12 | yes | no | no | no | A 2024-01-04 T, B 2024-01-03 F; session-wide first-5 vs last-5 print sizes (1 vs 1), no extreme, rate 0.86. |
| R-F13 | yes | no | no | no | A 2026-07-15 F: STOP p.9 trapped-buyer boxes at the overnight highs (≈30,044–30,056); the flag keys on the 6–9 high in the AM and never fires. B 2024-01-03 F. |
| R-F14 | yes | no | no | no | A 2024-01-05 T: 350% from full-RTH same-price volumes and an unrelated BigTrades flag at a TBR level. B 2024-01-03 F. |
| R-F15 | yes | no | no | no | A 2024-01-03 T, B 2024-01-04 F; alias of F18 (stacked 4× footprint without refill). OFM p.5–6 schematics: catalyst box, failure rectangle, entry at the re-squeeze edge, stop below the aggression. |
| R-F16 | yes | no | no | no | A 2024-01-03 F, B 2024-01-04 F; never fires; top side only, keyed on the 6–9 high. |
| R-F17 | yes | no | no | no | A 2024-04-23 T: ≥100-lot cluster 17,486.25–17,486.75 (2 ticks); REF p.7's NQ zone is a ≈15-pt rectangle built at 09:27–09:29 and retested at 09:40. B 2024-01-03 F. |
| R-F18 | yes | no | no | no | A 2024-01-03 T, B 2024-01-04 F; same flag as F15; no tape-speed release, no no-failure window. |
| R-R01 | yes | no | no | no | A 2024-01-03 T: QQQ spot 400.14, flip 358.00, call wall 402, put wall 400. GEX p.7 / p.15 put the flip beside spot (726.17 vs 731.98); our cumulative-sum flip sits 10% away. dte ≤ 14 at 09:30–09:35 instead of 0DTE pre-open. B 2024-01-10 F. |
| R-R02 | yes | no | no | yes | A 2024-02-14 T, B 2024-01-03 F. Prior-session VIXCLS is the right vintage; bins omit the printed 14 cut; the scored value is a band share, not the realized-range rows. |
| R-R03 | yes | no | yes | yes | A 2024-01-03 T, B 2024-01-04 F. `r_r03_thesis` kills a short label on any AM wick above VAL and sets the death time to 12:00; value shift is off unless passed; news is a calendar flag. |
| R-R04 | yes | blocked | blocked | blocked | A 2024-01-04 (`smt_ohlc` true), B 2024-01-03 (false); canvas shows NQ/ES/YM/RTY returns from each 09:30 open. |
| R-S01 | yes | no | no | no | A 2026-07-14 F (NYAM p.4–5 session): his range-bottom band ≈29,735–29,745, long 29,757.25, stop 29,744.25, target 29,804.25; our prior VAL 29,469.00 / VAH 29,663.50 sit 71–266 pts lower. B 2024-01-23 T. |
| R-S02 | yes | no | no | no | A 2026-07-14 F: his support band ≈29,622–29,633 tested from above three times (10:00–10:14), short 29,608.50 stopped at 29,621.25; our VAL band 29,468.50–29,469.50. Defence volumes are hard-coded 0. B 2024-01-23 T. |
| R-S03 | yes | no | no | no | A 2024-01-03 F, B 2024-01-04 F; flag = F09's thinning (never fires). |
| R-S04 | yes | no | no | no | A 2024-01-03 F, B 2024-01-04 F; never fires. K2345 p.5 prints the 350% box a few points tall at the trapped-seller price. |
| R-S05 | yes | no | no | no | A 2024-01-03 T: "microbalance" = the 09:30–09:40 clock box, last close-run 16,565.50–16,574.00 found at 11:57; rate 0.997. K2345 p.7 draws a ≈7-pt price box under the entry. B 2024-01-04 F. |
| R-S06 | yes | no | no | no | A 2024-01-22 T, B 2024-01-03 F. Single swing high; K10 p.7 draws the reaction area as two lines 7,558.75 / 7,564.00 (ES) and p.8 the long mirror (ticket R:R 9.60, FORMULAS writes 1.00). |
| R-S07 | yes | no | no | no | A 2026-07-23 F (ANAT session): his shelf band ≈28,700–28,707 with "OFM" at its base, nine trades 10:14–10:32; our prior VA 29,131.50–29,287.50 is 400 pts above price; trigger = first AM print. B 2024-01-03 F. |
| R-S08 | yes | no | no | no | A 2024-01-03 F, B 2024-01-04 F; never fires; "delta" inputs are 5m close-minus-open price changes. |
| R-S09 | yes | no | no | no | A 2024-01-17 T with the 09:30 open 16,825.25 BELOW prior VAL 16,876.75: the code's "open above value" compares to its own 09:30–10:00 VAH (16,783.50). AVG p.21–22: the TPO opens fully above yesterday's VAH. B 2024-01-03 F. |
| R-P01 | yes | no | no | yes | A 2024-01-09 T: bands 16,778.89 / 16,667.11 from the 08:00 open 16,723.00; σ from 4 log changes (history starts 2024-01-02) instead of 20 daily % changes; pooled rate 0.61 vs the hour-8 upper claim 78.4% (n 732). B 2024-01-03 F. |
| R-P02 | yes | no | no | yes | A 2024-01-03 T, B 2024-06-20 F; rate 0.98. Only the high-sweep return is effectively scored (operator precedence) and the sweep bar may also be the return bar; per-hour × isAbove tables not built. |
| R-P03 | yes | no | no | yes | A/B 2024-01-03/04 both T (rate 1.0): hour boxes at 23/00/01/02/06/07/08 with mids are drawn right, but break and target times are synthetic (+4 / +20 min). |
| R-P04 | yes | no | no | no | A 2024-01-03 T: NYAM 09:00–10:00 box + 5 pts (16,647.25); the Pine boxes are 02:00–02:15, 09:00–09:15, 13:00–13:15; an unconfirmed raid counts. B 2024-01-11 F. |
| R-P05 | yes | no | no | no | A 2024-01-03 T: London "candle" = 00:00–03:00 box (25% level 16,706.06); the Pine London candle is 02:00–08:00 and NY 08:00–17:00; the predicate counts a fail as a fire. B 2024-01-05 F. |
| R-P06 | yes | no | no | no | A 2024-01-03 T: Asia 20:00–00:00 and London 00:00–03:00; the mapper uses Asia 20:00–02:00, London 02:00–08:00, NY 08:00–16:00 and position vs the midpoint. B 2024-01-23 F. |
| R-P07 | yes | no | no | yes | A 2024-01-03 T (OR5 16,581.50–16,623.75), B 2024-01-08 F. Mid retest scanned to 12:00 (Pine to session end); extreme-first taken after the OR; rates pooled. |
| R-P08 | yes | no | no | yes | A 2024-01-03 T, B 2024-01-04 F. Same predicate as R-A15; no combo key, no 0.1% leave-and-return band, no percentile extensions. |
| R-P09 | yes | yes | no | yes | A 2024-01-03 T (open 16,610.00 below prior RTH L 16,622.50), B 2024-01-05 F. Construction matches the Pine; the predicate ORs three conditional outcomes into one rate. |
| R-P10 | yes | no | no | yes | A 2024-01-05 T (P 16,491.33), B 2024-01-03 F (P 16,797.58). Pivots from the 18:00→17:00 bar are right; the touch is `rth_high ≥ P`, so every open above P counts as a touch. |
| R-P11 | yes | no | no | no | A 2024-01-03 T: 1m FVG 16,601.00–16,609.25 in 09:30–10:00; the Pine uses 5m bars with a close condition and W1/W2 first-presented boxes. B 2024-04-03 F. |
| R-P12 | yes | no | no | no | A 2024-01-10 T: first two 1m RTH candles (16,839.50–16,863.25); the Pine sweeps completed HTF candles. B 2024-01-03 F. |
| R-P13 | yes | yes | yes | yes | A 2024-01-04 T (00:00 open 16,549.00), B 2024-01-03 F (16,695.00). `tdo_touch_ny` = a bar spanning TDO in 08:00–16:00, the Pine window; the overall 73.75% is the mapper's default row. |
| R-P14 | yes | no | no | no | A 2024-01-11 T, B 2024-01-03 F. Flag = first-30-minute high ≥ RTH HOD; the Pine's HOD is the 18:00→17:00 session high with 4H checkpoint states. |
| R-P15 | yes | no | no | no | A 2024-01-04 T, B 2024-01-03 F. Levels = open ± median range with MFE/MAE set to 0.6 / 0.4 of it (invented); the Pine uses nearest-rank percentiles per session window. |
| R-P16 | yes | no | no | yes | A 2024-01-04 T (prior close 16,542.75, log zones), B 2024-01-03 F. VIX stands in for VOLI; whole-session containment is scored while the 75.2% claim is a close inside ±1 SD of another file. |
| R-P17 | yes | no | no | no | A 2024-01-04 T (18:00 open 16,545.25), B 2024-01-03 F. The Pine body/wick profile is not built; the Pine prints no touch rate for the 18:00 open. |
| R-P18 | yes | blocked | blocked | blocked | A 2024-01-04 (`cvd_agree_ohlc` true), B 2024-01-03 (false). |
| R-P19 | yes | no | no | no | A 2024-03-14 T: gap between the first two AM bodies (18,106.00–18,107.25) only; no fill, no 80/20 confluence. B 2024-01-03 F. |
| R-P20 | yes | no | no | no | A 2024-01-03 T (max AM print 276, range 438 ticks), B 2024-01-10 F. No MVFL delta or volume-anomaly zones exist. |

## 5. Implementation specs

Each spec lists: **Wrong now** (code, event, geometry, missing label) · **Procedure** (ET clock, bounds, bars, field, reset, `known_at`, sides) · **Constants** (printed ones only; everything else is marked source-unspecified and carries a named default) · **Invalid** (what makes it a different object) · **Fixture** (typable numbers) · **Files**. Paths: code under `implementation/src/trading_research/research/phase1_live/`, wiki under `planning/phase-1-live/wiki/`, FORMULAS = `planning/phase-1-live/FORMULAS.md` (its block for the id; edit it only in a later pass that is allowed to).

### 5.0 Shared definitions (every spec uses these by name)

- **S-1 Clock and bars.** America/New_York wall time. Session key = NY trade date; session = 18:00 of the prior calendar day → 17:00. QuantPad 1s/1m `t` = UTC ms bar start; MBP-1 `t` = UTC ns; tick = 0.25. Every level carries `known_at` = the end of the window that builds it; every intraday input is computed as-of the bar close (never from a 12:00 or 16:00 aggregate). "Taken" = a print strictly beyond the level (high ≥ level + 1 tick for a high, low ≤ level − 1 tick for a low).
- **S-2 Level ledger with retirement.** One record per level: `name, price, side, window, born_at, taken_at`. `taken_at` = first S-1 "taken" print after `born_at`. A level is valid at time t only if `taken_at` is empty or later than t. Levels: Asia H/L; London H/L; ONH/ONL (18:00–09:30); PDH/PDL = prior **full-session** 18:00→17:00 high/low; pRTHH/pRTHL = prior 09:30–16:00 high/low; D-1/D-2/D-3 High/Low = full-session extremes of the last three sessions; PWH/PWL = prior Sunday 18:00 → Friday 17:00 extremes; TDO = 00:00 1m open; NWOG = [Friday 16:59 1m close, Sunday 18:00 1m open] (15:59 and 17:00 settle are named variants). Windows by family: Jumbo liquidity map London 02:00–07:05, Asia 18:00–00:05 (v2 settings; manual 03:00–07:00 and 20:00–00:00 are named variants); GB Asia 20:00–00:00, London 02:00–05:00. Exception: PD RTH Range+ (R-J19) ignores ETH, so pRTHH/pRTHL retire only on RTH prints.
- **S-3 Jumbo 6–9 box and ladder.** Build 06:00:00–08:59:59 on 1s bars (1m fallback): H, L, W = H − L, EQ = L + W/2, Q25, Q75, range open = first print at/after 06:00, range close = last print before 09:00; `known_at` 09:00. Ladder on BOTH sides, in W beyond the edge: mean-reversal 0.1 / 0.2 / 0.3; 0.33 / 0.66 (shaded band; charts from Dec 2025); 0.5; 1.0; 1.33 / 1.66 (shaded band); 2.0; 2.33 / 2.66; 2.5; 3.0. Edge sweep = first 1m bar after 09:30 that takes H or L (any depth); depth = max excursion beyond that edge in W. Overshoot δ past a level: source-unspecified, named {2 ticks, 0.1·W}.
- **S-4 London TBR box.** Build [20:00 prior day, 02:00) — the 02:00 end is printed by the dotted vertical where the internals start; the start is where his HIGH/LOW lines begin (≈20:00; minute source-unspecified, named 20:00). Action window 02:00–06:00, "London open analog" 03:00, handoff 06:00. Same internals and ladder as S-3 in London width.
- **S-5 Green Bird boxes and events.** NYAM 09:00–10:00 (events from 10:00), 10:00–11:00 (from 11:00), previous completed clock hour (events inside the next hour), Asia 20:00–00:00 (from 00:00), London 02:00–05:00 (from 05:00). Sweep of a FINISHED box = first 1m bar after the box end that takes H or L (S-1). Fail-back = first 5m close (buckets aligned to :00/:05) strictly inside (L, H) after the sweep; no printed time cap (named caps 30 / 60 min). Invalidation = a 5m close beyond the sweep extreme (body reading) and, as the named wick variant, any print beyond it. Targets in order: opposite box edge, AS.L / LO.L, PDH/PDL (S-2 full session), NWOG.
- **S-6 Grid.** Touch t2 = a 1m bar within 2 ticks of the level; `b.c1` / `b.c5` = 1m / 5m close beyond; reject(r, k) = after the touch, a 1m close ≥ r·R back on the original side within k minutes with no `b.c1` first; hold(h) = every 1m close beyond the level for h minutes **starting with the bar after the event bar**; defaults r = 0.5, k = 15, h = 30 (grid values, not printed).
- **S-7 Profiles.** Prior RTH trade profile (MBP-1 prints 09:30–16:00, 1-tick bins, POC = max bin, VA = 70% expanded toward the heavier neighbour), fixed at 16:00. Developing profile = same construction as-of each bar. Overnight profile = prints 18:00–09:30. HVN, LVN, shelf and value area are **bands** (VP2 p.3–5, MAMT p.14); a ledge is a **line** at a volume step (VP2 p.5). Node thresholds (1.5× / 0.5× median, 3× step) are named defaults, not printed.
- **S-8 Tape.** MBP-1 trades with aggressor side; delta = Σ buy − Σ sell; blocked objects (CVD trade, SMT, absorption B, bigtrade q90) stay blocked by `FINDINGS.md`.
- **S-9 Scoring.** Print per side and per condition cell; never OR conditional outcomes into one rate; outcomes run from the event's `known_at`; a presence flag is a denominator, not a result.

### 5.1 Jumbo

**R-J01 — Judas reversal, trade #2**
- Wrong now: `family_recipes.py` sets `j01_ladder` from the deepest ladder level reached by the whole-AM extreme (known at 12:00); the predicate ORs three flags; no edge-sweep location (depth < 0.1·W), no 0.33/0.66 levels, no overshoot; FORMULAS excludes the edge-sweep reversal his 13 Oct 2025 "textbook" chart shows.
- Procedure: S-3 box. After 09:30 take the first edge sweep on either side. Walk 1m bars: `depth(t)` = running max excursion beyond the swept edge. At each bar inside 09:40:00–09:49:59, the location is the deepest of {edge (0 < depth < 0.1), 0.1, 0.2, 0.3, 0.33, 0.5, 0.66} already touched (t2 or ≤ δ beyond) — all known at that bar. Reversal = S-6 reject at that location with R = W (named) **or** `rev.inside` = a 1m close back inside [L, H]; both printed. Draw rows: EQ, the clean edge, then valid S-2 Asia/London/D-1 levels on the reversal side, reach by 10:30 / 12:00 / 16:00. Both sides.
- Constants: printed 09:40–09:50; 0.1/0.2/0.3/0.5; 0.33/0.66; 86.46% (per touch, pooled, 4,537 days); 09:47:36 / 09:51:05. Source-unspecified: reject r, k; δ; the reversal definition behind 86.46%.
- Invalid: level chosen from a later extreme; a close-through treated as the sweep; one side only; window-free reversal histogram.
- Fixture: synthetic H 110, L 90, W 20: 09:42 low 89.5 (depth 0.025 → location "edge"), 09:47 close 100.5 ≥ 90 + 10 → reject 1, depth column "edge". Second session: 09:44 low 79.75 (depth 0.51 → −0.5 at 80.0 with overshoot 1 tick ≤ δ), close 90.25 at 09:55 → reject 1, depth 0.5. Dated check: 2025-10-14 box H 24,665.00 / L 24,502.50 (his ≈24,660 / 24,500); −0.5 low = 24,421.25, first touch 09:45.
- Files: `family_recipes.py` (`j01_ladder` → as-of ladder), `sessions.py::projections` (add 0.33/0.66/2.33/2.66, mr lines), `recipe_score.py::_preds.j01`, wiki `tbr-6-9-range.md`, FORMULAS R-J01 ("different object" clause).

**R-J02 — Judas rider, trade #1**
- Wrong now: `open_to_m05_before_0940` is true when any ladder level prints in 09:30–09:40, while the catalog event says −0.5; no side rule, no per-depth rows, no excursion in R.
- Procedure: 09:30 1m open. For each side, first touch (t2) before 09:40:00 of 0.1 / 0.2 / 0.3 / 0.33 / 0.5 beyond that side's edge; print the deepest per side, the side of the first edge taken, and the side nearer the open. Excursion = |open − deepest level| in points and in R = |open − ±0.5 of that side|. Condition cell: Model A (R-J06).
- Constants: printed 09:30, 09:40–09:50. Source-unspecified: which depth "the projections" means (all printed as rows).
- Invalid: touches counted to 09:50 (trade #2 territory); the 6–9 edge as the target.
- Fixture: H 110, L 90, open 100; 09:36 low 88.0 (0.1 = 88.0 touched), 09:39 low 85.9 (0.2 = 86.0 touched) → deepest low-side depth 0.2, `m05_before_0940` = 0. Dated: 2025-10-14 open 24,638.75, −0.5 low first touched 09:45 → `m05_before_0940` = 0, deepest before 09:40 printed.
- Files: `family_levels.py` (`open_to_m05_before_0940` → per-depth fields), `recipe_score.py` catalog text, FORMULAS R-J02.

**R-J03 — Single break, extended overnight**
- Wrong now: `formulas.py::midretrace_hold` starts the 15-minute hold on the EQ-touch bar, whose close is at or through EQ, so the flag is 0 on all 647 sessions.
- Procedure: extended = 08:30 red-folder day or `w.rel-prior-rth ≥ 1.0` (named). Single break = first `b.c1` beyond one edge after 09:30 with the other edge untouched to 12:00. Retrace = first touch (t2) of EQ / Q25 / Q75 / range open after the break, before 10:00. Hold = S-6 hold(15) on the break side of that level from the bar after the touch. Outcomes: broken-edge reach by 10:00 / 12:00; 12:00–13:00 range ≤ 0.5·W (consolidation, named).
- Constants: printed 06:00–09:00, 10:00, EQ/quadrants, "until lunch". Source-unspecified: extended cut, hold length.
- Invalid: hold measured from the touch bar; a retrace after 10:00; projections as targets.
- Fixture: H 110, L 90, EQ 100; closes 110.5+ from 09:41; 09:52 low 100.25 (touch); closes 100.5–103 from 09:53 to 10:08 → hold 1.
- Files: `formulas.py::midretrace_hold` (start at touch index + 1), `family_levels.py` caller, FORMULAS R-J03.

**R-J04 — Single break, overnight purged**
- Wrong now: `purged_source` uses Asia 20:00–00:00 and London 00:00–03:00; his liquidity map is London 02:00–07:05 and Asia 18:00–00:05.
- Procedure: S-2 Jumbo map levels (London H/L 02:00–07:05, Asia H/L 18:00–00:05). Purged = all four taken before 09:30:00. Shrunk overnight = `w.rel-prior-rth ≤ 0.5` (named). Single break as R-J03; expansion = `b.c1` beyond EQ or a quadrant in the break direction; 09:40–09:50 continuation = no reversal ≥ 0.25·W inside the window. Reach of 1.0 / 1.33 / 1.66 by 10:30 / 12:00 / 16:00; re-entry count.
- Constants: printed EQ, quadrants, 1.33/1.66. Source-unspecified: purge completeness, shrink cut.
- Invalid: "purged" read as the 6–9 edge equal to an overnight extreme; windows 00:00–03:00.
- Fixture: Asia H 120 / L 100 (18:00–00:05), London H 118 / L 98 (02:00–07:05); prints 120.25 at 04:10 and 97.75 at 06:40 → purged 1 at 06:40.
- Files: `formulas.py::purged_overnight`, `sessions.py` (liquidity windows), `family_levels.py`, wiki `tbr-6-9-range.md`, FORMULAS R-J04 / P3-02.

**R-J05 — Single break, range-open / mid retrace**
- Wrong now: predicate = any later EQ touch on the 09:30–12:00 path. That misses his 27 Jul 2026 entry at EQ at 09:00, which came before the break. No A-period gate, no hold; the range open and OR mid are not scored; the v2 retrace table is not recomputed.
- Procedure: three rows, each scored separately. (a) Mid entry at range close: first touch (t2) of EQ from 09:00 (box complete) up to the first `b.c1` beyond an edge. Direction = the first move ≥ 0.25·W away from EQ (named). Outcome = a single break on that side through the A period (09:30–10:00) with the other edge untouched to 12:00, and reach of the next valid S-2 level beyond (27 Jul: the Asia low). (b) Range-open tag after 09:30 + S-6 reject (16 Jul). (c) After an A-period single break (`b.c1` beyond one edge in 09:30–10:00, other edge untouched), retrace to EQ, range open, 15m OR mid ((H + L)/2 of 09:30–09:44) and 5m OR mid. Two outcomes: S-6 reject in the break direction (R = W), and the counter-move reach of each mid by 10:30 (16 Jul, "could've taken the long back to mid"). Exit rows for all three: broken edge by 09:50 ("first 20 minutes") and by 12:00. Recompute his table: for each hour 09–10, 10–11, 11–12 with a low sweep, the share retracing to the range high / range open / EQ (and the high-sweep mirror).
- Constants: printed 60.4%; 86.8 / 92.8 / 66.2 (09–10 row) etc.; 15m / 5m OR. Source-unspecified: hold rule; the row (a) direction distance.
- Invalid: row (c) breaks after 10:00; double breaks.
- Fixture: 2026-07-27: EQ 28,693.62; the 09:00 bar tags it (H 28,700.00; his sell 28,685.75); 09:25 close 28,627.00 < L 28,629.25; high side untouched (09:30–12:00 high 28,615.75); Asia low 28,500.00 tagged 09:33 → row (a) = 1. 2026-07-16: range open 29,530.25 tagged at 09:30 (H 29,532.00); 09:34 close 29,433.50, 96.75 pts below it → row (b) = 1; low break 09:41 (close 29,350.50 < L 29,361.00); EQ 29,461.12 and OR15 mid 29,420.25 reached by 10:16 → row (c) reach = 1. 2026-07-21 (TradingView MNQ): scalps between R-Hi, EQ and R-Lo; our box 29,207.00 / 29,111.50 vs his ≈29,203.8 / ≈29,110.8 (his MNQ 06:36 spike high 3.25 pts lower).
- Files: `family_levels.py`, `sessions.py::_midretrace`, `recipe_score.py::_preds.j05`, wiki `range-path-class.md`, FORMULAS R-J05.

**R-J06 — 2026 context gate**
- Wrong now: path class uses 09:30–12:00 while his open-location table uses 09:30–10:30; prior VA edge differs from his pRTHVAL by 28 pts on 10 Jul 2026 (likely a different VA build); the predicate tests only "outside both + RVOL → double break".
- Procedure: at 09:30 the open cell = open vs prior RTH VA (S-7) × prior RTH range × 6–9 box. Path class on 09:30–10:30 1m closes for the table; 09:30–12:00 as a named row. Rows: his cells ("Below VAL, in range", "Below VAL & below PDL", …) HIGH-only / LOW-only / BOTH / ONE-side; the "discard mean reversion" cell (outside value and range, RVOL ≥ 1) double-break share; `open.oneway.A`. Print his RTHop / pRTHVAL / pRTHVAH beside ours for dated days.
- Constants: printed cells and rates (n 396: 29.5 / 37.6 / 29.8 / 67.2; n 517: 23.6 / 46.2 / 27.3 / 69.8). Source-unspecified: RVOL window, VA method of MGILevels.
- Invalid: 6–9-only "outside"; a 12:00 window for the table.
- Fixture: 2026-07-10 open 29,834.75, our prior VA 29,823.00–29,986.25 (his 29,795–29,985) → cell "in value" both ways; 2026-07-28 his RTHop 27,950 < pRTHVAL 27,990, > pRTHL 27,940 → "Below VAL, in range".
- Files: `family_open.py::build_open_table`, `recipe_score.py::_preds.j06`, wiki `open-location-switch.md`, FORMULAS R-J06.

**R-J07 — Range-size classifier**
- Wrong now: predicate is the pooled double share; the classification window is 09:30–12:00 while his table says "9-12 window".
- Procedure: `w.pct` = 100·W / close(08:59); bins [0, 0.3), [0.3, 0.5), [0.5, 0.8), [0.8, 1.2), [1.2, ∞). Path class on 09:00–12:00 (his) and 09:30–12:00 (named), by closes (named; wicks as a variant). Table per bin: double / single-H / single-L / none, n. Balanced vs imbalanced overnight (body ratio, named) as a split.
- Constants: printed bins and rates (0–0.3: n 1034, 55.5 / 23.7 / 20.3 / 0.5; … 1.2%+: n 169, 17.8 / 35.3 / 38.5 / 8.3; ALL n 3249, 44.8 / 28.0 / 26.1 / 1.1). Source-unspecified: close vs wick.
- Invalid: one pooled rate.
- Fixture: W 67.75, close 16,617.0 → 0.408% → bin 0.3–0.5 (2024-01-03); path low-only → single-L cell +1.
- Files: `sessions.py::build_session`, report tables for `range.6-9.published`, `recipe_score.py::_preds.j07`, FORMULAS R-J07.

**R-J08 — 1.33 / 1.66 fork**
- Wrong now: scored only in 13:00–16:00, so his 9 Sep 2025 10:45 reversal in the band is missed; band treated as two lines; no continue-vs-reject split.
- Procedure: S-3 band both sides. After the AM leg reaches the band on one side (first touch of 1.33, interior, or 1.66, any time after 09:30), outcome: reject = S-6 reject from the deepest touched level (R = W, overshoot ≤ δ past 1.66 allowed) vs continue = `b.c1` beyond 1.66 + δ with hold(30). Rows by touch time: AM (09:30–12:00) and PM (13:00–16:00). Also recompute "captured" rows (share of sessions whose daily high/low lies inside the band, both sides).
- Constants: printed labels ±1.33 / ±1.66, AM / lunch / PM windows, 88.2 / 65.6 / 92.4 / 66.8 (meaning of "captured" not printed).
- Invalid: 1.33 measured from the origin; PM-only; one side.
- Fixture: 2025-09-09 H 23,860.25, L 23,811.75, W 48.50 → low band 23,747.24–23,731.24; a 10:45 low inside it then a 1m close ≥ 23,747.24 + 24.25 within 15 min → reject 1 (AM row). Synthetic high side H 110, W 20: band 136.6–143.2, 13:40 high 140.0, 13:52 close 126.0 → reject 1 (PM row).
- Files: `family_levels.py` (band touch, AM window), `sessions.py::projections`, `recipe_score.py::_preds.j08`, wiki `extensions-1-33-1-66.md`, FORMULAS R-J08.

**R-J09 — London TBR**
- Wrong now: box 00:00–03:00 (`clocks.py` `range.london.00-03`); his box ends 02:00 and starts ≈20:00; edge reversals (8 Oct 2025 03:05 sweep of LOW) not scored.
- Procedure: S-4 box; events 02:00–06:00 exactly as R-J01 (edge / ladder depth, reject or return inside) and R-J08 (band), London width; 06:00 handoff ends the window.
- Constants: printed 02:00 end (dotted vertical), 03:00 and 06:00 dashed lines, 1.33–1.66 longs. Source-unspecified: the build start minute (named 20:00).
- Invalid: 00:00–03:00 or 03:00–03:30 box; 6–9 width.
- Fixture: box [20:00, 02:00) H 100, L 90; 03:05 low 89.75 (edge sweep), 03:14 close 95.25 ≥ 90 + 5 → reject 1 at depth "edge". Dated: 2025-10-08 his LOW 25,028; our 00–03 L 25,026.25 — recompute on [20:00, 02:00) and print both.
- Files: `clocks.py` (new `range.london.2000-0200`), `family_levels.py`, `recipe_score.py::_preds.j09`, wiki `tbr-remaining-clocks.md`, FORMULAS R-J09 and P3-06.

**R-J10 — Draws after the reversal**
- Wrong now: candidates = Asia 20–00, London 00–03, PDH/PDL (prior RTH); no D-1..D-3 daily pivots; no liquidity-map windows; retirement not applied.
- Procedure: at the R-J01 reversal (or the 10:00 expansion), candidates = valid S-2 levels on the reversal side: London H1/L1 (02:00–07:05), Asia H2/L2 (18:00–00:05), D-1/D-2/D-3 High/Low, pRTHH/pRTHL. Nearest valid candidate = the draw; outcome = touch by 10:30 / 12:00 / 16:00; the candidate retires at its first touch.
- Constants: printed windows and "D-1..D-3"; "deleted once purged". Source-unspecified: none beyond t2.
- Invalid: candidates already taken before the fire time; measured from 09:30.
- Fixture: London L1 = 25,684.75 taken at 08:12 → invalid at 09:45; Asia L2 25,696.75 untaken → the draw below.
- Files: `formulas_jumbo.py::j10_draw` / `j10_untouched`, `sessions.py` windows, new ledger helper (S-2) in `formulas.py`, wiki `prior-session-reference-levels.md`, FORMULAS R-J10.

**R-J11 — SessionStat 9–12**
- Wrong now: one mean line per side; `minavg` = min(mean_up, mean_dn) is falsified by his H4 table (Min Avg 40.74 < 74.53 and 65.55); scored event = reach of the mean line.
- Procedure: anchor = session open (09:00 1m open; London H4 uses its 02:00 open). Over the prior 60 sessions (printed default): up_i = H − open, dn_i = open − L. HIGH box = [open + median(up), open + mean(up)], LOW box = [open − mean(dn), open − median(dn)], dotted midline of each box; +MEH = HIGH top + 0.5 × (HIGH top − LOW bottom), −MEL mirror (printed 0.5 expansion); Min Avg (reading consistent with the table, not printed) = mean over sessions of min(up_i, dn_i). Events: first touch of each box by 12:00, reaction = S-6 reject from inside the box (R = box-to-box distance), coincidence rows with ±0.5, the 0.33–0.66 band and the 1.33–1.66 band within the box.
- Constants: printed lookback 60, simple average, Avg/Med box, expansion 0.5, sessions 09:00–12:00. Source-unspecified: the min-avg formula.
- Invalid: 09:30 anchor; averaging the range instead of the one-sided excursions.
- Fixture: up = [10, 20, 30, 40, 100] → median 30, mean 40; open 1,000 → HIGH box [1,030, 1,040]; dn = [15, 25, 35, 45, 30] → median 30, mean 30 → LOW box [970, 970]; min_i = [10, 20, 30, 40, 30] → Min Avg 26.
- Files: `family_env.py::build_env_table` (`ss_*`), `recipe_score.py::_preds.j11`, wiki `sessionstat-9-12-envelope.md`, FORMULAS R-J11.

**R-J12 — P-zone at the edge with the range open**
- Wrong now: P-zone = [p50, p75] band from the 09:30 open (70–80 pts); the tweet's ">" is read as "AM low > range open"; the reject is at ±0.5.
- Procedure: P-zone boxes per session anchor (09:00 S1, 09:50 or 10:00 S2, 02:00 S3; NT variant 15:30): for each anchor, over the prior 500 sessions, the excursion distribution from the anchor open; box edges at percentiles scaled by current volatility (engine unpublished — keep the thin-box geometry: box height = his printed 5–8 pts on NQ, named 6 pts), T1 = first percentile box each side, T3/T4 outer. Boxes are deleted when invalidated (a close beyond the far edge). Setup, long: a box within t2 of or beyond the 6–9 L; trigger = touch of the box then S-6 reject; target = range open (the ">" path); second leg = the 09:40–09:50 reversal (R-J01). Short mirror at H. "10 am p-zone > London low" = S2 box short, target London L (valid S-2).
- Constants: printed 500 sessions, percentile scaling, anchors, T1–T4, "Delete invalidated zones". Source-unspecified: percentile values, box height, volatility filter.
- Invalid: a band tens of points tall; ">" as an inequality; a box with no TBR level under it (FIND p.8).
- Fixture: 2026-01-02 H 25,742.75, L 25,679.25, range open 25,730.25 (his 25,743 / 25,680 / 25,730); his box 25,660–25,665 under L; touch 09:22 → long; range open reached 09:32 → target 1.
- Files: `family_env.py` (`pz_*`), `formulas.py::pz_edge_setup` / `pz_edge_setup_high`, `recipe_score.py::_preds.j12`, wiki `p-zones-benchmark.md`, FORMULAS R-J12.

**R-J13 — EV range to EQ**
- Wrong now: EV = 09:30 open ± 60-session mean excursion; his EVRange prices differ by 57–200 pts on 28 Aug, 1 Sep, 2 Sep 2026; predicate = reach.
- Procedure: keep EVRange as an unpublished estimator: store his printed lines as a calibration set and accept any candidate only if it reproduces them within 2 pts (28 Aug upper 29,724.50; 2 Sep 29,115 / 28,870; 1 Sep lower ≈29,074). Event with the lines once known: touch of either line, S-6 reject from it (R = line-to-EQ distance), then EQ reach; the "+50% / +60%" lines as overshoot rows. On a big 6–9 (his 2 Sep note) the EQ is the level and the EV lines are targets.
- Constants: printed line prices on those dates; "+50%", "+60%" labels (meaning unstated).
- Invalid: scoring any estimator as his without the calibration pass; reach without reaction.
- Fixture: candidate estimator must output upper 29,724.50 ± 2 on 2026-08-28; ours 29,781.34 → fail.
- Files: `family_env.py` (`ev_*`), `recipe_score.py::_preds.j13`, wiki `ev-range-expected-move.md`, FORMULAS R-J13.

**R-J14 — Absorption Zone+**
- Wrong now: body ≤ 0.3, k = 2.5 (printed 0.6 and 1.5); the trailing SMA14 resets at 09:30 so nothing can fire before 10:12 on 3m bars; levels limited.
- Procedure: bars = chart timeframe (named 3m; 1m and 5m rows). Volume average = SMA14 of the SAME continuous series across the session (no reset at 09:30; the prior 14 bars may be overnight). Flag = body/range ≤ 0.6 and volume ≥ 1.5 × SMA14(prior 14 bars). Location = any S-3 level ±t2, both sides, plus P-zone boxes. Outcome: S-6 reject at the level with vs without the flag; overlap with absorption A.
- Constants: printed 0.6, 1.5, 14.
- Invalid: centred average; an AM reset; a flag with no level.
- Fixture: 3m bar at 09:33 with body 1.0 / range 2.0 = 0.5 ≤ 0.6, volume 3,000 vs SMA14 1,800 → 1.67 ≥ 1.5 → flag 1 (2026-01-09 at his 09:33 marker).
- Files: `formulas.py::absorption_candle_at_levels`, `family_levels.py` caller, wiki `absorption-candle-jumbo.md`, FORMULAS R-J14 and P3-15.

**R-J15 — BigTrades at the level**
- Wrong now: only EQ and ±0.5 are tested; "London" = 02:00–05:00; the at-level test misses the print clusters he boxes (23 Jul 2026: ≈28,656–28,672, between ladder levels).
- Procedure: prints ≥ 100 (09:30–16:00) or ≥ 75 (London 02:00–07:05, map window) within t2 of any valid S-3 / S-2 level while the level is under test (first touch → 15 min, named). Rows: reject rate with vs without a print; print side; overlap with absorption A. Separate row: the print cluster as its own zone (box = the cluster's price span, ≈16 pts on 23 Jul), outcome hold vs run-through ("dunked on"). The size population is source-unspecified. His bubbles are MNQ (the chart series) or aggregated orders, and they don't match single NQ MBP-1 prints (23 Jul, 19 May, 16 Jul, 27 Jul 2026). Measurement is deferred.
- Constants: printed 100 NY, 75 London. Source-unspecified: at-level tolerance, test window, the instrument and aggregation behind the size.
- Invalid: session-wide "any print ≥ 100"; size quantiles.
- Fixture: level 18,420.00 touched 09:43; prints 120 @ 18,420.25 (counts), 95 @ 18,420.00 (noise), 150 @ 18,426.00 (off level) → 1 qualifying print. Real: 2026-07-23 his box ≈28,656–28,672 (714 + 213 buys at ≈28,664.5, 10:48) → run-through to ≈28,484 by 11:15.
- Files: `formulas_jumbo.py::j15_bigtrade_at_level`, `family_tape.py`, FORMULAS R-J15.

**R-J16 — RTH VP and delta shapes**
- Wrong now: no top-35% filter; no taper row; the predicate is a two-sided flag at EQ ±2 ticks with excursion ≤ 2 ticks, which excludes his 8 Jun 2026 probe 11.25 pts under EQ.
- Procedure: developing RTH profile (S-7) from prints in the top 35% of the session-so-far size distribution. At the EQ test (first touch → 15 min): the absorption window is a band around EQ (his 8 Jun band ≈25 pts; named 0.1·W), not ±2 ticks; sellers (buyers) hitting at the lows (highs) of the test candles with the candle closing back through EQ = absorption; taper = volume per row strictly declining over the last rows into the candle low (named 4 rows). Candles: 2-minute (his footprint). Outcome: reject at EQ / the low given the shape. Measurement deferred (MNQ population, see R-J15).
- Constants: printed 35%, RTH scope. Source-unspecified: band width, taper length; chart candle period 2 minutes (read from the footprint axis).
- Invalid: ETH profile; unfiltered prints.
- Fixture: FORMULAS R-J16 fixture (bins at EQ 100.0 two-sided; taper 30, 22, 15, 9, 4). Real: 2026-06-08 EQ 29,342.75; 10:00–10:01 candle L 29,331.50 → C 29,400.50 (his band ≈29,334.6–29,359.8); retest 10:04–10:05 L 29,348.50; 10:36 high 29,603.75.
- Files: `formulas_jumbo.py::j16_two_sided_at_eq`, `j16_taper_at_low`, `family_tape.py`, FORMULAS R-J16.

**R-J17 — Node under a TBR level**
- Wrong now: presence flag; level set EQ/±0.5; the node-under-level rule rests on FIND p.7–8, while v2's range-profile post is a shape classifier (24 Sep 2025) and the profile on his charts is the RTH session VP.
- Procedure: (1) Shape row (the v2 use): range profile of the 6–9 box (prints 06:00–09:00) → type P / b / D and direction (his table: "Profile Type b, Direction Bearish") → single vs double break by 12:00 (R-J07 split). (2) Node row (FIND, kept as a named comparison): LVN band / shelf edge (S-7) within tR = 0.05·W of each S-3 level (H, L, EQ, Q25, Q75, 0.33, 0.5, 1.33) on the 6–9 range profile and, separately, on the RTH session profile as-of the touch; outcome = reject at the level with vs without a node.
- Constants: none printed. Source-unspecified: shape thresholds, node thresholds, tR.
- Invalid: presence as the score.
- Fixture: 2025-09-24: box 24,913.50 / 24,869.50 (his HIGH / LOW), profile b → bearish; first close below L at 09:30, low 24,784.50 at 09:51 through −1.33/−1.66 (24,810.98 / 24,796.46) → shape row 1. 2026-06-08: slot 29,332.5–29,345 under EQ 29,342.75 → node_under 1. FORMULAS R-J17 fixture (LVN 100.75 under EQ 100.75 → 1; Q75 on an HVN → 0).
- Files: `formulas_jumbo.py::j17_node_under`, new range-profile shape classifier, FORMULAS R-J17.

**R-J18 — Entry models (3-candle OB, rejection block)**
- Wrong now: only ±0.5; only 3m; no rejection block; no invalidation rows.
- Procedure: 2m, 3m, 5m bars. Bullish OB: C2.low < C1.low and C3.close > C2.high; formed at C3 close; the sweep within t2 of (or ≤ δ beyond) any reversal location of R-J01 / R-J08 / R-J12 on the low side; entry = block top, stops = midpoint (aggressive) and C2.low (conservative). Bearish mirror. Rejection block (single break): the sweep candle's wick at EQ / quadrant / range open, confirmed by a close beyond the sweep candle. Rows per level and side.
- Constants: printed 2/3/5m, the two stop placements.
- Invalid: a new-extreme continuation; a block not tied to a level.
- Fixture: FORMULAS R-J18 fixture (C1 [80.50, 82.0], C2 [79.50, 81.75], C3 close 82.25 → OB, block [79.50, 81.75], mid 80.625).
- Files: `formulas_jumbo.py::j18_ob_bull` / `j18_ob_bear`, `family_recipes.py`, FORMULAS R-J18.

**R-J19 — PD RTH Range+**
- Wrong now: the first-presented M15 / H1 imbalance ("15" box) is not built; horizon 12:00 only.
- Procedure: pRTHH/pRTHL/EQ from the prior 09:30–16:00; ETH prints never retire them (S-2 exception). Direction after the RTH open = first `b.c1` beyond a 6–9 edge (named) and first 15m close vs 09:30 open (named). Draw = the untaken prior RTH extreme in that direction; reach by 12:00 / 16:00. First-presented FVG on 15m and 60m RTH bars (three-bar wick gap, first of the session), labelled with its timeframe; fill of near edge / mid / far edge.
- Constants: printed 09:30–16:00, M15, H1.
- Invalid: ETH taking PDH retires the level; direction read before 09:30.
- Fixture: 2025-04-01 pRTHH 19,489.75 / pRTHL 18,976.75 / EQ 19,233.25 (his 19,490 / 18,985 / 19,240); his M15 box 19,300–19,325.
- Files: `formulas_jumbo.py::j19_pd_touch` / `j19_htf_fvg`, `family_recipes.py`, FORMULAS R-J19.

**R-J20 — Delayed cycle 2 on 10:00 news**
- Wrong now: the flag bins the first −0.5 touch, not the reversal.
- Procedure: 10:00 release days (FRED 10:00 set, named). Reversal time = time of the R-J01 reversal event; rows = reversal-bin histogram on 10:00 days vs others.
- Constants: printed 10:00.
- Invalid: 08:30 days; touch time as reversal time.
- Fixture: 2024-01-03 (JOLTS/ISM): first −0.5 touch 10:17 (bin 10:00–10:30); the reversal time is the reject bar of R-J01 on that touch.
- Files: `formulas_jumbo.py::j20_delayed`, `family_levels.py::load_red_folder`, FORMULAS R-J20.

**R-J21 — Market conditions**
- Wrong now: `j21_class(red_folder_0830=False, …)` drops the red-folder condition; the score is a class share.
- Procedure: classes per TBR p.22–24 (extended = 08:30 red folder or `w.rel ≥ 1`; range-bound into news = sessions before a CPI/NFP/FOMC release that week; expansive = neither with a held single break). Outcome table per class: 6–9 H/L reach until 12:00, 1.0 / 1.33 / 1.66 reach by 16:00, knock-outs and re-entries.
- Constants: printed CPI/NFP/FOMC, 08:30, "until lunch time".
- Invalid: classes read from the outcome path.
- Fixture: 2024-01-05 (NFP) → extended; targets 6–9 H 16,426.75 / L 16,334.25. Dated sanity: 2026-07-10 +1.33 = 30,042.70 vs his sell limits 30,041.25.
- Files: `formulas_jumbo.py::j21_class` caller in `family_recipes.py`, FORMULAS R-J21.

**R-J22 — Failure protocol**
- Wrong now: only three-strike at the path side's ±0.5; returns measured from the touching bar itself.
- Procedure: at the deepest location reached on the swept side (R-J01), from the first touch: signatures (1) no R-J18 block within 15 min (named), (2) touching 3m body/range ≥ 0.6 (named), (3) `b.c1` beyond level + δ with hold(15), (4) touch outside 09:40–09:50, (5) three touches each followed by a return < 0.25·R measured from the bar after the touch, (6) touching volume < SMA14; label failed if any; then switched-to-single-break row.
- Constants: printed 3 strikes, 09:40–09:50, 14-period average.
- Invalid: failure inferred from the outcome.
- Fixture: FORMULAS R-J22 fixture (three touches, returns 3.0 / 2.5 / 1.5 with R = 20 → strike 3).
- Files: `formulas_jumbo.py::j22_*`, `family_recipes.py`, FORMULAS R-J22.

**R-J23 — Other published clocks**
- Wrong now: predicate is always True; ladders stop at ±1.66, no mr lines, no 0.33/0.66.
- Procedure: the eight printed clocks, each with the S-3 ladder in its own width, outcome window = until the next printed clock starts (named); rows per clock and side as R-J01 / R-J03.
- Constants: printed eight build windows.
- Invalid: the 09:40–09:50 cluster applied to other clocks.
- Fixture: 2024-01-03 midnight box 16,689.00–16,699.00 (W 10) → 0.5 levels 16,684.00 / 16,704.00.
- Files: `family_clocks.py`, `clocks.py`, `recipe_score.py::_preds.j23`, FORMULAS R-J23.

**R-J24 — Management rows**
- Wrong now: MFE uses 09:30–09:50 extremes that include prints before the entry.
- Procedure: entry = the R-J01 reject bar close; MFE/MAE from the bar after entry to 09:50 / 10:00 / 12:00; EQ reach and front-run reject at EQ; clean-edge, 1.0, 1.33 reach; `done_by_0950`.
- Constants: printed windows, "first 20 mins".
- Invalid: extremes before the entry.
- Fixture: entry long 80.0 at 09:44; bars after: high 88.0 by 09:50 → MFE_0950 8.0; a 09:31 high of 95 is ignored.
- Files: `formulas_jumbo.py::j24_management`, `family_recipes.py` (`first20` → post-entry window), FORMULAS R-J24.

**R-J25 — Swing-mid retraces (observation)**
- Wrong now: one mid from the first swing low and first swing high of the whole AM; flag 0 on all sessions.
- Procedure: trend-day sessions (single break held through 12:00, named). 5m fractal swings (2/2, confirmed two bars later); for each completed swing leg in the trend direction, mid = (swing high + swing low)/2, known at the confirming bar; outcome = touch then S-6 reject in the trend direction vs `b.c1` through; count per session.
- Constants: none printed.
- Invalid: swings found after the fact; one mid per session.
- Fixture: FORMULAS R-J25 fixture (swing 90 → 110, mid 100, touch 99.9, close 105 → hold 1).
- Files: `formulas_jumbo.py::j25_fractal_swings` / `j25_mid_retrace_hold`, `family_recipes.py`, FORMULAS R-J25.

### 5.2 Green Bird

**R-G01 — NYAM failed breakout / breakdown**
- Wrong now: PDH/PDL confluence uses prior RTH (his are full session); sweep depth 0 ticks in `family_fail.py::_failback` vs 2 in `grid.py`; k = 30 cap unprinted; no target rows.
- Procedure: S-5 NYAM box; sweep after 10:00; fail-back 5m close inside; entry = the fail-back close (his tickets also sell at TDO when it sits inside the box); invalidation = S-5; target rows = opposite edge, full-session PDH/PDL beyond, TDO; both sides. Confluence flag = swept edge within 2 ticks of a valid full-session PDH/PDL (S-2).
- Constants: printed 09:00–10:00, after 10:00, 5-minute close. Source-unspecified: depth, time cap.
- Invalid: events before 10:00; 1m close-back as the faithful row; 6–9 box.
- Fixture: 2026-08-28 NYAM H 29,703.25 (his ≈29,700); first 1m bar ≥ 29,703.50 after 10:00, 5m close 29,628 by 10:05 → fail 1; full-session PDH 29,708.00 (his stop 29,708.75) → confluence 1; full-session PDL 29,401.75 (his target area 29,400).
- Files: `family_fail.py::_failback` (1-tick take, no cap), `sessions.py` / new full-session prior H/L, `recipe_score.py::_preds.g01`, wiki `session-fail-boxes.md`, FORMULAS R-G01 / P3-07.

**R-G02 — Asia / midnight failure**
- Wrong now: only sweeps after 00:00; his 14 Jul 2026 trade swept PDL inside the Asia window and targeted the Asia high; producer issues as G01.
- Procedure: row A (finished box): S-5 Asia box, sweep after 00:00, 5m fail-back, TDO close-through row, target opposite Asia edge by 06:00 / 09:30. Row B (inside the window): a valid full-session PDH/PDL taken inside 20:00–00:00 and reclaimed by a 5m close; target the Asia box edge on the reclaim side.
- Constants: printed 20:00–00:00, TDO 00:00, 5-minute close.
- Invalid: 20:00–20:30 box; outcome into RTH.
- Fixture: 2026-07-14: Asia box 29,303.50–29,541.25; PDL (13 Jul full session) 29,386.50 taken at ≈23:20, reclaimed; his long 29,414.25 → Asia high 29,541.25 reached 01:14 → target 1 (row B).
- Files: `family_fail.py`, `clocks.py` `range.gb.asia`, `recipe_score.py::_preds.g02`, wiki `session-fail-boxes.md`, FORMULAS R-G02.

**R-G03 — Previous-hour box**
- Wrong now: two-hour outcome windows and events summed over boxes → 0.9985.
- Procedure: each completed clock hour h (09:00–15:00) → box; events only inside hour h + 1; one event per box per side; rows per hour: fail share, repeat-fade count per session, reach of opposite edge / TDO / full-session PDH/PDL.
- Constants: printed 60 minutes, completed hour.
- Invalid: 5-minute stepped boxes; events two hours out.
- Fixture: 2026-08-27 10:00 hour H 29,623.50 (his 29,620); 11:00–11:30 high 29,635.00 (his sweep 29,633), 5m close back < 29,623.50 → 1 event in the 10:00 box.
- Files: `formulas.py::clock_hour_boxes` / `hour_fail_count`, `family_levels.py`, `recipe_score.py` special case, FORMULAS R-G03.

**R-G04 — 9:30 manipulation reclaim**
- Wrong now: no "hold on the original side"; no discount target.
- Procedure: 09:30 1m open; sweep = a print ≤ open − 1 tick after 09:30; reclaim = 5m close above the open; hold = next 5m close also above (named); target = 50–61.8% pocket of the prior down move (R-G07) and the sweep low as the stop. Above-open short = named variant.
- Constants: printed 09:30, 50–61.8%.
- Invalid: 15-minute cap as the rule.
- Fixture: open 100.00; 09:33 low 99.50; 09:40 5m close 100.50; 09:45 5m close 100.75 → reclaim + hold 1.
- Files: `formulas.py::reclaim_5m`, `family_levels.py`, FORMULAS R-G04.

**R-G05 — TDO close-through**
- Wrong now: AM window only; the Asia-sweep → TDO case (his 3 and 8 Sep 2026 shorts at 00:30–00:45) is not a TDO row.
- Procedure: TDO = 00:00 1m open. After any S-5 sweep (Asia box after 00:00, NYAM after 10:00, previous hour, full-session PDH/PDL), a 5m close on the far side of TDO = close-through; rows per sweep source, overnight and AM separately.
- Constants: printed 00:00, 5-minute close.
- Invalid: a TDO cross without a sweep.
- Fixture: 2026-08-28 TDO 29,668.00 (his entry 29,674.25); NYAM sweep 10:00–10:03, 5m close 29,628 < 29,668 → close-through 1.
- Files: `family_levels.py` (`tdo_c5`), `family_fail.py`, FORMULAS R-G05.

**R-G06 — NWOG destination**
- Wrong now: Friday 15:59 close (the 16:59 session close is the faithful endpoint; it moves only the far edge); the tag window includes the Sunday 18:00 bar, which trades into the gap itself.
- Procedure: NWOG = [Friday 16:59 close, Sunday 18:00 open]. Near edge = the edge facing Monday's price (the Sunday open when price has moved away from it overnight). Valid until tagged, counting only after price has left the gap by ≥ 4 ticks (named). Monday rows: near-edge tag by 10:00 (his lockout), 12:00, 16:00; conditional row after a midnight (TDO) or Asia sweep-and-fail (17 Aug: TDO swept 09:31, failed 09:32, tag 09:39); far-edge fill separately; 15:59 and 17:00 as named variants.
- Constants: printed Friday close, Sunday 18:00, Monday, ≈10:00 lockout, ~30 minutes.
- Invalid: settle as the faithful endpoint; counting the 18:00 bar as the tag.
- Fixture: 2026-08-17: gap [30,154.00, 30,170.00] (16:59) / [30,144.50, 30,170.00] (15:59); TDO 30,246.75 swept 09:31 (H 30,266.00), 09:32 close 30,205.50; near edge tagged 09:39 (L 30,165.50) → tag by 10:00 = 1. 2026-07-27: gap top 28,500.00 tagged 09:33. 2026-08-03 (tape): gap [28,287.00, 28,565.00]; short level 28,665 ≈ TDO 28,669.00; near edge tagged 03:02.
- Files: `family_fail.py` (NWOG endpoint, tag start), FORMULAS R-G06; data: the NQ 1m index lacks 2026-08-03 and 2026-08-04 (0 of 1,380 bars) although the MBP-1 tape has both sessions — rebuild those bars.

**R-G07 — Golden pocket**
- Wrong now: impulse = the NYAM box; predicate = touch.
- Procedure: impulse = the completed move he measures: from the last valid swing extreme before the move (overnight high/low or the prior swing, confirmed 5m fractal) to the move's end (the running extreme at evaluation time); pocket = 50–61.8% retrace from the end back toward the start; direction from the impulse; event = touch then S-6 reject in the impulse direction, or sweep + 5m close of a level inside the pocket (e.g. PDL); traverse = `b.c1` through the far edge; outcome = impulse-extreme reach.
- Constants: printed 50–61.8%.
- Invalid: 38.2–50%; box-based impulse; touch as the score.
- Fixture: 2026-09-01 impulse ONH 29,571.25 → AM low 29,040.25 (W 531.00) → pocket 29,305.75–29,368.41; his retrace to ≈29,315 (sweep of PDL 29,273.50 full session) and short 29,253.75 → touch 1.
- Files: `formulas.py::gp_band_impulse`, `family_levels.py::_gp_band` caller, FORMULAS R-G07 / P3-07.

**R-G08 — Overnight PDL / PDH sweep-and-reclaim bias**
- Wrong now: PDL/PDH from prior RTH; reclaim read from the 09:29 close; no PWL/PWH (his 19 Nov 2025 example is the previous-week low).
- Procedure: levels = valid full-session PDL/PDH and PWL/PWH (S-2). Overnight 18:00–09:30: take, then 5m close back on the original side, then no 5m close back through until 09:30; bias = reclaim side; outcomes = 09:30–12:00 path class and golden-pocket pullback reach.
- Constants: printed "overnight", PDL, PWL.
- Invalid: 1m reclaim; RTH-only levels.
- Fixture: 2026-07-14 full-session PDL 29,386.50 taken ≈23:20 (low 29,303.50), 5m close back above → bias long.
- Files: `family_levels.py` (`prior_rth_overnight_reclaim`), new PWH/PWL in the S-2 ledger, FORMULAS R-G08.

**R-G09 — Stacked sweep to NWOG**
- Wrong now: London 00–03, PDH RTH, tR = 0.05·W69 unprinted; no failed breakout, no structure shift.
- Procedure: stack = valid full-session PDH, Asia H (20:00–00:00), London H (02:00–05:00) within tR (named 0.1% of price); sweep of the highest, 5m close back below the lowest of them, 5m close below the last 5m swing low (structure shift, named); target = NWOG below; outcome = tag by 16:00. Low-side mirror = named variant.
- Constants: printed the three levels, NWOG.
- Invalid: a single-level sweep.
- Fixture: FORMULAS R-G09 fixture (PDH 110.0, Asia H 109.9, London H 110.1 → stacked; sweep 110.75, 5m close 109.5, MSS at 108.0, NWOG [100, 102] tagged).
- Files: `family_levels.py` (`stacked_asia_london_pdh`), FORMULAS R-G09.

**R-G10 — Chop-day repeated fade**
- Wrong now: both sides counted; no one-way lean.
- Procedure: boxes 09:00–10:00 and 10:00–11:00; lean = the side of "path of least resistance" (prior session close vs its open, named); count S-5 fail-backs at the box edge on the lean side only; ≥ 2 = repeated; reject share after each.
- Constants: printed the two boxes, shorts only in the example.
- Invalid: counting both sides.
- Fixture: 2026-08-20 NYAM H 29,470.25 (his stop box 29,449–29,473), full-session PDL 29,375.75 (his 29,377); two up-pop fails → count 2.
- Files: `family_levels.py` (`fade_count`), FORMULAS R-G10.

**R-G11 — A+ vs B+ label**
- Wrong now: session-level OR over three boxes (0.978).
- Procedure: label per TRADE: the traded range's sweep + fail-back (A+), sweep only (named weaker), neither (B+); outcome shares by label for each G01–G10 event.
- Constants: none.
- Invalid: a session-level label.
- Fixture: G01 event on 2026-08-28 (sweep + fail of the NYAM box) → A+.
- Files: `formulas.py::aplus_failback`, `family_fail.py`, FORMULAS R-G11.

### 5.3 AMT

**R-A01 — Balance-rule fade**
- Wrong now: inside-balance precondition and POC reach not in the predicate.
- Procedure: S-7 prior VA as bands (edge ± t2, named); precondition = no `b.c1` + hold(30) outside since 09:30; event = touch then S-6 reject (R = VAH − VAL) at either edge; outcome = POC touch within 60 min (named); MAMT's general failed-auction share = excursions beyond an edge that close back inside before any hold(30), per side.
- Constants: printed 70% VA; 80% claim.
- Invalid: developing VA; no precondition; one edge.
- Fixture: VAL 100 / VAH 120 / POC 112; 09:47 low 99.75, 09:58 close 110.5 → reject 1; POC 10:05 → reach 1.
- Files: `formulas_jumbo.py::a01_fade`, `family_recipes.py`, `recipe_score.py::_preds.a01`, FORMULAS R-A01.

**R-A02 — Ledge continuation**
- Wrong now: "ledge" = the VA edge picked by the open; any AM print within 2 ticks counts.
- Procedure: ledges = S-7 lines at volume steps on the prior RTH profile (four around the POC); break = `b.c1` beyond a ledge + hold(30); retest = first touch from outside after the hold; hold = S-6 reject in the break direction and no `b.c1` back inside for 30 min; outcome = next node reach by 16:00.
- Constants: none printed.
- Invalid: VA edge as the ledge; retest from inside.
- Fixture: FORMULAS R-A02 fixture (shelf 100.00–100.50; break above; retest 100.5 at 10:20; close 101.0 → hold 1).
- Files: `formulas_jumbo.py::a02_shelves` / `a02_ledge_retest_hold` (wire them), `family_tape.py`, FORMULAS R-A02.

**R-A03 — Failed-auction traverse**
- Wrong now: only open-outside cases.
- Procedure: breakout = open outside the prior VA or `b.c1` + hold(30) outside during RTH; re-entry = `b.c1` back inside + hold(30); outcome = opposite-edge touch by 16:00.
- Constants: printed 80%, 72–80%.
- Invalid: requiring two 30-minute periods (that is R-A04).
- Fixture: VAL 100, VAH 120, open 96; 10:03 close 100.5, closes ≥ 100 to 10:33; 13:40 high 119.5 → traverse 1.
- Files: `formulas_jumbo.py::a03_reentry_traverse`, FORMULAS R-A03.

**R-A04 — Strict 80% rule**
- Wrong now: traverse not computed; only the 10:00 / 10:30 closes are checked.
- Procedure: open outside the prior VA; two consecutive 30-minute periods inside = both the A and B period closes inside (faithful) and, as a named variant, every 1m close of both periods inside; outcome = opposite-edge touch by 16:00.
- Constants: printed two 30-minute periods, 80%.
- Invalid: open inside value.
- Fixture: VAL 100, VAH 120, open 96; 10:00 close 101, 10:30 close 103; 14:00 high 119.5 → 1.
- Files: `family_levels.py` (`amt_80pct` + traverse), FORMULAS R-A04.

**R-A05 — POC tell**
- Wrong now: chop label only; far/near reach not scored.
- Procedure: after R-A03 re-entry or an inside open: chop = ≥ 2 POC touches without a held `b.c1`; traverse = `b.c1` through POC + retest reject; outcome = far vs near edge reach by 16:00, split by case.
- Constants: printed "again and again".
- Invalid: developing POC.
- Fixture: FORMULAS R-A05 fixture.
- Files: `formulas_jumbo.py::a05_poc_tell`, FORMULAS R-A05.

**R-A06 — MAMT Failed Auction setup**
- Wrong now: predicate = naked prior POC; `a06_failed_auction` targets the near edge; no older balance.
- Procedure: established balance = prior RTH VA; older balance = the most recent earlier session whose POC is still valid (S-2, untraded since); break from the established VA (`b.c1` + hold(30)) toward it; tag = touch of the older POC; rejection = close back ≥ 0.5·R toward the established balance within 5 min (MAMT) with tag depth as a column (AMTL deep dip); target = the FAR edge of the established balance (VAH after a downside break); outcome by 16:00.
- Constants: printed 80%.
- Invalid: any retest level; near-edge target.
- Fixture: VAL 100 / VAH 120; older POC 92; closes < 100 from 10:00 with hold; 10:52 low 91.75; 10:56 close 96.5 → setup 1; 12:10 high 120.0 → far-edge reach 1.
- Files: `formulas_jumbo.py::a06_failed_auction` (target), `family_tape.py`, FORMULAS R-A06.

**R-A07 — Break-retest continuation**
- Wrong now: break and retest searched in the same window; only IB edges.
- Procedure: boundaries = prior VAH/VAL bands, ledges, IB H/L (known 10:30); break = `b.c1` + hold(30); retest searched only after the hold ends; hold = S-6 reject + no `b.c1` back for 30 min; outcome = next value reach; HTF filter = prior RTH close vs its VA.
- Constants: none printed.
- Invalid: a retest before the hold completes.
- Fixture: FORMULAS R-A07 fixture (IB 100–110; closes > 110 10:41–11:11; retest 11:30; close 115.25 at 11:44).
- Files: `formulas_jumbo.py::a07_break_retest`, `family_recipes.py`, FORMULAS R-A07.

**R-A08 — Re-accept flips bias**
- Wrong now: side chosen by the open; reach not scored.
- Procedure: both sides: held break outside, then `b.c1` back inside + hold(30); outcome = opposite-edge reach by 16:00.
- Constants: none printed.
- Invalid: an unheld poke.
- Fixture: FORMULAS R-A08 fixture.
- Files: `formulas_jumbo.py::a08_reaccept`, `family_recipes.py`, FORMULAS R-A08.

**R-A09 — Traverse without hold**
- Wrong now: extra 30-minute cap between the two edge closes; continuation not scored.
- Procedure: `b.c1` through both edges with no 30-minute run of closes inside between them (no other cap); outcome = continuation share on later retests of either edge.
- Constants: none printed.
- Invalid: the unprinted cap.
- Fixture: FORMULAS R-A09 fixture.
- Files: `formulas_jumbo.py::a09_traverse_nohold`, FORMULAS R-A09.

**R-A10 — Open-type / day-type gate**
- Wrong now: only "drive"; no MAMT four-class label.
- Procedure: open labels on 09:30–10:00 (drive / test-drive / rejection-reverse / auction per AMT1 p.11); day labels at 16:00 (AMT1 five types, thresholds named) and MAMT four classes (trend = beyond 2×IB one way; neutral extreme = both IB sides broken, close in outer 20%; neutral = both broken, close inside IB; normal = neither); transition matrix open × day.
- Constants: printed first 30 minutes, IBx2.
- Invalid: labels read before 16:00 for the day type.
- Fixture: IB 100–110; RTH range 95–125 closing 124 → both sides broken, close in outer 20% → neutral extreme.
- Files: `family_gap.py::_amt_open_label` / `_amt_day_label`, FORMULAS R-A10.

**R-A11 — Profile-shape gate**
- Wrong now: shape from bar HLC3 volume; only the RTVP pairing.
- Procedure: shape from the prior RTH trade profile (S-7): P / b / D / double / trending (named thresholds); rows per shape and resolution direction next session, each author's claim separately (AMT1 balance after; RTVP continuation; MAMT P resolves down).
- Constants: none printed.
- Invalid: 6–9 box profile; developing profile.
- Fixture: FORMULAS R-A11 fixture (thirds 590 / 195 / 115 of 900 → P).
- Files: `formulas_jumbo.py::a11_vp_shape`, `formulas.py::vp_p_shape`, FORMULAS R-A11.

**R-A12 — Overnight inventory and LVN**
- Wrong now: open within 2 ticks of single LVN prices.
- Procedure: overnight profile (S-7); double distribution → LVN band between humps and shelf band at the hump edge nearest the open; from 09:30: respected = touch + S-6 reject at the band; disrespected = `b.c1` through + hold(30); outcomes = ONH/ONL reach by 12:00; inventory sign stays tape-gated.
- Constants: printed 18:00–09:30.
- Invalid: prior RTH profile; price-change inventory.
- Fixture: FORMULAS R-A12 fixture (humps 100 / 110, bridge 105).
- Files: `formulas_jumbo.py::a12_double_lvn` / `a12_respected`, `family_tape.py`, FORMULAS R-A12.

**R-A13 — Overnight touch statistics**
- Wrong now: nothing in the ONH/ONL row; MPOC 73% and ONVAH/ONVAL/ONVPOC rows not scored.
- Procedure: keep ONH-or-ONL in RTH; add MPOC = (ONH + ONL)/2 touch given the RTH open inside the prior overnight VA; ONVAH / ONVAL / ONVPOC rows; half gap from pHOD/pLOD.
- Constants: printed MAMT p.21–23 tables, 94%, 73%.
- Invalid: AM-only window; MPOC = volume POC.
- Fixture: 2024-01-03 ON 16,591.50–16,737.25 → MPOC 16,664.38; RTH low touched ONL → 1.
- Files: `family_levels.py`, FORMULAS R-A13.

**R-A14 — TPO unfinished business**
- Wrong now: rate 1.0 by construction on the current RTH.
- Procedure: prior RTH TPO (30-minute letters A–M, 1-point rows, named); singles (interior), poor extreme (≥ 2 periods at the extreme) and 1-row tail as separate rows, excess (≥ 2-row single-letter tail); next-session outcomes: single fill, poor revisit, excess hold on first test. Full-session TPO (letters past M, as the figures print) = named variant.
- Constants: printed 30 minutes, "two or more rows".
- Invalid: pooled presence; current-session flags.
- Fixture: FORMULAS R-A14 fixture (single 109–111; filled next day at 10:12).
- Files: `formulas_jumbo.py::a14_tpo` / `a14_single_fill`, `family_gap.py::_tpo_poor`, FORMULAS R-A14.

**R-A15 — IB extension read**
- Wrong now: presence only.
- Procedure: IB 09:30–10:30; after 10:30 `b.c1` single / both / neither; continuation = RTH close beyond the broken edge (MAMT p.23 rows) per side; rotation = POC touch when IB holds.
- Constants: printed first hour, MAMT p.23 rows.
- Invalid: wick extension as the faithful row.
- Fixture: 2024-01-03 IB 16,556.50–16,653.50, single-side break → close beyond? (read 16:00 close).
- Files: `family_levels.py` (`ib_*`), FORMULAS R-A15.

**R-A16 — Ledge with confluence**
- Wrong now: ledge = prior VAL; AM VWAP known at 12:00.
- Procedure: ledges per R-A02; partners at the touch time: running session VWAP ±1 SD (as-of), prior VA edges, valid naked POCs; stacked = within tR (named); event = S-6 reject; stacked vs lone.
- Constants: none printed.
- Invalid: VA edge as the ledge; noon VWAP.
- Fixture: FORMULAS R-A16 fixture.
- Files: `formulas_jumbo.py::a16_stacked` / `a16_stacked_reject`, `family_tape.py`, FORMULAS R-A16.

**R-A17 — Two-transition extremes**
- Wrong now: presence on the current RTH profile known at 16:00.
- Procedure: prior RTH (or composite) profile; LVN with a second transition vs tail; ledge vs shelf split; event = S-6 reject at the level next session; with vs without the second transition.
- Constants: none printed.
- Invalid: VAH/VAL as extremes.
- Fixture: FORMULAS R-A17 fixture.
- Files: `formulas_jumbo.py::a17_second_transition`, `family_tape.py`, FORMULAS R-A17.

**R-A18 — C3 balance-position bias**
- Wrong now: synthetic tick integers as single prints; flag = AM high ≥ VAH.
- Procedure: singles from R-A14 (valid, unfilled); bullish = reject at VAL with an unfilled single above → outcome single reach; bearish = acceptance below VAL (`b.c1` + hold 30) → nearest single / poor low below; both mirrors.
- Constants: none printed.
- Invalid: singles inside the balance.
- Fixture: FORMULAS R-A18 fixture.
- Files: `formulas_jumbo.py::a18_bias`, `family_tape.py`, FORMULAS R-A18.

### 5.4 Order flow

Tape objects use NQ MBP-1 aggressor trades (S-8). "Absorption A at price p" = 2-minute aggressive volume into p ≥ the session q90 (as-of) with the price advance through p ≤ 2 ticks, evaluated at the touch minute, never at a session-end value. Every flag below is computed as-of its event minute.

**R-F01 — VWAP deviation fade with absorption**
- Wrong now: the running 18:00 VWAP ±2σ touch is OR-ed with an absorption at the noon AM-trade VWAP band (known at 12:00); "never on the touch alone" (VWAP p.4) is lost.
- Procedure: anchor = session 18:00 (VWAP p.3 plots 20:00–04:00; "resets every day"); HLC3 on 1m bars; standard-deviation bands ±1 and ±2 (the p.8 screenshot), ±2.5 named; event = touch of ±2 (±1 named "at least the 1") AND absorption A at the band within the touch minute ± 2 min; skip when a valid untaken S-2 level lies beyond the band within 0.5σ (the "draw still higher" clause, distance named); outcome = VWAP touch within 60 min (named); both sides; ETH and RTH rows separately.
- Constants: printed session anchor, HLC3, bands 1 and 2 (2.5 and 3 in text). Source-unspecified: absorption window, horizon, owed-draw distance.
- Invalid: touch alone; the 09:30 or noon VWAP as the faithful row.
- Fixture: FORMULAS R-F01 fixture (VWAP 100, σ 2, upper touch 104.25 at 10:14, 3,700 lots ≥ q90, advance 2 ticks → 1; 10:41 low 99.9 → reach 1; lower mirror at 11:30).
- Files: `family_recipes.py` (`f01_eth_touch` → AND with an at-touch absorption), `mbp1_objects.py::absorption_a` (price argument, as-of), `recipe_score.py::_preds.f01`.

**R-F02 — CVD three-step (blocked)**
- Wrong now: blocked by the `flow.cvd.trade` tape-trust gate; no divergence function; the canvas draws the retained diagnostic `f02_divergence` only.
- Procedure (when the gate lifts): CVD = cumulative aggressive buy − sell from 18:00 (09:30 named); swings = confirmed 5m fractals; step 1 divergence = new swing high with CVD below the CVD at the prior swing high (lows mirrored); step 2 exhaustion = aggressive volume on the push below the prior push (named); step 3 grade = a `b.c1` break with CVD slope against the break = fakeout; outcome = return inside the prior swing range within 30 min (named).
- Constants: none printed.
- Invalid: any bar-proxy CVD as the trigger.
- Fixture: FORMULAS R-F02 fixture (CVD 4,200 vs 3,950 at the new high → divergence; slope −80 lots/min at the 10:30 break → fakeout 1).
- Files: `mbp1_objects.py::cvd_from_trades`, new `f02_cvd_steps`, `FINDINGS.md` trust row first.

**R-F03 — Anchored VWAP convergence**
- Wrong now: AM VWAP to noon (lookahead), overnight VWAP and prior VA mid stand in for the three anchors.
- Procedure: as-of each 1m bar: session VWAP (18:00), weekly VWAP (Sunday 18:00), swing VWAP (anchored at the last confirmed 5m swing high and swing low, both kept); convergence = max spread of the three ≤ tR (named 0.05 × prior VA height); event = first touch of the convergence price after convergence + S-6 reject (close ≥ 0.5σ of the session band away within 15 min, named); both sides.
- Constants: none printed.
- Invalid: stand-in anchors; noon VWAP.
- Fixture: FORMULAS R-F03 fixture (100.20 / 100.35 / 100.10, tR 0.30 → convergence; touch 11:07, close 101.5 → reject 1).
- Files: new `formulas_flow.py::anchored_vwap`, wire `r_f03_convergence`, `family_tape.py` (`f03_vwap_conv`).

**R-F04 — Footprint stacked-imbalance magnet**
- Wrong now: the zone is found on the whole RTH ladder (known 16:00) and OR-ed with the AM-wide `footprint_4x`; no hold.
- Procedure: per candle (1m named; candle period not printed): diagonal imbalance = ask at p vs bid at p − 1 tick (and bid at p vs ask at p + 1) ≥ k (k = 3 and 4, both printed "3×–4×"); zone = ≥ 3 consecutive same-side imbalances (FP8 p.6), at-level variant ≥ 2 (p.7); known at the candle close; later revisit from outside; hold = S-6 reject in the stack direction within 15 min; both sides (buy "in a column", sell "stacked down").
- Constants: printed 3×–4×, three in a row, two or three at a level.
- Invalid: session-aggregate ladders; zones used before their candle closes.
- Fixture: FORMULAS R-F04 fixture (second candle stack 100.00–100.50; revisit 11:20; close 103.0 → hold 1).
- Files: `formulas_flow.py::r_f04_candle_stack`, `family_tape.py` (`f04_stack_revisit`, drop the `footprint_4x` OR), `mbp1_objects.py::footprint_4x`.

**R-F05 — Footprint absorption stack**
- Wrong now: the AM is treated as one candle (O 16,610.00, C 16,562.25, Δ 10,817); no candle POC flip; no level.
- Procedure: at a level (the DOM6 set: prior VAH/VAL, ledges, shelves, old highs/lows, within 3 ticks): candle direction vs candle delta disagree (FP9 p.4 "aggressive flow one way, price the other"); next candle's POC flips from the lower to the upper third (or reverse); reversal = S-6 reject within 15 min; both sides.
- Constants: none printed.
- Invalid: multi-candle aggregates; no level.
- Fixture: FORMULAS R-F05 fixture (10:07 bullish candle Δ −180 at VAL 100; POC 0.25 → 0.9 at 10:08; close 105.5 by 10:20 → 1).
- Files: `formulas_flow.py::r_f05_absorption_stack`, new per-candle delta/POC in `mbp1_objects.py`, `family_tape.py` (`f05_poc_flip`).

**R-F06 — DOM absorption at a level**
- Wrong now: the flag requires the 15-minute reversal, so trigger and outcome are one event; levels limited to prior VAL/VAH.
- Procedure: level set = prior VAH/VAL, ledges/shelves (S-7), valid old highs/lows (S-2); zone = level ± 3 ticks (printed); trigger = absorption A in the zone; outcome rows separately: reversal ≥ 0.25·R within 15 min (named), exhaustion split (window volume vs the previous window); both sides.
- Constants: printed 3-tick zone.
- Invalid: trigger that already contains the outcome.
- Fixture: FORMULAS R-F06 fixture (PDL 16,622.5 on 2024-01-03: 3,600 lots, min 16,622.0 → trigger 1; reversal 17.5 < 62.75 → outcome 0).
- Files: `family_tape.py` (`f06_abs_va` split into trigger/outcome), `formulas_flow.py::r_f06_dom_absorption` / `exhaustion_split`.

**R-F07 — Iceberg reload (blocked)**
- Wrong now: blocked for data (MBP-1 has no queue behind the display); `iceberg_touch_infer` fires on 439 of 446 MBP-1 sessions.
- Procedure (with MBP-10 or MBO): trade at the level larger than the displayed size, then displayed size restored to ≥ the prior display within 500 ms (named), ≥ 2 reloads, price advance ≤ 2 ticks (printed); outcome = S-6 reject.
- Constants: printed 2 ticks.
- Invalid: any MBP-1 inference as the trigger.
- Fixture: FORMULAS R-F07 fixture.
- Files: data inventory (NQ mbp-10), `mbp1_objects.py::iceberg_touch_infer` stays diagnostic.

**R-F08 — ABS four-check absorption**
- Wrong now: reward measured from the first AM trade; no location gate.
- Procedure: (1) location = at a DOM6 level within 3 ticks; (2) absorption print (aggression absorbed, advance ≤ 2 ticks); (3) reward = 3 ticks in the absorber's direction measured FROM the absorption price before 1 tick adverse beyond it; (4) second aggression = opposite-side 2-min volume ≥ q75 (named); failure share = absorptions without reward that fail (claim 27%); both sides.
- Constants: printed 3 ticks, 27%, 72–80%.
- Invalid: reward from any other origin; absorptions off-level.
- Fixture: FORMULAS R-F08 fixture (VAH 120.00, print 120.25, path to 119.50, adverse 120.50 → reward 1; 2,900 ≥ 2,600 → second aggression 1).
- Files: `formulas_flow.py::reward_3tick` / `r_f08_abs_four_check`, `family_tape.py` (`f08_reward_3tick`).

**R-F09 — STOP three-step with the four absorption stages**
- Wrong now: the flag compares the first 20 vs last 20 AM print medians session-wide (1 vs 1) and is false on every session; AM only while his clips are overnight.
- Procedure: at a thesis level (DOM6 set + dealing-range extreme), ETH and RTH: stage 1 absorption A; stage 2 replenishment (blocked, depth); stage 3 digit thinning AT the level = median size of the last 20 aggressor prints at the level ≤ 0.5 × the earlier median there (named), with the 1-minute delta turning against the aggressors; stage 4 liftoff = 2–4 upticks away from the level (printed); entry within 1–2 ticks of the liftoff price (printed); digit classes: literal 1 / 10 / 100-lot classes (ES clips) and NQ session-quantile classes as two named readings; both sides.
- Constants: printed 3 ticks, 2–4 upticks, 1–2 ticks, 27%.
- Invalid: session-wide size medians.
- Fixture: FORMULAS R-F09 fixture (liftoff 100.75). Real session 2026-07-15 overnight (STOP p.8–9, 01:01 and 03:04 ET): his trapped-buyer boxes at the overnight highs ≈30,044–30,056; our 01:00–01:05 bars 30,001.25–30,058.25; SELL 1 R:R 2.00, −$100 | 20 ticks, +$200 | 40 ticks.
- Files: `formulas_flow.py::digits_thinning` (level-local), wire `liftoff_upticks` / `r_f09_stop_stages`, `family_tape.py` (`f09_thinning`), session window 18:00–17:00.

**R-F10 — Protected-low trailing**
- Wrong now: "last five AM prints above the AM low + 2 ticks" (rate 0.9985); low side only.
- Procedure: protected low = confirmed 1m fractal low (3/3 named) with the largest |Δ| cluster at the low ≥ q75 (RD p.4 draws the SELL-delta cluster there: "Sellers have become trapped = Buyers will protect here"; FORMULAS' positive-delta fixture = named variant), then an escape (1m close above the prior swing high), then 5 bars not back within 2 ticks; stop trails to just below it (RD p.5); break = 1m close below the highest-|Δ| protected low → "traversing to the stop"; rows: break share, MFE before break; protected high mirror.
- Constants: none printed.
- Invalid: lows without an escape.
- Fixture: FORMULAS R-F10 fixture (fractal 100.0, escape at bar 17, break at bar 41, MFE 4.5).
- Files: wire `formulas_flow.py::r_f10_protected_low` (+ high mirror), `family_tape.py` (`f10_protected`).

**R-F11 — Delta print at an LVN extreme**
- Wrong now: the RTH POC (16:00) near LVNs stands in for the delta print; no touch.
- Procedure: LVN extreme = the edge of a volume band (S-7) on the prior or composite profile; highest-|Δ| print of the running delta profile as-of the touch within tR (named) of that edge; event = wick reaction (touch and 1m close back on the original side, RD p.9) with the repeat count ("more than one wick reaction", RD p.10); when the delta print and the wick disagree, the delta print wins (RD p.10); outcome = S-6 reject; both sides.
- Constants: none printed.
- Invalid: full-session dp.max; the POC.
- Fixture: FORMULAS R-F11 fixture (LVN 118.5, dp.max 118.25 → paired; 10:44 wick → wick_reaction 1; 12:10 → repeat 2).
- Files: wire `formulas_flow.py::r_f11_delta_lvn`, `family_value.py::scan_rth_delta` (as-of), `family_tape.py` (`f11_delta_lvn`).

**R-F12 — Who's-in-control arrival read**
- Wrong now: session-wide first-5 vs last-5 print sizes (rate 0.86), no extreme.
- Procedure: at a balance extreme (WIC draws shaded bands) on touch: displacement speed of the last 5 closes vs the session q75 so far and the slope of aggressive volume per minute → aggressive / passive arrival; outcome on the printed 15-minute confirmation timeframe: broken = a 15m close beyond the band, defended = S-6 reject; both sides.
- Constants: printed 15-minute confirmation.
- Invalid: session-wide statistics.
- Fixture: FORMULAS R-F12 fixture (3.12 ticks/min ≥ 2.5, rising volume → aggressive; 15m close 121.5 → broken).
- Files: wire `formulas_flow.py::r_f12_arrival`, `family_tape.py` (`f12_arrival_aggr`).

**R-F13 — Trapped buyers, one retest**
- Wrong now: keyed on the 6–9 high in the AM; never fires; no trap print, failure memory or retest.
- Procedure: dealing-range extreme = redrawn balance high band; trap = prior-session highest-|Δ| print within tR of it and two prior failures (no 1m close beyond, printed "two prior failures"); breakdown = 1m close below the intraday range; one retest of the breakdown edge with a rewarded sell print inside the bar body; hold = close ≥ 0.5 × range away (named); trapped-seller mirror; ETH and RTH (STOP p.9 is overnight).
- Constants: printed two failures.
- Invalid: 6–9 box edges; retests after the first.
- Fixture: FORMULAS R-F13 fixture (20:15 breakdown, 20:40 retest, 60-lot print in the body, 20:52 close → hold 1). Real session 2026-07-15: his trapped-buyer boxes ≈30,044–30,056 at the overnight highs.
- Files: wire `formulas_flow.py::r_f13_trapped_buyers` (+ low mirror), weekly/daily delta profiles in `family_tape.py`.

**R-F14 — BigTrades body-vs-wick and 350% line**
- Wrong now: 350% read from full-RTH same-price volumes plus an unrelated BigTrades print at a TBR level.
- Procedure: 30–60-lot aggressor prints classified by the 1m bar that contains them (40-range bars printed, not reproducible; 1m named): inside the body = rewarded, in a wick = absorbed; 350% line = a price where aggressive sell ≥ 3.5 × aggressive buy (or the reverse) as-of the print; marked when it holds a rewarded print; retest = first return + S-6 reject; both signs.
- Constants: printed 30–60 lots, 350%, 40-range bars.
- Invalid: session-end volumes.
- Fixture: FORMULAS R-F14 fixture (sell 420 / buy 110 at 100.5 with a rewarded print; retest 10:40, close 99.6 → 1).
- Files: `formulas_flow.py::r_f14_imb350` called at the print, `family_tape.py` (`f14_imb350`).

**R-F15 — Origin of the move (OFM)**
- Wrong now: alias of F18 (stacked 4× without refill).
- Procedure: catalyst = box across ≥ 2 absorbed 30–60-lot prints in the wicks at a swing extreme (box ≤ 0.1·R named; OFM p.5 draws three); release = close beyond the box with 30-s tape speed ≥ q90 (named); failure = close back through the box ("Sellers regain control" rectangle, OFM p.6); refill = aggressive with no result → aggressive with result (the printed REFILL clock); entry = re-squeeze at the edge of the failure rectangle (main), refill-box entry = named higher-risk variant; stop below the aggression; outcomes 1R / 2R / 3R; both sides.
- Constants: printed 30–60 lots, 1R–3R.
- Invalid: any footprint-stack stand-in.
- Fixture: FORMULAS R-F15 fixture (catalyst 109.75–110.0, failure 10:14, re-squeeze 10:41 at 110.75, 1.2R → reach_1R 1).
- Files: wire `formulas_flow.py::r_f15_ofm`, `family_tape.py` (`f15_ofm`).

**R-F16 — Balance-day fade**
- Wrong now: top side only, keyed on the 6–9 high; never fires.
- Procedure: dealing range = redrawn balance bands; absorbed wick prints at an extreme with no 1m close beyond for 15 min; leave ≥ 0.25·R (named); test back + absorption A → fade; target = the last rewarded body print before the extreme; both extremes.
- Constants: printed long-gamma / balance claims only.
- Invalid: the 6–9 box; one side.
- Fixture: FORMULAS R-F16 fixture (range 100–120; test 11:05 → trigger 1; 12:30 low 112.25 → target 1).
- Files: `formulas_flow.py::r_f16_balance_fade` (+ bottom mirror), `family_tape.py` (`f16_fade`).

**R-F17 — Refill-zone touch**
- Wrong now: ≥ 100-lot cluster 2 ticks wide with a revisit flag (REF p.7 draws a ≈15-pt NQ rectangle built 09:27–09:29, retested 09:40).
- Procedure: zone = big aggressive prints (60 / 80 / 100 lots, each a named cut) within 30 s (named) on one side; band = min..max price of the burst (the drawn rectangle); per-print and per-burst readings; leave ≥ 4 ticks (named); touch; hold = no 1m close beyond the far edge for 30 min (printed cancel) and a 12-tick move away; penetration ticks; target rows 12 / 32 / 96 ticks; stop 25–65, target 20–100 grids; both sides.
- Constants: printed 60 / 80 / 100 lots, 12 / 32 / 96 ticks, 30 min, 25–65 / 20–100.
- Invalid: a revisit without an outcome.
- Fixture: FORMULAS R-F17 fixture (zone 100.00–100.25, touch 10:40, dip 99.50, high 103.25 → hold 1, penetration 2).
- Files: wire `formulas_flow.py::r_f17_refill_zone`, `mbp1_objects.py::on_touch_refill` (diagnostic), `family_tape.py` (`f17_refill_zone`).

**R-F18 — Squeeze without failure**
- Wrong now: same flag as F15; no tape-speed release, no no-failure window.
- Procedure: catalyst per F15; release with 30-s tape speed ≥ q90 (named); no 1m close back through the catalyst for 15 min (named); pullback into the catalyst with absorption A = trigger; outcome = next level (S-2) reach; both sides.
- Constants: none printed.
- Invalid: footprint stand-ins.
- Fixture: FORMULAS R-F18 fixture (release 10:12, no failure to 10:27, trigger 10:33, prior RTH L 84.0 at 11:10 → 1).
- Files: wire `formulas_flow.py::tape_speed_pps` / `r_f18_squeeze`, `family_tape.py` (`f18_squeeze`).

### 5.5 Regime

**R-R01 — GEX regime gate**
- Wrong now: dte ≤ 14 quotes at 09:30–09:35; cumulative-sum flip with an argmin fallback sits 10% from spot (358.00 vs 400.14 on 2024-01-03) while GEX p.7 / p.15 draws the flip beside spot (726.17 vs 731.98).
- Procedure: QQQ 0DTE chain before the open (prior-close OI, 09:25 quotes named); GEX per strike = Γ·OI·100·S²·0.01 (call +, put −); flip readings recorded side by side: (a) per-strike sign change nearest spot, (b) cumulative-sum zero, (c) net GEX re-computed over a spot grid, zero crossing (the vendor-style profile; faithful to "beside spot"); walls = top 3 positive above and negative below, ranked; "Mom Trigger" kept as an undefined column; outcome rows: RTH realized range vs its 20-session median, first wall touch + S-6 reject per wall; per regime (net sign, spot vs flip).
- Constants: printed 0DTE, QQQ for NQ, per 1% move.
- Invalid: multi-expiry pooling as the faithful row.
- Fixture: FORMULAS R-R01 fixture (net −1.0e7 → short gamma; reading (c) between 495 and 505).
- Files: `family_gex.py::_gex_day`, `formulas_flow.py::r_r01_gex_k`, `recipe_score.py::_preds.r01`.

**R-R02 — VIX regime gate**
- Wrong now: bins 13 / 15 / 18 / 20 omit the printed 14 cut; the score is a band share, not the realized-range rows.
- Procedure: prior-session VIXCLS (the pre-open value); bins < 13, 13–14, 14–15, 15–18, 18–20, ≥ 20; rows per bin: RTH realized range (points, %), implied daily move = VIX/√252 × price, completion share (realized ≥ implied), VIX up/down vs the prior close.
- Constants: printed √252, 12.5 / 16 / 22 (ES 30 / 50 / 95 pts), cuts 13 / 14 / 15–18 / 20.
- Invalid: same-day close.
- Fixture: 2024-01-03 VIXCLS(2024-01-02) 13.20 → bin 13–14, implied 0.8315% ≈ 138.1 pts at 16,610.
- Files: `formulas.py::vix_band`, `_preds.r02`, FORMULAS R-R02.

**R-R03 — Thesis validity**
- Wrong now: `r_r03_thesis` kills a short label on any AM wick above VAL and stamps the death time 12:00; value shift is off; news is a calendar flag only.
- Procedure: label from the open vs the prior VA; death = `b.c1` through the band edge on the thesis side + hold(30); death time = the minute the hold completes; value shift = developing VA (as-of) overlapping the prior VA by < 50% (named) → dead; news as its own column; evaluation to 16:00 (12:00 named); both sides.
- Constants: none printed.
- Invalid: wick death; fixed death times.
- Fixture: FORMULAS R-R03 fixture (2024-01-03 short below VAL 16,685.0; no break → alive ≥ 150 min).
- Files: `formulas_flow.py::r_r03_thesis` (eval_min, death rule), `family_recipes.py`.

**R-R04 — Triad IØD / RFZ (blocked)**
- Wrong now: blocked by the `flow.smt.*` gate; the canvas draws `smt_ohlc` and the NQ / ES / YM / RTY returns from 09:30.
- Procedure (when rebuilt): each index against its own full-session PDH/PDL and pRTHH/pRTHL (S-2); SMT = one takes its level within a 5-minute window (named) while NQ does not (or the reverse); sister reject = the taker closes back ≥ 0.5·R within 15 min; IØD reaction = NQ moves ≥ 0.25·R the other way within 15 min; RFZ recorded when drawn.
- Constants: none printed.
- Invalid: trade-level ES SMT after 2024-08-30 (out of F).
- Fixture: FORMULAS R-R04 fixture (ES takes 5,500 at 10:14, NQ does not; NQ ≤ 104.5 by 10:29 → 1).
- Files: `family_flow.py::build_smt_ohlc`, `FINDINGS.md` trust row.

### 5.6 Sires / Saint

Shared: Sires levels are BANDS (§3 rule 14): NQ heights 7–20 pts on his charts (29,735–29,745; 29,775–29,795; 29,622–29,633; 28,700–28,707), ES 5.25 pts (K10). Band builder (source-unspecified, named): contiguous rows ≥ the 70th volume percentile of the daily / weekly / composite profile (the DeepCharts tabs he shows), plus prior-session highs/lows drawn as bands, height capped at 20 NQ pts. Dealing range = the balance price has rotated in since the last `b.c1` + hold(30) break. First touches of a fresh zone are a separate row (REF p.16, K18 p.7). ETH and RTH both (DeepCharts stamps are ET).

**R-S01 — Refill long at the range bottom**
- Wrong now: bands = prior VAL/VAH ±2 ticks, 71–266 pts from his band on 14 Jul 2026.
- Procedure: range-bottom band; absorption A inside it ("sellers absorbed at the bottom, no result for the push"); entry = first 1m close above the absorption box high ("buyers regain control, the refill"); stop just under the band; objective = next band / prior highs above; short mirror at the range top.
- Constants: none printed; tickets illustrative.
- Invalid: prior VA edges as the band.
- Fixture: 2026-07-14 (NYAM p.4–5): band ≈29,735–29,745, absorption box ≈29,745–29,750 at ≈09:36, +1 @ 29,757.25, STP 29,744.25 (−$260), LMT 29,804.25 (+$940) under the prior-high rectangle ≈29,812–29,830; our 09:30 open 29,811.00.
- Files: band builder (new, `formulas_flow.py`), `family_tape.py` (`r_s01_refill_long/short` inputs), `recipe_score.py::_preds.s01`.

**R-S02 — Third-retest short**
- Wrong now: prior VAL ±2-tick band; defence volumes hard-coded 0.
- Procedure: support band tested from above three times with a leave ≥ 0.25·R between tests (named); defence per test = aggressive buy volume at the band ≥ q90; third undefended test → short on the first 1m close below the band; stop above the band; win and loss rows; resistance mirror.
- Constants: printed "twice", "third".
- Invalid: counting tests without a leave.
- Fixture: 2026-07-14 (NYAM p.6–7): band ≈29,622–29,633, three tests 10:00–10:14, short 29,608.50 stopped at 29,621.25 → loss 1.
- Files: `family_recipes.py` (`r_s02_third_retest` band + defence volume from MBP-1).

**R-S03 — OFM level defended a second time**
- Wrong now: flag = F09 thinning (never fires).
- Procedure: OFM line (origin of the move, R-F15) → `b.c1` break → retest from the other side; defence = aggressive volume ≥ q75 with steady refresh (each print ≥ 0.8 × the first, named); trade only after the second defence (K18 p.14); outcome = reversal ≥ 0.25·R in 15 min; both sides.
- Constants: printed "second and third refresh".
- Invalid: a first defence.
- Fixture: FORMULAS R-S03 fixture; real 2026-07-14 purple OFM line ≈29,786 (NYAM p.9–11).
- Files: `family_tape.py` (new `s03_second_defence`), `formulas_flow.py`.

**R-S04 — ATH pullback OFM long**
- Wrong now: never fires on either canvas; the 350% test is a single tick while K2345 p.5 draws a box a few points tall at the trapped-seller price; no short mirror.
- Procedure: 5-session delta profile; trapped sellers = most negative delta within tR of the weekly high; ≥ 2 reclaim failures at the prior range high; buy-side 350% box (a few points, named 3 pts) at the trapped price; microbalance (R-S05) break long; outcome = next HTF level; mirror named.
- Constants: printed 350%.
- Invalid: single-tick 350%.
- Fixture: FORMULAS R-S04 fixture.
- Files: `family_tape.py` (`r_s04_ath_ofm`), `formulas_flow.py::r_f14_imb350` (box input).

**R-S05 — Microbalance breakout**
- Wrong now: 09:30–09:40 clock box; the last close-run box is found at 11:57 (2024-01-03, 16,565.50–16,574.00); rate 0.997.
- Procedure: ≥ 6 consecutive 1m closes (named) within 0.1·R (named; K2345 p.7 box ≈7 pts), known at the last close; breakout = first 1m close beyond; invalidation = opposite edge ± 2 ticks; outcome = prior RTH H/L reach; both sides; at a Sires band (named).
- Constants: none printed.
- Invalid: clock boxes; boxes used before they complete.
- Fixture: FORMULAS R-S05 fixture.
- Files: `family_recipes.py` (`s05_micro_break`).

**R-S06 — Two-reason level**
- Wrong now: single swing high, short only, no band; FORMULAS records R:R 1.00 for K10 p.8 whose ticket prints 9.60.
- Procedure: band = prior rejection band (two lines) with a minor HVN inside tR; touch + S-6 reject; invalidation beyond the band; 1.5R reach (printed); long mirror. ES source, NQ transfer labelled.
- Constants: printed 1.5R.
- Invalid: single-price levels.
- Fixture: K10 p.7 short band 7,558.75 / 7,564.00 (ES, SELL 2 R:R 1.00, 20 ticks); p.8 long band 7,547.75 / 7,544.75 (BUY 2 R:R 9.60, −$500 | 20 ticks, +$4,800 | 192 ticks).
- Files: `formulas_flow.py::r_s06_two_reason` (band, both sides), `family_tape.py`.

**R-S07 — Areas-not-direction thesis**
- Wrong now: prior VA 400 pts above price on 23 Jul 2026; trigger = first AM print; no band, side or re-entry.
- Procedure: areas = Sires bands; trigger = absorption A in the band + 1m close out on the thesis side; side from the band (support → long, resistance → short); stop/target rows 35/188, 15/211, 115/248 ticks; re-entry only on a print back inside the same band; trade count and daily objective recorded only.
- Constants: printed ticket rows, nine trades 10:14–10:32.
- Invalid: re-entry outside the band.
- Fixture: 2026-07-23 (ANAT p.7): band ≈28,700–28,707, "OFM" at ≈28,698, rally to 28,765 at 10:22; our 09:30 open 28,718.25.
- Files: `formulas_flow.py::r_s07_areas`, `family_tape.py` (`s07_mfe`).

**R-S08 — Continuation short at a minor node**
- Wrong now: never fires; "delta" = 5m close − open.
- Procedure: minor HVN band at the top of balance with ≥ 2 prior rejections; ≥ 3 consecutive 5m bars of negative aggressor delta (MBP-1); touch + S-6 reject → short; outcome = as-of intraday POC; flip row = 1m close above + retest hold → VWAP reach; mirror.
- Constants: tickets illustrative (9-pt stop, 55-pt target).
- Invalid: price-change delta.
- Fixture: FORMULAS R-S08 fixture.
- Files: `family_tape.py` (`s08_node`), `formulas_flow.py`.

**R-S09 — Open above value**
- Wrong now: compares the open to its own 09:30–10:00 VAH (2024-01-17 opened 16,825.25 below prior VAL 16,876.75 and fires).
- Procedure: A period (09:30–10:00) fully above the PRIOR VAH; after ≈10:00, 1m close above the developing VAH (as-of) with a 3-stack buy imbalance (named); retest from above + S-6 reject → long; mirror below VAL named.
- Constants: printed ≈10:00, A period.
- Invalid: the frozen A-period VAH.
- Fixture: 2024-01-17 → not eligible (A period below prior VAL); FORMULAS synthetic retest (24,210 → 24,221) → 1.
- Files: `family_recipes.py` (`s09_vah_break`), `family_open.py::build_open_table`.

### 5.7 Pine

Each Pine id is scored per the file's own table keys (§3 rule 16); windows are the Pine's, never the GB or Jumbo windows.

**R-P01** — Wrong now: σ from ≤ 20 log changes (4 on 2024-01-09); pooled rate. Procedure: σ% = sample stdev of the last 20 daily % changes (close to close), σ_px = σ% × 08:00 open; bands = open ± 0.25σ; touch in 08:00–12:00; reversion to the 08:00 open by 10:00 / 12:00; rows per touch hour × side. Constants: printed 20, 0.25σ, 08:00–12:00. Invalid: < 20 sessions of history. Fixture: FORMULAS R-P01 (σ 1.20% → 16,649.8 / 16,550.2). Files: `family_recipes.py` (p01), history warm-up.

**R-P02** — Wrong now: operator precedence scores only the high sweep; the sweep bar can be the return bar. Procedure: per hour: prev H/L/open/mid; isAbove = open > prev open; sweep = strict beyond; retrace (swept, mid, open, opposite) on bars after the sweep bar; 24 × 2 tables. Constants: printed arrays. Invalid: same-bar return. Fixture: FORMULAS R-P02. Files: `family_recipes.py` (p02), `family_clocks.py::_gb_hour_rows`.

**R-P03** — Wrong now: break and target times synthetic (+4 / +20 min) → rate 1.0. Procedure: hour candles 23/00/01/02/06/07/08; first break after the candle; excursion ep% → Z1–Z6; target = mid; real times; hard-stop hours. Constants: printed. Invalid: synthetic times. Fixture: FORMULAS R-P03 (07:00 candle, Z2, win 18 min). Files: `family_recipes.py` (p03), `family_clocks.py`.

**R-P04** — Wrong now: NYAM hour box + 5 pts; unconfirmed raids count. Procedure: 15-minute boxes 02:00, 09:00, 13:00; raid = beyond edge + 5 pts within 120 min; confirmation = 1m close back inside; buckets; both sides. Constants: printed 5 pts, 120 min, 15 min. Fixture: FORMULAS R-P04. Files: `family_recipes.py` (p04).

**R-P05** — Wrong now: London = 00:00–03:00; a fail counts as a fire. Procedure: London candle 02:00–08:00, NY 08:00–17:00; level = close ∓ 0.25 × body; success and fail rows separately. Constants: printed 0.25, windows. Fixture: FORMULAS R-P05. Files: `family_recipes.py` (p05).

**R-P06** — Wrong now: Asia 20–00 and London 00–03 boxes; pooled. Procedure: Asia 20:00–02:00, London 02:00–08:00, NY 08:00–16:00; position of the session open vs the prior session's midpoint; first-hit and sequential rows per position. Fixture: FORMULAS R-P06. Files: `family_recipes.py` (p06), `clocks.py`.

**R-P07** — Wrong now: mid retest to 12:00; extreme-first taken after the OR; pooled. Procedure: OR5 / OR15; key = OR colour × which OR extreme printed first inside the OR; mid retest to the Pine session end; extension targets. Fixture: FORMULAS R-P07 (mid 16,603). Files: `family_open.py` (p07).

**R-P08** — Wrong now: R-A15 predicate. Procedure: key = IB colour × first touch side after 10:30 × open vs IB mid; 0.1% leave-and-return mid band; extension percentiles. Fixture: FORMULAS R-P08. Files: `recipe_score.py::_preds.p08`, `family_levels.py`.

**R-P09** — Wrong now: three conditional rates OR-ed into one. Procedure: keep the construction; rows per open status (above / inside / below): no break of prior H, no break of prior L, one side / both, to 16:00. Fixture: 2024-01-03 status Below. Files: `recipe_score.py::_preds.p09`.

**R-P10** — Wrong now: touch = RTH high ≥ PP. Procedure: two-sided touch (1m bar spans PP / R1 / S1 / GZ); rows by open context. Fixture: FORMULAS R-P10 (PP 16,707.17). Files: `formulas_flow.py::r_p10_pivots`.

**R-P11** — Wrong now: 1m gap in 09:30–10:00, no close condition. Procedure: 5m bars; BISI/SIBI with the close condition; W1/W2 first-presented; direction_ok; near-edge fill. Fixture: FORMULAS R-P11. Files: `family_gap.py::_first_fvg_clock`.

**R-P12** — Wrong now: first two 1m RTH candles. Procedure: completed HTF candles (auto-mapped, 15m on 1m); variants a/b/c; midpoint box; outcome horizon named. Fixture: FORMULAS R-P12. Files: `family_gap.py::_cisd_closeback`.

**R-P13** — Correct (08:00–16:00 TDO touch, `tdo_touch_ny`); FORMULAS' Code bullet still says 09:30–12:00. Add the Pine's conditional rows. Fixture: 2024-01-04 TDO 16,549.00 touched. Files: FORMULAS text only.

**R-P14** — Wrong now: first-30 high ≥ RTH HOD. Procedure: session 18:00→17:00; 4H candles 18/22/02/06/10/14; checkpoint elimination state; HOD/LOD candle rows. Fixture: FORMULAS R-P14. Files: `family_recipes.py` (p14).

**R-P15** — Wrong now: open ± median range with MFE/MAE 0.6/0.4 of it (invented). Procedure: per session window, prior 60 sessions, nearest-rank percentiles of range / MFE / MAE from the window open; 15-minute box RE ladder k = 1–6; daily manipulation/distribution stats. Fixture: FORMULAS R-P15. Files: `family_recipes.py` (p15), `family_env.py`.

**R-P16** — Wrong now: VIX and 09:30 anchor, AM containment. Procedure: VXN (VOLI absent, named), prior settlement anchor, log zones a = V/16, b = V/√365, window 18:00–16:00; the 75.2% close-inside claim belongs to another file, scored separately. Fixture: FORMULAS R-P16. Files: `family_levels.py` (`ev_vix16_inside`).

**R-P17** — Wrong now: body/wick profile not built; 18:00-open touch has no Pine claim. Procedure: RTH 1m body/wick VP (rows 0.25), 70% VA, next-session VA outcomes; 18:00 / Sunday open recorded, not scored. Fixture: FORMULAS R-P17. Files: `family_recipes.py` (p17), `family_open.py::ohlc_vp`.

**R-P18 (blocked)** — OHLC CVD as a trigger stays blocked by the CVD trust gate; canvas draws `cvd_agree_ohlc`. Fixture: FORMULAS R-P18. Files: `family_flow.py::_ohlc_cvd`, `FINDINGS.md`.

**R-P19** — Wrong now: first two AM bodies only. Procedure: any consecutive bodies ≥ 4 ticks apart; near-edge fill; 80/20 confluence = gap edge within 8 ticks of an xx20 / xx80 price. Fixture: FORMULAS R-P19. Files: `family_recipes.py` (p19), `family_gap.py::_body_gap`.

**R-P20** — Wrong now: max AM print and range stand in. Procedure: 5m bars with sub-bar delta; sigEvent = |Δ| > max(6 × SMA50|Δ|, 3,000); volume anomaly > 2.5 × SMA20 → ±0.1% zone; vote. Fixture: FORMULAS R-P20. Files: `recipe_score.py` (`p20_mvfl`), `family_flow.py`.
