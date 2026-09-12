# Provide, withdraw and consume events

Object in [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

jetbundle begins with submissions that provide liquidity, cancellations that withdraw it and executions that consume it, then relates those events to the chart/DOM/tape impression. The illustration uses an AAPL ten-level order-book record. [MATH] pp.4–6.

**Not a standalone trade.** A static book snapshot does not reconstruct the event process, and displayed imbalance alone is not an entry.

**Record before use.** Native event/sequence_id, instrument, timestamp, action, side, price, size, depth/order identity, required_depth_levels and actual coverage of submissions/cancels/executions.

**Phase 1 observation.** Preserve event ordering and the declared native depth scope. AAPL and ten levels describe the illustration, not universal requirements; NQ is permitted ([MATH] pp.3, 16). Actual depth must cover required_depth_levels, and missing lifecycle evidence remains unknown. Do not infer cancellations from absent later snapshots.

**Current implementation (2026-09-12).** [O163 contract](../FORMULAS.md#o163) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Replay actual identified order actions for provided/withdrawn/consumed quantity and remaining-state reconciliation. A separate native executed-tape adapter retains B/A/N consumption and two-sided executions, with passive consumption opposite the known aggressor. Add/cancel/full-depth/hidden-order and remaining queue state remain unknown without native order lifecycle records. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/process_observations.py).

**Evidence limits.** Trade/BBO data do not supply native order-ID and full-depth lifecycle logs; those unavailable data are not reconstructed from snapshots. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Executed aggressor-side trades](aggressor-trades.md) · [DOM at a planned location](dom.md) · [Aggressive effort versus price-response efficiency](response-efficiency.md) · [B–A–D–E–W auction-state alphabet](auction-state.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
