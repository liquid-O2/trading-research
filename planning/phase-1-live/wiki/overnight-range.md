# Overnight high, low and width

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Overnight price extremes frame remaining liquidity and opening context. Sires's AMT discussion uses the 18:00–09:30 overnight auction; Jumbo also draws named Asia/London references whose configured windows differ. [MAMT] pp.14–16; [TBR] pp.12–15; [JR] pp.16–18.

**Not a standalone trade.** An overnight extreme or the claim that either side is often reached supplies no entry direction and no proof that both sides will trade.

**Record before use.** Window and source configuration, instrument, ONH/ONL, width, formation end, known_at and any separately named Asia/London extremes.

**Phase 1 observation.** Keep the whole overnight range separate from 6–9 and from the prior RTH range. Evaluate touches and purges after each reference becomes known.

**Existing attachments.** clocks; sessions; [family_levels.build_level_table](/workspace/implementation/src/trading_research/research/phase1_live/family_levels.py); [FORMULAS] R-J04/J10, R-A12 and P3-06. Exact configured window identity is required. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Overnight volume structure](overnight-profile.md) · [Overnight directional inventory](overnight-inventory.md) · [Chronological liquidity purges](overnight-purge.md) · [Green Bird's finished session references](session-fail-boxes.md) · [Source-conditioned reference statistics](reference-statistics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
