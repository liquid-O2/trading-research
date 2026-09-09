# TBR 6–9 range (published Jumbo box)

## Definition
The overnight box is the high and low printed between 06:00 and 09:00 ET on NQ, the "ONS session, main New York model" `[TBR p.7 L111, p.8 L120–126]`. Internals: equilibrium (EQ, midpoint), 25% and 75% quadrants, range open (06:00 print) and range close (09:00 print) `[TBR p.4 L48–50]`. Projections beyond each edge: −0.5 "mean reversal" level `[TBR p.5 L60–66, p.8 L143]`, 1.0, and the 1.33 / 1.66 retracement-reversal levels `[TBR p.21 L260–261]` (own page). Range high and low are rails, not reversal zones `[BRIEF]`.

Published clocks inside the box model: Judas trade from 09:30 into the projections, reversal in the 09:40–09:50 window `[TBR p.8 L124–142]`; single-break scenarios where 09:40–09:50 is discarded as a reversal window `[TBR p.12 L165–190]` and the real reversal comes after 10:00 `[TBR p.18 L238–239]`; the whole framing is 09:00–12:00 `[TBR p.16 L216–220, p.30 L475]`.

## Citations
- Published statistics `[TBR p.30]`: 20 years E-mini Nasdaq, 4,537 days; 86.46% of reversals at the −0.5 projection in the 9:40–9:50 framing; average reversal time 09:47:36 (original window) and 09:51:05 (extended) — read off the page render, confirmed by zoom.
- Reversal share by projection depth in the 09:00–12:00 window `[TBR p.12, table read by zoom]`: lower side 0.1 ≈ 87%, 0.2 ≈ 82%, 0.3 ≈ 78%, 0.5 ≈ 70%; upper side ≈ 85 / 80 / 74 / 66%.
- 2026 use: "average time of reversal in the 9–12 window over 15 years, highest count 9:40–9:50" `[XF p.47 L624]`; "Full reversal during 9:40-9:50" `[XF p.29 L382]`; "almost any time window between 5am and 9am will behave similarly" `[XF p.7 L93]` `[PACK L49]`; "Simple 6-9 range and OR mid retracements" `[XF p.14 L187]`; "nothing beats being done in the first 20 mins" `[XF p.15 L205]`; ORs are reference only `[XF p.25 L317]` `[PACK L62]`; IB stats are not edge `[XF p.8 L106–107]`.
- Sessions correlation AM / Lunch / PM `[TBR p.36 L540–543]`. Failure signatures: extended bodies at projections, extended moves, 3-strike rule `[TBR p.37 L568–585]`.
- Pine restatement of the same geometry: session 0600–0900, 25/50/75 levels, ±0.5/1.0/2.0 deviations, 1.33/1.66 extensions, prior RTH H/L, 9:40–9:50 zone `[PINE 6 to 9 Session and Levels.txt:1–120]`.
- Extended overnight range vs purged/compressed range scenarios `[TBR p.12 L175–190, p.24 L315–328]`; user asks to improve the time ranges and adapt them `[DTM L19]` `[JJX L146–148]`.

## Faithful object
`range.6-9.published`: box = H/L of 06:00:00–08:59:59 ET on NQ 1-second bars (`cov.nq.ohlc1s`), EQ, Q25, Q75, open, close, −0.5 / +1.0 projections each side, 1.33 / 1.66 each side. Two width tables, never mixed:
- `W69` = H69−L69 in points; XF p.24 % bins use `w.pct.0859close` = W69 / 08:59:59 close × 100 (alt `w.pct.0930open`).
- `WpriorRTH` = prior RTH (09:30–16:00) H−L in points; `w.rel-prior-rth` = W69 / WpriorRTH. Ratio bins [0,.3), [.3,.5), [.5,.8), [.8,1.2), [1.2,∞) are **not** the XF price-% table.
Zero `WpriorRTH` → unavailable. Outcome window default 09:30–12:00, secondary 09:30–10:30 and 09:30–16:00.

## Upgrades
- Clock family: → [clock-grid-and-bars](clock-grid-and-bars.md). Bars: `range.6-9.vol-elapsed` (box closes when cumulative volume since 06:00 reaches the 60-session median of 06:00–09:00 volume), `range.6-9.dollar-bars` (same with notional). No free-form morning box `[BRIEF]`.
- Level source: `range.6-9.trade-level` (H/L from trades, tick precision) vs 1-second bars; disagreement expected ≤ 1 tick.
- Width tables: XF p.24 price-% buckets on `w.pct.*`, and a **separate** `w.rel-prior-rth` table. Never relabel one as the other.

## Outcomes
Same table for every variant:
- Path class and break order → [range-path-class](range-path-class.md).
- First-touch time to EQ, Q25, Q75, open, close, −0.5, 1.0, 1.33, 1.66 per side; touch / reject / hold / break at each level under the shared grid.
- Reversal-at-projection rate in 09:00–12:00 (recompute of TBR p.30 and p.12 on F and on L); reversal-time histogram in 5-minute bins (09:40–09:50 share vs first 20 minutes vs 10:00–10:30).
- Mid-retrace rate after a break (his 60.4% `[XF p.23 L290]`).
- Report line: `range | 6-9.published | n | 0 | measured | path`.

## Links
[range-path-class](range-path-class.md) · [open-location-switch](open-location-switch.md) · [clock-grid-and-bars](clock-grid-and-bars.md) · [extensions-1-33-1-66](extensions-1-33-1-66.md) · [ev-range-expected-move](ev-range-expected-move.md) · [session-fail-boxes](session-fail-boxes.md)
