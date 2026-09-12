# Objective selected before entry

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — VWAP continuation](method-green-bird-vwap-continuation.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md).

The method selects a real destination: range/internal/opposing liquidity, POC/shelf/value, prior control, or the study's declared bracket. Sires fits reward to the HTF objective; Green Bird's VWAP post reports a result without publishing a general target-selection rule. [TBR] pp.8–24; [GB] pp.30–40; [ANAT] pp.8–10; [RTVP] pp.5–8; [REF] p.12.

**Not a standalone trade.** A later high/low or reported 150-point result cannot become the assumed planned target. A destination does not supply the entry.

**Record before use.** Objective_id and type/bounds, side, source scope and known_at, selected priority, entry association, later reach/invalidation times and target-policy uncertainty.

**Phase 1 observation.** Freeze the objective before decision when the source requires one. Score reach only afterward; distinguish an unpublished target algorithm from an observed trade result.

**Current implementation (2026-09-12).** [O141 contract](../FORMULAS.md#o141) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Select one dated active objective before entry and keep later outcome separate from objective selection. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py).

**Evidence limits.** Actual thesis, instruction, fill, management, account or state records are required for a historical instance. Scoped source policies and supplied interpretations cannot manufacture missing private records or a contemporaneous cohort. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Remaining auction objectives](unfinished-business.md) · [Profile point of control](profile-poc.md) · [Saint's Asia-range target context](asia-range-risk-context.md) · [Source-selected position management](position-management.md) · [Observed order lifecycle](order-lifecycle.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[REF]: </workspace/sources/documents/discretionary/refill-effect.pdf>
[ANAT]: </workspace/sources/documents/discretionary/anatomy-of-a-losing-start.pdf>
[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
