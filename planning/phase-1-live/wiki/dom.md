# DOM at a planned location

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md) · [Keani — open above value](method-keani-open-above-value.md) · [Sires × TeamVOT — The Refill Effect](method-refill-effect.md) · [jetbundle — participation and auction states](method-jetbundle-auction-states.md).

The DOM combines resting display, executed activity and pace at the planned level. Sires resets/reads it before arrival and then checks who is absorbed, who refreshes and who gains actual price reward. [DOM5] pp.3–7; [DOM6] pp.3–7; [DOM7] pp.3–7. Saint uses DOM with footprint at the held retest. [TRAP] pp.8–10. The Refill paper also shows its pre-modeling observations as read from the DOM. [REF] p.7.

**Not a standalone trade.** A displayed wall can disappear without executing. DOM display alone does not certify defense or hidden size.

**Record before use.** Premarked band, reset/observation start, quote price/size/depth, executed side/size, consumption/reload events, price response and known_at.

**Phase 1 observation.** Join observation, response and confirmation at the same level/attempt. Do not substitute final-session median size or an unexecuted displayed wall for local participation.

**Current implementation (2026-09-12).** [O100 contract](../FORMULAS.md#o100) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Measure local BBO display and executions while leaving hidden reserve and source defense interpretation unknown unless observed. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Executed passive replenishment](passive-replenishment.md) · [Iceberg evidence and added participation](iceberg-evidence.md) · [Bid-ask spread](spread-width.md) · [Speed of tape](tape-speed.md) · [At-level DOM rejection](dom-rejection-branch.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[DOM5]: </workspace/sources/documents/discretionary/dom-lesson-5.pdf>
[DOM6]: </workspace/sources/documents/discretionary/dom-lesson-6.pdf>
[DOM7]: </workspace/sources/documents/discretionary/dom-lesson-7.pdf>
[REF]: </workspace/sources/documents/discretionary/refill-effect.pdf>
[TRAP]: </workspace/sources/documents/discretionary/trapped-buyers-one-retest.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
