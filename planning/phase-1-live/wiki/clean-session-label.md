# Source session-cleanliness assessment

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The raw record sometimes favors London as the cleaner session in that market cycle. The manual relates AM expansion/consolidation to later-session behavior. This is an observed session-selection context. [TBR] p.36; [JR] pp.46, 50–51, 63–66.

**Not a standalone trade.** Cleaner is not a disclosed rolling-ten-day selector or a separate London entry rule.

**Record before use.** Author/date, session configuration, observed reason for preference, known_at and the branch subsequently used.

**Phase 1 observation.** Retain the source's qualitative judgment or name an explicit research variant. Do not use that day's eventual clean reversal to select its session retrospectively.

**Current implementation (2026-09-12).** [O022 contract](../FORMULAS.md#o022) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Preserve the source cleanliness label, session identity, reason, and selection time; never invent an automatic cleanliness classifier. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Cleanliness is a source assessment and remains unclassified automatically. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Other time-based range formations](tbr-remaining-clocks.md) · [Retrospective range path](range-path-class.md) · [Accumulation, manipulation and distribution phases](amd-phase-labels.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
