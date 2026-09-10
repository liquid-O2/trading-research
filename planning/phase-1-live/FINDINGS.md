# Phase 1 findings

Slice F is NY trade dates 2024-01-02 to 2026-08-31. Bar objects use n=647 eligible sessions unless noted. Tape objects use the holdout after a frozen discovery cut (n=429). Do not promote a row with tape trusted = no into a Phase 2 tape object.

object | n | unit | vs faithful | year note | tape trusted? | one sentence
---|---|---|---|---|---|---
range.6-9.published | 647 | sessions | measured | 2024 0.36 / 2025 0.32 / 2026 0.33 double-break | no | Faithful 06:00–09:00 box on 1s H/L and 1m path. Bar object only.
range.8-9 | 653 | sessions | better | 2024 0.44 / 2025 0.48 / 2026 0.45 vs 6–9 0.34 | no | Shorter 08:00–09:00 box has more double-breaks than published 6–9. Still a bar clock.
env.ev.mean60 | 647 | sessions | measured | reach 0.75 across years | no | AM envelope from 09:30 open using a 60-session mean. Distinct from SessionStat and P-zone.
env.ev.median60 | 647 | sessions | better | reach 0.87 vs mean 0.75 | no | Median estimator reaches more often than mean60. Same 09:30-open mid, not 6–9 EQ.
env.ss.avgHL60 | 647 | sessions | measured | reach 0.71–0.78 | no | 09:00–12:00 average H–L, not an EV alias.
env.ext.133.from-edge | 647 | sessions | measured | reach 0.38–0.43 | no | From-edge 1.33 extension of the 6–9 box. Separate id from EV and P-zone.
env.ext.166.from-edge | 647 | sessions | worse | reach 0.29–0.34 vs 1.33 | no | 1.66 reaches less than 1.33. Keep both ids.
open.switch.published | 647 | sessions | measured | 27 cells; 2024/25/26 double-break ~0.32–0.36 | no | Open vs prior value, prior range, and 6–9 independently. Trade VP vs OHLC-VP disagrees on 107 sessions.
range.gb.london vs range.london.00-03 | 648 / 643 | sessions | worse vs 6–9 | GB-London 0.17 double-break; Jumbo 00–03 0.19 | no | Two different clocks. Neither matches 6–9 path class.
fail.box.6-9.gb.c5 vs Judas | 647 | sessions | measured | fail-back 0.69; Judas is a path flag, not this grid | no | Fail-back after a wick of the 6–9 box is common. Judas stays on the path family.
flow.cvd.trade | 429 | sessions | measured | holdout 2024 n=29 only; rate 1.0 every year | no | Sign of MBP-1 CVD is almost always nonzero. Do not reuse as an event.
flow.smt.trade.nq | 429 | sessions | null vs ohlc.4 | rate 1.0 | no | Detector fires every holdout session. Not a reusable SMT event.
flow.smt.ohlc.4 | 429 | sessions | measured | rate 1.0 | no | Same saturation on 1m sisters. Not trusted as an event.
flow.absorption.A | 429 | sessions | measured | 2024 0.00 (n=29) / 2025 0.041 / 2026 0.045 | yes | MBP-1 2-minute q90 aggressive volume at the 6–9 touch, ≤2 ticks, then 0.25R reverse. Rare.
flow.absorption.B | 429 | sessions | better | rate 1.0 | no | BBO reload ≥50% in 500 ms twice fires every session. Too loose to reuse.
flow.bigtrade.100ny | 429 | sessions | measured | 2024 0.45 / 2025 0.87 / 2026 0.90 | yes | Source size ≥100 on NY hours. Discriminates. Keep with the quantile grid.
flow.bigtrade.75ldn | 429 | sessions | worse | 2024 0.14 / 2025 0.18 / 2026 0.34 | yes | Source size ≥75 in London hours. Different from 100ny.
flow.bigtrade.q90 | 429 | sessions | better | rate 1.0 | no | Frozen discovery q90 print size is 3 lots, so the flag is always on. Do not replace 100ny with it.
value.node.oi.ndx.top3 | 647 | sessions | measured | OI file present every F session | no | Native NDX OI nodes. Daily cash map. Not tape.
value.node.oi.ndxp.top3 | 647 | sessions | measured | full F coverage | no | Native NDXP. Listed separately from NDX.
value.node.oi.spx.top3 | 647 | sessions | measured | full F coverage | no | Native SPX. Not cash minutes.
value.node.oi.spxw.top3 | 647 | sessions | measured | full F coverage | no | Native SPXW. Not cash minutes.

Off-touch refill, hidden book, ES trade SMT, NWOG fill, ATM IV, NQ.OPT OI, dealer inventory, and Skylit stay not-measurable or deferred. They are not in this table.
