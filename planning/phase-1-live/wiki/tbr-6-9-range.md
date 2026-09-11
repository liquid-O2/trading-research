# Jumbo's 06:00–09:00 range

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The main New York formation range supplies its high, low, width and internal references before the post-formation decisions. It is one geometry inside SDRange / Time-Based Ranges. [TBR] pp.4–8; [JR] pp.11, 14, posts 2055344660986364371 / 2026059018750378427.

**Not a standalone trade.** The high, low or EQ is a location. Neither an edge touch nor the eventual single/double-break class is a complete entry.

**Record before use.** Formation [06:00,09:00) ET under a declared endpoint convention; H, L, W=H−L, instrument, date and known_at=09:00. Preserve zero/missing width as unavailable.

**Phase 1 observation.** Reconstruct the completed box before evaluating a touch. Measure later path and branch-specific reaction without choosing the deepest or best eventual excursion as the entry.

**Existing attachments.** [sessions.build_session/projections](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py); family_range; family_clocks; [FORMULAS] R-J05/J07/J23, P3-01/P3-06. Geometry exists; source-open identity and modern inner ranges require separate records. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Range EQ and quadrants](range-internals.md) · [Source range-open and range-close references](range-open-close.md) · [Range width and expectations](range-width-context.md) · [Retrospective range path](range-path-class.md) · [Range exhaustion and mean-reversal area](range-exhaustion-area.md) · [The 1.33–1.66 extension area](extensions-1-33-1-66.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
