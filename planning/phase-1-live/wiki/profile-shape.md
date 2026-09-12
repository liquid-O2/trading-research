# Profile shape and trade permission

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md).

Balanced, double-distribution, trending and P/b shapes describe where the auction has accepted trade. Saint's P/b examples form a balance after an impulse and then require break/retest. Sires's MAMT P/b captions and drawings do not prescribe a consistent universal direction. [RTVP] pp.6–11; [MAMT] pp.6–8.

**Not a standalone trade.** Buy every P or sell every b is not a sourced rule. A double distribution requires reading both shelves and the connection.

**Record before use.** Author, profile_id/as_of, selected shape definition, accepted sub-balances, connecting LVN and source trade permission.

**Phase 1 observation.** Preserve source-specific permission. Saint's trending-profile stand-down and Sires's established-trend continuation belong to different loops; shape alone cannot select between them.

**Current implementation (2026-09-12).** [O085 contract](../FORMULAS.md#o085) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Preserve a source profile-shape label and permission, sub-balance/LVN identities, and completed break-retest evidence without inferring direction from shape. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** P/b shape direction and trade permission are not inferred automatically. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Auction balance](auction-balance.md) · [Profile shelf](profile-shelf.md) · [Low-volume node](lvn.md) · [Accepted break and defended boundary retest](break-retest.md) · [Developing auction day structure](day-type.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
