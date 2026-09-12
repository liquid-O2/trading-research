# Defense, replenishment, exhaustion and lift-off

Object in [Sires — thesis, risk and order flow](method-sires-thesis-flow.md).

The stop/re-entry lesson requires location → initial defense → replenishment → opposing print thinning → absorber becomes aggressive and price lifts off. The correct clip illustrates 2–4 ticks of reward, entry within 1–2 ticks of confirmation and the stated −4R daily stop. [STOP] pp.6–15.

**Not a standalone trade.** No missing box becomes acceptable by reducing size. A stop-out starts a new attempt with every check repeated.

**Record before use.** Fixed real extreme, stage times and sides, replenishment evidence, digit sequence, delta filter, reward/entry distance in ticks and daily R before entry.

**Phase 1 observation.** Check defense < replenishment ≤ exhaustion < lift-off ≤ decision, supportive delta, reward 2–4 ticks, entry distance at most 2 ticks and daily R before >−4 in this source variant. Do not translate spatial ticks into elapsed event counts.

**Current implementation (2026-09-12).** [O123 contract](../FORMULAS.md#o123) is complete, with executable checks passing in the [object review](/workspace/implementation/validation/phase1-completion/obligation-matrix.json). Enforce the STOP branch two-to-four tick reward, zero-to-two tick entry distance, ordered flow stages, and pre-entry daily-risk gate. [Implementation](/workspace/implementation/src/trading_research/research/method_pack/objects/flow_sequences.py).

**Evidence limits.** Each required stage, side, parent band and source qualifier needs its own causal observation. Unpublished author classifications remain source limitations; a missing private stage or attempt record is not replaced by a supplied true flag. See [current status](current-status.md) for the separate historical comparison scope; implementation completion does not establish a source trade or its performance.

**Related objects.** [Aggressor print-size thinning](digit-thinning.md) · [Absorber becomes aggressive and price lifts off](lift-off.md) · [Price reward near the absorption origin](reward-system-3tick.md) · [Cumulative volume delta and its source reference](cvd-variants.md) · [Source account and session stop](daily-loss-limit.md) · [Freshly qualified re-entry](reentry.md)

[Index](index.md) · [Observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)

[STOP]: </workspace/sources/documents/discretionary/stop-re-entering.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
