# Confirmed protected high or low

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Protected structure follows demonstrated control. In the K18 short, the prior low must break and close with real aggression before the intervening high is treated as protected for trailing. The low-side lesson similarly links protection to defended control and reward. [K18] pp.8–14; [RD] pp.4–7.

**Not a standalone trade.** An unconfirmed wick or final-AM extreme is not a protected stop reference. The high-side mirror must be bound to actual source evidence.

**Record before use.** Control band, pivot/extreme price time, confirming break/close and aggression time, protected_known_at, side and later stop action.

**Phase 1 observation.** The stop action must follow confirmation, not merely the earlier pivot bar. Keep structure formation, confirmation and management timestamps separate.

**Current implementation (2026-09-12).** [O143 contract](../FORMULAS.md#o143) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Trail only after the protected price and required confirmation are known, with side-specific protection. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py).

**Evidence limits.** Actual thesis, instruction, fill, management, account or state records are required for a historical instance. Scoped source policies and supplied interpretations cannot manufacture missing private records or a contemporaneous cohort. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Signed volume-by-price profile](weekly-delta-profile.md) · [Entry-side structural invalidation](structural-risk.md) · [Source-selected position management](position-management.md) · [Price-defined microbalance continuation](microbalance.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[RD]: </workspace/sources/documents/discretionary/reading-delta.pdf>
[K18]: </workspace/sources/documents/discretionary/18k-payout-session.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
