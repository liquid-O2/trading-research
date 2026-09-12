# Rotation within accepted balance

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md) · [Saint — AMT on live markets](method-saint-amt.md).

An established balance permits a responsive read at a real outer edge, followed by the chosen confirmation and travel toward POC/fair value. Reassess at POC before presuming the far side. [AMT1] pp.7–10; [VP2] pp.3–8; [RTVP] pp.5–8.

**Not a standalone trade.** This is an auction route inside the parent loop. A prior-VA edge touch without current balance and confirmation is not a complete fade.

**Record before use.** Balance_id fixed before arrival, real edge, current context, confirmation branch, preselected POC/other objective and event order.

**Phase 1 observation.** Require contemporaneous balance plus the selected local entry branch. Record initial fair-value reach, POC behavior and any later far-side objective separately.

**Current implementation (2026-09-12).** [O090 contract](../FORMULAS.md#o090) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Validate ordered edge arrival and local confirmation inside an actual balance; keep later far-side outcome separate from the rotation setup. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/auction_geometry.py).

**Evidence limits.** A later far-side objective is not inferred from a local rotation without an actual outcome parent. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Auction balance](auction-balance.md) · [Profile point of control](profile-poc.md) · [Four-check absorption reversal](absorption-reward-retest.md) · [Failure of aggression in long-gamma balance](balance-failure-fade.md) · [POC failure versus efficient passage](poc-traversal.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[RTVP]: </workspace/sources/documents/discretionary/reading-the-volume-profile.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
