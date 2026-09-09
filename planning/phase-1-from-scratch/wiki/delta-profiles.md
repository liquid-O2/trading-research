# Signed delta profiles and intrabar POC migration

Family: **auction-order-flow**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[reading-delta.pdf, pp.4–10](../../../sources/documents/discretionary/reading-delta.pdf#page=4) uses directional delta concentration, a small balance then escape, protected extremes, minor/LVN confluence and repeated control changes. “Highest point of delta profile” is ambiguous between price position and magnitude. [fp-lesson-9.pdf, pp.3–5](../../../sources/documents/discretionary/fp-lesson-9.pdf#page=3) describes POC moving within one developing candle from lower to upper region or the reverse. It is distinct from session POC migration. [18k-payout-session.pdf, pp.4–8](../../../sources/documents/discretionary/18k-payout-session.pdf#page=4) and [2345-funded-session.pdf, pp.4–7](../../../sources/documents/discretionary/2345-funded-session.pdf#page=4) show weekly delta profiles and protected structures. [xfcmg2.pdf, pp.14–16; post 2077828415923581206](../../../sources/documents/jumbo/xfcmg2.pdf#page=14) confirms RTH VP plus delta profile use.

## Computability and faithful reconstruction

Trade aggressor sides provide buy/sell volume by price. Unknown sides stay unknown. MBP-1 supports NQ price and BBO context; OHLC signed volume is a separately labeled proxy.

Persist signed rows, positive/negative peaks, absolute-magnitude peak, highest-price concentration and anchor. Do not choose the “delta print” meaning silently. Intrabar POC requires an as-of sequence; store flip time and later price response separately. Future absence of retest cannot confirm a protected extreme earlier.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **trade versus OHLC delta profile**, **RTH / overnight / week / dealing-range anchor**, **tick/volatility bins**, **signed concentration normalized by volume**, **intrabar POC path versus final POC**.
- **volume-clock snapshots**, **peak-prominence**, **prior-test memory**, and fixed location/no-location ablations.

## Phase 1 outcomes

Concentration/POC-flip creation, retest, breach, role change, excursion and outcome timing; profile agreement and year stability. Keep POC, delta peak and range midpoint distinct.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

Q12 defines delta-print anchor/peak meaning and POC-flip thresholds. Until then emit primitives with unresolved semantic label.

## Related

[cvd constructions](cvd-constructions.md), [footprint imbalances](footprint-imbalances.md), [swing rails protected extremes](swing-rails-protected-extremes.md), [origin control role flips](origin-control-role-flips.md)

Review findings: D-DELTA-01, D-DELTA-02, D-FP-02, D-CASE-02, D-CASE-04, J-X-05. [Review ledger](../REVIEW_LEDGER.md).
