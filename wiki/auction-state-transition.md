# Conditioned next-state transition

**Current reconstruction context.** The later Phase 1 reconstruction includes an explicitly inferred operational version of this input, measured in the acquired census. The dated source-object snapshot below describes the author-specific contract, not the absence of that later model. [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) defines the inference; [current status](current-status.md) links its evidence. Phase 1.5/2 preserve this distinction.


Object in [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

The framework considers the next auction state conditional on current liquidity and pace, distinguishing persistence from change. The 20,000-event AAPL example and its matrix illustrate the process; they are not universal NQ probabilities. [MATH] pp.9–11.

**Not a standalone trade.** A matrix cell or persistent absorption state is not an entry, and absorption must be reconsidered when replenishment fails.

**Record before use.** Current/next state IDs and times, native instrument/depth, conditioning variables available at the current state, cohort and transition count/denominator, including source_counts_symbol provenance.

**Phase 1 observation.** Require state_at < next_state_at and conditioning known_at ≤ state_at. NQ observations are permitted. Counts must belong to that native instrument; equal frequencies by coincidence are not an identity failure. Keep sample/depth and heuristic definitions attached; no new classifier, matrix or trading signal is trained by this source-audit procedure.

**Source-object implementation snapshot (2026-09-12).** [O166 contract](/workspace/planning/phase-1-live/FORMULAS.md#o166) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Validate an actual adjacent dated state transition and causal conditioning evidence; aggregate counts alone never certify it. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py).

**Source-specific evidence limits.** Actual thesis, instruction, fill, management, account or state records are required for a historical instance. Scoped source policies and supplied interpretations cannot manufacture missing private records or a contemporaneous cohort. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [B–A–D–E–W auction-state alphabet](auction-state.md) · [Speed of tape](tape-speed.md) · [Executed passive replenishment](passive-replenishment.md) · [Frozen observation cohort](research-cohort.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
