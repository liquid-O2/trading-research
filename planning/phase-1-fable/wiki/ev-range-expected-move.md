# EV range (AM expected-move envelope)

## Definition
The EV range is Jumbo's 2026 "AM vol expected range": a statistical stretch band for the New York morning around a reference price, computed from recent volatility `[XF p.7 L83]` `[PACK L17, L22–28]`. It is not a P-zone, not the 1.33 / 1.66 extension, and not the SessionStat 9–12 boundary `[PACK L28, L83]`. Its midpoint is its own target ID; the 6–9 EQ is a different target ID `[BRIEF]`. His exact estimator and reference price are unpublished → named variants.

## Citations
- 28 Aug 2026 recap lists "am vol expected range" beside the double-break expectancy split `[XF p.7 L81–83]` `[PACK L13–17]`; "discard mean reversion and range double breaks when these things align" `[PACK L35]`; inside prior value → "EQ / EV mean-revert" `[PACK L43]`.
- "expected mean reversion day, range breakouts likely to fail fast" `[XF p.16 L217]`.
- User asks for GK / YZ / HAR-RV based forward-vol modelling `[DTM L23]` `[JJX L147]`; vol estimators are features not a product `[BRIEF]`.
- Tier-2 analogues to recompute: TBR σ-bands (20-day stdev of daily % change, ±0.25σ touch, 78.4% reversion for hour-8 touches n=732) `[PINE AM TBR - NQ Stats.txt]`; sigma-per-anchor grids, 75.2% of days inside ±1 SD `[PINE NQ Stats Price Distributions.txt]`; manipulation / distribution average and median from open with 25/75 percentiles `[PINE Statistical OHLC Projections HTF.txt:322–341, 141–158]`; VIX/16 daily and VIX/√365 bands `[PINE Expected Volatility .txt]`; VIX → ES point table `[VIX4 p.4 L50–56]`.

## Faithful object
No published formula exists. Benchmark row `env.ev.mean60`: reference `ref.0930open`; band = ref ± mean over the prior 60 sessions of the AM excursions `max(H−ref)` and `max(ref−L)` measured 09:30–12:00, each side separately. Reported next to `env.ev.median60`, `env.ev.p75`, `env.ev.p90`.

## Upgrades
Estimator grid:
| id | band half-width |
|---|---|
| `env.ev.mean60` / `median60` / `p75` / `p90` | empirical AM excursion quantiles, 60 sessions |
| `env.ev.rv20` | 20-session close-to-close σ × √(2.5 h / 6.5 h) × ref |
| `env.ev.gk20` / `env.ev.yz20` | Garman–Klass / Yang–Zhang 20-session σ, same time scaling |
| `env.ev.har` | HAR-RV one-day forecast from 1-minute RV, scaled |
| `env.ev.iv` | ATM straddle-implied move from NDX (ThetaData quote-1m dte ≤ 14) or NQ.OPT 1m bars, scaled to the AM window `[INV L315, L104]` |
| `env.ev.vix16` | VIX / 16 · ref (tier-2 comparison) `[PINE Expected Volatility .txt]` |
| `env.ss.*` | SessionStat 9–12 rows → [sessionstat-9-12-envelope](sessionstat-9-12-envelope.md) |

Reference variants: `ref.0930open` (default), `ref.eq69`, `ref.0900close`, `ref.tdo`. Window variants: 09:30–12:00 (default), 09:30–10:30. Lookback 20 / 60 / 250 named. Every band emits its own midpoint ID `ev.mid.<variant>`.

## Outcomes
- reach, overshoot (band units), reject at band, time-to-touch, and whether the band level sits inside or outside prior RTH value (tag `in-value` / `out-of-value`) `[BRIEF]`.
- Coverage calibration: share of sessions whose AM H and L both fall inside the band (target ≈ the estimator's nominal quantile).
- Faithful disagreements: sessions where the row's reach label differs from `env.ev.mean60`.
- Coincidence with 1.33 / 1.66 and SessionStat levels (distance ≤ `tR`), reported as counts.

## Links
[sessionstat-9-12-envelope](sessionstat-9-12-envelope.md) · [extensions-1-33-1-66](extensions-1-33-1-66.md) · [p-zones-benchmark](p-zones-benchmark.md) · [vol-estimators](vol-estimators.md) · [open-location-switch](open-location-switch.md)
