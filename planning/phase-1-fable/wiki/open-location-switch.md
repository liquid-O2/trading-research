# Open-location switch

## Definition
Where the 09:30 RTH open prints relative to three references: (a) prior RTH value area (VAL–VAH of the prior 09:30–16:00 profile), (b) prior RTH range (PDL–PDH), (c) the current 6–9 box (below / inside / above; quadrant when inside) `[XF p.8 L118: "RTH open location in relation to previous day value/range and the current day 6-9"]`. The switch as used in 2026: open inside prior value / range → mean-reversion morning, breakouts likely to fail fast, EQ / EV targets `[XF p.16 L217–218]` `[PACK L38, L43]`; open outside prior value **and** prior range, with above-average RVOL → do not run the double-break fade `[PACK L40, L44]`. Double-break expectancy is split in-value vs in-range `[XF p.7 L81]` `[PACK L15]`.

## Citations
- Open-location table, 28 Jul 2026, 09:30–10:30 window `[XF p.11, confirmed by zoom]`:

| open location | n | high-only | low-only | both | one side |
|---|---|---|---|---|---|
| below VAL, inside prior range | 396 | 29.5 | 37.6 | 29.8 | 67.2 |
| below VAL and below PDL | 517 | 23.6 | 46.2 | 27.3 | 69.8 |

- 9 Jul 2026 claim: open outside prior value and range with RVOL above average → about 76% of A-period (09:30–10:00) stays one-way, 15-year sample; recompute `[PACK L40]`.
- Pine tier-2 (recompute): open above prior RTH → 84.11% no break of prior low; below → 81.82% no break of prior high; inside → 14.30% stays, 72.66% one side, 13.04% both `[PINE NQ Stats RTH Breaks with stats.txt]`; floor-pivot gap context (open above PDH 20.5% of days, R1 touch 65.9%; below PDL 11.3%, S1 touch 71.5%; within 68.2%, PP touch 69.5%) `[PINE Daily Floor Pivots.txt:1159–1196]`; NY open vs Asia box bucket `[PINE NY vs Asia Statistical Levels.txt]`.

## Faithful object
`open.switch.published`: 3 × 3 × 3 cell = (vs value: below / in / above) × (vs range: below / in / above) × (vs 6–9: below / in / above). His table names two cells; all 27 are emitted, sparse cells reported with n. Value area = prior RTH trade-level VP at 70% (→ [value-and-profiles](value-and-profiles.md)). Outcome window 09:30–10:30 to match his table, plus 09:30–12:00.

## Upgrades
- Value source: trade-level VP vs OHLC-1m VP (Pine-style) — two rows, disagreement counted.
- VA width 70% vs 68% `[RTVP p.4]` vs 40% intraday `[C3 p.7 L105]`.
- RVOL flag as a label only: 09:30–09:35 volume / 60-session median; threshold 1.0 and 1.5 named.
- Double-break expectancy split: `open.dbx.in-value` vs `open.dbx.in-range-not-value` vs `open.dbx.outside-both`.

## Outcomes
- Path class shares per cell (recompute of XF p.11 rows on F and L; cell difference = faithful disagreements).
- Double-break rate per cell; one-way A-period rate per cell (recompute of the 76% claim).
- Mid-retrace and EQ-reach rate per cell.

## Links
[range-path-class](range-path-class.md) · [value-and-profiles](value-and-profiles.md) · [ev-range-expected-move](ev-range-expected-move.md) · [tbr-6-9-range](tbr-6-9-range.md)
