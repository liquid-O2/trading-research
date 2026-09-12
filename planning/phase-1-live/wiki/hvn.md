# High-volume node

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md).

An HVN is a locally accepted concentration of volume; a minor HVN can refine a reaction area inside the larger auction. The unnamed member requires an independently identified minor HVN plus prior reaction history. [VP2] pp.3, 6–8; [K10] pp.5–8; [JR] pp.14, 48.

**Not a standalone trade.** The first detected peak, one high-volume price or a rounded resistance line is not automatically the member's two-reason setup.

**Record before use.** Profile_id/as_of, node bounds and peak, neighboring structure, source-selected scale, known_at and independent reaction-area identity when used.

**Phase 1 observation.** Keep the node as an area where the source draws one. Require actual contact and method-specific reaction; do not use a whole-day node or an unrelated prior extreme as the two reasons.

**Current implementation (2026-09-12).** [O066 contract](../FORMULAS.md#o066) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Measure volume in a source-selected HVN band from the actual profile while leaving automatic node selection unavailable. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/profile_integration.py).

**Evidence limits.** HVN band selection is source-supplied; no automatic peak-band algorithm is claimed. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Volume profile](value-and-profiles.md) · [Low-volume node](lvn.md) · [Prior defended reaction area](prior-reaction-area.md) · [Source-selected dealing range](dealing-range.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[K10]: </workspace/sources/documents/discretionary/10k-first-month.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
