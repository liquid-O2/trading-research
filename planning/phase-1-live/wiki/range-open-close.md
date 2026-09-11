# Source range-open and range-close references

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

Range open and close are separately drawn references. Their identity must be read from the actual source version, label and price. The January 2 range-open path is low → range open; the displayed line is anchored near the range finish, so a blanket first-06:00-print substitution is not established for that fixture. [TBR] pp.4–5; [JR] pp.53–54.

**Not a standalone trade.** A colored line or the arrow in low → open does not imply a fixed clock, an inequality, or a fill at the zone anchor time.

**Record before use.** Literal source label, price/band, platform/version, parent range, displayed anchor, clock interpretation, known_at and subsequent directed path.

**Phase 1 observation.** Match label plus value and source date before using the reference. Separate source-open identification from measured low-to-open reach; unresolved axis mapping is unknown.

**Existing attachments.** [sessions.build_session](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py) exposes the first open; [FORMULAS] R-J05/J12 and P3-01. The source-specific open/close identity and path join are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Range EQ and quadrants](range-internals.md) · [Time-anchored P-zones](p-zones-benchmark.md) · [Source clocks and availability](clock-grid-and-bars.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
