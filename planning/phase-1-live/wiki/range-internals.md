# Range EQ and quadrants

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

EQ and the quarter levels divide the chosen frozen range and provide internal locations or destinations. Extended and purged cases use EQ/quadrant entries differently; the large-range September example trades EQ in both directions with confirmation. [TBR] pp.4–5, 12–15, 24; [JR] p.3, post 2095172969035096454.

**Not a standalone trade.** Touch EQ is not a reversal command. Range EQ, an EV midpoint, volume POC and a range-open line have different identities.

**Record before use.** Parent range_id, L/H/W, Q25=L+0.25W, EQ=L+0.50W, Q75=L+0.75W, frozen bounds and known_at.

**Phase 1 observation.** Test internal contact only after formation; attach the selected extended, purged or internal-rotation branch. Equality at EQ need not be a strict break; use the source's chosen hold/reaction observation.

**Current implementation (2026-09-12).** [O007 contract](../FORMULAS.md#o007) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Compute EQ and 25/75 percent quadrants from one selected positive-width parent range, rejecting caller replacement geometry. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Pure arithmetic; validity depends entirely on the selected parent range coverage and identity. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Jumbo's 06:00–09:00 range](tbr-6-9-range.md) · [Source range-open and range-close references](range-open-close.md) · [Chronological liquidity purges](overnight-purge.md) · [Opening location and participation](open-location-switch.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
