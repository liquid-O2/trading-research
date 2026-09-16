# Green Bird — failed breakout / failed breakdown

## Current evidence

Phase 1 setup implementation and the acquired historical census are complete. These counts describe observed setups with branch-specific input limitations; they are not fills or profitability. The source definitions below retain author-specific boundaries. Our inferred reconstruction is versioned separately.

[Full method measurements](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-FAIL.md) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) · [Research status](current-status.md).

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| GB-FAIL | full acquired historical measurement | 7589 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-FAIL.md |
| GB-FAIL | B0 engineering slice (9 dates, not a family population) | see P15-10 BASELINE_PARITY | not claimed | dual-scan slice; full-history not run (p90>5s, P15-17 projection>24h) | implementation/reports/research-work/P15-10/ |
| GB-FAIL | B0.1 engineering slice (9 dates, not a family population) | see P15-10 BASELINE_PARITY | not claimed | C3 reclaim; P4 omission; A1 london_box / A2 asia_box / A3 overnight registered as own populations | implementation/reports/research-work/P15-10/ |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| GB-FAIL | M02 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |

## Source definitions


Operating method / GB-FAIL. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


**Source name and unification.** “Sweep → reclaim → opposing liquidity” is his own formulation ([GB] p.31). NYAM, Asia, prior hour, prior day/week/month, TDO confluence, and golden-pocket examples repeat this failure-and-reclaim mechanism. The raw golden-pocket explanation requires a failed breakdown and reclaim, or the PDL sweep followed by a five-minute close back below; the retracement band alone is not another strategy ([GB] pp.25, 31–35).

### Ordered loop and attachments

| Step | Source operation | Source-object implementation snapshot and evidence limits |
|---|---|---|
| 1. Establish the reference and contextual direction | Finish the selected box or use a known prior level. NYAM is 09:00–10:00 and that box cannot be traded as finished before 10:00. Previous-hour examples use the completed hour. Asia's box is painted 20:00–21:00, 20:00–23:00 or 20:00–00:00 and London's 03:00–04:30 or 02:00–05:00 depending on the month ([GB] pp.45, 51–56, 60; re-read 2026-09-15 below). Prior day, previous weekly candle, previous month, and an already-observed overnight reclaim can supply the context. ([GB] pp.23, 25, 27, 30–35, 38–40.) | [O003](clock-grid-and-bars.md) · [O046](session-fail-boxes.md) · [O048](prior-day-week-month-levels.md) · [O136](directional-bias.md). Completed reference windows, prior day/week/month geometry and attributed directional context are implemented. Same-contract prior coverage and exact source London bounds can remain unavailable. |
| 2. Locate the potential failure | Watch the relevant high/low or reclaimed level. Optional confluence includes PDH/PDL, Asia/London, midnight TDO, and the 50–61.8% retracement of the explicitly measured impulse. TDO is the midnight opening price; NWOG is a destination between the Friday-close and Sunday-open references. ([GB] pp.21, 25, 27, 32–39.) | [O049](true-day-open.md) · [O051](new-week-opening-gap.md) · [O052](golden-pocket.md) · [O053](premium-discount-50.md). TDO, NWOG endpoints and selected-impulse retracement geometry are implemented with parent identity and availability. The source still determines the impulse and endpoint convention. |
| 3. Wait for the sweep and its failure | Sweep above and fail back below → short; sweep below and reclaim → long. The explicit PDL and Asia/TDO examples wait for a completed five-minute close. Those cited close-confirmation variants wait for the reclaim. The November 20, 2025 figure separately shows entry at the high sweep ([GB] pp.31, 43); it must not inherit a later MSS/FVG prerequisite. ([GB] pp.21, 23, 25, 27, 30–35, 38.) | [O003](clock-grid-and-bars.md) · [O047](sweep-reclaim.md). Strict sweep/reclaim ordering and complete clock-aligned confirmations are implemented. The frozen comparison uses its declared endpoint and expiry; those parameters are not universal author rules. |
| 4. Preserve the case-specific entry and structural risk | Enter the reclaim or its retracement; the PDL reply says to wait a few points after the close and use a low-risk retracement. The November 20, 2025 MNQZ2025 two-minute figure displays a short entry at the 9–10 high sweep, at 25301.75. MSS/FVG is annotated later; exact fill time is not established. The September 1 09:30 manipulation/reclaim long is a distinct timing branch, not an early completed 9–10 box. ([GB] pp.25, 31, 40, chart p.43.) | [O054](market-structure-shift.md) · [O055](fvg-body-gaps.md) · [O139](structural-risk.md) · [O150](order-lifecycle.md). MSS/FVG geometry, linked decisions, structural invalidation and lifecycle checks are implemented. The November 2025 sweep-entry observation remains separate from subsequent annotations; exact fill time is unknown. |
| 5. Take opposing liquidity; manage the remaining position | Opposite box edge, intermediate 50%, TDO, prior/session extremes or NWOG as actually named. Take partials, move to breakeven once working, trail/leave the runner when appropriate, then stop the session. Size the quality of the setup; do not average down. ([GB] pp.25, 30–39.) | [O059](quality-grade.md) · [O140](position-sizing.md) · [O141](trade-objective.md) · [O142](position-management.md) · [O145](daily-loss-limit.md) · [O150](order-lifecycle.md). Entry-linked objectives, sizing, partials, stop changes, runners and session constraints are implemented. Historical actions remain unknown without actual source/order records. |

