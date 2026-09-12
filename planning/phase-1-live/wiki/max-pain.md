# Source max-pain reference

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The source gamma panels include a max-pain reference alongside walls. A panel's put wall and max pain can coincide in an example; that does not establish universal identity. [GEX] pp.13–19.

**Not a standalone trade.** Max pain is a contextual reference, not a standalone pinning trade or an automatic terminal-price prediction.

**Record before use.** Source product/expiry, printed label/value, snapshot/known_at, calculation convention if supplied and relation to separately labeled walls.

**Phase 1 observation.** Keep the literal source reference distinct from a named payout/OI approximation. Do not derive an entry or guaranteed expiry target from a displayed level.

**Current implementation (2026-09-12).** [O037 contract](../FORMULAS.md#o037) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Retain max-pain identity separately from same-price walls and calculate only the stated difference. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/context_observations.py).

**Evidence limits.** The payout engine and terminal prediction are not inferred from a supplied max-pain label. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Native options-chain identity](options-nodes.md) · [Gamma call and put walls](gex-walls-and-max-pain.md) · [Source gamma regime](gex-regime.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GEX]: </workspace/sources/documents/discretionary/gex-framework.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
