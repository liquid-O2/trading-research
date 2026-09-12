# Observed order lifecycle

Object in [JJumboFX — SDRange / Time-Based Ranges](method-jumbo-tbr.md) · [Green Bird — failed breakout / failed breakdown](method-green-bird-failure.md) · [Green Bird — VWAP continuation](method-green-bird-vwap-continuation.md) · [Green Bird — directional scalps](method-green-bird-directional-scalps.md) · [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Unnamed member — reaction area plus minor HVN](method-member-two-reasons.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md).

An entry instruction, drawn ticket, resting order, triggered order, fill, cancellation and exit are different events. OFM illustrates a stop-triggered continuation entry; the Refill study documents a passive-limit bracket and cancellation policy. [OFM] pp.11–13; [REF] pp.12, 22; [TBR] pp.27–29.

**Not a standalone trade.** A plotted bracket does not prove a fill or make its eventual target a preplanned outcome.

**Record before use.** Candidate/order/position IDs, source order type, placement/trigger/fill/cancel times, price/size, initial bracket, amendments and known supporting evidence.

**Phase 1 observation.** For the documented Refill configuration preserve 12-tick inside entry, 32-tick stop, 96-tick target, 30-minute cancellation and one position at a time. Other authors/cases retain their own rules; no live orders are placed.

**Current implementation (2026-09-12).** [O150 contract](../FORMULAS.md#o150) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Reconcile the full order and position state machine across placement, amendment, fills, cancel/expiry/reopen, brackets, exits, and source policy. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/lifecycles.py).

**Evidence limits.** Actual thesis, instruction, fill, management, account or state records are required for a historical instance. Scoped source policies and supplied interpretations cannot manufacture missing private records or a contemporaneous cohort. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Refill-study fill assumption](fill-model.md) · [Trading and account costs](cost-model.md) · [Entry-side structural invalidation](structural-risk.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[OFM]: </workspace/sources/documents/discretionary/origin-of-the-move.pdf>
[REF]: </workspace/sources/documents/discretionary/refill-effect.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