**Branches, not new products.**

- NYAM / completed hour / Asia failures use their own finished reference. A sweep during construction is part of the box.
- A prior-day/week/month reclaim can establish a bias for subsequent aligned pullbacks. Do not demand a fresh NYAM sweep for a separately cited prior-level trade.
- The golden pocket is `[L + 0.50(H-L), L + 0.618(H-L)]` for the illustrated retracement of a down impulse; direction and measured impulse matter. The September 1 source combines it with an actual PDL sweep and five-minute failure ([GB] p.25). The 2026-08-12 example (post 2087610880162664526) combines a fib pullback and hourly-low reclaim ([GB] p.35).
- The 09:30 manipulation branch is the source's below-open/reclaim long with a retracement objective and stop at the lows ([GB] p.40). Its confirmation duration is not fully specified by that reply; do not silently impose all parameters from the PDL example.
- A+ requires a relevant sweep; “no sweep = not A+” is a necessary quality condition, not proof that every sweep is A+ or that no other trade is allowed ([GB] pp.21–23, 37–40). R-G11 attaches to grading this candidate, not an OR across unrelated boxes somewhere during the day.

**Source additions, 2026-09-14.** Two dated posts ([raw](/workspace/sources/x-raw-2026-09-14/greenbirdtrader/README.md)) add: a London-box failure (sweep of the London low or high after the box completes, a five-minute close back through the level, an optional retest with a higher low or lower high, objectives the midnight true-day open then the opposite London edge); a plain Asia-box failure without the true-day-open confluence; and overnight entries for the level and box branches (the 2026-09-11 first long was a sweep below the previous day's low and reclaim at about 00:30 ET). The accepted implementation scans every failure branch from 09:30 and has no London reference, so these are versioned additions for the family adapter, defined in [SOURCE_ADDITIONS_2026-09-14.md](/workspace/planning/phase-1-5/SOURCE_ADDITIONS_2026-09-14.md). Printed fixtures on MNQU2026, 2026-09-14: long 28,903.75 to 29,037.00; short 29,081.50 with stop 29,098.75 and target 28,890.50.

**November 20, 2025 source correction.** The retained [case registry](/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json), case `GB-FAIL-2025-11-20`, separates the displayed MNQ sweep entry from the subsequent MSS/FVG annotation ([GB] pp.31, 43). The predicate below describes confirmed-reclaim variants; it must not be applied retrospectively as this case's entry prerequisite. The frozen `mss_fvg_refinement` research comparison remains separately named. An NQ comparison does not establish the displayed MNQ execution or its exact fill clock.

### Phase 1 predicate — `GB-FAIL`

`reference_px` is the swept boundary; `opposite_bound` is the other edge when the reference is a box. `box_return_ok` means the confirmation is back inside that finished box, or true for a single-level reclaim. `source_hold_confirmed` records the actual reclaim/hold observation when a five-minute rule was not stated. `tdo_required` is true only in the selected source variant.

```sql
reference_frozen AND bias_recorded AND risk_defined AND objective_fixed
AND reference_known_at <= sweep_at
AND context_at <= sweep_at AND sweep_at < confirm_at
AND confirm_at <= decision_at AND source_session_allowed
AND (
  (side = 'short' AND sweep_high > reference_px
                  AND confirm_close < reference_px)
  OR
  (side = 'long' AND sweep_low < reference_px
                 AND confirm_close > reference_px)
)
AND box_return_ok
AND CASE confirmation_mode
  WHEN 'five_minute_close' THEN complete_clock_five_minute_bar
  WHEN 'reclaim_and_hold' THEN source_hold_confirmed
  ELSE NULL
END
AND (NOT tdo_required OR source_tdo_close_confirmed)
AND (NOT pocket_required OR impulse_known_at <= touch_at
                            AND touch_in_measured_pocket)
AND (NOT retracement_entry OR confirm_at <= retest_at
                              AND retest_at <= decision_at)
```

Sequence citations: [GB] pp.21, 23, 25, 27, 30–35, 38–40. Outcome: the preselected opposing-liquidity objective after this entry, with source stop/management recorded separately. Examples that sweep and remain accepted outside fail this predicate. A 09:45 candidate using a final 09:00–10:00 box fails availability. A pocket touch without failure fails. Missing London bounds, prior-week/month data, or an unspecified reclaim detector leave the corresponding automatic check unknown.


## Source fidelity re-read, 2026-09-15

All 60 pages of [GB] and the 2026-09-14 raw capture were re-read with every chart at native resolution and the order tickets, position tools and ladders read from zoomed crops. The findings below define what the source-faithful baseline B0.2 ([P15-16A](/workspace/planning/phase-1-5/tasks/P15-16A.md)) must reproduce; the Phase 1 predicate above is unchanged.

### How the author actually trades

- **Three sessions, one template.** The same sweep-and-fail template is traded in Asia (a pink box painted 20:00–21:00 or 20:00–23:00 ET on the 2026 charts; 20:00–00:00 on the September charts), in London (a pink box painted 03:00–04:30 in April and August 2026 and 02:00–05:00 in late August and September 2026) and in New York (a green 09:00–10:00 box with a grey 09:30–10:00 or 10:00–11:00 sub-box) ([GB] pp.45, 51–56, 60). The PM sweep of the 09:00–10:00 highs at 12:45–13:00 is a recurring short trigger (2026-04-23, 2026-08-27) ([GB] pp.45, 56).
- **Levels.** PDH/PDL, PWH/PWL, the midnight True Day Open, Asia and London highs and lows (AS.L, LO.L), the 9–10 box edges, NWOG, and the "Golden Pocket" 50–61.8% retracement of the last impulse ([GB] pp.43, 45–46, 50–53, 56, 59–60).
- **Confirmation.** A 5-minute close back through the level for Asia-high, TDO and PDL cases; entry at the level on the failure for 9–10 box sweeps (2025-11-20 short at 25,301.75; 2026-08-31 short 4 at 29,510.50 at the 09:00–09:30 box high two minutes after the sweep) ([GB] pp.43, 58, 60).
- **Risk and size.** Every position tool carries "Amount: 750": the risk per account is a fixed $750 and the quantity is derived from the stop distance (qty 2.5 at a 200-tick stop, 4.464 at 112 ticks, 5.747 at 87 ticks, 7.042 at 71 ticks) ([GB] pp.52–53, 56, 58, 60). The master account's size scales with the number of copy accounts (26–37 accounts on the Tradesyncer dashboards; 4 to 28 MNQ per trade) ([GB] pp.44, 47–49, 53, 55, 57–59).
- **Exits.** Always a ladder of 1-lot limit orders toward the opposing liquidity, 4 to 18 rungs spaced 8–25 points, with the position tool's target at the far level and R:R 4.3–11.1 shown on the tool: 2026-04 long 11 at 26,336.75 with nine sell limits from 26,457 to 26,584.75; 2026-07-29 short 21 at 27,644.50 with eighteen buy limits from 27,533.75 to 27,191; 2026-08-11 long 12 at 29,637.25 with ten sell limits from 29,679.25 to 29,828; 2026-08-27 short 8 at 29,642.25 with eight buy limits from 29,551 to 29,425.50 ([GB] pp.44, 51–53, 56).
- **Overnight holds.** The 2026-08-11 Asia-low long was held through London into the next NY open where the PDH target filled ([GB] pp.53–54); the 2026-07-29 golden-pocket short and the 2026-07-30 London long are one overnight sequence ([GB] pp.51–52).
- **Outcome record.** Dashboards show identical per-account results (each account takes the same trade at the same $750 risk), e.g. +$3,042 per account on 2026-08-12 and −$3,036 per account on 2026-06-29, so a day's per-account P&L is a direct R multiple ([GB] pp.47, 53).

### Dated examples with printed prices

| Date (ET) | Case | Levels | Ticket | Source |
|---|---|---|---|---|
| 2025-11-20 | 9–10 high sweep, failure short; MSS+FVG boxes 25,270–25,285 and 25,250–25,262 | 9–10 high 25,301.75, NYAM.L 25,150, TDO 25,189 | short 25,301.75; buy limit 25,112.50; +732.50 on 2 MNQ | [GB] p.43 |
| 2026-04 (MNQM26) | 10:00 low sweep and reclaim long | low 26,280 | long 11 at 26,336.75; nine sell limits 26,457–26,584.75 (+$2,262 at 11:04) | [GB] p.44 |
| 2026-04-23 | 13:00 sweep of the 11:00 high; PM short | eye at 27,146.50; PDH 26,895, PWH 26,884, TDO 26,900 | short 1 at 27,116.25, stop 27,146.50 (30.25 pts), target 26,847.25 (269 pts, R:R 8.89) | [GB] p.45 |
| 2026-04-28 | both edges of the 9–10 box 27,075–27,250 traded 09:30–09:55 | | Day P&L +$13,410.40 | [GB] p.45 |
| 2026-07-13 | Asia sweep below PDL 29,385 to AS.L 29,340, reclaim long 20:40 | PDL 29,385 | long 4 at 29,414.25; sell limits 29,537.50 / 29,552.75 / 29,569.25 / 29,589.75 | [GB] p.48 |
| 2026-07-29/30 | overnight golden-pocket short of the 27,760 → 27,190 impulse; London long 04:00 | pocket 27,652–27,718 | short 21 at 27,644.50 and 15 at 27,652.25, stop 27,717.50 (73 pts), target 27,189 (455.50 pts, R:R 6.24), 18 buy limits; then long 5 at 27,359.75 and 5 at 27,382, sell limits 27,521.25–27,680.50 | [GB] pp.51–52 |
| 2026-08-11/12 | Asia-low long 20:40, held to the NY open; PDH target | AS.L 29,630, LO.L 29,695, TDO 29,830, PDH 29,896 | long 12 at 29,635.75, stop 29,587.50 (48.25 pts, 193 ticks), target 29,896 (260.25 pts, R:R 5.39), ten sell limits 29,679.25–29,828 | [GB] pp.52–54 |
| 2026-08-13 | 11:30 double top after the 09:35 breakout; PM short | tops 30,260 / 30,238.75 | short 2 at 30,227.50, stop 30,238.75, target 30,011.75, limit buy 30,069.50 | [GB] p.54 |
| 2026-08-27/28 | 12:45 sweep of the 09:00–10:00 highs; short; next-day 09:30 sweep short | 9–10 highs 29,600 / 29,620; LO.L 29,400; TDO 29,537; PDH 29,432 | short 8 at 29,642.25, stop 29,664 (21.75 pts, 87 ticks), target 29,425.25 (R:R 9.98), eight buy limits; short 8 at 29,680.75 with seven buy limits 29,492.50–29,384.50 | [GB] pp.55–56 |
| 2026-08-31 | 09:30–09:33 sweep of the 09:00–09:30 box high 29,515 | PDL 29,437, TDO 29,350 | short 4 at 29,510.50, stop 29,538.75 (28 pts, 112 ticks), target 29,280.75 (230 pts, R:R 8.21), buy limits 29,392 / 29,360.75 / 29,327.50 / 29,281.25 | [GB] p.58 |
| 2026-09-01 | golden pocket plus PDL sweep, 5-minute close below, short ≈11:45 | PDL 29,270; pocket 50% 29,311.50 | short 29,253.75, stop 29,303.50, target 29,044, buy limits 29,117.75 / 29,097.25 / 29,074 / 29,044 (R:R 4.22) | [GB] p.23 |
| 2026-09-03 | Asia-high sweep at 00:40, close back below, short | Asia high = TDO 29,238.25, PDH 29,213.25, AS.L 29,126.25 | short 29,238.25, stop 29,255, buy limits 29,140.50 / 29,126.50 | [GB] pp.27, 59 |
| 2026-09-08 | Asia-high sweep 00:30–00:45, 5-minute close below TDO, short; NYAM 9–10 low failure long | Asia high 29,748.25, TDO 29,740, AS.L 29,571; 9–10 low 29,469.25 | short 29,730.50, stop 29,748.25 (17.75 pts, 71 ticks), target 29,571 (R:R 8.99); long 29,469.25, stop 29,436.75, target 29,686.75 (R:R 6.69) | [GB] pp.16, 19, 60 |
| 2026-09-11 | overnight PDL/AS.L sweep and reclaim long 00:00–00:15 | AS.L 29,045, PDL 29,040, TDO 29,059.50 | long ≈29,059.50, stop 29,029 | raw capture 2026-09-14 |
| 2026-09-14 | London-low sweep, 5-minute reclaim long 09:40; Asia-high sweep short 10:10 | LO.L 28,860; TDO 29,018; Asia high ≈29,036–29,090 | long 28,903.75, stop 28,875.25, sell limit 29,036.25; short 29,081.50, stop 29,098.75, target 28,890.50 (R:R 11.09) | raw capture 2026-09-14 |
| 2026-09-15 | 09:50 sweep of the 09:00–10:00 box high, retest short 10:05; London-low sweep 10:55, reclaim long 11:05; PM sweep of the NY session low, long 15:35 | box high ≈29,453; LO.L 29,233.50; PWL 29,330.50; TDO ≈29,417; NY low ≈29,215.50 | short 2 at 29,441.50, stop 29,466.75, buy limits 29,330.50 / 29,233.50 (R:R 8.24); long 6 at 29,244.75, stop 29,215.25, sell limits 29,297.50–29,425.50 (R:R 6.19); long 1 at 29,215.50, sell limit 29,282.50 | raw capture 2026-09-15 |

### What the text above and the implementation had wrong or missing

1. Step 1 says "exact London bounds are not stated" and "Asia's drawn box is approximately 20:00–00:00": the boxes are painted on the charts, London 03:00–04:30 or 02:00–05:00 and Asia 20:00–21:00, 20:00–23:00 or 20:00–00:00 depending on the month; both variants must be registered as the author's, not as unknown ([GB] pp.45, 51–56, 60).
2. The accepted implementation scans from 09:30 only; the author's Asia entries print at 00:30–01:00 and 20:40, the London entries at 03:00–04:30, and the PM entries at 12:45–14:00 ([GB] pp.45, 48, 51–56).
3. Step 5 describes partials and runners; the author's exit is a resting limit ladder with the stop at a fixed $750 per account, and the quantity follows from the stop distance. A fixed contract count and a single target misstate the ledger ([GB] pp.44, 51–53, 56, 58, 60).
4. The golden pocket is used in three ways: the overnight short location on the retracement of a down impulse (2026-07-29), the stacked PDL short (2026-09-01) and the continuation long (2026-09-11); the pocket is measured on the leg in its own direction, and the 2026-09-11 stop sat at the pocket's near (50%) edge ([GB] pp.23, 51; raw capture).
5. "NYAM cannot be traded as finished before 10:00" is contradicted by the 2026-08-31 short at the 09:00–09:30 box high at 09:33 and the 2026-09-08 long at the 9–10 low; the author trades the box edges as soon as a sweep fails, and after 10:00 trades the completed box ([GB] pp.58, 60).
6. The overnight hold into the next NY open (2026-08-11/12) and the two-session sequence (2026-07-29/30) show that the objective can lie in the next session; the 30-minute and session-end censoring in the accepted comparison is a research convention, not the author's ([GB] pp.51–54).

### What B0.2 must reproduce

The three session boxes as painted, the level set, the two confirmation modes (5-minute close for level cases, at-level failure for box cases), the fixed-dollar risk with derived quantity, the limit ladder toward the opposing liquidity, and the author-example replay of the dated sessions above that fall inside the native calendar (2025-11-20 through 2026-09-03, the last and partial session of the run-1.0.1 calendar; the 2026-09-08 to 2026-09-15 examples postdate the data endpoint and are recorded as data_unavailable; corrected 2026-09-16, an earlier copy put the endpoint at 2026-08-19).


### Astra dossier corrections (2026-09-15, night)

From [GB-FAIL.md](/workspace/planning/research-program/reviews/astra-family-dossiers-2026-09-15/GB-FAIL.md), ruled SD03: the London-low long's stop sits below the retest's higher low and above the earlier sweep (2026-09-14 photo 1: live 28,903.75, stop 28,875.25, early sweep ≈28,827), so the A1 structural stop is "below the retest's higher low", not "beyond the sweep extreme"; live and drawn prices are distinct fixtures (2026-09-01 live 4 @ 29,254 / drawn 29,253.75; 2026-09-08 Asia live 29,730.75 / drawn 29,730.50; 2026-09-14 live 29,081.75 / drawn 29,081.50, other account 2 @ 29,074.25) and the replay compares against the live fill where one exists; 2025-11-19 adds a previous-week-low reclaim long (1 @ 24,625 with the sell limit 24,999 above PDH 24,975, [GB] p.31); 2026-08-27 has an earlier prior-hour attempt (5 @ 29,613.75, stop 29,633, target 29,427.75, [GB] p.38) before the 29,642.25 one, and 2026-08-28's ticket is 5 @ 29,674.25 with stop 29,708.75 and target 29,374 ([GB] p.39); the "do not average down" sentence above is house policy, not an anchored author statement.

### Source addition, 2026-09-15 post

Post 2099958990486798753 ([raw](/workspace/sources/x-raw-2026-09-15/greenbirdtrader/README.md); [additions note](/workspace/planning/phase-1-5/SOURCE_ADDITIONS_2026-09-15.md)) states the framework in the author's words: "Session highs. Session lows. Breakouts. Fakeouts. I know my range. Then I watch how price behaves at its edges. Break out and hold? I'm looking for continuation. Sweep a level and fail back inside? I'm looking for the reversal. For longs, I want a pullback into discount." Its three trades (table row 2026-09-15) confirm the September boxes (Asia 20:00–00:00, London 02:00–05:00, the 09:00–10:00 New York box with a 10:00–11:00 sub-box), the at-level entry on the retest after a box sweep, the fixed Amount 750 per account, and the limit ladder toward the opposing liquidity (six rungs spaced 18.75 to 32.25 points; the range is now 8–33). Two refinements: the structural stop sits below the retest's higher low when the entry follows a retest (2026-09-14) and beyond the sweep extreme with a buffer when the entry follows the reclaim directly (2026-09-15, stop 29,215.25 under the ≈29,227 sweep; short stop 29,466.75 above the ≈29,455 retest and under the ≈29,484 sweep); and the running New York session low or high (the author's "NY" marker beside AS.L and LO.L; [GB] text: the edges of the table are the session highs and lows) is a level for the afternoon sweep-and-fail template, first printed here as the 15:35 re-entry, registered in B0.2 as the author-observed branch `ny_session_extreme` with its own funnel. The example postdates the tape and is recorded as `GB-2026-09-15`, data_unavailable for replay.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Regime and thesis context.** [Scheduled news and changing information](news-event-context.md).

**Price references and price-action confirmation.** [Green Bird's finished session references](session-fail-boxes.md) · [Sweep, failure and reclaim](sweep-reclaim.md) · [Prior day, week and month extremes](prior-day-week-month-levels.md) · [Green Bird's midnight true-day open](true-day-open.md) · [09:30 cash-open price](cash-open-reference.md) · [New-week opening gap](new-week-opening-gap.md) · [Measured 50–61.8% retracement](golden-pocket.md) · [Premium / discount within a selected range](premium-discount-50.md) · [Market-structure shift after failure](market-structure-shift.md) · [Fair-value gaps and higher-timeframe imbalances](fvg-body-gaps.md) · [Source setup quality and exposure](quality-grade.md).

**Auction and profile structure.** [Prior-session auction landmarks](prior-session-reference-levels.md) · [Remaining auction objectives](unfinished-business.md).

**Risk, objectives and process.** [Green Bird's directional read](directional-bias.md) · [Entry-side structural invalidation](structural-risk.md) · [Exposure fitted to source risk constraints](position-sizing.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md) · [Source account and session stop](daily-loss-limit.md).

**Research, execution-study and risk records.** [Observed order lifecycle](order-lifecycle.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
