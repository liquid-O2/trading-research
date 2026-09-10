# TBR 6–9 range (published Jumbo box)

## Definition
The overnight box is the high and low printed between 06:00 and 09:00 ET on NQ, the "ONS session, main New York model" `[TBR p.7 L111, p.8 L120–126]`. Internals: equilibrium (EQ, midpoint), 25% and 75% quadrants, range open (06:00 print) and range close (09:00 print) `[TBR p.4 L48–50]`. Projections beyond **each** edge, all in units of the box height and drawn on both sides of every chart (+0.5 … +2 above the high, −0.5 … −2 below the low) `[TBR p.9–10, p.13, p.20–21 chart labels]`: the "mean reversal levels" — three lines at 0.1 / 0.2 / 0.3 of the range beyond the edge with the shaded "area of mean reversal" running from the edge to ±0.5 `[TBR p.5 L60–66, p.8 L143, p.30 bar chart]` — the ±0.5 projection, ±1.0, the 1.33 / 1.66 retracement-reversal area `[TBR p.21 L260–261]` (own page) and ±2 (−2.5 / −3 also printed on p.13). The exhaustion location on a fade is the mean-reversal area beyond the swept edge, whichever side that is (the manual reverses from above the high on p.9 Trade #2 and p.13 Scenario #1, from below the low on p.10 Trade #1), with the wick allowed to poke a little past the printed level (p.10, p.20; tolerance unprinted). Range high and low are rails, not reversal zones `[BRIEF]`.

Published clocks inside the box model: Judas trade from 09:30 into the projections, reversal in the 09:40–09:50 window `[TBR p.8 L124–142]`; single-break scenarios where 09:40–09:50 is discarded as a reversal window `[TBR p.12 L165–190]` and the real reversal comes after 10:00 `[TBR p.18 L238–239]`; the whole framing is 09:00–12:00 `[TBR p.16 L216–220, p.30 L475]`.

## Citations
- Published statistics `[TBR p.30]`: 20 years E-mini Nasdaq, 4,537 days; 86.46% of reversals at the −0.5 projection in the 9:40–9:50 framing; average reversal time 09:47:36 (original window) and 09:51:05 (extended) — read off the page render, confirmed by zoom.
- Reversal share by projection depth in the 09:00–12:00 window, **both sides**, from the p.30 bar chart "Reversal % by Projection (Upper vs Lower)" (read from the archived page render; the earlier "p.12 table" citation was wrong): lower side 0.1 ≈ 87%, 0.2 ≈ 82%, 0.3 ≈ 78%, 0.5 ≈ 70%; upper side ≈ 85 / 80 / 74 / 66%. The same page's console prints "Extended Range: ±0.5 STDV", "Reversal Percentage from Extended Range = 86.46%" and two average reversal times (original range 09:47:36, extended range 09:51:05), so the 86.46% is recomputed in both readings — reversal at the ±0.5 line, and reversal from inside the edge → ±0.5 area — per side `[TBR p.30]`.
- 2026 use: "average time of reversal in the 9–12 window over 15 years, highest count 9:40–9:50" `[XF p.47 L624]`; "Full reversal during 9:40-9:50" `[XF p.29 L382]`; "almost any time window between 5am and 9am will behave similarly" `[XF p.7 L93]` `[PACK L49]`; "Simple 6-9 range and OR mid retracements" `[XF p.14 L187]`; "nothing beats being done in the first 20 mins" `[XF p.15 L205]`; ORs are reference only `[XF p.25 L317]` `[PACK L62]`; IB stats are not edge `[XF p.8 L106–107]`.
- Sessions correlation AM / Lunch / PM `[TBR p.36 L540–543]`. Failure signatures: extended bodies at projections, extended moves, 3-strike rule `[TBR p.37 L568–585]`.
- A third-party Pine file restates the same geometry (session 0600–0900, 25/50/75, ±0.5/1.0/2.0, 1.33/1.66, prior RTH H/L, 9:40–9:50 zone) `[PINE 6 to 9 Session and Levels.txt:1–120]`; it is not Jumbo's script and is not a source for this object — comparison rows only (FORMULAS.md §0.1).
- Extended overnight range vs purged/compressed range scenarios `[TBR p.12 L175–190, p.24 L315–328]`; user asks to improve the time ranges and adapt them `[DTM L19]` `[JJX L146–148]`.

## Faithful object
`range.6-9.published`: box = H/L of 06:00:00–08:59:59 ET on NQ 1-second bars (`cov.nq.ohlc1s`), EQ, Q25, Q75, open, close, and on **each side** the mean-reversal ladder `lvl.mr.0.1 / 0.2 / 0.3` with `area.mr` (edge → ±0.5), ±0.5, ±1.0, 1.33 / 1.66 with `band.133-166`, ±2.0 — every level a multiple of `W69`. A touch carries the overshoot reading `proj.overshoot.δ` (δ ∈ {2 ticks, 0.1·W}, named; the charts draw the overshoot, no tolerance is printed). Width base of the ladder: `w.69` (faithful); `w.london` / `w.own` for the other clocks; `w.ev` is a named test variant only — no source states an EV-width projection (the "EVrange −60%" chart label `[PACK L24]` is unexplained). Two width tables, never mixed:
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
- First-touch time to EQ, Q25, Q75, open, close, the mean-reversal ladder 0.1 / 0.2 / 0.3, ±0.5, ±1.0, 1.33, the band, 1.66, ±2 per side; touch / reject / hold / break at each level under the shared grid, with and without the overshoot reading; the swept side as a column.
- Reversal-at-projection rate in 09:00–12:00 per depth and per side (recompute of the TBR p.30 bars and of the 86.46% in both readings on F and on L); reversal-time histogram in 5-minute bins (09:40–09:50 share vs first 20 minutes vs 10:00–10:30).
- Mid-retrace rate after a break (his 60.4% `[XF p.23 L290]`).
- Report line: `range | 6-9.published | n | 0 | measured | path`.

## Links
[range-path-class](range-path-class.md) · [open-location-switch](open-location-switch.md) · [clock-grid-and-bars](clock-grid-and-bars.md) · [extensions-1-33-1-66](extensions-1-33-1-66.md) · [ev-range-expected-move](ev-range-expected-move.md) · [session-fail-boxes](session-fail-boxes.md)
