# Price reward near the absorption origin

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The strict absorption reversal asks for the new controlling side to gain actual price reward near the original defense before a defended retest. The source discusses a three-tick neighborhood; the later four-stage clip illustrates 2–4 ticks of lift-off and entry within 1–2 ticks of confirmation. [ABS] pp.8–13; [STOP] pp.10–14.

**Not a standalone trade.** Failed opposing effort without reward does not pass the strict reversal branch. That does not add a reward requirement to the separate long-gamma balance-fade branch.

**Record before use.** Actual defense origin/band, rewarded side, reward price/displacement, source distance convention, event times, subsequent retest and entry distance.

**Phase 1 observation.** Keep tick distance distinct from number of events or elapsed time. Do not convert three-tick replenishment into a three-event horizon, and do not borrow one clip's digits across instruments.

**Current implementation (2026-09-12).** [O104 contract](../FORMULAS.md#o104) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Measure directional reward from the selected origin edge and keep reward, return, and renewed defense as distinct dated events. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Four-check absorption reversal](absorption-reward-retest.md) · [Defense, replenishment, exhaustion and lift-off](stop-four-stage.md) · [Absorber becomes aggressive and price lifts off](lift-off.md) · [Aggressor print-size thinning](digit-thinning.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[ABS]: </workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>
[STOP]: </workspace/sources/documents/discretionary/stop-re-entering.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
