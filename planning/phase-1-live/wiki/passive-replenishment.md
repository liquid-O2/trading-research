# Executed passive replenishment

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

Passive defense means liquidity is consumed and replenished at the relevant area, with the level continuing to hold. Consistency of refresh, size and pace matters on a retest. [DOM7] pp.3–7; [K18] p.11; [STOP] pp.9–10; [MATH] pp.6–8.

**Not a standalone trade.** A resting wall or one BBO size increase does not establish this sequence. A previously formed aggressive-print zone is not itself verified passive reload.

**Record before use.** Price/band, passive side, consumption events, quote/depth changes, refresh repetitions and timing, executed participation and price hold.

**Phase 1 observation.** Keep a BBO reload inference labeled as such. Do not assign a full-session reload flag to a local retest or invent the author's exact refresh threshold/window.

**Existing attachments.** [mbp1_objects.absorption_b/iceberg_touch_infer/on_touch_refill](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); [FORMULAS] R-F06/F07/F09/F17 and R-S03. Full off-touch depth and hidden reserve verification are missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [DOM at a planned location](dom.md) · [Iceberg evidence and added participation](iceberg-evidence.md) · [Zone formed by aggressive prints](refill-zone.md) · [Fresh defense of a continuation band](defended-band-continuation.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DOM7]: </workspace/sources/documents/discretionary/dom-lesson-7.pdf>
[STOP]: </workspace/sources/documents/discretionary/stop-re-entering.pdf>
[K18]: </workspace/sources/documents/discretionary/18k-payout-session.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
