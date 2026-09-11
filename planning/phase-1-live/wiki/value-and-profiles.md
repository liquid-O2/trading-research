# Volume profile

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md).

A volume profile distributes executed volume by price over a specified auction. POC, value, nodes, shelves and ledges are different readings of it. Jumbo later adds profile information at range references; Sires and Saint use it to locate current accepted structure. [VP2] pp.3–8; [RTVP] pp.3–11; [JR] pp.14, 48, 50.

**Not a standalone trade.** A volume histogram or its maximum is not a complete method. The current full-day profile cannot supply a morning confirmation.

**Record before use.** Profile_id, instrument, start/end/as_of, price-bin and volume conventions, executed volume by price, missing intervals and source-selected auction.

**Phase 1 observation.** Use only volume accumulated by the observation time. An OHLC allocation proxy must keep that label; final RTH volume/delta cannot confirm an earlier EQ touch.

**Existing attachments.** [family_open.scan_prior_rth_trade_vp](/workspace/implementation/src/trading_research/research/phase1_live/family_open.py); family_value; [mbp1_objects.vp_rth](/workspace/implementation/src/trading_research/research/phase1_live/mbp1_objects.py); [FORMULAS] P3-04/P3-07 and R-J16/J17, R-A01–A18. Developing source-aligned snapshots are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Profile point of control](profile-poc.md) · [Profile value area](value-area.md) · [High-volume node](hvn.md) · [Low-volume node](lvn.md) · [Profile shelf](profile-shelf.md) · [Profile ledge](profile-ledge.md) · [Developing profile snapshot](developing-profile.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
