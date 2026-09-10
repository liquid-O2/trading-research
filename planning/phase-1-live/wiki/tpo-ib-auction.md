# TPO, IB, and AMT day/open labels

One thin family. Jumbo 2026 demotes OR/IB as the **main** box `[XF p.8 L106–107]` `[PACK L62]`; those stay comparison rows on [clock-grid-and-bars](clock-grid-and-bars.md). This page keeps TPO geometry and AMT labels because the PDFs define computable objects.

## Definition
**TPO:** 30-minute letters, A = 09:30–10:00, B = 10:00–10:30; POC = max time-at-price; **single prints** = rows visited by one period; **excess** = ≥2 tail rows of the same letter; **poor extreme** = weak/no completed tail `[TPO p.3–10]`. **IB:** first RTH hour, A+B `[TPO p.8–10]`. **AMT day labels:** trend, normal, normal variation, neutral, non-trend `[AMT1 p.10–14]`. **AMT open labels:** drive, test-drive, rejection-reverse, auction `[AMT1 p.10–14]`. Keep AMT and Jumbo day-class taxonomies separate `[wiki/range-path-class.md]`.

## Citations
- tpo-lesson-3.pdf letters, excess, poor extremes; some page images clipped `[TPO p.3–10]`.
- Unfilled single prints as destinations `[C3 p.6]`.
- mastering-amt-vp four-class appendix; class percentages not exhaustive `[MAMT p.19–23]`.
- First 30m TPO entirely above prior VAH as an observed sequence `[AUT p.21–24]`.
- Pine IB/ORB hardcoded tables: comparison only `[PINE Initial Balance Statistical Mapping.txt]` `[PINE NY 5m and & 15m Orb Statistics & LTF Candle structure.txt]`.

## Faithful object
- `value.tpo.rth.30m`: 30-minute periods 09:30–16:00, row size 1 NQ point (named), trade-visited rows when MBP-1 exists else OHLC-spanned as a tagged proxy. Emit POC, single prints, excess, poor-extreme flags, IB high/low at 10:30 known_at.
- `label.amt.open.30m`: from the first 30 minutes, per `[AMT1 p.11]`: drive = price drives one way straight off the open and never trades back through the 09:30 open; test-drive = a key reference (prior low, prior value edge) is tested first, then the drive away; rejection-reverse = auctions one way, gets rejected and trades back through the open; auction = rotation around the open. Primitives stored before the exclusive label. The retained code labels drive vs the prior value area instead of vs the open (FORMULAS.md R-A10).
- `label.amt.day`: trend / normal / normal-variation / neutral / non-trend from completed RTH; developing snapshots at 30/60/120m with later known_at. Unmatched stays unmatched.

## Upgrades
- Period 15/30/60m; trade-visited vs OHLC-spanned rows.
- Tail 2/3-row excess; single-row vs flat-multiple-period poor extreme.
- IB as `range.ib` already on the clock grid (expected null vs 6–9). Do not promote it here.
- 80% claims as **separate rows** with their own denominators: generic re-entry, hold-inside, open-outside/two-period-inside (`label.amt.80pct.two-period` `[MAMT p.18]`), older-POC failed auction `[AMT1 p.7–9]` `[MAMT p.9–12]`. Do not pool.

## Outcomes
Excess hold on first test; poor-extreme revisit; single-print fill/repair; IB extension (comparison); AMT vs Jumbo label agreement matrix; unmatched/ambiguous counts. Shared grid on TPO structures. Final day label is an outcome, never a pre-open feature.

## Links
[value-and-profiles](value-and-profiles.md) · [range-path-class](range-path-class.md) · [clock-grid-and-bars](clock-grid-and-bars.md)
