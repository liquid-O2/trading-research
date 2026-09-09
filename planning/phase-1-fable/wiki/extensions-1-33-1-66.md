# Extensions 1.33 / 1.66

## Definition
Levels at 1.33 and 1.66 times the box height, projected beyond the box high and low, from the 6–9 range (and from the London box when London is the clock) `[TBR p.21 L260–261]` `[PACK L66, L82]` `[JJX L53]`. They are retracement / reversal levels for single-break days, monitored for interaction `[TBR p.21]`, and the fork for compressed-AM → PM expansion `[FIND p.6 L125]`. They are not P-zones and must not be called ATL `[BRIEF]`.

## Citations
- "1.33 1.66 Retracement/Reversal levels… monitor the interaction at these levels" `[TBR p.21 L259–261]`; chart shows −133% / −166% under the low, 28 Jul 2026 `[PACK L66]`; Pine geometry: fib ext 1.33/1.66 from H/L of the 06:00–09:00 session `[PINE 6 to 9 Session and Levels.txt]`; TBR-style ±1.0 / ±2.0 deviations in the same file.
- Lock: width table uses 6–9 H−L and prior RTH H−L; extensions come from the 6–9 range, not P-zones `[BRIEF]`.

## Faithful object
`env.ext.133.from-edge` and `env.ext.166.from-edge`: level = H + k·(H−L) above, L − k·(H−L) below, k ∈ {1.33, 1.66}, box = `range.6-9.published`. Sibling rows `env.ext.100` (measured move) and `env.ext.050` (the −0.5 projection, shared with the 6–9 page).

## Upgrades
- Box source: `range.london.00-03` (London row) `[PACK L82]`; any grid clock as a comparison.
- Anchor: from edge (faithful) vs from EQ (`env.ext.133.from-eq`) — named because the manual's figure anchors at the edge and some Pine files anchor at open.

## Outcomes
- Touch rate by 12:00 and by 16:00; touch / reject / hold / break under the grid; time-to-touch; order of touch relative to −0.5 and 1.0.
- PM-expansion fork: on compressed-AM sessions (`w.rel-prior-rth ≤ 0.5`), rate of reaching 1.33 and 1.66 after 12:00.
- Coincidence with SessionStat and EV levels.
- Faithful disagreements: sessions whose touch label differs from `env.ext.133.from-edge`.

## Links
[tbr-6-9-range](tbr-6-9-range.md) · [sessionstat-9-12-envelope](sessionstat-9-12-envelope.md) · [ev-range-expected-move](ev-range-expected-move.md) · [p-zones-benchmark](p-zones-benchmark.md)
