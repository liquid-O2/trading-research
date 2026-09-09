# P-zones (benchmark approximation)

## Definition
Jumbo's "P-zones" (probability zones) are grey boxes at distance bands from a clock anchor; the formula is unpublished `[PACK L81]` `[FIND p.2 L24, p.6 L129–130]`. 2026 usage is one-liners: "9:30 pzone" (4 Aug 2026) `[XF p.8 L115]`, "10am pzone" `[XF p.16 L224]`, "10 am p-zone > london low" `[FIND p.5 L101]`, 18:00 P-zones on gold Sundays `[FIND p.3 L64]`; the sweep extends to "exhaustion (−0.5 / mean-reversal / P-zone)" `[FIND p.4 L77–78]`. Phase 1 benchmarks a disclosed approximation and its upgrades; a learned reversal model is Phase 3 `[BRIEF]`.

## Citations
- Distance-band boxes drawn from a time anchor (gold Sunday figure: P-zone boxes, EQ, RTH range) `[FIND p.6 L129–130]`; Discord / indicator naming stays proprietary `[XF p.30 L405]`.
- Pine analogues of "time-anchored expected excursion boxes": Range Projections Statistical Levels percentile levels per session `[PINE Range Projections Statistical Levels.txt]`; Session Range Projections RE×1…6 `[PINE Session Range Projections with stats.txt]`; magic-hour zones Z1–Z6 by extension % `[PINE magic_hours:145–184]`.

## Faithful object
None published. Benchmark `pz.approx.A`: anchor price = last print at clock `t` ∈ {09:30, 10:00}; box_k = [q25, q75] of the distribution of `max excursion from anchor over the next 60 minutes` on the prior 60 sessions, drawn each side; outer box = [q75, q90]. This is the disclosed approximation; it is not his formula.

## Upgrades
- `pz.approx.B`: boxes at 0.5·R and 1.0·R beyond the 6–9 edges (R = box height) — the "distance bands" reading.
- Quantile pairs (25/75 vs 50/90), lookback 20 / 60 / 250, anchor 09:30 vs 10:00 vs 18:00 (18:00 measured on NQ only as a comparison row; gold is out of scope).
- Learned P-zone: **deferred to Phase 3** (row printed as `deferred`).

## Outcomes
- Touch / reject / hold / break at box edges (grid); reversal-inside-box rate = reject with `r=0.5`; time-to-touch.
- When EV band, −0.5 projection and P-zone box disagree on where the AM extreme printed, which one was closest (distance ranking, no P&L).
- Faithful disagreements: sessions whose reject label differs from `pz.approx.A`.

## Links
[ev-range-expected-move](ev-range-expected-move.md) · [extensions-1-33-1-66](extensions-1-33-1-66.md) · [tbr-6-9-range](tbr-6-9-range.md)
