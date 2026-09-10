# Extensions 1.33 / 1.66

## Definition
Levels at 1.33 and 1.66 times the box height projected beyond **both** the box high and the box low, with the shaded band between them, from the 6–9 range (and from the London box when London is the clock) `[TBR p.21 L260–261]` `[PACK L66, L82]` `[JJX L53]`. The manual draws the area below the low (p.21: band −1.33 … −1.66, the "Retracement" box holding inside it, the "Reversal" box with the wick poking through −1.66) and his charts draw it above the high (TBR p.10 +1.33 / +1.66; XF p.48 "1.33 1.66 end of day max expansion" band above the high). They are a retracement / reversal **area** for single-break days, monitored for interaction `[TBR p.21]`, the fork for compressed-AM → PM expansion `[FIND p.6 L125]`, and London range exhaustion when the London box is the clock `[XF p.25]`. They are not P-zones and must not be called ATL `[BRIEF]`.

## Citations
- "1.33 1.66 Retracement/Reversal levels… monitor the interaction at these levels" `[TBR p.21 L259–261]`; chart shows −133% / −166% under the low, 28 Jul 2026 `[PACK L66]`; the coordinate is fixed by his own chart labels (−133% / −166% under the low = 1.33 / 1.66 range-multiples beyond the edge) `[PACK L66]`; the FIND replication fib list `[FIND p.16]` read literally would give the from-origin reading and is kept only as a named alternative; the Pine archive file `6 to 9 Session and Levels.txt` is a third-party restatement, not Jumbo's script, and is not a source for this object. The area is shaded on both sides across his charts (`[TBR p.10, p.21]` `[XF p.31, p.33, p.48]`) and the reversal wick may overshoot 1.66 slightly (`[TBR p.21]` `[XF p.31]`; tolerance unprinted).
- Lock: width table uses 6–9 H−L and prior RTH H−L; extensions come from the 6–9 range, not P-zones `[BRIEF]`.

## Faithful object
`env.ext.133.from-edge` and `env.ext.166.from-edge` (**beyond-edge**): level = H + k·(H−L) above, L − k·(H−L) below, k ∈ {1.33, 1.66}, box = `range.6-9.published`, always both sides; `band.133-166` = the closed interval between them on each side (the shaded area; a touch inside it is a band touch); `proj.overshoot.δ` = the touch still counts with an excursion ≤ δ past 1.66, δ ∈ {2 ticks, 0.1·W} (named). Width is always `W69` (`w.london` when the London row is the source, `w.own` for the other clocks), never a P-zone; `w.ev` is a named test variant only — no source states an EV-width extension. Sibling rows `env.ext.100` (measured move), `env.ext.050` (the ±0.5 projection) and `lvl.mr.*` (the mean-reversal ladder, on the 6–9 page).

## Upgrades
- Box source: `range.london.00-03` (London row) `[PACK L82]`; any grid clock as a comparison.
- Coordinate: **beyond-edge** (faithful: his chart labels `[PACK L66]` and the TBR p.21 figure) vs **range-origin** `env.ext.133.from-origin` = L+k·W / H−k·W (`MTF OHLC Lines with Breakout & Retracement Labels.txt:293–307`). These disagree; both are printed.
- Anchor: from edge vs from EQ (`env.ext.133.from-eq`) — a named comparison only; not drawn on any Jumbo chart.
- Width base: `w.69` (faithful) | `w.london` | `w.own` | `w.ev` (test only). Level set per RULES §C SL-proj: ±0.5 | ±1.33 | ±1.66 | band | overshoot δ, each side.

## Outcomes
- Touch rate by 12:00 and by 16:00 per side (1.33, inside the band, 1.66, overshoot); touch / reject / hold / break under the grid; time-to-touch; order of touch relative to ±0.5 and ±1.0.
- PM-expansion fork: on compressed-AM sessions (`w.rel-prior-rth ≤ 0.5`), rate of reaching 1.33 and 1.66 after 12:00 on the AM-leg side; reject-inside-band vs continue-beyond-1.66 shares; end-of-day max expansion = the RTH extreme inside the band `[XF p.48]`.
- Coincidence with SessionStat and EV levels.
- Faithful disagreements: sessions whose touch label differs from `env.ext.133.from-edge`.

## Links
[tbr-6-9-range](tbr-6-9-range.md) · [sessionstat-9-12-envelope](sessionstat-9-12-envelope.md) · [ev-range-expected-move](ev-range-expected-move.md) · [p-zones-benchmark](p-zones-benchmark.md)
