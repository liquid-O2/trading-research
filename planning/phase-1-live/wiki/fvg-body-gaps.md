# Fair-value gaps and higher-timeframe imbalances

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md).

Jumbo's PD RTH Range+ uses M15/H1 imbalance destinations; Green Bird's chart uses an FVG after a confirmed failure/MSS for execution. The gap's timeframe and role belong to the source case. [TBR] pp.32–35; [GB] p.43.

**Not a standalone trade.** A gap is an area or refinement, not an independent trade. A body-only gap or first-presented variant must not be borrowed from another source without evidence.

**Record before use.** Instrument, timeframe/bar kind, defining completed candles, source gap bounds, known_at, active/fill state and role as entry area or destination.

**Phase 1 observation.** The gap becomes known only after its defining confirmation. Keep wick-bound and body-bound constructions distinct if the source does not resolve them; the current helper is not proof of a complete method.

**Existing attachments.** family_gap; [formulas_jumbo.j19_htf_fvg](/workspace/implementation/src/trading_research/research/phase1_live/formulas_jumbo.py); [FORMULAS] R-J19 and related R-G01/R-G09 ingredients. Source-specific entry and fill-state joins are partial. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [PD RTH Range+ destinations](pd-rth-range-plus.md) · [Market-structure shift after failure](market-structure-shift.md) · [Remaining auction objectives](unfinished-business.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
