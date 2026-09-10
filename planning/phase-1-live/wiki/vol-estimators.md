# Volatility estimators (features, not a product)

## Definition
Named volatility features attached to every session row and used as EV-range estimators: realized (RV from 1-minute returns, HAR-RV), range-based (Garman–Klass, Yang–Zhang), implied (ATM IV, 25-delta skew from NDX / NQ.OPT quotes), and VX term structure. They are features and regime slicers; no deployed forward-volatility product `[BRIEF]`.

## Citations
- User: forward-vol model with GK, YZ, HAR-RV `[DTM L23]`; regime better than VIX, using GK etc. `[JJX L147]`.
- Data: Cboe VX futures 2020 → 2026-09 `[INV L566–569]`; VVIX `[INV L559]`; VIX options `[INV L538–547]`; NDX quote-1m dte ≤ 14 / dte ≤ 60 ATM ±10 `[INV L315–322]`; NQ.OPT 1-minute bars `[INV L104]`; FRED volatility indices `[INV L685]`.
- Tier-2: the printed formula Expected Daily Move (%) = VIX / √252 (`[VIX4 p.3]` figure) with the "typical" ES point anchors (12.5 ≈ 30, 16 ≈ 50, 22 ≈ 95) and intraday VIX / ES divergence reads `[VIX4 p.3–4, p.6]`; VXN, the Cboe Nasdaq-100 twin, is in the inventory `[INV L610]` (named `vol.vxn`); VIX / 16 daily move `[PINE Expected Volatility .txt]`; 252-day vol scaling clamp `[PINE NQ Stats Price Distributions.txt]`; prior assistant regime proposal (GK / YZ + profile shape + NDX IV + hysteresis) `[CEX L70]` (tier 4).

## Faithful object
`vol.rv20`, `vol.gk20`, `vol.yz20` (20-session, daily 18:00–17:00 OHLC), `vol.har` (1/5/22-day RV), `vol.iv.atm` (09:25 snapshot, nearest dte ≥ 1 expiry, NDX or NQ.OPT), `vol.skew25`, `vol.vx.slope` (VX1 − VIX). Terciles per feature computed on F only (frozen).

## Upgrades
Window 10 / 20 / 60; overnight-only RV (18:00–09:30) as the "vol as of 09:29" variant.

## Outcomes
- Columns on every family report (regime slices); calibration of each as an EV-range estimator → [ev-range-expected-move](ev-range-expected-move.md).
- Reported, never used to select a variant.

## Links
[ev-range-expected-move](ev-range-expected-move.md) · [clock-grid-and-bars](clock-grid-and-bars.md) · [data-coverage](data-coverage.md)
