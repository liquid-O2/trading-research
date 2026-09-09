# Range breaks, clean edges and path classes

Family: **day-type**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[Time-Based ranges Framework (JJumbo).pdf, pp.8–11,15–16,30](../../../sources/documents/jumbo/Time-Based%20ranges%20Framework%20%28JJumbo%29.pdf#page=8) distinguishes sweeps, opposite rails and AM timing. Its 86.46% extended-reversal claim uses 4,537 days without a complete event definition. [xfcmg2.pdf, pp.23–24; post 2064008375751311653](../../../sources/documents/jumbo/xfcmg2.pdf#page=23) gives the 06–09 width table for breaks during 09–12: width% bins 0–0.3 / 0.3–0.5 / 0.5–0.8 / 0.8–1.2 / 1.2+, n 1034 / 1053 / 705 / 288 / 169. Both/high-only/low-only/neither percentages are 55.5/23.7/20.3/0.5; 48.1/25.6/25.7/0.5; 34.8/34.9/29.5/0.9; 34.0/31.2/33.0/1.7; 17.8/35.5/38.5/8.3. Total n3249: 44.8/28.0/26.1/1.1.

[xfcmg2.pdf, pp.10–12,29; posts 2082104746077245851,2007108825904460106](../../../sources/documents/jumbo/xfcmg2.pdf#page=10) has a distinct 09:30–10:30 prior-value table and 09–10/10–11/11–12 sweep-to-open/EQ/opposite-edge rates. These cannot share a denominator. [NQ Stats RTH Breaks with stats.txt, L148–153](../../../sources/documents/indicators/Pinescript-indicators--main.zip) supplies hardcoded prior-range-open contingencies, not recomputed evidence.

## 2026 conditional break expectancy

The [28 August frame](https://x.com/JJumboFX/status/2093335135789719861) distinguishes **in-value versus in-range double-break expectancy**. Store RTH-open position against prior VAH/VAL and prior RTH H/L independently, then report marginal and joint high-only/low-only/both/neither rates with each cell's n. An open outside value can still be inside range; those populations cannot be pooled into a single inside/outside flag.

Preserve the [open-in versus open-out switch](jumbo-day-classes.md#2026-open-location-switch): inside prior value/range supports the source's fade/EQ hypothesis; outside both with aligned 6–9 position and volume supports discarding the double-break fade. Count continuation and return failures in both contexts. The July 9 76% A-period claim has its own 09:30–10:00/OR-reference variants in [SPEC](../SPEC.md#ev-range-and-open-location-switch); it cannot inherit the 09–12 width-table or 09:30–10:30 denominator.

[27 August](https://x.com/JJumboFX/status/2093020177696755878) motivates **5–9 ≈ 6–9** as a clock comparison, not an established equivalence. Keep the published 6–9 benchmark and compare 05:00–09:00 on matched dates, widths and outcomes. Small-range double-break % is not edge: narrow boxes mechanically ease both-edge visits. Preserve the source's approximately 45% AM single-break assertion as a claim to recompute, including held breakouts and neither-break days.

## Computability and faithful reconstruction

Minutes support exclusive break classes but may leave within-minute order unknown. Trades resolve order on available samples. Prior value needs trade-derived or explicitly named approximate VP.

Emit high-only, low-only, both and neither for every eligible session; add high-first, low-first, simultaneous/unknown and no-break. Keep touch, strict break and breach-then-return separate. Preserve raw width in points and alternative percentage denominators until Q02 is settled. Never erase a swept rail; advance its lifecycle.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **trade-order** versus **minute-order-unknown**.
- **strict-break / equality-touch** and **first-break / all-rearmed-sweeps**.
- **width-vol-normalized**, **prior-value-conditioned**, **clean-edge-conditioned**, and **fixed-grid/formation-bar** comparisons from the range page. These are descriptive tables, not a classifier.

## Phase 1 outcomes

[Session-fail boxes](session-fail-boxes.md) contributes completed 9–10, 10–11 and portable-hour paths, plus **INFERRED** Asia 20–00 and London 02–05 clocks. Compare `sweep-fail-print`, `sweep-fail-close5` and hold-outside on this same table, with separate TDO/PDL close-through confirmations. Count only after each object's known_at; GB-NYAM cannot contribute a 09:45 event. Match observation cutoffs and horizons before comparing to Jumbo. NWOG is a destination and the 9:30 open is a separate reaction line. OR/IB remains secondary.

Recompute the five width bins and overall row, with all four classes, order, support and yearly intervals. Separately report each source horizon, midpoint/open/opposite-edge return, first passage time and maximum pre-return overshoot. Retain failures, untouched days and unresolved ordering.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q01 defines touch/break/rearm/horizons. Q02 resolves width denominator, boundary inclusivity and repeated-sweep population. Unpublished source probabilities remain unreconciled claims.

## Related

[time based ranges](time-based-ranges.md), [jumbo day classes](jumbo-day-classes.md), [timed retracements](timed-retracements.md), [value profiles](value-profiles.md)

Review findings: J-TBR-02, J-TBR-04, J-TBR-08, J-X-02, J-X-04, J-X-08, J-X-10, J-X-15, ZIP-46. [Review ledger](../REVIEW_LEDGER.md).
