# Triad AMT-object first use: IØD and RFZ

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

C1 compares ES, NQ and YM reacting to their corresponding AMT objects at different speeds. In IØD, YM's prior-balance test/rejection changes the ES reaction read. RFZ, Reactive Fill Zone, describes a correlated asset filling the corresponding single-print objective first, requiring reassessment of the remaining target. [C1] p.5.

**Not a standalone trade.** This is native-object timing and reaction, not generic same-price divergence or a separate entry system. Raw prices of different indices are not directly comparable.

**Record before use.** Each instrument's own AMT object_id/bounds and known_at, first-use times, reaction evidence, thesis/target revision and decision time.

**Phase 1 observation.** Require each native object to exist before its own use and the correlated event before the revised decision. Do not substitute arbitrary high/low disagreement or a future peer-market target hit.

**Current implementation (2026-09-12).** [O147 contract](../FORMULAS.md#o147) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Record native AMT objects and first-use times for ES/NQ/YM while preserving the documented IOD and RFZ revisions. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py).

**Evidence limits.** Actual thesis, instruction, fill, management, account or state records are required for a historical instance. Scoped source policies and supplied interpretations cannot manufacture missing private records or a contemporaneous cohort. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Remaining auction objectives](unfinished-business.md) · [TPO single-print structure](single-prints.md) · [Auction balance](auction-balance.md) · [Thesis, validity band and death condition](thesis-lifecycle.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[C1]: </workspace/sources/documents/discretionary/code-1-thesis.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
