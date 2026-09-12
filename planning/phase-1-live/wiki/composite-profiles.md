# Composite auction profiles

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md).

Profiles can combine the periods relevant to the current auction and its higher-timeframe objective. Sires distinguishes a small intraday auction from a weekly/swing scale; the current auction's structure determines the useful aggregation. [VP2] pp.6–8; [MATH] pp.12–14; [K10] pp.5–7.

**Not a standalone trade.** A fixed 5/20/250-day composite is not a universal source prescription and its node is not an entry on contact.

**Record before use.** Constituent sessions/auction bounds, instrument, aggregation window and rationale, as_of, node/value outputs and known_at.

**Phase 1 observation.** Only completed/available constituent observations enter the profile. Record a fixed-lookback experiment as a named variant rather than the author's selected auction.

**Current implementation (2026-09-12).** [O070 contract](../FORMULAS.md#o070) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Compose explicitly selected compatible profile parents with disjoint native event ownership and reconcile every row and total. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/profile_integration.py).

**Evidence limits.** Constituents must share instrument/tick/bin semantics and have disjoint event IDs; undisclosed value-area algorithms propagate holes. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source-selected dealing range](dealing-range.md) · [Volume profile](value-and-profiles.md) · [High-volume node](hvn.md) · [Low-volume node](lvn.md) · [Prior defended reaction area](prior-reaction-area.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[K10]: </workspace/sources/documents/discretionary/10k-first-month.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
