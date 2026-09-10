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
R-J01 | Jumbo | faithful | pass | 647 | G-default reject at deepest mean-reversal or ±0.5 ladder level, both sides, 09:40-09:50 | 0.0294 | [0.019, 0.045] | 2024 0.024 / 2025 0.029 / 2026 0.038 | low 0.028 / mid 0.042 / high 0.019 | 0 | leakage 0
R-J02 | Jumbo | faithful | pass | 647 | 09:30 open reaches -0.5 before 09:40 | 0.7063 | [0.670, 0.740] | 2024 0.704 / 2025 0.725 / 2026 0.679 | low 0.733 / mid 0.692 / high 0.692 | 0 | leakage 0
R-J03 | Jumbo | faithful | pass | 647 | single-break on extended overnight, EQ retrace with h=15 by 10:00 | 0.0000 | [-0.000, 0.006] | 2024 0.000 / 2025 0.000 / 2026 0.000 | low 0.000 / mid 0.000 / high 0.000 | 0 | leakage 0
R-J04 | Jumbo | faithful | pass | 647 | overnight Asia and London both swept by 09:30, single-break reach of 1.0 | 0.0294 | [0.019, 0.045] | 2024 0.053 / 2025 0.025 / 2026 0.000 | low 0.041 / mid 0.023 / high 0.024 | 0 | leakage 0
R-J05 | Jumbo | faithful | pass | 647 | single-break midretrace to EQ / range open | 0.1855 | [0.157, 0.217] | 2024 0.162 / 2025 0.180 / 2026 0.231 | low 0.203 / mid 0.168 / high 0.185 | 0 | leakage 0
R-J06 | Jumbo | faithful | pass | 647 | open_cell path class; outside-both + RVOL double-break | 0.0680 | [0.051, 0.090] | 2024 0.049 / 2025 0.086 / 2026 0.071 | low 0.069 / mid 0.079 / high 0.057 | 0 | leakage 0
R-J07 | Jumbo | faithful | pass | 647 | path class by w.pct.0859close bin (XF p.24 recompute lives on range.6-9.published) | 0.3385 | [0.303, 0.376] | 2024 0.360 / 2025 0.320 / 2026 0.333 | low 0.346 / mid 0.341 / high 0.336 | 0 | leakage 0
R-J08 | Jumbo | faithful | pass | 647 | PM reject at 1.33-1.66 band or 1.33 line, both sides, width = 6-9 box | 0.0216 | [0.013, 0.036] | 2024 0.016 / 2025 0.029 / 2026 0.019 | low 0.023 / mid 0.019 / high 0.024 | 0 | leakage 0
R-J09 | Jumbo | faithful | pass | 647 | London 00-03 box -0.5 reject in 03:00-06:00 | 0.0649 | [0.048, 0.087] | 2024 0.101 / 2025 0.053 / 2026 0.026 | low 0.069 / mid 0.093 / high 0.033 | 0 | leakage 0
R-J10 | Jumbo | faithful | pass | 647 | nearest untouched Asia/London/PDH/PDL draw reached in AM | 0.3617 | [0.326, 0.399] | 2024 0.356 / 2025 0.352 / 2026 0.385 | low 0.364 / mid 0.379 / high 0.346 | 0 | leakage 0
R-J11 | Jumbo | faithful | pass | 647 | SessionStat avgHL60 reach (median and min-average are named variants) | 0.7496 | [0.715, 0.781] | 2024 0.761 / 2025 0.713 / 2026 0.788 | low 0.737 / mid 0.706 / high 0.806 | 0 | leakage 0
R-J12 | Jumbo | faithful | pass | 647 | P-zone T1 reach with band overlapping 6-9 L, low > OP, Model A, reject at -0.5 | 0.0015 | [0.000, 0.009] | 2024 0.004 / 2025 0.000 / 2026 0.000 | low 0.000 / mid 0.005 / high 0.000 | 0 | leakage 0
R-J13 | Jumbo | faithful | pass | 647 | env.ev.mean60 reach; reject is not a separate EV function, reach is the sourced working-level event | 0.2411 | [0.210, 0.276] | 2024 0.279 / 2025 0.213 / 2026 0.224 | low 0.235 / mid 0.248 / high 0.242 | 0 | leakage 0
R-J14 | Jumbo | faithful | pass | 647 | 3m absorption candle at a 6-9 level, trailing SMA14, body/range <=0.3, k=2.5 | 0.0108 | [0.005, 0.022] | 2024 0.004 / 2025 0.012 / 2026 0.019 | low 0.009 / mid 0.019 / high 0.005 | 0 | leakage 0
R-J15 | Jumbo | faithful | pass | 647 | BigTrades >=100 at -0.5/EQ in NY AM, or >=75 in London | 0.0139 | [0.007, 0.026] | 2024 0.028 / 2025 0.004 / 2026 0.006 | low 0.018 / mid 0.014 / high 0.005 | 0 | leakage 0
R-J16 | Jumbo | faithful | pass | 647 | two-sided trade volume at EQ within 2 ticks | 0.2859 | [0.252, 0.322] | 2024 0.304 / 2025 0.270 / 2026 0.282 | low 0.300 / mid 0.285 / high 0.275 | 0 | leakage 0
R-J17 | Jumbo | faithful | pass | 647 | LVN or shelf under EQ or -0.5 in the 6-9 trade profile | 0.4189 | [0.381, 0.457] | 2024 0.413 / 2025 0.406 / 2026 0.449 | low 0.373 / mid 0.453 / high 0.431 | 0 | leakage 0
R-J18 | Jumbo | faithful | pass | 647 | 3-candle OB at -0.5 on 3m AM bars | 0.0263 | [0.016, 0.042] | 2024 0.020 / 2025 0.045 / 2026 0.006 | low 0.037 / mid 0.019 / high 0.024 | 0 | leakage 0
R-J19 | Jumbo | faithful | pass | 647 | PDH/PDL touch given open direction | 0.7125 | [0.676, 0.746] | 2024 0.676 / 2025 0.734 / 2026 0.737 | low 0.705 / mid 0.710 / high 0.725 | 0 | leakage 0
R-J20 | Jumbo | faithful | pass | 217 | 10:00 FRED release day and first -0.5 touch in 10:00-10:30 | 0.1797 | [0.134, 0.236] | 2024 0.250 / 2025 0.139 / 2026 0.130 | low 0.227 / mid 0.151 / high 0.160 | 0 | denominator is FRED 10:00 ET release days (ISM-like: JOLTS, Michigan, new homes, factory orders, inventories, construction)
R-J21 | Jumbo | faithful | pass | 647 | condition class extended (red-folder or w.rel-prior-rth >= 1) | 0.0386 | [0.026, 0.056] | 2024 0.036 / 2025 0.041 / 2026 0.038 | low 0.028 / mid 0.042 / high 0.047 | 0 | leakage 0
R-J22 | Jumbo | faithful | pass | 647 | three-strike failure protocol at -0.5 | 0.1236 | [0.100, 0.151] | 2024 0.146 / 2025 0.135 / 2026 0.071 | low 0.138 / mid 0.136 / high 0.090 | 0 | leakage 0
R-J23 | Jumbo | faithful | pass | 643 | path class of TBR published clocks including midnight / A-period / lunch / MOC | 0.4526 | [0.414, 0.491] | 2024 0.463 / 2025 0.465 / 2026 0.416 | n/a (clock table) | 0 | clocks range.midnight.0000-0030 and the other TBR published boxes; rate is midnight double-break. Lunch and MOC are comparison clocks.
R-J24 | Jumbo | faithful | pass | 647 | MFE after -0.5 entry by 09:50 is positive | 0.9969 | [0.989, 0.999] | 2024 1.000 / 2025 0.992 / 2026 1.000 | low 1.000 / mid 0.995 / high 0.995 | 0 | leakage 0
R-J25 | Jumbo | faithful | pass | 647 | swing-mid retrace hold on a single-break session | 0.0000 | [-0.000, 0.006] | 2024 0.000 / 2025 0.000 / 2026 0.000 | low 0.000 / mid 0.000 / high 0.000 | 0 | leakage 0
R-G01 | Green Bird | faithful | pass | 647 | NYAM 09:00-10:00 wick then 5m close-back after 10:00 | 0.7233 | [0.688, 0.756] | 2024 0.717 / 2025 0.738 / 2026 0.712 | low 0.733 / mid 0.757 / high 0.687 | 0 | leakage 0
R-G02 | Green Bird | faithful | pass | 647 | Asia 20:00-00:00 wick then 5m close-back 00:00-06:00 | 0.7110 | [0.675, 0.745] | 2024 0.713 / 2025 0.701 / 2026 0.724 | low 0.696 / mid 0.738 / high 0.697 | 0 | leakage 0
R-G03 | Green Bird | faithful | pass | 4529 | last completed clock-hour box fail-back | 0.6337 | [0.620, 0.648] | 2024 0.621 / 2025 0.636 / 2026 0.649 | low 0.614 / mid 0.637 / high 0.652 | 0 | n is completed clock-hour boxes (7 x sessions). Event is wick then 5m close-back on the next hour.
R-G04 | Green Bird | faithful | pass | 647 | sweep below 09:30 open then 5m close reclaim | 0.8114 | [0.779, 0.840] | 2024 0.810 / 2025 0.791 / 2026 0.846 | low 0.811 / mid 0.785 / high 0.839 | 0 | leakage 0
R-G05 | Green Bird | faithful | pass | 647 | TDO wick then 5m close back through midnight open | 0.3400 | [0.305, 0.377] | 2024 0.300 / 2025 0.357 / 2026 0.378 | low 0.364 / mid 0.322 / high 0.336 | 0 | leakage 0
R-G06 | Green Bird | faithful | pass | 125 | Monday NWOG fill by 12:00 (Friday 16:00 close vs Sunday 18:00 open) | 0.5280 | [0.441, 0.613] | 2024 0.574 / 2025 0.396 / 2026 0.667 | low 0.525 / mid 0.558 / high 0.512 | 0 | denominator is Mondays; 16:00 fill not computed (AM 09:30-12:00 overlap only)
R-G07 | Green Bird | faithful | pass | 647 | touch of NYAM 50-61.8% golden pocket after 10:00, measured from impulse end | 0.7094 | [0.673, 0.743] | 2024 0.721 / 2025 0.680 / 2026 0.737 | low 0.728 / mid 0.710 / high 0.697 | 0 | leakage 0
R-G08 | Green Bird | faithful | pass | 647 | overnight sweep of PDH/PDL then close back through before 09:30 | 0.3771 | [0.341, 0.415] | 2024 0.340 / 2025 0.344 / 2026 0.487 | low 0.378 / mid 0.350 / high 0.403 | 0 | leakage 0
R-G09 | Green Bird | faithful | pass | 1 | PDH + Asia high + London high stacked within 0.05 R, Monday NWOG fill | 1.0000 | [0.207, 1.000] | 2024 1.000 / 2025 n/a / 2026 n/a | low 1.000 / mid n/a / high n/a | 0 | stacked PDH+Asia+London within 0.05 R; fill on those Mondays
R-G10 | Green Bird | faithful | pass | 647 | NYAM fail-back plus 10-11 fail-back (fade count >= 2) | 0.4544 | [0.416, 0.493] | 2024 0.462 / 2025 0.418 / 2026 0.500 | low 0.475 / mid 0.458 / high 0.436 | 0 | leakage 0
R-G11 | Green Bird | faithful | pass | 647 | label.aplus = NYAM/Asia/10-11 sweep plus fail-back. Sweep-only is a named weaker label. | 0.9474 | [0.927, 0.962] | 2024 0.931 / 2025 0.975 / 2026 0.929 | low 0.949 / mid 0.944 / high 0.948 | 0 | leakage 0
R-A01 | AMT | faithful | pass | 647 | G-default reject at prior VAL/VAH | 0.0788 | [0.060, 0.102] | 2024 0.057 / 2025 0.074 / 2026 0.122 | low 0.074 / mid 0.084 / high 0.081 | 0 | leakage 0
R-A02 | AMT | faithful | pass | 647 | AM prints at the prior VAL/VAH ledge | 0.6229 | [0.585, 0.659] | 2024 0.611 / 2025 0.607 / 2026 0.667 | low 0.622 / mid 0.589 / high 0.659 | 0 | leakage 0
R-A03 | AMT | faithful | pass | 647 | failed-auction re-entry then traverse to the opposite VA edge | 0.0634 | [0.047, 0.085] | 2024 0.081 / 2025 0.045 / 2026 0.064 | low 0.046 / mid 0.098 / high 0.047 | 0 | leakage 0
R-A04 | AMT | faithful | pass | 647 | open outside prior VA then two 30m periods inside (09:30-10:30) | 0.0587 | [0.043, 0.080] | 2024 0.045 / 2025 0.082 / 2026 0.045 | low 0.055 / mid 0.061 / high 0.062 | 0 | leakage 0
R-A05 | AMT | faithful | pass | 647 | POC chop (two touches, no through-and-hold) | 0.3369 | [0.302, 0.374] | 2024 0.336 / 2025 0.340 / 2026 0.333 | low 0.346 / mid 0.336 / high 0.332 | 0 | leakage 0
R-A06 | AMT | faithful | pass | 647 | RTH POC untraded overnight (naked POC) | 0.4900 | [0.452, 0.528] | 2024 0.466 / 2025 0.520 / 2026 0.481 | low 0.498 / mid 0.481 / high 0.488 | 0 | leakage 0
R-A07 | AMT | faithful | pass | 647 | IB break, retest, hold | 0.0155 | [0.008, 0.028] | 2024 0.016 / 2025 0.016 / 2026 0.013 | low 0.018 / mid 0.019 / high 0.009 | 0 | leakage 0
R-A08 | AMT | faithful | pass | 647 | re-accept hold after a VA break | 0.0340 | [0.023, 0.051] | 2024 0.061 / 2025 0.020 / 2026 0.013 | low 0.023 / mid 0.070 / high 0.009 | 0 | leakage 0
R-A09 | AMT | faithful | pass | 647 | b.c1 through both VA edges with no 30-min hold inside | 0.0433 | [0.030, 0.062] | 2024 0.045 / 2025 0.037 / 2026 0.051 | low 0.032 / mid 0.061 / high 0.038 | 0 | leakage 0
R-A10 | AMT | faithful | pass | 647 | AMT open type is drive (first 30m never trades back through the 09:30 open) | 0.2179 | [0.188, 0.251] | 2024 0.206 / 2025 0.230 / 2026 0.218 | low 0.217 / mid 0.248 / high 0.190 | 0 | leakage 0
R-A11 | AMT | faithful | pass | 647 | prior RTH P-shape then single-break path | 0.0000 | [-0.000, 0.006] | 2024 0.000 / 2025 0.000 / 2026 0.000 | low 0.000 / mid 0.000 / high 0.000 | 0 | leakage 0
R-A12 | AMT | faithful | pass | 647 | 09:30 open at an overnight LVN | 0.1144 | [0.092, 0.141] | 2024 0.117 / 2025 0.107 / 2026 0.122 | low 0.106 / mid 0.112 / high 0.118 | 0 | leakage 0
R-A13 | AMT | faithful | pass | 647 | RTH 09:30-16:00 touch of overnight 18:00-09:30 high or low | 0.9536 | [0.935, 0.967] | 2024 0.968 / 2025 0.947 / 2026 0.942 | low 0.968 / mid 0.967 / high 0.924 | 0 | leakage 0
R-A14 | AMT | faithful | pass | 647 | TPO poor extreme or excess hold | 1.0000 | [0.994, 1.000] | 2024 1.000 / 2025 1.000 / 2026 1.000 | low 1.000 / mid 1.000 / high 1.000 | 0 | leakage 0
R-A15 | AMT | faithful | pass | 647 | IB single-side extension after 10:30 (b.c1 beyond IB H or L) | 0.7991 | [0.766, 0.828] | 2024 0.802 / 2025 0.783 / 2026 0.821 | low 0.811 / mid 0.822 / high 0.768 | 0 | leakage 0
R-A16 | AMT | faithful | pass | 647 | ledge stacked with AM VWAP or prior VAH within tR | 0.0278 | [0.018, 0.044] | 2024 0.016 / 2025 0.045 / 2026 0.019 | low 0.032 / mid 0.019 / high 0.033 | 0 | leakage 0
R-A17 | AMT | faithful | pass | 647 | second volume transition in the RTH trade profile | 0.0958 | [0.075, 0.121] | 2024 0.093 / 2025 0.086 / 2026 0.115 | low 0.083 / mid 0.098 / high 0.109 | 0 | leakage 0
R-A18 | AMT | faithful | pass | 647 | AM high reaches prior VAH | 0.6198 | [0.582, 0.656] | 2024 0.628 / 2025 0.611 / 2026 0.622 | low 0.636 / mid 0.636 / high 0.592 | 0 | leakage 0
R-F01 | Flow | faithful | pass | 647 | 18:00 session VWAP ±2 running bands, both sides (±1 is the named at-least row) | 0.7898 | [0.757, 0.819] | 2024 0.785 / 2025 0.828 / 2026 0.737 | low 0.829 / mid 0.804 / high 0.739 | 0 | leakage 0
R-F02 | Flow | faithful | blocked | n/a | flow.cvd.trade divergence (FORMULAS.md blocked; MBP-1 extract exists, not gap) | n/a | n/a | n/a | n/a | n/a | flow.cvd.trade divergence (FORMULAS.md blocked; MBP-1 extract exists, not gap)
R-F03 | Flow | faithful | pass | 647 | AM VWAP, overnight VWAP, and prior VA mid within tR | 0.0031 | [0.001, 0.011] | 2024 0.008 / 2025 0.000 / 2026 0.000 | low 0.005 / mid 0.005 / high 0.000 | 0 | leakage 0
R-F04 | Flow | faithful | pass | 647 | stacked 4x footprint then AM trade back through the zone | 0.7311 | [0.696, 0.764] | 2024 0.668 / 2025 0.721 / 2026 0.846 | low 0.664 / mid 0.724 / high 0.806 | 0 | leakage 0
R-F05 | Flow | faithful | pass | 647 | AM candle vs delta disagreement | 0.7573 | [0.723, 0.789] | 2024 0.765 / 2025 0.721 / 2026 0.801 | low 0.728 / mid 0.790 / high 0.763 | 0 | leakage 0
R-F06 | Flow | faithful | pass | 647 | absorption A at prior VAL/VAH; absorption B stays blocked | 0.0325 | [0.021, 0.049] | 2024 0.045 / 2025 0.020 / 2026 0.032 | low 0.028 / mid 0.042 / high 0.028 | 0 | leakage 0
R-F07 | Flow | faithful | blocked | n/a | iceberg reload / flow.absorption.B (MBP-1 iceberg not-measurable; B fires every session) | n/a | n/a | n/a | n/a | n/a | iceberg reload / flow.absorption.B (MBP-1 iceberg not-measurable; B fires every session)
R-F08 | Flow | faithful | pass | 647 | 3-tick reward after AM absorption; CVD-median stays blocked | 0.4992 | [0.461, 0.538] | 2024 0.526 / 2025 0.512 / 2026 0.436 | low 0.507 / mid 0.491 / high 0.498 | 0 | leakage 0
R-F09 | Flow | faithful | pass | 647 | print-size thinning in AM; stage 2 absorption B stays blocked | 0.0000 | [-0.000, 0.006] | 2024 0.000 / 2025 0.000 / 2026 0.000 | low 0.000 / mid 0.000 / high 0.000 | 0 | leakage 0
R-F10 | Flow | faithful | pass | 647 | protected AM low: last 5 prints stay above the AM low by 2 ticks | 0.9985 | [0.991, 1.000] | 2024 1.000 / 2025 0.996 / 2026 1.000 | low 1.000 / mid 1.000 / high 0.995 | 0 | leakage 0
R-F11 | Flow | faithful | pass | 647 | RTH POC within tR of an LVN | 0.0232 | [0.014, 0.038] | 2024 0.004 / 2025 0.033 / 2026 0.038 | low 0.023 / mid 0.009 / high 0.038 | 0 | leakage 0
R-F12 | Flow | faithful | pass | 647 | aggressive arrival: AM size median rising (slope rule; no invented q75) | 0.8624 | [0.834, 0.887] | 2024 0.826 / 2025 0.857 / 2026 0.929 | low 0.820 / mid 0.855 / high 0.915 | 0 | leakage 0
R-F13 | Flow | faithful | pass | 647 | AM tags 6-9 high then closes back below | 0.2968 | [0.263, 0.333] | 2024 0.308 / 2025 0.299 / 2026 0.276 | low 0.276 / mid 0.308 / high 0.308 | 0 | leakage 0
R-F14 | Flow | faithful | pass | 647 | 350% imbalance tick plus a BigTrades print at a TBR level | 0.0139 | [0.007, 0.026] | 2024 0.028 / 2025 0.004 / 2026 0.006 | low 0.018 / mid 0.014 / high 0.005 | 0 | leakage 0
R-F15 | Flow | faithful | pass | 647 | stacked footprint without on-touch refill; gamma stays None | 0.7264 | [0.691, 0.759] | 2024 0.660 / 2025 0.717 / 2026 0.846 | low 0.654 / mid 0.724 / high 0.801 | 0 | leakage 0
R-F16 | Flow | faithful | pass | 647 | absorption A at prior VA after AM tags 6-9 high; gamma stays None | 0.0232 | [0.014, 0.038] | 2024 0.032 / 2025 0.020 / 2026 0.013 | low 0.018 / mid 0.028 / high 0.024 | 0 | leakage 0
R-F17 | Flow | faithful | pass | 647 | on-touch refill zone from MBP-1 | 0.0062 | [0.002, 0.016] | 2024 0.012 / 2025 0.004 / 2026 0.000 | low 0.009 / mid 0.005 / high 0.005 | 0 | leakage 0
R-F18 | Flow | faithful | pass | 647 | stacked footprint without refill; tape-speed cut stays unspecified | 0.7264 | [0.691, 0.759] | 2024 0.660 / 2025 0.717 / 2026 0.846 | low 0.654 / mid 0.724 / high 0.801 | 0 | leakage 0
R-R01 | Regime | faithful | pass | 647 | QQQ short-gamma from inverted quote IV, OI, and BS gamma (09:30-09:35) | 0.4049 | [0.368, 0.443] | 2024 0.360 / 2025 0.406 / 2026 0.474 | low 0.304 / mid 0.388 / high 0.512 | 0 | leakage 0
R-R02 | Regime | faithful | pass | 647 | prior-session VIXCLS close in band 15-18 | 0.3910 | [0.354, 0.429] | 2024 0.231 / 2025 0.508 / 2026 0.462 | low 0.396 / mid 0.439 / high 0.346 | 0 | leakage 0
R-R03 | Regime | faithful | pass | 647 | open-vs-VA thesis still alive at 12:00 | 0.6151 | [0.577, 0.652] | 2024 0.652 / 2025 0.594 / 2026 0.590 | low 0.627 / mid 0.636 / high 0.588 | 0 | leakage 0
R-R04 | Regime | faithful | blocked | n/a | SMT / IØD (FORMULAS.md blocked until user SMT is the scored object; extract exists, not gap) | n/a | n/a | n/a | n/a | n/a | SMT / IØD (FORMULAS.md blocked until user SMT is the scored object; extract exists, not gap)
R-S01 | Sires | faithful | pass | 647 | absorption A at the 6-9 low then AM close above it | 0.0402 | [0.028, 0.058] | 2024 0.049 / 2025 0.033 / 2026 0.038 | low 0.037 / mid 0.051 / high 0.033 | 0 | leakage 0
R-S02 | Sires | faithful | pass | 647 | third test from above of prior VAL band, or from below of prior VAH (continuation through) | 0.1020 | [0.081, 0.128] | 2024 0.126 / 2025 0.111 / 2026 0.051 | low 0.143 / mid 0.098 / high 0.066 | 0 | leakage 0
R-S03 | Sires | faithful | pass | 647 | print-size thinning; absorption B stays blocked | 0.0000 | [-0.000, 0.006] | 2024 0.000 / 2025 0.000 / 2026 0.000 | low 0.000 / mid 0.000 / high 0.000 | 0 | leakage 0
R-S04 | Sires | faithful | pass | 647 | 350% imbalance with a BigTrades print | 0.0139 | [0.007, 0.026] | 2024 0.028 / 2025 0.004 / 2026 0.006 | low 0.018 / mid 0.014 / high 0.005 | 0 | leakage 0
R-S05 | Sires | faithful | pass | 647 | microbalance break after the first 10 minutes | 0.9969 | [0.989, 0.999] | 2024 0.996 / 2025 0.996 / 2026 1.000 | low 0.991 / mid 1.000 / high 1.000 | 0 | leakage 0
R-S06 | Sires | faithful | pass | 647 | 6-9 high stacked with an RTH HVN within tR | 0.0386 | [0.026, 0.056] | 2024 0.040 / 2025 0.041 / 2026 0.032 | low 0.037 / mid 0.042 / high 0.033 | 0 | leakage 0
R-S07 | Sires | faithful | pass | 647 | AM MAE under 15 ticks from the first print | 0.0294 | [0.019, 0.045] | 2024 0.028 / 2025 0.029 / 2026 0.032 | low 0.037 / mid 0.023 / high 0.028 | 0 | leakage 0
R-S08 | Sires | faithful | pass | 647 | RTH profile has at least two HVNs, or a 6-9 LVN under a TBR level | 0.4436 | [0.406, 0.482] | 2024 0.441 / 2025 0.426 / 2026 0.474 | low 0.406 / mid 0.472 / high 0.450 | 0 | leakage 0
R-S09 | Sires | faithful | pass | 647 | open above developing VAH then break/retest after 10:00 | 0.1731 | [0.146, 0.204] | 2024 0.186 / 2025 0.160 / 2026 0.173 | low 0.161 / mid 0.192 / high 0.171 | 0 | leakage 0
R-P01 | Pine | faithful | pass | 647 | 08:00 TBR 0.25-sigma touch then reversion to the open by 12:00 | 0.6136 | [0.576, 0.650] | 2024 0.628 / 2025 0.574 / 2026 0.654 | low 0.696 / mid 0.589 / high 0.569 | 0 | leakage 0
R-P02 | Pine | faithful | pass | 647 | hourly sweep then retrace to the swept edge | 0.9845 | [0.972, 0.992] | 2024 0.988 / 2025 0.980 / 2026 0.987 | low 0.977 / mid 0.991 / high 0.986 | 0 | leakage 0
R-P03 | Pine | faithful | pass | 647 | magic-hour box retrace to mid before the hard stop | 1.0000 | [0.994, 1.000] | 2024 1.000 / 2025 1.000 / 2026 1.000 | low 1.000 / mid 1.000 / high 1.000 | 0 | leakage 0
R-P04 | Pine | faithful | pass | 647 | NYAM raid >=5 pts then close back inside within 120 min | 0.5904 | [0.552, 0.628] | 2024 0.583 / 2025 0.598 / 2026 0.590 | low 0.590 / mid 0.561 / high 0.616 | 0 | leakage 0
R-P05 | Pine | faithful | pass | 647 | London 25% body, NY wick or fail | 0.5549 | [0.516, 0.593] | 2024 0.555 / 2025 0.545 / 2026 0.571 | low 0.558 / mid 0.579 / high 0.526 | 0 | leakage 0
R-P06 | Pine | faithful | pass | 647 | London first-hit of Asia H/L | 0.8006 | [0.768, 0.830] | 2024 0.781 / 2025 0.807 / 2026 0.821 | low 0.825 / mid 0.836 / high 0.739 | 0 | leakage 0
R-P07 | Pine | faithful | pass | 647 | 5m OR midpoint retest after 09:35 | 0.8516 | [0.822, 0.877] | 2024 0.862 / 2025 0.857 / 2026 0.827 | low 0.839 / mid 0.855 / high 0.867 | 0 | leakage 0
R-P08 | Pine | faithful | pass | 647 | IB path class after 10:30 (break combo reduced to single / both / neither) | 0.7991 | [0.766, 0.828] | 2024 0.802 / 2025 0.783 / 2026 0.821 | low 0.811 / mid 0.822 / high 0.768 | 0 | leakage 0
R-P09 | Pine | faithful | pass | 647 | open vs prior RTH, no-break of the far side or stay inside | 0.4575 | [0.419, 0.496] | 2024 0.466 / 2025 0.484 / 2026 0.404 | low 0.442 / mid 0.514 / high 0.417 | 0 | leakage 0
R-P10 | Pine | faithful | pass | 647 | daily floor pivot PP touched in RTH | 0.8253 | [0.794, 0.853] | 2024 0.846 / 2025 0.828 / 2026 0.788 | low 0.829 / mid 0.850 / high 0.806 | 0 | leakage 0
R-P11 | Pine | faithful | pass | 647 | first-presented FVG on the 09:30 hour, fill or presence | 0.9969 | [0.989, 0.999] | 2024 0.992 / 2025 1.000 / 2026 1.000 | low 1.000 / mid 0.995 / high 0.995 | 0 | leakage 0
R-P12 | Pine | faithful | pass | 647 | sweep then close back through the prior bar high | 0.2056 | [0.176, 0.238] | 2024 0.198 / 2025 0.209 / 2026 0.212 | low 0.203 / mid 0.201 / high 0.213 | 0 | leakage 0
R-P13 | Pine | faithful | pass | 647 | midnight-open (TDO) traded through in 08:00-16:00 | 0.7110 | [0.675, 0.745] | 2024 0.725 / 2025 0.734 / 2026 0.654 | low 0.733 / mid 0.687 / high 0.720 | 0 | leakage 0
R-P14 | Pine | faithful | pass | 647 | HOD already in by 10:00 | 0.2952 | [0.261, 0.331] | 2024 0.283 / 2025 0.295 / 2026 0.314 | low 0.304 / mid 0.322 / high 0.261 | 0 | leakage 0
R-P15 | Pine | faithful | pass | 647 | Session Statistical Levels p50 MFE from the open | 0.3632 | [0.327, 0.401] | 2024 0.356 / 2025 0.348 / 2026 0.397 | low 0.341 / mid 0.327 / high 0.417 | 0 | leakage 0
R-P16 | Pine | faithful | pass | 647 | 18:00-16:00 inside log-space VIX/16 a/b 1.0 zone from prior settle and prior VIX | 0.4250 | [0.387, 0.463] | 2024 0.429 / 2025 0.496 / 2026 0.308 | low 0.493 / mid 0.416 / high 0.365 | 0 | leakage 0
R-P17 | Pine | faithful | pass | 647 | 18:00 open touched in RTH | 0.6213 | [0.583, 0.658] | 2024 0.648 / 2025 0.635 / 2026 0.558 | low 0.608 / mid 0.664 / high 0.597 | 0 | leakage 0
R-P18 | Pine | faithful | blocked | n/a | flow.cvd.ohlc as trigger (FORMULAS.md blocked) | n/a | n/a | n/a | n/a | n/a | flow.cvd.ohlc as trigger (FORMULAS.md blocked)
R-P19 | Pine | faithful | pass | 647 | adjacent body gap >= 4 ticks | 0.0386 | [0.026, 0.056] | 2024 0.024 / 2025 0.045 / 2026 0.051 | low 0.014 / mid 0.047 / high 0.057 | 0 | leakage 0
R-P20 | Pine | faithful | pass | 647 | AM print >=100 lots and range >= 8 ticks | 0.6569 | [0.619, 0.692] | 2024 0.498 / 2025 0.730 / 2026 0.795 | low 0.627 / mid 0.645 / high 0.692 | 0 | leakage 0

## Faithful Jumbo / AMT / flow still gap

Phase 1 is not done. Green Bird section B rows are pass. These Jumbo, AMT, and flow rows that RULES.md calls faithful are still impl_fidelity=gap.

id | missing function
---|---

## Not started

Phase 2 is not started. Section C one-slot swaps wait until the parent B row is pass.
