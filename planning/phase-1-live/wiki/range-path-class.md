# Retrospective range path

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

High-only, low-only, both and neither describe which sides of a completed range were taken in a specified later window; break order and mid retraces describe the path. The author's single/double-break statistics frame expectations. [TBR] pp.8–15, 30; [JR] pp.48–49.

**Not a standalone trade.** The final path label is not information available at the opening entry. Judas, extended and purged branch qualification needs its earlier context and confirmation.

**Record before use.** Range_id, outcome window, high/low break times, break definition, tie ambiguity, first side, later EQ/open retrace and denominator.

**Phase 1 observation.** Use only observations after the frozen range. Report the stated 09:00–12:00, 09:30–10:30 or other source window separately; never pool them as one probability or reuse the result as entry direction.

**Current implementation (2026-09-12).** [O010 contract](../FORMULAS.md#o010) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Replay a covered post-formation path to identify which side broke first and any later EQ return without turning an unfinished absence into false. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** An unfinished or uncovered path cannot establish that a break did not occur; same-time opposite breaks leave order unknown. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Jumbo's 06:00–09:00 range](tbr-6-9-range.md) · [Range width and expectations](range-width-context.md) · [Jumbo reversal and action windows](reversal-time-window.md) · [Accumulation, manipulation and distribution phases](amd-phase-labels.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
