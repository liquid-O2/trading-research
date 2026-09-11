# TPO single-print structure

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Single prints are interior thin time structure left by directional movement between accepted areas. Their location can remain a future auction reference. [TPO] pp.5–7; [MAMT] pp.18–20.

**Not a standalone trade.** An outer excess tail or any price with one observed trade is not automatically an interior single-print zone or a trade.

**Record before use.** TPO profile and letter identities, interior band bounds, surrounding distributions, formation/known_at and later repair/visit history.

**Phase 1 observation.** Exclude merely outer tails from an interior-single-print definition. Never fabricate the band from an unrelated fixed-price offset or use final-day membership before it is known.

**Existing attachments.** [mbp1_objects.tpo_trade_visited](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); family_gap; [FORMULAS] R-A14/A18. True interior letter-aware bands and an unfinished-reference ledger are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Time-price-opportunity profile](tpo-ib-auction.md) · [TPO excess at auction extremes](excess.md) · [Remaining auction objectives](unfinished-business.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TPO]: </workspace/sources/documents/discretionary/tpo-lesson-3.pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
