# Refill-study fill assumption

Object in [Sires × TeamVOT — The Refill Effect](method-refill-effect.md).

The study's touch-or-trade-through execution assumption determines which passive orders count as filled. A modeled touch is not proof of queue priority or real fill. [REF] pp.12, 15, 22.

**Not a standalone trade.** A fill assumption is not an entry edge, and limit-versus-market cohorts with different fill counts are not paired outcomes on identical trades.

**Record before use.** Order_id, entry price/time, quote/trade coverage, declared touch/trade-through rule, modeled fill time, cancellation and any unavailable queue information.

**Phase 1 observation.** Keep discovered touches, selected orders and modeled fills as separate denominators. Never claim actual queue fills from a price touch or compare unmatched filled cohorts as matched executions.

**Current implementation (2026-09-12).** [O151 contract](../FORMULAS.md#o151) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Separate modeled touch-fill eligibility from actual fill reports and leave queue priority unverified without order-level evidence. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py).

**Evidence limits.** Actual thesis, instruction, fill, management, account or state records are required for a historical instance. Scoped source policies and supplied interpretations cannot manufacture missing private records or a contemporaneous cohort. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Observed order lifecycle](order-lifecycle.md) · [Frozen observation cohort](research-cohort.md) · [Trading and account costs](cost-model.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[REF]: </workspace/sources/documents/discretionary/refill-effect.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
