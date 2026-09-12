# Sires's narrower Failed Auction setup

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Established balance → break out → actually tag an older, separate balance's POC → instant rejection → return toward the specified boundary of the established balance. The source says rejection from above the older POC targets established VAH, and rejection from below targets established VAL; the diagram fixes the two balance identities. [MAMT] pp.9–11.

**Not a standalone trade.** A generic return to a gray zone is not this setup. The source's negative chart breaks/retests in continuation without tagging and rejecting an older POC.

**Record before use.** Established balance_id and VAH/VAL, older profile_id/POC, both known times, breakout, older-POC tag, rejection, decision and named target.

**Phase 1 observation.** Require two distinct balances and ordered break < prior-POC tag < rejection ≤ decision. Preserve the source's target binding; do not substitute the nearest boundary. Its 80% claim is not a newly verified result.

**Current implementation (2026-09-12).** [O093 contract](../FORMULAS.md#o093) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Keep established and older profiles distinct, then validate the Sires break, older-POC tag, rejection, and source target sequence. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** The narrower Sires route cannot alias Saint's return-to-value route or reuse the same profile as both balances. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Auction balance](auction-balance.md) · [Profile point of control](profile-poc.md) · [Untested prior POC](naked-poc.md) · [Saint's failed auction and return to value](failed-auction-saint.md) · [Source-conditioned reference statistics](reference-statistics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
