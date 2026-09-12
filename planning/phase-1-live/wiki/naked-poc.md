# Untested prior POC

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

An older POC that has not yet been revisited is a possible destination or reaction reference, depending on the live auction. It is one of the untouched landmarks mapped before action. [VP2] pp.6–8; [AMT1] pp.12–13; [MAMT] pp.9–11.

**Not a standalone trade.** An untouched POC alone is not Sires's Failed Auction setup; that setup requires an established balance, departure, actual older-POC tag and rejection.

**Record before use.** Prior profile_id, POC, profile end/known_at, intervening visit history, current active state and selected use.

**Phase 1 observation.** No visit after the current decision may determine whether the POC was naked before it. Keep prior and established-balance identities separate.

**Current implementation (2026-09-12).** [O065 contract](../FORMULAS.md#o065) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Evaluate whether an identified prior POC remained untested through a fully covered decision interval using actual post-formation visits. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/profile_integration.py).

**Evidence limits.** No-test conclusions require full interval coverage; same price with another identity is not the same reference. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Profile point of control](profile-poc.md) · [Remaining auction objectives](unfinished-business.md) · [Sires's narrower Failed Auction setup](failed-auction-sires.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
