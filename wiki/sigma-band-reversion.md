# σ-band reversion (Pine AM TBR)

**Historical background — scope clarified 2026-09-12.** This retained note predates the current M01–M12 / O001–O166 contracts and is outside empirical v1. Its “faithful object,” upgrade and outcome sections describe earlier proposals; they do not report current implementation acceptance or measured results. Source/Pine constructions and old statistics remain distinct from author rules. See the [current method map](index.md), [status](current-status.md), [source catalog](source-catalog.md) and [historical review ledger](/workspace/planning/phase-1-from-scratch/REVIEW_LEDGER.md).

## Definition
A daily-volatility band around the 08:00 open: σ = sample standard deviation of daily % change over a lookback, the touch level at ±0.25σ, and reversion = price returning to the 08:00 open after a touch, tracked cumulatively by 09:00 / 10:00 / 11:00 / 12:00 `[PINE AM TBR - NQ Stats.txt:16, 78, 135–139, 336–357, 415–471]`. The script hardcodes hour-8 touch 78.4% n=732, hour-9 69.7% n=492 and cumulative reversion 27.9 / 68.2 / 76.1 / 78.4 by 09 / 10 / 11 / 12; those are tier-2 claims to recompute, never parameters ([sources-pine-archive](sources-pine-archive.md)). Id `env.tbr.sigma025`. It is an envelope, not the EV range and not SessionStat.

## Citations
- Construction: touch level input 0.25σ `[PINE AM TBR - NQ Stats.txt:16]`; sample stdev on the daily series `[:135–139]`; anchor at the 08:00 open, levels open ± mult·σ·open `[:340–357]`; 08:00–12:00 touch and reversion tracking, reversion = lower-timeframe return to the open `[:168–175, 415–471]`; MFE targets after reversion `[:305–317]`.
- Listed as a tier-2 analogue on [ev-range-expected-move](ev-range-expected-move.md).

## Faithful object
`env.tbr.sigma025`: anchor = 08:00:00 open on NQ; σ20 = sample stdev of the prior 20 daily close-to-close % changes (18:00–17:00 sessions); band = anchor ± 0.25·σ20·anchor; touch side = first band touched in 08:00–12:00 (1-minute bars); reversion = a 1-minute low ≤ anchor (upper touch) or high ≥ anchor (lower touch) after the touch; milestones by 09:00 / 10:00 / 11:00 / 12:00.

## Upgrades
- Multiplier 0.5 / 1.0; lookback 60; anchor 09:30 open; window 09:30–12:00.

## Outcomes
- Touch rate by hour of touch; cumulative reversion by milestone; max extension beyond the band in σ units; every hardcoded cell printed beside the recomputed cell on F and L.

## Links
[ev-range-expected-move](ev-range-expected-move.md) · [sessionstat-9-12-envelope](sessionstat-9-12-envelope.md) · [sources-pine-archive](sources-pine-archive.md)
