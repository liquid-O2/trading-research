# SessionStat+ envelopes

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

SessionStat frames likely reach and exhaustion with average/median high-low boxes, a midpoint, extensions and minimum-average shading for the selected session/lookback. It also warns about choppy/low-volatility conditions. [SS] pp.3–12; [JR] pp.23–26.

**Not a standalone trade.** The envelope supplies context and confluence; it is not a blind band-touch trade or the full TBR loop.

**Record before use.** Session/reset, lookback, average type, source average/median bounds, midpoint, min-average and expansion labels, known_at and source configuration.

**Phase 1 observation.** Keep average and median as separate boundaries. The source settings do not justify min(mean_up,mean_down) or another invented minimum-average formula. A plotted source band can be annotated; a computed approximation must retain its name.

**Existing attachments.** [family_env.build_env_table](/workspace/implementation/src/trading_research/research/phase1_live/family_env.py); [FORMULAS] R-J11/P3-02. Average-excursion approximations exist; the exact minimum-average engine is missing. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Jumbo EVRange](ev-range-expected-move.md) · [The 1.33–1.66 extension area](extensions-1-33-1-66.md) · [Range exhaustion and mean-reversal area](range-exhaustion-area.md) · [Source clocks and availability](clock-grid-and-bars.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[SS]: </workspace/sources/documents/jumbo/SessionStat+.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
