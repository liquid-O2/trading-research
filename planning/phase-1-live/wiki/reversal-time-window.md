# Jumbo reversal and action windows

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The manual's Judas opening leg runs from the 09:30 open toward exhaustion, with reversal/exit framing around 09:40–09:50. In the purged continuation case that interval can be an add/continuation window. Later time-anchored examples use their actual clocks. [TBR] pp.8–15; [JR] pp.53–55.

**Not a standalone trade.** Being inside the interval does not confirm reversal, and a final reversal-time histogram cannot choose a live entry.

**Record before use.** Branch, source window, entry/exit purpose, reference/zone known_at, observed sweep/rejection times and any news-related delay.

**Phase 1 observation.** Check the timing required by the selected fixture/branch. Keep outbound and reversal legs separate, and leave an undocumented exact tolerance unknown.

**Current implementation (2026-09-12).** [O021 contract](../FORMULAS.md#o021) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Evaluate an actual action timestamp against explicit reversal/action window boundaries and surface boundary ambiguity. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Window boundaries and branch purpose must be supplied; equality at an excluded boundary stays ambiguous. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source clocks and availability](clock-grid-and-bars.md) · [Retrospective range path](range-path-class.md) · [Scheduled news and changing information](news-event-context.md) · [Time-anchored P-zones](p-zones-benchmark.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
