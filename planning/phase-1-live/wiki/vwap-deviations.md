# VWAP deviation bands

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The lesson draws standard-deviation bands around the selected VWAP and reads absorption/rejection at a chosen deviation. ±1/±2 are displayed; 2.5 and optional 3 also appear in the discussion. [VWAP] pp.3–8.

**Not a standalone trade.** A ±2 touch is not a universal fade, and changing band multiplier/reset is not automatically the source's chosen setting.

**Record before use.** Parent VWAP_id, weighting/variance convention, as_of deviation, selected multiplier/band, source settings, band known_at and later confirmation.

**Phase 1 observation.** Freeze the band from information available at the touch. Keep each disclosed or named multiplier separate and require the selected Sires branch's auction and flow gates.

**Existing attachments.** [formulas_flow.running_vwap/r_f01_vwap_fade](/workspace/implementation/src/trading_research/research/phase1_live/formulas_flow.py); [FORMULAS] R-F01/F03/P3-02. Exact source variance/reset construction and local confirmation are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Session VWAP](vwap-session.md) · [Anchored VWAP](vwap-anchored.md) · [Confirmed VWAP deviation fade](vwap-deviation-fade.md) · [Absorption: effort without price reward](absorption-and-big-trades.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VWAP]: </workspace/sources/documents/discretionary/vwap-lesson-10.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
