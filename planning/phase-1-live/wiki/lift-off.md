# Absorber becomes aggressive and price lifts off

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

After defense, replenishment and opposing exhaustion, the absorber turns aggressive and price accelerates. The correct clip illustrates a small initial reward and prompt entry; the wrong clip enters late while the opposite side still gets paid. [STOP] pp.10–14.

**Not a standalone trade.** An uptick by itself is not the four-stage confirmation. Late distance from the origin cannot be repaired by smaller size.

**Record before use.** Same-band defense sequence, absorbing side, new aggressive executions, price displacement/reward ticks, lift-off time and entry distance.

**Phase 1 observation.** Check defense < replenishment ≤ exhaustion < lift-off ≤ decision, together with delta/location. Preserve the illustrated 2–4-tick reward and 1–2-tick entry-distance context rather than relabeling them event counts.

**Current implementation (2026-09-12).** [O115 contract](../FORMULAS.md#o115) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Require ordered defense, replenishment, exhaustion, and liftoff stages, then measure directional reward and entry geometry. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/local_flow.py).

**Evidence limits.** Native executions and BBO support literal measurements. Source-only filters and defense/absorption/replenishment interpretations require attributed observations; the tape does not prove hidden reserve or full-depth order history. Timestamp ties without sequence retain ordering uncertainty. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Aggressor print-size thinning](digit-thinning.md) · [Price reward near the absorption origin](reward-system-3tick.md) · [Defense, replenishment, exhaustion and lift-off](stop-four-stage.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[STOP]: </workspace/sources/documents/discretionary/stop-re-entering.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
