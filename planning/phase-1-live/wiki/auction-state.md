# B–A–D–E–W auction-state alphabet

Object in [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

The guest framework names B balance, A absorption, D discovery, E exhaustion and W withdrawal. B has two-sided activity/revisits and low aggression; A combines high effort, low response and holding/refilling opposite liquidity; D is efficient displacement; E includes replenishment ending/level failure after prior effort; W is cancellation-dominated. [MATH] pp.7–10.

**Not a standalone trade.** These are heuristic current states, not AMT day types or automatic trade signals. Sires's following application remains separately attributed.

**Record before use.** State_id/time, source qualitative criteria, participation/response/depth evidence, threshold definition or unknown status, and input max known_at.

**Phase 1 observation.** Classify only from evidence available at state_at. Missing cancellation/depth data or unpublished thresholds make faithful automatic state assignment unknown; an annotated source state remains identifiable evidence.

**Existing attachments.** The source five-state classifier is missing from [FORMULAS] and current implementation. Generic day or absorption flags are not the complete state model. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Provide, withdraw and consume events](order-participation-events.md) · [Aggressive effort versus price-response efficiency](response-efficiency.md) · [Conditioned next-state transition](auction-state-transition.md) · [Evidence and data coverage](data-coverage.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
