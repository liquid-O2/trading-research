# Jumbo's 06:00–09:00 range

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The main New York formation range supplies its high, low, width and internal references before the post-formation decisions. It is one geometry inside SDRange / Time-Based Ranges. [TBR] pp.4–8; [JR] pp.11, 14, posts 2055344660986364371 / 2026059018750378427.

**Not a standalone trade.** The high, low or EQ is a location. Neither an edge touch nor the eventual single/double-break class is a complete entry.

**Record before use.** Formation [06:00,09:00) ET under a declared endpoint convention; H, L, W=H−L, instrument, date and known_at=09:00. Preserve zero/missing width as unavailable.

**Phase 1 observation.** Reconstruct the completed box before evaluating a touch. Measure later path and branch-specific reaction without choosing the deepest or best eventual excursion as the entry.

**Current implementation (2026-09-12).** [O005 contract](../FORMULAS.md#o005) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Freeze the dated 06:00-09:00 ET high, low, width, member identity, availability, and interval coverage from native members. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** The fixed 06:00-09:00 ET clock is implemented; missing interval membership remains a hole. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Range EQ and quadrants](range-internals.md) · [Source range-open and range-close references](range-open-close.md) · [Range width and expectations](range-width-context.md) · [Retrospective range path](range-path-class.md) · [Range exhaustion and mean-reversal area](range-exhaustion-area.md) · [The 1.33–1.66 extension area](extensions-1-33-1-66.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
