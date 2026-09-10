# RULES_SCORES.md

Phase 1 recipe scores on slice F (NY trade dates 2024-01-02 to 2026-08-31).
One row per RULES.md section B id. Section C swaps are not scored.
impl_fidelity=pass means every cited location, trigger, filter, and invalidation is a construction-audit pass function that matches the recipe clock, reset, side, and level.
gap and blocked rows have rate n/a. Those are not measured edges.
Event is the source event. Jumbo is path class and reach or reject of EQ, quadrants, range open, -0.5, and extensions. It is not a 6-9 H/L tag.
Green Bird is sweep plus fail-back after the box, after 10:00 on NYAM.
Order flow scores absorption A, 100ny, or 75ldn only when that trigger itself is pass. flow.smt.pine.3-3 is not a trigger.
Mapped NDX and SPX minutes are not used.

Rerun:

```
PYTHONPATH=implementation/src /tmp/trading-research-venv/bin/python implementation/tools/score_phase1_rules.py
```

id | framework | source_fidelity | impl_fidelity | n | event | rate | interval | year | RV | leakage | notes
---|---|---|---|---|---|---|---|---|---|---|---
R-J01 | Jumbo | faithful | pass | 647 | reject at -0.5 after 6-9 wick sweep, first touch in 09:40-09:50 | 0.0185 | [0.011, 0.032] | 2024 0.016 / 2025 0.020 / 2026 0.019 | low 0.014 / mid 0.023 / high 0.019 | 0 | leakage 0
R-J02 | Jumbo | faithful | pass | 647 | 09:30 open reaches -0.5 before 09:40 | 0.2813 | [0.248, 0.317] | 2024 0.251 / 2025 0.279 / 2026 0.333 | low 0.298 / mid 0.286 / high 0.259 | 0 | leakage 0
R-J03 | Jumbo | faithful | pass | 647 | single-break path class on extended overnight, EQ retrace | 0.0062 | [0.002, 0.016] | 2024 0.008 / 2025 0.008 / 2026 0.000 | low 0.014 / mid 0.000 / high 0.005 | 0 | leakage 0
R-J04 | Jumbo | faithful | pass | 647 | purged single-break reach of 1.0 / 1.33 from 6-9 edge | 0.0093 | [0.004, 0.020] | 2024 0.004 / 2025 0.012 / 2026 0.013 | low 0.005 / mid 0.014 / high 0.009 | 0 | leakage 0
R-J05 | Jumbo | faithful | pass | 647 | single-break midretrace to EQ / range open | 0.1855 | [0.157, 0.217] | 2024 0.162 / 2025 0.180 / 2026 0.231 | low 0.188 / mid 0.192 / high 0.175 | 0 | leakage 0
R-J06 | Jumbo | faithful | pass | 647 | open_cell path class; outside-both + RVOL double-break | 0.0680 | [0.051, 0.090] | 2024 0.049 / 2025 0.086 / 2026 0.071 | low 0.073 / mid 0.066 / high 0.066 | 0 | leakage 0
R-J07 | Jumbo | faithful | pass | 647 | path class by w.pct.0859close bin (XF p.24 recompute lives on range.6-9.published) | 0.3385 | [0.303, 0.376] | 2024 0.360 / 2025 0.320 / 2026 0.333 | low 0.362 / mid 0.305 / high 0.354 | 0 | leakage 0
R-J08 | Jumbo | faithful | pass | 647 | PM 13:00-16:00 reject at 1.33 from-edge | 0.0216 | [0.013, 0.036] | 2024 0.016 / 2025 0.029 / 2026 0.019 | low 0.028 / mid 0.014 / high 0.024 | 0 | leakage 0
R-J09 | Jumbo | faithful | pass | 647 | London 00-03 box -0.5 reject in 03:00-06:00 | 0.0541 | [0.039, 0.074] | 2024 0.089 / 2025 0.041 / 2026 0.019 | low 0.055 / mid 0.085 / high 0.024 | 0 | leakage 0
R-J10 | Jumbo | faithful | gap | n/a | leftover Asia/London/midnight reach after -0.5 reversal (draw list, not a location function) | n/a | n/a | n/a | n/a | n/a | leftover Asia/London/midnight reach after -0.5 reversal (draw list, not a location function)
R-J11 | Jumbo | faithful | pass | 647 | SessionStat avgHL60 reach (median and min-average are named variants) | 0.7496 | [0.715, 0.781] | 2024 0.761 / 2025 0.713 / 2026 0.788 | low 0.729 / mid 0.700 / high 0.821 | 0 | leakage 0
R-J12 | Jumbo | faithful | pass | 647 | P-zone T1 reach with 6-9 overlap and Model A | 0.0263 | [0.016, 0.042] | 2024 0.028 / 2025 0.012 / 2026 0.045 | low 0.014 / mid 0.019 / high 0.047 | 0 | leakage 0
R-J13 | Jumbo | faithful | pass | 647 | env.ev.mean60 reach; reject is not a separate EV function, reach is the sourced working-level event | 0.2411 | [0.210, 0.276] | 2024 0.279 / 2025 0.213 / 2026 0.224 | low 0.239 / mid 0.239 / high 0.250 | 0 | leakage 0
R-J14 | Jumbo | faithful | pass | 647 | absorption candle (body/range <=0.4 and vol >= 2.5 x SMA14) in AM | 0.4807 | [0.442, 0.519] | 2024 0.462 / 2025 0.480 / 2026 0.513 | low 0.482 / mid 0.465 / high 0.491 | 0 | leakage 0
R-J15 | Jumbo | faithful | gap | n/a | flow.bigtrade.100ny/75ldn at the TBR level (session print flag is not at-level) | n/a | n/a | n/a | n/a | n/a | flow.bigtrade.100ny/75ldn at the TBR level (session print flag is not at-level)
R-J16 | Jumbo | faithful | gap | n/a | RTH VP/delta shape at EQ (value.delta.rth.trade is delta-vs-POC, not two-sided midpoint) | n/a | n/a | n/a | n/a | n/a | RTH VP/delta shape at EQ (value.delta.rth.trade is delta-vs-POC, not two-sided midpoint)
R-J17 | Jumbo | faithful | gap | n/a | value.kz LVN under a TBR level (function is AM extreme near VAL/VAH) | n/a | n/a | n/a | n/a | n/a | value.kz LVN under a TBR level (function is AM extreme near VAL/VAH)
R-J18 | Jumbo | faithful | gap | n/a | 3-candle OB at -0.5 (block.sweep.tbr.3m is IB new-extreme continuation) | n/a | n/a | n/a | n/a | n/a | 3-candle OB at -0.5 (block.sweep.tbr.3m is IB new-extreme continuation)
R-J19 | Jumbo | faithful | gap | n/a | PDH/PDL reach given RTH open direction; HTF first-presented FVG fill | n/a | n/a | n/a | n/a | n/a | PDH/PDL reach given RTH open direction; HTF first-presented FVG fill
R-J20 | Jumbo | faithful | gap | n/a | 10:00 release calendar (inventory has CPI/NFP at 08:30 and FOMC date-only, not 10:00) | n/a | n/a | n/a | n/a | n/a | 10:00 release calendar (inventory has CPI/NFP at 08:30 and FOMC date-only, not 10:00)
R-J21 | Jumbo | faithful | gap | n/a | TBR p.22-24 condition class (unfavourable / expansive calendar table) | n/a | n/a | n/a | n/a | n/a | TBR p.22-24 condition class (unfavourable / expansive calendar table)
R-J22 | Jumbo | faithful | gap | n/a | 3-strike and extended-body failure-protocol counters | n/a | n/a | n/a | n/a | n/a | 3-strike and extended-body failure-protocol counters
R-J23 | Jumbo | faithful | pass | 643 | path class of TBR published clocks including midnight / A-period / lunch / MOC | 0.4526 | [0.414, 0.491] | 2024 0.463 / 2025 0.465 / 2026 0.416 | n/a (clock table) | 0 | clocks range.midnight.0000-0030 and the other TBR published boxes; rate is midnight double-break. Lunch and MOC are comparison clocks.
R-J24 | Jumbo | faithful | gap | n/a | MFE/MAE at TBR p.16 exit rules | n/a | n/a | n/a | n/a | n/a | MFE/MAE at TBR p.16 exit rules
R-J25 | Jumbo | faithful | gap | n/a | swing-mid retrace on trend-day sessions | n/a | n/a | n/a | n/a | n/a | swing-mid retrace on trend-day sessions
R-G01 | Green Bird | faithful | pass | 647 | NYAM 09:00-10:00 wick then 5m close-back after 10:00 | 0.7233 | [0.688, 0.756] | 2024 0.717 / 2025 0.738 / 2026 0.712 | low 0.748 / mid 0.732 / high 0.698 | 0 | leakage 0
R-G02 | Green Bird | faithful | pass | 647 | Asia 20:00-00:00 wick then 5m close-back 00:00-06:00 | 0.7110 | [0.675, 0.745] | 2024 0.713 / 2025 0.701 / 2026 0.724 | low 0.702 / mid 0.737 / high 0.693 | 0 | leakage 0
R-G03 | Green Bird | faithful | pass | 20057 | last-completed-hour box fail-back, any 5m step 09:30-12:00 | 0.5795 | [0.573, 0.586] | 2024 0.568 / 2025 0.582 / 2026 0.593 | low 0.575 / mid 0.579 / high 0.584 | 0 | n is hour boxes (31 steps x sessions). Session-any saturates; this is the per-box fail-back rate.
R-G04 | Green Bird | faithful | pass | 647 | sweep below 09:30 open then reclaim by 09:45 | 0.7388 | [0.704, 0.771] | 2024 0.757 / 2025 0.705 / 2026 0.763 | low 0.734 / mid 0.709 / high 0.769 | 0 | leakage 0
R-G05 | Green Bird | faithful | pass | 647 | TDO wick then 5m close back through midnight open | 0.3400 | [0.305, 0.377] | 2024 0.300 / 2025 0.357 / 2026 0.378 | low 0.353 / mid 0.333 / high 0.335 | 0 | leakage 0
R-G06 | Green Bird | faithful | pass | 125 | Monday NWOG fill by 12:00 (Friday 16:00 close vs Sunday 18:00 open) | 0.5280 | [0.441, 0.613] | 2024 0.574 / 2025 0.396 / 2026 0.667 | low 0.488 / mid 0.591 / high 0.500 | 0 | denominator is Mondays; 16:00 fill not computed (AM 09:30-12:00 overlap only)
R-G07 | Green Bird | faithful | pass | 647 | touch of NYAM 50-61.8% golden pocket after 10:00 | 0.7388 | [0.704, 0.771] | 2024 0.745 / 2025 0.721 / 2026 0.756 | low 0.757 / mid 0.723 / high 0.736 | 0 | leakage 0
R-G08 | Green Bird | faithful | pass | 647 | overnight sweep of PDH/PDL then close back through before 09:30 | 0.3771 | [0.341, 0.415] | 2024 0.340 / 2025 0.344 / 2026 0.487 | low 0.372 / mid 0.357 / high 0.406 | 0 | leakage 0
R-G09 | Green Bird | faithful | pass | 1 | PDH + Asia high + London high stacked within 0.05 R, Monday NWOG fill | 1.0000 | [0.207, 1.000] | 2024 1.000 / 2025 n/a / 2026 n/a | low 1.000 / mid n/a / high n/a | 0 | stacked PDH+Asia+London within 0.05 R; fill on those Mondays
R-G10 | Green Bird | faithful | pass | 647 | NYAM fail-back plus 10-11 fail-back (fade count >= 2) | 0.4544 | [0.416, 0.493] | 2024 0.462 / 2025 0.418 / 2026 0.500 | low 0.482 / mid 0.455 / high 0.434 | 0 | leakage 0
R-G11 | Green Bird | faithful | pass | 647 | label.aplus = 6-9 wick sweep observed | 0.9784 | [0.964, 0.987] | 2024 0.980 / 2025 0.975 / 2026 0.981 | low 0.995 / mid 0.967 / high 0.972 | 0 | saturates 0.978; locked A+ definition is 6-9 sweep only, not a trigger
R-A01 | AMT | faithful | gap | n/a | grid reject at prior-day VAH/VAL toward POC (value.vp.rth.trade is VAL present, not reject) | n/a | n/a | n/a | n/a | n/a | grid reject at prior-day VAH/VAL toward POC (value.vp.rth.trade is VAL present, not reject)
R-A02 | AMT | faithful | gap | n/a | ledge retest hold (value.kz is AM extreme near VAL/VAH, not a ledge retest) | n/a | n/a | n/a | n/a | n/a | ledge retest hold (value.kz is AM extreme near VAL/VAH, not a ledge retest)
R-A03 | AMT | faithful | gap | n/a | failed-auction traverse to opposite VA edge given re-entry | n/a | n/a | n/a | n/a | n/a | failed-auction traverse to opposite VA edge given re-entry
R-A04 | AMT | faithful | pass | 647 | open outside prior VA then two 30m periods inside (09:30-10:30) | 0.0587 | [0.043, 0.080] | 2024 0.045 / 2025 0.082 / 2026 0.045 | low 0.050 / mid 0.066 / high 0.061 | 0 | leakage 0
R-A05 | AMT | faithful | gap | n/a | POC chop vs through-and-retest split | n/a | n/a | n/a | n/a | n/a | POC chop vs through-and-retest split
R-A06 | AMT | faithful | gap | n/a | instant reject at naked prior POC after a balance break | n/a | n/a | n/a | n/a | n/a | instant reject at naked prior POC after a balance break
R-A07 | AMT | faithful | gap | n/a | break-retest hold at broken VAH/VAL/shelf/IB | n/a | n/a | n/a | n/a | n/a | break-retest hold at broken VAH/VAL/shelf/IB
R-A08 | AMT | faithful | gap | n/a | re-accept hold then opposite-edge reach | n/a | n/a | n/a | n/a | n/a | re-accept hold then opposite-edge reach
R-A09 | AMT | faithful | gap | n/a | b.c1 through both VA edges with no hold inside | n/a | n/a | n/a | n/a | n/a | b.c1 through both VA edges with no hold inside
R-A10 | AMT | faithful | pass | 647 | AMT open type is drive (first 30m vs prior VA) | 0.4096 | [0.372, 0.448] | 2024 0.385 / 2025 0.439 / 2026 0.404 | low 0.399 / mid 0.399 / high 0.429 | 0 | leakage 0
R-A11 | AMT | faithful | gap | n/a | next-session path class by prior profile shape | n/a | n/a | n/a | n/a | n/a | balance.vp-shape (OHLC 6-9 peak test returns double every session)
R-A12 | AMT | faithful | gap | n/a | value.vp.on LVN hold vs break at the open; FL-11 overnight delta sign | n/a | n/a | n/a | n/a | n/a | value.vp.on LVN hold vs break at the open; FL-11 overnight delta sign
R-A13 | AMT | faithful | pass | 647 | RTH touch of overnight high or low (18:00-09:30) | 0.8794 | [0.852, 0.902] | 2024 0.891 / 2025 0.869 / 2026 0.878 | low 0.904 / mid 0.859 / high 0.873 | 0 | leakage 0
R-A14 | AMT | faithful | gap | n/a | single-print fill, poor-extreme revisit, excess hold on first test | n/a | n/a | n/a | n/a | n/a | tpo.single fill / tpo.excess hold (value.tpo.rth.30m poor-extreme flag saturates)
R-A15 | AMT | faithful | pass | 647 | IB single-side extension after 10:30 (b.c1 beyond IB H or L) | 0.7991 | [0.766, 0.828] | 2024 0.802 / 2025 0.783 / 2026 0.821 | low 0.803 / mid 0.836 / high 0.764 | 0 | leakage 0
R-A16 | AMT | faithful | gap | n/a | reject at value.kz ledge stacked with VWAP / prior VA / naked POC | n/a | n/a | n/a | n/a | n/a | reject at value.kz ledge stacked with VWAP / prior VA / naked POC
R-A17 | AMT | faithful | gap | n/a | reject with vs without a second volume transition | n/a | n/a | n/a | n/a | n/a | reject with vs without a second volume transition
R-A18 | AMT | faithful | gap | n/a | single-print reach after rejection from the balance | n/a | n/a | n/a | n/a | n/a | single-print reach after rejection from the balance
R-F01 | Flow | faithful | gap | n/a | VWAP ±2SD reject plus flow.absorption.A (env.vwap.rth.sd2 is AM reach, not reject+absorption) | n/a | n/a | n/a | n/a | n/a | VWAP ±2SD reject plus flow.absorption.A (env.vwap.rth.sd2 is AM reach, not reject+absorption)
R-F02 | Flow | faithful | blocked | n/a | flow.cvd.trade divergence (tape-trusted no) | n/a | n/a | n/a | n/a | n/a | flow.cvd.trade divergence (tape-trusted no)
R-F03 | Flow | faithful | gap | n/a | env.vwap.anchored.* convergence | n/a | n/a | n/a | n/a | n/a | env.vwap.anchored.* convergence
R-F04 | Flow | faithful | gap | n/a | return to flow.footprint.stack3 (session stacked-4x flag is not a revisit) | n/a | n/a | n/a | n/a | n/a | return to flow.footprint.stack3 (session stacked-4x flag is not a revisit)
R-F05 | Flow | faithful | gap | n/a | flow.candle.poc.flip after candle-vs-delta disagreement | n/a | n/a | n/a | n/a | n/a | flow.candle.poc.flip after candle-vs-delta disagreement
R-F06 | Flow | faithful | gap | n/a | flow.absorption.A at shelf/ledge/VA (function is at 6-9 H/L); part 2 flow.absorption.B blocked; TR-19 pending | n/a | n/a | n/a | n/a | n/a | flow.absorption.A at shelf/ledge/VA (function is at 6-9 H/L); part 2 flow.absorption.B blocked; TR-19 pending
R-F07 | Flow | faithful | blocked | n/a | iceberg reload / flow.absorption.B (MBP-1 iceberg not-measurable; B fires every session) | n/a | n/a | n/a | n/a | n/a | iceberg reload / flow.absorption.B (MBP-1 iceberg not-measurable; B fires every session)
R-F08 | Flow | faithful | gap | n/a | flow.reward.3tick after absorption A at a real extreme; CVD-median blocked | n/a | n/a | n/a | n/a | n/a | flow.reward.3tick after absorption A at a real extreme; CVD-median blocked
R-F09 | Flow | faithful | gap | n/a | flow.digits.thinning and flow.reward.3tick; stage 2 flow.absorption.B blocked | n/a | n/a | n/a | n/a | n/a | flow.digits.thinning and flow.reward.3tick; stage 2 flow.absorption.B blocked
R-F10 | Flow | faithful | gap | n/a | lvl.protected.high/low | n/a | n/a | n/a | n/a | n/a | lvl.protected.high/low
R-F11 | Flow | faithful | gap | n/a | dp.max at value.kz LVN then k=5 wick reject | n/a | n/a | n/a | n/a | n/a | dp.max at value.kz LVN then k=5 wick reject
R-F12 | Flow | faithful | gap | n/a | flow.approach.speed | n/a | n/a | n/a | n/a | n/a | flow.approach.speed
R-F13 | Flow | faithful | gap | n/a | trap print + two prior-session failures then retest hold | n/a | n/a | n/a | n/a | n/a | trap print + two prior-session failures then retest hold
R-F14 | Flow | faithful | gap | n/a | flow.footprint.imb350 at the same price as a BigTrades print | n/a | n/a | n/a | n/a | n/a | flow.footprint.imb350 at the same price as a BigTrades print
R-F15 | Flow | faithful | gap | n/a | flow.ofm.sequence; FL-12 gamma (value.node.gamma not built, no strike IV) | n/a | n/a | n/a | n/a | n/a | flow.ofm.sequence; FL-12 gamma (value.node.gamma not built, no strike IV)
R-F16 | Flow | faithful | gap | n/a | absorption A at failed-aggression extreme; FL-12 long gamma | n/a | n/a | n/a | n/a | n/a | absorption A at failed-aggression extreme; FL-12 long gamma
R-F17 | Flow | faithful | gap | n/a | flow.refill.zone with 32-tick penetration / 12-tick rest (flow.refill.ontouch is a different event) | n/a | n/a | n/a | n/a | n/a | flow.refill.zone with 32-tick penetration / 12-tick rest (flow.refill.ontouch is a different event)
R-F18 | Flow | faithful | gap | n/a | flow.ofm.sequence non-failing squeeze + tape speed | n/a | n/a | n/a | n/a | n/a | flow.ofm.sequence non-failing squeeze + tape speed
R-R01 | Regime | faithful | gap | n/a | value.node.flip / GEX walls (no strike IV; OI top3 is not the flip). Do not use mapped NDX/SPX minutes | n/a | n/a | n/a | n/a | n/a | value.node.flip / GEX walls (no strike IV; OI top3 is not the flip). Do not use mapped NDX/SPX minutes
R-R02 | Regime | faithful | pass | 647 | VIX daily band 15-18 (lesson sweet spot) | 0.3910 | [0.354, 0.429] | 2024 0.235 / 2025 0.508 / 2026 0.455 | low 0.399 / mid 0.441 / high 0.340 | 0 | leakage 0
R-R03 | Regime | faithful | gap | n/a | thesis validity box | n/a | n/a | n/a | n/a | n/a | thesis validity box
R-R04 | Regime | faithful | blocked | n/a | SMT / IØD (flow.smt.* tape-trusted no; do not score flow.smt.pine.3-3) | n/a | n/a | n/a | n/a | n/a | SMT / IØD (flow.smt.* tape-trusted no; do not score flow.smt.pine.3-3)
R-S01 | Sires | faithful | gap | n/a | range.dealing bottom + flow.absorption.A | n/a | n/a | n/a | n/a | n/a | range.dealing bottom + flow.absorption.A
R-S02 | Sires | faithful | gap | n/a | third retest with no defending absorption A | n/a | n/a | n/a | n/a | n/a | third retest with no defending absorption A
R-S03 | Sires | faithful | gap | n/a | flow.digits.thinning; flow.absorption.B blocked | n/a | n/a | n/a | n/a | n/a | flow.digits.thinning; flow.absorption.B blocked
R-S04 | Sires | faithful | gap | n/a | value.delta.weekly trap + flow.footprint.imb350 + OFM | n/a | n/a | n/a | n/a | n/a | value.delta.weekly trap + flow.footprint.imb350 + OFM
R-S05 | Sires | faithful | gap | n/a | short-term microbalance b.c1 | n/a | n/a | n/a | n/a | n/a | short-term microbalance b.c1
R-S06 | Sires | faithful | gap | n/a | two-reason level (resistance + minor HVN within tR) | n/a | n/a | n/a | n/a | n/a | two-reason level (resistance + minor HVN within tR)
R-S07 | Sires | faithful | gap | n/a | MFE/MAE at 35-tick and 15-tick examples | n/a | n/a | n/a | n/a | n/a | MFE/MAE at 35-tick and 15-tick examples
R-S08 | Sires | faithful | gap | n/a | 5m minor node with negative delta stacking | n/a | n/a | n/a | n/a | n/a | 5m minor node with negative delta stacking
R-S09 | Sires | faithful | gap | n/a | developing current-day VAH break after 10:00 with TR-17 (ready-bar missing developing VAH) | n/a | n/a | n/a | n/a | n/a | developing current-day VAH break after 10:00 with TR-17 (ready-bar missing developing VAH)
R-P01 | Pine | faithful | gap | n/a | env.tbr.sigma025 touch then reversion to open by 12:00 | n/a | n/a | n/a | n/a | n/a | env.tbr.sigma025 touch then reversion to open by 12:00
R-P02 | Pine | faithful | gap | n/a | hourly sweep retrace to the swept level (range.gb.hour is path class of the hour box, not retrace) | n/a | n/a | n/a | n/a | n/a | hourly sweep retrace to the swept level (range.gb.hour is path class of the hour box, not retrace)
R-P03 | Pine | faithful | gap | n/a | magic-hour boxes Z1-Z6 | n/a | n/a | n/a | n/a | n/a | magic-hour boxes Z1-Z6
R-P04 | Pine | faithful | gap | n/a | grid.pine.raid5-120 | n/a | n/a | n/a | n/a | n/a | grid.pine.raid5-120
R-P05 | Pine | faithful | gap | n/a | London 25% body NY close-back counter | n/a | n/a | n/a | n/a | n/a | London 25% body NY close-back counter
R-P06 | Pine | faithful | gap | n/a | London-vs-Asia / NY-vs-London first-hit tables | n/a | n/a | n/a | n/a | n/a | London-vs-Asia / NY-vs-London first-hit tables
R-P07 | Pine | faithful | gap | n/a | OR midpoint retest 81.8-88.4% (open.oneway.OR is return to OR low, not midpoint) | n/a | n/a | n/a | n/a | n/a | OR midpoint retest 81.8-88.4% (open.oneway.OR is return to OR low, not midpoint)
R-P08 | Pine | faithful | pass | 647 | IB path class after 10:30 (break combo reduced to single / both / neither) | 0.7991 | [0.766, 0.828] | 2024 0.802 / 2025 0.783 / 2026 0.821 | low 0.803 / mid 0.836 / high 0.764 | 0 | leakage 0
R-P09 | Pine | faithful | gap | n/a | open vs prior RTH no-break rates | n/a | n/a | n/a | n/a | n/a | open vs prior RTH no-break rates
R-P10 | Pine | faithful | gap | n/a | daily floor pivots | n/a | n/a | n/a | n/a | n/a | daily floor pivots
R-P11 | Pine | faithful | gap | n/a | first-presented FVG fill/effectiveness (gap.fvg.first.clock is presence on the 09:00 hour) | n/a | n/a | n/a | n/a | n/a | first-presented FVG fill/effectiveness (gap.fvg.first.clock is presence on the 09:00 hour)
R-P12 | Pine | faithful | gap | n/a | HTF sweep + CISD screener body/wick/close variants | n/a | n/a | n/a | n/a | n/a | HTF sweep + CISD screener body/wick/close variants
R-P13 | Pine | faithful | pass | 647 | midnight-open (TDO) traded through in 09:30-12:00 | 0.5858 | [0.547, 0.623] | 2024 0.599 / 2025 0.570 / 2026 0.590 | low 0.615 / mid 0.554 / high 0.590 | 0 | leakage 0
R-P14 | Pine | faithful | gap | n/a | hod_lod_time 10:00 checkpoint | n/a | n/a | n/a | n/a | n/a | hod_lod_time 10:00 checkpoint
R-P15 | Pine | faithful | gap | n/a | env.pine.sessionstat / manipulation-distribution envelopes | n/a | n/a | n/a | n/a | n/a | env.pine.sessionstat / manipulation-distribution envelopes
R-P16 | Pine | faithful | pass | 647 | AM excursion inside VIX/16 band from 09:30 open | 0.7713 | [0.737, 0.802] | 2024 0.753 / 2025 0.811 / 2026 0.737 | low 0.817 / mid 0.770 / high 0.726 | 0 | leakage 0
R-P17 | Pine | faithful | gap | n/a | value.vp.rth.ohlc1m (RTH 1m OHLC VP with VA outcomes) and lvl.1800open | n/a | n/a | n/a | n/a | n/a | value.vp.rth.ohlc1m (RTH 1m OHLC VP with VA outcomes) and lvl.1800open
R-P18 | Pine | faithful | blocked | n/a | flow.cvd.ohlc as trigger | n/a | n/a | n/a | n/a | n/a | flow.cvd.ohlc as trigger
R-P19 | Pine | faithful | gap | n/a | body gap >=4 ticks near-edge fill (gap.body.adjacent is presence) | n/a | n/a | n/a | n/a | n/a | body gap >=4 ticks near-edge fill (gap.body.adjacent is presence)
R-P20 | Pine | faithful | gap | n/a | flow.delta.zone.kmeans / flow.vol.anomaly.zone on aggressor delta | n/a | n/a | n/a | n/a | n/a | flow.delta.zone.kmeans / flow.vol.anomaly.zone on aggressor delta

