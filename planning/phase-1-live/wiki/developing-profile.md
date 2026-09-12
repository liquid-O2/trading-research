# Developing profile snapshot

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Keani — open above value](method-keani-open-above-value.md).

The developing profile is the state visible so far. Sires rereads it after an impulse; Keani first observes value building higher and only later trades a break/retest of the current VAH. [AMT1] pp.12–13; [AVG] pp.21–22; [JR] pp.14, 48.

**Not a standalone trade.** The final bullish profile or final POC is not a pre-entry fact. A moving boundary by itself is not a trade.

**Record before use.** Profile_id, as_of event, accumulated volume/TPO, POC/VAH/VAL at that event, price bounds, source settings and snapshot known_at.

**Phase 1 observation.** Freeze the relevant snapshot at each stage. Keani's opening test uses yesterday's VAH; his later breakout uses developing VAH. Keep those two known times and identities separate.

**Current implementation (2026-09-12).** [O063 contract](../FORMULAS.md#o063) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Freeze an immutable developing-RTH profile snapshot at as-of so later events cannot revise the earlier snapshot. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/profile_integration.py).

**Evidence limits.** Snapshot immutability is enforced; it does not forecast the later developing POC. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Volume profile](value-and-profiles.md) · [Profile value area](value-area.md) · [Time-price-opportunity profile](tpo-ib-auction.md) · [Opening location and participation](open-location-switch.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
