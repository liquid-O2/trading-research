# Jumbo failure signatures and three attempts

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md).

The manual rejects the reversal idea after three failed attempts at the same level, persistent strong bodies/volume through it, or absent rejection. It says to exit/observe and, if continuing after failure, reduce allocation at least 50%. [TBR] pp.36–37.

**Not a standalone trade.** Three adjacent touch bars are not three trades or three distinct reversal attempts. Strong continuation through a level does not retrospectively make a failed fade successful.

**Record before use.** Level and branch IDs, distinct attempts with entry/confirmation/exit times, continuation bodies/volume, failure decision and subsequent exposure policy.

**Phase 1 observation.** Count source-defined attempts at the same level, not repeated rows from one touch. Evaluate the failure decision from evidence available then and record any later reduced allocation separately.

**Current implementation (2026-09-12).** [O024 contract](../FORMULAS.md#o024) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Count distinct failed attempts at the same level and branch by the decision time and apply the source invalidation/allocation policy separately. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/range_geometry.py).

**Evidence limits.** Three attempts are an invalidation signature only under the admitted source policy and same level/branch identity. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Range exhaustion and mean-reversal area](range-exhaustion-area.md) · [Jumbo Absorption Zone+ candle](absorption-candle-jumbo.md) · [Source-selected position management](position-management.md) · [Exposure fitted to source risk constraints](position-sizing.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
