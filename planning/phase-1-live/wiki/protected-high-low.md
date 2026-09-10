# Protected high / low

## Definition
A swing the market has already defended once `[ANAT p.3]`. Ethos forms it from delta: buying aggression clearly outweighs selling at the recent low, price forms a small balance and escapes it, and once that low is confirmed and price stops coming back to test it, it is a protected low; partials go below the sellers who defended it, the stop trails behind each new protected level `[RD p.4–5]`. The mirror on the short side: once price takes out the first swing low with enough aggression to close below it, that high becomes a protected high `[K18 p.8]`, a level defended by real covering `[K18 p.12]`. Ids `lvl.protected.high`, `lvl.protected.low`.

## Citations
- Protected low, partial below the defenders, only confirmed lows `[RD p.4]`; trailing protected low after protected low; a break of the highest-delta protected low = traversing `[RD p.5]`; protected highs and trailing convexity `[K18 p.8–9, p.14]`; covering vs dealer hedging `[K18 p.12]`; glossary and checklist `[ANAT p.3, p.10]`; stop trailed to the most recent protected low `[K2345 p.7]`.

## Faithful object
`lvl.protected.low`: a confirmed 5-bar fractal low on 1-minute NQ bars whose per-price delta at the swing (`value.delta.rth.trade` bins within 2 ticks) is ≥ q75 of the session's positive per-price delta (q75, the 5-bar fractal and the 5-bar quiet window are named; the source prints no numbers), followed by a 1-minute close above the prior swing high (escape) with no `t2` touch of the low in the next 5 bars; `known_at` = the escape close; protection ends at `b.c1` through the low. `lvl.protected.high` is the mirror. `[unmeasured]` (delta condition); the bar-only version (fractal + escape, no delta) is a named row.

## Upgrades
- Fractal 3 / 7; delta quantile q50 / q90; escape by `b.c5`; delta-free row.

## Outcomes
- Break rate and time-to-break; MFE from formation to break (points); count of protected levels per trend leg; share of breaks that traverse the full range (RD's "traversing to the stop").

## Links
[value-and-profiles](value-and-profiles.md) · [dealing-range](dealing-range.md) · [delta-spike](delta-spike.md) · [sweep-cisd-blocks](sweep-cisd-blocks.md)
