# Overnight high, low and width

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

Overnight price extremes frame remaining liquidity and opening context. Sires's AMT discussion uses the 18:00–09:30 overnight auction; Jumbo also draws named Asia/London references whose configured windows differ. [MAMT] pp.14–16; [TBR] pp.12–15; [JR] pp.16–18.

**Not a standalone trade.** An overnight extreme or the claim that either side is often reached supplies no entry direction and no proof that both sides will trade.

**Record before use.** Window and source configuration, instrument, ONH/ONL, width, formation end, known_at and any separately named Asia/London extremes.

**Phase 1 observation.** Keep the whole overnight range separate from 6–9 and from the prior RTH range. Evaluate touches and purges after each reference becomes known.

**Current implementation (2026-09-12).** [O011 contract](../FORMULAS.md#o011) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Measure overnight high, low, width, exact window identity, member ownership, and availability; enforce Sires 18:00-09:30 ET when selected. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Other authors' overnight clocks are accepted only as explicitly identified windows; incomplete tape remains a hole. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Overnight volume structure](overnight-profile.md) · [Overnight directional inventory](overnight-inventory.md) · [Chronological liquidity purges](overnight-purge.md) · [Green Bird's finished session references](session-fail-boxes.md) · [Source-conditioned reference statistics](reference-statistics.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
