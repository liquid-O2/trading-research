# Executed passive replenishment

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

Passive defense means liquidity is consumed and replenished at the relevant area, with the level continuing to hold. Consistency of refresh, size and pace matters on a retest. [DOM7] pp.3–7; [K18] p.11; [STOP] pp.9–10; [MATH] pp.6–8.

**Not a standalone trade.** A resting wall or one BBO size increase does not establish this sequence. A previously formed aggressive-print zone is not itself verified passive reload.

**Record before use.** Price/band, passive side, consumption events, quote/depth changes, refresh repetitions and timing, executed participation and price hold.

**Phase 1 observation.** Keep a BBO reload inference labeled as such. Do not assign a full-session reload flag to a local retest or invent the author's exact refresh threshold/window.

**Current implementation (2026-09-12).** [O102 contract](../FORMULAS.md#o102) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Reconcile consumption and subsequent same-price refresh; zero or unordered activity cannot verify replenishment. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [DOM at a planned location](dom.md) · [Iceberg evidence and added participation](iceberg-evidence.md) · [Zone formed by aggressive prints](refill-zone.md) · [Fresh defense of a continuation band](defended-band-continuation.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DOM7]: </workspace/sources/documents/discretionary/dom-lesson-7.pdf>
[STOP]: </workspace/sources/documents/discretionary/stop-re-entering.pdf>
[K18]: </workspace/sources/documents/discretionary/18k-payout-session.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
