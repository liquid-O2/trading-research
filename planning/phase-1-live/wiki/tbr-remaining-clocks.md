# Other time-based range formations

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The manual applies the same framework to Asia 20:00–20:30, midnight 00:00–00:30, London 03:00–03:30, 09:30–10:00, 10:00–10:30, lunch 12:00–12:30 and 15:00–15:30. Each formation has its own geometry and availability. [TBR] pp.6–7, 36. Later London examples show another source configuration whose exact formation bounds must be verified. [JR] pp.50–51, 63–66.

**Not a standalone trade.** These are session variants of the range loop, not eight independent entry systems. Liquidity-map hours are also not automatically the formation hours.

**Record before use.** Source version, selected formation clock, H/L/W, internal levels, known_at, later action clock and parent range for every projection.

**Phase 1 observation.** A projection must exist before its alleged reversal. Keep manual and later-platform configurations separate; an unknown formation window makes automatic author-faithful construction unknown.

**Current implementation (2026-09-12).** [O006 contract](../FORMULAS.md#o006) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Build another explicitly clocked native range and expose whether the selected source clock was actually verified. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Only explicitly verified clocks are faithful; manual clock whitelist does not infer other author windows. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Source clocks and availability](clock-grid-and-bars.md) · [Jumbo's 06:00–09:00 range](tbr-6-9-range.md) · [Range EQ and quadrants](range-internals.md) · [Source session-cleanliness assessment](clean-session-label.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
