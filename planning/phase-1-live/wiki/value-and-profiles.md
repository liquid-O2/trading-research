# Volume profile

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md).

A volume profile distributes executed volume by price over a specified auction. POC, value, nodes, shelves and ledges are different readings of it. Jumbo later adds profile information at range references; Sires and Saint use it to locate current accepted structure. [VP2] pp.3–8; [RTVP] pp.3–11; [JR] pp.14, 48, 50.

**Not a standalone trade.** A volume histogram or its maximum is not a complete method. The current full-day profile cannot supply a morning confirmation.

**Record before use.** Profile_id, instrument, start/end/as_of, price-bin and volume conventions, executed volume by price, missing intervals and source-selected auction.

**Phase 1 observation.** Use only volume accumulated by the observation time. An OHLC allocation proxy must keep that label; final RTH volume/delta cannot confirm an earlier EQ touch.

**Current implementation (2026-09-12).** [O061 contract](../FORMULAS.md#o061) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Build an immutable volume-by-price profile from canonical native executions, preserving B/A/N ownership, binning, coverage, event IDs, and instrument definition. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/profile_integration.py).

**Evidence limits.** Profile validity depends on exact instrument definition, bin rules, canonical execution ownership, and coverage; quotes are excluded. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Profile point of control](profile-poc.md) · [Profile value area](value-area.md) · [High-volume node](hvn.md) · [Low-volume node](lvn.md) · [Profile shelf](profile-shelf.md) · [Profile ledge](profile-ledge.md) · [Developing profile snapshot](developing-profile.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
