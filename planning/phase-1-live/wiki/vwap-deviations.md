# VWAP deviation bands

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The lesson draws standard-deviation bands around the selected VWAP and reads absorption/rejection at a chosen deviation. ±1/±2 are displayed; 2.5 and optional 3 also appear in the discussion. [VWAP] pp.3–8.

**Not a standalone trade.** A ±2 touch is not a universal fade, and changing band multiplier/reset is not automatically the source's chosen setting.

**Record before use.** Parent VWAP_id, weighting/variance convention, as_of deviation, selected multiplier/band, source settings, band known_at and later confirmation.

**Phase 1 observation.** Freeze the band from information available at the touch. Keep each disclosed or named multiplier separate and require the selected Sires branch's auction and flow gates.

**Current implementation (2026-09-12).** [O032 contract](../FORMULAS.md#o032) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Derive weighted population dispersion from the identical VWAP parent membership; preserve reset, snapshot and band identity and reject mixed or contact-inclusive snapshots. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/context_observations.py).

**Evidence limits.** An undisclosed platform variance rule stays unavailable; the explicitly named comparison rule is implemented. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Session VWAP](vwap-session.md) · [Anchored VWAP](vwap-anchored.md) · [Confirmed VWAP deviation fade](vwap-deviation-fade.md) · [Absorption: effort without price reward](absorption-and-big-trades.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VWAP]: </workspace/sources/documents/discretionary/vwap-lesson-10.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
