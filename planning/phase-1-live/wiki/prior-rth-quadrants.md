# Prior RTH quadrants

**Historical background — scope clarified 2026-09-12.** This retained note predates the current M01–M12 / O001–O166 contracts and is outside empirical v1. Its “faithful object,” upgrade and outcome sections describe earlier proposals; they do not report current implementation acceptance or measured results. Source/Pine constructions and old statistics remain distinct from author rules. See the [current method map](index.md), [status](current-status.md), [source catalog](source-catalog.md) and [historical review ledger](/workspace/planning/phase-1-from-scratch/REVIEW_LEDGER.md).

## Definition
The 25 / 50 / 75% levels of the previous day's RTH range, used on single-break days as the inner entry levels beside the 6–9 quadrants: "for single days where it's a single break, he uses either the 6 to 9 session or the previous day RTH sessions, like 75%, 25%, and 50% zones" `[DTM L19]`; continuation inside the range using one of the equilibrium levels `[DRFL L906]`. Jumbo's PD RTH Range+ carries the prior RTH high, low and key levels as the daily direction reference `[TBR p.32–33]`. Ids `lvl.prior-rth.q25`, `lvl.prior-rth.q50`, `lvl.prior-rth.q75`.

## Citations
- User hypothesis (tier 1) `[DTM L19]` (the earlier `[DRFL L906]` cite pointed at a file-attachment stub); prior RTH range as key levels for the next RTH session `[TBR p.32–33]`; EQ and quadrants as entries on single-break days `[TBR p.12]`.

## Faithful object
`lvl.prior-rth.q{25,50,75}`: L + k·(H − L) of the prior 09:30–16:00 range, k ∈ {0.25, 0.5, 0.75}, `known_at` 16:00 prior day; outcomes 09:30–12:00 with the shared grid.

## Upgrades
- Prior ETH range quadrants (18:00–16:00); prior TPO value-area quadrants.
- Use as the inner-level swap on the single-break recipes in `../RULES.md` C3 (R-J03, R-J04).

## Outcomes
- Touch / reject / hold; single-break sessions: which inner level (6–9 quadrant vs prior-RTH quadrant) printed the first hold after the break; coincidence counts with 6–9 quadrants (≤ `tR`).

## Links
[tbr-6-9-range](tbr-6-9-range.md) · [range-path-class](range-path-class.md) · [premium-discount-50](premium-discount-50.md) · [session-fail-boxes](session-fail-boxes.md)
