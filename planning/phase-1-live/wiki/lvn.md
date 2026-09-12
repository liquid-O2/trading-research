# Low-volume node

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md).

An LVN is the lower-participation connection between accepted areas; price can travel through it quickly or react at its boundary. Sires stresses the second transition back into balance: an outer taper alone is not the complete structure. [VP2] pp.3–5; [MATH] pp.12–14; [RTVP] pp.7–8.

**Not a standalone trade.** The minimum histogram bin or a thin tail outside one hump is not automatically a valid LVN or an entry.

**Record before use.** Profile_id/as_of, two neighboring accepted areas, bridge bounds/trough, volume-bin coverage, known_at and selected directional context.

**Phase 1 observation.** Retain zero-volume/missing-bin distinctions and both transitions. An LVN computed strictly inside 6–9 cannot simultaneously prove a source node outside that same range.

**Current implementation (2026-09-12).** [O067 contract](../FORMULAS.md#o067) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Measure volume in a source-selected bridge/LVN band and preserve the identities of the two accepted areas and their transition evidence. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/profile_integration.py).

**Evidence limits.** LVN/bridge selection and accepted-area identities are source-supplied; no automatic trough algorithm is claimed. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [High-volume node](hvn.md) · [Profile shelf](profile-shelf.md) · [Profile ledge](profile-ledge.md) · [Overnight volume structure](overnight-profile.md) · [Signed volume-by-price profile](weekly-delta-profile.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
