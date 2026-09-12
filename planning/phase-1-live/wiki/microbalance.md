# Price-defined microbalance continuation

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Inside the larger directional auction a small price balance forms, then strength breaks it in the thesis direction. The opposite side supplies structural risk; the pre-existing HTF objective remains the destination and later protected structure guides management. [K2345] pp.4–7.

**Not a standalone trade.** The microbalance is an execution structure in the wider thesis, not a standalone opening-range system.

**Record before use.** Microbalance_id/bounds, formation end/known_at, larger thesis, strength/breakout evidence, entry, stop behind structure and pre-existing objective.

**Phase 1 observation.** Freeze the actual small balance before its break. Do not select a later winning box or replace it with a fixed clock box; qualification requires the parent auction/thesis gates.

**Current implementation (2026-09-12).** [O131 contract](../FORMULAS.md#o131) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Freeze a positive-width microbalance, adverse-side stop, pre-existing target, and dated breakout in thesis direction. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/flow_sequences.py).

**Evidence limits.** Each required stage, side, parent band and source qualifier needs its own causal observation. Unpublished author classifications remain source limitations; a missing private stage or attempt record is not replaced by a supplied true flag. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Auction balance](auction-balance.md) · [Thesis, validity band and death condition](thesis-lifecycle.md) · [Entry-side structural invalidation](structural-risk.md) · [Confirmed protected high or low](protected-high-low.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[K2345]: </workspace/sources/documents/discretionary/2345-funded-session.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
