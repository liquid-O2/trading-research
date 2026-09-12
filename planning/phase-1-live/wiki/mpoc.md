# MPOC: the profile midpoint

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

MAMT explicitly labels the mid of the profile MPOC. It is different from volume POC. The 73% statement is conditional on RTH opening inside the previous ETH profile's balance. [MAMT] pp.15–16.

**Not a standalone trade.** MPOC is a target-context object; the percentage is not a trade admission rule or volume-POC hit rate.

**Record before use.** Profile_id and exact scope, H/L, midpoint=(H+L)/2, known_at, opening-condition interpretation and later contact.

**Phase 1 observation.** Do not substitute POC for midpoint or prior RTH for ETH. Preserve the prose/figure uncertainty about balance versus VA; report a scoped observation rather than an unconditional probability.

**Current implementation (2026-09-12).** [O076 contract](../FORMULAS.md#o076) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Compute MPOC strictly as the midpoint of verified profile high/low and compare it separately with volume POC and later contacts. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/profile_integration.py).

**Evidence limits.** MPOC is a geometric midpoint and must not be substituted for volume POC. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [ETH profile identity](prior-eth-profile.md) · [Profile point of control](profile-poc.md) · [Opening location and participation](open-location-switch.md) · [Source-conditioned reference statistics](reference-statistics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
