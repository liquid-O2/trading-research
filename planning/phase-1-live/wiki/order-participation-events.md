# Provide, withdraw and consume events

Object in [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

jetbundle begins with submissions that provide liquidity, cancellations that withdraw it and executions that consume it, then relates those events to the chart/DOM/tape impression. The illustration uses an AAPL ten-level order-book record. [MATH] pp.4–6.

**Not a standalone trade.** A static book snapshot does not reconstruct the event process, and displayed imbalance alone is not an entry.

**Record before use.** Native event/sequence_id, instrument, timestamp, action, side, price, size, depth/order identity and coverage of submissions/cancels/executions.

**Phase 1 observation.** Preserve event ordering and available depth. Do not label a BBO-only dataset as the illustrated full participation record or infer cancellations from absent later snapshots.

**Existing attachments.** mbp1_extract and mbp1_objects have limited trade/BBO ingredients. Full source order/depth reconstruction is missing; [FORMULAS] R-F06/F07 are only related partial observations. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Executed aggressor-side trades](aggressor-trades.md) · [DOM at a planned location](dom.md) · [Aggressive effort versus price-response efficiency](response-efficiency.md) · [B–A–D–E–W auction-state alphabet](auction-state.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