## Faithful Jumbo / AMT / flow still gap

Phase 1 is not done. Green Bird section B rows are pass. These Jumbo, AMT, and flow rows that RULES.md calls faithful are still impl_fidelity=gap.

id | missing function
---|---
R-J10 | leftover Asia/London/midnight reach after -0.5 reversal (draw list, not a location function)
R-J15 | flow.bigtrade.100ny/75ldn at the TBR level (session print flag is not at-level)
R-J16 | RTH VP/delta shape at EQ (value.delta.rth.trade is delta-vs-POC, not two-sided midpoint)
R-J17 | value.kz LVN under a TBR level (function is AM extreme near VAL/VAH)
R-J18 | 3-candle OB at -0.5 (block.sweep.tbr.3m is IB new-extreme continuation)
R-J19 | PDH/PDL reach given RTH open direction; HTF first-presented FVG fill
R-J20 | 10:00 release calendar (inventory has CPI/NFP at 08:30 and FOMC date-only, not 10:00)
R-J21 | TBR p.22-24 condition class (unfavourable / expansive calendar table)
R-J22 | 3-strike and extended-body failure-protocol counters
R-J24 | MFE/MAE at TBR p.16 exit rules
R-J25 | swing-mid retrace on trend-day sessions
R-A01 | grid reject at prior-day VAH/VAL toward POC (value.vp.rth.trade is VAL present, not reject)
R-A02 | ledge retest hold (value.kz is AM extreme near VAL/VAH, not a ledge retest)
R-A03 | failed-auction traverse to opposite VA edge given re-entry
R-A05 | POC chop vs through-and-retest split
R-A06 | instant reject at naked prior POC after a balance break
R-A07 | break-retest hold at broken VAH/VAL/shelf/IB
R-A08 | re-accept hold then opposite-edge reach
R-A09 | b.c1 through both VA edges with no hold inside
R-A11 | balance.vp-shape (OHLC 6-9 peak test returns double every session)
R-A12 | value.vp.on LVN hold vs break at the open; FL-11 overnight delta sign
R-A14 | tpo.single fill / tpo.excess hold (value.tpo.rth.30m poor-extreme flag saturates)
R-A16 | reject at value.kz ledge stacked with VWAP / prior VA / naked POC
R-A17 | reject with vs without a second volume transition
R-A18 | single-print reach after rejection from the balance
R-F01 | VWAP ±2SD reject plus flow.absorption.A (env.vwap.rth.sd2 is AM reach, not reject+absorption)
R-F03 | env.vwap.anchored.* convergence
R-F04 | return to flow.footprint.stack3 (session stacked-4x flag is not a revisit)
R-F05 | flow.candle.poc.flip after candle-vs-delta disagreement
R-F06 | flow.absorption.A at shelf/ledge/VA (function is at 6-9 H/L); part 2 flow.absorption.B blocked; TR-19 pending
R-F08 | flow.reward.3tick after absorption A at a real extreme; CVD-median blocked
R-F09 | flow.digits.thinning and flow.reward.3tick; stage 2 flow.absorption.B blocked
R-F10 | lvl.protected.high/low
R-F11 | dp.max at value.kz LVN then k=5 wick reject
R-F12 | flow.approach.speed
R-F13 | trap print + two prior-session failures then retest hold
R-F14 | flow.footprint.imb350 at the same price as a BigTrades print
R-F15 | flow.ofm.sequence; FL-12 gamma (value.node.gamma not built, no strike IV)
R-F16 | absorption A at failed-aggression extreme; FL-12 long gamma
R-F17 | flow.refill.zone with 32-tick penetration / 12-tick rest (flow.refill.ontouch is a different event)
R-F18 | flow.ofm.sequence non-failing squeeze + tape speed

## Not started

Phase 2 is not started. Section C one-slot swaps wait until the parent B row is pass.
