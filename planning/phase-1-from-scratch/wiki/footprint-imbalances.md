# Footprint imbalances and effort without result

Family: **auction-order-flow**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[fp-lesson-8.pdf, pp.3–7](../../../sources/documents/discretionary/fp-lesson-8.pdf#page=3) compares ask volume at p with bid volume one tick below, ratio3–4×, and stacked runs commonly≥3 rows (also “2 or3”). One figure’s colored highlights do not match the printed numeric comparison. [fp-lesson-9.pdf, pp.3–7](../../../sources/documents/discretionary/fp-lesson-9.pdf#page=3) defines positive candle/negative delta and its mirror at known levels, plus huge delta without extension; that “exhaustion print” differs from declining-flow exhaustion. [only-trade-big-trades.pdf, p.5](../../../sources/documents/discretionary/only-trade-big-trades.pdf#page=5) uses same-price “350% more” imbalance with a same-side large print. [2345-funded-session.pdf, p.5](../../../sources/documents/discretionary/2345-funded-session.pdf#page=5) does not supply the automated350% formula.

## Computability and faithful reconstruction

Trade-level signed prints support price rows and bar totals. Minutes cannot reproduce diagonal volume rows; OHLC proxies must not be called a faithful footprint.

Keep diagonal ratio and same-price ratio separate. Store numerator, denominator, zero/unknown handling, minimum row volume and run length. Record closed-bar price/delta sign only when the bar is known. Preserve formation-time stacked zones for future retests.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **3× / 4× / same-price-ratio variants** after Q13 resolves semantics.
- **volume-normalized imbalance**, **minimum-support**, **time/range/volume/dollar bars**, **trade-efficiency confirmation**, and **stack-length** sensitivity.

## Phase 1 outcomes

Imbalance-zone touch/retest, hold/break, price progress per aggression, overshoot and reversal/continuation paths; no-touch, zero-denominator and unavailable rows remain visible.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q13 resolves350% versus350%-more, diagonal direction, zero/minimum volume and stacked-run length.

## Related

[delta profiles](delta-profiles.md), [big print zones](big-print-zones.md), [absorption stages](absorption-stages.md), [cvd divergence](cvd-divergence.md)

Review findings: D-FP-01, D-FP-02, D-FP-03, D-BIG-01, D-CASE-04. [Review ledger](../REVIEW_LEDGER.md).
