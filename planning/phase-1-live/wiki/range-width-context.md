# Range width and expectations

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

Width conditions expectations: a wide/extended overnight can call for restrained targets; a compressed range after purges can support expansion. Printed percentage-width break tables and prior-RTH comparisons have different denominators. [TBR] pp.12–15, 24; [JR] pp.48–49.

**Not a standalone trade.** Wide or narrow is context, not a direction or an automatic single-break entry.

**Record before use.** Own width in points, percentage denominator price and timestamp, comparison range identity/width, source bucket if given, and context known_at.

**Phase 1 observation.** Keep width/price percent distinct from width/prior-RTH-width. Freeze the comparison before entry; final break class is a later outcome. No universal author threshold for extended is supplied.

**Existing attachments.** [sessions.width_bin](/workspace/implementation/src/trading_research/research/phase1_live/sessions.py); family_range; family_open; [FORMULAS] R-J03/J04/J07/J21. Generic ratio buckets do not reproduce a source price-percent table. Component mappings refer to [FORMULAS] and the current code; missing stages remain missing.

**Related objects.** [Jumbo's 06:00–09:00 range](tbr-6-9-range.md) · [Overnight high, low and width](overnight-range.md) · [Retrospective range path](range-path-class.md) · [Opening location and participation](open-location-switch.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
