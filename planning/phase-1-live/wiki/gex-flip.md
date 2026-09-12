# Gamma-flip reference

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The flip is a source regime/location reference read with current price and the relevant gamma map. The materials use more than one sign/flip description, and a recap records disagreement near it without changing the plan. [GEX] pp.6–7, 13–19; [K18] p.4.

**Not a standalone trade.** A calculated zero of an assumed aggregate gamma curve does not automatically reproduce the proprietary flip or dictate an entry.

**Record before use.** Source flip label/value, product and expiry, snapshot/known_at, sign/model convention, spot relation and uncertainty.

**Phase 1 observation.** Retain the source read or a named scenario; do not combine price-versus-flip and aggregate-sign interpretations opportunistically. The next impulse may require a reread before a new decision.

**Current implementation (2026-09-12).** [O035 contract](../FORMULAS.md#o035) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Retain attributed flip level, units and regime interpretation and compute spot relation using both observation clocks. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/context_observations.py).

**Evidence limits.** The dealer flip engine is unpublished; spot-minus-flip arithmetic does not infer a gamma regime. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source gamma regime](gex-regime.md) · [Native options-chain identity](options-nodes.md) · [Gamma call and put walls](gex-walls-and-max-pain.md) · [Thesis, validity band and death condition](thesis-lifecycle.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GEX]: </workspace/sources/documents/discretionary/gex-framework.pdf>
[K18]: </workspace/sources/documents/discretionary/18k-payout-session.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
