# TBR remaining clocks (midnight, RTH sub-windows, lunch, MOC)

## Definition
The five published time-based ranges from the TBR clock list that are not yet on the clock grid: the midnight opening range 00:00–00:30, the equities opening range 09:30–10:00 (the A period), the 10:00–10:30 window, the lunch opening range 12:00–12:30, and the MOC macro session 15:00–15:30 `[TBR p.7]`. Each carries the same internals as the 6–9 box on both sides, in its own height (`w.own`): H, L, open, close, EQ, Q25, Q75, the mean-reversal ladder 0.1 / 0.2 / 0.3 with its area, ±0.5, ±1.0, the 1.33 / 1.66 area, ±2 — the p.13 Scenario #2 chart draws the same ladder (−0.5 … −3) under the box — and the same outcome table `[TBR p.4–5, p.13]`. Ids: `range.midnight.0000-0030`, `range.rth.0930-1000`, `range.rth.1000-1030`, `range.lunch.1200-1230`, `range.moc.1500-1530`. Comparison rows: the 2026 record demotes lunch (a documented leak) and does not treat MOC as an A+ clock `[XF p.21]` `[FIND p.5–6]`.

## Citations
- Clock list with the four overnight and four RTH windows `[TBR p.7]`; 09:00–12:00 framed as one 3-hour window with the 09:30 open and the 09:40–09:50 window as entry / take-profit zones `[TBR p.16, p.19]`.
- AM / lunch / PM correlation (AM consolidation → PM expansion; AM expansion → PM consolidation) `[TBR p.36]`.
- "gave it all back during lunch trying to reach a daily target" `[XF p.21]`; lunch is not an A+ clock; AM expansion days often become PM consolidation `[FIND p.5–6]`.
- The A-period outcome rows `open.oneway.A.0930-1000` and `range.or.*` already exist on [open-location-switch](open-location-switch.md) and [clock-grid-and-bars](clock-grid-and-bars.md); this page adds the boxes, not the outcomes.

## Faithful object
Each id: H / L / open / close of the window on NQ 1-second bars, EQ, Q25, Q75, and on each side the mean-reversal ladder with `area.mr`, ±0.5, ±1.0, 1.33 / 1.66 with `band.133-166`, ±2.0, all in the box's own height (`w.own`; `w.69` and `w.ev` are named variants); `known_at` = window end. Outcome window (named default, not in the source): from window end to the next listed clock boundary (`range.midnight.0000-0030` → 03:00; `range.rth.0930-1000` → 12:00; `range.rth.1000-1030` → 12:00; `range.lunch.1200-1230` → 13:00; `range.moc.1500-1530` → 16:00), secondary to 16:00.

## Upgrades
- Bar type rows as on [clock-grid-and-bars](clock-grid-and-bars.md) (`bars.vol-elapsed`, `bars.dollar`, `bars.trade-count`); trade-level H / L.
- Outcome window to 16:00 for every row; London 03:00 handoff for the midnight box.

## Outcomes
- Same table as [tbr-6-9-range](tbr-6-9-range.md): path class, first-touch times, grid at every level, reversal-time bins.
- Faithful disagreements = sessions whose path class under the row differs from `range.6-9.published`; merge rows whose coverage tables cannot be told apart.
- Lunch and MOC rows are expected weak and print regardless.

## Links
[clock-grid-and-bars](clock-grid-and-bars.md) · [tbr-6-9-range](tbr-6-9-range.md) · [open-location-switch](open-location-switch.md) · `../RULES.md` A1.1
