# Volatility term structure and event change

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The volatility lesson reads curve shape, expansion/crush and event changes as context for risk and expected movement. These are inputs to the live thesis and trade ambition. [VIX4] pp.5–9.

**Not a standalone trade.** Curve shape alone is not an entry, and the source does not supply a universal ratio threshold that overrides the auction.

**Record before use.** Products/tenors, native values and units, simultaneous observation times, source curve interpretation, event association and known_at.

**Phase 1 observation.** Preserve point-in-time alignment and source conventions. A post-event crush cannot be used as information before the release.

**Current implementation (2026-09-12).** [O044 contract](../FORMULAS.md#o044) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Retain the exact selected tenor pair, comparable units and chosen difference/ratio; include an event change only after its actual publication. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/context_observations.py).

**Evidence limits.** Curve shape and event interpretation require the source observation; no tenor substitution occurs. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [VIX and volatility context](vix-context.md) · [VVIX context](vvix-context.md) · [Scheduled news and changing information](news-event-context.md) · [Thesis, validity band and death condition](thesis-lifecycle.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VIX4]: </workspace/sources/documents/discretionary/vix-lesson-4.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
