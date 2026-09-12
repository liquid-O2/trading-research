# B–A–D–E–W auction-state alphabet

Object in [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

The guest framework names B balance, A absorption, D discovery, E exhaustion and W withdrawal. B has two-sided activity/revisits and low aggression; A combines high effort, low response and holding/refilling opposite liquidity; D is efficient displacement; E includes replenishment ending/level failure after prior effort; W is cancellation-dominated. [MATH] pp.7–10.

**Not a standalone trade.** These are heuristic current states, not AMT day types or automatic trade signals. Sires's following application remains separately attributed.

**Record before use.** State_id/time, native instrument, source qualitative criteria, participation/response/depth evidence, required_depth_levels, threshold definition or unknown status, and input max known_at.

**Phase 1 observation.** Classify only from evidence available at state_at. NQ is eligible; AAPL's ten levels are illustrative rather than mandatory. Missing cancellation/required-depth data or unpublished thresholds make faithful automatic state assignment unknown; an annotated state remains identifiable evidence.

**Current implementation (2026-09-12).** [O165 contract](../FORMULAS.md#o165) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Record a dated supplied state only when all required evidence, both sides, depth, and availability checks are complete; no automatic state. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py).

**Evidence limits.** Actual thesis, instruction, fill, management, account or state records are required for a historical instance. Scoped source policies and supplied interpretations cannot manufacture missing private records or a contemporaneous cohort. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Provide, withdraw and consume events](order-participation-events.md) · [Aggressive effort versus price-response efficiency](response-efficiency.md) · [Conditioned next-state transition](auction-state-transition.md) · [Evidence and data coverage](data-coverage.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
