# P-zones (benchmark approximation)

## Definition
Jumbo's "P-zones" (probability zones) are grey boxes at distance bands from a clock anchor; the formula is unpublished `[PACK L81]` `[FIND p.2 L24, p.6 L129–130]`. 2026 usage is one-liners: "9:30 pzone" (4 Aug 2026) `[XF p.8 L115]`, "10am pzone" `[XF p.16 L224]`, "10 am p-zone > london low" `[FIND p.5 L101]`, 18:00 P-zones on gold Sundays `[FIND p.3 L64]`; the sweep extends to "exhaustion (−0.5 / mean-reversal / P-zone)" `[FIND p.4 L77–78]`. Phase 1 benchmarks a disclosed approximation and its upgrades; a learned reversal model is Phase 3 `[BRIEF]`.

## Citations
- Distance-band boxes drawn from a time anchor (gold Sunday figure: P-zone boxes, EQ, RTH range) `[FIND p.6 L129–130]`; Discord / indicator naming stays proprietary `[XF p.30 L405]`.
- Pine analogues of "time-anchored expected excursion boxes": Range Projections Statistical Levels percentile levels per session `[PINE Range Projections Statistical Levels.txt]`; Session Range Projections RE×1…6 `[PINE Session Range Projections with stats.txt]`; magic-hour zones Z1–Z6 by extension % `[PINE magic_hours:145–184]`.

## Faithful object
None published. Screenshot UI shows a 500-session learning window, percentile scaling, T1/T2 and optional T3/T4, invalidation deletion `[XF p.34–39]`. That is appearance, not a formula.

Benchmark `pz.approx.A` (disclosed-distance-approximation): at clock `t` ∈ {09:00, 09:30, 10:00} use the completed 6–9 midpoint as the 09:00 anchor (other clocks use last print at `t`). From the last **500** available completed sessions of the matching horizon, take nonnegative upper and lower excursions from each session’s corresponding anchor. Freeze nearest-rank percentile boundaries 50/75/90/95/99. Adjacent boundaries form four distance bands (labeled T1–T4 as **approximation tiers**, not a claim to recover original T1–T4). Insufficient history is warmup. This is not his formula.

## Upgrades
- `pz.approx.B`: boxes at 0.5·R and 1.0·R beyond the 6–9 edges (R = box height) — the "distance bands" reading.
- History-60 vs history-500; quantile pairs (25/75 vs 50/90 vs 50/75/90/95/99); anchor 09:00 / 09:30 / 10:00 / 18:00 (18:00 on NQ only; gold out of scope).
- `vol-scaled`: current available 6–9 GK/RV scale divided by the historical median of that scale.
- `similar-vol-tercile` historical filter; `formation-volume-filter` above the prior-60 median vs none.
- `VP-node-snap` to the nearest already-known node within one current band width vs no snapping `[FIND p.7–8]`.
- Retirement: none vs completed 1-minute close beyond the band’s far edge.
- Learned P-zone: **deferred to Phase 3** (row printed as `deferred`).

## Outcomes
- Touch / reject / hold / break at box edges (grid); reversal-inside-box rate = reject with `r=0.5`; time-to-touch.
- When EV band, −0.5 projection and P-zone box disagree on where the AM extreme printed, which one was closest (distance ranking, no P&L).
- Faithful disagreements: sessions whose reject label differs from `pz.approx.A`.

## Links
[ev-range-expected-move](ev-range-expected-move.md) · [extensions-1-33-1-66](extensions-1-33-1-66.md) · [tbr-6-9-range](tbr-6-9-range.md)
