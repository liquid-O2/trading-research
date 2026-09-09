# Floor pivots and golden pivot bands

Family: **auction-order-flow**. Measure faithful objects; experiment with named upgrades in Phase 1.

## Evidence and source rules

[Daily Floor Pivots.txt, L158–333,647–732,767–1200](../../../sources/documents/indicators/Pinescript-indicators--main.zip) defines PP=(H+L+C)/3 from prior daily HLC; R1=2PP−L,R2=PP+W,R3=H+2(PP−L), mirrored S1–S3, then width steps R4/5 and S4/5. Golden bands sit at 0.5–0.618 between selected bounds. It has 0.1%PP tolerances and hardcoded2482-day rates without dates. Session-change logic may reset on every in-session bar, so displayed “open” states need causal reconstruction.

## Computability and faithful reconstruction

Prior completed OHLC supports geometric rails. RTH versus exchange-day values and roll conventions are distinct.

Store every anchor/formula/tolerance and known_at. Golden pivot bands are neither VP value nor Jumbo P-zones. Keep source rates as unverified claims.

## Upgrades to measure

These are proposed experiments, not attributed source rules. The user requests stronger objects and independent comparisons. [Develop Trading Model.md, L13–31](../../../sources/documents/conversations/Develop%20Trading%20Model.md)

- **priorRTH versus exchange-day**, **tick/RV-normalized tolerance**, **equal-density shifted pivots**, **trade-touch versus close state**, **fixed time/activity-bar source aggregation**.

## Phase 1 outcomes

Touch, first/multiple contact, reject/continue, close relative to bands, gap and no-touch support by year.

Use [the common measurement contract](measurement-contract.md) for availability, denominators, discovery and confirmation. A source percentage is a claim to recompute. It is never a pass threshold.

## Definition questions

None specific. Use the common measurement definitions.

## Related

[candle patterns round levels](candle-patterns-round-levels.md), [extension projections](extension-projections.md), [value profiles](value-profiles.md)

Review findings: ZIP-13. [Review ledger](../REVIEW_LEDGER.md).
