# Time-anchored P-zones

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The source shows P-zones with session anchors, learning-window/percentile controls and invalidation settings. The January low → range-open and December 10 am P-zone → London-low examples describe directed paths. [JR] pp.16–18, 53–55, 58–62.

**Not a standalone trade.** A settings panel does not disclose the proprietary formula. A time anchor does not prove an entry at that time; a path arrow is not a price inequality.

**Record before use.** Source band bounds and anchor, configuration/version, known_at, active/invalidated state, selected path and actual touch/confirmation times.

**Phase 1 observation.** A source-annotated zone may support a fixture. Automatic author-faithful qualification is unknown without the engine. Preserve time-specific reversal evidence instead of forcing every zone into 09:40–09:50.

**Existing attachments.** [family_env.build_env_table](/workspace/implementation/src/trading_research/research/phase1_live/family_env.py); [FORMULAS] R-J12/P3-02. Exact P-zone construction and active-zone state are missing; historical quantile bands are approximations. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Source range-open and range-close references](range-open-close.md) · [Jumbo reversal and action windows](reversal-time-window.md) · [Remaining auction objectives](unfinished-business.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
