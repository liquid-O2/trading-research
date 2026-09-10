# Range path class and day-type labels

## Definition
Given a box (default the 6–9 box) and an outcome window, the path class is one of **high-only**, **low-only**, **both**, **neither**, with **break order** (which edge first) when both. A "break" is defined by the shared grid (default: 1-minute close beyond the edge; wick variant and 5-minute variant named). Day-type labels layered on the class:
- **Judas / false breakout / sweep-then-reverse**: one edge swept, extension toward projections, reversal back through EQ toward the other edge `[TBR p.6 L88, p.8 L124–142]` `[FIND p.4 L77–78]`.
- **Single break after an extended overnight range**: entries at EQ or quadrants, reduced expectations, range H/L often enough `[TBR p.12 L175–181, p.24 L315–319]`.
- **Single break after overnight already purged, compressed range**: internal range levels, larger expansion, 9:40–9:50 becomes continuation not reversal `[TBR p.12 L185–190]`.
- **Neither** (inside day) is its own label.

Predictors (range size, balance vs extended, clean edge, open vs prior value and vs 6–9, sister-index hunts) are **labelled here and predicted in Phase 2** `[BRIEF]`.

## Citations
- Range-size break classification, 8 Jun 2026, tweet `2064008375751311653`, n = 3,249 `[XF p.24, table confirmed by zoom]` `[PACK L46–56]`:

| width % | n | double | single high | single low | none |
|---|---|---|---|---|---|
| 0–0.3 | 1034 | 55.5 | 23.7 | 20.3 | 0.5 |
| 0.3–0.5 | 1053 | 48.1 | 25.6 | 25.7 | 0.5 |
| 0.5–0.8 | 705 | 34.8 | 34.9 | 29.5 | 0.9 |
| 0.8–1.2 | 288 | 34.0 | 31.2 | 33.0 | 1.7 |
| 1.2+ | 169 | 17.8 | 35.5 | 38.5 | 8.3 |
| all | 3249 | 44.8 | 28.0 | 26.1 | 1.1 |

- "1.2% range size very low chance of double break", "Retrace to midpoint stays at 60.4%" `[XF p.23 L288–290]`; small-range double-break % is skewed, not edge `[XF p.7 L91–93]` `[PACK L50, L92]`; "~45% of pre market ranges do single break during AM" `[FIND p.6 L137]`.
- Balanced vs imbalanced overnight matters `[FIND p.6 L138–141]`; classification of range = size, balance, already-purged overnight `[JJX L56]` (user); classify step: size, balance, which edge is still clean, open vs prior-day value, sister indices `[FIND p.3 L57–58]`.
- Clean edge: red = untouched edge, blue = swept edge, the untouched edge is the draw `[FIND p.4 L73–79]`.
- Pine tier-2 restatements to recompute, not to trust: prior-RTH-relative open → break rates `[PINE NQ Stats RTH Breaks with stats.txt]`; IB break combos `[PINE Initial Balance Statistical Mapping.txt]`; ORB extreme-first → next-break tables `[PINE NY 5m and & 15m Orb Statistics & LTF Candle structure.txt:899–1001]`.

## Faithful object
`path.6-9.published`: class over 09:30–12:00 with break = 1-minute close beyond; width metric `w.pct` (basis of his % is unpublished → variants `w.pct.0859close`, `w.pct.0930open`); buckets exactly his. Labels are named variants, never hidden constants, and are scored on whichever edge was swept (the swept side is a column): `judas.depth.any` (any excursion beyond an edge then 1-minute close back through EQ within window), `judas.depth.mr` (the excursion enters the mean-reversal area, ≥ 0.1·W beyond the edge), `judas.depth.-0.5` (the excursion reaches ±0.5 on that side, overshoot δ allowed). Extended overnight = `w.rel-prior-rth ≥ 1.0`; purged = Asia or London H/L already taken before 09:30; compressed = `w.rel-prior-rth ≤ 0.5`. Each threshold is a named variant, never a hidden constant.

## Upgrades
- Break confirmation: wick / 1-minute close / 5-minute close (grid).
- Window: 09:30–10:30 (matches XF p.11), 09:30–12:00 (matches TBR), 09:30–16:00.
- Box source: any clock from [clock-grid-and-bars](clock-grid-and-bars.md); trade-level H/L.
- Balance metric: overnight VP shape (b vs p vs trend) from [value-and-profiles](value-and-profiles.md); imbalance = |close − open| / (H−L) of the box.

## Outcomes
- Class shares per width bucket on F and on L vs his table (absolute difference per cell = "faithful disagreements" for recompute rows).
- Break order shares; time of first break; mid-retrace rate after first break; both-break rate conditional on first break.
- Label counts per session: Judas / single-extended / single-purged / neither, with the threshold variant that produced them.

## Links
[tbr-6-9-range](tbr-6-9-range.md) · [open-location-switch](open-location-switch.md) · [session-fail-boxes](session-fail-boxes.md) · [smt-divergence](smt-divergence.md)
