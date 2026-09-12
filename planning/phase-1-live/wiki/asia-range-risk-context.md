# Saint's Asia-range target context

Object in [Saint — AMT on live markets](method-saint-amt.md).

The trapped-buyer example keeps its target within a realistic Asia-session range distance and uses normal risk after the confirmed retest. This is the source case's target-ambition context. [TRAP] pp.8–10.

**Not a standalone trade.** It is not Sires's 18:00–09:30 overnight-inventory framework, a fixed numerical target, or an independent Asia-box entry.

**Record before use.** Source session/clock evidence, observed or expected range reference actually used, entry/structural stop, intended target and when the rationale was known.

**Phase 1 observation.** Preserve the cited case and its source session identity. Do not infer a universal clock, percentage of range, or fixed point target from one ticket.

**Current implementation (2026-09-12).** [O089 contract](../FORMULAS.md#o089) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Measure entry-stop-target distances for the cited Asia-range case while preserving the source range reference and leaving automatic target construction unavailable. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** The implementation records cited distances only; it does not derive a general Asia-range target rule. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Higher- and lower-timeframe control alignment](htf-ltf-alignment.md) · [Trapped aggression at an auction extreme](trapped-buyers.md) · [Entry-side structural invalidation](structural-risk.md) · [Source-selected position management](position-management.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
