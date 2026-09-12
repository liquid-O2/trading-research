# Frozen observation cohort

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md) · [Stoic — data engine / quantifying fundamentals](method-stoic-data-engine.md) · [Stoic — asymmetric compounding](method-stoic-asymmetric-compounding.md).

A repeatable process collects all eligible observations uniformly, then compares groups. The Refill study separates discovered touches, selected signals and actual fills; Sires reviews a declared block instead of selected winners; Stoic validates an existing process before applying the overlay. [DATA] pp.3–4, 8; [AVG] pp.27–30; [REF] pp.8–16; [K10] pp.10–15.

**Not a standalone trade.** A filtered set of profitable days is not the original opportunity set, and 64 fills versus 312 selected signals are not paired trade returns.

**Record before use.** Process/version, inclusion rule frozen_at, instrument/date range, candidate/touch/order/fill IDs, train/test boundaries if supplied, missingness and unselected observations.

**Phase 1 observation.** Retain all eligible observations under the original definition. Future day selection cannot supply an earlier feature or candidate; reverse/rotating diagnostic splits are not forward estimates. No model is trained in this compile.

**Current implementation (2026-09-12).** [O148 contract](../FORMULAS.md#o148) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Hash the fixed eligible cohort, account for selected/order/fill identities, and preserve uniform inclusion and split direction. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py).

**Evidence limits.** Actual thesis, instruction, fill, management, account or state records are required for a historical instance. Scoped source policies and supplied interpretations cannot manufacture missing private records or a contemporaneous cohort. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Declared model and review version](model-definition.md) · [Memory of earlier zone tests](zone-touch-memory.md) · [Supplied refill-touch grade](touch-grader.md) · [Refill-study fill assumption](fill-model.md) · [Outcome distribution of a declared process](outcome-metrics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[REF]: </workspace/sources/documents/discretionary/refill-effect.pdf>
[K10]: </workspace/sources/documents/discretionary/10k-first-month.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[DATA]: </workspace/sources/documents/discretionary/data-engine.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
