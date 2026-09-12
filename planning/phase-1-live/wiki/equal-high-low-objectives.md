# Equal-high or equal-low liquidity objective

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The extension-reaction example points toward still-owed equal highs after the source location produces a long reaction. Repeated prices are a destination only when the source selects them. [JR] pp.23–26.

**Not a standalone trade.** Repeated-looking highs do not by themselves create an entry or a guaranteed liquidity run.

**Record before use.** Source reference points/band, side, tolerance if specified, all contributing times and known_at, source objective selection and later visit.

**Phase 1 observation.** Identify the objective before entry and retain an unspecified equality tolerance as unresolved or named. Do not choose whichever later double top/bottom makes the target look successful.

**Current implementation (2026-09-12).** [O028 contract](../FORMULAS.md#o028) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Create an equal-high/low objective from at least two dated contributor parents and an explicit equality/band policy; track remaining status at selection. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Near-equality tolerance and objective band are policy inputs; price similarity alone does not create an objective. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Remaining auction objectives](unfinished-business.md) · [Objective selected before entry](trade-objective.md) · [The 1.33–1.66 extension area](extensions-1-33-1-66.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
