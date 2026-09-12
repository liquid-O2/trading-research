# Jumbo Absorption Zone+ candle

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The source settings display body threshold 0.6, volume multiplier 1.5 and a 14-period volume average. The small-body/high-volume candle is one confirmation aid at a framework location. [TBR] pp.31, 35; [JR] pp.14, 67–69.

**Not a standalone trade.** This is a candle feature, not proof of passive replenishment or an independent reversal system. The same word absorption does not make it the DOM four-check sequence.

**Record before use.** Bar identity/timeframe, body/range ratio, volume, trailing reference average and its reset, source settings/version, known_at and location.

**Phase 1 observation.** Check the displayed source constants and completed bar before use. Keep exact inequality, warm-up and reset conventions explicit where unpublished; never use a centered future-volume average.

**Current implementation (2026-09-12).** [O058 contract](../FORMULAS.md#o058) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Measure body and volume ratios from one current complete candle plus exactly fourteen causal same-timeframe bars under explicit averaging/reset/equality policies. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Only the declared 14-period policies are evaluated; insufficient or mismatched history stays unknown. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source execution bars](execution-bars.md) · [Range exhaustion and mean-reversal area](range-exhaustion-area.md) · [Absorption: effort without price reward](absorption-and-big-trades.md) · [Jumbo failure signatures and three attempts](jumbo-failure-attempts.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
