# Confirmed VWAP deviation fade

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

In an appropriate auction context, price reaches the selected source VWAP deviation; absorption/rejection plus CVD and ladder confirmation permit a rotation toward VWAP or another named objective. [VWAP] pp.3–8.

**Not a standalone trade.** A blind ±2-band touch is not the entry. This fade is not Green Bird's separately disclosed VWAP continuation.

**Record before use.** Source VWAP/reset and band settings, band known_at, local touch/absorption, CVD/ladder confirmation, preselected objective and risk.

**Phase 1 observation.** Use the selected deviation and contemporaneous VWAP. Absorption at an unrelated later price does not confirm this touch; a missing reset remains unknown for an author-faithful construction.

**Current implementation (2026-09-12).** [O125 contract](../FORMULAS.md#o125) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Freeze the selected VWAP deviation band and pre-existing objective; later VWAP cannot rewrite the target. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/flow_sequences.py).

**Evidence limits.** Each required stage, side, parent band and source qualifier needs its own causal observation. Unpublished author classifications remain source limitations; a missing private stage or attempt record is not replaced by a supplied true flag. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Session VWAP](vwap-session.md) · [VWAP deviation bands](vwap-deviations.md) · [Anchored VWAP](vwap-anchored.md) · [Cumulative volume delta and its source reference](cvd-variants.md) · [DOM at a planned location](dom.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[VWAP]: </workspace/sources/documents/discretionary/vwap-lesson-10.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
